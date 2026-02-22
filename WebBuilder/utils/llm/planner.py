from __future__ import annotations

import json
import re
from typing import Any, Optional

from django.utils.text import slugify

from .client import chat_completion, LLMError


ALLOWED_SITE_TYPES = ("blog", "portfolio", "catalog", "dashboard", "other")
MAPPING_FIELDS = ("title", "content", "image", "date")

# Palabras que el modelo a veces "confunde" como keys
BANNED_MAPPING_TOKENS = {
    "main_collection_path",
    "available_keys",
    "examples",
    "keys",
    "path",
    "item",
    "dataset",
    "collection",
    "mapping",
    "pages",
    "site_type",
}


class PlanError(Exception):
    """Error generando/parseando el plan (solo para fallos graves de parseo)."""


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
    """
    Extrae el primer objeto JSON { ... } aunque haya texto alrededor.
    """
    t = _strip_code_fences(text)
    if t.startswith("{") and t.endswith("}"):
        return t

    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise PlanError("No se encontró un objeto JSON en la respuesta del LLM.")
    return t[start : end + 1]


def _repair_common_json(text: str) -> str:
    """
    Reparaciones ligeras para JSON comúnmente roto:
    - comillas simples -> dobles (solo si parece dict simple)
    - trailing commas
    - True/False/None -> true/false/null
    """
    t = text.strip()

    # trailing commas antes de } o ]
    t = re.sub(r",\s*([}\]])", r"\1", t)

    # pythonisms
    t = t.replace(": True", ": true").replace(": False", ": false").replace(": None", ": null")

    # si usa comillas simples en claves/strings (heurística simple)
    if "'" in t and '"' not in t:
        t = t.replace("'", '"')

    return t


def _normalize_site_type(raw: Any) -> str:
    if isinstance(raw, str):
        s = raw.strip().lower()
    else:
        s = ""

    # Mapeos tolerantes
    if "dash" in s:
        return "dashboard"
    if "port" in s:
        return "portfolio"
    if "cata" in s or "shop" in s or "store" in s:
        return "catalog"
    if "blog" in s or "news" in s or "post" in s:
        return "blog"

    return s if s in ALLOWED_SITE_TYPES else "other"


def _clean_pages(pages: Any, site_type: str) -> list[str]:
    if not isinstance(pages, list):
        pages = []

    out: list[str] = []
    seen: set[str] = set()

    for p in pages:
        if not isinstance(p, str):
            continue
        slug = slugify(p.strip())
        if not slug:
            continue
        if slug not in seen:
            out.append(slug)
            seen.add(slug)

    # defaults por tipo
    if not out:
        if site_type == "catalog":
            out = ["home", "catalog", "item"]
        elif site_type == "portfolio":
            out = ["home", "projects", "project"]
        elif site_type == "blog":
            out = ["home", "posts", "post"]
        elif site_type == "dashboard":
            out = ["home", "dashboard"]
        else:
            out = ["home", "detail"]

    return out[:12]


def _case_insensitive_key_match(value: str, available_keys: list[str]) -> Optional[str]:
    v = value.strip()
    if not v:
        return None
    # match exact
    if v in available_keys:
        return v
    # case-insensitive
    low = v.lower()
    for k in available_keys:
        if k.lower() == low:
            return k
    # trim spaces common mistakes
    v2 = re.sub(r"\s+", " ", v)
    if v2 in available_keys:
        return v2
    for k in available_keys:
        if k.lower() == v2.lower():
            return k
    return None


def _looks_like_value_not_key(s: str) -> bool:
    """
    Heurísticas para detectar cuando el modelo metió un valor (frase/fecha/archivo) en vez de un nombre de clave.
    """
    if not s:
        return True
    if len(s) > 40 and " " in s:
        return True  # frase larga
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", s):
        return True  # fecha literal
    if re.search(r"\.(jpg|jpeg|png|gif|webp|svg)\b", s, re.IGNORECASE):
        return True  # filename
    if s.strip().lower() in {"null", "none", "n/a", "na", "undefined"}:
        return True
    return False


def _choose_key_by_hint(available_keys: list[str], field: str) -> Optional[str]:
    """
    Fallback heurístico: elige una key adecuada si el LLM no dio una válida.
    """
    if not available_keys:
        return None

    patterns = {
        "title": r"(title|name|common|label|headline)",
        "content": r"(desc|description|summary|content|text|body|notes|detail|about)",
        "image": r"(image|img|photo|picture|thumb|thumbnail|avatar|icon|url|link)",
        "date": r"(date|time|created|updated|published|timestamp)",
    }
    pat = re.compile(patterns.get(field, r"$^"), re.IGNORECASE)

    # 1) match por patrón
    for k in available_keys:
        if pat.search(k):
            return k

    # 2) por orden: title -> primera, content -> segunda/tercera, etc.
    if field == "title":
        return available_keys[0]
    if field == "content":
        return available_keys[1] if len(available_keys) > 1 else available_keys[0]
    return None


