from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..models import APIRequest, GeneratedSite
from ..utils.generator.project_generator import generate_project_files

import io
import zipfile
from django.http import HttpResponse

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

    # marcar generando
    site.generation_status = "generating"
    site.generation_error = ""
    site.save(update_fields=["generation_status", "generation_error"])

    try:
        files = generate_project_files(site)  # paso 3
        site.project_files = files
        site.generation_status = "ready"
        site.save(update_fields=["project_files", "generation_status"])
        messages.success(request, "Proyecto generado ✅")
    except Exception as e:
        site.generation_status = "error"
        site.generation_error = str(e)
        site.save(update_fields=["generation_status", "generation_error"])
        messages.error(request, f"Error generando: {e}")

    return redirect("site_render", api_request_id=api_request.id)

@login_required
def site_download_zip(request, api_request_id: int):
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if not site.project_files:
        messages.error(request, "No hay archivos generados todavía.")
        return redirect("site_render", api_request_id=api_request.id)

    # Crear ZIP en memoria
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in (site.project_files or {}).items():
            # Seguridad mínima: evitar rutas raras tipo ../../
            safe_path = str(path).lstrip("/").replace("..", "")
            zf.writestr(safe_path, content or "")

    buf.seek(0)

    filename = f"{site.project_name or 'generated_site'}.zip".replace(" ", "_")
    resp = HttpResponse(buf.getvalue(), content_type="application/zip")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp