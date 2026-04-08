from django.db import models
from django.contrib.auth.models import User
import uuid
from encrypted_model_fields.fields import EncryptedCharField


# Modelo para cada peticion URL
class APIRequest(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_requests')   # Usuario dueño
    api_url = models.URLField("URL de la API")                                              # URL introducida
    input_type = models.CharField(
        max_length=10,
        choices=[("url", "URL"), ("file", "Fichero")],
        default="url",
    )   

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



class GeneratedSite(models.Model):

    STATUS_CHOICES = [
        ("pending",    "Pendiente"),
        ("generating", "Generando"),
        ("ready",      "Listo"),
        ("error",      "Error"),
    ]

    project_source = models.OneToOneField(
        APIRequest,
        on_delete=models.CASCADE,
        related_name="site",
    )

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Snapshot del plan aceptado (para reproducibilidad)
    accepted_plan = models.JSONField()

    # Archivos del proyecto generado {ruta: contenido}
    project_files = models.JSONField(default=dict, blank=True)

    # Nombre del proyecto Django generado (slug del título)
    project_name = models.SlugField(max_length=80, blank=True, default="")

    # URL del preview levantado por n8n
    preview_url = models.URLField(blank=True, null=True)

    # Estado de la generación
    generation_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    generation_error = models.TextField(blank=True, default="")

    # Estado del despliegue vía n8n + Docker
    DEPLOY_STATUS_CHOICES = [
        ("idle",      "Sin desplegar"),
        ("deploying", "Desplegando"),
        ("done",      "Desplegado"),
        ("error",     "Error"),
    ]
    deploy_status = models.CharField(
        max_length=30,
        choices=DEPLOY_STATUS_CHOICES,
        default="idle",
    )
    deploy_error = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GeneratedSite #{self.id} — {self.project_name} ({self.public_id})"


class GenerationLog(models.Model):
    site = models.ForeignKey(
        GeneratedSite,
        on_delete=models.CASCADE,
        related_name='generation_logs'
    )
    step = models.CharField(max_length=50)          # 'models', 'views', 'template_home'...
    llm_model = models.CharField(max_length=100)    # 'llama-3.3-70b-instruct:free'
    system_prompt = models.TextField(blank=True)
    user_prompt = models.TextField(blank=True)
    raw_output = models.TextField(blank=True)
    consistency_errors = models.JSONField(default=list)
    had_retry = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.step} — {self.llm_model} ({self.created_at:%Y-%m-%d %H:%M})'
    
    
class SiteVersion(models.Model):

    site = models.ForeignKey(
        GeneratedSite,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version_number = models.PositiveIntegerField()
    project_files  = models.JSONField(default=dict)
    label          = models.CharField(max_length=100, blank=True, default="")
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']   # La más reciente primero

    def __str__(self):
        return f'v{self.version_number} — {self.site.project_name} ({self.created_at:%d/%m/%Y %H:%M})'
    
    
class SiteUser(models.Model):

    ROLE_CHOICES = [
        ("super",  "Superusuario"),
        ("normal", "Usuario normal"),
    ]

    site = models.ForeignKey(
        GeneratedSite,
        on_delete=models.CASCADE,
        related_name='site_users'
    )

    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    role     = models.CharField(max_length=10, choices=ROLE_CHOICES, default="normal")

    class Meta:
        unique_together = [('site', 'username')]  # No duplicados por proyecto

    def __str__(self):
        return f'{self.username} ({self.role}) — {self.site.project_name}'
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # LLM personalizado (opcional)
    custom_llm_base_url = models.URLField(blank=True, default="")
    custom_llm_model    = models.CharField(max_length=200, blank=True, default="")
    custom_llm_api_key  = EncryptedCharField(max_length=500, blank=True, default="")

    def __str__(self):
        return f"Perfil de {self.user.username}"