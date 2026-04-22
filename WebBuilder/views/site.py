import io
import os
import threading
import zipfile
import json
import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from ..models import APIRequest, GeneratedSite
from ..utils.generator.project_generator import generate_project_files

from django.views.decorators.http import require_GET, require_POST

import requests as http_requests
from django.conf import settings

# ---------------------------------------------------------------------------
# Generación (sin cambios respecto al original)
# ---------------------------------------------------------------------------

import time  # añade esto arriba del todo junto a los otros imports

def _run_generation(site_id: int):
    from ..models import GeneratedSite
    from ..utils.generator.notifications import notify_generation_done  # añade esto

    start_time = time.time()  # añade esto

    try:
        site = GeneratedSite.objects.get(pk=site_id)
        files = generate_project_files(site)
        site.project_files = files
        site.generation_status = "ready"
        site.generation_error = ""
        site.save(update_fields=["project_files", "generation_status", "generation_error"])

        # Notificar a n8n
        duration = int(time.time() - start_time)  # añade esto
        notify_generation_done(site, duration_seconds=duration)  # añade esto

    except Exception as e:
        try:
            site = GeneratedSite.objects.get(pk=site_id)
            site.generation_status = "error"
            site.generation_error = str(e)
            site.save(update_fields=["generation_status", "generation_error"])
        except Exception:
            pass

# Recojo los campos necesarios para las estadisitcas
@login_required
def site_render(request, api_request_id: int):
    import re
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site, _ = GeneratedSite.objects.get_or_create(project_source=api_request)

    plan = site.accepted_plan or {}

    # — Campos del modelo (parseando models.py generado)
    model_fields = []
    models_code = next((v for k, v in (site.project_files or {}).items() if k.endswith("models.py")), "")
    if models_code:
        for match in re.finditer(r'^\s+(\w+)\s*=\s*models\.(\w+)', models_code, re.MULTILINE):
            name, field_type = match.group(1), match.group(2)
            if name not in ("id", "created_at", "updated_at"):
                model_fields.append({"name": name, "type": field_type})

    # — Páginas generadas (parseando urls.py de la app)
    pages = []
    urls_code = next((v for k, v in (site.project_files or {}).items()
                      if k.endswith("siteapp/urls.py") or k.endswith("urls.py")), "")
    if urls_code:
        for match in re.finditer(r"path\('([^']*)',\s*views\.(\w+),\s*name='(\w+)'", urls_code):
            url, view, name = match.group(1), match.group(2), match.group(3)
            if name != "register":
                pages.append({"url": "/" + url, "view": view, "name": name})

    # — Stats de generación (desde los logs)
    logs = site.generation_logs.all().order_by("created_at")
    llm_model = logs.first().llm_model if logs.exists() else "—"
    total_calls = logs.count()
    retries = logs.filter(had_retry=True).count()
    consistency_errors = sum(len(l.consistency_errors) for l in logs)

    # — Desglose de archivos por tipo
    files = site.project_files or {}
    files_py   = sum(1 for k in files if k.endswith(".py"))
    files_html = sum(1 for k in files if k.endswith(".html"))
    files_other = len(files) - files_py - files_html

    return render(request, "WebBuilder/site_render.html", {
        "api_request":         api_request,
        "site":                site,
        "site_users":          site.site_users.all(),
        "plan":                plan,
        "model_fields":        model_fields,
        "pages":               pages,
        "llm_model":           llm_model,
        "total_calls":         total_calls,
        "retries":             retries,
        "consistency_errors":  consistency_errors,
        "files_py":            files_py,
        "files_html":          files_html,
        "files_other":         files_other,
    })

@login_required
def site_generate(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if request.method != "POST":
        return redirect("site_render", api_request_id=api_request.id)

    # Si ya había archivos generados, guardamos snapshot antes de borrarlos
    if site.project_files:
        from ..models import SiteVersion
        last = site.versions.order_by('-version_number').first()
        next_number = (last.version_number + 1) if last else 1
        SiteVersion.objects.create(
            site=site,
            version_number=next_number,
            project_files=site.project_files,
            label="Antes de regenerar",
        )

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
        "step": site.generation_step or "",
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
    deploy_dir = os.path.join(settings.N8N_LOCAL_FILES_PATH, "deploys", project_name)
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
            settings.N8N_DEPLOY_WEBHOOK,
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

@login_required
@require_GET
def site_versions(request, api_request_id: int):
    from ..models import SiteVersion
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    versions = site.versions.order_by('-version_number').values(
        'id', 'version_number', 'label', 'created_at'
    )

    return JsonResponse({
        'versions': [
            {
                'id': v['id'],
                'version_number': v['version_number'],
                'label': v['label'],
                'created_at': v['created_at'].strftime('%d/%m/%Y %H:%M'),
            }
            for v in versions
        ]
    })


@login_required
@require_POST
def site_version_restore(request, api_request_id: int, version_id: int):
    from ..models import SiteVersion
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)
    version = get_object_or_404(SiteVersion, id=version_id, site=site)

    # Guardamos la versión actual antes de restaurar
    if site.project_files:
        last = site.versions.order_by('-version_number').first()
        next_number = (last.version_number + 1) if last else 1
        SiteVersion.objects.create(
            site=site,
            version_number=next_number,
            project_files=site.project_files,
            label="Antes de restaurar",
        )

    # Restauramos
    site.project_files = version.project_files
    site.generation_status = "ready"
    site.save(update_fields=["project_files", "generation_status"])

    return JsonResponse({'ok': True})

