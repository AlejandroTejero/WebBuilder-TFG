from __future__ import annotations      # Usar todo como strings
from typing import Any                  # Para meter cualquier cosa en parsed_data (list,dict...)
import re                               # Parsear path
import json                             # Dict/List
from .analysis import get_by_path       # Navegar por paths


# ========================== FORMATEO A TEXTO ==========================

# Recortamos string a max_len para que reviente el preview
def _truncate(text: str, max_len: int = 600) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


# Convierte TODOS los valores a tipo str, para no trabajar con estructuras raras
def _to_text(value: Any, *, max_len: int = 600) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return _truncate(value, max_len=max_len)
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, (dict, list)):
        try:
            return _truncate(json.dumps(value, ensure_ascii=False, sort_keys=True), max_len=max_len)
        except Exception:
            return _truncate(str(value), max_len=max_len)
    return _truncate(str(value), max_len=max_len)



# ========================== ACCESO A CAMPOS (paths) ==========================

# Extrae los valores soportando todo tipo de estructuras 
# _get_nested({"user": {"name": "Ana"}}, "user.name") → "Ana"
# _get_nested({"images": ["a.jpg", "b.jpg"]}, "images[0]") → "a.jpg"
# _get_nested({"data": {"items": [{"id": 1}]}}, "data.items[0].id") → 1
def _get_nested(item: Any, key: str) -> Any:
    if not key:
        return None
    if not isinstance(item, dict):
        return None
    
    # Si no tiene caracteres especiales, acceso directo
    if "." not in key and "[" not in key:
        return item.get(key)
    
    # Regex que captura: palabras normales O índices con corchetes
    parts = re.findall(r'[^\.\[]+|\[\d+\]', key)
    
    node: Any = item
    for part in parts:
        # Si es un índice: [0], [1], etc.
        if part.startswith('[') and part.endswith(']'):
            try:
                index = int(part[1:-1])
            except (ValueError, IndexError):
                return None
                
            if not isinstance(node, list):
                return None
            if index < 0 or index >= len(node):
                return None
            node = node[index]
            
        # Si es una key normal
        else:
            if not isinstance(node, dict):
                return None
            if part not in node:
                return None
            node = node[part]
    
    return node



# ========================== VALIDACIONES ==========================

# Observa si un campo se parece a una URL (tipicamente son url o imagen)
def _looks_like_url(text: str) -> bool:
    t = (text or "").strip()
    
    # URLs absolutas
    if t.startswith("http://") or t.startswith("https://"):
        return True
    
    # URLs relativas comunes
    if t.startswith("/") or t.startswith("./") or t.startswith("../"):
        if len(t) > 1:
            return True
    
    return False



# ========================== SELECCIONADORES (pickers) ==========================

# Devuelve el primer valor no vacio de las keys candidatas
def _pick_text(item: dict, keys: list[str], *, max_len: int = 600, strict_mode: bool = False) -> str:
    if strict_mode:
        keys = keys[:1] if keys else []
    
    for k in keys:
        v = _get_nested(item, k)
        txt = _to_text(v, max_len=max_len)
        if txt:
            return txt
    return ""


# Selecciona la primera URL válida de una lista de keys candidatas.
def _pick_url(item: dict, keys: list[str], strict_mode: bool = False) -> str:
    if strict_mode:
        keys = keys[:1] if keys else []
    
    for k in keys:
        v = _get_nested(item, k)
        txt = _to_text(v, max_len=1200)
        if not txt:
            continue
        # Si viene con espacios, nos quedamos con el primer token
        candidate = txt.strip().split()[0]
        if _looks_like_url(candidate):
            return candidate
    return ""



# ========================== NORMALIZACION: API -> cards ==========================

# Busca la lista principal de items mirando el analisis de la coleccion principal 
def _extract_main_items(parsed_data: Any, analysis_result: dict) -> list[dict]:
    collection_path = analysis_result.get("main_collection", {}).get("path")
    
    # Si no conocemos el path devolvemos None
    if collection_path is None:
        return []
    
    # Navegamos por la ruta buscando la lista
    node = get_by_path(parsed_data, collection_path)
    if not isinstance(node, list):
        return []
    
    return [x for x in node if isinstance(x, dict)]


"""
Funcion: Normaliza los items para poder generar cards genericas
Args:
    parsed_data: Datos parseados de la API
    analysis_result: Resultado del análisis
    field_mapping: Mapping configurado por el usuario
    limit: Número máximo de items a procesar
    strict_mode: Si True, NO usa fallbacks automáticos (solo el mapping del usuario)
Salida estándar:
    title, description, image, link, raw, mapping_info
"""
def normalize_items(
    parsed_data: Any,
    analysis_result: dict,
    field_mapping: dict,
    limit: int = 20,
    strict_mode: bool = False,
) -> list[dict]:
    
    # Recogo los items y los meto en la lista final
    raw_items = _extract_main_items(parsed_data, analysis_result)
    normalized: list[dict] = []

    # Asigno las keys correspondientes a cada campo, si existen
    for idx, item in enumerate(raw_items[:limit], start=1):
        title_key = (field_mapping or {}).get("title", "") or ""
        description_key = (field_mapping or {}).get("description", "") or ""
        image_key = (field_mapping or {}).get("image", "") or ""
        link_key = (field_mapping or {}).get("link", "") or ""

        # En modo estricto, SOLO usa las keys del mapping (las q metio el user)
        # En modo normal: Sugerencias del mapping
        if strict_mode:
            title_candidates = [title_key] if title_key else []
            desc_candidates = [description_key] if description_key else []
            image_candidates = [image_key] if image_key else []
            link_candidates = [link_key] if link_key else []
        else:
            title_candidates = [k for k in [title_key, "title", "name", "headline", "label"] if k]
            desc_candidates = [k for k in [description_key, "description", "summary", "content", "text", "body", "excerpt"] if k]
            image_candidates = [k for k in [image_key, "image", "image_url", "thumbnail", "thumbnail_url", "thumb", "media.url", "media.image"] if k]
            link_candidates = [k for k in [link_key, "link", "url", "href", "permalink", "web_url"] if k]

        # Seleccion final de los campos
        title = _pick_text(item, title_candidates, max_len=140, strict_mode=strict_mode)
        description = _pick_text(item, desc_candidates, max_len=520, strict_mode=strict_mode)
        image = _pick_url(item, image_candidates, strict_mode=strict_mode)
        link = _pick_url(item, link_candidates, strict_mode=strict_mode)

        # Si aún no hay title, inventa uno estable
        if not title:
            id_txt = _pick_text(item, ["id", "uuid", "identifier"], max_len=80)
            title = id_txt if id_txt else f"Item #{idx}"

        # Construir info para mostrar en la card
        mapping_info = {}
        if title_key:
            mapping_info["title"] = title_key
        if description_key:
            mapping_info["description"] = description_key
        if image_key:
            mapping_info["image"] = image_key
        if link_key:
            mapping_info["link"] = link_key

        normalized.append(
            {
                "title": title,
                "description": description,
                "image": image,
                "link": link,
                "raw": item,
                "mapping_info": mapping_info if mapping_info else None,
            }
        )

    return normalized
