"""
Vistas del asistente (wizard de generación de webs)
Maneja el flujo completo: análisis, mapping, preview
"""

from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache  # ✨ Sistema de caché de Django

import hashlib

from ..models import APIRequest
from ..forms import APIRequestForm
from ..utils.url_reader import fetch_url
from ..utils.parsers import parse_raw, summarize_data
from ..utils.analysis import build_analysis, calculate_mapping_quality
from ..utils.intents import (
    get_profile,
    roles_for_intent,
    normalize_intent,
    sections_for_intent,
    role_ui,
)
from ..utils.mapping import (
    read_mapping,
    store_mapping,
    get_mapping,
    resolve_api_id,
    save_mapping_to_db,
    build_role_options,
    validate_mapping,
    get_intent,
    store_intent,
)


# ✨ Configuración de caché
CACHE_TIMEOUT = 3600  # 1 hora en segundos
CACHE_KEY_PREFIX = "api_analysis"


def _get_cache_key(api_url: str) -> str:
    """
    Genera una clave de caché única basada en la URL.

    Usa hash MD5 para evitar problemas con caracteres especiales en las keys.
    """
    url_hash = hashlib.md5(api_url.encode("utf-8")).hexdigest()
    return f"{CACHE_KEY_PREFIX}:{url_hash}"


# ============================== Helper de render ==============================

def render_assistant(
    request,
    *,
    form,
    api_request=None,
    analysis=None,
    role_options=None,
    saved_mapping=None,
    template="WebBuilder/assistant.html",
):
    """
    Renderiza la página del asistente con contexto consistente
    """
    if saved_mapping is None:
        saved_mapping = get_mapping(request)

    # Intención actual (para UI)
    mapping_intent = normalize_intent(get_intent(request))
    intent_profile = get_profile(mapping_intent)

    context = {
        "form": form,
        "saved_mapping": saved_mapping,
        "mapping_intent": mapping_intent,
        "intent_profile": intent_profile,
    }

    # Calcula calidad del mapping si hay datos
    if saved_mapping and analysis is not None:
        mapping_quality = calculate_mapping_quality(saved_mapping, analysis)
        context["mapping_quality"] = mapping_quality

    if api_request is not None:
        context["api_request"] = api_request
    if analysis is not None:
        context["analysis"] = analysis
    if role_options is not None:
        context["role_options"] = role_options

    return render(request, template, context)


def _build_role_options_for_ui(request, analysis: dict, mapping: dict) -> list[dict]:
    """
    Construye role_options enriquecido con:
    - orden guiado por intención (si aplica)
    - secciones (required/recommended/optional/other)
    - labels/help humanos
    """
    intent_key = normalize_intent(get_intent(request))
    ordered_roles = roles_for_intent(intent_key) or None

    # Si no hay ordered_roles (custom), usa el orden por defecto del analysis
    roles_for_ui = ordered_roles or (analysis.get("roles", []) or [])

    role_sections = sections_for_intent(intent_key, roles_for_ui)
    role_ui_map = {r: role_ui(r) for r in roles_for_ui}

    return build_role_options(
        analysis,
        mapping,
        roles=ordered_roles,
        role_sections=role_sections,
        role_ui_map=role_ui_map,
    )


# ============================== GET del asistente ==============================

def get_assistant(request):
    """
    Maneja el GET del asistente

    Si viene api_request_id en querystring, carga ese análisis específico
    Si no, muestra el formulario vacío
    """
    form = APIRequestForm()
    api_request_id = request.GET.get("api_request_id")

    # Modo reabrir 
    if api_request_id:
        api_request = APIRequest.objects.filter(id=api_request_id, user=request.user).first()

        if not api_request:
            messages.error(request, "No se encontró ese análisis en tu cuenta.")
            return render_assistant(request, form=form)

        # Mapping: preferimos el guardado en BD; si no, sesión
        saved_mapping = api_request.field_mapping or get_mapping(request)

        analysis = None
        role_options = []

        if api_request.parsed_data:
            analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
            role_options = _build_role_options_for_ui(request, analysis, saved_mapping)
            form = APIRequestForm(initial={"api_url": api_request.api_url})

        return render_assistant(
            request,
            form=form,
            api_request=api_request,
            analysis=analysis,
            role_options=role_options,
            saved_mapping=saved_mapping,
        )

    # Modo vacio
    saved_mapping = get_mapping(request)
    return render_assistant(request, form=form, saved_mapping=saved_mapping)


# ============================== POST: set intent ==============================

def set_intent(request):
    """Guarda la intención (tipo de web) en sesión y re-renderiza el asistente."""
    intent = normalize_intent(request.POST.get("intent"))
    store_intent(request, intent)

    api_request_id = resolve_api_id(
        request,
        post_api_request_id=request.POST.get("api_request_id"),
    )

    api_request_obj = None
    analysis_result = None
    role_select_options = []

    if api_request_id:
        api_request_obj = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
        if api_request_obj and api_request_obj.parsed_data:
            analysis_result = build_analysis(
                api_request_obj.parsed_data,
                raw_text=api_request_obj.raw_data or "",
            )
            role_select_options = _build_role_options_for_ui(
                request,
                analysis_result,
                get_mapping(request),
            )

    form = APIRequestForm(initial={"api_url": api_request_obj.api_url if api_request_obj else ""})

    messages.success(request, f"Tipo de web seleccionado: {get_profile(intent).label}")

    return render_assistant(
        request,
        form=form,
        api_request=api_request_obj,
        analysis=analysis_result,
        role_options=role_select_options,
        saved_mapping=get_mapping(request),
    )


