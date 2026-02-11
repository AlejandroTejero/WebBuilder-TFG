# Permite usar anotaciones de tipos como strings
from __future__ import annotations

from typing import Any

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
    """Obtiene un valor por key. Soporta paths tipo 'a.b.c'."""
    if not key:
        return None
    if not isinstance(item, dict):
        return None
    # Soporta dotted paths
    if "." in key:
        node: Any = item
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node.get(part)
            else:
                return None
        return node
    return item.get(key)


def _looks_like_url(text: str) -> bool:
    t = (text or "").strip()
    return t.startswith("http://") or t.startswith("https://")


def _pick_text(item: dict, keys: list[str], *, max_len: int = 600) -> str:
    for k in keys:
        v = _get_nested(item, k)
        txt = _to_text(v, max_len=max_len)
        if txt:
            return txt
    return ""


def _pick_url(item: dict, keys: list[str]) -> str:
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
) -> list[dict]:
    """Normaliza items para poder renderizar cards genéricas.

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

        # Fallbacks "con sentido" (incluso si mapping está incompleto)
        title_candidates = [k for k in [title_key, "title", "name", "headline", "label"] if k]
        desc_candidates = [k for k in [description_key, "description", "summary", "content", "text", "body", "excerpt"] if k]
        image_candidates = [k for k in [image_key, "image", "image_url", "thumbnail", "thumbnail_url", "thumb", "media.url", "media.image"] if k]
        link_candidates = [k for k in [link_key, "link", "url", "href", "permalink", "web_url"] if k]

        title = _pick_text(item, title_candidates, max_len=140)
        description = _pick_text(item, desc_candidates, max_len=520)
        image = _pick_url(item, image_candidates)
        link = _pick_url(item, link_candidates)

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
