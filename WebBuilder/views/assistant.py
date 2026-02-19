"""
Vistas del asistente (MVP - solo análisis)
Flujo actual:
- El usuario introduce una URL
- Se descarga + parsea (JSON/XML)
- Se analiza la estructura y se guarda en BD
- Se muestra un resumen del análisis

El mapping/intents/preview se implementarán con LLM en el siguiente paso.
"""

from __future__ import annotations

import hashlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseNotAllowed
from django.shortcuts import render

from ..forms import APIRequestForm
from ..models import APIRequest
from ..utils.ingest.url_reader import fetch_url
from ..utils.ingest.parsers import parse_raw, summarize_data
from ..utils.analysis import build_analysis


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
    template: str = "WebBuilder/assistant.html",
):
    context = {"form": form}

    if api_request is not None:
        context["api_request"] = api_request
    if analysis is not None:
        context["analysis"] = analysis

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

    return render_assistant(request, form=form, api_request=api_request, analysis=analysis)


# ============================== POST: analizar URL (con caché) ==============================

def analyze_url(request):
    form = APIRequestForm(request.POST)

    if not form.is_valid():
        messages.error(request, "La URL no es válida (incluye http:// o https://).")
        return render_assistant(request, form=form)

    api_url = form.cleaned_data["api_url"]
    cache_key = _get_cache_key(api_url)
    cached_data = cache.get(cache_key)

    # -------- Cache hit --------
    if cached_data:
        messages.info(
            request,
            "⚡ Análisis cargado desde caché (datos recientes). "
            "Si quieres forzar un nuevo análisis, espera 1 hora o cambia la URL ligeramente."
        )

        api_request_obj = APIRequest.objects.create(
            user=request.user,
            api_url=api_url,
            raw_data=cached_data["raw_text"],
            parsed_data=cached_data["parsed_payload"],
            response_summary=cached_data["response_summary"],
            status="processed",
            error_message="",
        )

        request.session["last_api_request_id"] = api_request_obj.id

        analysis_result = build_analysis(
            cached_data["parsed_payload"],
            raw_text=cached_data["raw_text"],
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
        )

    # -------- Cache miss --------
    api_request_obj = APIRequest.objects.create(
        user=request.user,
        api_url=api_url,
        status="pending",
    )

    try:
        raw_text, fetch_summary = fetch_url(api_url)
        data_format, parsed_payload = parse_raw(raw_text)

        analysis_result = build_analysis(parsed_payload, raw_text=raw_text)
        parse_summary = summarize_data(data_format, parsed_payload)

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

        request.session["last_api_request_id"] = api_request_obj.id

        messages.success(request, "URL descargada, parseada y analizada correctamente.")

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
        )

    except Exception as exc:
        api_request_obj.status = "error"
        api_request_obj.error_message = str(exc)
        api_request_obj.response_summary = "Error al descargar, parsear o analizar la URL."
        api_request_obj.save()

        messages.error(request, f"No se pudo procesar la URL: {exc}")
        return render_assistant(request, form=form)


# ============================== VISTA PRINCIPAL ==============================

@login_required
def assistant(request):
    if request.method == "GET":
        return get_assistant(request)

    if request.method == "POST":
        return analyze_url(request)

    return HttpResponseNotAllowed(["GET", "POST"])
