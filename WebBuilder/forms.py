# Importa el módulo de formularios de Django
from django import forms

# Importa el modelo de usuario estándar de Django (lo usas para el registro)
from django.contrib.auth.models import User

# Importa tu modelo APIRequest para que el ModelForm sepa qué tabla/campos usar
from .models import APIRequest


# Formulario para introducir SOLO la URL de la API (nada de pegar datos)
# - ModelForm: Django construye el formulario a partir del modelo y guarda en BD con form.save()
class APIRequestForm(forms.ModelForm):

    # Campo extra del formulario (NO pertenece al modelo) -> LLM
    user_prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 4,
            "class": "form-control",  # opcional, para que se vea igual que api_url
            "placeholder": "Describe qué web quieres y cómo la quieres..."
        })
    )

    # Meta define cómo se construye el formulario a partir del modelo
    class Meta:

        # Le decimos a Django qué modelo está “detrás” del formulario
        model = APIRequest

        # Campos del modelo que queremos mostrar en el formulario (solo api_url)
        fields = ['api_url']

        # Widgets: personalizan cómo se renderiza el input en HTML y qué atributos tiene
        widgets = {
            'api_url': forms.URLInput(attrs={
                # Clase CSS para que encaje con tu diseño (bootstrap-like)
                'class': 'form-control',
                # Texto de ejemplo dentro del input
                'placeholder': 'Introduce la URL de la API',
            })
        }

        # Etiquetas: aquí lo dejas vacío porque probablemente pones el texto en el placeholder
        labels = {
            'api_url': ''
        }