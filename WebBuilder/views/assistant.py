"""
Vistas del asistente (Fase 2 - análisis + plan JSON con LLM)
Flujo:
- El usuario introduce una URL + (opcional) un prompt
- Se descarga + parsea (JSON/XML)
- Se analiza la estructura y se guarda en BD
- Si hay prompt: el LLM devuelve SOLO JSON (plan) validado y se guarda en BD
"""

from __future__ import annotations

import hashlib
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect

from ..forms import APIRequestForm
from ..models import APIRequest
from ..utils.ingest.url_reader import fetch_url
from ..utils.ingest.parsers import parse_raw, summarize_data
from ..utils.analysis import build_analysis
from ..utils.analysis.helpers import get_by_path

from ..utils.llm.client import LLMError
from ..utils.llm.planner import generate_site_plan, PlanError

# ============================== CONFIG ==============================

CACHE_TIMEOUT = 3600  # 1h
CACHE_KEY_PREFIX = "api_analysis"


def _get_cache_key(api_url: str) -> str:
    url_hash = hashlib.md5(api_url.encode("utf-8")).hexdigest()
    return f"{CACHE_KEY_PREFIX}:{url_hash}"


# ============================== RENDER ==============================

def render_assistant(
    request,
    *,
    form: APIRequestForm,
    api_request: APIRequest | None = None,
    analysis: dict | None = None,
    llm_plan_text: str | None = None,
    llm_plan: dict | None = None,
    llm_error: str | None = None,
    template: str = "WebBuilder/assistant.html",
):
    context = {"form": form}

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

    return render(request, template, context)


# ============================== GET ==============================

def get_assistant(request):
    """
    - Modo vacío: muestra formulario
    - Modo reabrir: ?api_request_id=... carga desde BD y reconstruye analysis
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
    if api_request.parsed_data:
        analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
        form = APIRequestForm(initial={"api_url": api_request.api_url})

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


# ============================== POST ==============================

@login_required
def analyze_url(request):
    if request.method != "POST":
        return redirect("assistant")  # en tus urls el name es "assistant"

    action = (request.POST.get("action") or "analyze").strip().lower()
    api_request_id = (request.POST.get("api_request_id") or "").strip()

    def _truncate_value(v: object, *, max_len: int = 220) -> object:
        if v is None:
            return None
        if isinstance(v, (int, float, bool)):
            return v
        if isinstance(v, str):
            s = v.strip()
            return s if len(s) <= max_len else (s[: max_len - 3] + "...")
        # dict/list/other -> string compacta
        try:
            s = json.dumps(v, ensure_ascii=False)
        except Exception:
            s = str(v)
        return s if len(s) <= max_len else (s[: max_len - 3] + "...")

    def _build_examples(parsed_payload: object, *, main_path: list | None, available_keys: list[str]) -> list[dict]:
        """
        Coge 1-3 items del array principal y recorta a keys frecuentes.
        """
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

    def _call_llm_plan(
        *,
        api_request_obj: APIRequest,
        analysis_result: dict,
        parsed_payload: object,
        user_prompt: str,
    ) -> tuple[dict | None, str | None]:
        """
        Genera el plan JSON validado y lo guarda en api_request.field_mapping.
        """
        user_prompt = user_prompt or ""
        
        main = (analysis_result.get("main_collection") or {})
        keys = (analysis_result.get("keys") or {})
        #available_keys = (keys.get("top") or [])
        available_keys = (keys.get("top") or [])[:30]
        main_path = main.get("path")

        examples = _build_examples(parsed_payload, main_path=main_path, available_keys=available_keys)

        try:
            plan = generate_site_plan(
                user_prompt=user_prompt,
                available_keys=available_keys,
                examples=examples,
                main_collection_path=main_path,
                retries=1,
            )

            api_request_obj.field_mapping = plan
            # si tienes plan_accepted en el modelo, lo reseteamos al regenerar
            if hasattr(api_request_obj, "plan_accepted"):
                api_request_obj.plan_accepted = False
                api_request_obj.save(update_fields=["field_mapping", "plan_accepted"])
            else:
                api_request_obj.save(update_fields=["field_mapping"])

            return plan, None
        except (PlanError, LLMError) as e:
            return None, str(e)

    # ===================== Acciones sobre un análisis existente =====================
    if action in {"regenerate", "accept_plan"}:
        api_request_obj = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
        if not api_request_obj:
            messages.error(request, "No se encontró ese análisis en tu cuenta.")
            return redirect("assistant")

        if action == "accept_plan":
            if not api_request_obj.field_mapping:
                messages.error(request, "Aún no hay un plan válido para aceptar.")
                return redirect(f"/asistente?api_request_id={api_request_obj.id}")

            if hasattr(api_request_obj, "plan_accepted"):
                api_request_obj.plan_accepted = True
                api_request_obj.save(update_fields=["plan_accepted"])
            messages.success(request, "Plan aceptado ✅")
            return redirect(f"/asistente?api_request_id={api_request_obj.id}")

        # action == regenerate
        form = APIRequestForm(request.POST)
        user_prompt = (form.data.get("user_prompt") or "").strip()
        analysis_result = build_analysis(api_request_obj.parsed_data, raw_text=api_request_obj.raw_data or "")

        llm_plan, llm_error = _call_llm_plan(
            api_request_obj=api_request_obj,
            analysis_result=analysis_result,
            user_prompt=user_prompt,
            parsed_payload=api_request_obj.parsed_data,
        )

        if llm_plan is not None:
            messages.success(request, "Plan regenerado ✅")

        form = APIRequestForm(initial={"api_url": api_request_obj.api_url, "user_prompt": user_prompt})
        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            llm_plan_text=json.dumps(llm_plan, ensure_ascii=False, indent=2) if llm_plan else None,
            llm_plan=llm_plan,
            llm_error=llm_error,
        )

    # ===================== Análisis (flujo normal) =====================
    form = APIRequestForm(request.POST)
    if not form.is_valid():
        messages.error(request, "La URL no es válida (incluye http:// o https://).")
        return render_assistant(request, form=form)

    api_url = form.cleaned_data["api_url"]
    user_prompt = (form.cleaned_data.get("user_prompt") or "").strip()

    cache_key = _get_cache_key(api_url)
    cached_data = cache.get(cache_key)

    # -------- CACHE HIT --------
    if cached_data:
        messages.info(request, "⚡ Análisis cargado desde caché (datos recientes).")

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
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            llm_plan_text=json.dumps(llm_plan, ensure_ascii=False, indent=2) if llm_plan else None,
            llm_plan=llm_plan,
            llm_error=llm_error,
        )

    # -------- CACHE MISS --------
    api_request_obj = APIRequest.objects.create(
        user=request.user,
        api_url=api_url,
        status="pending",
    )

    try:
        raw_text, fetch_summary = fetch_url(api_url)
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
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            llm_plan_text=json.dumps(llm_plan, ensure_ascii=False, indent=2) if llm_plan else None,
            llm_plan=llm_plan,
            llm_error=llm_error,
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
        )


# ============================== VISTA PRINCIPAL ==============================

@login_required
def assistant(request):
    if request.method == "GET":
        return get_assistant(request)

    if request.method == "POST":
        return analyze_url(request)

    return HttpResponseNotAllowed(["GET", "POST"])