from __future__ import annotations                  # Usar todo como strings
import json                                         # Payloads para parsear JSON
import xmltodict                                    # Para poder parsear los XML
from defusedxml import ElementTree as DefusedET     # Validacion de seguridad para XML


# ========================== DETECCION Y PARSEO ==========================

# Detecta el formato del texto (json/xml/unknown)
def detect_format(raw_text: str) -> str:
    trimmed = raw_text.lstrip()
    if trimmed.startswith("{") or trimmed.startswith("["):
        # Puede ser GeoJSON — lo comprobamos antes de declararlo JSON genérico
        try:
            maybe = json.loads(trimmed[:500])  # solo el inicio para ser rápidos
            if isinstance(maybe, dict) and maybe.get("type") == "FeatureCollection":
                return "geojson"
        except Exception:
            pass
        return "json"
    if trimmed.startswith("<"):
        return "xml"
    # CSV: si la primera línea tiene comas o puntos y coma, lo tratamos como CSV
    first_line = trimmed.split("\n")[0]
    if "," in first_line or ";" in first_line:
        return "csv"
    return "unknown"


def _parse_csv(raw_text: str) -> list[dict]:
    import csv, io
    sample = raw_text[:2000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
    except csv.Error:
        dialect = csv.excel  # fallback al dialecto estándar con comas
    reader = csv.DictReader(io.StringIO(raw_text), dialect=dialect)
    rows = []
    for i, row in enumerate(reader):
        if i >= 2000:
            break
        rows.append(dict(row))
    return rows

# No hay parse json ni xml pq es facil con las librerias que tenemos
# Convertirmos csv y geojson a list[dict], asi tiene el mismo formato que un json
def _parse_geojson(raw_text: str) -> list[dict]:
    data = json.loads(raw_text)
    features = data.get("features", [])
    result = []
    for feature in features:
        if not isinstance(feature, dict):
            continue
        props = feature.get("properties") or {}
        # Añadimos geometry_type por si es útil como campo
        geometry = feature.get("geometry") or {}
        props["_geometry_type"] = geometry.get("type", "")
        result.append(props)
    return result

# Parsea el rawx_text (crudo) y devuelve (formato, estructura_parseada)
def parse_raw(raw_text: str) -> tuple[str, object]:
    detected_format = detect_format(raw_text)
    if detected_format == "json":
        return "json", json.loads(raw_text)
    if detected_format == "xml":
        DefusedET.fromstring(raw_text.encode("utf-8"))
        return "xml", xmltodict.parse(raw_text)
    if detected_format == "csv":
        return "csv", _parse_csv(raw_text)
    if detected_format == "geojson":
        return "geojson", _parse_geojson(raw_text)
    raise ValueError("Formato no reconocido. Soportados: JSON, XML, CSV, GeoJSON.")


# ========================== RESUMEN PARA RESPONSE_SUMMARY ==========================

# Crea resumen de lo parseado para response_summary (models)
def summarize_data(fmt: str, parsed: object) -> str:
    if fmt == "csv":
        if isinstance(parsed, list):
            cols = list(parsed[0].keys()) if parsed else []
            return f"CSV con {len(parsed)} filas y {len(cols)} columnas: {', '.join(cols[:8])}{'...' if len(cols) > 8 else ''}."
        return "CSV parseado."

    if fmt == "geojson":
        if isinstance(parsed, list):
            sample_keys = [k for k in (parsed[0].keys() if parsed else []) if not k.startswith("_")]
            return f"GeoJSON con {len(parsed)} features. Propiedades: {', '.join(list(sample_keys)[:8])}{'...' if len(sample_keys) > 8 else ''}."
        return "GeoJSON parseado."

    #if isinstance(parsed, dict):
    #    return f"Formato detectado: {fmt}. Raíz: dict. Claves raíz: {len(parsed.keys())}."

    #if isinstance(parsed, list):
    #    return f"Formato detectado: {fmt}. Raíz: list. Elementos: {len(parsed)}."

    #return f"Formato detectado: {fmt}. Raíz: {type(parsed).__name__}."

    if isinstance(parsed, dict):
        return f"Formato: {fmt}."

    if isinstance(parsed, list):
        return f"Formato: {fmt}."

    return f"Formato: {fmt}."