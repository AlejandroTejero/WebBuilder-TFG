# Permite usar anotaciones de tipos como strings
from __future__ import annotations

# Importa json para parsear payloads JSON
import json

# Importa xmltodict para convertir XML a dict
import xmltodict
# Importa defusedxml para validar XML de forma segura
from defusedxml import ElementTree as DefusedET


# Detecta el formato del texto (json/xml/unknown)
def detect_format(raw_text: str) -> str:
    # Quita espacios iniciales para mirar el primer carácter real
    trimmed = raw_text.lstrip()
    # Si empieza por { o [, asumimos JSON
    if trimmed.startswith("{") or trimmed.startswith("["):
        # Devuelve formato JSON
        return "json"
    # Si empieza por <, asumimos XML
    if trimmed.startswith("<"):
        # Devuelve formato XML
        return "xml"
    # Si no cuadra, devolvemos unknown
    return "unknown"


# Parsea el texto crudo y devuelve (formato, estructura_parseada)
def parse_raw(raw_text: str) -> tuple[str, object]:
    # Detecta formato por heurística
    detected_format = detect_format(raw_text)

    # Si es JSON, parsea con json.loads
    if detected_format == "json":
        # Devuelve el formato y el objeto parseado
        return "json", json.loads(raw_text)

    # Si es XML, valida seguro y convierte a dict
    if detected_format == "xml":
        # Valida el XML para evitar ataques (XXE y similares)
        DefusedET.fromstring(raw_text.encode("utf-8"))
        # Convierte el XML a dict serializable
        return "xml", xmltodict.parse(raw_text)

    # Si no es JSON ni XML, lanza error
    raise ValueError("El contenido descargado no parece JSON ni XML válido.")


# Construye un resumen corto de lo parseado para guardarlo en response_summary
def summarize_data(fmt: str, parsed: object) -> str:
    # Si la raíz es dict, damos número de claves
    if isinstance(parsed, dict):
        # Devuelve resumen para dict
        return f"Formato detectado: {fmt}. Raíz: dict. Claves raíz: {len(parsed.keys())}."
    # Si la raíz es list, damos número de elementos
    if isinstance(parsed, list):
        # Devuelve resumen para list
        return f"Formato detectado: {fmt}. Raíz: list. Elementos: {len(parsed)}."
    # Para otros tipos, devolvemos el nombre del tipo
    return f"Formato detectado: {fmt}. Raíz: {type(parsed).__name__}."
