"""
project_generator.py — Orquestador de la generación del proyecto Django completo.

Flujo:
  1. LLM decide la estructura de páginas (prompt_pages_structure)
  2. LLM genera models.py
  3. LLM genera views.py
  4. LLM genera base.html
  5. LLM genera un template HTML por cada página
  6. LLM genera load_data.py (management command)
  7. Se ensamblan los archivos fijos (settings, manage, urls, Dockerfile...)
  8. Se devuelve dict {ruta: contenido} listo para guardar en GeneratedSite.project_files
"""
from __future__ import annotations

import time
import logging
from django.utils.text import slugify

from ..llm.client import chat_completion, LLMError
from ..llm.llm_utils import parse_llm_json
from ..llm.generator_prompts import (
    prompt_pages_structure,
    prompt_models,
    prompt_views,
    prompt_base_template,
    prompt_template,
    prompt_load_data,
)

from ..llm.field_extractor import extract_model_fields
from ..llm.consistency_checker import check_consistency
from ..llm.enrich_prompt import enrich_user_prompt

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# ARCHIVOS FIJOS (sin LLM)
# ──────────────────────────────────────────────────────────────────────────────

def _fixed_files(project: str, app: str = "siteapp") -> dict[str, str]:
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

# ELIMINAR, LAS MIGRACIONES YA SE GENERAN CON LLM ----------------------------------------------

def _generate_initial_migration(models_code: str, app: str = "siteapp") -> str:
    """
    Genera un 0001_initial.py básico parseando los campos del models.py generado.
    Soporta CharField, TextField, IntegerField, FloatField, BooleanField,
    DateTimeField, URLField, EmailField, DecimalField.
    Siempre añade id AutoField y created_at DateTimeField si no están presentes.
    """
    import re

    field_type_map = {
        "CharField":      "models.CharField",
        "TextField":      "models.TextField",
        "IntegerField":   "models.IntegerField",
        "FloatField":     "models.FloatField",
        "BooleanField":   "models.BooleanField",
        "DateTimeField":  "models.DateTimeField",
        "URLField":       "models.URLField",
        "EmailField":     "models.EmailField",
        "DecimalField":   "models.DecimalField",
        "PositiveIntegerField": "models.PositiveIntegerField",
    }

    # Extraer líneas de campos del models.py
    field_lines = []
    in_model = False
    for line in models_code.splitlines():
        stripped = line.strip()
        if re.match(r"class \w+\(models\.Model\)", stripped):
            in_model = True
            continue
        if in_model:
            # Detectar fin de clase
            if stripped and not stripped.startswith("#") and not stripped.startswith("def") \
               and not stripped.startswith("class") and "=" in stripped:
                # Es una línea de campo
                field_match = re.match(r"(\w+)\s*=\s*models\.(\w+)\((.*)\)", stripped)
                if field_match:
                    fname, ftype, fargs = field_match.groups()
                    if fname in ("id",):
                        continue
                    if ftype in field_type_map:
                        field_lines.append((fname, ftype, fargs))
            elif stripped.startswith("class ") and in_model:
                break

    # Construir las líneas de campos para la migración
    migration_fields = [
        "                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),",
    ]
    for fname, ftype, fargs in field_lines:
        migration_fields.append(f"                ('{fname}', models.{ftype}({fargs})),")

    # Asegurar created_at si no está
    has_created_at = any(f[0] == "created_at" for f in field_lines)
    if not has_created_at:
        migration_fields.append(
            "                ('created_at', models.DateTimeField(auto_now_add=True)),"
        )

    fields_str = "\n".join(migration_fields)

    return f"""from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
{fields_str}
            ],
        ),
    ]
"""


def _app_urls(pages: list[dict], app: str = "siteapp") -> str:
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


# ──────────────────────────────────────────────────────────────────────────────
# LLAMADA AL LLM CON FALLBACK
# ──────────────────────────────────────────────────────────────────────────────

def _llm_call(system: str, user_text: str, label: str, temperature: float = 0.3) -> str:
    try:
        time.sleep(1)
        return chat_completion(
            user_text=user_text,
            system_text=system,
            temperature=temperature,
        )
    except LLMError as e:
        logger.error(f"[generator] LLM falló en '{label}': {e}")
        return ""

