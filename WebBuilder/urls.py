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
	
    # Projects
    path("sites/<int:site_id>/", views.site_home, name="site_home"),
    path("sites/<int:site_id>/item/<int:item_index>/", views.site_detail, name="site_detail"),
]
