"""
enrich_prompt.py — Enriquece el prompt del usuario con contexto del dataset.

Objetivo:
- Ayudar al LLM a entender mejor qué datos existen.
- Sugerir usos razonables de esos datos.
- Nunca contradecir la instrucción explícita del usuario.
"""

from __future__ import annotations

_MAX_ENRICHED_CHARS = 1500

# ── DETECCIÓN DE TIPOS DE CAMPO ──────────────────────────────────────────────

_IMAGE_KEYS = {
    "image", "img", "photo", "thumbnail", "picture", "avatar", "cover",
    "poster", "imagen", "foto", "miniatura", "portada", "thumb",
}
_PRICE_KEYS = {
    "price", "cost", "amount", "fee", "salary", "budget", "rate",
    "precio", "coste", "importe", "tarifa", "salario",
}
_DATE_KEYS = {
    "date", "created_at", "updated_at", "published", "timestamp",
    "year", "time", "fecha", "año", "tiempo", "publicado",
}
_RATING_KEYS = {
    "rating", "score", "stars", "votes", "rank", "puntuacion",
    "valoracion", "estrellas", "votos", "nota",
}
_CATEGORY_KEYS = {
    "category", "type", "genre", "tag", "label", "group", "kind",
    "categoria", "tipo", "genero", "etiqueta", "grupo",
}
_LOCATION_KEYS = {
    "location", "city", "country", "address", "place", "region",
    "ubicacion", "ciudad", "pais", "direccion", "lugar", "region",
}
_URL_KEYS = {"url", "link", "website", "href", "enlace", "web", "sitio"}
_TEXT_KEYS = {
    "description", "content", "body", "summary", "bio", "about",
    "text", "descripcion", "contenido", "resumen", "biografia", "texto",
}
_TITLE_KEYS = {
    "title", "name", "nombre", "titulo", "common", "label",
    "etiqueta", "heading", "encabezado",
}

_DATASET_PRIORITY_RULES = [
    "La instrucción explícita del usuario tiene prioridad absoluta.",
    "Las sugerencias derivadas del dataset son orientativas y nunca obligatorias.",
    "Nunca uses una sugerencia del dataset para contradecir una restricción del usuario.",
    "Si el usuario pide una estética concreta, el dataset solo debe complementar esa dirección.",
]


# ── HELPERS DE DETECCIÓN ─────────────────────────────────────────────────────

def _matches(key: str, keyword_set: set[str]) -> bool:
    key_lower = key.lower()
    if key_lower in keyword_set:
        return True
    key_parts = set(key_lower.split("_"))
    return bool(key_parts & keyword_set)


def _detect_title_field(fields: list[dict], sample_items: list[dict]) -> str | None:
    """
    Intenta identificar el campo más representativo para usar como título.
    Primero busca por nombre semántico, luego por valores cortos en los ejemplos.
    """
    for field in fields:
        if _matches(field["key"], _TITLE_KEYS):
            return field["key"]

    if sample_items:
        for field in fields:
            key = field["key"]
            values = [str(item.get(key, "")) for item in sample_items[:3] if item.get(key)]
            if values and all(5 < len(v) < 80 for v in values):
                return key

    return None


def _sample_value(key: str, sample_items: list[dict]) -> str | None:
    """Devuelve un valor de ejemplo real para un campo dado."""
    for item in sample_items[:3]:
        val = item.get(key)
        if val and str(val).strip():
            return str(val).strip()[:60]
    return None


# ── HELPERS DE CONTEXTO ──────────────────────────────────────────────────────

def _build_priority_rules_text() -> str:
    return "\n".join(f"- {rule}" for rule in _DATASET_PRIORITY_RULES)


def _build_field_context(fields: list[dict], sample_items: list[dict]) -> str:
    parts: list[str] = []
    for field in fields[:10]:
        key = field["key"]
        label = field.get("label", key)
        value = _sample_value(key, sample_items)
        if value:
            parts.append(f'  - {key} ({label}): ej. "{value}"')
        else:
            parts.append(f"  - {key} ({label})")
    return "\n".join(parts)