def _llm_json_call(system: str, user_text: str, label: str) -> dict:
    """Llama al LLM esperando JSON. Devuelve {} si falla."""
    raw = _llm_call(system, user_text, label, temperature=0.0)
    if not raw:
        return {}
    try:
        return parse_llm_json(raw)
    except Exception as e:
        logger.error(f"[generator] JSON parse falló en '{label}': {e}")
        return {}

def _llm_call_logged(system: str, user_text: str, label: str, 
                     temperature: float, site=None) -> str:
    """Wrapper que llama al LLM y guarda el log si site está disponible."""
    result = _llm_call(system, user_text, label, temperature)

    if site is not None:
        try:
            from ..models import GenerationLog
            from django.conf import settings
            GenerationLog.objects.create(
                site=site,
                step=label,
                llm_model=settings.LLM_MODEL,
                system_prompt=system[:2000],
                user_prompt=user_text[:2000],
                raw_output=result[:5000],
            )
        except Exception:
            pass  # El log nunca puede romper la generación

    return result

# ──────────────────────────────────────────────────────────────────────────────
# FALLBACKS SI EL LLM FALLA
# ──────────────────────────────────────────────────────────────────────────────

def _fallback_pages(site_type: str) -> list[dict]:
    """Estructura de páginas mínima si el LLM falla."""
    return [
        {
            "name": "home",
            "url": "/",
            "template": "siteapp/home.html",
            "view_name": "home",
            "description": "Portada del sitio",
            "is_list": False,
            "is_detail": False,
        },
        {
            "name": "catalog",
            "url": "/catalog/",
            "template": "siteapp/catalog.html",
            "view_name": "catalog",
            "description": "Listado de items",
            "is_list": True,
            "is_detail": False,
        },
        {
            "name": "detail",
            "url": "/item/<pk>/",
            "template": "siteapp/detail.html",
            "view_name": "detail",
            "description": "Detalle de un item",
            "is_list": False,
            "is_detail": True,
        },
    ]


def _fallback_models(fields: list[dict]) -> str:
    """models.py mínimo si el LLM falla."""
    lines = ["from django.db import models", "", "class Item(models.Model):"]
    for f in fields:
        name = slugify(f["key"]).replace("-", "_") or "field"
        lines.append(f"    {name} = models.CharField(max_length=500, blank=True)")
    lines += [
        "    created_at = models.DateTimeField(auto_now_add=True)",
        "",
        "    def __str__(self):",
        "        return str(self.pk)",
        "",
    ]
    return "\n".join(lines)


def _fallback_views(pages: list[dict]) -> str:
    """views.py mínimo si el LLM falla."""
    lines = [
        "from django.shortcuts import render, get_object_or_404",
        "from .models import Item",
        "",
    ]
    for page in pages:
        if page.get("is_detail"):
            lines += [
                f"def {page['view_name']}(request, pk):",
                "    item = get_object_or_404(Item, pk=pk)",
                f"    return render(request, '{page['template']}', {{'item': item, 'site_title': 'Mi Sitio'}})",
                "",
            ]
        elif page.get("is_list"):
            lines += [
                f"def {page['view_name']}(request):",
                "    items = Item.objects.all().order_by('-id')",
                f"    return render(request, '{page['template']}', {{'items': items, 'site_title': 'Mi Sitio'}})",
                "",
            ]
        else:
            lines += [
                f"def {page['view_name']}(request):",
                "    items = Item.objects.all().order_by('-id')[:6]",
                f"    return render(request, '{page['template']}', {{'items': items, 'site_title': 'Mi Sitio'}})",
                "",
            ]
    return "\n".join(lines)

# ──────────────────────────────────────────────────────────────────────────────
# Regenerar errores llm 
# ──────────────────────────────────────────────────────────────────────────────

