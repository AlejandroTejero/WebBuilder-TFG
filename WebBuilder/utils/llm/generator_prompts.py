"""
generator_prompts.py — Prompts para que el LLM genere cada archivo del proyecto Django.

Archivos que genera el LLM:
  - models.py        → campos inferidos del dataset
  - views.py         → views por página
  - templates HTML   → una llamada por página
  - base.html        → navbar, Tailwind CDN, Dark & Sharp
  - load_data.py     → management command que descarga de la API

Archivos fijos (NO genera el LLM):
  - settings.py, manage.py, urls.py, wsgi.py, Dockerfile, requirements.txt
"""
from __future__ import annotations
import json

from .template_examples import get_example

def _fields_info(fields):
    return json.dumps(fields, ensure_ascii=False, indent=2)

def _samples_info(sample_items, n=4):
    return json.dumps(sample_items[:n], ensure_ascii=False, indent=2)

def _base_system():
    return (
        "Eres un desarrollador Django senior experto en Python y Tailwind CSS. "
        "Devuelves SOLO código puro, sin explicaciones, sin Markdown, sin bloques ```. "
        "El código debe ser correcto, limpio y funcionar sin modificaciones."
    )


# ── 1) ESTRUCTURA DE PÁGINAS ─────────────────────────────────────────────────
# Primera llamada al LLM: decide qué páginas tendrá el sitio.
# El resto de llamadas (views, templates) se basan en este output.

def prompt_pages_structure(*, site_type, site_title, user_prompt, fields, sample_items):
    system = (
        "Eres un arquitecto de sitios web. "
        "Devuelves SOLO un objeto JSON válido, sin Markdown ni texto extra."
    )

    example = json.dumps({"pages": [
        {"name": "home", "url": "/", "template": "siteapp/home.html",
         "view_name": "home", "description": "Portada con hero y resumen",
         "is_list": False, "is_detail": False},
        {"name": "catalog", "url": "/catalog/", "template": "siteapp/catalog.html",
         "view_name": "catalog", "description": "Listado de items en grid",
         "is_list": True, "is_detail": False},
        {"name": "detail", "url": "/item/<pk>/", "template": "siteapp/detail.html",
         "view_name": "detail", "description": "Detalle de un item",
         "is_list": False, "is_detail": True},
    ]}, ensure_ascii=False, indent=2)

    rules = [
        "Devuelve SOLO JSON con key 'pages' (lista de páginas).",
        "Mínimo obligatorio: home/portada + listado + detalle.",
        "Opcionales según el prompt: about, contact, categorías, búsqueda.",
        "Máximo 6 páginas en total.",
        "Cada página: name, url, template, view_name, description, is_list, is_detail.",
        "Solo UNA página con is_list=true. Solo UNA con is_detail=true.",
        "La de detalle siempre con url que contenga <pk>.",
        "Nombres en snake_case. URLs en kebab-case.",
    ]

    user_text = "\n".join([
        f"SITIO: {site_title}  |  TIPO: {site_type}",
        f"PROMPT DEL USUARIO: {user_prompt or '(sin prompt)'}",
        "", "CAMPOS:", _fields_info(fields),
        "", "DATOS DE EJEMPLO:", _samples_info(sample_items, 2),
        "", "REGLAS:", "\n".join(f"- {r}" for r in rules),
        "", "EJEMPLO DE OUTPUT:", example,
        "", "Genera la estructura de páginas ahora:",
    ])
    return system, user_text


# ── 2) MODELS.PY ─────────────────────────────────────────────────────────────

