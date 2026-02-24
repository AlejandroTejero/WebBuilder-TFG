"""
Vistas de sitios generados — renderiza con schema dinámico.

Los templates del LLM acceden a los items así:
  home_html:   {% for it in items %} → it.<key> para cada field del schema
  detail_html: {{ item.<key> }} para cada field del schema

_normalize_item construye un objeto SimpleNamespace-like (dict con acceso
dot-notation vía Context de Django) con todos los fields del schema.
"""

from __future__ import annotations

import json
import re
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, Template, TemplateSyntaxError
from django.utils.safestring import mark_safe
from django.http import HttpResponse

from ..models import GeneratedSite, APIRequest
from ..utils.analysis import build_analysis
from ..utils.analysis.helpers import get_by_path


# ────────────────────────── helpers ─────────────────────────────────

def _to_text(value: Any, *, max_len: int = 400) -> str:
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


def _normalize_item(raw_item: Any, fields: list[dict], *, index: int, max_len: int = 400) -> dict:
    """
    Convierte un item del dataset en un dict plano con las keys del schema.
    Cada key del schema queda como item[key] = str con truncado configurable.
    Siempre incluye 'index'.
    """
    result: dict[str, Any] = {"index": index}
    if not isinstance(raw_item, dict):
        return result
    for field in fields:
        key = field["key"]
        result[key] = _to_text(raw_item.get(key), max_len=max_len)
    return result


def _get_fields_from_plan(plan: dict) -> list[dict]:
    """Extrae la lista de fields del plan (nuevo schema dinámico)."""
    if not isinstance(plan, dict):
        return []
    return plan.get("fields") or []


def _get_main_items(api_request: APIRequest) -> list[Any]:
    analysis  = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
    main      = analysis.get("main_collection") or {}
    main_path = main.get("path")
    if main_path is None:
        return []
    node = get_by_path(api_request.parsed_data, main_path)
    return node if isinstance(node, list) else []


# ────────────────────────── template fix + render ───────────────────

def _fix_llm_template(s: str) -> str:
    """
    Repara los errores más comunes que comete el LLM al generar templates Django.
    """
    if not s:
        return s

    # item.get('key') o item.get("key") → item.key
    s = re.sub(r'(\w+)\.get\(["\']([\w.]+)["\']\)', r'\1.\2', s)
    # item['key'] o item["key"] → item.key
    s = re.sub(r'(\w+)\[["\']([\w.]+)["\']\]', r'\1.\2', s)

    # func('algo') o func("algo") → func
    s = re.sub(r'(\w+)\(["\'][^"\']*["\']\)', r'\1', s)
    # func() → func
    s = re.sub(r'(\w+)\(\s*\)', r'\1', s)

    # Filtros mal formados
    s = re.sub(r'\|join(?!\s*:)', '', s)
    s = re.sub(r'\|join:\s*(?=[|\s}])', '', s)
    s = re.sub(r'\|join:\s*,', '|join:", "', s)
    s = re.sub(r'\|truncatechars(?!\s*:)', '', s)

    # Normalizar espacios dentro de {{ }}
    s = re.sub(r'\{\{\s*(.*?)\s*\}\}', lambda m: '{{ ' + m.group(1).strip() + ' }}', s)

    return s


def _fallback_theme(fields: list[dict]) -> dict:
    """Templates mínimos de emergencia cuando el LLM genera algo que no se puede renderizar."""
    first_key = fields[0]["key"] if fields else "id"

    detail_rows = "\n".join(
        f'{{% if item.{f["key"]} %}}'
        f'<div class="field-row">'
        f'<span class="field-label">{f["label"]}</span>'
        f'<span class="field-value">{{{{ item.{f["key"]} }}}}</span>'
        f'</div>'
        f'{{% endif %}}'
        for f in fields
    )

    return {
        "base_html": (
            '<!doctype html><html lang="es"><head>'
            '<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>{{ site.title }}</title>'
            '<style>{{ css }}</style>'
            '</head><body>'
            '<main style="max-width:1100px;margin:0 auto;padding:16px;">{{ content }}</main>'
            '</body></html>'
        ),
        "home_html": (
            f'<h1>{{{{ site.title }}}}</h1><ul>'
            f'{{% for it in items %}}'
            f'<li><a href="/sites/{{{{ site.id }}}}/item/{{{{ it.index }}}}/">{{{{ it.{first_key} }}}}</a></li>'
            f'{{% endfor %}}</ul>'
        ),
        "detail_html": (
            f'<p><a href="/sites/{{{{ site.id }}}}/">← Volver</a></p>'
            f'<h1>{{{{ item.{first_key} }}}}</h1>'
            f'<div class="detail-fields">{detail_rows}</div>'
        ),
    }


