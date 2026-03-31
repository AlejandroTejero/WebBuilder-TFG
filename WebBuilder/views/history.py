"""
Vistas de historial
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from ..models import APIRequest, GeneratedSite


@login_required
def history_analysis(request):
    qs = APIRequest.objects.filter(user=request.user).order_by("-date")

    status_filter = request.GET.get("status", "")
    if status_filter in ("pending", "processed", "error"):
        qs = qs.filter(status=status_filter)

    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(api_url__icontains=search)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page", 1)
    api_requests = paginator.get_page(page_number)

    total_sites = GeneratedSite.objects.filter(project_source__user=request.user).count()

    return render(request, "WebBuilder/partials/history/recent_analysis.html", {
        "api_requests": api_requests,
        "status_filter": status_filter,
        "search": search,
        "total_count": paginator.count,
        "total_sites": total_sites,
    })


@login_required
def history_sites(request):
    qs = (
        GeneratedSite.objects
        .filter(project_source__user=request.user)
        .select_related("project_source")
        .order_by("-created_at")
    )

    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(accepted_plan__site_title__icontains=search)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page", 1)
    generated_sites = paginator.get_page(page_number)

    total_analysis = APIRequest.objects.filter(user=request.user).count()

    return render(request, "WebBuilder/partials/history/published_sites.html", {
        "generated_sites": generated_sites,
        "search": search,
        "total_count": paginator.count,
        "total_analysis": total_analysis,
    })


@login_required
def history(request):
    return redirect("history_analysis")


@login_required
def delete_analysis(request, api_request_id):
    if request.method != "POST":
        return redirect("history_analysis")

    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    api_request.delete()
    messages.success(request, "Análisis eliminado correctamente.")
    return redirect("history_analysis")

@login_required
def delete_site(request, site_id):
    if request.method != "POST":
        return redirect("history_sites")

    site = get_object_or_404(GeneratedSite, id=site_id, project_source__user=request.user)
    site.delete()
    messages.success(request, "Sitio eliminado correctamente.")
    return redirect("history_sites")