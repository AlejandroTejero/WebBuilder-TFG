# Importa el módulo de formularios de Django
from django import forms

# Importa el modelo de usuario estándar de Django (lo usas para el registro)
from django.contrib.auth.models import User

# Importa tu modelo APIRequest para que el ModelForm sepa qué tabla/campos usar
from .models import APIRequest


# Formulario para introducir SOLO la URL de la API (nada de pegar datos)
# - ModelForm: Django construye el formulario a partir del modelo y guarda en BD con form.save()
class APIRequestForm(forms.ModelForm):

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


# Formulario personalizado de login (solo recoge datos; la autenticación real la hace la vista/login de Django)
class CustomLoginForm(forms.Form):

    # Campo usuario con un input normal y clases CSS
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombre de usuario'
    }))

    # Campo contraseña con un input de tipo password para ocultar caracteres
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))


# Formulario personalizado de registro (se basa en el modelo User)
class CustomRegisterForm(forms.ModelForm):

    # Campo contraseña (no existe como tal en el modelo User como texto plano; luego se debe usar set_password)
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))

    # Confirmación de contraseña para validar que el usuario no se equivoca
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repite la contraseña'
    }))

    # Meta define qué campos del User se piden en el registro
    class Meta:
        # Modelo sobre el que se construye el formulario
        model = User

        # Campos reales del modelo User que se van a rellenar
        fields = ['username', 'email']
