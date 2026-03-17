import io
import os
import threading
import zipfile
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from ..models import APIRequest, GeneratedSite
from ..utils.generator.project_generator import generate_project_files

import requests as http_requests
from django.conf import settings


# URL del webhook de n8n — configurada en .env como N8N_DEPLOY_WEBHOOK
N8N_DEPLOY_WEBHOOK = getattr(settings, "N8N_DEPLOY_WEBHOOK", "http://localhost:5678/webhook/webbuilder-deploy")

# Carpeta local compartida con n8n (montada en /files dentro del contenedor)
# Configurada en .env como N8N_LOCAL_FILES_PATH
N8N_LOCAL_FILES_PATH = getattr(settings, "N8N_LOCAL_FILES_PATH", "/home/alejandro/Desktop/TFG/docker/n8n/local-files")


# ---------------------------------------------------------------------------
# Generación (sin cambios respecto al original)
# ---------------------------------------------------------------------------

def _run_generation(site_id: int):
    from ..models import GeneratedSite
    try:
        site = GeneratedSite.objects.get(pk=site_id)
        files = generate_project_files(site)
        site.project_files = files
        site.generation_status = "ready"
        site.generation_error = ""
        site.save(update_fields=["project_files", "generation_status", "generation_error"])
    except Exception as e:
        try:
            site = GeneratedSite.objects.get(pk=site_id)
            site.generation_status = "error"
            site.generation_error = str(e)
            site.save(update_fields=["generation_status", "generation_error"])
        except Exception:
            pass


@login_required
def site_render(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)
    return render(request, "WebBuilder/site_render.html", {
        "api_request": api_request,
        "site": site,
    })


@login_required
def site_generate(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if request.method != "POST":
        return redirect("site_render", api_request_id=api_request.id)

    site.generation_status = "generating"
    site.generation_error = ""
    site.project_files = {}
    site.save(update_fields=["generation_status", "generation_error", "project_files"])

    thread = threading.Thread(target=_run_generation, args=(site.pk,), daemon=True)
    thread.start()

    return redirect("site_render", api_request_id=api_request.id)


@login_required
@require_GET
def site_status(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)
    return JsonResponse({
        "status": site.generation_status,
        "error": site.generation_error or "",
        "files_count": len(site.project_files) if site.project_files else 0,
    })


@login_required
def site_download_zip(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if not site.project_files:
        messages.error(request, "No hay archivos generados todavía.")
        return redirect("site_render", api_request_id=api_request.id)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in (site.project_files or {}).items():
            safe_path = str(path).lstrip("/").replace("..", "")
            zf.writestr(safe_path, content or "")

    buf.seek(0)
    filename = f"{site.project_name or 'generated_site'}.zip".replace(" ", "_")
    resp = HttpResponse(buf.getvalue(), content_type="application/zip")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# ---------------------------------------------------------------------------
# Despliegue asíncrono
# ---------------------------------------------------------------------------

def _run_deploy(site_id: int):
    """
    Ejecuta el despliegue en un hilo secundario:
      1. Construye el ZIP en memoria
      2. Lo guarda en la carpeta compartida con n8n
      3. Hace POST al webhook de n8n y espera la respuesta
      4. Guarda preview_url / deploy_status en la BD
    """
    from ..models import GeneratedSite

    def _set_error(site, msg: str):
        site.deploy_status = "error"
        site.deploy_error = msg
        site.save(update_fields=["deploy_status", "deploy_error"])

    try:
        site = GeneratedSite.objects.get(pk=site_id)
    except GeneratedSite.DoesNotExist:
        return

    project_name = (site.project_name or "generated_site").replace(" ", "_")
    zip_filename = f"{project_name}.zip"

    # 1. Construir ZIP
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in (site.project_files or {}).items():
            safe_path = str(path).lstrip("/").replace("..", "")
            zf.writestr(safe_path, content or "")
    buf.seek(0)

    # 2. Guardar en disco compartido con n8n
    deploy_dir = os.path.join(N8N_LOCAL_FILES_PATH, "deploys", project_name)
    zip_path = os.path.join(deploy_dir, zip_filename)
    try:
        os.makedirs(deploy_dir, exist_ok=True)
        with open(zip_path, "wb") as f:
            f.write(buf.getvalue())
    except Exception as exc:
        _set_error(site, f"Error al guardar el ZIP en disco: {exc}")
        return

    # 3. Llamar al webhook de n8n (bloqueante en el hilo secundario)
    try:
        response = http_requests.post(
            N8N_DEPLOY_WEBHOOK,
            json={
                "project_name": project_name,
                "site_id": str(site.pk),
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        preview_url = data.get("preview_url") or ""
    except http_requests.exceptions.Timeout:
        _set_error(site, "n8n tardó demasiado en responder (timeout 180 s).")
        return
    except http_requests.exceptions.ConnectionError:
        _set_error(site, "No se pudo conectar con n8n. ¿Está corriendo?")
        return
    except Exception as exc:
        _set_error(site, f"Error al desplegar: {exc}")
        return

    if not preview_url:
        _set_error(site, "n8n no devolvió una preview_url. Revisa el workflow.")
        return

    # 4. Guardar resultado
    site.preview_url = preview_url
    site.deploy_status = "done"
    site.deploy_error = ""
    site.save(update_fields=["preview_url", "deploy_status", "deploy_error"])


@login_required
def site_deploy(request, api_request_id: int):
    if request.method != "POST":
        return redirect("site_render", api_request_id=api_request_id)

    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if site.generation_status != "ready" or not site.project_files:
        messages.error(request, "El proyecto debe estar generado antes de desplegarlo.")
        return redirect("site_render", api_request_id=api_request_id)

    # Marcar como desplegando y responder inmediatamente al navegador
    site.deploy_status = "deploying"
    site.deploy_error = ""
    site.save(update_fields=["deploy_status", "deploy_error"])

    thread = threading.Thread(target=_run_deploy, args=(site.pk,), daemon=True)
    thread.start()

    return redirect("site_render", api_request_id=api_request_id)


@login_required
@require_GET
def site_deploy_status(request, api_request_id: int):
    """
    Endpoint de polling: devuelve el estado actual del despliegue.
    El frontend llama a este endpoint cada 3 s mientras deploy_status == 'deploying'.
    """
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)
    return JsonResponse({
        "deploy_status": site.deploy_status,
        "deploy_error":  site.deploy_error or "",
        "preview_url":   site.preview_url or "",
    })


# Modificar el codigo hecho por el llm
@login_required
@require_POST  # Evita que alguien entre en cualquier peticion
def site_update_file(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    path    = data.get("path", "").strip()
    content = data.get("content", "")

    if not path:
        return JsonResponse({"ok": False, "error": "path vacío"}, status=400)

    files = site.project_files or {}
    if path not in files:
        return JsonResponse({"ok": False, "error": "Ruta no encontrada"}, status=404)

    files[path] = content
    site.project_files = files
    site.save(update_fields=["project_files"])

    return JsonResponse({"ok": True})