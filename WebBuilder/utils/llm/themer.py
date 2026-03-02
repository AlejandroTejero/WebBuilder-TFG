"""
Themer — rellena las plantillas base Dark & Sharp con los campos del schema.

Flujo:
  1. Se coge la plantilla base para el site_type (catalog/blog/portfolio/other).
  2. El LLM genera SOLO dos fragmentos pequeños de HTML Django:
       - home_fields:   el interior de cada card en el listado
       - detail_fields: el bloque de campos en la vista de detalle
  3. Los fragmentos se inyectan en los placeholders de la plantilla.
  4. Si el LLM falla, se usa un fallback generado directamente en Python.

Variables disponibles en los fragmentos generados:
  home_fields:   it.<key> para cada field del schema
  detail_fields: item.<key> para cada field del schema
"""

from __future__ import annotations

import json
import re

from .client import chat_completion, LLMError
from .llm_utils import parse_llm_json
from .templates import (
    get_template,
    HOME_FIELDS_PLACEHOLDER,
    DETAIL_FIELDS_PLACEHOLDER,
)


class ThemeError(Exception):
    pass


# ─────────────────────────── sanitización ────────────────────────────

def _sanitize_fragment(s: str) -> str:
    """Elimina tags de herencia/includes que no tienen sentido en un fragmento."""
    if not s:
        return ""
    s = re.sub(r"{%\s*extends\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*include\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*load\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*block\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*endblock\s*.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    return s.strip()


# ─────────────────────────── fallback ────────────────────────────────

def _fallback_home_fields(fields: list[dict]) -> str:
    """Fragmento home mínimo funcional con clases Tailwind Dark & Sharp."""
    if not fields:
        return ""
    first = fields[0]
    rest = fields[1:4]

    lines = [
        f'{{% if it.{first["key"]} %}}'
        f'<p class="text-white font-semibold text-sm truncate">{{{{ it.{first["key"]} }}}}</p>'
        f'{{% endif %}}'
    ]
    for f in rest:
        lines.append(
            f'{{% if it.{f["key"]} %}}'
            f'<p class="text-gray-400 text-xs font-mono truncate">'
            f'<span class="text-gray-600">{f["label"]}:</span> {{{{ it.{f["key"]} }}}}'
            f'</p>'
            f'{{% endif %}}'
        )
    return "\n".join(lines)


def _fallback_detail_fields(fields: list[dict]) -> str:
    """Fragmento detail mínimo funcional con clases Tailwind Dark & Sharp."""
    lines = []
    for f in fields:
        lines.append(
            f'{{% if item.{f["key"]} %}}'
            f'<div class="flex gap-4 py-3 border-b border-gray-800 last:border-0">'
            f'<span class="text-gray-500 font-mono text-xs w-32 shrink-0 pt-0.5">{f["label"]}</span>'
            f'<span class="text-gray-100 text-sm break-words flex-1">{{{{ item.{f["key"]} }}}}</span>'
            f'</div>'
            f'{{% endif %}}'
        )
    return "\n".join(lines)


def _fallback_theme(fields: list[dict], site_type: str) -> dict:
    """Tema funcional usando la plantilla base + fragmentos generados en Python."""
    tpl = get_template(site_type)
    home_fields   = _fallback_home_fields(fields)
    detail_fields = _fallback_detail_fields(fields)

    return {
        "base_html":   tpl["base_html"],
        "home_html":   tpl["home_html"].replace(HOME_FIELDS_PLACEHOLDER, home_fields),
        "detail_html": tpl["detail_html"].replace(DETAIL_FIELDS_PLACEHOLDER, detail_fields),
        "css":         "",
    }


# ─────────────────────────── prompt ──────────────────────────────────

def _build_theme_prompt(
    *,
    site_title: str,
    site_type: str,
    fields: list[dict],
    sample_items: list[dict],
) -> tuple[str, str]:

    field_vars_home   = ", ".join(f"it.{f['key']}"   for f in fields)
    field_vars_detail = ", ".join(f"item.{f['key']}" for f in fields)
    first_key = fields[0]["key"] if fields else "id"

    # Construir ejemplos sin f-strings anidadas
    home_example_lines = []
    for i, f in enumerate(fields[:4]):
        if i == 0:
            css_class = "text-white font-semibold text-sm"
            prefix = ""
        else:
            css_class = "text-gray-400 text-xs font-mono"
            prefix = f'<span class="text-gray-600">{f["label"]}:</span> '
        home_example_lines.append(
            f'{{% if it.{f["key"]} %}}'
            f'<p class="{css_class} truncate">{prefix}{{{{ it.{f["key"]} }}}}</p>'
            f'{{% endif %}}'
        )
    example_home_fields = "\n".join(home_example_lines)

    example_detail_fields = "\n".join(
        f'{{% if item.{f["key"]} %}}'
        f'<div class="flex gap-4 py-3 border-b border-gray-800 last:border-0">'
        f'<span class="text-gray-500 font-mono text-xs w-32 shrink-0">{f["label"]}</span>'
        f'<span class="text-gray-100 text-sm break-words flex-1">{{{{ item.{f["key"]} }}}}</span>'
        f'</div>'
        f'{{% endif %}}'
        for f in fields
    )

    fields_info = json.dumps(
        [{"key": f["key"], "label": f["label"]} for f in fields],
        ensure_ascii=False, indent=2,
    )

    system = (
        "Eres un experto en templates Django y Tailwind CSS. "
        "Devuelve SOLO un objeto JSON válido con 2 keys: home_fields y detail_fields. "
        "Ambos son fragmentos HTML con clases Tailwind y sintaxis Django pura. "
        "NUNCA uses sintaxis Python: nada de item.get(), item['key'], f-strings o items(). "
        "NO incluyas <html>, <head>, <body>, {% extends %}, {% block %} ni {% load %}."
    )

    rules = [
        "Devuelve SOLO JSON con 2 keys: home_fields y detail_fields.",
        "home_fields: fragmento HTML para el interior de cada card en el listado.",
        f"  - Variables disponibles: it.index, {field_vars_home}",
        f"  - El primer campo ({first_key}) debe destacar visualmente (más grande, texto blanco).",
        "  - Los campos secundarios en gris más pequeño con font-mono.",
        "  - Usa {% if it.<key> %} ... {% endif %} para cada campo.",
        "  - NO incluyas el enlace <a> ni el contenedor de la card, solo el contenido interior.",
        "detail_fields: fragmento HTML para la vista de detalle de un item.",
        f"  - Variables disponibles: item.index, {field_vars_detail}",
        "  - Muestra todos los campos en filas label + valor.",
        "  - Usa {% if item.<key> %} ... {% endif %} para cada campo.",
        "  - NO incluyas el enlace de volver ni el contenedor exterior.",
        "ESTILO: Dark & Sharp con Tailwind. Fondo oscuro ya aplicado en la plantilla base.",
        "  - Texto principal: text-white o text-gray-100",
        "  - Texto secundario: text-gray-400 o text-gray-500",
        "  - Acento: text-green-400",
        "  - Fuente datos: font-mono text-xs o text-sm",
        "PROHIBIDO inventar variables que no estén en la lista de fields.",
        "NUNCA uses item.get(), item['key'] ni ninguna sintaxis Python.",
    ]

    user_text = "\n".join([
        "SCHEMA DE CAMPOS:",
        fields_info,
        "",
        "ITEMS DE EJEMPLO (así llegan los datos):",
        json.dumps(sample_items[:3], ensure_ascii=False, indent=2),
        "",
        "META:",
        json.dumps({"title": site_title, "site_type": site_type}, ensure_ascii=False),
        "",
        "REGLAS:",
        "\n".join(f"- {r}" for r in rules),
        "",
        "EJEMPLO home_fields CORRECTO:",
        example_home_fields,
        "",
        "EJEMPLO detail_fields CORRECTO:",
        example_detail_fields,
        "",
        "CONTRATO (devuelve EXACTAMENTE estas 2 keys):",
        json.dumps(
            {
                "home_fields":   "fragmento HTML interior de cada card, con it.<key>",
                "detail_fields": "fragmento HTML con todos los campos, con item.<key>",
            },
            ensure_ascii=False, indent=2,
        ),
    ])

    return system, user_text
# ─────────────────────────── ensamblado ──────────────────────────────

def _assemble(tpl: dict, home_fields: str, detail_fields: str) -> dict:
    """Inyecta los fragmentos en los placeholders de la plantilla base."""
    return {
        "base_html":   tpl["base_html"],
        "home_html":   tpl["home_html"].replace(HOME_FIELDS_PLACEHOLDER, home_fields),
        "detail_html": tpl["detail_html"].replace(DETAIL_FIELDS_PLACEHOLDER, detail_fields),
        "css":         "",
    }


# ─────────────────────────── función pública ─────────────────────────

def generate_site_theme(
    *,
    site_title: str,
    site_type: str,
    design_hint: str,
    fields: list[dict],
    sample_items: list[dict],
    retries: int = 1,
) -> dict:
    """
    Genera el tema completo inyectando fragmentos del LLM en la plantilla base.

    Si el LLM falla, usa _fallback_theme que genera los fragmentos en Python.
    """
    if not fields:
        return _fallback_theme(fields, site_type)

    tpl = get_template(site_type)
    system, user_text = _build_theme_prompt(
        site_title=site_title,
        site_type=site_type,
        fields=fields,
        sample_items=sample_items,
    )

    for attempt in range(retries + 1):
        try:
            raw  = chat_completion(user_text=user_text, system_text=system, temperature=0.3)
            data = parse_llm_json(raw, exc_class=ThemeError)

            if not isinstance(data, dict):
                raise ThemeError("La respuesta del LLM no era un objeto JSON.")

            home_fields   = _sanitize_fragment(str(data.get("home_fields",   "") or ""))
            detail_fields = _sanitize_fragment(str(data.get("detail_fields", "") or ""))

            if not home_fields or not detail_fields:
                raise ThemeError("El LLM no devolvió home_fields o detail_fields.")

            if "item.get(" in home_fields or "item.get(" in detail_fields:
                raise ThemeError("El LLM usó sintaxis Python (item.get) en vez de Django.")

            return _assemble(tpl, home_fields, detail_fields)

        except (LLMError, ThemeError, ValueError, json.JSONDecodeError):
            if attempt >= retries:
                return _fallback_theme(fields, site_type)

    return _fallback_theme(fields, site_type)
