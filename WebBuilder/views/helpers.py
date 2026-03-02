"""
view_helpers.py — Utilidades compartidas entre edit.py y render.py.

Contiene:
  - _to_text: convierte cualquier valor a string truncado.
  - _get_fields_from_plan: extrae la lista de fields de un plan.
  - _normalize_item: convierte un item del dataset en un dict plano con las keys del schema.
"""

from __future__ import annotations

import json
from typing import Any


def _to_text(value: Any, *, max_len: int = 180) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, str):
        s = value.strip()
    else:
        try:
            s = json.dumps(value, ensure_ascii=False)
        except Exception:
            s = str(value)
    return s if len(s) <= max_len else s[: max_len - 3] + "..."


def _get_fields_from_plan(plan: Any) -> list[dict]:
    if not isinstance(plan, dict):
        return []
    return plan.get("fields") or []


def _normalize_item(raw_item: Any, fields: list[dict], *, index: int, max_len: int = 180) -> dict:
    """
    Convierte un item del dataset en un dict plano con las keys del schema.
    Cada campo del schema se convierte en item[key] = valor (truncado).
    Siempre se incluye 'index'.
    """
    result: dict[str, Any] = {"index": index}
    if not isinstance(raw_item, dict):
        return result
    for field in fields:
        key = field["key"]
        result[key] = _to_text(raw_item.get(key), max_len=max_len)
    return result
