"""
enrich_prompt.py — Enriquece el prompt del usuario con contexto del dataset.
Si el prompt es vago, añade información útil para que el LLM genere mejor.
"""


def enrich_user_prompt(
    user_prompt: str,
    site_type: str,
    fields: list[dict],
    sample_items: list[dict],
) -> str:
    """
    Combina el prompt del usuario con contexto del dataset.
    Devuelve un prompt enriquecido más accionable para el LLM.
    """
    base_prompt = (user_prompt or "").strip()

    # Extraer info útil del dataset
    field_names = [f["key"] for f in fields[:8]]
    has_images = any(
        "image" in f["key"].lower() or "img" in f["key"].lower() or "photo" in f["key"].lower()
        for f in fields
    )
    has_price = any(
        "price" in f["key"].lower() or "cost" in f["key"].lower()
        for f in fields
    )
    has_date = any(
        "date" in f["key"].lower() or "time" in f["key"].lower()
        for f in fields
    )

    # Construir contexto automático
    context_parts = []

    if site_type and site_type != "other":
        context_parts.append(f"Tipo de sitio detectado: {site_type}")

    if field_names:
        context_parts.append(f"Campos disponibles: {', '.join(field_names)}")

    if has_images:
        context_parts.append("El dataset tiene imágenes — úsalas de forma destacada")

    if has_price:
        context_parts.append("El dataset tiene precios — destácalos visualmente")

    if has_date:
        context_parts.append("El dataset tiene fechas — muéstralas de forma clara")

    context = ". ".join(context_parts)

    # Combinar prompt del usuario con contexto
    if base_prompt:
        return f"{base_prompt}\n\nContexto del dataset: {context}"
    else:
        # Sin prompt del usuario, generar uno básico según el tipo
        defaults = {
            "catalog": "Diseño moderno para catálogo de productos, grid de cards con imagen y precio destacado.",
            "blog": "Blog limpio y legible, tipografía clara, fechas y categorías visibles.",
            "portfolio": "Portfolio elegante, imágenes grandes, diseño minimalista y profesional.",
            "dashboard": "Dashboard compacto y profesional, datos claros, tablas y métricas.",
            "other": "Diseño limpio y moderno, fácil de navegar.",
        }
        base = defaults.get(site_type, defaults["other"])
        return f"{base}\n\nContexto del dataset: {context}"