def _build_dataset_hints(fields: list[dict], sample_items: list[dict]) -> list[str]:
    hints: list[str] = []

    has_images = any(_matches(f["key"], _IMAGE_KEYS) for f in fields)
    has_price = any(_matches(f["key"], _PRICE_KEYS) for f in fields)
    has_date = any(_matches(f["key"], _DATE_KEYS) for f in fields)
    has_rating = any(_matches(f["key"], _RATING_KEYS) for f in fields)
    has_category = any(_matches(f["key"], _CATEGORY_KEYS) for f in fields)
    has_location = any(_matches(f["key"], _LOCATION_KEYS) for f in fields)
    has_url = any(_matches(f["key"], _URL_KEYS) for f in fields)
    has_long_text = any(_matches(f["key"], _TEXT_KEYS) for f in fields)

    title_field = _detect_title_field(fields, sample_items)
    if title_field:
        sample = _sample_value(title_field, sample_items)
        suffix = f' (ej: "{sample}")' if sample else ""
        hints.append(
            f'El campo "{title_field}" parece ser un buen candidato para título principal o referencia textual del item{suffix}.'
        )

    if has_images:
        img_field = next((f["key"] for f in fields if _matches(f["key"], _IMAGE_KEYS)), None)
        hints.append(
            f'Hay imágenes (campo "{img_field}"); puedes usarlas si aportan valor y si el prompt del usuario permite un listado, detalle o portada más visual.'
        )

    if has_price:
        price_field = next((f["key"] for f in fields if _matches(f["key"], _PRICE_KEYS)), None)
        sample = _sample_value(price_field, sample_items) if price_field else None
        suffix = f' (ej: "{sample}")' if sample else ""
        hints.append(
            f'Hay precios o importes (campo "{price_field}"){suffix}; puedes destacarlos cuando ese dato sea importante para el tipo de sitio.'
        )

    if has_rating:
        hints.append(
            "Hay valoraciones o puntuaciones; puedes mostrarlas como metadato útil, badge o dato secundario si encaja con la estética solicitada."
        )

    if has_category:
        category_field = next((f["key"] for f in fields if _matches(f["key"], _CATEGORY_KEYS)), None)
        hints.append(
            f'Hay categorías o tipos (campo "{category_field}"); puedes usarlos para clasificar, etiquetar o contextualizar los items cuando aporte claridad.'
        )

    if has_date:
        hints.append(
            "Hay fechas; puedes mostrarlas en formato legible en listados o detalles si el contenido lo pide."
        )

    if has_location:
        hints.append(
            "Hay datos de ubicación; puedes mostrar ciudad, país o lugar como metadato cuando sea útil."
        )

    if has_url:
        hints.append(
            "Hay URLs externas; puedes añadir enlaces de salida o referencias externas si encajan con la experiencia del sitio."
        )

    if has_long_text:
        hints.append(
            "Hay texto largo; puedes resumirlo en listados y mostrarlo completo en detalle."
        )

    return hints


def _default_style_for_site_type(site_type: str) -> str:
    """Estilo por defecto suave, sin imponer una estética agresiva."""
    defaults = {
        "catalog": (
            "Catálogo claro y ordenado. Jerarquía visual limpia, navegación fácil y fichas bien estructuradas."
        ),
        "blog": (
            "Blog legible y sobrio. Buena tipografía, ritmo de lectura cómodo y metadatos claros."
        ),
        "portfolio": (
            "Portfolio limpio y cuidado. Mucho aire, buena jerarquía y foco en el contenido principal."
        ),
        "dashboard": (
            "Dashboard claro y funcional. Datos bien organizados, contraste correcto y lectura rápida."
        ),
        "other": (
            "Sitio web limpio y bien estructurado. Navegación clara y diseño coherente con el contenido."
        ),
    }
    return defaults.get(site_type, defaults["other"])


# ── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

def enrich_user_prompt(
    user_prompt: str,
    site_type: str,
    fields: list[dict],
    sample_items: list[dict],
) -> str:
    """
    Combina el prompt del usuario con contexto real del dataset.

    Regla principal:
    - El prompt del usuario siempre manda.
    - El contexto del dataset solo complementa, nunca sustituye.
    """
    base_prompt = (user_prompt or "").strip()
    field_context = _build_field_context(fields, sample_items)
    dataset_hints = _build_dataset_hints(fields, sample_items)

    context_lines = [
        f"Tipo de sitio: {site_type}",
        "",
        "Campos del dataset con valores reales:",
        field_context,
    ]

    if dataset_hints:
        context_lines += ["", "Sugerencias basadas en el dataset (opcionales):"]
        context_lines += [f"  - {hint}" for hint in dataset_hints]

    context = "\n".join(context_lines)

    if base_prompt:
        result = f"{base_prompt}\n\n---\nContexto del dataset:\n{context}"
    else:
        default_prompt = _default_style_for_site_type(site_type)
        result = f"{default_prompt}\n\n---\nContexto del dataset:\n{context}"

    if len(result) > _MAX_ENRICHED_CHARS:
        result = result[:_MAX_ENRICHED_CHARS] + "\n[contexto truncado por longitud]"

    return result