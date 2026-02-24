"""
Planner — genera un schema dinámico a partir de un dataset JSON/XML.

Nuevo contrato (schema dinámico):
  {
    "site_type": "blog | portfolio | catalog | dashboard | other",
    "site_title": "Nombre descriptivo del sitio",
    "fields": [
      { "key": "<key exacta de available_keys>", "label": "Etiqueta legible" },
      ...
    ]
  }

Reglas anti-alucinación:
  - Cada "key" en fields DEBE estar en available_keys.
  - Cualquier key no presente se descarta silenciosamente en backend.
  - El LLM elige libremente cuántos campos incluir y en qué orden.
  - No hay roles fijos (title/content/image/date).
"""

from __future__ import annotations

import json
import re
from typing import Any

from .client import chat_completion, LLMError


ALLOWED_SITE_TYPES = ("blog", "portfolio", "catalog", "dashboard", "other")

# Tokens que el LLM confunde a veces con keys reales
BANNED_KEY_TOKENS = {
    "main_collection_path", "available_keys", "examples", "keys", "path",
    "item", "dataset", "collection", "mapping", "pages", "site_type",
    "site_title", "fields", "key", "label",
}


class PlanError(Exception):
    """Error irrecuperable generando/parseando el plan."""


# ─────────────────────────── helpers JSON ────────────────────────────

def _safe_dumps(obj: Any, *, indent: int | None = None) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=indent)
    except Exception:
        return str(obj)


def _strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _extract_json_object(text: str) -> str:
    t = _strip_code_fences(text)
    if t.startswith("{") and t.endswith("}"):
        return t
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise PlanError("No se encontró un objeto JSON en la respuesta del LLM.")
    return t[start: end + 1]


def _repair_common_json(text: str) -> str:
    t = text.strip()
    t = re.sub(r",\s*([}\]])", r"\1", t)
    t = t.replace(": True", ": true").replace(": False", ": false").replace(": None", ": null")
    if "'" in t and '"' not in t:
        t = t.replace("'", '"')
    return t


# ─────────────────────────── normalización ───────────────────────────

def _normalize_site_type(raw: Any) -> str:
    s = (raw or "").strip().lower() if isinstance(raw, str) else ""
    if "dash" in s:
        return "dashboard"
    if "port" in s:
        return "portfolio"
    if "cata" in s or "shop" in s or "store" in s:
        return "catalog"
    if "blog" in s or "news" in s or "post" in s:
        return "blog"
    return s if s in ALLOWED_SITE_TYPES else "other"


def _looks_like_value_not_key(s: str) -> bool:
    """Detecta cuando el modelo metió un valor en vez de un nombre de clave."""
    if not s:
        return True
    if len(s) > 60 and " " in s:
        return True
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", s):
        return True
    if re.search(r"\.(jpg|jpeg|png|gif|webp|svg)\b", s, re.IGNORECASE):
        return True
    if s.strip().lower() in {"null", "none", "n/a", "na", "undefined"}:
        return True
    if s.startswith("http://") or s.startswith("https://"):
        return True
    return False


def _validate_and_normalize_schema(raw: Any, *, available_keys: list[str]) -> dict:
    """
    Devuelve SIEMPRE un schema válido:
      - site_type normalizado al enum.
      - site_title string limpio.
      - fields: lista de {key, label} con keys validadas contra available_keys.
        Cualquier key no presente se descarta silenciosamente.
    """
    if not isinstance(raw, dict):
        raw = {}

    site_type = _normalize_site_type(raw.get("site_type"))
    site_title = str(raw.get("site_title") or site_type).strip()[:120]
    if not site_title:
        site_title = site_type

    raw_fields = raw.get("fields")
    if not isinstance(raw_fields, list):
        raw_fields = []

    available_set = set(available_keys)
    seen_keys: set[str] = set()
    validated_fields: list[dict] = []

    for entry in raw_fields:
        if not isinstance(entry, dict):
            continue

        key = entry.get("key")
        if not isinstance(key, str):
            continue

        key = key.strip()

        # Rechazar tokens del contexto
        if key.lower() in BANNED_KEY_TOKENS:
            continue

        # Rechazar si parece un valor, no una clave
        if _looks_like_value_not_key(key):
            continue

        # Anti-alucinación: DEBE estar en available_keys
        if key not in available_set:
            # Intento case-insensitive como última gracia
            matched = next((k for k in available_keys if k.lower() == key.lower()), None)
            if not matched:
                continue  # descartado definitivamente
            key = matched

        # Evitar duplicados
        if key in seen_keys:
            continue
        seen_keys.add(key)

        label = str(entry.get("label") or key).strip()[:80]
        if not label:
            label = key

        validated_fields.append({"key": key, "label": label})

    # Fallback: si el LLM no dio ningún campo válido, usar todas las keys
    if not validated_fields:
        for k in available_keys[:12]:
            validated_fields.append({"key": k, "label": k})

    return {
        "site_type": site_type,
        "site_title": site_title,
        "fields": validated_fields,
    }


# ─────────────────────────── prompt ──────────────────────────────────

