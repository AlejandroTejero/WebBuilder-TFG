"""
Vistas de páginas simples
"""

from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """
    Renderiza la página de inicio
    
    Muestra la landing page con información del proyecto
    y el call-to-action para ir al asistente
    """
    try:
        # Devuelve la plantilla de home
        return render(request, "WebBuilder/home.html")
    except Exception as exc:
        # Captura errores inesperados y devuelve mensaje
        return HttpResponse(f"Error al procesar: {exc}")