@login_required
@require_GET
def site_version_download(request, api_request_id: int, version_id: int):
    from ..models import SiteVersion
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)
    version = get_object_or_404(SiteVersion, id=version_id, site=site)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in (version.project_files or {}).items():
            safe_path = str(path).lstrip("/").replace("..", "")
            zf.writestr(safe_path, content or "")

    buf.seek(0)
    filename = f"{site.project_name or 'version'}_v{version.version_number}.zip"
    resp = HttpResponse(buf.getvalue(), content_type="application/zip")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

@login_required
@require_POST
def site_users_save(request, api_request_id: int):
    from ..models import SiteUser
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site, _ = GeneratedSite.objects.get_or_create(
            project_source=api_request,
            defaults={"accepted_plan": False}
        )
    
    try:
        data = json.loads(request.body)
        users = data.get('users', [])
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    # Validación básica
    for u in users:
        if not u.get('username') or not u.get('password'):
            return JsonResponse({'ok': False, 'error': 'Usuario o contraseña vacíos'}, status=400)

    # Borramos los anteriores y guardamos los nuevos
    SiteUser.objects.filter(site=site).delete()
    for u in users:
        SiteUser.objects.create(
            site=site,
            username=u['username'].strip(),
            password=u['password'].strip(),
            role=u.get('role', 'normal'),
        )

    return JsonResponse({'ok': True, 'saved': len(users)})

@login_required
@require_POST
def site_refine_file(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if not site.project_files:
        return JsonResponse({"ok": False, "error": "No hay archivos generados."}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    message = data.get("message", "").strip()
    if not message:
        return JsonResponse({"ok": False, "error": "Mensaje vacío"}, status=400)

    # Identificar qué archivo tocar según el mensaje del usuario
    file_list = "\n".join(site.project_files.keys())
    system_identify = (
        "Eres un asistente que identifica qué archivo de un proyecto Django "
        "debe modificarse según la petición del usuario. "
        "Devuelve SOLO el path exacto del archivo más relevante, sin explicación ni comillas. "
        "Si la petición afecta a la página de inicio responde con el path del home.html. "
        "Si afecta al listado responde con el catalog/list html. "
        "Si afecta al estilo global responde con base.html. "
        "Si afecta a la lógica responde con views.py."
    )
    user_identify = f"Archivos disponibles:\n{file_list}\n\nPetición del usuario: {message}"

    try:
        from ..utils.llm.client import chat_completion, LLMError
        target_path = chat_completion(
            user_text=user_identify,
            system_text=system_identify,
            temperature=0.0,
        ).strip().strip('"').strip("'")
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Error identificando archivo: {e}"}, status=500)

    if target_path not in site.project_files:
        # Intentar match parcial
        match = next((p for p in site.project_files if target_path in p or p.endswith(target_path)), None)
        if not match:
            return JsonResponse({"ok": False, "error": f"Archivo no encontrado: {target_path}"}, status=404)
        target_path = match

    current_content = site.project_files[target_path]
    ext = target_path.split(".")[-1]

    system_rewrite = (
        "Eres un desarrollador Django senior experto en Python y Tailwind CSS. "
        "REGLA ABSOLUTA: devuelves ÚNICAMENTE código puro, sin ningún tipo de Markdown. "
        "PROHIBIDO escribir ``` en cualquier parte de tu respuesta. "
        "Tu respuesta empieza DIRECTAMENTE con la primera línea de código."
    )
    user_rewrite = (
        f"Modifica el siguiente archivo ({target_path}) según esta petición: {message}\n\n"
        f"ARCHIVO ACTUAL:\n{current_content}\n\n"
        f"Devuelve el archivo COMPLETO modificado. No expliques nada, solo el código."
    )

    try:
        new_content = chat_completion(
            user_text=user_rewrite,
            system_text=system_rewrite,
            temperature=0.3,
        )
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Error del LLM: {e}"}, status=500)

    if not new_content.strip():
        return JsonResponse({"ok": False, "error": "El LLM devolvió una respuesta vacía."}, status=500)

    # Limpiar fences si se colaron
    import re
    new_content = re.sub(r'```[\w]*\n?', '', new_content)
    new_content = re.sub(r'```', '', new_content).strip()

    files = site.project_files
    files[target_path] = new_content
    site.project_files = files
    site.save(update_fields=["project_files"])

    return JsonResponse({"ok": True, "file": target_path})


@login_required
@require_GET
def site_code_viewer(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)
    return render(request, "WebBuilder/code_viewer.html", {
        "api_request": api_request,
        "site": site,
    })