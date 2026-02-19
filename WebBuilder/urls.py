from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    # URLS PRINCIPALES
    path("", views.home, name="home"),
    path("asistente", views.assistant, name="assistant"),
    path("historial", views.history, name="history"),
    path("login", LoginView.as_view(next_page="home"), name="login"),
    path("registro", views.register, name="register"),

    # Preview (placeholder por ahora)
    path("preview/<int:api_request_id>", views.preview, name="preview"),
]
