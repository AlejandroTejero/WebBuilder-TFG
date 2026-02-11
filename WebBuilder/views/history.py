"""
Vista de historial
Muestra el historial de análisis del usuario
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import APIRequest


@login_required
def history(request):
    """
    Muestra el historial de análisis del usuario
    
    Lista todos los APIRequest del usuario ordenados por fecha
    (más recientes primero)
    
    Args:
        request: Request de Django
        
    Returns:
        HttpResponse con la página de historial renderizada
    """
    # Carga los análisis del usuario (más recientes primero)
    api_requests = (
        APIRequest.objects
        .filter(user=request.user)
        .order_by("-date")
    )

    # Placeholder para futuras "webs generadas"
    generated_sites = []

    return render(request, "WebBuilder/history.html", {
        "api_requests": api_requests,
        "generated_sites": generated_sites,
    })