def prompt_models(*, fields, sample_items, site_title):
    rules = [
        "Genera SOLO el contenido de models.py. Sin Markdown.",
        "Un modelo llamado 'Item' con los campos del schema.",
        "Infiere el tipo Django correcto con los ejemplos:",
        "  URL/imagen → URLField(blank=True)",
        "  Texto largo o HTML → TextField(blank=True)",
        "  Texto corto → CharField(max_length=500, blank=True)",
        "  Entero → IntegerField(null=True, blank=True)",
        "  Decimal/precio → DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)",
        "  Fecha → DateField(null=True, blank=True)",
        "  Booleano → BooleanField(null=True, blank=True)",
        "  OBJETO ANIDADO (dict con subkeys) → CharField(max_length=500, blank=True) guardando solo el valor mas representativo como string.",
        "Todos los campos opcionales (blank=True / null=True).",
        "Añade created_at = models.DateTimeField(auto_now_add=True).",
        "__str__ devuelve el campo más representativo.",
        "Nombres de campo en snake_case. NO uses 'id' como nombre.",
        "Solo importa 'from django.db import models'.",
        "NUNCA uses JSONField para ningún campo.",
    ]
    user_text = "\n".join([
        f"SITIO: {site_title}",
        "", "CAMPOS:", _fields_info(fields),
        "", "DATOS DE EJEMPLO:", _samples_info(sample_items),
        "", "REGLAS:", "\n".join(f"- {r}" for r in rules),
        "", "Genera models.py ahora:",
    ])
    return _base_system(), user_text


# ── 3) VIEWS.PY ──────────────────────────────────────────────────────────────

def prompt_views(*, fields, site_type, site_title, user_prompt, pages, real_fields=None):
    fields_list = ", ".join(f["key"] for f in fields)
    rules = [
        "Genera SOLO el contenido de views.py. Sin Markdown.",
        "Importa: from django.shortcuts import render, get_object_or_404",
        "Importa: from .models import Item",
        "Una view por cada página en PÁGINAS.",
        "La view de listado: items = Item.objects.all().order_by('-id')",
        "La view de detalle: recibe pk y usa get_object_or_404(Item, pk=pk).",
        "Páginas no-listado no-detalle (home, about...): puede pasar items[:6] como featured.",
        "Cada view pasa 'site_title' al contexto.",
        "Sin autenticación, sin formularios complejos.",
    ]

    if real_fields:
        rules.append(f"CAMPOS EXACTOS del modelo Item (úsalos tal cual): {real_fields}")
        rules.append("NUNCA uses un nombre de campo que no esté en esa lista.")

    user_text = "\n".join([
        f"SITIO: {site_title}  |  TIPO: {site_type}",
        f"PROMPT: {user_prompt or '(sin prompt)'}",
        f"CAMPOS DEL MODELO: {fields_list}",
        "", "PÁGINAS:", json.dumps(pages, ensure_ascii=False, indent=2),
        "", "REGLAS:", "\n".join(f"- {r}" for r in rules),
        "", "Genera views.py ahora:",
    ])
    return _base_system(), user_text


# ── 4) BASE.HTML ─────────────────────────────────────────────────────────────

def prompt_base_template(*, site_title, site_type, user_prompt, all_pages):
    nav_pages = [p for p in all_pages if not p.get("is_detail")]
    nav_info = json.dumps(
        [{"name": p["name"], "url": p["url"], "view_name": p["view_name"]} for p in nav_pages],
        ensure_ascii=False,
    )
    rules = [
        "Genera SOLO el HTML de base.html. Sin Markdown.",
        "Incluye <script src='https://cdn.tailwindcss.com'></script> en <head>.",
        "Incluye Inter font de Google Fonts en <head>.",
        "COLORES: usa los colores indicados en el prompt del usuario.",
        "Si no hay indicación, usa fondo oscuro bg-gray-950 con texto claro.",
        "Navbar: site_title a la izquierda, links de nav a la derecha.",
        "Links del navbar usan {% url 'view_name' %}.",
        "{% block content %}{% endblock %} dentro de <main class='max-w-7xl mx-auto px-6 py-10'>.",
        "Footer minimalista con el nombre del sitio.",
        "NO uses JavaScript propio.",
    ]
    
    user_text = "\n".join([
        f"SITIO: {site_title}  |  TIPO: {site_type}",
        "",
        "═══ INSTRUCCIÓN PRINCIPAL DEL USUARIO (prioridad máxima) ═══",
        f"{user_prompt or '(sin instrucciones — usa tu criterio según el dataset)'}",
        "═══════════════════════════════════════════════════════════",
        "",
        "IMPORTANTE: El estilo visual del sitio debe reflejar",
        "fielmente la instrucción del usuario.",
        "",
        "", "PÁGINAS PARA EL NAVBAR:", nav_info,
        "", "REGLAS TÉCNICAS:", "\n".join(f"- {r}" for r in rules),
        "", "Genera base.html ahora:",
    ])
    return _base_system(), user_text


