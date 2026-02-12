# Permite usar anotaciones de tipos como strings
from __future__ import annotations

from typing import Any
import re
import json

from .analysis import get_by_path


def _truncate(text: str, max_len: int = 600) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _to_text(value: Any, *, max_len: int = 600) -> str:
    """Convierte valores a texto de forma estable y "amigable" para UI."""
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


def _get_nested(item: Any, key: str) -> Any:
    """
    ✨ MEJORADO: Obtiene un valor por key con soporte de paths complejos.
    
    Soporta:
    - Keys simples: "title"
    - Paths con punto: "user.name"
    - Paths con arrays: "images[0]", "data.items[1].url"
    - Paths mixtos: "user.posts[0].comments[2].text"
    
    Ejemplos:
        _get_nested({"user": {"name": "Ana"}}, "user.name") → "Ana"
        _get_nested({"images": ["a.jpg", "b.jpg"]}, "images[0]") → "a.jpg"
        _get_nested({"data": {"items": [{"id": 1}]}}, "data.items[0].id") → 1
    """
    if not key:
        return None
    if not isinstance(item, dict):
        return None
    
    # Si no tiene caracteres especiales, acceso directo
    if "." not in key and "[" not in key:
        return item.get(key)
    
    # Parsear el path completo: "user.posts[0].title" → ["user", "posts", "[0]", "title"]
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


def _looks_like_url(text: str) -> bool:
    """
    ✨ MEJORADO: Detecta si un texto parece una URL (absoluta o relativa).
    
    Soporta:
    - URLs absolutas: http://..., https://...
    - URLs relativas: /images/photo.jpg, ./assets/img.png
    """
    t = (text or "").strip()
    
    # URLs absolutas
    if t.startswith("http://") or t.startswith("https://"):
        return True
    
    # URLs relativas comunes
    if t.startswith("/") or t.startswith("./") or t.startswith("../"):
        # Verificar que no sea solo "/" (raíz vacía)
        if len(t) > 1:
            return True
    
    return False


def _pick_text(item: dict, keys: list[str], *, max_len: int = 600, strict_mode: bool = False) -> str:
    """
    Selecciona el primer valor no vacío de una lista de keys candidatas.
    
    Args:
        item: Dict del que extraer el valor
        keys: Lista de keys candidatas (en orden de prioridad)
        max_len: Longitud máxima del texto
        strict_mode: Si True, solo usa la PRIMERA key (no hace fallbacks)
    """
    # ✨ NUEVO: En modo estricto, solo intentamos la primera key
    if strict_mode:
        keys = keys[:1] if keys else []
    
    for k in keys:
        v = _get_nested(item, k)
        txt = _to_text(v, max_len=max_len)
        if txt:
            return txt
    return ""


def _pick_url(item: dict, keys: list[str], strict_mode: bool = False) -> str:
    """
    Selecciona la primera URL válida de una lista de keys candidatas.
    
    Args:
        item: Dict del que extraer la URL
        keys: Lista de keys candidatas (en orden de prioridad)
        strict_mode: Si True, solo usa la PRIMERA key (no hace fallbacks)
    """
    # ✨ NUEVO: En modo estricto, solo intentamos la primera key
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


def _extract_main_items(parsed_data: Any, analysis_result: dict) -> list[dict]:
    collection_path = analysis_result.get("main_collection", {}).get("path")
    if collection_path is None:
        return []
    node = get_by_path(parsed_data, collection_path)
    if not isinstance(node, list):
        return []
    return [x for x in node if isinstance(x, dict)]


def normalize_items(
    parsed_data: Any,
    analysis_result: dict,
    field_mapping: dict,
    limit: int = 20,
    strict_mode: bool = False,
) -> list[dict]:
    """
    Normaliza items para poder renderizar cards genéricas.

    Args:
        parsed_data: Datos parseados de la API
        analysis_result: Resultado del análisis
        field_mapping: Mapping configurado por el usuario
        limit: Número máximo de items a procesar
        strict_mode: ✨ NUEVO - Si True, NO usa fallbacks automáticos (solo el mapping del usuario)

    Salida estándar:
      - title, description, image, link, raw, mapping_info
    """
    raw_items = _extract_main_items(parsed_data, analysis_result)
    normalized: list[dict] = []

    for idx, item in enumerate(raw_items[:limit], start=1):
        # Keys seleccionadas en wizard (si existen)
        title_key = (field_mapping or {}).get("title", "") or ""
        description_key = (field_mapping or {}).get("description", "") or ""
        image_key = (field_mapping or {}).get("image", "") or ""
        link_key = (field_mapping or {}).get("link", "") or ""

        # ✨ NUEVO: En modo estricto, SOLO usa las keys del mapping (sin fallbacks)
        # En modo normal: usa fallbacks si el mapping está vacío
        if strict_mode:
            # Solo usar lo que el usuario mapeó explícitamente
            title_candidates = [title_key] if title_key else []
            desc_candidates = [description_key] if description_key else []
            image_candidates = [image_key] if image_key else []
            link_candidates = [link_key] if link_key else []
        else:
            # Fallbacks "con sentido" (incluso si mapping está incompleto)
            title_candidates = [k for k in [title_key, "title", "name", "headline", "label"] if k]
            desc_candidates = [k for k in [description_key, "description", "summary", "content", "text", "body", "excerpt"] if k]
            image_candidates = [k for k in [image_key, "image", "image_url", "thumbnail", "thumbnail_url", "thumb", "media.url", "media.image"] if k]
            link_candidates = [k for k in [link_key, "link", "url", "href", "permalink", "web_url"] if k]

        title = _pick_text(item, title_candidates, max_len=140, strict_mode=strict_mode)
        description = _pick_text(item, desc_candidates, max_len=520, strict_mode=strict_mode)
        image = _pick_url(item, image_candidates, strict_mode=strict_mode)
        link = _pick_url(item, link_candidates, strict_mode=strict_mode)

        # Si aún no hay title, inventa uno estable
        if not title:
            # intenta id como fallback antes de Item #
            id_txt = _pick_text(item, ["id", "uuid", "identifier"], max_len=80)
            title = id_txt if id_txt else f"Item #{idx}"

        # Construir información del mapping para mostrar en la card
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
