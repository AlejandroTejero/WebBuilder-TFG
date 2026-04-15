"""
Vistas del asistente — Fase 2: análisis + schema dinámico con LLM.

Flujo:
  1. El usuario introduce una URL + (opcional) un prompt.
  2. Se descarga y parsea (JSON/XML).
  3. Se analiza la estructura (main_collection_path, available_keys).
  4. El LLM devuelve un schema dinámico validado y se guarda en BD.

Nuevo schema (field_mapping):
  {
    "site_type": str,
    "site_title": str,
    "fields": [{"key": str, "label": str}, ...],
    "user_prompt": str,
  }
"""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from ..forms import APIRequestForm
from ..models import APIRequest
from ..utils.analysis import build_analysis
from ..utils.analysis.helpers import get_by_path
from ..utils.ingest.parsers import parse_raw, summarize_data
from ..utils.ingest.url_reader import fetch_url, read_file
from ..utils.llm.client import LLMError
from ..utils.llm.llm_catalog import LLM_CATALOG
from ..utils.llm.planner import PlanError, generate_site_plan


# ────────────────────────── CONFIG ──────────────────────────────────

CACHE_TIMEOUT = 3600  # 1h
CACHE_KEY_PREFIX = "api_analysis"


# ────────────────────────── HELPERS LLM ─────────────────────────────

def _resolve_llm(user, llm_choice: str) -> tuple[str, str, str]:
    """
    Devuelve (model, base_url, api_key) según la elección del usuario.
    - Si es un modelo del catálogo, usa la api_key del .env.
    - Si es 'custom', usa los datos del perfil del usuario.
    """
    if llm_choice == "default" or not llm_choice:
        llm_choice = LLM_CATALOG[0]["id"]

    if llm_choice == "custom":
        profile = getattr(user, "profile", None)
        if not profile or not profile.custom_llm_model:
            raise ValueError("No tienes un modelo personalizado configurado en tu perfil.")
        return (
            profile.custom_llm_model,
            profile.custom_llm_base_url,
            profile.custom_llm_api_key,
        )

    catalog_entry = next((m for m in LLM_CATALOG if m["id"] == llm_choice), None)
    if not catalog_entry:
        raise ValueError(f"Modelo '{llm_choice}' no encontrado en el catálogo.")

    from django.conf import settings

    return (
        catalog_entry["id"],
        catalog_entry["base_url"],
        settings.LLM_API_KEY,
    )


def _call_llm_plan(
    *,
    api_request_obj: APIRequest,
    analysis_result: dict,
    parsed_payload: object,
    user_prompt: str,
    llm_model: str,
    llm_base_url: str,
    llm_api_key: str,
) -> tuple[dict | None, str | None]:
    """
    Genera el schema dinámico y lo guarda en api_request.field_mapping.

    Importante:
    - El prompt del usuario se persiste dentro del plan para que la fase de
      generación final pueda reutilizarlo.
    """
    main = analysis_result.get("main_collection") or {}
    keys = analysis_result.get("keys") or {}

    available_keys = (keys.get("all") or [])[:50]
    main_path = main.get("path")
    examples = _build_examples(parsed_payload, main_path=main_path, available_keys=available_keys)

    try:
        plan = generate_site_plan(
            user_prompt=user_prompt or "",
            available_keys=available_keys,
            examples=examples,
            main_collection_path=main_path,
            retries=1,
            model=llm_model,
            base_url=llm_base_url,
            api_key=llm_api_key,
        )

        if isinstance(plan, dict):
            plan["user_prompt"] = (user_prompt or "").strip()

        api_request_obj.field_mapping = plan
        if hasattr(api_request_obj, "plan_accepted"):
            api_request_obj.plan_accepted = False
            api_request_obj.save(update_fields=["field_mapping", "plan_accepted"])
        else:
            api_request_obj.save(update_fields=["field_mapping"])

        return plan, None
    except (PlanError, LLMError) as e:
        return None, str(e)


