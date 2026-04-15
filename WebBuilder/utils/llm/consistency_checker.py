"""
consistency_checker.py — Valida y corrige los archivos generados por el LLM.

Responsabilidades:
  1. fix_template              → limpia el output HTML del LLM antes de guardarlo
  2. check_consistency         → detecta campos inválidos en views y templates
  3. check_django_syntax       → detecta errores básicos de sintaxis Django
  4. check_tailwind_validity   → detecta clases Tailwind inválidas o sospechosas
  5. check_template_structure  → valida estructura mínima de templates
  6. check_prompt_contradictions → detecta contradicciones simples con el prompt del usuario
  7. run_all_checks            → ejecuta todos los chequeos en un solo punto
"""

from __future__ import annotations

import re


# ── HELPERS INTERNOS ────────────────────────────────────────────────────────

_DJANGO_ATTRS = {"pk", "__str__", "objects", "save", "delete"}

_INVALID_TAILWIND_PATTERNS = [
    r'\bbg-#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b',
    r'\btext-#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b',
    r'\bborder-#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b',
    r'\bhover:bg-#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b',
    r'\bhover:text-#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b',
    r'\bhover:border-#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})(?:/\d+)?\b',
]


def _find_first_matching_file(files: dict[str, str], suffix: str) -> str:
    return next((v for k, v in files.items() if k.endswith(suffix)), "")


def _extract_model_fields(models_code: str) -> set[str]:
    fields = set(re.findall(r'^\s+(\w+)\s*=\s*models\.', models_code, re.MULTILINE))
    return fields - {"created_at", "updated_at", "id"}


def _normalize_prompt(user_prompt: str | None) -> str:
    return (user_prompt or "").strip().lower()


def _iter_html_files(files: dict[str, str]):
    for path, content in files.items():
        if path.endswith(".html"):
            yield path, content


def _page_type_from_path(path: str) -> str:
    path_lower = path.lower()
    if "detail" in path_lower:
        return "detail"
    if "catalog" in path_lower or "list" in path_lower:
        return "list"
    if "home" in path_lower or path_lower.endswith("index.html"):
        return "home"
    return "other"


# ── LIMPIEZA DE TEMPLATES ───────────────────────────────────────────────────

def fix_template(html: str) -> str:
    """
    Limpia y corrige el output HTML del LLM antes de guardarlo.
    No llama al LLM — solo correcciones de texto.
    """
    if not html or not html.strip():
        return html

    # 1. Quitar bloques markdown que se cuelen (```html, ```django, ```)
    html = re.sub(r'```[\w]*\n?', '', html)
    html = re.sub(r'```', '', html)

    # 2. Asegurar que {% extends %} está en la primera línea si existe
    if '{% extends' in html and not html.strip().startswith('{% extends'):
        match = re.search(r'\{%\s*extends\s+[\'"][^\'"]+[\'"]\s*%\}', html)
        if match:
            extends_tag = match.group(0)
            html = html[:match.start()].replace(extends_tag, '')
            html = extends_tag + '\n' + html

    # 3. Corregir cierres Django incompletos
    html = re.sub(r'\{%-?\s*(endif|endfor|endblock|endwith)\s*\n', r'{% \1 %}\n', html)

    # 4. Quitar líneas vacías excesivas
    html = re.sub(r'\n{3,}', '\n\n', html)

    # 5. Eliminar espacios basura al inicio/final
    return html.strip()


# ── CHEQUEO DE CONSISTENCIA ENTRE ARCHIVOS ─────────────────────────────────

def check_consistency(files: dict[str, str]) -> list[str]:
    """
    Detecta referencias a campos inexistentes del modelo en views y templates.
    """
    errors: list[str] = []

    models_code = _find_first_matching_file(files, "models.py")
    model_fields = _extract_model_fields(models_code)

    if not model_fields:
        return []

    views_code = _find_first_matching_file(files, "views.py")
    view_refs = re.findall(r'item\.(\w+)', views_code)
    for ref in sorted(set(view_refs)):
        if ref not in model_fields and ref not in _DJANGO_ATTRS:
            errors.append(f"views.py usa item.{ref} pero no existe en models.py")

    for path, content in _iter_html_files(files):
        template_refs = re.findall(r'item\.(\w+)', content)
        for ref in sorted(set(template_refs)):
            if ref not in model_fields and ref not in _DJANGO_ATTRS:
                errors.append(f"{path} usa item.{ref} pero no existe en models.py")

    return errors


# ── CHEQUEO BÁSICO DE SINTAXIS DJANGO ──────────────────────────────────────

def check_django_syntax(files: dict[str, str]) -> list[str]:
    errors: list[str] = []

    for path, content in _iter_html_files(files):
        for_count = len(re.findall(r'\{%[-\s]*for\s', content))
        endfor_count = len(re.findall(r'\{%[-\s]*endfor', content))
        if for_count != endfor_count:
            errors.append(f"{path}: {for_count} {{% for %}} pero {endfor_count} {{% endfor %}}")

        if_count = len(re.findall(r'\{%[-\s]*if\s', content))
        endif_count = len(re.findall(r'\{%[-\s]*endif', content))
        if if_count != endif_count:
            errors.append(f"{path}: {if_count} {{% if %}} pero {endif_count} {{% endif %}}")

        block_count = len(re.findall(r'\{%[-\s]*block\s', content))
        endblock_count = len(re.findall(r'\{%[-\s]*endblock', content))
        if block_count != endblock_count:
            errors.append(f"{path}: {block_count} {{% block %}} pero {endblock_count} {{% endblock %}}")

        if '```' in content:
            errors.append(f"{path}: contiene bloques Markdown (```)")

    return errors


