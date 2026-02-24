from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    # WebBuilder
    path("", views.home, name="home"),
    path("asistente", views.assistant, name="assistant"),
    path("historial", views.history, name="history"),
    path("login", LoginView.as_view(next_page="home"), name="login"),
    path("registro", views.register, name="register"),
	
    path("preview/<int:api_request_id>", views.preview, name="preview"),
    path("preview/<int:api_request_id>/render/", views.site_render, name="site_render"),
    path("preview/<int:api_request_id>/render/regenerar/", views.site_render_regen, name="site_render_regen"),


]
