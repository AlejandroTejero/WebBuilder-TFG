from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .views.auth import WebBuilderLoginView


urlpatterns = [
    path("", views.home, name="home"),
    path("asistente", views.assistant, name="assistant"),
    path('metricas/', views.metrics_view, name='metrics'),
	path("perfil", views.profile, name="profile"),

    path("historial", views.history, name="history"),
    path("historial/analisis", views.history_analysis, name="history_analysis"),
    path("historial/sitios", views.history_sites, name="history_sites"),
    path("historial/eliminar/<int:api_request_id>", views.delete_analysis, name="delete_analysis"),
    path("historial/sitios/eliminar/<int:site_id>", views.delete_site, name="delete_site"),
	
    #path("login", LoginView.as_view(), name="login"),
    path("login", WebBuilderLoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("registro", views.register, name="register"),
	
    path("edit/<int:api_request_id>", views.edit, name="edit"),
	path("site/<int:api_request_id>", views.site_render, name="site_render"),

    path("site/<int:api_request_id>/generate/", views.site_generate, name="site_generate"),
    path("site/<int:api_request_id>/download/", views.site_download_zip, name="site_download_zip"),
    path("site/<int:api_request_id>/status/", views.site_status, name="site_status"),
	
    path("site/<int:api_request_id>/deploy/", views.site_deploy, name="site_deploy"),
    path("site/<int:api_request_id>/deploy-status/", views.site_deploy_status, name="site_deploy_status"),
	
    path("site/<int:api_request_id>/update-file/", views.site_update_file, name="site_update_file"),
    path("site/<int:api_request_id>/refine/", views.site_refine_file, name="site_refine_file"),
		
    path("site/<int:api_request_id>/versions/", views.site_versions, name="site_versions"),
    path("site/<int:api_request_id>/versions/<int:version_id>/restore/", views.site_version_restore, name="site_version_restore"),
	path("site/<int:api_request_id>/versions/<int:version_id>/download/", views.site_version_download, name="site_version_download"),

    path("site/<int:api_request_id>/users/save/", views.site_users_save, name="site_users_save"),
]
