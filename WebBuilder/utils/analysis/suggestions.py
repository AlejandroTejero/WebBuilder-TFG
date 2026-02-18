from __future__ import annotations      # Usar todo como strings
from .constants import ROLE_DEFS        # Catalogo de roles  
from .helpers import (                  
	_normalize_key, 
    _is_url, 
    _is_date,
    _is_number,
)

# ========================== SUGERIR MAPING POR PUNTUACION ==========================

# Sugiere items para cada select, las 5 mejores
# Devuelve un dict con las mejores opciones pero evitando la misma sugerencia para diferentes roles
def suggest_mapping_smart(items: list, role_defs: dict = ROLE_DEFS) -> dict:    
    suggestions = {role: [] for role in role_defs.keys()}
    if not items or not isinstance(items, list):
        return suggestions

    dict_items = [x for x in items if isinstance(x, dict)]
    if not dict_items:
        return suggestions

    all_keys = set()
    for obj in dict_items:
        all_keys.update(obj.keys())

    scores: dict[str, dict[str, int]] = {role: {} for role in role_defs.keys()}
    sample_items = dict_items[:20]

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

    # DIREFENCIA CON SUGGEST_MAPPING
    # Keys ya asignadas como primera sugerencia
    used_keys: set[str] = set() 
    
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


# ========================== ELIMINAR ==========================

# Sugiere items para cada select, las 5 mejores
# Devuelve un dict con las mejores opciones
def suggest_mapping(items: list, role_defs: dict = ROLE_DEFS) -> dict:
    # Inicializa sugerencias vacías para todos los roles
    suggestions = {role: [] for role in role_defs.keys()}
    if not items or not isinstance(items, list):
        return suggestions

    # Filtra solo los elementos que son dict
    dict_items = [x for x in items if isinstance(x, dict)]
    if not dict_items:
        return suggestions

    # Cojo todas las keys del dict para analizar posibles candidatos
    all_keys = set()
    for obj in dict_items:
        all_keys.update(obj.keys())

    # Creo tabla para puntuar uno por uno
    scores: dict[str, dict[str, int]] = {role: {} for role in role_defs.keys()}
    sample_items = dict_items[:20]
    for key in all_keys:
        normalized_key = _normalize_key(key)
        
        str_count = 0
        url_count = 0
        date_count = 0
        num_count = 0
        list_count = 0

        # Recorre la muestra
        for obj in sample_items:
            if key not in obj:
                continue
            value = obj.get(key)

            # Cuenta strings y detecta URLs/fechas
            if isinstance(value, str):
                str_count += 1
                if _is_url(value):
                    url_count += 1
                if _is_date(value):
                    date_count += 1

            # Cuenta números
            if _is_number(value):
                num_count += 1

            # Cuenta listas
            if isinstance(value, list):
                list_count += 1

        # Puntúa esta key para cada rol según hints y tipo
        for role_name, meta in role_defs.items():
            hints = meta["hints"]
            kind = meta["kind"]

            # Aplica score por coincidencias de nombre
            for hint in hints:
                normalized_hint = _normalize_key(hint)
                # Si coincide exacto, score fuerte
                if normalized_key == normalized_hint:
                    scores[role_name][key] = scores[role_name].get(key, 0) + 6
                # Si el hint está contenido, score medio
                elif normalized_hint in normalized_key:
                    scores[role_name][key] = scores[role_name].get(key, 0) + 3

            # Aplica score por tipo observado
            if kind == "url" and url_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == "date" and date_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == "number" and num_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == "list" and list_count >= 2:
                scores[role_name][key] = scores[role_name].get(key, 0) + 4
            if kind == "text" and str_count >= 3:
                scores[role_name][key] = scores[role_name].get(key, 0) + 1

    # Construye top-5 por rol ordenando por score
    for role_name in role_defs.keys():
        ordered = sorted(scores[role_name].items(), key=lambda kv: kv[1], reverse=True)
        # Guarda las top 5 keys sugeridas
        suggestions[role_name] = [k for k, _ in ordered[:5]]

    return suggestions

