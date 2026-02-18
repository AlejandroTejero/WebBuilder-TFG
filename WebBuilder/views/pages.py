from django.shortcuts import render
from django.http import HttpResponse

# Render de algunas vistas

def home(request):

    try:
        # Devuelve la plantilla de home
        return render(request, "WebBuilder/home.html")
    except Exception as exc:
        # Captura errores inesperados y devuelve mensaje
        return HttpResponse(f"Error al procesar: {exc}")
