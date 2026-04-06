"""
enrich_prompt.py — Enriquece el prompt del usuario con contexto del dataset.
Analiza los campos y datos reales para dar instrucciones visuales concretas al LLM.
"""

# ── DETECCIÓN DE TIPOS DE CAMPO ───────────────────────────────────────────────

_IMAGE_KEYS    = {"image", "img", "photo", "thumbnail", "picture", "avatar", "cover",
                  "poster", "imagen", "foto", "miniatura", "portada", "thumb"}
_PRICE_KEYS    = {"price", "cost", "amount", "fee", "salary", "budget", "rate",
                  "precio", "coste", "importe", "tarifa", "salario"}
_DATE_KEYS     = {"date", "created_at", "updated_at", "published", "timestamp",
                  "year", "time", "fecha", "año", "tiempo", "publicado"}
_RATING_KEYS   = {"rating", "score", "stars", "votes", "rank", "puntuacion",
                  "valoracion", "estrellas", "votos", "nota"}
_CATEGORY_KEYS = {"category", "type", "genre", "tag", "label", "group", "kind",
                  "categoria", "tipo", "genero", "etiqueta", "grupo"}
_LOCATION_KEYS = {"location", "city", "country", "address", "place", "region",
                  "ubicacion", "ciudad", "pais", "direccion", "lugar", "region"}
_URL_KEYS      = {"url", "link", "website", "href", "enlace", "web", "sitio"}
_TEXT_KEYS     = {"description", "content", "body", "summary", "bio", "about",
                  "text", "descripcion", "contenido", "resumen", "biografia", "texto"}
_TITLE_KEYS    = {"title", "name", "nombre", "titulo", "common", "label",
                  "etiqueta", "heading", "encabezado"}


def _matches(key: str, keyword_set: set) -> bool:
    """Comprueba si el key del campo contiene alguna de las palabras clave."""
    key_lower = key.lower()
    return key_lower in keyword_set or any(k in key_lower for k in keyword_set)


def _detect_title_field(fields: list[dict], sample_items: list[dict]) -> str | None:
    """
    Intenta identificar el campo más representativo para usar como título.
    Primero busca por nombre semántico, luego por valores cortos en los ejemplos.
    """
    # 1. Buscar por nombre semántico
    for f in fields:
        if _matches(f["key"], _TITLE_KEYS):
            return f["key"]

    # 2. Buscar el primer campo con valores de texto corto en los ejemplos
    if sample_items:
        for f in fields:
            key = f["key"]
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


# ── FUNCIÓN PRINCIPAL ─────────────────────────────────────────────────────────

def enrich_user_prompt(
    user_prompt: str,
    site_type: str,
    fields: list[dict],
    sample_items: list[dict],
) -> str:
    """
    Combina el prompt del usuario con contexto real del dataset.
    Devuelve un prompt enriquecido con instrucciones visuales concretas para el LLM.
    """
    base_prompt = (user_prompt or "").strip()

    # ── Detectar tipos de campo presentes ────────────────────────────────────
    has_images   = any(_matches(f["key"], _IMAGE_KEYS)    for f in fields)
    has_price    = any(_matches(f["key"], _PRICE_KEYS)    for f in fields)
    has_date     = any(_matches(f["key"], _DATE_KEYS)     for f in fields)
    has_rating   = any(_matches(f["key"], _RATING_KEYS)   for f in fields)
    has_category = any(_matches(f["key"], _CATEGORY_KEYS) for f in fields)
    has_location = any(_matches(f["key"], _LOCATION_KEYS) for f in fields)
    has_url      = any(_matches(f["key"], _URL_KEYS)      for f in fields)
    has_long_text= any(_matches(f["key"], _TEXT_KEYS)     for f in fields)

    # ── Identificar campo principal (título) ─────────────────────────────────
    title_field = _detect_title_field(fields, sample_items)

    # ── Construir contexto de campos con valores reales ──────────────────────
    field_context_parts = []
    for f in fields[:10]:
        key   = f["key"]
        label = f.get("label", key)
        val   = _sample_value(key, sample_items)
        if val:
            field_context_parts.append(f'  - {key} ({label}): ej. "{val}"')
        else:
            field_context_parts.append(f'  - {key} ({label})')

    field_context = "\n".join(field_context_parts)

    # ── Construir instrucciones visuales según lo detectado ──────────────────
    visual_hints = []

    if title_field:
        ex = _sample_value(title_field, sample_items)
        ex_str = f' (ej: "{ex}")' if ex else ""
        visual_hints.append(f'El campo "{title_field}" es el título principal de cada item{ex_str} — úsalo como heading en las cards')

    if has_images:
        img_field = next((f["key"] for f in fields if _matches(f["key"], _IMAGE_KEYS)), None)
        visual_hints.append(f'Hay imágenes (campo "{img_field}") — úsalas como elemento visual principal con object-cover y aspect-video')

    if has_price:
        price_field = next((f["key"] for f in fields if _matches(f["key"], _PRICE_KEYS)), None)
        ex = _sample_value(price_field, sample_items) if price_field else None
        ex_str = f' (ej: "{ex}")' if ex else ""
        visual_hints.append(f'Hay precios (campo "{price_field}"){ex_str} — destácalos con tipografía grande y color de acento')

    if has_rating:
        visual_hints.append('Hay valoraciones/ratings — muéstralos con estrellas SVG o badge numérico destacado')

    if has_category:
        cat_field = next((f["key"] for f in fields if _matches(f["key"], _CATEGORY_KEYS)), None)
        visual_hints.append(f'Hay categorías (campo "{cat_field}") — añade badges de color por categoría en las cards')

    if has_date:
        visual_hints.append('Hay fechas — muéstralas en formato legible y destacadas en las cards')

    if has_location:
        visual_hints.append('Hay datos de ubicación — muestra ciudad o país en las cards')

    if has_url:
        visual_hints.append('Hay URLs externas — añade botones "Ver enlace" o "Visitar"')

    if has_long_text:
        visual_hints.append('Hay texto largo — usa truncatechars en listados, muestra completo en la página de detalle')

    # ── Ensamblar contexto final ──────────────────────────────────────────────
    context_lines = [
        f"Tipo de sitio: {site_type}",
        "",
        "Campos del dataset con valores reales:",
        field_context,
    ]

    if visual_hints:
        context_lines += ["", "Instrucciones visuales basadas en el dataset:"]
        context_lines += [f"  - {h}" for h in visual_hints]

    context = "\n".join(context_lines)

    # ── Combinar con el prompt del usuario ───────────────────────────────────
    if base_prompt:
        return f"{base_prompt}\n\n---\nContexto del dataset:\n{context}"
    else:
        defaults = {
            "catalog":   "Catálogo moderno y elegante. Cards con imagen grande, precio destacado, hover effects suaves. Diseño oscuro con acento de color vibrante.",
            "blog":      "Blog limpio y legible. Tipografía cuidada, fechas y categorías visibles, artículo destacado en la home.",
            "portfolio": "Portfolio minimalista y elegante. Imágenes grandes, mucho espacio, tipografía grande y llamativa.",
            "dashboard": "Dashboard profesional y compacto. Stat cards, tablas limpias, datos legibles de un vistazo. Azul y gris.",
            "other":     "Sitio web moderno y bien estructurado. Diseño oscuro con acentos de color, fácil de navegar.",
        }
        base = defaults.get(site_type, defaults["other"])
        return f"{base}\n\n---\nContexto del dataset:\n{context}"