def _regenerate_with_errors(
    files, issues, pages, fields, site_type, site_title,
    user_prompt, real_fields, real_url_names, project, app,
    site=None
):
    """Regenera los archivos con errores pasando el contexto al LLM."""

    error_context = "\n".join(f" - {e}" for e in issues)

    # ── Regenerar views.py si tiene errores ─────────────────────────
    views_errors = [e for e in issues if "views.py" in e]
    if views_errors:
        logger.info("[generator] Regenerando views.py con correcciones...")
        system, user_text = prompt_views(
            fields=fields,
            site_type=site_type,
            site_title=site_title,
            user_prompt=user_prompt,
            pages=pages,
            real_fields=real_fields,
        )
        user_text += (
            f"\n\nCORRECCIÓN OBLIGATORIA — tu views.py anterior tenía estos errores:\n"
            f"{error_context}\n"
            f"Los campos reales del modelo son: {real_fields}\n"
            f"Corrige views.py usando SOLO esos campos."
        )
        new_views = _llm_call_logged(system, user_text, "views_retry", temperature=0.05, site=site)
        if new_views.strip():
            files[f"{project}/{app}/views.py"] = new_views
            logger.info("[generator] views.py regenerado ✅")

    # ── Regenerar templates con errores ─────────────────────────────
    for page in pages:
        template_path = f"{project}/{app}/templates/{page['template']}"
        template_errors = [e for e in issues if page["template"] in e]
        if not template_errors:
            continue

        logger.info(f"[generator] Regenerando template '{page['name']}' con correcciones...")
        template_error_context = "\n".join(f" - {e}" for e in template_errors)
        system, user_text = prompt_template(
            page=page,
            fields=fields,
            sample_items=(fields or []),
            site_type=site_type,
            site_title=site_title,
            user_prompt=user_prompt,
            all_pages=pages,
            real_fields=real_fields,
            real_url_names=real_url_names,
        )
        user_text += (
            f"\n\nCORRECCIÓN OBLIGATORIA — tu template anterior tenía estos errores:\n"
            f"{template_error_context}\n"
            f"Los campos reales del modelo son: {real_fields}\n"
            f"Corrige el template usando SOLO esos campos y URLs."
        )
        new_html = _llm_call_logged(system, user_text, f"template_{page['name']}_retry", temperature=0.4, site=site)
        if new_html.strip():
            files[template_path] = new_html
            logger.info(f"[generator] Template '{page['name']}' regenerado ✅")

    return files


# ──────────────────────────────────────────────────────────────────────────────
# LIMPIEZA DE RESPUESTAS LLM
# ──────────────────────────────────────────────────────────────────────────────

