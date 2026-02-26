from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
import requests

from ..forms import RegisterForm


N8N_WEBHOOK_REGISTRO = "TU_URL_WEBHOOK_REGISTRO"
N8N_WEBHOOK_LOGIN    = "TU_URL_WEBHOOK_LOGIN"


def _llamar_webhook(url: str, datos: dict) -> None:
    """Llama a un webhook de n8n. Si falla no interrumpe el flujo."""
    try:
        requests.post(url, json=datos, timeout=5)
    except Exception:
        pass


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            _llamar_webhook(N8N_WEBHOOK_REGISTRO, {
                "username": user.username,
                "email":    user.email,
            })

            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


class WebBuilderLoginView(LoginView):

    def form_valid(self, form):
        user = form.get_user()

        _llamar_webhook(N8N_WEBHOOK_LOGIN, {
            "username": user.username,
            "email":    user.email,
        })

        return super().form_valid(form)