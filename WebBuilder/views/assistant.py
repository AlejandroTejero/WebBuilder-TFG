"""
Vistas del asistente (wizard de generación de webs)
Maneja el flujo completo: análisis, mapping, preview
"""

from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# ✨ NUEVO: Sistema de caché de Django
from django.core.cache import cache
import hashlib

from ..models import APIRequest
from ..forms import APIRequestForm
from ..utils.url_reader import fetch_url
from ..utils.parsers import parse_raw, summarize_data
from ..utils.analysis import build_analysis, calculate_mapping_quality
from ..utils.mapping import (
    read_mapping,
    store_mapping,
    get_mapping,
    resolve_api_id,
    save_mapping_to_db,
    build_role_options,
    validate_mapping,
)


# ✨ NUEVO: Configuración de caché
CACHE_TIMEOUT = 3600  # 1 hora en segundos
CACHE_KEY_PREFIX = "api_analysis"


# ✨ NUEVO: Función para generar clave de caché única por URL
def _get_cache_key(api_url: str) -> str:
    """
    Genera una clave de caché única basada en la URL.
    
    Usa hash MD5 para evitar problemas con caracteres especiales en las keys.
    """
    url_hash = hashlib.md5(api_url.encode('utf-8')).hexdigest()
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
    
    Args:
        request: Request de Django
        form: Formulario a pintar
        api_request: APIRequest opcional a mostrar
        analysis: Análisis opcional a mostrar
        role_options: Opciones del wizard opcionales
        saved_mapping: Mapping guardado opcional (si no se pasa, se lee de sesión)
        template: Template a renderizar
        
    Returns:
        HttpResponse con el template renderizado
    """
    # Si no se pasa mapping, lo cargamos desde sesión
    if saved_mapping is None:
        saved_mapping = get_mapping(request)

    # Construye el contexto base
    context = {
        "form": form,
        "saved_mapping": saved_mapping,
    }

    # Calcula calidad del mapping si hay datos
    if saved_mapping and analysis is not None:
        mapping_quality = calculate_mapping_quality(saved_mapping, analysis)
        context["mapping_quality"] = mapping_quality

    # Añade elementos opcionales al contexto
    if api_request is not None:
        context["api_request"] = api_request
    if analysis is not None:
        context["analysis"] = analysis
    if role_options is not None:
        context["role_options"] = role_options

    # Renderiza plantilla con el contexto construido
    return render(request, template, context)


# ============================== GET del asistente ==============================

def get_assistant(request):
    """
    Maneja el GET del asistente
    
    Si viene api_request_id en querystring, carga ese análisis específico
    Si no, muestra el formulario vacío
    """
    # Form vacío por defecto
    form = APIRequestForm()

    # Si viene api_request_id por querystring, intentamos cargarlo
    api_request_id = request.GET.get("api_request_id")

    if api_request_id:
        api_request = APIRequest.objects.filter(id=api_request_id, user=request.user).first()

        if not api_request:
            messages.error(request, "No se encontró ese análisis en tu cuenta.")
            return render_assistant(request, form=form)

        # Mapping: preferimos el guardado en BD; si no, sesión
        saved_mapping = api_request.field_mapping or get_mapping(request)

        # Si hay datos parseados, reconstruimos analysis y role_options
        analysis = None
        role_options = []

        if api_request.parsed_data:
            analysis = build_analysis(api_request.parsed_data, raw_text=api_request.raw_data or "")
            role_options = build_role_options(analysis, saved_mapping)

            # Pre-rellenar la URL en el form
            form = APIRequestForm(initial={"api_url": api_request.api_url})

        return render_assistant(
            request,
            form=form,
            api_request=api_request,
            analysis=analysis,
            role_options=role_options,
            saved_mapping=saved_mapping,
        )

    # Si no viene api_request_id, comportamiento normal
    saved_mapping = get_mapping(request)
    return render_assistant(request, form=form, saved_mapping=saved_mapping)


# ============================== POST: guardar mapping ==============================

def save_mapping(request):
    """
    Guarda el mapping configurado en el paso 2
    
    Valida el mapping, lo guarda en sesión y en BD si es posible,
    y re-renderiza el asistente con los resultados
    """
    # Lee el mapping desde POST
    field_mapping = read_mapping(request.POST)

    # Intentamos construir análisis si podemos (para validar keys)
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

    # Valida mapping con parámetros mejorados
    validation = validate_mapping(
        field_mapping,
        analysis_result=analysis_for_validation,
        required_roles=("title",),
        prevent_duplicates_in=("title", "description", "subtitle", "content", "author"),
        allow_duplicate_in=("id", "link", "date", "category", "tags"),
    )

    # Siempre guardamos en sesión para no perder selección del usuario
    field_mapping = validation["cleaned"]
    store_mapping(request, field_mapping)

    # Si hay errores, NO guardamos en BD (solo mostramos mensajes y re-render)
    if not validation["ok"]:
        for msg in validation["errors"]:
            messages.error(request, msg)

        role_select_options = []
        if analysis_for_validation:
            role_select_options = build_role_options(analysis_for_validation, field_mapping)

        form = APIRequestForm(initial={"api_url": api_request_for_validation.api_url if api_request_for_validation else ""})

        return render_assistant(
            request,
            form=form,
            api_request=api_request_for_validation,
            analysis=analysis_for_validation,
            role_options=role_select_options,
            saved_mapping=field_mapping,
        )

    # Si hay warnings, los mostramos pero dejamos continuar
    for msg in validation["warnings"]:
        messages.warning(request, msg)

    # Ahora sí: guardado en BD si existe APIRequest del user
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
        role_select_options = build_role_options(analysis_result, field_mapping)

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
    
    ✨ MEJORAS:
    - Sistema de caché: Si la URL ya fue analizada recientemente (< 1h), 
      usa los datos cacheados en vez de descargar de nuevo
    - Ahorra tiempo, ancho de banda y CPU
    """
    # Construye el form con POST para validar URL
    form = APIRequestForm(request.POST)

    # Si el form no es válido, informa y re-renderiza
    if not form.is_valid():
        messages.error(request, "La URL no es válida (incluye http:// o https://).")
        return render_assistant(request, form=form)

    # Extrae URL validada
    api_url = form.cleaned_data["api_url"]
    
    # ✨ NUEVO: Intentar obtener del caché primero
    cache_key = _get_cache_key(api_url)
    cached_data = cache.get(cache_key)
    
    if cached_data:
        # ✨ Datos encontrados en caché - usar directamente
        messages.info(
            request, 
            "⚡ Análisis cargado desde caché (datos recientes). "
            "Si quieres forzar un nuevo análisis, espera 1 hora o cambia la URL ligeramente."
        )
        
        # Crear registro en BD con los datos cacheados
        api_request_obj = APIRequest.objects.create(
            user=request.user,
            api_url=api_url,
            raw_data=cached_data["raw_text"],
            parsed_data=cached_data["parsed_payload"],
            response_summary=cached_data["response_summary"],
            status="processed",
            error_message="",
        )
        
        # Guardar en sesión
        request.session["last_api_request_id"] = api_request_obj.id
        
        # Reconstruir análisis
        analysis_result = build_analysis(
            cached_data["parsed_payload"], 
            raw_text=cached_data["raw_text"]
        )
        
        saved_mapping = get_mapping(request)
        role_select_options = build_role_options(analysis_result, saved_mapping)
        
        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            role_options=role_select_options,
            saved_mapping=saved_mapping,
        )
    
    # ✨ No hay caché - proceder con descarga normal
    # Crea el registro en BD como pending para poder guardar errores luego
    api_request_obj = APIRequest.objects.create(
        user=request.user,
        api_url=api_url,
        status="pending",
    )

    # Intenta ejecutar descarga/parse/análisis
    try:
        # Descarga texto crudo y obtiene resumen HTTP
        raw_text, fetch_summary = fetch_url(api_url)
        # Parsea texto crudo y obtiene (fmt, parsed)
        data_format, parsed_payload = parse_raw(raw_text)

        # Construye análisis de estructura para UI
        analysis_result = build_analysis(parsed_payload, raw_text=raw_text)
        # Construye resumen de lo parseado
        parse_summary = summarize_data(data_format, parsed_payload)
        
        response_summary = f"{fetch_summary} {parse_summary}"

        # Guarda en BD
        api_request_obj.raw_data = raw_text
        api_request_obj.parsed_data = parsed_payload
        api_request_obj.response_summary = response_summary
        api_request_obj.status = "processed"
        api_request_obj.error_message = ""
        api_request_obj.save()
        
        # ✨ NUEVO: Guardar en caché para futuros análisis
        cache.set(cache_key, {
            "raw_text": raw_text,
            "parsed_payload": parsed_payload,
            "response_summary": response_summary,
        }, CACHE_TIMEOUT)

        # Guarda el último id analizado en sesión (fallback para mapping)
        request.session["last_api_request_id"] = api_request_obj.id

        # Carga mapping desde sesión
        saved_mapping = get_mapping(request)
        # Construye opciones del wizard con analysis + mapping
        role_select_options = build_role_options(analysis_result, saved_mapping)

        # Mensaje de éxito
        messages.success(request, "URL descargada, parseada y analizada correctamente.")

        # Renderiza asistente con resultados
        return render_assistant(
            request,
            form=form,
            api_request=api_request_obj,
            analysis=analysis_result,
            role_options=role_select_options,
            saved_mapping=saved_mapping,
        )

    except Exception as exc:
        # Marca estado error
        api_request_obj.status = "error"
        api_request_obj.error_message = str(exc)
        api_request_obj.response_summary = "Error al descargar, parsear o analizar la URL."
        api_request_obj.save()

        # Mensaje de error al usuario
        messages.error(request, f"No se pudo procesar la URL: {exc}")
        return render_assistant(request, form=form)


# ============================== Vista principal ==============================

@login_required
def assistant(request):
    """
    Vista principal del asistente (router GET/POST)
    
    GET: Muestra la página del asistente (posiblemente con un análisis cargado)
    POST: Decide acción según el parámetro 'action':
          - 'save_mapping': Guarda mapping
          - sin action: Analiza URL
    """
    # Si llega GET, muestra la página
    if request.method == "GET":
        return get_assistant(request)

    # Si llega POST, decide acción
    if request.method == "POST":
        # Si la acción es guardar mapping
        if request.POST.get("action") == "save_mapping":
            return save_mapping(request)
        # Si no, interpreta como analizar URL
        return analyze_url(request)

    # Rechaza otros métodos (PUT/DELETE, etc.)
    return HttpResponseNotAllowed(["GET", "POST"])
