"""
project_generator.py — Orquestador de la generación del proyecto Django completo.

Flujo:
  1. LLM decide la estructura de páginas (prompt_pages_structure)
  2. LLM genera models.py
  3. LLM genera views.py
  4. LLM genera base.html
  5. LLM genera un template HTML por cada página
  6. LLM genera load_data.py (management command)
  7. Se ensamblan los archivos estáticos (settings, manage, urls, Dockerfile...)
  8. Se devuelve dict {ruta: contenido} listo para guardar en GeneratedSite.project_files
"""
from __future__ import annotations

import logging

from django.utils.text import slugify

from ..llm.generator_prompts import (
    prompt_pages_structure,
    prompt_models,
    prompt_views,
    prompt_base_template,
    prompt_template,
    prompt_load_data,
)
from ..llm.field_extractor import extract_model_fields
from ..llm.consistency_checker import fix_template, run_all_checks
from ..llm.enrich_prompt import enrich_user_prompt

from .llm_wrappers import (
    llm_call_logged,
    llm_json_call,
    strip_markdown_fences,
    extract_requirements,
    translate_prompt_to_english,
)

from .fallbacks import (
    fallback_pages,
    fallback_models,
    fallback_views,
    fallback_base_html,
    fallback_template,
    fallback_load_data,
)
from .static_files import build_static_files, build_app_urls
from .migrations_generator import generate_initial_migration

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# HELPER DE PROGRESO
# ──────────────────────────────────────────────────────────────────────────────

