"""
Detección de la colección principal de items
Identifica la lista más adecuada para usar como fuente de datos
"""

from __future__ import annotations

from .constants import (
    BAD_NAMES,
    GOOD_KEYS,
    MIN_DICT_DENSITY,
    MAX_SIZE_SCORE,
    DENSITY_PENALTY_MULTIPLIER,
    PATH_INDEX_PENALTY,
    PATH_LENGTH_PENALTY,
    PATH_LENGTH_THRESHOLD,
    MAX_SAMPLE_ITEMS,
)


def find_main_items(parsed_data: object) -> dict:
    """
    Encuentra la colección principal (lista) con heurísticas
    
    Objetivo: elegir una lista que tenga pinta de "items" y evitar listas de metadata
    (facets, links, etc.). Devuelve path + conteos de keys para ayudar al wizard.
    
    Args:
        parsed_data: Datos parseados (dict, list, etc.)
        
    Returns:
        Dict con:
        - found: bool - Si se encontró una colección
        - path: list - Path a la colección
        - count: int - Número de items
        - sample_keys: list - Keys de un item de muestra
        - top_keys: list - Keys más frecuentes (tuples de (key, count))
    """
    best = {"found": False, "path": None, "count": 0, "items": None, "score": float("-inf")}

    def path_penalty(path: list) -> float:
        """
        Calcula penalización por complejidad del path
        Penaliza paths con índices y paths muy profundos
        """
        # Penaliza paths con índices (menos "estables" / suelen ser listas internas)
        idxs = sum(1 for p in path if isinstance(p, int))
        return PATH_INDEX_PENALTY * idxs + PATH_LENGTH_PENALTY * max(0, len(path) - PATH_LENGTH_THRESHOLD)

    def last_key_name(path: list) -> str:
        """
        Obtiene el último nombre de key en el path (ignora índices)
        """
        for p in reversed(path):
            if isinstance(p, str):
                return p.lower()
        return ""

    def score_list(node: list, path: list) -> float:
        """
        Calcula score de calidad para una lista como colección de items
        
        Considera:
        - Tamaño de la lista
        - Densidad de dicts
        - Consistencia de keys
        - Presencia de keys típicas de contenido
        - Penalizaciones por metadata
        """
        n = len(node)
        if n == 0:
            return float("-inf")

        dict_items = [x for x in node if isinstance(x, dict)]
        dict_count = len(dict_items)
        density = dict_count / n
        
        # Si no hay dicts, no es una colección de items
        if dict_count == 0:
            return float("-inf")

        # Muchas APIs mezclan nulls/strings con dicts
        # Aplicamos penalización en vez de descartar
        density_pen = 0.0
        if density < MIN_DICT_DENSITY:
            density_pen = (MIN_DICT_DENSITY - density) * DENSITY_PENALTY_MULTIPLIER

        # Tamaño: crece con n pero saturado
        size_score = min(n, MAX_SIZE_SCORE) ** 0.5  # sqrt

        # Consistencia de keys (mira primeros items)
        sample = dict_items[:MAX_SAMPLE_ITEMS]
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
            - density_pen
        )

    def walk(node: object, path: list):
        """
        Recorre recursivamente la estructura buscando listas candidatas
        """
        nonlocal best
        
        if isinstance(node, list):
            s = score_list(node, path)
            if s > best["score"]:
                best = {"found": True, "path": path[:], "count": len(node), "items": node, "score": s}
            # Recorre dentro de la lista (limitando para evitar explosión)
            for i, it in enumerate(node[:MAX_SAMPLE_ITEMS]):
                walk(it, path + [i])
                
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + [k])

    # Inicia la búsqueda
    walk(parsed_data, [])

    if not best["found"]:
        return {"found": False, "path": None, "count": 0, "sample_keys": [], "top_keys": []}

    # Analiza las keys de los items encontrados
    items = best["items"] or []
    key_counts: dict[str, int] = {}
    for item in items:
        if isinstance(item, dict):
            for key in item.keys():
                key_counts[str(key)] = key_counts.get(str(key), 0) + 1

    top_keys = sorted(key_counts.items(), key=lambda kv: kv[1], reverse=True)

    # Obtiene keys de muestra del primer item
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