def _validate_and_normalize_plan(plan: Any, *, available_keys: list[str]) -> dict:
    """
    Devuelve SIEMPRE un plan válido con el contrato.
    Repara:
      - site_type fuera de lista -> 'other' o mapeo
      - pages inválidas -> defaults
      - mapping inválido -> null o match por case-insensitive o heurística
    """
    if not isinstance(plan, dict):
        plan = {}

    site_type = _normalize_site_type(plan.get("site_type"))
    pages = _clean_pages(plan.get("pages"), site_type)

    mapping_raw = plan.get("mapping")
    if not isinstance(mapping_raw, dict):
        mapping_raw = {}

    normalized_mapping: dict[str, str | None] = {}

    for field in MAPPING_FIELDS:
        v = mapping_raw.get(field, None)

        # normaliza string "null" -> None
        if isinstance(v, str) and v.strip().lower() in {"null", "none", "n/a", "na", "undefined", ""}:
            v = None

        if v is None:
            # fallback heurístico (opcional): si quieres más conservador, comenta estas 2 líneas
            chosen = _choose_key_by_hint(available_keys, field)
            normalized_mapping[field] = chosen if chosen in (available_keys or []) else None
            continue

        if not isinstance(v, str):
            normalized_mapping[field] = None
            continue

        vv = v.strip()

        # No permitir tokens del contexto
        if vv.lower() in BANNED_MAPPING_TOKENS:
            normalized_mapping[field] = None
            continue

        # Si parece valor (frase/fecha/archivo), lo anulamos
        if _looks_like_value_not_key(vv):
            normalized_mapping[field] = None
            continue

        # Debe ser una key exacta (con tolerancia case-insensitive)
        matched = _case_insensitive_key_match(vv, available_keys)
        if matched:
            normalized_mapping[field] = matched
        else:
            # fallback heurístico si no coincide
            chosen = _choose_key_by_hint(available_keys, field)
            normalized_mapping[field] = chosen if chosen in (available_keys or []) else None

    return {
        "site_type": site_type,
        "pages": pages,
        "mapping": normalized_mapping,
    }


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
        "NO uses Markdown, NO uses texto extra, NO uses bloques ```."
        " NO describas diseño/estilos/colores. NO escribas marketing. SOLO devuelve el plan JSON."
    )

    contract = {
        "site_type": "blog | portfolio | catalog | dashboard | other",
        "pages": ["home", "..."],
        "mapping": {
            "title": "<key_name_or_null>",
            "content": "<key_name_or_null>",
            "image": "<key_name_or_null>",
            "date": "<key_name_or_null>",
        },
    }

    user_parts = [
        "OBJETIVO_USUARIO (texto libre):",
        user_prompt.strip() or "(sin prompt: decide tú lo mejor según el dataset)",
        "",
        "CONTRATO_JSON (forma exacta requerida):",
        _safe_dumps(contract, indent=2),
        "",
        "REGLAS IMPORTANTES (OBLIGATORIAS):",
        "- Devuelve SOLO un objeto JSON válido. Nada de texto extra. Nada de Markdown. Nada de ```.",
        "- Debes ELEGIR el site_type más adecuado según el dataset y el objetivo del usuario.",
        "- Guía site_type: lista de items/productos/plantas/libros -> catalog; entradas con fecha/texto largo -> blog; proyectos/personas -> portfolio; métricas/estadísticas -> dashboard; si duda -> other.",
        "- pages: elige 2-6 slugs coherentes con el site_type (ej: home, catalog, item, about, contact).",
        "- mapping SOLO puede contener NOMBRES DE CLAVES que estén EXACTAMENTE en available_keys, o null.",
        "- mapping NO puede contener: rutas, nombres de variables, paths, texto inventado, ni valores de ejemplo.",
        "- PROHIBIDO usar palabras del contexto como keys: main_collection_path, available_keys, examples, keys, path, item, dataset, collection.",
        '- Ejemplo correcto: "title": "COMMON" (si "COMMON" está en available_keys).',
        '- Ejemplo incorrecto: "title": "Bloodroot" (es un valor, no una key).',
        '- Ejemplo incorrecto: "title": "main_collection_path" (no es key del dataset).',
        '- Ejemplo incorrecto: "content": "Explore our plant collection" (texto inventado).',
        "- Si no hay una clave clara para un campo, usa null.",
        "- Para null, escribe null (sin comillas). NO uses \"null\".",
        "",
        f"main_collection_path (solo contexto, NO es una key): {main_collection_path}",
        "",
        "available_keys (USA SOLO estas strings exactas si quieres asignar mapping):",
        _safe_dumps(available_keys),
        "",
        "examples (1-3 items recortados, solo para entender el dataset):",
        _safe_dumps(examples, indent=2),
    ]

    if retry_hint:
        user_parts.extend(
            [
                "",
                "CORRECCIÓN (tu respuesta anterior fue inválida):",
                retry_hint,
                "",
                "Devuelve SOLO el JSON corregido, sin texto adicional.",
            ]
        )

    return system, "\n".join(user_parts)


def generate_site_plan(
    *,
    user_prompt: str,
    available_keys: list[str],
    examples: list[dict],
    main_collection_path: list | None,
    retries: int = 1,
) -> dict:
    """
    Genera y devuelve un plan con contrato fijo:
      - site_type
      - pages
      - mapping {title,content,image,date} (keys exactas o null)

    Robustez:
      - Intenta parsear JSON
      - Si falla, reintenta 1 vez con hint de error
      - Si el JSON viene “flojo”, normaliza/repara para que SIEMPRE salga un plan válido
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
            raw = chat_completion(
                user_text=user_text,
                system_text=system_text,
                temperature=0.0,
            )
        except LLMError as e:
            # si falla red, no bloqueamos: devolvemos plan fallback
            fallback = _validate_and_normalize_plan({}, available_keys=available_keys)
            return fallback

        try:
            json_text = _extract_json_object(raw)
            try:
                parsed = json.loads(json_text)
            except json.JSONDecodeError:
                parsed = json.loads(_repair_common_json(json_text))

            return _validate_and_normalize_plan(parsed, available_keys=available_keys)

        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}. Respuesta cruda: {raw[:600]}"
            if attempt >= retries:
                # Último recurso: plan fallback (no reventar la vista)
                fallback = _validate_and_normalize_plan({}, available_keys=available_keys)
                return fallback

    # No debería llegar aquí
    return _validate_and_normalize_plan({}, available_keys=available_keys)