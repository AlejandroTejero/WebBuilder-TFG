import datetime
import logging
import requests

from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse

logger = logging.getLogger(__name__)


def _llamar_webhook(url: str, datos: dict) -> None:
    """Llama a un webhook de n8n. Si falla no interrumpe el flujo."""
    try:
        requests.post(url, json=datos, timeout=5)
    except Exception:
        pass


class WebBuilderSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """
        Se llama cuando un usuario OAuth se registra por primera vez.
        Creamos su cuenta y disparamos el webhook de registro de n8n.
        """
        user = super().save_user(request, sociallogin, form)

        _llamar_webhook(settings.N8N_WEBHOOK_REGISTRO, {
            "username": user.username,
            "email":    user.email,
        })

        return user

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        """
        Se llama cuando falla el login OAuth.
        Logueamos el error y redirigimos al login en vez de mostrar la página fea de allauth.
        """
        logger.error(
            "[OAuth] Error en provider=%s | error=%s | exception=%s",
            provider, error, exception
        )
        raise ImmediateHttpResponse(redirect("login"))

    def pre_social_login(self, request, sociallogin):
        """
        Se llama en cada login OAuth (tanto registro como accesos posteriores).
        Disparamos el webhook de login de n8n.
        """
        user = sociallogin.user

        # Si el usuario aún no tiene pk es que todavía no existe en BD
        # (primer login = registro), el webhook de registro ya lo cubre save_user
        if not user.pk:
            return

        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR", "desconocida")
        )

        _llamar_webhook(settings.N8N_WEBHOOK_LOGIN, {
            "username":   user.username,
            "email":      user.email,
            "ip":         ip,
            "dispositivo": request.META.get("HTTP_USER_AGENT", "desconocido"),
            "hora":       datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        })