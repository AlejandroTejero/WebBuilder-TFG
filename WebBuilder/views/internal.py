"""
internal.py — Endpoints internos para n8n (no expuestos al usuario).
"""
import os
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

import logging
logger = logging.getLogger(__name__)

from ..models import GeneratedSite, GenerationLog

def _check_token(request) -> bool:
    token = request.headers.get("X-Internal-Token", "")
    return token == getattr(settings, "INTERNAL_TOKEN", "")


@require_GET
def health_summary(request):
    if not _check_token(request):
        return JsonResponse({"error": "Forbidden"}, status=403)

    since = timezone.now() - timedelta(hours=24)

    # Generaciones en las últimas 24h
    sites_24h = GeneratedSite.objects.filter(created_at__gte=since)
    total = sites_24h.count()

    if total == 0:
        success_rate = 100
        retry_rate = 0
        avg_duration = 0
        failed = 0
    else:
        ready = sites_24h.filter(generation_status="ready").count()
        failed = sites_24h.filter(generation_status="error").count()
        success_rate = round((ready / total) * 100, 1)

        # Retry rate — sites que tuvieron al menos un log con had_retry=True
        with_retry = sites_24h.filter(generation_logs__had_retry=True).distinct().count()
        retry_rate = round((with_retry / total) * 100, 1)

        # Duración media (updated_at - created_at en segundos)
        durations = []
        for site in sites_24h.filter(generation_status="ready"):
            delta = (site.updated_at - site.created_at).total_seconds()
            if delta > 0:
                durations.append(delta)
        avg_duration = round(sum(durations) / len(durations), 1) if durations else 0

    # Contenedores activos (aproximación: deploy_status=done)
    active_containers = GeneratedSite.objects.filter(deploy_status="done").count()

    # Disco usado en la carpeta de deploys
    disk_used_mb = 0
    deploy_dir = getattr(settings, "N8N_LOCAL_FILES_PATH", "")
    if deploy_dir:
        deploys_path = os.path.join(deploy_dir, "deploys")
        if os.path.exists(deploys_path):
            total_bytes = sum(
                os.path.getsize(os.path.join(dirpath, f))
                for dirpath, _, files in os.walk(deploys_path)
                for f in files
            )
            disk_used_mb = round(total_bytes / (1024 * 1024), 1)

    # Errores más frecuentes
    errors = (
        sites_24h.filter(generation_status="error")
        .exclude(generation_error="")
        .values_list("generation_error", flat=True)
    )
    errors_last_24h = list(set(e[:80] for e in errors))[:5]

    return JsonResponse({
        "generations_last_24h":  total,
        "success_rate_24h":      success_rate,
        "retry_rate_24h":        retry_rate,
        "avg_duration_seconds":  avg_duration,
        "failed_generations":    failed,
        "active_containers":     active_containers,
        "disk_used_mb":          disk_used_mb,
        "errors_last_24h":       errors_last_24h,
    })



@csrf_exempt
@require_POST
def container_shutdown(request):
    if not _check_token(request):
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    container_name = data.get("container_name", "").strip()
    if not container_name:
        return JsonResponse({"error": "container_name vacío"}, status=400)

    # El nombre del contenedor es wb_<project_name>
    # Buscamos el sitio por project_name
    project_name = container_name.replace("wb_", "", 1)

    
    site = GeneratedSite.objects.filter(project_name=project_name).order_by('-created_at').first()
    if not site:
        logger.warning("[internal] Contenedor %s no encontrado en BD", container_name)
        return JsonResponse({"ok": False, "error": "Sitio no encontrado"}, status=404)

    site.deploy_status = "idle"
    site.preview_url = ""
    site.save(update_fields=["deploy_status", "preview_url"])
    logger.info("[internal] Contenedor %s marcado como idle (sin desplegar)", container_name)
    
    return JsonResponse({"ok": True, "project_name": project_name})
