from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


# Render de vistas de autenticacion 
def register(request):
    """
    GET: Muestra el formulario de registro vacío
    POST: Procesa el registro y redirige al login si es exitoso
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        # Construye un form vacío
        form = UserCreationForm()
    
    return render(request, "registration/register.html", {"form": form})
