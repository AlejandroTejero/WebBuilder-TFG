"""
Vistas de preview
Muestran los datos normalizados en formato de cards
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import APIRequest
from ..utils.analysis import build_analysis
from ..utils.normalizer import normalize_items
from ..utils.mapping import get_mapping


@login_required
def preview(request, api_request_id: int):
    """
    Vista de preview completa (con layout completo)
    
    Muestra una página completa con información del análisis
    y las cards normalizadas de los items
    
    Args:
        request: Request de Django
        api_request_id: ID del APIRequest a mostrar
        
    Returns:
        HttpResponse con la página de preview renderizada
    """
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
    analysis_result = build_analysis(
        api_request_obj.parsed_data, 
        raw_text=api_request_obj.raw_data or ""
    )

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

@login_required
def preview_cards(request, api_request_id: int):
    """
    Vista AJAX que devuelve HTML de preview (lista + detalle).
    Soporta ?index=N para seleccionar un item.
    """
    api_request_obj = APIRequest.objects.filter(id=api_request_id, user=request.user).first()
    if not api_request_obj:
        return HttpResponse('<div class="wb-message wb-message--error">APIRequest no encontrado</div>')

    field_mapping = api_request_obj.field_mapping or get_mapping(request)

    if not api_request_obj.parsed_data:
        return HttpResponse('<div class="wb-message wb-message--warning">No hay datos parseados</div>')

    analysis_result = build_analysis(
        api_request_obj.parsed_data,
        raw_text=api_request_obj.raw_data or ""
    )

    normalized_items = normalize_items(
        parsed_data=api_request_obj.parsed_data,
        analysis_result=analysis_result,
        field_mapping=field_mapping,
        limit=20,
    )

    # index seleccionado (0-based)
    try:
        selected_index = int(request.GET.get("index", "0"))
    except ValueError:
        selected_index = 0

    if selected_index < 0:
        selected_index = 0
    if selected_index >= len(normalized_items):
        selected_index = max(0, len(normalized_items) - 1)

    selected_item = normalized_items[selected_index] if normalized_items else None

    return render(request, "WebBuilder/preview_cards_snippet.html", {
        "items": normalized_items,
        "selected_index": selected_index,
        "selected_item": selected_item,
    })

