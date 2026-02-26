"""
Vista de preview — trabaja con el nuevo schema dinámico.

Schema (field_mapping):
  {
    "site_type": str,
    "site_title": str,
    "fields": [{"key": str, "label": str}, ...]
  }

En preview el usuario puede:
  - Ver los items con todos los campos del schema.
  - Editar site_type, site_title y reordenar/activar/desactivar campos.
  - Aceptar el plan → genera el tema con el LLM y crea el GeneratedSite.
"""

from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from ..models import APIRequest, GeneratedSite
from ..utils.analysis import build_analysis
from ..utils.analysis.helpers import get_by_path
from ..utils.llm.themer import generate_site_theme


# ────────────────────────── helpers ─────────────────────────────────

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


def _normalize_site_type(value: str | None) -> str:
    allowed = {"blog", "portfolio", "catalog", "dashboard", "other"}
    v = (value or "").strip().lower()
    return v if v in allowed else "other"


def _normalize_item(raw_item: Any, fields: list[dict], *, index: int) -> dict:
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
        result[key] = _to_text(raw_item.get(key), max_len=300)
    return result


def _get_available_keys_from_analysis(api_request: APIRequest) -> list[str]:
    analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
    keys_info = analysis.get("keys") or {}
    return (keys_info.get("top") or [])[:30]


def _validate_fields_against_keys(fields: list[dict], available_keys: list[str]) -> list[dict]:
    """
    Filtra la lista de fields para que solo queden keys presentes en available_keys.
    Previene que fields guardados en BD con keys ya inválidas rompan la vista.
    """
    available_set = set(available_keys)
    return [f for f in fields if isinstance(f, dict) and f.get("key") in available_set]


# ────────────────────────── vista principal ──────────────────────────

@login_required
def edit(request, api_request_id: int):
    api_request = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
    if not api_request:
        messages.error(request, "No se encontró ese análisis en tu cuenta.")
        return redirect("assistant")

    plan = api_request.field_mapping
    if not plan:
        messages.error(request, "Este análisis no tiene schema del LLM todavía.")
        return redirect(reverse("assistant") + f"?api_request_id={api_request.id}")

    if not api_request.parsed_data:
        messages.error(request, "Este análisis no tiene datos parseados.")
        return redirect(reverse("assistant") + f"?api_request_id={api_request.id}")
    
    # Normalizar plan (compatibilidad con schema antiguo y nuevo)
    if not isinstance(plan, dict):
        plan = {}

    # Migrar schema antiguo (mapping fijo) al nuevo formato si es necesario
    if "mapping" in plan and "fields" not in plan:
        old_mapping = plan.get("mapping") or {}
        plan = {
            "site_type": plan.get("site_type", "other"),
            "site_title": plan.get("site_type_custom") or plan.get("site_type", "Site"),
            "fields": [
                {"key": v, "label": k.capitalize()}
                for k, v in old_mapping.items()
                if v
            ],
        }

    plan.setdefault("site_type", "other")
    plan.setdefault("site_title", "Site")
    plan.setdefault("fields", [])

    # Recalcular analysis para keys disponibles y main_path
    analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
    main = analysis.get("main_collection") or {}
    main_path = main.get("path")

    keys_info = analysis.get("keys") or {}
    available_keys = (keys_info.get("top") or [])[:30]

    # Validar y limpiar fields del plan contra available_keys reales
    plan["fields"] = _validate_fields_against_keys(plan["fields"], available_keys)

    # Items para preview
    items = []
    if main_path is not None:
        node = get_by_path(api_request.parsed_data, main_path)
        if isinstance(node, list):
            items = node[:12]

    # ──────────────── POST ────────────────────────────────────────────
    if request.method == "POST":
        action = (request.POST.get("action") or "").strip().lower()

        # ── Guardar edición del schema ──────────────────────────────
        if action == "save_schema":
            new_site_type = _normalize_site_type(request.POST.get("site_type"))
            new_site_title = (request.POST.get("site_title") or "").strip()[:120] or new_site_type

            # Los fields se envían como campos ocultos: field_key_0, field_label_0, ...
            # con checkboxes field_active_0 para activar/desactivar
            new_fields = []
            i = 0
            while True:
                key = request.POST.get(f"field_key_{i}")
                if key is None:
                    break
                label = (request.POST.get(f"field_label_{i}") or key).strip()
                active = request.POST.get(f"field_active_{i}") == "on"
                if active and key in set(available_keys):
                    new_fields.append({"key": key, "label": label})
                i += 1

            # Si no queda ningún field activo, mantener los anteriores
            if not new_fields:
                new_fields = plan["fields"]

            plan["site_type"] = new_site_type
            plan["site_title"] = new_site_title
            plan["fields"] = new_fields

            api_request.field_mapping = plan
            api_request.plan_accepted = False
            api_request.save(update_fields=["field_mapping", "plan_accepted"])
            messages.success(request, "Schema actualizado ✅ (vuelve a aceptar para publicar)")
            return redirect("edit", api_request_id=api_request.id)

        # ── Aceptar plan y publicar ─────────────────────────────────
        if action == "accept_plan":
            fields = plan.get("fields") or []
            site_type = plan.get("site_type") or "other"
            site_title = plan.get("site_title") or site_type

            api_request.plan_accepted = True
            api_request.save(update_fields=["plan_accepted"])

            # Sample items normalizados para pasar al LLM themer
            sample_items = [
                _normalize_item(it, fields, index=idx)
                for idx, it in enumerate(items[:6])
            ]

            # Crear o recuperar GeneratedSite
            site, created = GeneratedSite.objects.get_or_create(
                project_source=api_request,
                defaults={"accepted_plan": plan},
            )

            plan_changed = site.accepted_plan != plan
            if plan_changed:
                site.accepted_plan = plan

            # Generar tema si no existe o si cambió el plan
            if (not site.theme_templates) or plan_changed:
                theme = generate_site_theme(
                    site_title=site_title,
                    site_type=site_type,
                    design_hint=site_title,
                    fields=fields,
                    sample_items=sample_items,
                    retries=1,
                )
                site.theme_templates = {
                    "base_html":   theme["base_html"],
                    "home_html":   theme["home_html"],
                    "detail_html": theme["detail_html"],
                }
                site.theme_css = theme.get("css", "")
                site.theme_prompt = site_title

            site.save()
            messages.success(request, "Plan aceptado y sitio publicado ✅")
            return redirect("site_render", api_request_id=api_request.id)

    # ──────────────── GET — construir contexto ────────────────────────
    fields = plan.get("fields") or []
    preview_items = [_normalize_item(it, fields, index=idx) for idx, it in enumerate(items)]
    site_obj = getattr(api_request, "site", None)

    # Keys disponibles que aún no están en el schema (para poder añadirlas)
    used_keys = {f["key"] for f in fields}
    unused_keys = [k for k in available_keys if k not in used_keys]

    return render(
        request,
        "WebBuilder/edit.html",
        {
            "api_request":    api_request,
            "plan":           plan,
            "analysis":       analysis,
            "main_path":      main_path,
            "available_keys": available_keys,
            "unused_keys":    unused_keys,
            "preview_items":  preview_items,
            "site_obj":       site_obj,
        },
    )
