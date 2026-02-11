"""
Vistas de autenticación
"""

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


def register(request):
    """
    Maneja el registro de nuevos usuarios
    
    GET: Muestra el formulario de registro vacío
    POST: Procesa el registro y redirige al login si es exitoso
    """
    if request.method == "POST":
        # Construye el form con los datos enviados
        form = UserCreationForm(request.POST)
        
        # Valida el form
        if form.is_valid():
            # Guarda el usuario
            form.save()
            # Redirige al login
            return redirect("login")
    else:
        # Construye un form vacío
        form = UserCreationForm()
    
    # Renderiza la plantilla de registro con el form
    return render(request, "registration/register.html", {"form": form})
