"""
Vista de métricas — /admin/metricas/
Solo accesible para staff (is_staff=True).
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg, Q
from ..models import GenerationLog, GeneratedSite, APIRequest


@staff_member_required
def metrics_view(request):

    # ── Total de logs ────────────────────────────────────────────
    total_logs = GenerationLog.objects.count()
    total_sites = GeneratedSite.objects.count()
    total_analyses = APIRequest.objects.count()

    # ── Logs por paso ────────────────────────────────────────────
    steps_stats = (
        GenerationLog.objects
        .values("step")
        .annotate(
            total=Count("id"),
            retries=Count("id", filter=Q(had_retry=True)),
        )
        .order_by("-total")
    )

    # ── Logs por modelo LLM ──────────────────────────────────────
    model_stats = (
        GenerationLog.objects
        .values("llm_model")
        .annotate(
            total=Count("id"),
            retries=Count("id", filter=Q(had_retry=True)),
        )
        .order_by("-total")
    )

    # ── Generaciones por día (últimos 30 días) ───────────────────
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models.functions import TruncDate

    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_stats = (
        GeneratedSite.objects
        .filter(created_at__gte=thirty_days_ago)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # ── Pasos con más errores de consistencia ────────────────────
    error_steps = (
        GenerationLog.objects
        .exclude(consistency_errors=[])
        .values("step")
        .annotate(total_errors=Count("id"))
        .order_by("-total_errors")[:5]
    )

    return render(request, "admin/metrics.html", {
        "total_logs": total_logs,
        "total_sites": total_sites,
        "total_analyses": total_analyses,
        "steps_stats": steps_stats,
        "model_stats": model_stats,
        "daily_stats": daily_stats,
        "error_steps": error_steps,
    })