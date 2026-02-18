from __future__ import annotations
from ..parsers import detect_format
from .constants import ROLE_DEFS
from .helpers import get_by_path, _path_display
from .detection import find_main_items
from .suggestions import suggest_mapping_smart

"""
Construye el dict final de análisis para UI

Pasos del analisis:
1. Detecta el formato del raw_text
2. Determina el tipo de la raíz
3. Encuentra la colección principal de items
4. Calcula sugerencias de mapping
5. Construye un dict consolidado para el frontend

Args:
1. parsed_data: Datos parseados (dict, list, etc.)
2. raw_text: Texto crudo original (opcional, para detectar formato)
"""

def build_analysis(parsed_data: object, raw_text: str | None = None) -> dict:

    # ========================== 1) METADATA PAYLOAD ==========================

    # Intenta detectar formato si tenemos raw_text
    detected_format = detect_format(raw_text) if raw_text else "unknown"

    # Determina el tipo raíz del payload parseado
    if isinstance(parsed_data, dict):
        root_type = "dict"
    elif isinstance(parsed_data, list):
        root_type = "list"
    else:
        root_type = type(parsed_data).__name__

    # ========================== 2) COLECCION PRINCIPAL ==========================

    # Encuentra la colección principal de items
    main = find_main_items(parsed_data)

    # Construye resumen de colección principal
    main_collection = {
        "found": bool(main.get("found")),
        "path": main.get("path"),
        "count": int(main.get("count", 0) or 0),
        "top_keys": main.get("top_keys", []),
        "sample_keys": main.get("sample_keys", []),
        "path_display": _path_display(main.get("path")),
    }

    # ========================== 3) KEYS DISPONIBLES ==========================

    # Lista solo de keys top
    top_keys_only = [k for (k, _) in main_collection["top_keys"]] if main_collection["top_keys"] else []

    # Acumula keys "all" combinando sample + top sin duplicados
    all_keys: list[str] = []

    # Añade sample_keys primero
    for key in main_collection["sample_keys"]:
        if key not in all_keys:
            all_keys.append(key)

    # Añade top_keys después
    for key in top_keys_only:
        if key not in all_keys:
            all_keys.append(key)

    # ========================== 4) ITEMS + SUGERENCIAS ==========================

    items_list = []

    # Si hay colección encontrada y path válido, extrae items por path
    if main_collection["found"] and main_collection["path"] is not None:
        items_list = get_by_path(parsed_data, main_collection["path"]) or []

    # Calcula sugerencias si items_list es lista
    if isinstance(items_list, list):
        suggestions = suggest_mapping_smart(items_list, ROLE_DEFS)
    else:
        suggestions = {role: [] for role in ROLE_DEFS.keys()}

    # ========================== 5) MENSAJE + OUTPUT FINAL ==========================

    analysis_message = ""
    if not main_collection["found"]:
        analysis_message = (
            "No se detectó una lista principal de items. "
            "Puede ser un objeto único o estar muy anidado. "
            "Si el dataset sí tiene items, revisa la ruta o prueba otra URL."
        )

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