# ── 5) TEMPLATE POR PÁGINA ───────────────────────────────────────────────────

def prompt_template(*, page, fields, sample_items, site_type, site_title, user_prompt, all_pages,  real_fields=None, real_url_names=None):
    is_list   = page.get("is_list", False)
    is_detail = page.get("is_detail", False)

    nav_links = "\n".join(
        f"  {p['name']}: {p['url']}"
        for p in all_pages if not p.get("is_detail")
    )

    if is_list:
        context_hint = (
            "CONTEXTO: 'items' (queryset de Item), 'site_title'.\n"
            "Usa {% for item in items %} para iterar.\n"
            "Enlace a detalle: {% url 'detail' item.pk %}"
        )
    elif is_detail:
        context_hint = (
            "CONTEXTO: 'item' (objeto Item individual), 'site_title'.\n"
            "Muestra todos los campos del item.\n"
            "Enlace de vuelta: {% url 'catalog' %} (o la página de listado)."
        )
    else:
        context_hint = (
            "CONTEXTO: 'site_title', 'items' (primeros 6 para featured).\n"
            "Es una página estática/editorial. Diseña un hero atractivo.\n"
            "Incluye CTA hacia el listado principal."
        )

    rules = [
        "Genera SOLO el HTML del template. Sin Markdown.",
        "USA {% extends 'base.html' %} y {% block content %}...{% endblock %}.",
        "USA Tailwind CSS (CDN ya en base.html). Sin <style> extenso.",
        "DISEÑO: sigue el estilo indicado en el prompt del usuario para colores y estética.",
        "Si no hay indicación de colores, usa un diseño oscuro moderno.",
        "Hover en cards: añade transición suave hover:shadow-lg transition-all.",
        context_hint,
        "USA {% if item.campo %} para campos opcionales.",
        "El diseño debe adaptarse al site_type y al prompt del usuario.",
        "Nombres de campo: usa los 'key' del schema directamente como atributos del modelo.",
        "CRITICO: todos los campos del modelo son strings o tipos simples, NUNCA objetos. No uses item.campo.subcampo.",
    ]

    if real_fields:
        rules.append(f"CAMPOS EXACTOS del modelo Item: {real_fields}")
        rules.append("En los templates usa item.<campo> SOLO con campos de esa lista.")
        rules.append("NUNCA uses item.campo.subcampo — todos son strings simples.")

    if real_url_names:
        detail_page = next((n for n, v in real_url_names.items()
                           if any(p.get("is_detail") and p["name"] == n
                                  for p in all_pages)), None)
        
        url_rules = "NOMBRES EXACTOS de las URLs para usar en {% url %}:\n"
        for name, view_name in real_url_names.items():
            url_rules += f"  - {{% url '{view_name}' %}}\n"
        if detail_page:
            url_rules += f"  - Para detalle con pk: {{% url '{real_url_names[detail_page]}' item.pk %}}\n"

        rules.append(url_rules)
        rules.append("NUNCA inventes nombres de URL que no estén en esa lista.")

    user_text = "\n".join([
        f"SITIO: {site_title}  |  TIPO: {site_type}",
        "",
        "═══ INSTRUCCIÓN PRINCIPAL DEL USUARIO (prioridad máxima) ═══",
        f"{user_prompt or '(sin instrucciones — usa tu criterio según el dataset)'}",
        "═══════════════════════════════════════════════════════════",
        "",
        "IMPORTANTE: El diseño, estilo, colores y estructura deben",
        "reflejar fielmente la instrucción del usuario de arriba.",
        "Si pide minimalista → minimalista. Si pide colorido → colorido.",
        "Si pide oscuro → oscuro. La instrucción del usuario manda.",
        "",
        f"PÁGINA: {page['name']} — {page['description']}",
        "", "NAVEGACIÓN:", nav_links,
        "", "CAMPOS:", _fields_info(fields),
        "", "DATOS DE EJEMPLO:", _samples_info(sample_items, 3),
        "", "REGLAS TÉCNICAS:", "\n".join(f"- {r}" for r in rules),
        f"", f"Genera el template '{page['name']}' ahora:",
    ])

    # Añadir ejemplo few-shot si existe para este tipo
    page_kind = 'list' if is_list else ('detail' if is_detail else 'home')
    example_html = get_example(site_type, page_kind)

    if example_html:
        user_text += "\n\nEJEMPLO DE REFERENCIA (úsalo como inspiración estructural):"
        user_text += example_html
        user_text += "\n(Adapta el diseño libremente. USA los campos reales, NO los del ejemplo. NO copies esto tal cual.)"

    return _base_system(), user_text


