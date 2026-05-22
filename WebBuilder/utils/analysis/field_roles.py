from __future__ import annotations

"""
field_roles.py — Inferencia del ROL SEMÁNTICO de cada campo del dataset.

A diferencia de detection.py (que localiza la colección de items) y de
field_extractor.py (que lee nombres del models.py ya generado), este módulo
trabaja ANTES de generar nada: observa los valores de ejemplo y deduce qué
representa cada campo.

Roles posibles:
  - "numeric"   → valor numérico real (precio, capitalización, volumen, rank…),
                  incluso si la API lo entrega como string ("76753.69").
  - "percent"   → numérico que representa una variación/porcentaje (puede ser
                  negativo). Útil para badges de signo en dashboards.
  - "image"     → URL de imagen.
  - "url"       → URL no-imagen (enlace externo).
  - "date"      → fecha o datetime.
  - "boolean"   → booleano.
  - "long_text" → texto largo (descripciones, cuerpo…).
  - "title"     → texto corto que actúa como nombre/título del item.
  - "category"  → texto corto repetido entre items (tipo, estado, género…).
  - "text"      → texto corto sin rol más específico.

El resultado se usa para:
  - generar tipos Django correctos (FloatField / IntegerField / …),
  - elegir qué campo agregar en un dashboard,
  - saber cuál es la imagen y el título en catálogos y portfolios.
"""

import re
from typing import Any

# ── Patrones de nombre que refuerzan la inferencia ────────────────────────

_IMAGE_NAME_HINTS = ("image", "img", "thumbnail", "thumb", "photo", "picture", "avatar", "cover", "poster", "logo")
_PERCENT_NAME_HINTS = ("percent", "change", "pct", "growth", "delta", "variation", "ratio")
_DATE_NAME_HINTS = ("date", "_at", "time", "created", "updated", "published", "release", "fecha")
_TITLE_NAME_HINTS = ("name", "title", "headline", "label", "symbol", "nameid")
_CATEGORY_NAME_HINTS = ("type", "category", "categoria", "status", "estado", "genre", "género", "kind", "tag", "rank", "tier", "group", "class")
_IMAGE_EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|avif|bmp)(\?|$)", re.IGNORECASE)
_DATE_VALUE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2})?")
_NUMERIC_VALUE_RE = re.compile(r"^-?\d+(\.\d+)?$")
_INT_VALUE_RE = re.compile(r"^-?\d+$")


def _is_numeric_string(value: str) -> bool:
    """True si la string representa limpiamente un número (incluye negativos y decimales)."""
    return bool(_NUMERIC_VALUE_RE.match(value.strip())) if value.strip() else False


def _collect_values(sample_items: list[dict], key: str, limit: int = 12) -> list[Any]:
    """Recoge los valores no vacíos de una key a lo largo de los items de ejemplo."""
    values: list[Any] = []
    for item in sample_items:
        if not isinstance(item, dict):
            continue
        if key in item:
            v = item[key]
            if v is None or v == "":
                continue
            values.append(v)
        if len(values) >= limit:
            break
    return values


