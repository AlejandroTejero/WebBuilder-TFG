from django.db import models
from django.contrib.auth.models import User


# Modelo para cada peticion URL
class APIRequest(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_requests')   # Usuario dueño
    api_url = models.URLField("URL de la API")                                              # URL introducida
    date = models.DateTimeField(auto_now_add=True)                                          # Fecha del análisis
    raw_data = models.TextField(blank=True, null=True)                                      # Datos en crudo (raw)
    parsed_data = models.JSONField(blank=True, null=True)                                   # Datos parseados

    # Posibles estados del analisis
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("processed", "Procesada"),
        ("error", "Error"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")     # Estado del analisis
    response_summary = models.TextField(blank=True, null=True)                              # Resumen del analisis
    error_message = models.TextField(blank=True, null=True)                                 # Mensaje tras el analisis

    field_mapping = models.JSONField(blank=True, null=True)                                 # Estructura de campos guardados

    # Representación en texto del objeto
    def __str__(self):
        return f"{self.api_url} ({self.user.username})"
