"""
Vista de historial
Muestra el historial de análisis del usuario
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import APIRequest, GeneratedSite

# Muestra del historial por usuario
@login_required
def history(request):
    # Carga los análisis del usuario ordenados recientes
    api_requests = (
        APIRequest.objects.filter(user=request.user).order_by("-date")
    )

    # Webs generadas del usuario
    generated_sites = (
        GeneratedSite.objects
        .filter(project_source__user=request.user)
        .select_related("project_source")
        .order_by("-created_at")
    )

    return render(request, "WebBuilder/history.html", {
        "api_requests": api_requests,
        "generated_sites": generated_sites,
    })
