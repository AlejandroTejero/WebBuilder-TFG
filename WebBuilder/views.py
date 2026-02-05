# Importa HttpResponse para texto plano y HttpResponseNotAllowed para rechazar métodos no soportados
from django.http import HttpResponse, HttpResponseNotAllowed
# Importa render para devolver HTML y redirect para redirigir
from django.shortcuts import render, redirect
# Importa mensajes para feedback al usuario
from django.contrib import messages
# Importa login_required para proteger la vista
from django.contrib.auth.decorators import login_required
# Importa el formulario de registro básico de Django
from django.contrib.auth.forms import UserCreationForm

# Importa el modelo que guarda cada análisis
from .models import APIRequest
# Importa el formulario donde el usuario pega la URL
from .forms import APIRequestForm

# Importa el lector de URL (descarga texto crudo)
from .utils.url_reader import fetch_url
# Importa el parser (formato + parse + resumen)
from .utils.parsers import parse_raw, summarize_data
# Importa el análisis de estructura (main items + sugerencias)
from .utils.analysis import build_analysis, calculate_mapping_quality
# Importa helpers del mapping (sesión + BD + opciones del wizard)
from .utils.mapping import (
    # Lee mapping desde POST
    read_mapping,
    # Guarda mapping en sesión
    store_mapping,
    # Carga mapping desde sesión
    get_mapping,
    # Resuelve id de APIRequest para guardar mapping
    resolve_api_id,
    # Guarda mapping en BD
    save_mapping_to_db,
    # Construye opciones de roles para el template
    build_role_options,
    validate_mapping,
)


from .utils.normalizer import normalize_items

# ============================== Páginas simples ==============================

# Renderiza la página de inicio
def home(request):
    # Intenta renderizar la plantilla
    try:
        # Devuelve la plantilla de home
        return render(request, "WebBuilder/homeOriginal.html")
    # Captura errores inesperados
    except Exception as exc:
        # Devuelve un texto plano con el error
        return HttpResponse(f"Error al procesar: {exc}")

# Maneja el registro de usuarios
def register(request):
    # Si llega un POST, intenta crear usuario
    if request.method == "POST":
        # Construye el form con los datos enviados
        form = UserCreationForm(request.POST)
        # Valida el form
        if form.is_valid():
            # Guarda el usuario
            form.save()
            # Redirige al login
            return redirect("login")
    # Si no es POST, muestra formulario vacío
    else:
        # Construye un form vacío
        form = UserCreationForm()
    # Renderiza la plantilla de registro con el form
    return render(request, "registration/register.html", {"form": form})


# ============================== Helper de render del asistente ==============================

# Renderiza la página del asistente con contexto consistente
def render_assistant(
    # Request de Django
    request,
    # Fuerza args por nombre para claridad
    *,
    # Formulario a pintar
    form,
    # APIRequest opcional a mostrar
    api_request=None,
    # Análisis opcional a mostrar
    analysis=None,
    # Opciones del wizard opcionales
    role_options=None,
    # Mapping guardado opcional (si no se pasa, se lee de sesión)
    saved_mapping=None,
    # Template a renderizar
    template="WebBuilder/assistant.html",
):
    # Si no se pasa mapping, lo cargamos desde sesión
    if saved_mapping is None:
        # Lee mapping desde sesión
        saved_mapping = get_mapping(request)

    # Construye el contexto base
    context = {
        # Pasa el formulario
        "form": form,
        # Pasa el mapping (para preselección en wizard)
        "saved_mapping": saved_mapping,
    }

    # ✨ NUEVO: Calcula calidad del mapping si hay datos
    if saved_mapping and analysis is not None:
        mapping_quality = calculate_mapping_quality(saved_mapping, analysis)
        context["mapping_quality"] = mapping_quality

    # Si hay APIRequest, lo añade al contexto
    if api_request is not None:
        # Añade api_request al contexto
        context["api_request"] = api_request
    # Si hay análisis, lo añade al contexto
    if analysis is not None:
        # Añade analysis al contexto
        context["analysis"] = analysis
    # Si hay role_options, lo añade al contexto
    if role_options is not None:
        # Añade role_options al contexto
        context["role_options"] = role_options

    # Renderiza plantilla con el contexto construido
    return render(request, template, context)


# ============================== GET del asistente ==============================

def get_assistant(request):
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

    # ✨ Valida mapping con parámetros mejorados
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



# ============================== POST: analizar URL ==============================

