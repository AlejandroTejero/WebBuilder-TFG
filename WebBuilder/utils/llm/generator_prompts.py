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

from .examples import get_example

def _fields_info(fields):
    return json.dumps(fields, ensure_ascii=False, indent=2)

def _samples_info(sample_items, n=4):
    return json.dumps(sample_items[:n], ensure_ascii=False, indent=2)

def _base_system():
    return (
        "Eres un desarrollador Django senior experto en Python y Tailwind CSS. "
        "REGLA ABSOLUTA: devuelves ÚNICAMENTE código puro, sin ningún tipo de Markdown. "
        "PROHIBIDO escribir ``` en cualquier parte de tu respuesta. "
        "PROHIBIDO escribir ```python, ```html, ```django o cualquier variante. "
        "Tu respuesta empieza DIRECTAMENTE con la primera línea de código, sin preámbulo. "
        "Tu respuesta termina DIRECTAMENTE con la última línea de código, sin explicación. "
        "Si añades bloques Markdown el código fallará en producción. No los añadas."
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
        "MÍNIMO OBLIGATORIO: home + listado + detalle. Siempre estas tres.",
        "CRÍTICO: la página 'home' es una LANDING PAGE — hero, stats y featured items. NUNCA es el listado completo.",
        "CRÍTICO: el listado completo va SIEMPRE en una página separada (catalog, list, etc.) con is_list=true.",
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
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con 'from django.db import models'. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```python o cualquier bloque Markdown. Código puro.",
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
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con 'from django.shortcuts import render, get_object_or_404'. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```python o cualquier bloque Markdown. Código puro.",
        "Importa: from .models import Item",
        "Importa: from django.core.paginator import Paginator",
        "Una view por cada página en PÁGINAS.",
        "La view de listado acepta búsqueda server-side: q = request.GET.get('q', ''); si q no está vacío, filtra con Item.objects.filter(pk__isnull=False) y añade Q objects para cada campo de texto disponible. Pasa 'q' al contexto para que el template pueda mostrar el valor en el input.",
        "La view de listado DEBE usar paginación:",
        "  from django.core.paginator import Paginator",
        "  queryset = Item.objects.all().order_by('-id')",
        "  paginator = Paginator(queryset, 12)",
        "  page_number = request.GET.get('page', 1)",
        "  items = paginator.get_page(page_number)",
        "  Pasar 'items' y 'page_obj' (= items) al contexto.",
        "La view de detalle: recibe pk y usa get_object_or_404(Item, pk=pk).",
        "La view de detalle ADEMÁS pasa 'related' al contexto: related = Item.objects.exclude(pk=item.pk).order_by('?')[:3]",
        "Páginas no-listado no-detalle (home, about...): pasa items[:6] como featured usando Item.objects.all().order_by('-id')[:6].",
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
    nav_info  = json.dumps(
        [{"name": p["name"], "url": p["url"], "view_name": p["view_name"]} for p in nav_pages],
        ensure_ascii=False,
    )
    rules = [
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con '<!doctype html>'. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```html o cualquier bloque Markdown. HTML puro.",
        "Incluye <script src='https://cdn.tailwindcss.com'></script> en <head>.",
        "Incluye la fuente Inter de Google Fonts en <head>: family=Inter:wght@300;400;500;600;700.",
        "META TAGS OBLIGATORIOS en <head>: charset, viewport, description con site_title, og:title.",
        "FAVICON: añade <link rel='icon' href='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>'>.",
        "NAVBAR: sticky top-0 z-50 con backdrop-blur-sm y border-b sutil. site_title a la izquierda en font-bold.",
        "NAVBAR ACTIVO: usa request.path para marcar el link activo — añade color primario y font-semibold al link actual.",
        "NAVBAR AUTH OBLIGATORIO: en el lado derecho del navbar incluye SIEMPRE este bloque exacto de autenticación, estilado con Tailwind acorde al diseño:\n{% if user.is_authenticated %}\n  <span class='text-gray-400 text-sm'>{{ user.username }}</span>\n  <form method='post' action='{% url \"logout\" %}'>\n    {% csrf_token %}\n    <button type='submit' class='text-gray-400 hover:text-white text-sm'>Cerrar sesión</button>\n  </form>\n{% else %}\n  <a href='{% url \"login\" %}' class='text-gray-400 hover:text-white text-sm'>Entrar</a>\n  <a href='{% url \"register\" %}' class='bg-blue-600 hover:bg-blue-500 text-white text-sm px-3 py-1 rounded-lg'>Registro</a>\n{% endif %}",
        "Links del navbar usan {% url 'view_name' %}.",
        "COLORES: usa los colores indicados en el prompt del usuario con clases Tailwind.",
        "Si no hay indicación de colores, usa fondo oscuro bg-gray-950 con texto claro.",
        "{% block content %}{% endblock %} dentro de <main class='max-w-7xl mx-auto px-6 py-10'>.",
        "FOOTER OBLIGATORIO: dos columnas — (1) nombre del sitio + descripción breve, (2) links de navegación. Separado con border-t. Copyright: © {% now 'Y' %} {{ site_title }}.",
        "ANIMACIONES: añade en <head> un <style> con estas clases: @keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } } .animate-in { animation: fadeInUp 0.5s ease-out forwards; } .animate-in-delay-1 { opacity:0; animation: fadeInUp 0.5s 0.1s ease-out forwards; } .animate-in-delay-2 { opacity:0; animation: fadeInUp 0.5s 0.2s ease-out forwards; }",
        "NO uses JavaScript propio.",
    ]

    user_text = "\n".join([
        f"SITIO: {site_title}  |  TIPO: {site_type}",
        "",
        "═══ INSTRUCCIÓN DEL USUARIO (prioridad máxima) ═══",
        f"{user_prompt or '(sin instrucciones — usa tu criterio según el dataset)'}",
        "═══════════════════════════════════════════════════",
        "",
        "IMPORTANTE: el estilo visual, colores y personalidad deben reflejar fielmente la instrucción del usuario.",
        "",
        "PÁGINAS PARA EL NAVBAR:", nav_info,
        "", "REGLAS TÉCNICAS:", "\n".join(f"- {r}" for r in rules),
        "", "Genera base.html ahora:",
    ])
    return _base_system(), user_text


# ── 5) TEMPLATE POR PÁGINA ───────────────────────────────────────────────────

_VISUAL_REQUIREMENTS = {
    "home": [
        "OBLIGATORIO: Hero section con H1 grande (text-5xl+), subtítulo text-xl y botón CTA hacia el listado.",
        "OBLIGATORIO: El hero usa gradiente CSS (bg-gradient-to-br) con los colores del tema, nunca color plano.",
        "OBLIGATORIO: Sección de stats/highlights con 3 números o características en cards pequeñas.",
        "OBLIGATORIO: Grid de featured items con los primeros 6 items (variable 'items'). Cards con imagen si existe.",
        "OBLIGATORIO: Cada card del grid tiene hover effect: hover:-translate-y-1 hover:shadow-2xl transition-all duration-300.",
        "OBLIGATORIO: Título del hero con gradiente de texto: bg-gradient-to-r bg-clip-text text-transparent.",
        "RECOMENDADO: Eyebrow label sobre el H1 (badge pequeño con el tipo de sitio o temática).",
    ],
    "list": [
        "CRÍTICO: para el enlace al detalle de cada card usa EXACTAMENTE el nombre de URL de la página de detalle indicado en NOMBRES EXACTOS de las URLs. NUNCA uses 'detail' genérico.",
        "OBLIGATORIO: Cabecera de sección con título H1 y contador de resultados ({{ items|length }} items).",
        "OBLIGATORIO: Input de búsqueda con id='search-input' y placeholder descriptivo justo antes del grid.",
        "OBLIGATORIO: Cada card debe tener atributo data-search con todos sus campos concatenados en minúsculas. Ejemplo: data-search='{{ item.title|lower }} {{ item.category|lower }} {{ item.description|lower }}'.",
        "OBLIGATORIO: Al final del {% block content %}, antes del {% endblock %}, añade este JS exacto: <script>const si=document.getElementById('search-input');si.addEventListener('input',()=>{const q=si.value.toLowerCase();document.querySelectorAll('.search-item').forEach(c=>{c.style.display=c.dataset.search.includes(q)?'':'none';});});</script>",
        "OBLIGATORIO: Cada card debe tener además la clase CSS 'search-item'.",
        "OBLIGATORIO: Grid responsive: grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4.",
        "OBLIGATORIO: Cards con imagen (aspect-video object-cover) si existe campo de imagen en el modelo.",
        "OBLIGATORIO: Placeholder visual con SVG inline cuando no hay imagen. NUNCA uses placeholder.com.",
        "OBLIGATORIO: Badge de categoría en las cards si existe el campo.",
        "OBLIGATORIO: Hover en cards: hover:-translate-y-1 hover:shadow-2xl transition-all duration-300.",
        "OBLIGATORIO: Empty state visual con icono SVG y mensaje cuando no hay items ({% empty %}).",
        "RECOMENDADO: Mini hero (py-12) con título y subtítulo antes del grid.",
        "OBLIGATORIO: Controles de paginación al final del grid. Usa page_obj para navegar: {% if page_obj.has_other_pages %}<div class='flex justify-center gap-2 mt-10'>{% if page_obj.has_previous %}<a href='?page={{ page_obj.previous_page_number }}' class='px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700'>← Anterior</a>{% endif %}<span class='px-4 py-2 text-gray-400'>Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span>{% if page_obj.has_next %}<a href='?page={{ page_obj.next_page_number }}' class='px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700'>Siguiente →</a>{% endif %}</div>{% endif %}.",
    ],
    "detail": [
        "OBLIGATORIO: Breadcrumb arriba: Inicio › Listado › Nombre del item.",
        "OBLIGATORIO: Layout dos columnas en desktop: lg:grid lg:grid-cols-2 lg:gap-16.",
        "OBLIGATORIO: Imagen grande (aspect-square object-cover rounded-2xl) con placeholder SVG si no existe.",
        "OBLIGATORIO: Mostrar TODOS los campos del modelo. Campos secundarios en grid de metadatos con separadores.",
        "OBLIGATORIO: Dato principal (precio, score...) con tipografía grande y color de acento si existe.",
        "OBLIGATORIO: Botón 'Volver al listado' bien visible al final.",
        "RECOMENDADO: Sección 'También te puede interesar' con 3 items al final si hay variable 'items'.",
    ],
    "other": [
        "OBLIGATORIO: Hero con título y descripción clara de la página.",
        "OBLIGATORIO: Al menos un elemento visual destacado (stats, timeline o grid de features).",
        "OBLIGATORIO: Diseño coherente con el resto del sitio.",
    ],
}

_TAILWIND_DESIGN_RULES = [
    "TIPOGRAFÍA: jerarquía clara — H1: text-5xl font-black, H2: text-3xl font-bold, cuerpo: text-base text-gray-300.",
    "ESPACIADO: secciones separadas con py-16 o py-20. Nunca aglomeres contenido.",
    "CARDS: siempre border rounded-2xl overflow-hidden. Nunca esquinas cuadradas.",
    "BOTONES primarios: bg-gradient-to-r font-bold px-8 py-3 rounded-xl hover:opacity-90 transition-opacity.",
    "BOTONES secundarios: border border-gray-600 text-gray-300 hover:border-white hover:text-white transition-colors.",
    "IMÁGENES: siempre con aspect-ratio fijo (aspect-video o aspect-square). Nunca dejes que rompan el layout.",
    "BADGES: pills con bg-color/10 text-color text-xs font-semibold px-3 py-1 rounded-full.",
    "FONDOS: alterna entre bg-gray-950 y bg-gray-900/50 en secciones consecutivas.",
    "SOMBRAS: usa shadow-xl o shadow-2xl. Nunca shadow sin modificador.",
    "GRADIENTES de texto en heroes: bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent.",
    "ICONOS SVG: úsalos en features, empty states y stats. Paths simples 24x24, sin librerías externas.",
]


def prompt_template(*, page, fields, sample_items, site_type, site_title, user_prompt, all_pages, real_fields=None, real_url_names=None):
    is_list   = page.get("is_list", False)
    is_detail = page.get("is_detail", False)

    nav_links = "\n".join(
        f"  {p['name']}: {p['url']}"
        for p in all_pages if not p.get("is_detail")
    )

    # Resolver nombre real de la URL de detalle
    detail_page = next((p for p in all_pages if p.get("is_detail")), None)
    detail_url_name = detail_page["name"] if detail_page else "detail"

    # Resolver nombre real de la URL de listado
    list_page = next((p for p in all_pages if p.get("is_list")), None)
    list_url_name = list_page["name"] if list_page else "catalog"

    if is_list:
        context_hint = (
            "CONTEXTO: 'items' (queryset de Item), 'site_title'.\n"
            "Usa {% for item in items %} para iterar.\n"
            f"Enlace a detalle: {{% url '{detail_url_name}' item.pk %}}"
        )
    elif is_detail:
        context_hint = (
            "CONTEXTO: 'item' (objeto Item individual), 'site_title'.\n"
            "Muestra TODOS los campos del item de forma visual y organizada.\n"
            f"Enlace de vuelta: {{% url '{list_url_name}' %}} (o la página de listado)."
        )
    else:
        context_hint = (
            "CONTEXTO: 'site_title', 'items' (primeros 6 para featured).\n"
            "Es la portada del sitio. Diseña un hero impactante con CTA al listado.\n"
            "Incluye grid de featured items usando la variable 'items'."
        )

    # Requisitos visuales según tipo de página
    page_kind    = "list" if is_list else ("detail" if is_detail else ("home" if page["name"] == "home" else "other"))
    requirements = _VISUAL_REQUIREMENTS.get(page_kind, _VISUAL_REQUIREMENTS["other"])

    rules = [
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con {% extends 'base.html' %}. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```html o cualquier bloque Markdown. HTML puro.",
        "USA {% extends 'base.html' %} y {% block content %}...{% endblock %}.",
        "USA Tailwind CSS (CDN ya en base.html). Sin <style> extenso.",
        "DISEÑO: sigue el estilo indicado en el prompt del usuario para colores y estética.",
        "Si no hay indicación de colores, usa un diseño oscuro moderno con bg-gray-950.",
        context_hint,
        "USA {% if item.campo %} para campos opcionales.",
        "Nombres de campo: usa los 'key' del schema directamente como atributos del modelo.",
        "CRÍTICO: todos los campos del modelo son strings o tipos simples. NUNCA uses item.campo.subcampo.",
        "ICONOS SVG: para features, stats, empty states y botones usa iconos SVG inline simples (24x24). No necesitas librerías externas. Ejemplo: <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 13l4 4L19 7'/></svg>. Dibuja paths básicos: checks, flechas, estrellas, imágenes, calendarios, ubicaciones.",
        "ANIMACIONES: aplica la clase 'animate-in' al hero principal y 'animate-in-delay-1', 'animate-in-delay-2' a los elementos siguientes (subtítulo, CTA, primer grid). Estas clases ya están definidas en base.html.",
    ]

    if real_fields:
        rules.append(f"CAMPOS EXACTOS del modelo Item (úsalos tal cual, ninguno más): {real_fields}")
        rules.append("NUNCA uses un campo que no esté en esa lista.")

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
        "═══ INSTRUCCIÓN DEL USUARIO (prioridad máxima) ═══",
        f"{user_prompt or '(sin instrucciones — usa tu criterio según el dataset)'}",
        "═══════════════════════════════════════════════════",
        "",
        "IMPORTANTE: colores, estilo y estructura deben reflejar fielmente la instrucción del usuario.",
        "Si pide minimalista → minimalista. Si pide oscuro → oscuro. El usuario manda.",
        "",
        f"PÁGINA: {page['name']} — {page['description']}",
        "", "NAVEGACIÓN:", nav_links,
        "", "CAMPOS:", _fields_info(fields),
        "", "DATOS DE EJEMPLO:", _samples_info(sample_items, 3),
        "", "COMPONENTES OBLIGATORIOS para esta página (implementa TODOS los marcados como OBLIGATORIO):",
        "\n".join(f"  {r}" for r in requirements),
        "", "REGLAS DE DISEÑO TAILWIND:",
        "\n".join(f"  {r}" for r in _TAILWIND_DESIGN_RULES),
        "", "REGLAS TÉCNICAS:", "\n".join(f"- {r}" for r in rules),
        "", f"Genera el template '{page['name']}' ahora:",
    ])

    # Few-shot example
    page_kind    = "list" if is_list else ("detail" if is_detail else "home")
    example_html = get_example(site_type, page_kind)
    if example_html:
        user_text += "\n\nEJEMPLO DE REFERENCIA (inspiración estructural — adapta los campos reales, NO copies esto tal cual):"
        user_text += example_html

    return _base_system(), user_text

# ── 6) LOAD_DATA.PY ──────────────────────────────────────────────────────────

def prompt_load_data(*, fields, sample_items, api_url, main_collection_path=None, real_fields=None):
    mapping = "\n".join(
        f"  dataset['{f['key']}'] → Item.{f['key']}"
        for f in fields[:10]
    )
    rules = [
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con 'from django.core.management.base import BaseCommand'. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```python o cualquier bloque Markdown. Código puro.",
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
        "CRÍTICO: al final de tu respuesta, después del código, añade una línea exactamente así: ##REQUIREMENTS:libreria1,libreria2 listando SOLO las librerías externas que hayas importado que NO sean de la librería estándar de Python ni django ni requests. Si no necesitas ninguna extra escribe ##REQUIREMENTS:none",
        "Ejemplo: si usas xmltodict escribe ##REQUIREMENTS:xmltodict>=0.13 — si usas solo json o xml.etree escribe ##REQUIREMENTS:none",
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