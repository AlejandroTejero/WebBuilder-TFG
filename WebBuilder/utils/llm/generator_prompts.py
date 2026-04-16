"""
generator_prompts.py — Prompts para que el LLM genere cada archivo del proyecto Django.

Archivos que genera el LLM:
  - models.py        → campos inferidos del dataset
  - views.py         → views por página
  - templates HTML   → una llamada por página
  - base.html        → layout base, navbar, Tailwind CDN
  - load_data.py     → management command que descarga de la API

Archivos fijos (NO genera el LLM):
  - settings.py, manage.py, urls.py, wsgi.py, Dockerfile, requirements.txt
"""

from __future__ import annotations

import json

from .examples import get_example
from .design.theme_rules import build_theme_rules_text

# ── CONSTANTES GENERALES ──────────────────────────────────────────────────

_PAGE_REQUIREMENTS = {
    "home": {
        "structural": [
            "PRIORIDAD ABSOLUTA: respeta la estética, colores, tipografía, layout y restricciones indicadas por el usuario. Ninguna sugerencia visual puede contradecir su prompt.",
            "La página de inicio debe tener una apertura clara con un H1 visible y un texto introductorio que explique el sitio o su contenido.",
            "Debe existir una jerarquía clara entre bloque principal, contenido destacado y navegación hacia el resto del sitio.",
            "Incluye una acción principal hacia el listado o exploración del contenido cuando tenga sentido para el tipo de sitio.",
            "Si existe la variable 'items', puedes mostrar una selección inicial de items destacados.",
            "La home debe sentirse completa aunque no haya imágenes ni datos muy ricos.",
        ],
        "visual": [
            "El bloque de apertura puede ser hero, cabecera editorial, bloque sobrio o composición visual, según el prompt del usuario.",
            "Puedes añadir highlights, stats o bloques de valor solo si encajan con el contenido y con el estilo pedido.",
            "Usa imágenes en portada solo si existen, aportan valor y no contradicen la instrucción del usuario.",
            "Evita gradientes, sombras fuertes, animaciones llamativas o efectos de tarjeta si el prompt sugiere una estética editorial, minimalista o sobria.",
            "RECOMENDADO: una pequeña etiqueta introductoria sobre el H1 si encaja con la estética general.",
        ],
    },
    "list": {
        "structural": [
            "CRÍTICO: para el enlace al detalle de cada card usa EXACTAMENTE el nombre de URL de la página de detalle indicado en NOMBRES EXACTOS de las URLs. NUNCA uses 'detail' genérico.",
            "La página debe mostrar un listado claro y navegable de items.",
            "Incluye una cabecera de sección con título claro; el contador de resultados es opcional.",
            "Usa grid, lista vertical o columna editorial según encaje mejor con el prompt del usuario.",
            "Incluye empty state claro cuando no haya items ({% empty %}).",
            "Si existe page_obj, añade paginación funcional y bien integrada visualmente.",
            "El diseño del listado debe seguir funcionando correctamente con o sin imágenes.",
        ],
        "visual": [
            "El buscador es opcional. Añádelo solo cuando aporte valor al tipo de sitio.",
            "Si añades buscador, usa id='search-input' y placeholder descriptivo.",
            "Si añades buscador, cada item filtrable debe tener la clase CSS 'search-item'.",
            "Si añades buscador, cada item filtrable debe tener atributo data-search con campos concatenados en minúsculas.",
            "Si añades buscador, al final del {% block content %}, antes del {% endblock %}, puedes añadir este JS: <script>const si=document.getElementById('search-input');if(si){si.addEventListener('input',()=>{const q=si.value.toLowerCase();document.querySelectorAll('.search-item').forEach(c=>{c.style.display=c.dataset.search.includes(q)?'':'none';});});}</script>",
            "Usa imágenes en cards solo si existen y si el prompt del usuario permite un listado visual con imágenes.",
            "Si no usas imagen, evita cajas vacías, placeholders decorativos o huecos visuales innecesarios.",
            "Puedes mostrar categoría, fecha, autor, extracto u otros metadatos si existen y aportan valor.",
            "Evita hover effects llamativos salvo que el prompt sugiera una estética más visual o interactiva.",
        ],
    },
    "detail": {
        "structural": [
            "La página debe mostrar con claridad la información principal del item.",
            "Incluye una cabecera clara con título y metadatos relevantes si existen.",
            "Muestra los campos relevantes del modelo con buena jerarquía visual.",
            "Incluye una navegación clara para volver al listado.",
            "El layout puede ser de una o dos columnas según el contenido y el prompt del usuario.",
        ],
        "visual": [
            "Si existe imagen y encaja con la estética, muéstrala de forma destacada.",
            "Si no existe imagen o el prompt no la favorece, no inventes bloques visuales innecesarios.",
            "Destaca el dato principal si existe, pero sin imponer colores o tamaños que contradigan el prompt del usuario.",
            "RECOMENDADO: añadir items relacionados o contenido complementario al final si existe la variable 'items' y aporta valor.",
        ],
    },
    "other": {
        "structural": [
            "La página debe tener un encabezado claro con título y contexto suficiente.",
            "Debe existir una estructura visual mínima para que la página no quede vacía.",
            "Mantén coherencia funcional y visual con el resto del sitio.",
        ],
        "visual": [
            "Añade elementos visuales solo cuando aporten claridad o valor.",
            "No fuerces heroes, stats, grids o timelines si no encajan con el prompt del usuario ni con el contenido.",
        ],
    },
}