# Analiza una URL (descarga + parsea + analiza + guarda en BD)
def analyze_url(request):
    # Construye el form con POST para validar URL
    form = APIRequestForm(request.POST)

    # Si el form no es válido, informa y re-renderiza
    if not form.is_valid():
        # Mensaje de error
        messages.error(request, "La URL no es válida (incluye http:// o https://).")
        # Renderiza asistente con errores del form
        return render_assistant(request, form=form)

    # Extrae URL validada
    api_url = form.cleaned_data["api_url"]

    # Crea el registro en BD como pending para poder guardar errores luego
    api_request_obj = APIRequest.objects.create(
        # Usuario dueño
        user=request.user,
        # URL objetivo
        api_url=api_url,
        # Estado inicial
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

        # Guarda raw_data
        api_request_obj.raw_data = raw_text
        # Guarda parsed_data
        api_request_obj.parsed_data = parsed_payload
        # Guarda resumen combinado
        api_request_obj.response_summary = f"{fetch_summary} {parse_summary}"
        # Marca como processed
        api_request_obj.status = "processed"
        # Limpia error_message
        api_request_obj.error_message = ""
        # Persiste cambios
        api_request_obj.save()

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
            # Pasa request
            request,
            # Pasa form
            form=form,
            # Pasa api_request
            api_request=api_request_obj,
            # Pasa analysis
            analysis=analysis_result,
            # Pasa role options
            role_options=role_select_options,
            # Pasa mapping
            saved_mapping=saved_mapping,
        )

    # Captura error del pipeline
    except Exception as exc:
        # Marca estado error
        api_request_obj.status = "error"
        # Guarda mensaje de error
        api_request_obj.error_message = str(exc)
        # Guarda resumen genérico
        api_request_obj.response_summary = "Error al descargar, parsear o analizar la URL."
        # Persiste error
        api_request_obj.save()

        # Mensaje de error al usuario
        messages.error(request, f"No se pudo procesar la URL: {exc}")
        # Renderiza asistente con el form
        return render_assistant(request, form=form)


# ============================== Vista principal ==============================

# Vista principal del asistente (router GET/POST)
@login_required
def assistant(request):
    # Si llega GET, muestra la página
    if request.method == "GET":
        # Delegación a GET handler
        return get_assistant(request)

    # Si llega POST, decide acción
    if request.method == "POST":
        # Si la acción es guardar mapping, llama a save_mapping
        if request.POST.get("action") == "save_mapping":
            # Guarda mapping
            return save_mapping(request)
        # Si no, interpreta como analizar URL
        return analyze_url(request)

    # Rechaza otros métodos (PUT/DELETE, etc.)
    return HttpResponseNotAllowed(["GET", "POST"])


# ============================== Normalizar los datos ==============================

@login_required
def preview(request, api_request_id: int):
    # Busca el APIRequest del usuario (seguridad)
    api_request_obj = APIRequest.objects.filter(id=api_request_id, user=request.user).first()

    # Si no existe, devolvemos 404 simple
    if not api_request_obj:
        return HttpResponse("No encontrado.", status=404)

    # Decide el mapping: primero BD, si no, sesión
    field_mapping = api_request_obj.field_mapping or get_mapping(request)

    # Si no hay parsed_data, no podemos hacer preview
    if not api_request_obj.parsed_data:
        messages.warning(request, "No hay datos parseados para este análisis.")
        return redirect("assistant")

    # Recalcula analysis para asegurar coherencia con los datos actuales
    analysis_result = build_analysis(api_request_obj.parsed_data, raw_text=api_request_obj.raw_data or "")

    # Normaliza items a formato estándar
    normalized_items = normalize_items(
        parsed_data=api_request_obj.parsed_data,
        analysis_result=analysis_result,
        field_mapping=field_mapping,
        limit=20,
    )

    # Renderiza la plantilla de preview
    return render(request, "WebBuilder/preview.html", {
        "api_request": api_request_obj,
        "analysis": analysis_result,
        "saved_mapping": field_mapping,
        "items": normalized_items,
    })


# ============================== Historial ==============================

@login_required
def history(request):
    # Carga los análisis del usuario (más recientes primero)
    api_requests = (
        APIRequest.objects
        .filter(user=request.user)
        .order_by("-date")
    )

    # Placeholder para futuras “webs generadas”
    generated_sites = []

    return render(request, "WebBuilder/history.html", {
        "api_requests": api_requests,
        "generated_sites": generated_sites,
    })