# ────────────────────────── HELPERS DE DATOS ────────────────────────

def _get_cache_key(api_url: str) -> str:
    url_hash = hashlib.md5(api_url.encode("utf-8")).hexdigest()
    return f"{CACHE_KEY_PREFIX}:{url_hash}"


def _truncate_value(v: object, *, max_len: int = 220) -> object:
    if v is None:
        return None
    if isinstance(v, (int, float, bool)):
        return v
    if isinstance(v, str):
        s = v.strip()
        return s if len(s) <= max_len else (s[: max_len - 3] + "...")
    try:
        s = json.dumps(v, ensure_ascii=False)
    except Exception:
        s = str(v)
    return s if len(s) <= max_len else (s[: max_len - 3] + "...")


def _build_examples(
    parsed_payload: object,
    *,
    main_path: list | None,
    available_keys: list[str],
) -> list[dict]:
    if not main_path:
        return []

    items = get_by_path(parsed_payload, main_path)
    if not isinstance(items, list):
        return []

    out: list[dict] = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue
        keys = (available_keys or list(item.keys()))[:20]
        out.append({k: _truncate_value(item.get(k)) for k in keys if k in item})
    return out


def _build_preview_items(
    parsed_data: object,
    analysis: dict | None,
    plan: dict | None,
    *,
    max_items: int = 3,
) -> list[dict]:
    """
    Extrae hasta max_items items del dataset normalizados con los fields del plan.
    Devuelve lista de dicts {key: str_value, ...} listos para el template.
    """
    if not parsed_data or not plan:
        return []

    fields = plan.get("fields") or []
    if not fields:
        return []

    main = (analysis or {}).get("main_collection") or {}
    main_path = main.get("path")
    if main_path is None:
        return []

    raw_items = get_by_path(parsed_data, main_path)
    if not isinstance(raw_items, list):
        return []

    result = []
    for raw in raw_items[:max_items]:
        if not isinstance(raw, dict):
            continue
        item: dict = {}
        for field in fields:
            key = field.get("key", "")
            val = raw.get(key)
            if val is None:
                continue
            if isinstance(val, (int, float, bool)):
                item[key] = str(val)
            elif isinstance(val, str):
                item[key] = val.strip()
            else:
                try:
                    item[key] = json.dumps(val, ensure_ascii=False)
                except Exception:
                    item[key] = str(val)
        result.append(item)

    return result


# ────────────────────────── RENDER ──────────────────────────────────

def render_assistant(
    request,
    *,
    form: APIRequestForm,
    api_request: APIRequest | None = None,
    analysis: dict | None = None,
    llm_plan_text: str | None = None,
    llm_plan: dict | None = None,
    llm_error: str | None = None,
    selected_llm_choice: str | None = None,
    template: str = "WebBuilder/assistant.html",
):
    default_llm_choice = LLM_CATALOG[0]["id"] if LLM_CATALOG else ""

    context = {
        "form": form,
        "llm_catalog": LLM_CATALOG,
        "selected_llm_choice": selected_llm_choice or default_llm_choice,
    }
    if api_request is not None:
        context["api_request"] = api_request
    if analysis is not None:
        context["analysis"] = analysis
    if llm_plan_text is not None:
        context["llm_plan_text"] = llm_plan_text
    if llm_plan is not None:
        context["llm_plan"] = llm_plan
    if llm_error is not None:
        context["llm_error"] = llm_error

    if api_request is not None and llm_plan is not None:
        context["preview_items"] = _build_preview_items(
            api_request.parsed_data,
            analysis,
            llm_plan,
        )

    return render(request, template, context)


# ────────────────────────── GET ─────────────────────────────────────

