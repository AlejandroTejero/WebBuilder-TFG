from __future__ import annotations

# ==================== LÍMITES Y UMBRALES ====================

# Número de items que se procesan para obtener el análisis
MAX_SAMPLE_ITEMS = 6
# Densidad mínima de dicts para considerar una lista como colección de items
MIN_DICT_DENSITY = 0.55
# Tamaño máximo para scoring (se satura después)
MAX_SIZE_SCORE = 500


# =========== ELIMINAR =========== (Parte de la calidad del analisis) ===========

# Penalización por baja densidad de dicts
DENSITY_PENALTY_MULTIPLIER = 6.0
# Penalización por paths profundos
PATH_INDEX_PENALTY = 1.25
PATH_LENGTH_PENALTY = 0.15
PATH_LENGTH_THRESHOLD = 6


# ==================== CATÁLOGO DE ROLES ====================

# Catálogo de roles del wizard (hints = lista de palabras tipicas para ese rol)
ROLE_DEFS = {
    "id": {"hints": ["id", "uuid", "identifier"], "kind": "text"},
	# strings con contenido
    "title": {"hints": ["title", "name", "headline", "label"], "kind": "text"},
    "subtitle": {"hints": ["subtitle", "tagline", "subheading"], "kind": "text"},
    "description": {"hints": ["description", "summary", "desc", "body", "text"], "kind": "text"},
    "content": {"hints": ["content", "html", "markdown", "article", "post"], "kind": "text"},
	# posible formato url
    "image": {"hints": ["image", "img", "photo", "picture"], "kind": "url"},
    "thumbnail": {"hints": ["thumbnail", "thumb", "avatar", "icon"], "kind": "url"},
    "link": {"hints": ["url", "link", "href", "permalink", "website"], "kind": "url"},
	# strings sueltos
    "author": {"hints": ["author", "user", "username", "by", "creator"], "kind": "text"},
    "date": {"hints": ["date", "created", "updated", "published", "timestamp"], "kind": "date"},
    "category": {"hints": ["category", "section", "type", "topic"], "kind": "text"},
    "tags": {"hints": ["tags", "tag", "keywords", "labels"], "kind": "list"},
    "price": {"hints": ["price", "amount", "cost", "value"], "kind": "number"},
    "currency": {"hints": ["currency", "curr", "iso", "symbol"], "kind": "text"},
}


# ==================== LISTAS DE NOMBRES PARA PREDECCION ====================

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

