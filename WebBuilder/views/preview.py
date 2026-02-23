from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import APIRequest, GeneratedSite
from ..utils.analysis import build_analysis
from ..utils.analysis.helpers import get_by_path
from ..utils.llm.themer import generate_site_theme


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

    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def normalize_item(item: Any, plan: dict) -> dict:
    """
    Convierte un item (dict) en un objeto normalizado para UI usando plan["mapping"].
    mapping: {title/content/image/date} con keys o None
    """
    mapping = (plan or {}).get("mapping") or {}

    if not isinstance(item, dict):
        return {"title": "", "content": "", "image": "", "date": "", "raw": _to_text(item, max_len=220)}

    def pick(field: str) -> Any:
        key = mapping.get(field)
        if not key:
            return None
        return item.get(key)

    title = _to_text(pick("title"), max_len=80) or "(sin título)"
    content = _to_text(pick("content"), max_len=220)
    image = _to_text(pick("image"), max_len=300)
    date = _to_text(pick("date"), max_len=60)

    return {
        "title": title,
        "content": content,
        "image": image,
        "date": date,
        "raw": None,
    }


def _normalize_selected_key(value: str | None, available_keys: list[str]) -> str | None:
    """
    Convierte el valor del <select> en una key válida o None.
    """
    if value is None:
        return None
    v = value.strip()
    if not v or v.lower() == "null":
        return None
    return v if v in available_keys else None


def _normalize_site_type(value: str | None) -> str:
    allowed = {"blog", "portfolio", "catalog", "dashboard", "other"}
    v = (value or "").strip().lower()
    return v if v in allowed else "other"


@login_required
def preview(request, api_request_id: int):
    api_request = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
    if not api_request:
        messages.error(request, "No se encontró ese análisis en tu cuenta.")
        return redirect("assistant")

    plan = api_request.field_mapping
    if not plan:
        messages.error(request, "Este análisis no tiene plan del LLM todavía.")
        return redirect(f"/asistente?api_request_id={api_request.id}")

    if not api_request.parsed_data:
        messages.error(request, "Este análisis no tiene datos parseados.")
        return redirect(f"/asistente?api_request_id={api_request.id}")

    # Normalizar plan
    if not isinstance(plan, dict):
        plan = {}
    plan.setdefault("mapping", {})
    if not isinstance(plan["mapping"], dict):
        plan["mapping"] = {}

    # Recalcular analysis para sacar main_path + available_keys
    analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
    main = analysis.get("main_collection") or {}
    main_path = main.get("path")

    keys_info = analysis.get("keys") or {}
    available_keys = (keys_info.get("top") or [])[:30]

    # Items para preview + samples (los calculamos antes para poder usarlos en POST accept_plan)
    items = []
    if main_path is not None:
        node = get_by_path(api_request.parsed_data, main_path)
        if isinstance(node, list):
            items = node[:12]

    # ---------- POST ----------
    if request.method == "POST":
        action = (request.POST.get("action") or "").strip().lower()

        # Guardar cambios del plan
        if action == "save_mapping":
            selected_site_type = _normalize_site_type(request.POST.get("site_type"))
            custom_site_type = (request.POST.get("site_type_custom") or "").strip()

            plan["site_type"] = selected_site_type
            if custom_site_type:
                plan["site_type_custom"] = custom_site_type
            else:
                plan.pop("site_type_custom", None)

            new_mapping = {
                "title": _normalize_selected_key(request.POST.get("map_title"), available_keys),
                "content": _normalize_selected_key(request.POST.get("map_content"), available_keys),
                "image": _normalize_selected_key(request.POST.get("map_image"), available_keys),
                "date": _normalize_selected_key(request.POST.get("map_date"), available_keys),
            }
            plan["mapping"] = new_mapping

            api_request.field_mapping = plan

            # ✅ Importante: si cambias el plan, ya NO está aceptado
            api_request.plan_accepted = False

            api_request.save(update_fields=["field_mapping", "plan_accepted"])
            messages.success(request, "Plan actualizado ✅ (vuelve a aceptar para publicar)")
            return redirect("preview", api_request_id=api_request.id)

        # Aceptar plan + publicar (generar theme y crear GeneratedSite)
        if action == "accept_plan":
            api_request.plan_accepted = True
            api_request.save(update_fields=["plan_accepted"])

            mapping = (plan.get("mapping") or {}) if isinstance(plan, dict) else {}
            pages = (plan.get("pages") or []) if isinstance(plan, dict) else []
            site_type = (plan.get("site_type") or "other") if isinstance(plan, dict) else "other"
            design_hint = (plan.get("site_type_custom") or "").strip() if isinstance(plan, dict) else ""

            # sample items normalizados para pasar al LLM
            sample_items = []
            for idx, it in enumerate(items[:6]):
                if not isinstance(it, dict):
                    continue

                def pick(field: str, max_len: int) -> str:
                    key = mapping.get(field)
                    return _to_text(it.get(key), max_len=max_len) if key else ""

                sample_items.append(
                    {
                        "index": idx,
                        "title": pick("title", 80),
                        "content": pick("content", 180),
                        "image": pick("image", 200),
                        "date": pick("date", 60),
                    }
                )

            # crear o recuperar site publicado
            site, created = GeneratedSite.objects.get_or_create(
                project_source=api_request,
                defaults={"accepted_plan": plan},
            )

            plan_changed = site.accepted_plan != plan
            if plan_changed:
                site.accepted_plan = plan

            # genera theme si no existe o si cambió el plan
            if (not site.theme_templates) or plan_changed:
                theme = generate_site_theme(
                    site_title=design_hint or site_type,
                    site_type=site_type,
                    design_hint=design_hint,
                    pages=pages,
                    mapping=mapping,
                    sample_items=sample_items,
                    retries=1,
                )
                site.theme_templates = {
                    "base_html": theme["base_html"],
                    "home_html": theme["home_html"],
                    "detail_html": theme["detail_html"],
                }
                site.theme_css = theme.get("css", "")
                site.theme_prompt = design_hint

            site.save()
            messages.success(request, "Plan aceptado y sitio publicado ✅")
            return redirect("site_home", site_id=site.id)

    # ---------- Construir items para preview ----------
    preview_items = [normalize_item(it, plan) for it in items]
    site_obj = getattr(api_request, "site", None)
    
    return render(
        request,
        "WebBuilder/preview.html",
        {
            "api_request": api_request,
            "plan": plan,
            "analysis": analysis,
            "main_path": main_path,
            "available_keys": available_keys,
            "preview_items": preview_items,
            "site_obj": site_obj,
        },
    )