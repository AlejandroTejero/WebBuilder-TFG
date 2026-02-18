"""
Vista de historial
Muestra el historial de análisis del usuario
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import APIRequest

# Muestra del historial por usuario
@login_required
def history(request):
    # Carga los análisis del usuario ordenados recientes
    api_requests = (
        APIRequest.objects.filter(user=request.user).order_by("-date")
    )

    # Hueco para "webs generadas"
    generated_sites = []

    return render(request, "WebBuilder/history.html", {
        "api_requests": api_requests,
        "generated_sites": generated_sites,
    })