def _build_prompt(
    *,
    user_prompt: str,
    available_keys: list[str],
    examples: list[dict],
    main_collection_path: list | None,
    retry_hint: str | None = None,
) -> tuple[str, str]:

    system = (
        "Eres un planificador ESTRICTO para una app que genera sitios web a partir de datasets JSON/XML. "
        "Tu respuesta DEBE ser SOLO un único objeto JSON válido. "
        "NO uses Markdown. NO uses texto extra. NO uses bloques ```. "
        "SOLO devuelve el JSON."
    )

    contract = {
        "site_type": "blog | portfolio | catalog | dashboard | other",
        "site_title": "Nombre descriptivo del sitio (string)",
        "fields": [
            {"key": "<key exacta de available_keys>", "label": "Etiqueta legible para el usuario"},
            {"key": "...", "label": "..."},
        ],
    }

    rules = [
        "Devuelve SOLO un objeto JSON válido. Sin texto extra. Sin Markdown. Sin ```.",
        "site_type: elige el más adecuado según el dataset y el objetivo del usuario.",
        "  - lista de productos/plantas/libros → catalog",
        "  - entradas con fecha/texto largo → blog",
        "  - proyectos/personas/trabajos → portfolio",
        "  - métricas/estadísticas → dashboard",
        "  - si no encaja → other",
        "site_title: nombre corto y descriptivo para el sitio (máx 80 chars).",
        "fields: lista ORDENADA de campos que el sitio debe mostrar.",
        "  - Incluye TODOS los campos relevantes del dataset.",
        "  - El orden importa: pon primero los más importantes visualmente.",
        "  - 'key' DEBE ser exactamente una de las strings de available_keys. NADA más.",
        "  - 'label' es la etiqueta legible que verá el usuario (en el idioma apropiado).",
        "PROHIBIDO en 'key': valores del dataset, rutas, texto inventado, palabras del contexto.",
        "PROHIBIDO usar como key: main_collection_path, available_keys, examples, fields, key, label.",
        "Si una key no existe en available_keys → NO la incluyas.",
        "Ejemplo CORRECTO:   {\"key\": \"COMMON\", \"label\": \"Nombre\"} (si 'COMMON' está en available_keys).",
        "Ejemplo INCORRECTO: {\"key\": \"Bloodroot\", \"label\": \"Planta\"} → 'Bloodroot' es un VALOR, no una key.",
        "Ejemplo INCORRECTO: {\"key\": \"price_usd\", \"label\": \"Precio\"} → solo si 'price_usd' está en available_keys.",
    ]

    user_parts = [
        "OBJETIVO_USUARIO (texto libre):",
        user_prompt.strip() or "(sin prompt: decide tú lo mejor según el dataset)",
        "",
        "CONTRATO_JSON (devuelve exactamente esta estructura):",
        _safe_dumps(contract, indent=2),
        "",
        "REGLAS OBLIGATORIAS:",
        "\n".join(f"- {r}" for r in rules),
        "",
        f"main_collection_path (solo contexto, NO es una key válida): {main_collection_path}",
        "",
        "available_keys (SOLO estas strings son válidas para el campo 'key' en fields):",
        _safe_dumps(available_keys),
        "",
        "examples (1-3 items del dataset, para entender qué valores contiene cada key):",
        _safe_dumps(examples, indent=2),
    ]

    if retry_hint:
        user_parts.extend([
            "",
            "CORRECCIÓN (tu respuesta anterior fue inválida):",
            retry_hint,
            "",
            "Devuelve SOLO el JSON corregido, sin texto adicional.",
        ])

    return system, "\n".join(user_parts)


# ─────────────────────────── función pública ─────────────────────────

def generate_site_plan(
    *,
    user_prompt: str,
    available_keys: list[str],
    examples: list[dict],
    main_collection_path: list | None,
    retries: int = 1,
) -> dict:
    """
    Genera y devuelve un schema dinámico validado:
      {
        "site_type": str,
        "site_title": str,
        "fields": [{"key": str, "label": str}, ...]
      }

    Nunca lanza excepción: si el LLM falla, devuelve fallback con todas las keys.
    """
    last_error: str | None = None

    for attempt in range(retries + 1):
        system_text, user_text = _build_prompt(
            user_prompt=user_prompt,
            available_keys=available_keys,
            examples=examples,
            main_collection_path=main_collection_path,
            retry_hint=last_error,
        )

        try:
            raw = chat_completion(user_text=user_text, system_text=system_text, temperature=0.0)
        except LLMError:
            return _validate_and_normalize_schema({}, available_keys=available_keys)

        try:
            json_text = _extract_json_object(raw)
            try:
                parsed = json.loads(json_text)
            except json.JSONDecodeError:
                parsed = json.loads(_repair_common_json(json_text))

            return _validate_and_normalize_schema(parsed, available_keys=available_keys)

        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}. Respuesta cruda: {raw[:600]}"
            if attempt >= retries:
                return _validate_and_normalize_schema({}, available_keys=available_keys)

    return _validate_and_normalize_schema({}, available_keys=available_keys)
