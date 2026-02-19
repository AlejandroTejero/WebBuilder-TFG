from __future__ import annotations                  # Usar todo como strings
import json                                         # Payloads para parsear JSON
import xmltodict                                    # Para poder parsear los XML
from defusedxml import ElementTree as DefusedET     # Validacion de seguridad para XML


# ========================== DETECCION Y PARSEO ==========================

# Detecta el formato del texto (json/xml/unknown)
def detect_format(raw_text: str) -> str:
    # Elimino si existe el espacio inicial
    trimmed = raw_text.lstrip()    
    if trimmed.startswith("{") or trimmed.startswith("["):
        return "json"
    if trimmed.startswith("<"):
        return "xml"
    return "unknown"


# Parsea el rawx_text (crudo) y devuelve (formato, estructura_parseada)
def parse_raw(raw_text: str) -> tuple[str, object]:
    detected_format = detect_format(raw_text)
    if detected_format == "json":
        return "json", json.loads(raw_text)
    if detected_format == "xml":
        # Valida el XML para evitar ataques
        DefusedET.fromstring(raw_text.encode("utf-8"))
        return "xml", xmltodict.parse(raw_text)

    raise ValueError("El contenido no parece JSON ni XML.")


# ========================== RESUMEN PARA RESPONSE_SUMMARY ==========================

# Crea resumen de lo parseado para response_summary (models)
def summarize_data(fmt: str, parsed: object) -> str:

    # Si es un dict (JSON), contamos numero de keys, no values
    if isinstance(parsed, dict):
        return f"Formato detectado: {fmt}. Raíz: dict. Claves raíz: {len(parsed.keys())}."

    # Si es una list, damos número de elementos
    if isinstance(parsed, list):
        return f"Formato detectado: {fmt}. Raíz: list. Elementos: {len(parsed)}."
    
    # Para otros tipos, devolvemos el nombre del tipo
    return f"Formato detectado: {fmt}. Raíz: {type(parsed).__name__}."