# ── 6) LOAD_DATA.PY ──────────────────────────────────────────────────────────

def prompt_load_data(*, fields, sample_items, api_url, main_collection_path=None, real_fields=None):
    mapping = "\n".join(
        f"  dataset['{f['key']}'] → Item.{f['key']}"
        for f in fields[:10]
    )
    rules = [
        "Genera SOLO el management command load_data.py. Sin Markdown.",
        "from django.core.management.base import BaseCommand",
        "from siteapp.models import Item",
        "import requests",
        f"El comando hace GET a '{api_url}'.",
        "Parsea el JSON y encuentra la lista principal de items (puede estar anidada).",
        "CRITICO: usa get_or_create separando campos en defaults:",
        "Item.objects.get_or_create(campo_id=valor, defaults={'campo1': val1, 'campo2': val2})",
        "Si no hay campo único identificador, usa update_or_create o simplemente create().",
        "Si un campo del dataset es un OBJETO ANIDADO (dict), extrae solo el valor más representativo como string.",
        "  Ejemplo: rating = {'rate': 4.5, 'count': 120} → guardar str(item['rating']['rate'])",
        "Limpia valores: precios → Decimal(str(valor).replace('$','').strip()), el precio puede venir como float o como string con '$', usa siempre str() primero para evitar errores. Fechas → parsear, enteros → int().",
        "Si falla la conversión → None (no romper el comando).",
        "Informa del progreso con self.stdout.write().",
        "try/except general para no romper si la API falla.",
        "Clase 'Command(BaseCommand)', help descriptivo.",
    ]

    if real_fields:
        rules.append(f"CAMPOS EXACTOS del modelo Item: {real_fields}")
        rules.append("El mapeo debe ser: raw_item['api_key'] → item_field para CADA campo.")

    if main_collection_path:
        path_str = " -> ".join(str(p) for p in main_collection_path)
        rules.append(
            f"RUTA EXACTA de la colección en el JSON: {path_str}. "
            f"Accede navegando esa ruta desde la raíz del JSON."
        )

    user_text = "\n".join([
        f"API URL: {api_url}",
        "", "MAPPING KEY → CAMPO MODELO:", mapping,
        "", "CAMPOS COMPLETOS:", _fields_info(fields),
        "", "EJEMPLO DE DATOS:", _samples_info(sample_items, 3),
        "", "REGLAS:", "\n".join(f"- {r}" for r in rules),
        "", "Genera load_data.py ahora:",
    ])
    return _base_system(), user_text