def _strip_markdown_fences(code: str) -> str:
    """
    Limpieza definitiva de fences Markdown.
    Estrategia: eliminar cualquier línea que sea únicamente un fence (```xxx),
    sin tocar el código real. Funciona independientemente de dónde ponga
    el LLM los fences.
    """
    import re
    code = code.strip()

    # Primero intentar extraer el interior de un bloque completo
    match = re.search(r"```(?:\w+)?\n(.*?)```", code, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Si no hay bloque completo, eliminar línea a línea cualquier fence
    lines = code.splitlines()
    clean = [line for line in lines if not re.match(r"^\s*```", line)]
    return "\n".join(clean).strip()


# ──────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

def generate_project_files(site) -> dict[str, str]:
    """
    Genera todos los archivos del proyecto Django.

    Recibe un objeto GeneratedSite con:
      - site.accepted_plan  → dict con site_type, site_title, fields, _meta.sample_items
      - site.project_name   → slug del nombre del proyecto
      - site.project_source.api_url → URL de la API original

    Devuelve dict {ruta_relativa: contenido} listo para guardar en project_files.
    """
    plan         = site.accepted_plan or {}
    fields       = plan.get("fields") or []
    sample_items = (plan.get("_meta") or {}).get("sample_items") or []
    main_path    = (plan.get("_meta") or {}).get("main_collection_path")
    site_type    = plan.get("site_type") or "other"
    site_title   = plan.get("site_title") or "Mi Sitio"
    user_prompt  = plan.get("user_prompt") or ""
    api_url      = site.project_source.api_url

    # Enriquecer el prompt del usuario con contexto del dataset
    enriched_prompt = enrich_user_prompt(
        user_prompt=user_prompt,
        site_type=site_type,
        fields=fields,
        sample_items=sample_items,
    )
    logger.info(f"[generator] Prompt enriquecido: {enriched_prompt[:100]}...")

    project = slugify(site.project_name or site_title).replace("-", "_") or "generated_site"
    app     = "siteapp"

    files: dict[str, str] = {}

    # ── PASO 1: Estructura de páginas ────────────────────────────────────────
    logger.info("[generator] Paso 1: estructura de páginas")
    system, user_text = prompt_pages_structure(
        site_type=site_type,
        site_title=site_title,
        user_prompt=enriched_prompt,
        fields=fields,
        sample_items=sample_items,
    )
    pages_data = _llm_json_call(system, user_text, "pages_structure")
    pages = pages_data.get("pages") or []

    # Validar mínimos
    has_list   = any(p.get("is_list")   for p in pages)
    has_detail = any(p.get("is_detail") for p in pages)
    if not pages or not has_list or not has_detail:
        logger.warning("[generator] Páginas inválidas, usando fallback")
        pages = _fallback_pages(site_type)

    # ── PASO 2: models.py ────────────────────────────────────────────────────
    logger.info("[generator] Paso 2: models.py")
    system, user_text = prompt_models(
        fields=fields,
        sample_items=sample_items,
        site_title=site_title,
    )
    models_code = _llm_call_logged(system, user_text, "models", temperature=0.05, site=site)
    if not models_code.strip():
        models_code = _fallback_models(fields)

    files[f"{project}/{app}/models.py"] = _strip_markdown_fences(models_code)

    # Extraer nombres reales de campos para usarlos en prompts siguientes
    real_fields = extract_model_fields(models_code)  # ← añadir esto
    logger.info(f"[generator] Campos reales extraídos: {real_fields}")  # ← y esto

    # Generar migración inicial a partir del models.py
    files[f"{project}/{app}/migrations/__init__.py"] = ""
    files[f"{project}/{app}/migrations/0001_initial.py"] = _generate_initial_migration(models_code, app)

    # ── PASO 3: views.py ─────────────────────────────────────────────────────
    logger.info("[generator] Paso 3: views.py")
    system, user_text = prompt_views(
        fields=fields,
        site_type=site_type,
        site_title=site_title,
        user_prompt=enriched_prompt,
        pages=pages,
        real_fields=real_fields,
    )
    views_code = _llm_call_logged(system, user_text, "views", temperature=0.05, site=site)
    if not views_code.strip():
        views_code = _fallback_views(pages)

    files[f"{project}/{app}/views.py"] = _strip_markdown_fences(views_code)

    # urls.py de la app (generado en Python, no por el LLM)
    files[f"{project}/{app}/urls.py"] = _app_urls(pages, app)

    # Extraer nombres reales de URLs para pasarlos a los prompts de templates
    real_url_names = {page["name"]: page["view_name"] for page in pages}
    logger.info(f"[generator] URLs reales: {real_url_names}")

    # ── PASO 4: base.html ────────────────────────────────────────────────────
    logger.info("[generator] Paso 4: base.html")
    system, user_text = prompt_base_template(
        site_title=site_title,
        site_type=site_type,
        user_prompt=enriched_prompt,
        all_pages=pages,
    )
    base_html = _llm_call_logged(system, user_text, "base.html", temperature=0.1, site=site)
    if not base_html.strip():
        base_html = _minimal_base_html(site_title, pages)

    files[f"{project}/{app}/templates/base.html"] = base_html

    # ── PASO 5: template por página ──────────────────────────────────────────
    for page in pages:
        logger.info(f"[generator] Paso 5: template '{page['name']}'")
        system, user_text = prompt_template(
            page=page,
            fields=fields,
            sample_items=sample_items,
            site_type=site_type,
            site_title=site_title,
            user_prompt=enriched_prompt,
            all_pages=pages,
            real_fields=real_fields,
            real_url_names=real_url_names,
        )
        html = _llm_call_logged(system, user_text, f"template_{page['name']}", temperature=0.4, site=site)
        if not html.strip():
            html = _minimal_template(page)

        files[f"{project}/{app}/templates/{page['template']}"] = _strip_markdown_fences(html)

    # ── PASO 6: load_data.py ─────────────────────────────────────────────────
    logger.info("[generator] Paso 6: load_data.py")
    system, user_text = prompt_load_data(
        fields=fields,
        sample_items=sample_items,
        api_url=api_url,
        main_collection_path=main_path,
        real_fields=real_fields,
    )
    load_data_code = _llm_call_logged(system, user_text, "load_data", temperature=0.05, site=site)
    if not load_data_code.strip():
        load_data_code = _fallback_load_data(fields, api_url)

    files[f"{project}/{app}/management/commands/load_data.py"] = _strip_markdown_fences(load_data_code)

    # ── PASO 7: archivos fijos ───────────────────────────────────────────────
    logger.info("[generator] Paso 7: archivos fijos")
    files.update(_fixed_files(project, app))

    # ── PASO 8: Validación de consistencia y autocorrección ─────────────────
    logger.info("[generator] Paso 8: validando consistencia entre archivos")
    issues = check_consistency(files)
    if issues:
        logger.warning(f"[generator] {len(issues)} inconsistencias detectadas:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        logger.info("[generator] Intentando autocorrección...")
        files = _regenerate_with_errors(
            files=files,
            issues=issues,
            pages=pages,
            fields=fields,
            site_type=site_type,
            site_title=site_title,
            user_prompt=enriched_prompt,
            real_fields=real_fields,
            real_url_names=real_url_names,
            project=project,
            app=app,
            site=site,
        )
    else:
        logger.info("[generator] Sin inconsistencias detectadas")
        
    logger.info(f"[generator] Completado: {len(files)} archivos generados")
    return files

# ──────────────────────────────────────────────────────────────────────────────
# FALLBACKS HTML MÍNIMOS
# ──────────────────────────────────────────────────────────────────────────────

def _minimal_base_html(site_title: str, pages: list[dict]) -> str:
    nav_links = "\n".join(
        f'      <a href="{p["url"]}" class="text-gray-300 hover:text-green-400">{p["name"].title()}</a>'
        for p in pages if not p.get("is_detail")
    )
    return f"""<!doctype html>
<html lang="es" class="bg-gray-950">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{site_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
  <nav class="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
    <span class="text-green-400 font-bold">{site_title}</span>
    <div class="flex gap-6 text-sm">
{nav_links}
    </div>
  </nav>
  <main class="max-w-7xl mx-auto px-6 py-10">
    {{% block content %}}{{% endblock %}}
  </main>
  <footer class="text-center text-gray-600 text-xs py-8">{site_title}</footer>
</body>
</html>"""


def _minimal_template(page: dict) -> str:
    if page.get("is_list"):
        return (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'>\n"
            "{% for item in items %}\n"
            "  <a href=\"{% url 'detail' item.pk %}\" "
            "class='block bg-gray-900 border border-gray-800 rounded-xl p-5 "
            "hover:border-green-400 transition-all'>\n"
            "    <p class='text-white font-semibold'>{{ item }}</p>\n"
            "  </a>\n"
            "{% endfor %}\n"
            "</div>\n"
            "{% endblock %}\n"
        )
    elif page.get("is_detail"):
        return (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<a href=\"{% url 'catalog' %}\" class='text-green-400 text-sm'>← Volver</a>\n"
            "<div class='bg-gray-900 border border-gray-800 rounded-xl p-8 mt-4'>\n"
            "  <p class='text-white text-2xl font-bold'>{{ item }}</p>\n"
            "</div>\n"
            "{% endblock %}\n"
        )
    else:
        return (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='text-center py-20'>\n"
            "  <h1 class='text-5xl font-black text-white'>{{ site_title }}</h1>\n"
            "  <a href=\"{% url 'catalog' %}\" "
            "class='mt-8 inline-block bg-green-400 text-black px-8 py-3 "
            "rounded-lg font-bold hover:bg-green-300 transition-colors'>Ver catálogo</a>\n"
            "</div>\n"
            "{% endblock %}\n"
        )


def _fallback_load_data(fields: list[dict], api_url: str) -> str:
    mapping = {f["key"]: slugify(f["key"]).replace("-", "_") for f in fields}
    return (
        "from django.core.management.base import BaseCommand\n"
        "from siteapp.models import Item\n"
        "import requests\n"
        "\n"
        f"API_URL = '{api_url}'\n"
        f"MAPPING = {mapping!r}\n"
        "\n"
        "class Command(BaseCommand):\n"
        "    help = 'Carga datos desde la API'\n"
        "\n"
        "    def handle(self, *args, **options):\n"
        "        try:\n"
        "            data = requests.get(API_URL, timeout=30).json()\n"
        "        except Exception as e:\n"
        "            self.stderr.write(f'Error descargando datos: {e}')\n"
        "            return\n"
        "\n"
        "        items = data if isinstance(data, list) else (\n"
        "            next((v for v in data.values() if isinstance(v, list)), [])\n"
        "            if isinstance(data, dict) else []\n"
        "        )\n"
        "\n"
        "        created = 0\n"
        "        for raw in items:\n"
        "            if not isinstance(raw, dict):\n"
        "                continue\n"
        "            obj = {}\n"
        "            for api_key, field_name in MAPPING.items():\n"
        "                val = raw.get(api_key)\n"
        "                obj[field_name] = str(val) if val is not None else ''\n"
        "            Item.objects.create(**obj)\n"
        "            created += 1\n"
        "\n"
        "        self.stdout.write(self.style.SUCCESS(f'Creados {created} items.'))\n"
    )