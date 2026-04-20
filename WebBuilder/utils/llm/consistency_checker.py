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

_INVENTED_CLASS_PATTERNS = [
    r'\b\w+_base\b',       # card_base, input_base, button_base...
    r'\b\w+_soft\b',       # card_soft...
    r'\b\w+_dark\b',       # muted_text_dark...
    r'\b\w+_medium\b',     # title_medium...
    r'\b\w+_strong\b',     # title_strong...
    r'\bcontainer_\w+\b',  # container_base, container_narrow...
    r'\bsection_\w+\b',    # section_spacing...
    # Efectos visuales inventados con prefijo de estado (hover:glow-violet, lg:shimmer, etc.)
    r'\bhover:glow-\w+\b',
    r'\bhover:shimmer\b',
    r'\bhover:neon-\w+\b',
    r'\bhover:pulse-\w+\b',
    r'\bhover:float\b',
    r'\bhover:levitate\b',
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
            html = extends_tag + '\n' + html[:match.start()] + html[match.end():]

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
    filter_refs = re.findall(r'\.filter\([^)]*?(\w+)__', views_code)

    for ref in sorted(set(view_refs) | set(filter_refs)):
        if ref not in model_fields and ref not in _DJANGO_ATTRS:
            errors.append(f"views.py usa item.{ref} pero no existe en models.py")

    for path, content in _iter_html_files(files):
        template_refs = re.findall(r'item\.(\w+)', content)
        for ref in sorted(set(template_refs)):
            if ref not in model_fields and ref not in _DJANGO_ATTRS:
                errors.append(f"{path} usa item.{ref} pero no existe en models.py")

    return errors


# ── CHEQUEO BÁSICO DE SINTAXIS DJANGO ──────────────────────────────────────

def check_django_syntax(files: dict[str, str], valid_url_names: set[str] | None = None) -> list[str]:
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

        if valid_url_names:
            url_refs = re.findall(r'\{%\s*url\s+[\'"](\w+)[\'"]', content)
            for url_ref in url_refs:
                if url_ref not in valid_url_names:
                    errors.append(f"{path}: usa {{% url '{url_ref}' %}} pero esa URL no existe en el proyecto")

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

    for path, content in _iter_html_files(files):
        invented = []
        class_attrs = re.findall(r'class=["\']([^"\']+)["\']', content)
        for class_attr in class_attrs:
            for pattern in _INVENTED_CLASS_PATTERNS:
                matches = re.findall(pattern, class_attr)
                invented.extend(matches)
        if invented:
            unique = sorted(set(invented))
            errors.append(
                f"{path}: posibles clases CSS inventadas detectadas: {', '.join(unique)}"
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
            content_normalized = re.sub(r'\s+', ' ', content)
            has_valid_loop = (
                "{% for item in page_obj %}" in content_normalized
                or "{% for item in featured %}" in content_normalized
            )
            has_invalid_loop = "{% for item in items %}" in content_normalized
            if not has_valid_loop:
                errors.append(f"{path}: página de listado sin bucle sobre page_obj")
            if has_invalid_loop:
                errors.append(f"{path}: página de listado usa {{% for item in items %}} en vez de page_obj")
            if "{% empty %}" not in content:
                errors.append(f"{path}: página de listado sin {{% empty %}} para estado vacío")

        if page_type == "detail":
            if "item." not in content:
                errors.append(f"{path}: página de detalle sin uso claro del objeto item")

    return errors


# ── SETS DE PALABRAS CLAVE (añadir arriba junto a _DJANGO_ATTRS) ────────────
# Solo palabras en ingles, ya que se traduce el prompt
_NEGATION_WORDS = {"without", "no", "avoid", "remove", "eliminate", "none", "don't", "dont", "exclude"}
_IMAGE_WORDS = {"image", "images", "photo", "photos", "picture", "pictures", "img"}
_PRICE_WORDS = {"price", "prices", "cost", "costs", "fee", "fees", "rate"}

def _prompt_bans(prompt: str, target_words: set[str]) -> bool:
    words = set(prompt.lower().split())
    has_target = bool(words & target_words)
    has_negation = bool(words & _NEGATION_WORDS)
    return has_target and has_negation


# ── CONTRADICCIONES SIMPLES CONTRA EL PROMPT DEL USUARIO ───────────────────

def check_prompt_contradictions(files: dict[str, str], user_prompt: str | None = None) -> list[str]:
    errors: list[str] = []
    prompt = _normalize_prompt(user_prompt)

    if not prompt:
        return errors

    prompt_bans_images = _prompt_bans(prompt, _IMAGE_WORDS)
    prompt_bans_prices = _prompt_bans(prompt, _PRICE_WORDS)

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
            if not re.search(r'#[0-9a-fA-F]{6}\b', content):
                errors.append(f"{path}: el prompt incluye colores HEX, pero no se detecta ningún HEX en el template generado")

    return errors

# ── CHEQUEO DE LOAD_DATA.PY ─────────────────────────────────────────────────

def check_load_data_integrity(files: dict[str, str], api_url: str | None = None) -> list[str]:
    """
    Valida que load_data.py tenga una estructura mínima fiable:
      1. La URL que usa coincide con la API real del proyecto.
      2. El except captura Exception (no solo RequestException).
      3. Hay al menos un get_or_create o create real.
      4. No guarda str(...) en campos IntegerField.
    """
    errors: list[str] = []

    load_data_code = _find_first_matching_file(files, "load_data.py")
    models_code    = _find_first_matching_file(files, "models.py")

    if not load_data_code:
        return errors

    # ── 1. URL correcta ──────────────────────────────────────────────────────
    if api_url:
        urls_in_code = re.findall(r"https?://[^\s'\"]+", load_data_code)
        # Extraer el path de la api_url para comparación parcial
        # ej: 'https://rickandmortyapi.com/api/episode' → '/api/episode'
        api_path = re.sub(r"https?://[^/]+", "", api_url).rstrip("/")
        if urls_in_code:
            url_match = any(
                api_url in u or u in api_url or (api_path and api_path in u)
                for u in urls_in_code
            )
            if not url_match:
                errors.append(
                    f"load_data.py: la URL del comando ({urls_in_code[0]!r}) no coincide "
                    f"con la API del proyecto ({api_url!r}). El comando cargará datos incorrectos."
                )
        else:
            errors.append(
                f"load_data.py: no se detecta ninguna URL hardcodeada. "
                f"Asegúrate de que el comando apunta a {api_url!r}."
            )

    # ── 2. Except suficientemente amplio ────────────────────────────────────
    if "except Exception" not in load_data_code and "except requests.RequestException" in load_data_code:
        errors.append(
            "load_data.py: el except solo captura requests.RequestException. "
            "Usa 'except Exception' para no silenciar errores de conversión de tipos."
        )

    # ── 3. Hay al menos un insert real ──────────────────────────────────────
    has_insert = bool(re.search(r'\.(get_or_create|update_or_create|create)\(', load_data_code))
    if not has_insert:
        errors.append(
            "load_data.py: no se detecta ningún get_or_create, update_or_create ni create. "
            "El comando no insertará datos en la BD."
        )

    # ── 4. str() guardado en IntegerField ───────────────────────────────────
    if models_code:
        integer_fields = set(re.findall(
            r'^\s+(\w+)\s*=\s*models\.IntegerField',
            models_code, re.MULTILINE
        ))
        str_assignments = re.findall(r"'(\w+)'\s*:\s*str\(", load_data_code)
        for field in str_assignments:
            if field in integer_fields:
                errors.append(
                    f"load_data.py: guarda str(...) en '{field}' pero el modelo "
                    f"lo define como IntegerField. Usa int() o len() según corresponda."
                )

    return errors


def check_views_urls_consistency(files: dict[str, str]) -> list[str]:
    """
    Detecta funciones definidas en views.py que no tienen
    su URL registrada en urls.py.
    """
    errors = []

    views_code = _find_first_matching_file(files, "views.py")
    urls_code = _find_first_matching_file(files, "urls.py")

    if not views_code or not urls_code:
        return errors

    # Extraer nombres de funciones definidas en views.py
    view_funcs = set(re.findall(r'^def (\w+)\(request', views_code, re.MULTILINE))

    # Extraer nombres registrados en urls.py
    url_names = set(re.findall(r"name=['\"](\w+)['\"]", urls_code))
    url_views = set(re.findall(r'views\.(\w+)', urls_code))

    for func in view_funcs:
        if func not in url_views:
            errors.append(
                f"views.py define '{func}' pero no está registrada en urls.py"
            )

    return errors

# ── FUNCIÓN PRINCIPAL PARA EJECUTAR TODOS LOS CHECKS ───────────────────────

def run_all_checks(
    files: dict[str, str],
    user_prompt: str | None = None,
    valid_url_names: set[str] | None = None,
    api_url: str | None = None,
) -> dict[str, list[str]]:
    """
    Ejecuta todos los chequeos disponibles y devuelve un dict con dos listas:
      - "blocking": problemas que rompen el proyecto en runtime (disparan regeneracion)
      - "warning":  avisos de calidad (se loggean pero no disparan regeneracion)
    """
    blocking_checks = [
        check_consistency(files),
        check_django_syntax(files, valid_url_names=valid_url_names),
        check_template_structure(files),
        check_load_data_integrity(files, api_url=api_url),
        check_views_urls_consistency(files),
    ]

    warning_checks = [
        check_tailwind_validity(files),
        check_prompt_contradictions(files, user_prompt=user_prompt),
    ]

    def _flatten_dedup(groups: list[list[str]]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for group in groups:
            for item in group:
                if item not in seen:
                    result.append(item)
                    seen.add(item)
        return result

    return {
        "blocking": _flatten_dedup(blocking_checks),
        "warning": _flatten_dedup(warning_checks),
    }