# ── CHEQUEO DE TAILWIND / CLASES SOSPECHOSAS ───────────────────────────────

def check_tailwind_validity(files: dict[str, str]) -> list[str]:
    """
    Detecta clases Tailwind inválidas o sospechosas, sobre todo con colores HEX.
    """
    errors: list[str] = []

    for path, content in _iter_html_files(files):
        matches: list[str] = []
        for pattern in _INVALID_TAILWIND_PATTERNS:
            matches.extend(re.findall(pattern, content))

        if matches:
            unique_matches = sorted(set(matches))
            errors.append(
                f"{path}: clases Tailwind HEX inválidas o sospechosas detectadas: {', '.join(unique_matches)}"
            )

    return errors


# ── ESTRUCTURA MÍNIMA DE TEMPLATES ─────────────────────────────────────────

def check_template_structure(files: dict[str, str]) -> list[str]:
    """
    Valida estructura mínima razonable de los templates generados.
    """
    errors: list[str] = []

    for path, content in _iter_html_files(files):
        page_type = _page_type_from_path(path)

        if path.endswith("base.html"):
            if "{% block content %}" not in content or "{% endblock %}" not in content:
                errors.append(f"{path}: base.html debería incluir {{% block content %}} ... {{% endblock %}}")
            continue

        if "{% extends 'base.html' %}" not in content and '{% extends "base.html" %}' not in content:
            errors.append(f"{path}: el template debería extender de base.html")

        if "{% block content %}" not in content:
            errors.append(f"{path}: falta {{% block content %}}")

        if page_type == "list":
            if "{% for item in items %}" not in content and "{% for item in items %}" not in content.replace("  ", " "):
                errors.append(f"{path}: página de listado sin bucle claro sobre items")
            if "{% empty %}" not in content:
                errors.append(f"{path}: página de listado sin {{% empty %}} para estado vacío")

        if page_type == "detail":
            if "item." not in content:
                errors.append(f"{path}: página de detalle sin uso claro del objeto item")

    return errors


# ── CONTRADICCIONES SIMPLES CONTRA EL PROMPT DEL USUARIO ───────────────────

def check_prompt_contradictions(files: dict[str, str], user_prompt: str | None = None) -> list[str]:
    """
    Detecta contradicciones simples entre el HTML generado y restricciones explícitas del prompt.
    Es deliberadamente conservador: mejor pocos checks fiables que muchos checks ruidosos.
    """
    errors: list[str] = []
    prompt = _normalize_prompt(user_prompt)

    if not prompt:
        return errors

    prompt_bans_images = (
        "sin imágenes" in prompt
        or "sin imagenes" in prompt
        or "no usar imágenes" in prompt
        or "no usar imagenes" in prompt
        or "sin imágenes en el listado" in prompt
        or "sin imagenes en el listado" in prompt
    )

    prompt_bans_prices = (
        "sin precios" in prompt
        or "sin precio" in prompt
        or "no mostrar precios" in prompt
        or "no uses precios" in prompt
    )

    prompt_wants_four_cols = (
        "4 columnas" in prompt
        or "cuatro columnas" in prompt
        or "grid de 4 columnas" in prompt
    )

    prompt_mentions_hex = bool(re.search(r'#[0-9a-fA-F]{6}\b', prompt))

    for path, content in _iter_html_files(files):
        content_lower = content.lower()
        page_type = _page_type_from_path(path)

        if prompt_bans_images and page_type == "list":
            if "<img" in content_lower:
                errors.append(f"{path}: el prompt parece prohibir imágenes en listado, pero el template contiene <img>")

        if prompt_bans_prices:
            if any(token in content_lower for token in ["price", "precio", "€", "$"]):
                errors.append(f"{path}: el prompt parece prohibir precios, pero el template contiene referencias a precio")

        if prompt_wants_four_cols and page_type == "list":
            has_four_col_hint = any(
                token in content
                for token in [
                    "lg:grid-cols-4",
                    "xl:grid-cols-4",
                    "grid-cols-4",
                ]
            )
            if not has_four_col_hint:
                errors.append(f"{path}: el prompt pide grid de 4 columnas, pero no se detecta una clase clara de 4 columnas")

        if prompt_mentions_hex:
            # No exigimos todos los colores, pero sí comprobamos al menos que aparezca algún HEX en el HTML
            if not re.search(r'#[0-9a-fA-F]{6}\b', content):
                errors.append(f"{path}: el prompt incluye colores HEX, pero no se detecta ningún HEX en el template generado")

    return errors


# ── FUNCIÓN PRINCIPAL PARA EJECUTAR TODOS LOS CHECKS ───────────────────────

def run_all_checks(files: dict[str, str], user_prompt: str | None = None) -> list[str]:
    """
    Ejecuta todos los chequeos disponibles y devuelve una lista unificada de errores/warnings.
    """
    all_errors: list[str] = []

    checks = [
        check_consistency(files),
        check_django_syntax(files),
        check_tailwind_validity(files),
        check_template_structure(files),
        check_prompt_contradictions(files, user_prompt=user_prompt),
    ]

    for result in checks:
        all_errors.extend(result)

    # Eliminar duplicados preservando orden
    deduped: list[str] = []
    seen: set[str] = set()
    for err in all_errors:
        if err not in seen:
            deduped.append(err)
            seen.add(err)

    return deduped