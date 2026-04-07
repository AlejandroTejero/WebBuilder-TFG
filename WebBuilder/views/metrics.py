"""
Vista de métricas — /metricas/
Solo accesible para staff (is_staff=True).
"""

import json
from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from ..models import APIRequest, GeneratedSite, GenerationLog


@user_passes_test(lambda u: u.is_staff, login_url='login')
def metrics_view(request):

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago  = now - timedelta(days=7)

    # ── KPIs generales ───────────────────────────────────────────
    total_users     = User.objects.count()
    total_analyses  = APIRequest.objects.count()
    total_sites     = GeneratedSite.objects.count()
    total_logs      = GenerationLog.objects.count()

    success_analyses = APIRequest.objects.filter(status="processed").count()
    success_rate = round(success_analyses / total_analyses * 100, 1) if total_analyses else 0

    sites_from_analyses = APIRequest.objects.filter(plan_accepted=True).count()
    conversion_rate = round(sites_from_analyses / total_analyses * 100, 1) if total_analyses else 0

    total_retries = GenerationLog.objects.filter(had_retry=True).count()
    retry_rate = round(total_retries / total_logs * 100, 1) if total_logs else 0

    # ── Usuarios ─────────────────────────────────────────────────
    active_users = (
        User.objects
        .filter(api_requests__date__gte=seven_days_ago)
        .distinct()
        .count()
    )

    users_with_sites = (
        User.objects
        .filter(api_requests__site__isnull=False)
        .distinct()
        .count()
    )

    top_users_analyses = (
        User.objects
        .annotate(total=Count('api_requests'))
        .filter(total__gt=0)
        .order_by('-total')[:5]
        .values('username', 'total')
    )

    top_users_sites = (
        User.objects
        .annotate(total=Count('api_requests__site'))
        .filter(total__gt=0)
        .order_by('-total')[:5]
        .values('username', 'total')
    )

    # ── Actividad últimos 30 días ─────────────────────────────────
    daily_analyses = (
        APIRequest.objects
        .filter(date__gte=thirty_days_ago)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    daily_sites = (
        GeneratedSite.objects
        .filter(created_at__gte=thirty_days_ago)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    # Construir listas paralelas para Chart.js
    from datetime import date, timedelta as td
    days_range = [(thirty_days_ago + td(days=i)).date() for i in range(31)]
    analyses_map = {r['day']: r['total'] for r in daily_analyses}
    sites_map    = {r['day']: r['total'] for r in daily_sites}

    chart_labels    = [d.strftime('%-d %b') for d in days_range]
    chart_analyses  = [analyses_map.get(d, 0) for d in days_range]
    chart_sites     = [sites_map.get(d, 0)    for d in days_range]

    # Formato de entrada
    json_count = APIRequest.objects.filter(input_type='url').count()
    file_count = APIRequest.objects.filter(input_type='file').count()

    # ── LLM ──────────────────────────────────────────────────────
    consistency_errors_total = (
        GenerationLog.objects
        .exclude(consistency_errors=[])
        .count()
    )
    consistency_rate = round(consistency_errors_total / total_logs * 100, 1) if total_logs else 0

    avg_calls_per_site = round(total_logs / total_sites, 1) if total_sites else 0

    model_stats = (
        GenerationLog.objects
        .values('llm_model')
        .annotate(
            total=Count('id'),
            retries=Count('id', filter=Q(had_retry=True)),
        )
        .order_by('-total')
    )
    # Calcular tasa de reintento por modelo y el máximo para las barras
    model_stats = list(model_stats)
    max_model_total = max((m['total'] for m in model_stats), default=1)
    for m in model_stats:
        m['retry_rate'] = round(m['retries'] / m['total'] * 100, 1) if m['total'] else 0
        m['bar_pct']    = round(m['total'] / max_model_total * 100)

    error_steps = (
        GenerationLog.objects
        .exclude(consistency_errors=[])
        .values('step')
        .annotate(total_errors=Count('id'))
        .order_by('-total_errors')[:6]
    )
    error_steps = list(error_steps)
    max_errors = error_steps[0]['total_errors'] if error_steps else 1
    for e in error_steps:
        e['bar_pct'] = round(e['total_errors'] / max_errors * 100)

    steps_stats = (
        GenerationLog.objects
        .values('step')
        .annotate(
            total=Count('id'),
            retries=Count('id', filter=Q(had_retry=True)),
        )
        .order_by('-total')
    )

    # ── Generaciones recientes ────────────────────────────────────
    recent_sites = (
        GeneratedSite.objects
        .select_related('project_source__user')
        .order_by('-created_at')[:10]
    )

    all_sites = (
        GeneratedSite.objects
        .select_related('project_source__user')
        .order_by('-created_at')[:50]
    )

    # ── Alertas ──────────────────────────────────────────────────
    stuck_generating = (
        GeneratedSite.objects
        .filter(
            generation_status='generating',
            updated_at__lt=now - timedelta(minutes=15),
        )
        .select_related('project_source__user')
    )

    pending_analyses = APIRequest.objects.filter(status='pending').count()

    oldest_pending = (
        APIRequest.objects
        .filter(status='pending')
        .order_by('date')
        .first()
    )

    recent_errors = (
        GeneratedSite.objects
        .filter(
            generation_status='error',
            updated_at__gte=now - timedelta(hours=24),
        )
        .select_related('project_source__user')
        .order_by('-updated_at')[:5]
    )

    return render(request, 'WebBuilder/metrics.html', {
        # KPIs
        'total_users':       total_users,
        'total_analyses':    total_analyses,
        'total_sites':       total_sites,
        'total_logs':        total_logs,
        'success_rate':      success_rate,
        'conversion_rate':   conversion_rate,
        'retry_rate':        retry_rate,
        # Usuarios
        'active_users':      active_users,
        'users_with_sites':  users_with_sites,
        'top_users_analyses': top_users_analyses,
        'top_users_sites':   top_users_sites,
        # Actividad
        'chart_labels':      json.dumps(chart_labels),
        'chart_analyses':    json.dumps(chart_analyses),
        'chart_sites':       json.dumps(chart_sites),
        'json_count':        json_count,
        'file_count':        file_count,
        # LLM
        'consistency_errors_total': consistency_errors_total,
        'consistency_rate':  consistency_rate,
        'avg_calls_per_site': avg_calls_per_site,
        'model_stats':       model_stats,
        'error_steps':       error_steps,
        'steps_stats':       steps_stats,
        # Generaciones
        'recent_sites':      recent_sites,
        'all_sites':         all_sites,
        # Alertas
        'stuck_generating':  stuck_generating,
        'pending_analyses':  pending_analyses,
        'oldest_pending':    oldest_pending,
        'recent_errors':     recent_errors,
    })