_TAILWIND_GUIDANCE = {
    "structural": [
        "TIPOGRAFÍA: mantén jerarquía clara entre H1, H2, metadatos y cuerpo.",
        "ESPACIADO: usa ritmo vertical suficiente; evita páginas apelotonadas.",
        "RESPONSIVE: el layout debe adaptarse bien a móvil y desktop.",
        "IMÁGENES: si se usan, no deben romper el layout.",
        "COMPONENTES: botones, enlaces y bloques deben ser consistentes entre páginas.",
    ],
    "visual": [
        "Aplica rounded, sombras, gradientes, badges y efectos hover solo si encajan con el prompt del usuario.",
        "En diseños editoriales o sobrios, prioriza tipografía, márgenes, ritmo y contraste frente a efectos visuales.",
        "En diseños visuales o promocionales, puedes usar más contraste, bloques destacados y recursos gráficos, siempre sin romper legibilidad.",
        "Usa iconos SVG inline solo cuando aporten claridad real; no los metas por inercia.",
    ],
}

_PRIORITY_RULES = [
    "1. La instrucción explícita del usuario tiene prioridad absoluta.",
    "2. Las restricciones funcionales del proyecto no pueden romperse.",
    "3. Los requisitos estructurales de la página deben respetarse siempre que no contradigan al usuario.",
    "4. Las sugerencias derivadas del dataset son orientativas, no obligatorias.",
    "5. Los ejemplos, estilos por defecto y guías visuales solo se usan si no contradicen niveles superiores.",
    "Nunca uses una sugerencia del dataset o una convención visual para contradecir una instrucción explícita del usuario.",
]

_AUTH_BLOCK = """{% if user.is_authenticated %}
  <span class='text-sm opacity-80'>{{ user.username }}</span>
  <form method='post' action='{% url "logout" %}'>
    {% csrf_token %}
    <button type='submit' class='text-sm transition-opacity hover:opacity-70'>Cerrar sesión</button>
  </form>
{% else %}
  <a href='{% url "login" %}' class='text-sm transition-opacity hover:opacity-70'>Entrar</a>
  <a href='{% url "register" %}' class='text-sm px-3 py-1 rounded-lg border transition-colors'>Registro</a>
{% endif %}"""


# ── HELPERS BÁSICOS ────────────────────────────────────────────────────────

def build_priority_rules_text() -> str:
    return "\n".join(f"- {rule}" for rule in _PRIORITY_RULES)


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


# ── PRIORIDADES GLOBALES DE DISEÑO ────────────────────────────────────────