@login_required
def get_assistant(request):
    """
    - Modo vacío: muestra formulario.
    - Modo reabrir: ?api_request_id=... carga desde BD y reconstruye analysis.
    """
    form = APIRequestForm()
    api_request_id = request.GET.get("api_request_id")

    if not api_request_id:
        return render_assistant(request, form=form)

    api_request = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
    if not api_request:
        messages.error(request, "No se encontró ese análisis en tu cuenta.")
        return render_assistant(request, form=form)

    analysis = None
    saved_prompt = ""
    if api_request.field_mapping and isinstance(api_request.field_mapping, dict):
        saved_prompt = (api_request.field_mapping.get("user_prompt") or "").strip()

    if api_request.parsed_data:
        analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
        form = APIRequestForm(initial={
            "api_url": api_request.api_url,
            "user_prompt": saved_prompt,
        })

    llm_plan_text = None
    if api_request.field_mapping:
        llm_plan_text = json.dumps(api_request.field_mapping, ensure_ascii=False, indent=2)

    return render_assistant(
        request,
        form=form,
        api_request=api_request,
        analysis=analysis,
        llm_plan_text=llm_plan_text,
        llm_plan=api_request.field_mapping,
    )


# ────────────────────────── POST ────────────────────────────────────

@login_required
def analyze_url(request):
    if request.method != "POST":
        return redirect("assistant")

    action = (request.POST.get("action") or "analyze").strip().lower()
    api_request_id = (request.POST.get("api_request_id") or "").strip()

    # ── Acciones sobre análisis existente ───────────────────────────
    if action in {"regenerate", "accept_plan"}:
        api_request_obj = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
        if not api_request_obj:
            messages.error(request, "No se encontró ese análisis en tu cuenta.")
            return redirect("assistant")

        if action == "accept_plan":
            if not api_request_obj.field_mapping:
                messages.error(request, "Aún no hay un plan válido para aceptar.")
                return redirect(reverse("assistant") + f"?api_request_id={api_request_obj.id}")

            if hasattr(api_request_obj, "plan_accepted"):
                api_request_obj.plan_accepted = True
                api_request_obj.save(update_fields=["plan_accepted"])
            messages.success(request, "Plan aceptado ✅")
            return redirect(reverse("assistant") + f"?api_request_id={api_request_obj.id}")

        # action == regenerate
        form = APIRequestForm(request.POST)
        user_prompt = (form.data.get("user_prompt") or "").strip()

        llm_choice = request.POST.get("llm_choice", "")
        try:
            llm_model, llm_base_url, llm_api_key = _resolve_llm(request.user, llm_choice)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("assistant")

        analysis_result = build_analysis(api_request_obj.parsed_data, raw_text=api_request_obj.raw_data or "")

        llm_plan, llm_error = _call_llm_plan(
            api_request_obj=api_request_obj,
            analysis_result=analysis_result,
            user_prompt=user_prompt,
            parsed_payload=api_request_obj.parsed_data,
            llm_model=llm_model,
            llm_base_url=llm_base_url,
            llm_api_key=llm_api_key,
        )

        if llm_plan is not None:
            messages.success(request, "Schema regenerado ✅")

        form = APIRequestForm(initial={"api_url": api_request_obj.api_url, "user_prompt": user_prompt})
        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            llm_plan_text=json.dumps(llm_plan, ensure_ascii=False, indent=2) if llm_plan else None,
            llm_plan=llm_plan,
            llm_error=llm_error,
            selected_llm_choice=llm_choice,
        )

    # ── Análisis normal ─────────────────────────────────────────────
    form = APIRequestForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Por favor corrige los errores del formulario.")
        return render_assistant(request, form=form)

    llm_choice = request.POST.get("llm_choice", "")
    try:
        llm_model, llm_base_url, llm_api_key = _resolve_llm(request.user, llm_choice)
    except ValueError as e:
        messages.error(request, str(e))
        return render_assistant(request, form=form)

    api_url = form.cleaned_data["api_url"]
    user_prompt = (form.cleaned_data.get("user_prompt") or "").strip()

    cache_key = _get_cache_key(api_url)
    cached_data = cache.get(cache_key)

    # ── CACHE HIT ───────────────────────────────────────────────────
    if cached_data:
        messages.info(request, "⚡ Análisis cargado desde caché (datos recientes).")

        one_hour_ago = timezone.now() - timedelta(hours=1)
        api_request_obj = (
            APIRequest.objects.filter(user=request.user, api_url=api_url, date__gte=one_hour_ago)
            .order_by("-date")
            .first()
        )

        if not api_request_obj:
            api_request_obj = APIRequest.objects.create(
                user=request.user,
                api_url=api_url,
                raw_data=cached_data["raw_text"],
                parsed_data=cached_data["parsed_payload"],
                response_summary=cached_data["response_summary"],
                status="processed",
                error_message="",
            )

        analysis_result = build_analysis(
            cached_data["parsed_payload"],
            raw_text=cached_data["raw_text"],
        )

        llm_plan, llm_error = _call_llm_plan(
            api_request_obj=api_request_obj,
            analysis_result=analysis_result,
            parsed_payload=cached_data["parsed_payload"],
            user_prompt=user_prompt,
            llm_model=llm_model,
            llm_base_url=llm_base_url,
            llm_api_key=llm_api_key,
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            llm_plan_text=json.dumps(llm_plan, ensure_ascii=False, indent=2) if llm_plan else None,
            llm_plan=llm_plan,
            llm_error=llm_error,
            selected_llm_choice=llm_choice,
        )

    # ── CACHE MISS ──────────────────────────────────────────────────
    api_request_obj = APIRequest.objects.create(
        user=request.user,
        api_url=api_url,
        status="pending",
    )
    uploaded_file = request.FILES.get("file_input")

    try:
        if uploaded_file:
            raw_text, fetch_summary = read_file(uploaded_file)
            api_request_obj.input_type = "file"
        else:
            raw_text, fetch_summary = fetch_url(api_url)
            api_request_obj.input_type = "url"

        fmt, parsed_payload = parse_raw(raw_text)

        analysis_result = build_analysis(parsed_payload, raw_text=raw_text)
        parse_summary = summarize_data(fmt, parsed_payload)
        response_summary = f"{fetch_summary} {parse_summary}"

        api_request_obj.raw_data = raw_text
        api_request_obj.parsed_data = parsed_payload
        api_request_obj.response_summary = response_summary
        api_request_obj.status = "processed"
        api_request_obj.error_message = ""
        api_request_obj.save()

        cache.set(
            cache_key,
            {
                "raw_text": raw_text,
                "parsed_payload": parsed_payload,
                "response_summary": response_summary,
            },
            CACHE_TIMEOUT,
        )

        messages.success(request, "URL descargada, parseada y analizada correctamente.")

        llm_plan, llm_error = _call_llm_plan(
            api_request_obj=api_request_obj,
            analysis_result=analysis_result,
            parsed_payload=parsed_payload,
            user_prompt=user_prompt,
            llm_model=llm_model,
            llm_base_url=llm_base_url,
            llm_api_key=llm_api_key,
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            llm_plan_text=json.dumps(llm_plan, ensure_ascii=False, indent=2) if llm_plan else None,
            llm_plan=llm_plan,
            llm_error=llm_error,
            selected_llm_choice=llm_choice,
        )

    except Exception as exc:
        api_request_obj.status = "error"
        api_request_obj.error_message = str(exc)
        api_request_obj.response_summary = "Error al descargar, parsear o analizar la URL."
        api_request_obj.save()

        messages.error(request, f"No se pudo procesar la URL: {exc}")
        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis={"error": str(exc)},
            llm_error=str(exc),
            selected_llm_choice=llm_choice,
        )


# ────────────────────────── VISTA PRINCIPAL ─────────────────────────

@login_required
def assistant(request):
    if request.method == "GET":
        return get_assistant(request)
    if request.method == "POST":
        return analyze_url(request)
    return HttpResponseNotAllowed(["GET", "POST"])