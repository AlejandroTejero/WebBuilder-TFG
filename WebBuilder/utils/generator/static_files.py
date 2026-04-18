"""
static_files.py — Scaffolding estático del proyecto Django generado.

Contiene todo lo que no requiere LLM:
  - Archivos de infraestructura (manage, settings, wsgi, urls, Dockerfile...)
  - Generación de urls.py de la app a partir de las páginas
"""
from __future__ import annotations


def build_static_files(project: str, app: str = "siteapp", design_system: dict = None, site_type: str = "other") -> dict[str, str]:
    """Archivos de infraestructura que son siempre iguales."""

    files = {}

    # ── Design system para templates de auth ─────────────────────────────────
    ds = design_system or {}
    card       = ds.get("card",           "bg-gray-900 border border-gray-700 rounded-2xl p-8")
    input_cls  = ds.get("input",          "w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500")
    btn        = ds.get("btn_primary",    "w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg transition")
    link       = ds.get("link",           "text-blue-400 hover:underline")
    text_muted = ds.get("text_muted",     "text-gray-400 text-sm")
    h1         = ds.get("h1",             "text-2xl font-bold text-white mb-6 text-center")

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

    # urls.py del proyecto
    if site_type == "portfolio":
        files[f"{project}/{project}/urls.py"] = (
            "from django.contrib import admin\n"
            "from django.urls import path, include\n"
            "\n"
            "urlpatterns = [\n"
            "    path('admin/', admin.site.urls),\n"
            f"    path('', include('{app}.urls')),\n"
            "]\n"
        )
    else:
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

    # entrypoint.sh — seed_users solo para tipos con auth
    _seed_users_block = (
        "echo '--- Creando usuarios ---'\n"
        "python manage.py seed_users || echo 'AVISO: seed_users falló, continuando'\n"
        "\n"
    ) if site_type != "portfolio" else ""

    files[f"{project}/entrypoint.sh"] = (
        "#!/bin/sh\n"
        "set -e\n"
        "\n"
        "echo '--- Generando migraciones ---'\n"
        "python manage.py makemigrations siteapp --noinput\n"
        "\n"
        "echo '--- Aplicando migraciones ---'\n"
        "python manage.py migrate --noinput\n"
        "\n"
        "echo '--- Cargando datos ---'\n"
        "if python manage.py load_data; then\n"
        "    echo '--- Verificando datos cargados ---'\n"
        "    COUNT=$(python manage.py shell -c \"from siteapp.models import Item; print(Item.objects.count())\" 2>/dev/null)\n"
        "    if [ \"$COUNT\" = \"0\" ] || [ -z \"$COUNT\" ]; then\n"
        "        echo 'ERROR CRITICO: load_data se ejecutó pero no hay datos en la BD.'\n"
        "        echo 'Posibles causas: URL de API incorrecta, API sin datos, error silencioso en la carga.'\n"
        "        exit 1\n"
        "    fi\n"
        "    echo \"OK: $COUNT registros cargados correctamente.\"\n"
        "else\n"
        "    echo 'ERROR CRITICO: load_data falló. El sitio no arrancará sin datos.'\n"
        "    exit 1\n"
        "fi\n"
        "\n"
        + _seed_users_block +
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

    # Auth — solo para tipos que lo necesitan
    if site_type != "portfolio":
        files[f"{project}/templates/registration/login.html"] = (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='min-h-screen flex items-center justify-center'>\n"
            f"  <div class='{card} w-full max-w-md'>\n"
            f"    <h1 class='{h1}'>Iniciar sesión</h1>\n"
            "    {% if form.errors %}\n"
            "      <div class='bg-red-900/40 border border-red-700 text-red-300 rounded-lg p-3 mb-4 text-sm'>\n"
            "        Usuario o contraseña incorrectos.\n"
            "      </div>\n"
            "    {% endif %}\n"
            "    <form method='post'>\n"
            "      {% csrf_token %}\n"
            "      <div class='mb-4'>\n"
            f"        <label class='block {text_muted} mb-1'>Usuario</label>\n"
            f"        <input type='text' name='username' autofocus class='{input_cls}'>\n"
            "      </div>\n"
            "      <div class='mb-6'>\n"
            f"        <label class='block {text_muted} mb-1'>Contraseña</label>\n"
            f"        <input type='password' name='password' class='{input_cls}'>\n"
            "      </div>\n"
            "      <input type='hidden' name='next' value='{{ next }}'>\n"
            f"      <button type='submit' class='{btn} w-full mt-2'>Entrar</button>\n"
            "    </form>\n"
            f"    <p class='text-center {text_muted} mt-4'>\n"
            f"      ¿No tienes cuenta? <a href='{{% url \"register\" %}}' class='{link}'>Regístrate</a>\n"
            "    </p>\n"
            "  </div>\n"
            "</div>\n"
            "{% endblock %}\n"
        )

        files[f"{project}/templates/registration/logged_out.html"] = (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='min-h-screen flex items-center justify-center'>\n"
            f"  <div class='{card} w-full max-w-md text-center'>\n"
            f"    <h1 class='{h1}'>Sesión cerrada</h1>\n"
            f"    <p class='{text_muted} mb-6'>Has cerrado sesión correctamente.</p>\n"
            f"    <a href='{{% url \"login\" %}}' class='{btn} inline-block px-6'>Volver a entrar</a>\n"
            "  </div>\n"
            "</div>\n"
            "{% endblock %}\n"
        )

        files[f"{project}/templates/registration/register.html"] = (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='min-h-screen flex items-center justify-center'>\n"
            f"  <div class='{card} w-full max-w-md'>\n"
            f"    <h1 class='{h1}'>Crear cuenta</h1>\n"
            "    {% if form.errors %}\n"
            "      <div class='bg-red-900/40 border border-red-700 text-red-300 rounded-lg p-3 mb-4 text-sm'>\n"
            "        Corrige los errores del formulario.\n"
            "      </div>\n"
            "    {% endif %}\n"
            "    <form method='post'>\n"
            "      {% csrf_token %}\n"
            "      {% for field in form %}\n"
            "        <div class='mb-4'>\n"
            f"          <label class='block {text_muted} mb-1'>{{{{ field.label }}}}</label>\n"
            f"          <input type='{{{{ field.field.widget.input_type }}}}' name='{{{{ field.html_name }}}}'\n"
            "                 value='{{ field.value|default:\"\" }}'\n"
            f"                 class='{input_cls}'>\n"
            "          {% if field.errors %}\n"
            "            <p class='text-red-400 text-xs mt-1'>{{ field.errors|join:', ' }}</p>\n"
            "          {% endif %}\n"
            "        </div>\n"
            "      {% endfor %}\n"
            f"      <button type='submit' class='{btn} w-full mt-2'>Registrarse</button>\n"
            "    </form>\n"
            f"    <p class='text-center {text_muted} mt-4'>\n"
            f"      ¿Ya tienes cuenta? <a href='{{% url \"login\" %}}' class='{link}'>Inicia sesión</a>\n"
            "    </p>\n"
            "  </div>\n"
            "</div>\n"
            "{% endblock %}\n"
        )

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

def build_app_urls(pages: list[dict], app: str = "siteapp", site_type: str = "other") -> str:
    """Genera urls.py de la app a partir de las páginas decididas por el LLM."""
    if site_type == "portfolio":
        lines = [
            "from django.urls import path",
            "from . import views",
            "",
            "urlpatterns = [",
        ]
    else:
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