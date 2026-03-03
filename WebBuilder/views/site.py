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