def _safe_render_template(template_str: str, context_dict: dict, fields: list[dict]) -> str:
    """
    Renderiza un template Django con 3 niveles de defensa:
      1. Repara errores comunes del LLM y renderiza.
      2. Si falla, usa el fallback_theme para este fragmento.
      3. Nunca devuelve un 500.
    """
    cleaned = _fix_llm_template(template_str)
    try:
        return Template(cleaned).render(Context(context_dict, autoescape=True))
    except Exception as e:
        error_msg = str(e)

    # Intento 2: fallback según el contexto
    fallback = _fallback_theme(fields)
    if "content" in context_dict:
        fallback_tpl = fallback["base_html"]
    elif "item" in context_dict and context_dict.get("item"):
        fallback_tpl = fallback["detail_html"]
    else:
        fallback_tpl = fallback["home_html"]

    try:
        return Template(fallback_tpl).render(Context(context_dict, autoescape=True))
    except Exception:
        pass

    return f"<!-- Error al renderizar template: {error_msg} -->"


def _render_theme_page(
    *,
    site: GeneratedSite,
    page: str,
    items_norm: list[dict],
    item_norm: dict | None = None,
) -> str:
    theme       = site.theme_templates or {}
    base_html   = theme.get("base_html")   or ""
    home_html   = theme.get("home_html")   or ""
    detail_html = theme.get("detail_html") or ""
    css         = site.theme_css or theme.get("css") or ""

    plan       = site.accepted_plan or {}
    fields     = _get_fields_from_plan(plan)
    site_title = plan.get("site_title") or plan.get("site_type") or "Site"
    site_type  = plan.get("site_type") or "other"

    site_ctx = {"id": site.id, "title": site_title, "type": site_type}

    # Fragmento home / detail
    if page == "detail":
        fragment = _safe_render_template(
            detail_html,
            {"site": site_ctx, "items": items_norm, "item": item_norm or {}},
            fields,
        )
    else:
        fragment = _safe_render_template(
            home_html,
            {"site": site_ctx, "items": items_norm},
            fields,
        )

    # Base con fragmento + css inyectados
    full = _safe_render_template(
        base_html,
        {
            "site":    site_ctx,
            "content": mark_safe(fragment),
            "css":     mark_safe(css),
        },
        fields,
    )
    return full


# ────────────────────────── vistas ──────────────────────────────────

@login_required
def site_home(request, site_id: int):
    site = get_object_or_404(
        GeneratedSite.objects.select_related("project_source"),
        id=site_id,
        project_source__user=request.user,
    )

    api_request = site.project_source

    if not api_request.plan_accepted:
        messages.error(request, "Este plan no está aceptado. Vuelve al preview.")
        return redirect("preview", api_request_id=api_request.id)

    plan   = site.accepted_plan or api_request.field_mapping or {}
    fields = _get_fields_from_plan(plan)

    raw_items  = _get_main_items(api_request)
    items_norm = [
        _normalize_item(it, fields, index=i, max_len=260)
        for i, it in enumerate(raw_items[:24])
    ]

    site_html = _render_theme_page(site=site, page="home", items_norm=items_norm)
    return HttpResponse(site_html, content_type="text/html; charset=utf-8")


@login_required
def site_detail(request, site_id: int, item_index: int):
    site = get_object_or_404(
        GeneratedSite.objects.select_related("project_source"),
        id=site_id,
        project_source__user=request.user,
    )

    api_request = site.project_source

    if not api_request.plan_accepted:
        messages.error(request, "Este plan no está aceptado. Vuelve al preview.")
        return redirect("preview", api_request_id=api_request.id)

    plan   = site.accepted_plan or api_request.field_mapping or {}
    fields = _get_fields_from_plan(plan)

    raw_items = _get_main_items(api_request)

    if item_index < 0 or item_index >= len(raw_items):
        messages.error(request, "Item fuera de rango.")
        return redirect("site_home", site_id=site.id)

    items_norm = [
        _normalize_item(it, fields, index=i, max_len=260)
        for i, it in enumerate(raw_items[:24])
    ]
    item_norm = _normalize_item(raw_items[item_index], fields, index=item_index, max_len=2000)

    site_html = _render_theme_page(site=site, page="detail", items_norm=items_norm, item_norm=item_norm)
    return HttpResponse(site_html, content_type="text/html; charset=utf-8")
