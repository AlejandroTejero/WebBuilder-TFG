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
    path("edit/<int:api_request_id>/render/", views.site_render, name="site_render"),
    path("edit/<int:api_request_id>/render/<int:item_index>/", views.site_render_detail, name="site_render_detail"),
    path("edit/<int:api_request_id>/render/regenerar/", views.site_render_regen, name="site_render_regen"),

]
