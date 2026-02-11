"""
Sugerencias de mapping automático
Analiza items y sugiere qué keys mapear a qué roles
"""

from __future__ import annotations

from .constants import ROLE_DEFS
from .helpers import _normalize_key, _is_url, _is_date, _is_number


def suggest_mapping(items: list, role_defs: dict = ROLE_DEFS) -> dict:
    """
    Sugiere candidatos de keys por rol (top-5)
    
    Analiza los items y sugiere qué keys son buenas candidatas para cada rol
    basándose en nombres de keys y tipos de datos observados.
    
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
        url_count = 0
        date_count = 0
        num_count = 0
        list_count = 0

        # Recorre la muestra para estimar tipos
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
        # Ordena (key, score) por score desc
        ordered = sorted(scores[role_name].items(), key=lambda kv: kv[1], reverse=True)
        # Guarda las top 5 keys sugeridas
        suggestions[role_name] = [k for k, _ in ordered[:5]]

    return suggestions


def suggest_mapping_smart(items: list, role_defs: dict = ROLE_DEFS) -> dict:
    """
    Versión mejorada de suggest_mapping que evita sugerir la misma key para múltiples roles
    
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
