import io
import threading
import zipfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from ..models import APIRequest, GeneratedSite
from ..utils.generator.project_generator import generate_project_files

import requests as http_requests
from django.conf import settings


# URL del webhook de n8n — configurada en .env como N8N_DEPLOY_WEBHOOK
N8N_DEPLOY_WEBHOOK = getattr(settings, "N8N_DEPLOY_WEBHOOK", "http://localhost:5678/webhook/webbuilder-deploy")


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

@login_required
def site_deploy(request, api_request_id: int):
    if request.method != "POST":
        return redirect("site_render", api_request_id=api_request_id)

    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if site.generation_status != "ready" or not site.project_files:
        messages.error(request, "El proyecto debe estar generado antes de desplegarlo.")
        return redirect("site_render", api_request_id=api_request_id)

    # Construir ZIP en memoria (igual que site_download_zip)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in (site.project_files or {}).items():
            safe_path = str(path).lstrip("/").replace("..", "")
            zf.writestr(safe_path, content or "")
    buf.seek(0)

    zip_name = f"{site.project_name or 'generated_site'}.zip".replace(" ", "_")

    # Mandar el ZIP a n8n como multipart/form-data
    try:
        response = http_requests.post(
            N8N_DEPLOY_WEBHOOK,
            files={"file": (zip_name, buf, "application/zip")},
            data={
                "project_name": site.project_name or "generated_site",
                "site_id": str(site.pk),
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        preview_url = data.get("preview_url") or ""
    except http_requests.exceptions.Timeout:
        messages.error(request, "n8n tardó demasiado en responder (timeout 120s).")
        return redirect("site_render", api_request_id=api_request_id)
    except http_requests.exceptions.ConnectionError:
        messages.error(request, "No se pudo conectar con n8n. ¿Está corriendo?")
        return redirect("site_render", api_request_id=api_request_id)
    except Exception as exc:
        messages.error(request, f"Error al desplegar: {exc}")
        return redirect("site_render", api_request_id=api_request_id)

    if not preview_url:
        messages.error(request, "n8n no devolvió una preview_url. Revisa el workflow.")
        return redirect("site_render", api_request_id=api_request_id)

    site.preview_url = preview_url
    site.save(update_fields=["preview_url"])

    messages.success(request, f"Proyecto desplegado. Preview: {preview_url}")
    return redirect("site_render", api_request_id=api_request_id)