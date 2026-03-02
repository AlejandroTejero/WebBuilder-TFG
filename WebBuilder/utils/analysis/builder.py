from __future__ import annotations

from ..ingest.parsers import detect_format
from .helpers import get_by_path, _path_display
from .detection import find_main_items

"""
Construye el dict final de análisis para UI

Pasos del analisis:
1. Detecta el formato del raw_text
2. Determina el tipo de la raíz
3. Encuentra la colección principal de items
4. Construye un dict consolidado para el frontend

Args:
1. parsed_data: Datos parseados (dict, list, etc.)
2. raw_text: Texto crudo original (opcional, para detectar formato)
"""

def build_analysis(parsed_data: object, raw_text: str | None = None) -> dict:

    # ========================== 1) METADATA PAYLOAD ==========================

    detected_format = detect_format(raw_text) if raw_text else "unknown"

    if isinstance(parsed_data, dict):
        root_type = "dict"
    elif isinstance(parsed_data, list):
        root_type = "list"
    else:
        root_type = type(parsed_data).__name__

    # ========================== 2) COLECCION PRINCIPAL ==========================

    main = find_main_items(parsed_data)

    main_collection = {
        "found": bool(main.get("found")),
        "path": main.get("path"),
        "count": int(main.get("count", 0) or 0),
        "top_keys": main.get("top_keys", []),
        "sample_keys": main.get("sample_keys", []),
        "path_display": _path_display(main.get("path")),
    }

    # ========================== 3) KEYS DISPONIBLES ==========================

    top_keys_only = [k for (k, _) in main_collection["top_keys"]] if main_collection["top_keys"] else []

    all_keys: list[str] = []
    for key in main_collection["sample_keys"]:
        if key not in all_keys:
            all_keys.append(key)
    for key in top_keys_only:
        if key not in all_keys:
            all_keys.append(key)

    # ========================== 4) MENSAJE + OUTPUT FINAL ==========================

    analysis_message = ""
    if not main_collection["found"]:
        analysis_message = (
            "No se detectó una lista principal de items. "
            "Puede ser un objeto único o estar muy anidado. "
            "Si el dataset sí tiene items, revisa la ruta o prueba otra URL."
        )

    return {
        "format": detected_format,
        "root_type": root_type,
        "message": analysis_message,
        "main_collection": main_collection,
        "keys": {"all": all_keys, "top": top_keys_only[:40]},
    }