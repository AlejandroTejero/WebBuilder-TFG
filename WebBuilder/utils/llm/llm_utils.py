"""
llm_utils.py — Utilidades compartidas para los módulos LLM (planner y themer).

Contiene:
  - Helpers para parseo y reparación de JSON generado por el LLM.
  - Solo utilidades genéricas de texto/JSON.
"""

from __future__ import annotations

import json
import re
from typing import Any


# ─────────────────────────── helpers JSON ────────────────────────────

def strip_code_fences(text: str) -> str:
    """Elimina bloques de código Markdown (``` o ```json) que el LLM añade a veces."""
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def extract_json_object(text: str, exc_class: type[Exception] = ValueError) -> str:
    """
    Extrae el primer objeto JSON {...} de un texto libre.
    Lanza exc_class si no se encuentra ninguno.
    """
    t = strip_code_fences(text)
    if t.startswith("{") and t.endswith("}"):
        return t
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise exc_class("No se encontró un objeto JSON en la respuesta del LLM.")
    return t[start: end + 1]


def repair_common_json(text: str) -> str:
    """
    Intenta reparar JSON malformado con errores comunes del LLM:
      - Comas finales antes de } o ]
      - Literales Python True/False/None en vez de true/false/null
      - Comillas simples en vez de dobles (solo si no hay comillas dobles)
    """
    t = text.strip()
    t = re.sub(r",\s*([}\]])", r"\1", t)
    t = t.replace(": True", ": true").replace(": False", ": false").replace(": None", ": null")
    if "'" in t and '"' not in t:
        t = t.replace("'", '"')
    return t


def safe_dumps(obj: Any, *, indent: int | None = None) -> str:
    """json.dumps seguro: nunca lanza, devuelve str(obj) como fallback."""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=indent)
    except Exception:
        return str(obj)


def parse_llm_json(raw: str, exc_class: type[Exception] = ValueError) -> dict:
    """
    Parsea la respuesta cruda del LLM a un dict JSON.
    Intenta reparar el JSON si el primer parse falla.
    Lanza exc_class si no es posible parsearlo.
    """
    json_text = extract_json_object(raw, exc_class=exc_class)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return json.loads(repair_common_json(json_text))
