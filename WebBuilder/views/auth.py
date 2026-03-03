from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
import requests

from ..forms import RegisterForm


N8N_WEBHOOK_REGISTRO = "http://localhost:5678/webhook/WebBuilder-Register"
N8N_WEBHOOK_LOGIN    = "http://localhost:5678/webhook/WebBuilder-Login"


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
        request = self.request

        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR", "desconocida")
        )

        _llamar_webhook(N8N_WEBHOOK_LOGIN, {
            "username": user.username,
            "email":    user.email,
            "ip":       ip,
            "dispositivo": request.META.get("HTTP_USER_AGENT", "desconocido"),
            "hora":     __import__("datetime").datetime.now().strftime("%d/%m/%Y %H:%M"),
        })

        return super().form_valid(form)