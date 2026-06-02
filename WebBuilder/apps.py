from django.apps import AppConfig


class WebbuilderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WebBuilder'

    def ready(self):
        # Registra las señales al arrancar Django, para crear usuario con Oauth
        import WebBuilder.signals