_GLOBAL_STYLE_RULES = [
    "PRIORIDAD ABSOLUTA: la instrucción del usuario manda sobre cualquier estilo por defecto, sugerencia del dataset o convención visual genérica.",
    "Si el usuario especifica colores, tipografía, layout, densidad visual, tono o restricciones concretas, debes reflejarlos explícitamente en el HTML generado.",
    "Si el usuario pide una estética sobria, editorial, minimalista o similar, evita gradientes, sombras fuertes, animaciones llamativas y tarjetas visuales innecesarias.",
    "Si el usuario pide no usar imágenes en listados, no uses imágenes en listados aunque existan campos de imagen en el dataset.",
    "No conviertas automáticamente todo sitio en un diseño oscuro, startup o dashboard si el prompt no lo pide.",
]


# ── 1) ESTRUCTURA DE PÁGINAS ───────────────────────────────────────────────

def prompt_pages_structure(*, site_type, site_title, user_prompt, fields, sample_items):
    system = (
        "Eres un arquitecto de sitios web. "
        "Devuelves SOLO un objeto JSON válido, sin Markdown ni texto extra."
    )
    priority_rules_text = build_priority_rules_text()

    example = json.dumps(
        {
            "pages": [
                {
                    "name": "home",
                    "url": "/",
                    "template": "siteapp/home.html",
                    "view_name": "home",
                    "description": "Portada o landing del sitio",
                    "is_list": False,
                    "is_detail": False,
                },
                {
                    "name": "catalog",
                    "url": "/catalog/",
                    "template": "siteapp/catalog.html",
                    "view_name": "catalog",
                    "description": "Listado completo de items",
                    "is_list": True,
                    "is_detail": False,
                },
                {
                    "name": "detail",
                    "url": "/item/<pk>/",
                    "template": "siteapp/detail.html",
                    "view_name": "detail",
                    "description": "Detalle de un item",
                    "is_list": False,
                    "is_detail": True,
                },
            ]
        },
        ensure_ascii=False,
        indent=2,
    )

    rules = [
        "Devuelve SOLO JSON con key 'pages' (lista de páginas).",
        "MÍNIMO OBLIGATORIO: home + listado + detalle. Siempre estas tres.",
        "CRÍTICO: la página 'home' es una portada o landing; no debe ser el listado completo.",
        "CRÍTICO: el listado completo va SIEMPRE en una página separada con is_list=true.",
        "Opcionales según el prompt: about, contact, categorías, búsqueda, faq, landing secundaria.",
        "Máximo 6 páginas en total.",
        "Cada página: name, url, template, view_name, description, is_list, is_detail.",
        "Solo UNA página con is_list=true. Solo UNA con is_detail=true.",
        "La de detalle siempre con url que contenga <pk>.",
        "Nombres en snake_case. URLs en kebab-case.",
    ]

    user_text = "\n".join(
        [
            f"SITIO: {site_title}  |  TIPO: {site_type}",
            "",
            "REGLAS DE PRIORIDAD:",
            priority_rules_text,
            "",
            "PROMPT DEL USUARIO:",
            f"{user_prompt or '(sin prompt)'}",
            "",
            "PRIORIDADES GLOBALES:",
            "\n".join(f"- {r}" for r in _GLOBAL_STYLE_RULES),
            "",
            "CAMPOS:",
            _fields_info(fields),
            "",
            "REGLAS:",
            "\n".join(f"- {r}" for r in rules),
            "",
            "EJEMPLO DE OUTPUT:",
            example,
            "",
            "Genera la estructura de páginas ahora:",
        ]
    )
    return system, user_text


# ── 2) MODELS.PY ───────────────────────────────────────────────────────────

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
        "  OBJETO ANIDADO (dict con subkeys) → CharField(max_length=500, blank=True) guardando solo el valor más representativo como string.",
        "Todos los campos opcionales (blank=True / null=True).",
        "Añade created_at = models.DateTimeField(auto_now_add=True).",
        "__str__ devuelve el campo más representativo.",
        "Nombres de campo en snake_case. NO uses 'id' como nombre.",
        "Solo importa 'from django.db import models'.",
        "NUNCA uses JSONField para ningún campo.",
    ]

    user_text = "\n".join(
        [
            f"SITIO: {site_title}",
            "",
            "CAMPOS:",
            _fields_info(fields),
            "",
            "DATOS DE EJEMPLO:",
            _samples_info(sample_items),
            "",
            "REGLAS:",
            "\n".join(f"- {r}" for r in rules),
            "",
            "Genera models.py ahora:",
        ]
    )
    return _base_system(), user_text


