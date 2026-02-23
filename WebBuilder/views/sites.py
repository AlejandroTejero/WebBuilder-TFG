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

    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def _normalize_item(raw_item: Any, mapping: dict, *, index: int, detail: bool = False) -> dict:
    if not isinstance(raw_item, dict):
        return {"index": index, "title": "(sin título)", "content": "", "image": "", "date": ""}

    def pick(field: str) -> Any:
        k = (mapping or {}).get(field)
        return raw_item.get(k) if k else None

    title   = _to_text(pick("title"),   max_len=90)                or "(sin título)"
    content = _to_text(pick("content"), max_len=2000 if detail else 260)
    image   = _to_text(pick("image"),   max_len=500)
    date    = _to_text(pick("date"),    max_len=80)

    return {"index": index, "title": title, "content": content, "image": image, "date": date}


def _get_main_items(api_request: APIRequest) -> list[Any]:
    analysis  = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
    main      = analysis.get("main_collection") or {}
    main_path = main.get("path")
    if main_path is None:
        return []
    node = get_by_path(api_request.parsed_data, main_path)
    return node if isinstance(node, list) else []


def _fallback_theme() -> dict:
    """Templates mínimos de emergencia cuando el LLM genera algo que no se puede renderizar."""
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
            '<h1>{{ site.title }}</h1><ul>'
            '{% for it in items %}'
            '<li><a href="/sites/{{ site.id }}/item/{{ it.index }}/">{{ it.title }}</a>'
            '{% if it.content %} — {{ it.content }}{% endif %}</li>'
            '{% endfor %}</ul>'
        ),
        "detail_html": (
            '<p><a href="/sites/{{ site.id }}/">← Volver</a></p>'
            '<h1>{{ item.title }}</h1>'
            '{% if item.date %}<p><small>{{ item.date }}</small></p>{% endif %}'
            '{% if item.image %}<img src="{{ item.image }}" alt="{{ item.title }}">{% endif %}'
            '{% if item.content %}<div>{{ item.content }}</div>{% endif %}'
        ),
    }


def _fix_llm_template(s: str) -> str:
    """
    Repara los errores más comunes que comete el LLM al generar templates Django.

    Problemas cubiertos (en orden de aplicación):
    - item.get('key')    → método Python    → convierte a item.key
    - item['key']        → subscript Python → convierte a item.key
    - items('')/ items() → llamada Python   → quita los paréntesis
    - |join / |join:     → sin argumento    → elimina el filtro
    - |join:,            → sin comillas     → corrige a |join:", "
    - |truncatechars     → sin número       → elimina el filtro
    """
    if not s:
        return s

    # Primero los más específicos para evitar que el regex genérico los machaque
    # item.get('key') o item.get("key") → item.key
    s = re.sub(r'(\w+)\.get\(["\'](\w+)["\']\)', r'\1.\2', s)
    # item['key'] o item["key"] → item.key
    s = re.sub(r'(\w+)\[["\'](\w+)["\']\]', r'\1.\2', s)

    # Después los genéricos
    # func('algo') o func("algo") → func
    s = re.sub(r'(\w+)\(["\'][^"\']*["\']\)', r'\1', s)
    # func() → func
    s = re.sub(r'(\w+)\(\s*\)', r'\1', s)

    # Filtros mal formados
    # |join sin argumento (no seguido de :)
    s = re.sub(r'\|join(?!\s*:)', '', s)
    # |join: con separador vacío
    s = re.sub(r'\|join:\s*(?=[|\s}])', '', s)
    # |join:, sin comillas → corregir
    s = re.sub(r'\|join:\s*,', '|join:", "', s)
    # |truncatechars sin número
    s = re.sub(r'\|truncatechars(?!\s*:)', '', s)

    # Normalizar espacios dentro de {{ }}
    s = re.sub(r'\{\{\s*(.*?)\s*\}\}', lambda m: '{{ ' + m.group(1).strip() + ' }}', s)

    return s





def _safe_render_template(template_str: str, context_dict: dict) -> str:
    """
    Renderiza un template Django con 3 niveles de defensa:
      1. Repara errores comunes del LLM y renderiza.
      2. Si falla, usa el fallback_theme para este fragmento según el contexto.
      3. Nunca devuelve un 500 ni una página vacía.
    """
    cleaned = _fix_llm_template(template_str)
    try:
        return Template(cleaned).render(Context(context_dict, autoescape=True))
    except Exception as e:
        # Guardar el error para devolver info útil
        error_msg = str(e)

    # Intento 2: usar fallback según el contexto disponible
    # Si hay "items" en el contexto → es home_html, usar el fallback de home
    # Si hay "item" (singular) → es detail_html
    # Si hay "content" → es base_html
    fallback = _fallback_theme()
    site_ctx = context_dict.get("site", {})

    if "content" in context_dict:
        # Es base_html
        fallback_tpl = fallback["base_html"]
    elif "item" in context_dict and context_dict.get("item"):
        # Es detail_html
        fallback_tpl = fallback["detail_html"]
    else:
        # Es home_html
        fallback_tpl = fallback["home_html"]

    try:
        return Template(fallback_tpl).render(Context(context_dict, autoescape=True))
    except Exception:
        pass

    # Intento 3: solo el error visible para debugging
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
    site_title = plan.get("site_type_custom") or plan.get("site_type") or "Site"
    site_type  = plan.get("site_type") or "other"

    site_ctx = {"id": site.id, "title": site_title, "type": site_type}

    # Fragmento home / detail
    if page == "detail":
        fragment = _safe_render_template(
            detail_html,
            {"site": site_ctx, "items": items_norm, "item": item_norm or {}},
        )
    else:
        fragment = _safe_render_template(
            home_html,
            {"site": site_ctx, "items": items_norm},
        )

    # Base con fragmento + css inyectados
    full = _safe_render_template(
        base_html,
        {
            "site":    site_ctx,
            "content": mark_safe(fragment),
            "css":     mark_safe(css),
        },
    )
    return full


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------

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

    plan    = site.accepted_plan or api_request.field_mapping or {}
    mapping = (plan.get("mapping") or {}) if isinstance(plan, dict) else {}

    raw_items  = _get_main_items(api_request)
    items_norm = [_normalize_item(it, mapping, index=i, detail=False) for i, it in enumerate(raw_items[:24])]

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

    plan    = site.accepted_plan or api_request.field_mapping or {}
    mapping = (plan.get("mapping") or {}) if isinstance(plan, dict) else {}

    raw_items = _get_main_items(api_request)

    if item_index < 0 or item_index >= len(raw_items):
        messages.error(request, "Item fuera de rango.")
        return redirect("site_home", site_id=site.id)

    items_norm = [_normalize_item(it, mapping, index=i, detail=False) for i, it in enumerate(raw_items[:24])]
    item_norm  = _normalize_item(raw_items[item_index], mapping, index=item_index, detail=True)

    site_html = _render_theme_page(site=site, page="detail", items_norm=items_norm, item_norm=item_norm)
    return HttpResponse(site_html, content_type="text/html; charset=utf-8")
