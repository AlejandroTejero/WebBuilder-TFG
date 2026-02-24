"""
Vistas de render a pantalla completa.

/preview/<id>/render/           → muestra el sitio generado con barra WebBuilder encima
/preview/<id>/render/regenerar/ → regenera el tema con nuevo hint y redirige al render
"""

from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..models import APIRequest, GeneratedSite
from ..utils.analysis import build_analysis
from ..utils.analysis.helpers import get_by_path
from ..utils.llm.themer import generate_site_theme
from ..utils.llm.planner import _validate_and_normalize_schema


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


def _get_fields_from_plan(plan: dict) -> list[dict]:
    if not isinstance(plan, dict):
        return []
    return plan.get("fields") or []


def _normalize_item(raw_item: Any, fields: list[dict], *, index: int, max_len: int = 400) -> dict:
    result: dict[str, Any] = {"index": index}
    if not isinstance(raw_item, dict):
        return result
    for field in fields:
        key = field["key"]
        result[key] = _to_text(raw_item.get(key), max_len=max_len)
    return result


def _get_main_items(api_request: APIRequest) -> list[Any]:
    analysis  = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
    main      = analysis.get("main_collection") or {}
    main_path = main.get("path")
    if main_path is None:
        return []
    node = get_by_path(api_request.parsed_data, main_path)
    return node if isinstance(node, list) else []


def _render_site_html(site: GeneratedSite, api_request: APIRequest) -> str:
    """Renderiza el HTML completo del sitio usando los templates del GeneratedSite."""
    import re
    import json as _json
    from django.template import Context, Template
    from django.utils.safestring import mark_safe

    plan   = site.accepted_plan or {}
    fields = _get_fields_from_plan(plan)

    raw_items  = _get_main_items(api_request)
    items_norm = [
        _normalize_item(it, fields, index=i, max_len=260)
        for i, it in enumerate(raw_items[:24])
    ]

    theme       = site.theme_templates or {}
    base_html   = theme.get("base_html") or ""
    home_html   = theme.get("home_html") or ""
    css         = site.theme_css or theme.get("css") or ""

    site_title = plan.get("site_title") or plan.get("site_type") or "Site"
    site_type  = plan.get("site_type") or "other"
    site_ctx   = {"id": site.id, "title": site_title, "type": site_type}

    def _fix(s: str) -> str:
        if not s:
            return s
        s = re.sub(r'(\w+)\.get\(["\']([\w.]+)["\']\)', r'\1.\2', s)
        s = re.sub(r'(\w+)\[["\']([\w.]+)["\']\]', r'\1.\2', s)
        s = re.sub(r'(\w+)\(["\'][^"\']*["\']\)', r'\1', s)
        s = re.sub(r'(\w+)\(\s*\)', r'\1', s)
        return s

    def _safe_render(tpl_str: str, ctx: dict) -> str:
        try:
            return Template(_fix(tpl_str)).render(Context(ctx, autoescape=True))
        except Exception:
            return f"<!-- Error renderizando template -->"

    fragment = _safe_render(home_html, {"site": site_ctx, "items": items_norm})
    full     = _safe_render(base_html, {
        "site":    site_ctx,
        "content": mark_safe(fragment),
        "css":     mark_safe(css),
    })
    return full


# ────────────────────────── vistas ──────────────────────────────────

@login_required
def site_render(request, api_request_id: int):
    """
    Renderiza el sitio a pantalla completa con barra WebBuilder encima.
    """
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)

    # Consulta directa para evitar caché del ORM
    site = GeneratedSite.objects.filter(project_source=api_request).first()

    if not site:
        # No hay GeneratedSite todavía — mostrar pantalla de "sin publicar"
        return render(request, "WebBuilder/site_render.html", {
            "api_request": api_request,
            "site":        None,
            "site_html":   "",
            "plan":        api_request.field_mapping or {},
        })

    plan     = site.accepted_plan or api_request.field_mapping or {}
    site_html = _render_site_html(site, api_request)

    return render(request, "WebBuilder/site_render.html", {
        "api_request": api_request,
        "site":        site,
        "site_html":   site_html,
        "plan":        plan,
    })


@login_required
def site_render_regen(request, api_request_id: int):
    """
    POST: regenera el tema con un nuevo hint de diseño y redirige al render.
    """
    if request.method != "POST":
        return redirect("site_render", api_request_id=api_request_id)

    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = GeneratedSite.objects.filter(project_source=api_request).first()

    if not site:
        messages.warning(request, "Acepta el plan primero.")
        return redirect("preview", api_request_id=api_request_id)

    design_hint = (request.POST.get("design_hint") or "").strip()

    plan       = site.accepted_plan or api_request.field_mapping or {}
    fields     = _get_fields_from_plan(plan)
    site_type  = plan.get("site_type") or "other"
    site_title = plan.get("site_title") or site_type

    raw_items    = _get_main_items(api_request)
    sample_items = [
        _normalize_item(it, fields, index=i, max_len=180)
        for i, it in enumerate(raw_items[:6])
    ]

    theme = generate_site_theme(
        site_title=site_title,
        site_type=site_type,
        design_hint=design_hint or site_title,
        fields=fields,
        sample_items=sample_items,
        retries=1,
    )

    site.theme_templates = {
        "base_html":   theme["base_html"],
        "home_html":   theme["home_html"],
        "detail_html": theme["detail_html"],
    }
    site.theme_css    = theme.get("css", "")
    site.theme_prompt = design_hint
    site.save()

    messages.success(request, "Diseño regenerado ✅")
    return redirect("site_render", api_request_id=api_request_id)