def _update_step(site, step: str) -> None:
    """Actualiza el paso actual de generación en la base de datos."""
    try:
        site.generation_step = step
        site.save(update_fields=["generation_step"])
    except Exception:
        pass


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
    plan = site.accepted_plan or {}
    fields = plan.get("fields") or []
    sample_items = (plan.get("_meta") or {}).get("sample_items") or []
    main_path = (plan.get("_meta") or {}).get("main_collection_path")
    site_type = plan.get("site_type") or "other"
    site_title = plan.get("site_title") or "Mi Sitio"
    user_prompt = plan.get("user_prompt") or ""
    user_prompt_normalized = translate_prompt_to_english(user_prompt)
    api_url = site.project_source.api_url

    # Enriquecer el prompt del usuario con contexto del dataset
    enriched_prompt = enrich_user_prompt(
        user_prompt=user_prompt_normalized,
        site_type=site_type,
        fields=fields,
        sample_items=sample_items,
    )
    logger.info("[generator] Prompt enriquecido: %s...", enriched_prompt[:100])

    project = slugify(site.project_name or site_title).replace("-", "_") or "generated_site"
    app = "siteapp"

    files: dict[str, str] = {}

    # ── PASO 1: Estructura de páginas ────────────────────────────────────────
    _update_step(site, "Analizando estructura del sitio...")
    logger.info("[generator] Paso 1: estructura de páginas")
    system, user_text = prompt_pages_structure(
        site_type=site_type,
        site_title=site_title,
        user_prompt=enriched_prompt,
        fields=fields,
        sample_items=sample_items,
    )
    pages_data = llm_json_call(system, user_text, "pages_structure")
    pages = pages_data.get("pages") or []

    has_list = any(p.get("is_list") for p in pages)
    has_detail = any(p.get("is_detail") for p in pages)
    if not pages or not has_list or not has_detail:
        logger.warning("[generator] Páginas inválidas, usando fallback")
        pages = fallback_pages(site_type)

    # ── PASO 2: models.py ────────────────────────────────────────────────────
    _update_step(site, "Generando modelos de datos...")
    logger.info("[generator] Paso 2: models.py")
    system, user_text = prompt_models(
        fields=fields,
        sample_items=sample_items,
        site_title=site_title,
    )
    models_code = llm_call_logged(system, user_text, "models", temperature=0.05, site=site)
    if not models_code.strip():
        models_code = fallback_models(fields)

    models_code = strip_markdown_fences(models_code)
    files[f"{project}/{app}/models.py"] = models_code

    real_fields = extract_model_fields(models_code)
    logger.info("[generator] Campos reales extraídos: %s", real_fields)

    files[f"{project}/{app}/migrations/__init__.py"] = ""
    files[f"{project}/{app}/migrations/0001_initial.py"] = generate_initial_migration(models_code, app)

    # ── PASO 3: views.py ─────────────────────────────────────────────────────
    _update_step(site, "Generando vistas y controladores...")
    logger.info("[generator] Paso 3: views.py")
    system, user_text = prompt_views(
        fields=fields,
        site_type=site_type,
        site_title=site_title,
        user_prompt=enriched_prompt,
        pages=pages,
        real_fields=real_fields,
    )
    views_code = llm_call_logged(system, user_text, "views", temperature=0.05, site=site)
    if not views_code.strip():
        views_code = fallback_views(pages)

    files[f"{project}/{app}/views.py"] = strip_markdown_fences(views_code)
    files[f"{project}/{app}/urls.py"] = build_app_urls(pages, app)

    real_url_names = {page["name"]: page["view_name"] for page in pages}
    logger.info("[generator] URLs reales: %s", real_url_names)

    # ── PASO 4: base.html ────────────────────────────────────────────────────
    _update_step(site, "Generando plantilla base...")
    logger.info("[generator] Paso 4: base.html")
    system, user_text = prompt_base_template(
        site_title=site_title,
        site_type=site_type,
        user_prompt=enriched_prompt,
        all_pages=pages,
    )
    base_html = llm_call_logged(system, user_text, "base.html", temperature=0.1, site=site)
    if not base_html.strip():
        base_html = fallback_base_html(site_title, pages)

    files[f"{project}/{app}/templates/base.html"] = fix_template(base_html)

    # ── PASO 5: template por página ──────────────────────────────────────────
    for page in pages:
        _update_step(site, f"Generando pagina '{page['name']}'...")
        logger.info("[generator] Paso 5: template '%s'", page["name"])
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
        html = llm_call_logged(
            system,
            user_text,
            f"template_{page['name']}",
            temperature=0.4,
            site=site,
        )
        if not html.strip():
            html = fallback_template(page)

        files[f"{project}/{app}/templates/{page['template']}"] = fix_template(html)

    # ── PASO 6: load_data.py ─────────────────────────────────────────────────
    _update_step(site, "Generando cargador de datos...")
    logger.info("[generator] Paso 6: load_data.py")
    system, user_text = prompt_load_data(
        fields=fields,
        sample_items=sample_items,
        api_url=api_url,
        main_collection_path=main_path,
        real_fields=real_fields,
    )
    load_data_code = llm_call_logged(system, user_text, "load_data", temperature=0.05, site=site)
    if not load_data_code.strip():
        load_data_code = fallback_load_data(fields, api_url)

    load_data_code, extra_reqs = extract_requirements(strip_markdown_fences(load_data_code))
    files[f"{project}/{app}/management/commands/load_data.py"] = load_data_code

    if extra_reqs:
        logger.info("[generator] Librerías extra detectadas: %s", extra_reqs)
        current_reqs = files.get(f"{project}/requirements.txt", "")
        for req in extra_reqs:
            if req not in current_reqs:
                current_reqs += f"{req}\n"
        files[f"{project}/requirements.txt"] = current_reqs

    # ── PASO 6b: seed_users.py ───────────────────────────────────────────────
    logger.info("[generator] Paso 6b: seed_users.py")
    site_users = list(site.site_users.values("username", "password", "role"))
    if site_users:
        seed_lines = []
        for u in site_users:
            seed_lines.append(f"    ('{u['username']}', '{u['password']}', '{u['role']}'),")

        seed_users_code = (
            '"""\n'
            'Management command: seed_users\n'
            'Crea los usuarios predefinidos al arrancar el proyecto.\n'
            'Uso: python manage.py seed_users\n'
            '"""\n'
            'from django.contrib.auth.models import User\n'
            'from django.core.management.base import BaseCommand\n'
            '\n'
            'USERS = [\n'
            + "\n".join(seed_lines) + "\n"
            ']\n'
            '\n'
            'class Command(BaseCommand):\n'
            '    help = "Crea los usuarios predefinidos del proyecto"\n'
            '\n'
            '    def handle(self, *args, **kwargs):\n'
            '        for username, password, role in USERS:\n'
            '            if User.objects.filter(username=username).exists():\n'
            '                self.stdout.write(f"  ⚠ Usuario {username} ya existe, omitido.")\n'
            '                continue\n'
            '            if role == "super":\n'
            '                User.objects.create_superuser(username=username, password=password)\n'
            '            else:\n'
            '                User.objects.create_user(username=username, password=password)\n'
            '            self.stdout.write(f"  ✔ Creado: {username} ({role})")\n'
        )
        files[f"{project}/{app}/management/commands/seed_users.py"] = seed_users_code

    # ── PASO 7: archivos estáticos ───────────────────────────────────────────
    _update_step(site, "Ensamblando archivos del proyecto...")
    logger.info("[generator] Paso 7: archivos estáticos")
    files.update(build_static_files(project, app))

    # ── PASO 8: Validación de consistencia y autocorrección ─────────────────
    _update_step(site, "Validando consistencia entre archivos...")
    logger.info("[generator] Paso 8: validando consistencia entre archivos")
    valid_url_names = set(real_url_names.values()) | {"login", "logout", "register"}
    issues = run_all_checks(files, user_prompt=user_prompt, valid_url_names=valid_url_names)

    if issues:
        logger.warning("[generator] %s inconsistencias detectadas:", len(issues))
        for issue in issues:
            logger.warning("  - %s", issue)

        _update_step(site, "Corrigiendo inconsistencias detectadas...")
        logger.info("[generator] Intentando autocorrección...")
        files = _regenerate_with_errors(
            files=files,
            issues=issues,
            pages=pages,
            fields=fields,
            sample_items=sample_items,
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

    _update_step(site, "Generacion completada.")
    logger.info("[generator] Completado: %s archivos generados", len(files))
    return files


# ──────────────────────────────────────────────────────────────────────────────
# AUTOCORRECCIÓN DE ERRORES LLM
# ──────────────────────────────────────────────────────────────────────────────

def _regenerate_with_errors(
    files,
    issues,
    pages,
    fields,
    sample_items,
    site_type,
    site_title,
    user_prompt,
    real_fields,
    real_url_names,
    project,
    app,
    site=None,
):
    """Regenera los archivos con errores pasando el contexto de corrección al LLM."""
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
            f"\n\nCORRECCION OBLIGATORIA — tu views.py anterior tenia estos errores:\n"
            f"{error_context}\n"
            f"Los campos reales del modelo son: {real_fields}\n"
            f"Corrige views.py usando SOLO esos campos."
        )
        new_views = llm_call_logged(
            system,
            user_text,
            "views_retry",
            temperature=0.05,
            site=site,
        )
        if new_views.strip():
            files[f"{project}/{app}/views.py"] = strip_markdown_fences(new_views)
            logger.info("[generator] views.py regenerado")

    # ── Regenerar templates con errores ─────────────────────────────
    for page in pages:
        template_path = f"{project}/{app}/templates/{page['template']}"
        template_errors = [e for e in issues if page["template"] in e]
        if not template_errors:
            continue

        logger.info("[generator] Regenerando template '%s' con correcciones...", page["name"])
        template_error_context = "\n".join(f" - {e}" for e in template_errors)

        system, user_text = prompt_template(
            page=page,
            fields=fields,
            sample_items=sample_items,
            site_type=site_type,
            site_title=site_title,
            user_prompt=user_prompt,
            all_pages=pages,
            real_fields=real_fields,
            real_url_names=real_url_names,
        )
        user_text += (
            f"\n\nCORRECCION OBLIGATORIA — tu template anterior tenia estos errores:\n"
            f"{template_error_context}\n"
            f"Los campos reales del modelo son: {real_fields}\n"
            f"Corrige el template usando SOLO esos campos y URLs."
        )
        new_html = llm_call_logged(
            system,
            user_text,
            f"template_{page['name']}_retry",
            temperature=0.4,
            site=site,
        )
        if new_html.strip():
            files[template_path] = fix_template(new_html)
            logger.info("[generator] Template '%s' regenerado", page["name"])

    return files