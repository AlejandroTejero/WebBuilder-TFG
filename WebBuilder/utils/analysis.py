# Permite usar anotaciones de tipos como strings
from __future__ import annotations

# Importa re para heurísticas de fechas
import re

# Importa detect_format para intentar inferir el formato cuando hay raw_text
from .parsers import detect_format


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


# Busca recursivamente la lista principal de items (list[dict]) más grande
def find_main_items(parsed_data: object) -> dict:
    """Encuentra la colección principal (lista) con heurísticas.

    Objetivo: elegir una lista que tenga pinta de "items" y evitar listas de metadata
    (facets, links, etc.). Devuelve path + conteos de keys para ayudar al wizard.
    """
    best = {"found": False, "path": None, "count": 0, "items": None, "score": float("-inf")}

    BAD_NAMES = {
        "meta", "metadata", "links", "link", "headers", "header", "facets", "facet",
        "aggregations", "aggregation", "pagination", "page", "pages", "request", "response",
        "status", "errors", "error", "warnings", "warning",
    }
    GOOD_KEYS = {"id", "uuid", "title", "name", "headline", "description", "summary", "content", "text", "url", "link", "href", "image", "thumbnail"}

    def path_penalty(path: list) -> float:
        # Penaliza paths con índices (menos "estables" / suelen ser listas internas)
        idxs = sum(1 for p in path if isinstance(p, int))
        return 1.25 * idxs + 0.15 * max(0, len(path) - 6)

    def last_key_name(path: list) -> str:
        for p in reversed(path):
            if isinstance(p, str):
                return p.lower()
        return ""

    def score_list(node: list, path: list) -> float:
        n = len(node)
        if n == 0:
            return float("-inf")

        dict_items = [x for x in node if isinstance(x, dict)]
        dict_count = len(dict_items)
        density = dict_count / n

        # Requerimos una densidad mínima de dicts
        if density < 0.55:
            return float("-inf")

        # Tamaño: crece con n pero saturado
        size_score = min(n, 500) ** 0.5  # sqrt

        # Consistencia de keys (mira primeros 6 dicts)
        sample = dict_items[:6]
        key_sets = [set(d.keys()) for d in sample if isinstance(d, dict)]
        if not key_sets:
            return float("-inf")
        union = set().union(*key_sets)
        # Evita listas de dicts vacíos
        if len(union) == 0:
            return float("-inf")
        avg_size = sum(len(s) for s in key_sets) / len(key_sets)
        # Consistencia aproximada: promedio de |s| / |union|
        consistency = sum((len(s) / len(union)) for s in key_sets) / len(key_sets)

        # Bonus por presencia de keys típicas de "contenido"
        commonish = {k for k in union if sum(1 for s in key_sets if k in s) >= max(1, len(key_sets) // 2)}
        good_bonus = 0.0
        hits = len(GOOD_KEYS.intersection({str(k).lower() for k in commonish}))
        good_bonus += min(hits, 6) * 0.35

        # Penaliza nombres típicos de metadata
        name = last_key_name(path)
        meta_pen = 0.0
        if name in BAD_NAMES:
            meta_pen += 1.6
        # Penaliza si el union es casi todo keys "meta" típicas
        metaish = {"meta", "links", "link", "type", "status", "count", "total"}
        meta_hits = len(metaish.intersection({str(k).lower() for k in union}))
        meta_pen += min(meta_hits, 4) * 0.25

        # Score final
        return (
            2.2 * size_score
            + 1.8 * density
            + 2.0 * consistency
            + 0.25 * avg_size / 10.0
            + good_bonus
            - meta_pen
            - path_penalty(path)
        )

    def walk(node: object, path: list):
        nonlocal best
        if isinstance(node, list):
            s = score_list(node, path)
            if s > best["score"]:
                best = {"found": True, "path": path[:], "count": len(node), "items": node, "score": s}
            # Recorre dentro de la lista (limitando para evitar explosión)
            for i, it in enumerate(node[:6]):
                walk(it, path + [i])
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + [k])

    walk(parsed_data, [])

    if not best["found"]:
        return {"found": False, "path": None, "count": 0, "sample_keys": [], "top_keys": []}

    items = best["items"] or []
    key_counts: dict[str, int] = {}
    for item in items:
        if isinstance(item, dict):
            for key in item.keys():
                key_counts[str(key)] = key_counts.get(str(key), 0) + 1

    top_keys = sorted(key_counts.items(), key=lambda kv: kv[1], reverse=True)

    sample_keys: list[str] = []
    for item in items:
        if isinstance(item, dict):
            sample_keys = [str(k) for k in item.keys()]
            break

    return {
        "found": True,
        "path": best["path"],
        "count": best["count"],
        "sample_keys": sample_keys[:25],
        "top_keys": top_keys[:10],
    }



# Navega parsed_data siguiendo un path de keys/índices
def get_by_path(parsed_data: object, path: list):
    # Empieza en la raíz
    node = parsed_data
    # Recorre cada paso del path
    for step in path:
        # Si el paso es un índice
        if isinstance(step, int):
            # Si el nodo actual no es lista o índice inválido, devuelve None
            if not isinstance(node, list) or step < 0 or step >= len(node):
                # No existe el path
                return None
            # Avanza al elemento indexado
            node = node[step]
        # Si el paso es una key de dict
        elif isinstance(step, str):
            # Si el nodo actual no es dict o no existe la key, devuelve None
            if not isinstance(node, dict) or step not in node:
                # No existe el path
                return None
            # Avanza al valor de esa key
            node = node[step]
        # Si el paso no es int ni str, devolvemos None
        else:
            # Path inválido
            return None
    # Devuelve el nodo final
    return node


# Normaliza una key para comparaciones
def _normalize_key(text: str) -> str:
    # Pasa a minúsculas y recorta espacios
    return text.strip().lower()


# Heurística: parece URL
def _is_url(value: object) -> bool:
    # Solo tiene sentido si es string
    if not isinstance(value, str):
        # No puede ser URL
        return False
    # Normaliza el string
    lowered = value.strip().lower()
    # Comprueba prefijo http/https
    return lowered.startswith("http://") or lowered.startswith("https://")


# Heurística: parece fecha
def _is_date(value: object) -> bool:
    # Solo tiene sentido si es string
    if not isinstance(value, str):
        # No puede ser fecha
        return False
    # Recorta espacios
    text = value.strip()
    # Busca patrón YYYY-MM-DD o YYYY/MM/DD
    if re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", text):
        # Parece fecha
        return True
    # Busca patrón ISO con T
    if re.search(r"\d{4}-\d{2}-\d{2}T", text):
        # Parece fecha ISO
        return True
    # Si no cuadra, no es fecha
    return False


# Heurística: parece número
def _is_number(value: object) -> bool:
    # True si es int/float pero no bool
    return isinstance(value, (int, float)) and not isinstance(value, bool)


# Sugiere candidatos de keys por rol (top-5)
def suggest_mapping(items: list, role_defs: dict = ROLE_DEFS) -> dict:
    # Inicializa sugerencias vacías para todos los roles
    suggestions = {role: [] for role in role_defs.keys()}
    # Si items no es lista o está vacío, devuelve vacío
    if not items or not isinstance(items, list):
        # Devuelve sugerencias vacías
        return suggestions

    # Filtra solo los elementos que son dict
    dict_items = [x for x in items if isinstance(x, dict)]
    # Si no hay dicts, devuelve vacío
    if not dict_items:
        # Devuelve sugerencias vacías
        return suggestions

    # Junta todas las keys observadas
    all_keys = set()
    # Recorre dicts para recolectar keys
    for obj in dict_items:
        # Añade keys de cada objeto al set
        all_keys.update(obj.keys())

    # Crea tabla de scores por rol y key
    scores: dict[str, dict[str, int]] = {role: {} for role in role_defs.keys()}
    # Toma una muestra de items para mirar tipos
    sample_items = dict_items[:20]

    # Recorre cada key y calcula señales
    for key in all_keys:
        # Normaliza la key
        normalized_key = _normalize_key(key)
        # Inicializa contadores por tipo
        str_count = 0
        # Inicializa contadores URL
        url_count = 0
        # Inicializa contadores date
        date_count = 0
        # Inicializa contadores number
        num_count = 0
        # Inicializa contadores list
        list_count = 0

        # Recorre la muestra para estimar tipos
        for obj in sample_items:
            # Si la key no está en el objeto, salta
            if key not in obj:
                # Sigue al siguiente
                continue
            # Obtiene el valor de esa key
            value = obj.get(key)

            # Si el valor es string, suma str_count
            if isinstance(value, str):
                # Incrementa contador de strings
                str_count += 1
                # Si parece URL, suma url_count
                if _is_url(value):
                    # Incrementa contador de urls
                    url_count += 1
                # Si parece fecha, suma date_count
                if _is_date(value):
                    # Incrementa contador de fechas
                    date_count += 1

            # Si parece número, suma num_count
            if _is_number(value):
                # Incrementa contador de números
                num_count += 1

            # Si el valor es lista, suma list_count
            if isinstance(value, list):
                # Incrementa contador de listas
                list_count += 1

        # Puntúa esta key para cada rol según hints y tipo
        for role_name, meta in role_defs.items():
            # Extrae hints del rol
            hints = meta["hints"]
            # Extrae kind del rol
            kind = meta["kind"]

            # Aplica score por coincidencias de nombre
            for hint in hints:
                # Normaliza el hint
                normalized_hint = _normalize_key(hint)
                # Si coincide exacto, score fuerte
                if normalized_key == normalized_hint:
                    # Suma score alto
                    scores[role_name][key] = scores[role_name].get(key, 0) + 6
                # Si el hint está contenido, score medio
                elif normalized_hint in normalized_key:
                    # Suma score medio
                    scores[role_name][key] = scores[role_name].get(key, 0) + 3

            # Aplica score por tipo observado
            if kind == "url" and url_count >= 2:
                # Suma score por url
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            # Aplica score por fecha
            if kind == "date" and date_count >= 2:
                # Suma score por date
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            # Aplica score por número
            if kind == "number" and num_count >= 2:
                # Suma score por number
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            # Aplica score por lista
            if kind == "list" and list_count >= 2:
                # Suma score por list
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            # Aplica score pequeño por texto frecuente
            if kind == "text" and str_count >= 3:
                # Suma score pequeño por texto
                scores[role_name][key] = scores[role_name].get(key, 0) + 1

    # Construye top-5 por rol ordenando por score
    for role_name in role_defs.keys():
        # Ordena (key, score) por score desc
        ordered = sorted(scores[role_name].items(), key=lambda kv: kv[1], reverse=True)
        # Guarda las top 5 keys sugeridas
        suggestions[role_name] = [k for k, _ in ordered[:5]]

    # Devuelve sugerencias por rol
    return suggestions


# Construye el dict final de análisis para UI
def _path_display(path: list | None) -> str:
    if path is None:
        return "—"
    if path == []:
        return "(raíz)"
    parts: list[str] = []
    for p in path:
        if isinstance(p, int):
            parts.append(f"[{p}]")
        else:
            parts.append(str(p))
    return " → ".join(parts)



def build_analysis(parsed_data: object, raw_text: str | None = None) -> dict:
    # Intenta detectar formato si tenemos raw_text
    detected_format = detect_format(raw_text) if raw_text else "unknown"

    # Determina el tipo raíz del payload parseado
    if isinstance(parsed_data, dict):
        # Raíz dict
        root_type = "dict"
    elif isinstance(parsed_data, list):
        # Raíz list
        root_type = "list"
    else:
        # Raíz otro tipo
        root_type = type(parsed_data).__name__

    # Encuentra la colección principal de items
    main = find_main_items(parsed_data)
    # Construye resumen de colección principal
    main_collection = {
        # Indica si se encontró colección
        "found": bool(main.get("found")),
        # Path a la colección
        "path": main.get("path"),
        # Número de elementos
        "count": int(main.get("count", 0) or 0),
        # Top keys con frecuencias
        "top_keys": main.get("top_keys", []),
        # Sample keys
        "sample_keys": main.get("sample_keys", []),
        # Path mostrado de forma amigable
        "path_display": _path_display(main.get("path")),
    }

    # Lista solo de keys top (sin conteos)
    top_keys_only = [k for (k, _) in main_collection["top_keys"]] if main_collection["top_keys"] else []

    # Acumula keys “all” combinando sample + top sin duplicados
    all_keys: list[str] = []
    # Añade sample_keys primero
    for key in main_collection["sample_keys"]:
        # Evita duplicados
        if key not in all_keys:
            # Añade key
            all_keys.append(key)
    # Añade top_keys después
    for key in top_keys_only:
        # Evita duplicados
        if key not in all_keys:
            # Añade key
            all_keys.append(key)

    # Inicializa items_list por defecto
    items_list = []
    # Si hay colección encontrada y path válido, extrae items por path
    if main_collection["found"] and main_collection["path"] is not None:
        # Lee el nodo por path o lista vacía
        items_list = get_by_path(parsed_data, main_collection["path"]) or []

    # Calcula sugerencias si items_list es lista
    if isinstance(items_list, list):
        # Obtiene sugerencias por rol
        suggestions = suggest_mapping_smart(items_list, ROLE_DEFS)
    else:
        # Si no hay lista, sugiere vacío por rol
        suggestions = {role: [] for role in ROLE_DEFS.keys()}

    # Mensaje de ayuda cuando no se detecta colección principal
    analysis_message = ""
    if not main_collection["found"]:
        analysis_message = (
            "No se detectó una lista principal de items. "
            "Puede ser un objeto único o estar muy anidado. "
            "Si el dataset sí tiene items, revisa la ruta o prueba otra URL."
        )

    # Devuelve el análisis consolidado
    return {
        # Formato detectado (json/xml/unknown)
        "format": detected_format,
        # Tipo raíz del payload
        "root_type": root_type,
        # Mensaje UX (si aplica)
        "message": analysis_message,
        # Info de colección principal
        "main_collection": main_collection,
        # Keys agregadas
        "keys": {"all": all_keys, "top": top_keys_only[:10]},
        # Lista de roles disponibles
        "roles": list(ROLE_DEFS.keys()),
        # Sugerencias por rol
        "suggestions": suggestions,
    }


# ==================== ✨ FUNCIONES MEJORADAS AGREGADAS ✨ ====================

def suggest_mapping_smart(items: list, role_defs: dict = ROLE_DEFS) -> dict:
    """
    Versión mejorada de suggest_mapping que evita sugerir la misma key para múltiples roles.
    
    MEJORAS vs suggest_mapping original:
    - Asignación greedy: roles prioritarios 'reservan' sus mejores sugerencias
    - Reduce repeticiones en las primeras sugerencias de cada rol
    - Mantiene compatibilidad con código existente
    
    Args:
        items: Lista de dicts del dataset
        role_defs: Definición de roles (usa ROLE_DEFS por defecto)
    
    Returns:
        dict: {role_name: [suggested_keys]} - Top 5 sugerencias por rol
    """
    
    # Inicializa sugerencias vacías para todos los roles
    suggestions = {role: [] for role in role_defs.keys()}
    
    # Si items no es lista o está vacío, devuelve vacío
    if not items or not isinstance(items, list):
        return suggestions

    # Filtra solo los elementos que son dict
    dict_items = [x for x in items if isinstance(x, dict)]
    if not dict_items:
        return suggestions

    # Junta todas las keys observadas
    all_keys = set()
    for obj in dict_items:
        all_keys.update(obj.keys())

    # Crea tabla de scores por rol y key (MISMO CÓDIGO QUE ORIGINAL)
    scores: dict[str, dict[str, int]] = {role: {} for role in role_defs.keys()}
    sample_items = dict_items[:20]

    # Calcula scores (EXACTAMENTE IGUAL QUE suggest_mapping original)
    for key in all_keys:
        normalized_key = _normalize_key(key)
        str_count = 0
        url_count = 0
        date_count = 0
        num_count = 0
        list_count = 0

        for obj in sample_items:
            if key not in obj:
                continue
            value = obj.get(key)

            if isinstance(value, str):
                str_count += 1
                if _is_url(value):
                    url_count += 1
                if _is_date(value):
                    date_count += 1

            if _is_number(value):
                num_count += 1

            if isinstance(value, list):
                list_count += 1

        # Scoring por hint y tipo
        for role_name, meta in role_defs.items():
            hints = meta['hints']
            kind = meta['kind']

            for hint in hints:
                normalized_hint = _normalize_key(hint)
                if normalized_key == normalized_hint:
                    scores[role_name][key] = scores[role_name].get(key, 0) + 6
                elif normalized_hint in normalized_key:
                    scores[role_name][key] = scores[role_name].get(key, 0) + 3

            if kind == 'url' and url_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == 'date' and date_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == 'number' and num_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == 'list' and list_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == 'text' and str_count >= 3:
                scores[role_name][key] = scores[role_name].get(key, 0) + 1

    # ✨ NUEVA LÓGICA: Asignación greedy por prioridad de rol
    used_keys: set[str] = set()  # Keys ya asignadas como primera sugerencia
    
    # Define prioridad de roles (los más críticos primero)
    role_priority = [
        'id',           # Identificador único (muy crítico)
        'title',        # Título (más importante)
        'description',  # Descripción (segunda más importante)
        'image',        # Imagen principal
        'link',         # URL/enlace
        'subtitle',     # Subtítulo
        'content',      # Contenido largo
        'author',       # Autor
        'date',         # Fecha
        'thumbnail',    # Miniatura
        'category',     # Categoría
        'tags',         # Etiquetas
        'price',        # Precio
        'currency',     # Moneda
    ]
    
    # Asigna sugerencias por prioridad
    for role_name in role_priority:
        if role_name not in scores:
            continue
        
        # Ordena candidates por score descendente
        candidates = sorted(
            scores[role_name].items(), 
            key=lambda kv: kv[1], 
            reverse=True
        )
        
        role_suggestions = []
        for key, score in candidates:
            if score <= 0:
                break
            
            # Si esta key NO ha sido usada como primera sugerencia
            if key not in used_keys:
                role_suggestions.append(key)
                
                # Solo marca como 'usada' la PRIMERA sugerencia
                if len(role_suggestions) == 1:
                    used_keys.add(key)
                
                # Toma hasta 5 sugerencias
                if len(role_suggestions) >= 5:
                    break
        
        suggestions[role_name] = role_suggestions
    
    # Roles que no están en priority list
    for role_name in role_defs.keys():
        if role_name not in suggestions or not suggestions[role_name]:
            candidates = sorted(
                scores[role_name].items(), 
                key=lambda kv: kv[1], 
                reverse=True
            )
            suggestions[role_name] = [
                k for k, s in candidates[:5] if s > 0
            ]
    
    return suggestions


def calculate_mapping_quality(field_mapping: dict, analysis_result: dict | None = None) -> dict:
    """
    Calcula un score de calidad del mapping (0-100).
    
    Útil para mostrar al usuario qué tan bueno es su mapping actual.
    Considera: campos obligatorios, duplicados, y completitud.
    
    Args:
        field_mapping: Mapping actual del usuario {role: key}
        analysis_result: Análisis de la API (opcional, no usado actualmente)
    
    Returns:
        {
            'score': int,           # Score 0-100
            'percentage': int,      # Same as score
            'quality': str,         # 'Excelente ✅', 'Bueno 👍', etc.
            'color': str,           # 'green', 'blue', 'orange', 'red'
            'issues': list[str],    # Lista de problemas/sugerencias
        }
    """
    score = 0
    max_score = 100
    issues = []
    
    # +30 puntos: Tiene title (CRÍTICO)
    if field_mapping.get('title'):
        score += 30
    else:
        issues.append('⚠️ Falta título - es el campo más importante')
    
    # +20 puntos: Tiene description
    if field_mapping.get('description'):
        score += 20
    else:
        issues.append('⚠️ Falta descripción - ayuda a entender el contenido')
    
    # +15 puntos: Tiene image
    if field_mapping.get('image'):
        score += 15
    else:
        issues.append('💡 Considera agregar una imagen - hace la web más atractiva')
    
    # +10 puntos: Tiene link
    if field_mapping.get('link'):
        score += 10
    else:
        issues.append('💡 Agrega un enlace si quieres que los usuarios accedan al contenido original')
    
    # +10 puntos: Tiene date
    if field_mapping.get('date'):
        score += 10
    else:
        issues.append('💡 La fecha ayuda a contextualizar el contenido')
    
    # +5 puntos: Tiene author
    if field_mapping.get('author'):
        score += 5
    
    # +10 puntos: No hay duplicados en roles críticos
    critical_roles = ['title', 'description', 'content', 'subtitle', 'author']
    used_keys = {}
    has_duplicates = False
    
    for role in critical_roles:
        key = field_mapping.get(role)
        if key and key in used_keys:
            has_duplicates = True
            issues.append(
                f"❌ '{role}' y '{used_keys[key]}' usan el mismo campo '{key}' - "
                f"esto hará que se muestre contenido repetido"
            )
        elif key:
            used_keys[key] = role
    
    if not has_duplicates:
        score += 10
    
    # Clasificación por score
    if score >= 80:
        quality = 'Excelente'
        quality_emoji = '✅'
        color = 'green'
    elif score >= 60:
        quality = 'Bueno'
        quality_emoji = '👍'
        color = 'blue'
    elif score >= 40:
        quality = 'Aceptable'
        quality_emoji = '⚠️'
        color = 'orange'
    else:
        quality = 'Mejorable'
        quality_emoji = '❌'
        color = 'red'
    
    return {
        'score': score,
        'max_score': max_score,
        'percentage': score,  # Ya está en escala 0-100
        'quality': f'{quality} {quality_emoji}',
        'color': color,
        'issues': issues,
    }

