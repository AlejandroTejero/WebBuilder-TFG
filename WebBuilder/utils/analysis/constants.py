"""
Constantes y configuraciones del módulo de análisis
"""

from __future__ import annotations


# ==================== CATÁLOGO DE ROLES ====================

# Catálogo de roles del wizard (fuente de verdad)
ROLE_DEFS = {
    # Rol id
    "id": {"hints": ["id", "uuid", "identifier"], "kind": "text"},
    # Rol title
    "title": {"hints": ["title", "name", "headline", "label"], "kind": "text"},
    # Rol subtitle
    "subtitle": {"hints": ["subtitle", "tagline", "subheading"], "kind": "text"},
    # Rol description
    "description": {"hints": ["description", "summary", "desc", "body", "text"], "kind": "text"},
    # Rol content
    "content": {"hints": ["content", "html", "markdown", "article", "post"], "kind": "text"},
    # Rol image
    "image": {"hints": ["image", "img", "photo", "picture"], "kind": "url"},
    # Rol thumbnail
    "thumbnail": {"hints": ["thumbnail", "thumb", "avatar", "icon"], "kind": "url"},
    # Rol link
    "link": {"hints": ["url", "link", "href", "permalink", "website"], "kind": "url"},
    # Rol author
    "author": {"hints": ["author", "user", "username", "by", "creator"], "kind": "text"},
    # Rol date
    "date": {"hints": ["date", "created", "updated", "published", "timestamp"], "kind": "date"},
    # Rol category
    "category": {"hints": ["category", "section", "type", "topic"], "kind": "text"},
    # Rol tags
    "tags": {"hints": ["tags", "tag", "keywords", "labels"], "kind": "list"},
    # Rol price
    "price": {"hints": ["price", "amount", "cost", "value"], "kind": "number"},
    # Rol currency
    "currency": {"hints": ["currency", "curr", "iso", "symbol"], "kind": "text"},
}


# ==================== LISTAS DE NOMBRES PARA HEURÍSTICAS ====================

# Nombres de keys que suelen ser metadata (no items)
BAD_NAMES = {
    "meta", "metadata", "links", "link", "headers", "header", "facets", "facet",
    "aggregations", "aggregation", "pagination", "page", "pages", "request", "response",
    "status", "errors", "error", "warnings", "warning",
}

# Nombres de keys que suelen indicar items/contenido
GOOD_KEYS = {
    "id", "uuid", "title", "name", "headline", "description", "summary", 
    "content", "text", "url", "link", "href", "image", "thumbnail"
}


# ==================== LÍMITES Y UMBRALES ====================

# Número máximo de items a muestrear para análisis
MAX_SAMPLE_ITEMS = 6

# Densidad mínima de dicts para considerar una lista como colección de items
MIN_DICT_DENSITY = 0.55

# Tamaño máximo para scoring (se satura después)
MAX_SIZE_SCORE = 500

# Penalización por baja densidad de dicts
DENSITY_PENALTY_MULTIPLIER = 6.0

# Penalización por paths profundos
PATH_INDEX_PENALTY = 1.25
PATH_LENGTH_PENALTY = 0.15
PATH_LENGTH_THRESHOLD = 6
