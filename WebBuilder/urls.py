from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .views.auth import WebBuilderLoginView

urlpatterns = [
    path("", views.home, name="home"),
    path("asistente", views.assistant, name="assistant"),
    path("historial", views.history, name="history"),
	
	#path("login", LoginView.as_view(), name="login"),
    path("login", WebBuilderLoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("registro", views.register, name="register"),
	
    path("edit/<int:api_request_id>", views.edit, name="edit"),
	path("site/<int:api_request_id>", views.site_render, name="site_render"),

    path("site/<int:api_request_id>/generate/", views.site_generate, name="site_generate"),
    path("site/<int:api_request_id>/download/", views.site_download_zip, name="site_download_zip"),
    path("site/<int:api_request_id>/status/", views.site_status, name="site_status"),
]