# ── 3) VIEWS.PY ────────────────────────────────────────────────────────────

def prompt_views(*, fields, site_type, site_title, user_prompt, pages, real_fields=None):
    fields_list = ", ".join(f["key"] for f in fields)
    priority_rules_text = build_priority_rules_text()
    
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

    user_text = "\n".join(
        [
            f"SITIO: {site_title}  |  TIPO: {site_type}",
            "",
            "REGLAS DE PRIORIDAD:",
            priority_rules_text,
            "",
            "PROMPT DEL USUARIO:",
            f"{user_prompt or '(sin prompt)'}",
            "",
            "PRIORIDADES GLOBALES:",
            "\n".join(f"- {r}" for r in _GLOBAL_STYLE_RULES),
            "",
            f"CAMPOS DEL MODELO: {fields_list}",
            "",
            "PÁGINAS:",
            json.dumps(pages, ensure_ascii=False, indent=2),
            "",
            "REGLAS:",
            "\n".join(f"- {r}" for r in rules),
            "",
            "Genera views.py ahora:",
        ]
    )
    return _base_system(), user_text


# ── 4) BASE.HTML ───────────────────────────────────────────────────────────

def prompt_base_template(*, site_title, site_type, user_prompt, all_pages):
    nav_pages = [p for p in all_pages if not p.get("is_detail")]
    nav_info = json.dumps(
        [{"name": p["name"], "url": p["url"], "view_name": p["view_name"]} for p in nav_pages],
        ensure_ascii=False,
    )
    priority_rules_text = build_priority_rules_text()
    theme_rules_text = build_theme_rules_text()
    
    rules = [
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con '<!doctype html>'. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```html o cualquier bloque Markdown. HTML puro.",
        "Incluye <script src='https://cdn.tailwindcss.com'></script> en <head>.",
        "TIPOGRAFÍA: si el usuario indica combinación tipográfica concreta (serif, sans, mono, etc.), refléjala en el documento. Si no indica ninguna, usa Inter como fallback razonable.",
        "META TAGS OBLIGATORIOS en <head>: charset, viewport, description con site_title, og:title.",
        "FAVICON: añade <link rel='icon' href='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>'.",
        "NAVBAR: clara, usable y coherente con la estética del usuario. Puede ser sobria, minimalista, editorial o visual, pero debe incluir navegación funcional.",
        "NAVBAR ACTIVO: usa request.path para marcar el link activo con el tratamiento visual que mejor encaje con el estilo pedido.",
        f"NAVBAR AUTH: incluye SIEMPRE esta lógica Django exacta, pero adapta sus clases al diseño pedido por el usuario:\n{_AUTH_BLOCK}",
        "Links del navbar usan {% url 'view_name' %}.",
        "COLORES: si el usuario da colores HEX o paleta concreta, aplícalos explícitamente en fondo, texto, links, botones y estados activos usando clases Tailwind y/o valores arbitrarios como bg-[#111111].",
        "Si no hay indicación de colores, usa una base neutra y coherente con el tipo de sitio; no fuerces oscuro por defecto salvo que tenga sentido.",
        "Incluye {% block content %}{% endblock %} dentro de un <main> bien proporcionado. El ancho puede ser estrecho, medio o amplio según el prompt del usuario.",
        "FOOTER OBLIGATORIO: nombre del sitio + navegación básica + copyright con © {% now 'Y' %} {{ site_title }}.",
        "ANIMACIONES: si las usas, deben ser discretas. Puedes añadir utilidades CSS mínimas para fade-in suave, pero evita efectos llamativos si el prompt es sobrio o editorial.",
        "NO uses JavaScript propio salvo necesidad mínima estructural.",
    ]

    user_text = "\n".join(
        [
            f"SITIO: {site_title}  |  TIPO: {site_type}",
            "",
            "REGLAS DE PRIORIDAD:",
            priority_rules_text,
            "",
            "═══ INSTRUCCIÓN DEL USUARIO (prioridad máxima) ═══",
            f"{user_prompt or '(sin instrucciones — usa tu criterio según el dataset)'}",
            "═══════════════════════════════════════════════════",
            "",
            "PRIORIDADES GLOBALES:",
            "\n".join(f"- {r}" for r in _GLOBAL_STYLE_RULES),
            "",
            "TEMA Y BASE VISUAL RECOMENDADA:",
            theme_rules_text,
            "",
            "PÁGINAS PARA EL NAVBAR:",
            nav_info,
            "",
            "REGLAS TÉCNICAS:",
            "\n".join(f"- {r}" for r in rules),
            "",
            "Genera base.html ahora:",
        ]
    )
    return _base_system(), user_text


# ── 5) TEMPLATE POR PÁGINA ────────────────────────────────────────────────

def build_page_requirements(page_type: str) -> str:
    spec = _PAGE_REQUIREMENTS.get(page_type, _PAGE_REQUIREMENTS["other"])

    lines = ["REGLAS ESTRUCTURALES (prioridad alta):"]
    lines.extend(f"- {rule}" for rule in spec["structural"])
    lines.append("")
    lines.append("GUÍA VISUAL (subordinada al prompt del usuario):")
    lines.extend(f"- {rule}" for rule in spec["visual"])
    return "\n".join(lines)


def build_tailwind_guidance() -> str:
    lines = ["GUÍA TAILWIND ESTRUCTURAL:"]
    lines.extend(f"- {rule}" for rule in _TAILWIND_GUIDANCE["structural"])
    lines.append("")
    lines.append("GUÍA TAILWIND VISUAL:")
    lines.extend(f"- {rule}" for rule in _TAILWIND_GUIDANCE["visual"])
    return "\n".join(lines)


def prompt_template(
    *,
    page,
    fields,
    sample_items,
    site_type,
    site_title,
    user_prompt,
    all_pages,
    real_fields=None,
    real_url_names=None,
):
    is_list = page.get("is_list", False)
    is_detail = page.get("is_detail", False)

    nav_links = "\n".join(
        f"  {p['name']}: {p['url']}" for p in all_pages if not p.get("is_detail")
    )

    detail_page = next((p for p in all_pages if p.get("is_detail")), None)
    detail_url_name = detail_page["name"] if detail_page else "detail"

    list_page = next((p for p in all_pages if p.get("is_list")), None)
    list_url_name = list_page["name"] if list_page else "catalog"

    if is_list:
        context_hint = (
            "CONTEXTO: 'items' (queryset paginado de Item), 'site_title' y opcionalmente 'q'.\n"
            "Usa {% for item in items %} para iterar.\n"
            f"Enlace a detalle: {{% url '{detail_url_name}' item.pk %}}"
        )
    elif is_detail:
        context_hint = (
            "CONTEXTO: 'item' (objeto Item individual), 'site_title' y opcionalmente 'related'.\n"
            "Muestra los campos relevantes del item de forma clara y ordenada.\n"
            f"Enlace de vuelta: {{% url '{list_url_name}' %}}."
        )
    else:
        context_hint = (
            "CONTEXTO: 'site_title' e 'items' (primeros 6 para featured).\n"
            "Es la portada del sitio. Debe presentar el proyecto y facilitar la exploración del contenido."
        )

    page_kind = "list" if is_list else ("detail" if is_detail else ("home" if page["name"] == "home" else "other"))
    page_requirements_text = build_page_requirements(page_kind)
    tailwind_guidance_text = build_tailwind_guidance()
    priority_rules_text = build_priority_rules_text()
    theme_rules_text = build_theme_rules_text()

    rules = [
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con {% extends 'base.html' %}. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```html o cualquier bloque Markdown. HTML puro.",
        "USA {% extends 'base.html' %} y {% block content %}...{% endblock %}.",
        "USA Tailwind CSS (CDN ya en base.html). Sin <style> extenso.",
        "DISEÑO: sigue fielmente el estilo indicado en el prompt del usuario para colores, tipografía, layout y tono visual.",
        "Si no hay indicación de colores, usa una paleta neutra y coherente con el tipo de sitio; no fuerces diseño oscuro salvo que sea razonable.",
        context_hint,
        "Usa condicionales Django para campos opcionales cuando haga falta.",
        "Nombres de campo: usa los 'key' del schema directamente como atributos del modelo.",
        "CRÍTICO: todos los campos del modelo son strings o tipos simples. NUNCA uses item.campo.subcampo.",
        "Usa iconos SVG inline solo cuando sumen claridad real.",
        "Las animaciones, si existen, deben ser discretas y coherentes con el prompt del usuario.",
    ]

    if real_fields:
        rules.append(f"CAMPOS EXACTOS del modelo Item (úsalos tal cual, ninguno más): {real_fields}")
        rules.append("NUNCA uses un campo que no esté en esa lista.")

    if real_url_names:
        detail_page_name = next(
            (
                name
                for name, _view_name in real_url_names.items()
                if any(p.get("is_detail") and p["name"] == name for p in all_pages)
            ),
            None,
        )
        url_rules = "NOMBRES EXACTOS de las URLs para usar en {% url %}:\n"
        for _name, view_name in real_url_names.items():
            url_rules += f"  - {{% url '{view_name}' %}}\n"
        if detail_page_name:
            url_rules += f"  - Para detalle con pk: {{% url '{real_url_names[detail_page_name]}' item.pk %}}\n"
        rules.append(url_rules)
        rules.append("NUNCA inventes nombres de URL que no estén en esa lista.")

    user_text = "\n".join(
        [
            f"SITIO: {site_title}  |  TIPO: {site_type}",
            "",
            "REGLAS DE PRIORIDAD:",
            priority_rules_text,
            "",
            "═══ INSTRUCCIÓN DEL USUARIO (prioridad máxima) ═══",
            f"{user_prompt or '(sin instrucciones — usa tu criterio según el dataset)'}",
            "═══════════════════════════════════════════════════",
            "",
            "PRIORIDADES GLOBALES:",
            "\n".join(f"- {r}" for r in _GLOBAL_STYLE_RULES),
            "",
            "TEMA Y BASE VISUAL RECOMENDADA:",
            theme_rules_text,
            "",
            f"PÁGINA: {page['name']} — {page['description']}",
            "",
            "NAVEGACIÓN:",
            nav_links,
            "",
            "CAMPOS:",
            _fields_info(fields),
            "",
            "DATOS DE EJEMPLO:",
            _samples_info(sample_items, 3),
            "",
            page_requirements_text,
            "",
            tailwind_guidance_text,
            "",
            "REGLAS TÉCNICAS:",
            "\n".join(f"- {r}" for r in rules),
            "",
            f"Genera el template '{page['name']}' ahora:",
        ]
    )

    example_kind = "list" if is_list else ("detail" if is_detail else "home")
    example_html = get_example(site_type, example_kind, user_prompt)
    if example_html:
        example_html = example_html[:1500]
        user_text += (
            "\n\nEJEMPLO DE REFERENCIA (inspiración estructural y visual secundaria — "
            "adapta los campos reales y NO contradigas el prompt del usuario; "
            "NO copies esto tal cual):\n"
        )
        user_text += example_html

    return _base_system(), user_text


# ── 6) LOAD_DATA.PY ────────────────────────────────────────────────────────

def prompt_load_data(*, fields, sample_items, api_url, main_collection_path=None, real_fields=None):
    mapping = "\n".join(f"  dataset['{f['key']}'] → Item.{f['key']}" for f in fields[:10])
    priority_rules_text = build_priority_rules_text()

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
            f"RUTA EXACTA de la colección en el JSON: {path_str}. Accede navegando esa ruta desde la raíz del JSON."
        )

    user_text = "\n".join(
        [
            f"API URL: {api_url}",
            "",
            "REGLAS DE PRIORIDAD:",
            priority_rules_text,
            "",
            "MAPPING KEY → CAMPO MODELO:",
            mapping,
            "",
            "CAMPOS COMPLETOS:",
            _fields_info(fields),
            "",
            "EJEMPLO DE DATOS:",
            _samples_info(sample_items, 3),
            "",
            "REGLAS:",
            "\n".join(f"- {r}" for r in rules),
            "",
            "Genera load_data.py ahora:",
        ]
    )
    return _base_system(), user_text