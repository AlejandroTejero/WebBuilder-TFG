"""
static_files.py — Scaffolding estático del proyecto Django generado.

Contiene todo lo que no requiere LLM:
  - Archivos de infraestructura (manage, settings, wsgi, urls, Dockerfile...)
  - Generación de urls.py de la app a partir de las páginas
"""
from __future__ import annotations


def build_static_files(project: str, app: str = "siteapp") -> dict[str, str]:
    """Archivos de infraestructura que son siempre iguales."""

    files = {}

    # manage.py
    files[f"{project}/manage.py"] = (
        "#!/usr/bin/env python\n"
        "import os, sys\n"
        "\n"
        "def main():\n"
        f"    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project}.settings')\n"
        "    from django.core.management import execute_from_command_line\n"
        "    execute_from_command_line(sys.argv)\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )

    # settings.py — incluye LOGIN_URL, LOGIN_REDIRECT_URL y LOGOUT_REDIRECT_URL
    files[f"{project}/{project}/settings.py"] = (
        "from pathlib import Path\n"
        "\n"
        "BASE_DIR = Path(__file__).resolve().parent.parent\n"
        "SECRET_KEY = 'dev-secret-key-change-in-production'\n"
        "DEBUG = True\n"
        "ALLOWED_HOSTS = ['*']\n"
        "\n"
        "INSTALLED_APPS = [\n"
        "    'django.contrib.admin',\n"
        "    'django.contrib.auth',\n"
        "    'django.contrib.contenttypes',\n"
        "    'django.contrib.sessions',\n"
        "    'django.contrib.messages',\n"
        "    'django.contrib.staticfiles',\n"
        f"    '{app}',\n"
        "]\n"
        "\n"
        "MIDDLEWARE = [\n"
        "    'django.middleware.security.SecurityMiddleware',\n"
        "    'django.contrib.sessions.middleware.SessionMiddleware',\n"
        "    'django.middleware.common.CommonMiddleware',\n"
        "    'django.middleware.csrf.CsrfViewMiddleware',\n"
        "    'django.contrib.auth.middleware.AuthenticationMiddleware',\n"
        "    'django.contrib.messages.middleware.MessageMiddleware',\n"
        "    'django.middleware.clickjacking.XFrameOptionsMiddleware',\n"
        "]\n"
        "\n"
        f"ROOT_URLCONF = '{project}.urls'\n"
        "\n"
        "TEMPLATES = [{\n"
        "    'BACKEND': 'django.template.backends.django.DjangoTemplates',\n"
        "    'DIRS': [BASE_DIR / 'templates'],\n"
        "    'APP_DIRS': True,\n"
        "    'OPTIONS': {'context_processors': [\n"
        "        'django.template.context_processors.request',\n"
        "        'django.contrib.auth.context_processors.auth',\n"
        "        'django.contrib.messages.context_processors.messages',\n"
        "    ]},\n"
        "}]\n"
        "\n"
        f"WSGI_APPLICATION = '{project}.wsgi.application'\n"
        "\n"
        "DATABASES = {'default': {\n"
        "    'ENGINE': 'django.db.backends.sqlite3',\n"
        "    'NAME': BASE_DIR / 'db.sqlite3',\n"
        "}}\n"
        "\n"
        "LANGUAGE_CODE = 'es-es'\n"
        "TIME_ZONE = 'Europe/Madrid'\n"
        "USE_I18N = True\n"
        "USE_TZ = True\n"
        "STATIC_URL = 'static/'\n"
        "DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'\n"
        "\n"
        "# Auth\n"
        "LOGIN_URL = 'login'\n"
        "LOGIN_REDIRECT_URL = 'home'\n"
        "LOGOUT_REDIRECT_URL = 'login'\n"
    )

    # wsgi.py
    files[f"{project}/{project}/wsgi.py"] = (
        "import os\n"
        "from django.core.wsgi import get_wsgi_application\n"
        f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project}.settings')\n"
        "application = get_wsgi_application()\n"
    )

    # __init__.py del proyecto
    files[f"{project}/{project}/__init__.py"] = ""

    # urls.py del proyecto — incluye auth de Django
    files[f"{project}/{project}/urls.py"] = (
        "from django.contrib import admin\n"
        "from django.urls import path, include\n"
        "\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "    path('accounts/', include('django.contrib.auth.urls')),\n"
        f"    path('', include('{app}.urls')),\n"
        "]\n"
    )

    # requirements.txt
    files[f"{project}/requirements.txt"] = (
        "django>=4.2,<6.0\n"
        "requests>=2.28\n"
        "gunicorn>=21.0\n"
        "xmltodict>=0.13\n"
    )

    # Dockerfile
    files[f"{project}/Dockerfile"] = (
        "FROM python:3.12-slim\n"
        "\n"
        "WORKDIR /app\n"
        "\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "\n"
        "COPY . .\n"
        "\n"
        "EXPOSE 8000\n"
        "\n"
        "COPY entrypoint.sh /entrypoint.sh\n"
        "RUN chmod +x /entrypoint.sh\n"
        "\n"
        'CMD ["/entrypoint.sh"]\n'
    )

    # entrypoint.sh — incluye seed_users
    # entrypoint.sh — incluye seed_users
    files[f"{project}/entrypoint.sh"] = (
        "#!/bin/sh\n"
        "\n"
        "echo '--- Generando migraciones ---'\n"
        "python manage.py makemigrations siteapp --noinput\n"
        "\n"
        "echo '--- Aplicando migraciones ---'\n"
        "python manage.py migrate --noinput\n"
        "\n"
        "echo '--- Cargando datos ---'\n"
        "python manage.py load_data || echo 'AVISO: load_data falló, el sitio arrancará sin datos'\n"
        "\n"
        "echo '--- Creando usuarios ---'\n"
        "python manage.py seed_users || echo 'AVISO: seed_users falló, continuando'\n"
        "\n"
        "echo '--- Arrancando servidor ---'\n"
        f"gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 "
        f"{project}.wsgi:application\n"
    )

    # app __init__.py y apps.py
    files[f"{project}/{app}/__init__.py"] = ""
    files[f"{project}/{app}/apps.py"] = (
        "from django.apps import AppConfig\n"
        "\n"
        "class SiteappConfig(AppConfig):\n"
        "    default_auto_field = 'django.db.models.BigAutoField'\n"
        f"    name = '{app}'\n"
    )

    # admin.py básico
    files[f"{project}/{app}/admin.py"] = (
        "from django.contrib import admin\n"
        "from .models import Item\n"
        "\n"
        "admin.site.register(Item)\n"
    )

    # management command __init__.py
    files[f"{project}/{app}/management/__init__.py"] = ""
    files[f"{project}/{app}/management/commands/__init__.py"] = ""

    # ── Templates de autenticación ────────────────────────────────────────────
    # Django busca registration/login.html y registration/logged_out.html
    # en DIRS, así que los ponemos en la carpeta raíz templates/

    files[f"{project}/templates/registration/login.html"] = (
        "{% extends 'base.html' %}\n"
        "{% block content %}\n"
        "<div class='min-h-screen flex items-center justify-center'>\n"
        "  <div class='bg-gray-900 border border-gray-700 rounded-2xl p-8 w-full max-w-md'>\n"
        "    <h1 class='text-2xl font-bold text-white mb-6 text-center'>Iniciar sesión</h1>\n"
        "    {% if form.errors %}\n"
        "      <div class='bg-red-900/40 border border-red-700 text-red-300 rounded-lg p-3 mb-4 text-sm'>\n"
        "        Usuario o contraseña incorrectos.\n"
        "      </div>\n"
        "    {% endif %}\n"
        "    <form method='post'>\n"
        "      {% csrf_token %}\n"
        "      <div class='mb-4'>\n"
        "        <label class='block text-gray-400 text-sm mb-1'>Usuario</label>\n"
        "        <input type='text' name='username' autofocus\n"
        "               class='w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500'>\n"
        "      </div>\n"
        "      <div class='mb-6'>\n"
        "        <label class='block text-gray-400 text-sm mb-1'>Contraseña</label>\n"
        "        <input type='password' name='password'\n"
        "               class='w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500'>\n"
        "      </div>\n"
        "      <input type='hidden' name='next' value='{{ next }}'>\n"
        "      <button type='submit'\n"
        "              class='w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg transition'>\n"
        "        Entrar\n"
        "      </button>\n"
        "    </form>\n"
        "    <p class='text-center text-gray-500 text-sm mt-4'>\n"
        "      ¿No tienes cuenta? <a href='{% url \"register\" %}' class='text-blue-400 hover:underline'>Regístrate</a>\n"
        "    </p>\n"
        "  </div>\n"
        "</div>\n"
        "{% endblock %}\n"
    )

    files[f"{project}/templates/registration/logged_out.html"] = (
        "{% extends 'base.html' %}\n"
        "{% block content %}\n"
        "<div class='min-h-screen flex items-center justify-center'>\n"
        "  <div class='bg-gray-900 border border-gray-700 rounded-2xl p-8 w-full max-w-md text-center'>\n"
        "    <h1 class='text-2xl font-bold text-white mb-4'>Sesión cerrada</h1>\n"
        "    <p class='text-gray-400 mb-6'>Has cerrado sesión correctamente.</p>\n"
        "    <a href='{% url \"login\" %}'\n"
        "       class='bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded-lg transition'>\n"
        "      Volver a entrar\n"
        "    </a>\n"
        "  </div>\n"
        "</div>\n"
        "{% endblock %}\n"
    )

    files[f"{project}/templates/registration/register.html"] = (
        "{% extends 'base.html' %}\n"
        "{% block content %}\n"
        "<div class='min-h-screen flex items-center justify-center'>\n"
        "  <div class='bg-gray-900 border border-gray-700 rounded-2xl p-8 w-full max-w-md'>\n"
        "    <h1 class='text-2xl font-bold text-white mb-6 text-center'>Crear cuenta</h1>\n"
        "    {% if form.errors %}\n"
        "      <div class='bg-red-900/40 border border-red-700 text-red-300 rounded-lg p-3 mb-4 text-sm'>\n"
        "        Corrige los errores del formulario.\n"
        "      </div>\n"
        "    {% endif %}\n"
        "    <form method='post'>\n"
        "      {% csrf_token %}\n"
        "      {% for field in form %}\n"
        "        <div class='mb-4'>\n"
        "          <label class='block text-gray-400 text-sm mb-1'>{{ field.label }}</label>\n"
        "          <input type='{{ field.field.widget.input_type }}' name='{{ field.html_name }}'\n"
        "                 value='{{ field.value|default:\"\" }}'\n"
        "                 class='w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500'>\n"
        "          {% if field.errors %}\n"
        "            <p class='text-red-400 text-xs mt-1'>{{ field.errors|join:', ' }}</p>\n"
        "          {% endif %}\n"
        "        </div>\n"
        "      {% endfor %}\n"
        "      <button type='submit'\n"
        "              class='w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg transition mt-2'>\n"
        "        Registrarse\n"
        "      </button>\n"
        "    </form>\n"
        "    <p class='text-center text-gray-500 text-sm mt-4'>\n"
        "      ¿Ya tienes cuenta? <a href='{% url \"login\" %}' class='text-blue-400 hover:underline'>Inicia sesión</a>\n"
        "    </p>\n"
        "  </div>\n"
        "</div>\n"
        "{% endblock %}\n"
    )

    # Vista de registro en la app
    files[f"{project}/{app}/auth_views.py"] = (
        "from django.shortcuts import render, redirect\n"
        "from django.contrib.auth.forms import UserCreationForm\n"
        "from django.contrib.auth import login\n"
        "\n"
        "def register(request):\n"
        "    if request.method == 'POST':\n"
        "        form = UserCreationForm(request.POST)\n"
        "        if form.is_valid():\n"
        "            user = form.save()\n"
        "            login(request, user)\n"
        "            return redirect('home')\n"
        "    else:\n"
        "        form = UserCreationForm()\n"
        "    return render(request, 'registration/register.html', {'form': form})\n"
    )

    return files


def build_app_urls(pages: list[dict], app: str = "siteapp") -> str:
    """Genera urls.py de la app a partir de las páginas decididas por el LLM."""
    lines = [
        "from django.urls import path",
        "from . import views",
        "from .auth_views import register",
        "",
        "urlpatterns = [",
        "    path('register/', register, name='register'),",
    ]
    for page in pages:
        url = page["url"].lstrip("/")
        view_name = page["view_name"]
        name = page["name"]

        if page.get("is_detail"):
            url = url.replace("<pk>", "<int:pk>").rstrip("/") + "/"
            lines.append(f"    path('{url}', views.{view_name}, name='{name}'),")
        else:
            if url and not url.endswith("/"):
                url += "/"
            lines.append(f"    path('{url}', views.{view_name}, name='{name}'),")

    lines.append("]")
    lines.append("")
    return "\n".join(lines)