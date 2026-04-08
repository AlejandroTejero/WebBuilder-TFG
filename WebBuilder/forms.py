from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import APIRequest
from .models import APIRequest, UserProfile

class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "auth-input",
            "placeholder": "tu@email.com",
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# Formulario para introducir SOLO la URL de la API
class APIRequestForm(forms.ModelForm):

    user_prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 4,
            "class": "form-control",
            "placeholder": "Describe qué web quieres y cómo la quieres...",
        })
    )

    file_input = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".json,.xml",
        })
    )


    class Meta:
        model = APIRequest
        fields = ["api_url", "file_input"]
        widgets = {
            "api_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "Introduce la URL de la API",
            })
        }
        labels = {
            "api_url": ""
        }

class UserProfileForm(forms.ModelForm):

    custom_llm_api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "sk-...",
            "autocomplete": "off",
        }),
        label="API Key",
    )

    class Meta:
        model = UserProfile
        fields = ["custom_llm_base_url", "custom_llm_model", "custom_llm_api_key"]
        widgets = {
            "custom_llm_base_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://api.openai.com/v1",
            }),
            "custom_llm_model": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "gpt-4o",
            }),
        }
        labels = {
            "custom_llm_base_url": "Base URL del proveedor",
            "custom_llm_model": "Nombre del modelo",
        }