def infer_field_role(key: str, values: list[Any]) -> str:
    """Infiere el rol de un único campo a partir de su nombre y sus valores."""
    name = (key or "").lower()

    if not values:
        # Sin datos, decidimos solo por el nombre.
        if any(h in name for h in _IMAGE_NAME_HINTS):
            return "image"
        if any(h in name for h in _DATE_NAME_HINTS):
            return "date"
        if any(h in name for h in _TITLE_NAME_HINTS):
            return "title"
        return "text"

    # Trabajamos sobre representaciones string para uniformar APIs que mezclan tipos.
    str_values = [str(v).strip() for v in values]

    # ── Booleano ──
    bool_like = {"true", "false", "0", "1", "yes", "no"}
    if all(isinstance(v, bool) for v in values):
        return "boolean"
    if all(s.lower() in bool_like for s in str_values) and len({s.lower() for s in str_values}) <= 2 and not all(_INT_VALUE_RE.match(s) for s in str_values):
        return "boolean"

    # ── Imagen / URL ──
    url_like = [s for s in str_values if s.startswith("http://") or s.startswith("https://")]
    if url_like and len(url_like) >= max(1, len(str_values) // 2):
        if any(_IMAGE_EXT_RE.search(s) for s in url_like) or any(h in name for h in _IMAGE_NAME_HINTS):
            return "image"
        return "url"

    # ── Numérico (incluye strings numéricas tipo "76753.69") ──
    numeric_count = sum(1 for s in str_values if _is_numeric_string(s))
    if numeric_count >= max(1, int(len(str_values) * 0.8)):
        # Un campo cuyo nombre sugiere fecha (creation_date, year…) con años sueltos
        # NO es una métrica agregable: lo tratamos como texto/fecha, no numeric.
        if any(h in name for h in _DATE_NAME_HINTS) or "year" in name or "año" in name:
            return "text"
        # ¿Es una variación/porcentaje? (nombre sugiere cambio, o hay negativos)
        has_negative = any(s.startswith("-") for s in str_values)
        if any(h in name for h in _PERCENT_NAME_HINTS):
            return "percent"
        if has_negative and "rank" not in name:
            return "percent"
        return "numeric"

    # ── Fecha ──
    if any(h in name for h in _DATE_NAME_HINTS) or all(_DATE_VALUE_RE.match(s) for s in str_values):
        if all(_DATE_VALUE_RE.match(s) for s in str_values):
            return "date"

    # ── Texto: distinguir título / categoría / largo / corto ──
    max_len = max((len(s) for s in str_values), default=0)
    avg_len = (sum(len(s) for s in str_values) / len(str_values)) if str_values else 0
    if max_len > 90 or avg_len > 60:
        return "long_text"

    distinct = {s.lower() for s in str_values}
    repetition_ratio = 1 - (len(distinct) / len(str_values)) if str_values else 0

    if any(h in name for h in _CATEGORY_NAME_HINTS):
        return "category"
    # Pocos valores distintos y repetidos → categoría (género, estado, tipo…)
    if len(str_values) >= 4 and repetition_ratio >= 0.4 and max_len <= 40:
        return "category"
    if any(h in name for h in _TITLE_NAME_HINTS):
        return "title"

    return "text"


def is_numeric_role(role: str) -> bool:
    return role in ("numeric", "percent")


def infer_roles(fields: list[dict], sample_items: list[dict]) -> dict[str, str]:
    """
    Devuelve {key: role} para cada campo del schema.

    `fields` es la lista [{key, label}, ...] del plan; `sample_items` son
    los items de ejemplo del dataset.
    """
    roles: dict[str, str] = {}
    for field in fields or []:
        key = field.get("key") if isinstance(field, dict) else None
        if not key:
            continue
        values = _collect_values(sample_items or [], key)
        roles[key] = infer_field_role(key, values)
    return roles


def pick_primary_numeric(roles: dict[str, str], fields: list[dict]) -> str | None:
    """
    Elige el campo numérico 'principal' para agregar en un dashboard.
    Prefiere campos cuyo nombre sugiere magnitud (price, value, total, cap,
    amount, volume) sobre porcentajes o ranks.
    """
    order_fields = [f.get("key") for f in (fields or []) if isinstance(f, dict)]
    magnitude_hints = ("price", "value", "valor", "total", "cap", "amount", "monto", "volume", "volumen", "revenue", "sales", "count", "score")

    numeric_keys = [k for k in order_fields if roles.get(k) == "numeric"]
    if not numeric_keys:
        # como último recurso, aceptamos percent
        numeric_keys = [k for k in order_fields if roles.get(k) == "percent"]
    if not numeric_keys:
        return None

    for k in numeric_keys:
        if any(h in (k or "").lower() for h in magnitude_hints):
            return k
    return numeric_keys[0]


def pick_signed_field(roles: dict[str, str], fields: list[dict]) -> str | None:
    """Elige un campo de variación con signo (para badges sube/baja en dashboards)."""
    for f in (fields or []):
        if isinstance(f, dict) and roles.get(f.get("key")) == "percent":
            return f.get("key")
    return None


def roles_summary_text(roles: dict[str, str], primary_numeric: str | None = None, signed: str | None = None) -> str:
    """Texto listo para inyectar en los prompts del LLM."""
    lines = ["ROLES SEMÁNTICOS DE CAMPOS (inferidos del dataset):"]
    for key, role in roles.items():
        lines.append(f"  - {key}: {role}")
    if primary_numeric:
        lines.append(f"CAMPO NUMÉRICO PRINCIPAL (para métricas/agregados): {primary_numeric}")
    if signed:
        lines.append(f"CAMPO DE VARIACIÓN CON SIGNO (para badges sube/baja): {signed}")
    return "\n".join(lines)


__all__ = [
    "infer_field_role",
    "infer_roles",
    "is_numeric_role",
    "pick_primary_numeric",
    "pick_signed_field",
    "roles_summary_text",
]