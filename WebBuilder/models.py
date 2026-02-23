from django.db import models
from django.contrib.auth.models import User
import uuid


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

    field_mapping = models.JSONField(blank=True, null=True)                                 # Campos guardados en mapping

    plan_accepted = models.BooleanField(default=False)                                      # Aceptacion del mapping del llm

    # Representación en texto del objeto
    def __str__(self):
        return f"{self.api_url} ({self.user.username})"



# Modelo que recoge todo lo que se creara en los proyectos de django con IA
class GeneratedSite(models.Model):

    project_source = models.OneToOneField(
        APIRequest,
        on_delete=models.CASCADE,
        related_name="site",
    )

    plublic_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Snapshot del plan aceptado (para reproducibilidad)
    accepted_plan = models.JSONField()

    # Theme pack generado por IA (strings)
    theme_templates = models.JSONField(default=dict, blank=True)
    theme_css = models.TextField(blank=True, default="")
    theme_prompt = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GeneratedSite #{self.id} ({self.plublic_id})"