# ============================== POST: guardar mapping ==============================

def save_mapping(request):
    """
    Guarda el mapping configurado en el paso 2

    Valida el mapping, lo guarda en sesión y en BD si es posible,
    y re-renderiza el asistente con los resultados
    """
    field_mapping = read_mapping(request.POST)

    analysis_for_validation = None
    api_request_id = resolve_api_id(
        request,
        post_api_request_id=request.POST.get("api_request_id"),
    )

    api_request_for_validation = None
    if api_request_id:
        api_request_for_validation = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
        if api_request_for_validation and api_request_for_validation.parsed_data:
            analysis_for_validation = build_analysis(
                api_request_for_validation.parsed_data,
                raw_text=api_request_for_validation.raw_data or "",
            )

    validation = validate_mapping(
        field_mapping,
        analysis_result=analysis_for_validation,
        required_roles=("title",),
        prevent_duplicates_in=("title", "description", "subtitle", "content", "author"),
        allow_duplicate_in=("id", "link", "date", "category", "tags"),
    )

    field_mapping = validation["cleaned"]
    store_mapping(request, field_mapping)

    if not validation["ok"]:
        for msg in validation["errors"]:
            messages.error(request, msg)

        role_select_options = []
        if analysis_for_validation:
            role_select_options = _build_role_options_for_ui(
                request,
                analysis_for_validation,
                field_mapping,
            )

        form = APIRequestForm(
            initial={"api_url": api_request_for_validation.api_url if api_request_for_validation else ""}
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_for_validation,
            analysis=analysis_for_validation,
            role_options=role_select_options,
            saved_mapping=field_mapping,
        )

    for msg in validation["warnings"]:
        messages.warning(request, msg)

    api_request_obj = save_mapping_to_db(
        user=request.user,
        api_request_id=api_request_id,
        field_mapping=field_mapping,
    )

    if api_request_obj:
        messages.success(request, "Mapping guardado en sesión y en base de datos.")
    elif api_request_id:
        messages.warning(request, "No se encontró el APIRequest. Mapping guardado solo en sesión.")
    else:
        messages.warning(request, "No llegó api_request_id ni hay last_api_request_id. Guardado solo en sesión.")

    analysis_result = None
    role_select_options = []

    if api_request_obj and api_request_obj.parsed_data:
        analysis_result = build_analysis(api_request_obj.parsed_data, raw_text=api_request_obj.raw_data or "")
        role_select_options = _build_role_options_for_ui(
            request,
            analysis_result,
            field_mapping,
        )

    form = APIRequestForm(initial={"api_url": api_request_obj.api_url if api_request_obj else ""})

    return render_assistant(
        request,
        form=form,
        api_request=api_request_obj,
        analysis=analysis_result,
        role_options=role_select_options,
        saved_mapping=field_mapping,
    )


# ============================== POST: analizar URL (CON CACHÉ) ==============================

def analyze_url(request):
    """
    Analiza una URL (descarga + parsea + analiza + guarda en BD)

    MEJORAS:
    - Sistema de caché: Si la URL ya fue analizada recientemente (< 1h),
      usa los datos cacheados en vez de descargar de nuevo
    """
    form = APIRequestForm(request.POST)

    if not form.is_valid():
        messages.error(request, "La URL no es válida (incluye http:// o https://).")
        return render_assistant(request, form=form)

    api_url = form.cleaned_data["api_url"]

    cache_key = _get_cache_key(api_url)
    cached_data = cache.get(cache_key)

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

        saved_mapping = get_mapping(request)
        role_select_options = _build_role_options_for_ui(
            request,
            analysis_result,
            saved_mapping,
        )

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            role_options=role_select_options,
            saved_mapping=saved_mapping,
        )

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

        saved_mapping = get_mapping(request)
        role_select_options = _build_role_options_for_ui(
            request,
            analysis_result,
            saved_mapping,
        )

        messages.success(request, "URL descargada, parseada y analizada correctamente.")

        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            role_options=role_select_options,
            saved_mapping=saved_mapping,
        )

    except Exception as exc:
        api_request_obj.status = "error"
        api_request_obj.error_message = str(exc)
        api_request_obj.response_summary = "Error al descargar, parsear o analizar la URL."
        api_request_obj.save()

        messages.error(request, f"No se pudo procesar la URL: {exc}")
        return render_assistant(request, form=form)


# ============================== Vista principal ==============================

@login_required
def assistant(request):
    """
    Vista principal del asistente (router GET/POST)

    GET: Muestra la página del asistente (posiblemente con un análisis cargado)
    POST: Decide acción según el parámetro 'action':
          - 'set_intent': Guarda tipo de web (intención)
          - 'save_mapping': Guarda mapping
          - sin action: Analiza URL
    """
    if request.method == "GET":
        return get_assistant(request)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "set_intent":
            return set_intent(request)

        if action == "save_mapping":
            return save_mapping(request)

        return analyze_url(request)

    return HttpResponseNotAllowed(["GET", "POST"])
