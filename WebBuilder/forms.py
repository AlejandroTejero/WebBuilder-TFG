from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import APIRequest


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
        fields = ["api_url"]
        widgets = {
            "api_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "Introduce la URL de la API",
            })
        }
        labels = {
            "api_url": ""
        }
        fields = ["api_url", "file_input"]