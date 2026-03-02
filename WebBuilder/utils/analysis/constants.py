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

