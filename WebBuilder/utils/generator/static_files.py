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

    # settings.py
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
        "    'DIRS': [],\n"
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

    # urls.py del proyecto (incluye la app)
    files[f"{project}/{project}/urls.py"] = (
        "from django.contrib import admin\n"
        "from django.urls import path, include\n"
        "\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        f"    path('', include('{app}.urls')),\n"
        "]\n"
    )

    # requirements.txt
    files[f"{project}/requirements.txt"] = (
        "django>=4.2,<6.0\n"
        "requests>=2.28\n"
        "gunicorn>=21.0\n"
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

    # entrypoint.sh
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
        "python manage.py load_data\n"
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

    return files


def build_app_urls(pages: list[dict], app: str = "siteapp") -> str:
    """Genera urls.py de la app a partir de las páginas decididas por el LLM."""
    lines = [
        "from django.urls import path",
        "from . import views",
        "",
        "urlpatterns = [",
    ]
    for page in pages:
        url = page["url"].lstrip("/")
        view_name = page["view_name"]
        name = page["name"]

        # La página de detalle tiene <pk> en la url
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
