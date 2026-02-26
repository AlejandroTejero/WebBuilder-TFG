# Implementación Login, Registro y Logout con n8n

Mejora del sistema de autenticación de WebBuilder (26/02)

## Índice

- [Logout](#1-logout)
- [Formulario de Registro (RegisterForm)](#2-formulario-de-registro-registerform)
- [Vista de Registro y Login (auth.py)](#3-vista-de-registro-y-login-authpy)
- [URLs](#4-urls-urlspy)
- [Templates](#5-templates)


## 1. Logout

Django tiene una vista de cierre de sesión integrada llamada LogoutView. Antes no estaba registrada en el proyecto, por lo que el botón de Cerrar Sesión del navbar redirigía a la pantalla de login sin cerrar la sesión realmente.

### urls.py — añadir LogoutView

Importamos LogoutView junto a LoginView y registramos la URL /logout:
```python
from django.contrib.auth.views import LoginView, LogoutView

path('logout', LogoutView.as_view(), name='logout'),
```

Django ya tiene configurado a dónde redirigir tras el logout en settings.py:
```python
LOGOUT_REDIRECT_URL = 'login'
```

### navbar.html — cambiar el enlace por un formulario POST

El logout en Django requiere una petición POST por seguridad (evita que una página externa cierre tu sesión con un simple enlace). Sustituimos el `<a>` por un `<form>`:
```html
<form method="post" action="{% url 'logout' %}">
  {% csrf_token %}
  <button type="submit" class="wb-dropdown-item"
    style="width:100%; background:none; border:none; cursor:pointer;
           text-align:left; font:inherit; color:inherit; display:block;">
    <div class="wb-dropdown-content">
      <div class="wb-dropdown-title">Cerrar Sesión</div>
    </div>
  </button>
</form>
```

El estilo `font:inherit` y `color:inherit` es necesario porque los navegadores aplican estilos por defecto a los botones que rompen el diseño del menú.


## 2. Formulario de Registro (forms.py)

Antes se usaba `UserCreationForm` directamente, que solo pedía usuario y contraseña. Creamos nuestro propio `RegisterForm` que hereda de él y añade el campo email.

El modelo `User` de Django ya tiene el campo email, pero `UserCreationForm` no lo muestra por defecto. Al heredar de `UserCreationForm` mantenemos toda la lógica de validación de contraseñas y solo añadimos lo que necesitamos.
```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
```

- El método `save()` se sobreescribe para guardar el email en el modelo. Sin esto el campo se validaría pero no se guardaría en la base de datos.
- `commit=False` permite modificar el objeto antes de guardarlo. Después llamamos a `user.save()` manualmente.


## 3. Vista de Registro y Login (auth.py)

Este archivo centraliza toda la lógica de autenticación: registro, login y en el futuro recuperación de contraseña.

### ¿Qué es un webhook?

Un webhook es una URL que escucha peticiones. Cuando Django la llama mandándole datos en formato JSON, n8n los recibe y actúa en consecuencia (en nuestro caso, manda un email).

El flujo es:
- Usuario se registra o inicia sesión en Django
- Django llama al webhook de n8n con los datos del usuario (username, email)
- N8n recibe los datos y manda el email correspondiente

### _llamar_webhook()

Función auxiliar que hace la llamada HTTP a n8n. El `try/except` es importante: si n8n está caído o falla, el registro y el login siguen funcionando con normalidad.
```python
def _llamar_webhook(url: str, datos: dict) -> None:
    """Llama a un webhook de n8n. Si falla no interrumpe el flujo."""
    try:
        requests.post(url, json=datos, timeout=5)
    except Exception:
        pass
```

- `timeout=5` significa que si n8n no responde en 5 segundos se abandona la llamada y continúa.

### Vista de registro

Usa el nuevo `RegisterForm` y llama al webhook de registro tras guardar el usuario:
```python
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            _llamar_webhook(N8N_WEBHOOK_REGISTRO, {
                "username": user.username,
                "email":    user.email,
            })
            login(request, user)
            return redirect("home")
```

### Vista de login — WebBuilderLoginView

El login lo gestiona Django automáticamente con `LoginView`. Para interceptarlo y añadir la llamada al webhook creamos nuestra propia clase que hereda de `LoginView` y sobreescribe `form_valid`.

`form_valid` es el método que Django ejecuta cuando el usuario y contraseña son correctos. Lo sobreescribimos para colar la llamada al webhook justo antes de que Django cree la sesión.
```python
class WebBuilderLoginView(LoginView):

    def form_valid(self, form):
        user = form.get_user()
        _llamar_webhook(N8N_WEBHOOK_LOGIN, {
            "username": user.username,
            "email":    user.email,
        })
        return super().form_valid(form)
```

- `super().form_valid(form)` es la forma de llamar al método del padre en Python. Sin esta línea Django nunca crearía la sesión aunque las credenciales fueran correctas.

IMPORTANTE: Las URLs de los webhooks se rellenan cuando se configuran los workflows en n8n:
```python
N8N_WEBHOOK_REGISTRO = "TU_URL_WEBHOOK_REGISTRO"
N8N_WEBHOOK_LOGIN    = "TU_URL_WEBHOOK_LOGIN"
```


## 4. URLs (urls.py)

Dos cambios respecto a la versión anterior:
- Se añade la URL de logout con `LogoutView`
- Se sustituye `LoginView` por `WebBuilderLoginView` para que el login use nuestra vista con el webhook
```python
from django.contrib.auth.views import LogoutView
from .views.auth import WebBuilderLoginView

path('login',  WebBuilderLoginView.as_view(), name='login'),
path('logout', LogoutView.as_view(),          name='logout'),
```


## 5. Templates

### register.html

Se añade el campo email entre Usuario y Contraseña, siguiendo el mismo patrón HTML que los demás campos:
```html
<!-- Email -->
<div class="auth-field">
  <label class="auth-label" for="{{ form.email.id_for_label }}">Email</label>
  <div class="auth-input-wrap">
    <span class="auth-input-icon">✉️</span>
    {{ form.email }}
  </div>
  {% if form.email.errors %}
    <div class="auth-field-error">{{ form.email.errors.0 }}</div>
  {% endif %}
</div>
```

### login.html

Se añade el enlace de recuperar contraseña desactivado visualmente. Pendiente de implementar con n8n en una fase posterior:
```html
<!-- Recuperar contraseña — pendiente de implementar con n8n -->
<div class="auth-hint" style="text-align:center; margin-top: 8px;">
  <span style="color: #475569; cursor: not-allowed;">
    ¿Olvidaste tu contraseña?
  </span>
</div>
```


## Pendiente

- Configurar workflows en n8n: webhook de registro y webhook de login
- Rellenar `N8N_WEBHOOK_REGISTRO` y `N8N_WEBHOOK_LOGIN` en auth.py con las URLs reales
- Implementar recuperación de contraseña completa con n8n