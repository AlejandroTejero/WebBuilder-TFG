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

# ========================== SCORING: penalizaciones / nombres ==========================

# Penalizacion por paths complejos ELIMINAR
def _path_penalty(path: list) -> float:

    idxs = sum(1 for p in path if isinstance(p, int))
    return PATH_INDEX_PENALTY * idxs + PATH_LENGTH_PENALTY * max(0, len(path) - PATH_LENGTH_THRESHOLD)


# Devuelve el último nombre de key en el path (ignorando índices).
def _last_key_name(path: list) -> str:
    """
    """
    for p in reversed(path):
        if isinstance(p, str):
            return p.lower()
    return ""


# ========================== SCORING: lista candidata ==========================

# Calcula score de calidad para una lista como colección de items. ELIMINAR
def _score_list(node: list, path: list) -> float:
    n = len(node)
    if n == 0:
        return float("-inf")

    dict_items = [x for x in node if isinstance(x, dict)]
    dict_count = len(dict_items)
    density = dict_count / n

    # Si no hay dicts, no es una colección de items
    if dict_count == 0:
        return float("-inf")

    # Muchas APIs mezclan nulls/strings con dicts → penalizamos en vez de descartar
    density_pen = 0.0
    if density < MIN_DICT_DENSITY:
        density_pen = (MIN_DICT_DENSITY - density) * DENSITY_PENALTY_MULTIPLIER

    # Tamaño: crece con n pero saturado (sqrt para no disparar)
    size_score = min(n, MAX_SIZE_SCORE) ** 0.5

    # Consistencia de keys: mirar primeros items dict
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

    # Bonus por presencia de keys típicas de "contenido" (en al menos ~la mitad)
    commonish = {
        k for k in union
        if sum(1 for s in key_sets if k in s) >= max(1, len(key_sets) // 2)
    }
    hits = len(GOOD_KEYS.intersection({str(k).lower() for k in commonish}))
    good_bonus = min(hits, 6) * 0.35

    # Penaliza nombres típicos de metadata en el "último tramo" del path
    name = _last_key_name(path)
    meta_pen = 0.0
    if name in BAD_NAMES:
        meta_pen += 1.6

    # Penaliza si el union tiene muchas keys meta típicas
    metaish = {"meta", "links", "link", "type", "status", "count", "total"}
    meta_hits = len(metaish.intersection({str(k).lower() for k in union}))
    meta_pen += min(meta_hits, 4) * 0.25

    return (
        2.2 * size_score
        + 1.8 * density
        + 2.0 * consistency
        + 0.25 * avg_size / 10.0
        + good_bonus
        - meta_pen
        - _path_penalty(path)
        - density_pen
    )


# ========================== TRAVERSAL: búsqueda recursiva ==========================

# Recorre recursivamente la estructura buscando listas candidatas. ELIMINAR
def _walk_collect_best(node: object, path: list, best: dict) -> None:
    if isinstance(node, list):
        s = _score_list(node, path)
        if s > best["score"]:
            best.update(
                {
                    "found": True,
                    "path": path[:],
                    "count": len(node),
                    "items": node,
                    "score": s,
                }
            )

        # Recorre dentro de la lista (limitado) para encontrar listas anidadas
        for i, it in enumerate(node[:MAX_SAMPLE_ITEMS]):
            _walk_collect_best(it, path + [i], best)

    elif isinstance(node, dict):
        for k, v in node.items():
            _walk_collect_best(v, path + [k], best)


# ========================== API PUBLICA ==========================


def find_main_items(parsed_data: object) -> dict:
    # Mejor candidato encontrado durante el recorrido
    best = {"found": False, "path": None, "count": 0, "items": None, "score": float("-inf")}

    # Inicia la búsqueda desde la raíz
    _walk_collect_best(parsed_data, [], best)

    if not best["found"]:
        return {"found": False, "path": None, "count": 0, "sample_keys": [], "top_keys": []}

    # Analiza las keys de los items encontrados
    items = best["items"] or []
    key_counts: dict[str, int] = {}
    for item in items:
        if isinstance(item, dict):
            for key in item.keys():
                k = str(key)
                key_counts[k] = key_counts.get(k, 0) + 1

    top_keys = sorted(key_counts.items(), key=lambda kv: kv[1], reverse=True)

    # Obtiene keys de muestra del primer item dict
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
