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

#from .examples import get_example
from .design.theme_rules import build_theme_rules_text

from .design.snippets import get_snippet

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
            "IMÁGENES en cards: usa siempre aspect-square o aspect-video con object-cover en vez de altura fija (h-48, h-64...). Ejemplo correcto: class='w-full aspect-square object-cover rounded-t-2xl'. PROHIBIDO usar h-48, h-56, h-64 o cualquier altura fija en imágenes de cards.",

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
            "Si existe imagen y encaja con la estética, muéstrala de forma destacada. Usa aspect-square o aspect-video con object-cover, nunca altura fija. Ejemplo: class='w-full aspect-square object-cover rounded-2xl'.",
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

    if site_type == "portfolio":
        example = json.dumps({
            "pages": [
                {
                    "name": "home",
                    "url": "/",
                    "template": "siteapp/home.html",
                    "view_name": "home",
                    "description": "Landing principal: presentación, proyectos destacados y contacto",
                    "is_list": False,
                    "is_detail": False,
                },
                {
                    "name": "project_detail",
                    "url": "/project/<pk>/",
                    "template": "siteapp/project_detail.html",
                    "view_name": "project_detail",
                    "description": "Detalle completo de un proyecto individual",
                    "is_list": False,
                    "is_detail": True,
                },
            ]
        }, ensure_ascii=False, indent=2)
    else:
        example = json.dumps({
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
        }, ensure_ascii=False, indent=2)

    if site_type == "portfolio":
        rules = [
            "Devuelve SOLO JSON con key 'pages' (lista de páginas).",
            "CRÍTICO: esto es un PORTFOLIO, no un catálogo. La estructura es completamente diferente.",
            "MÍNIMO OBLIGATORIO: landing (home) + detalle de proyecto. Solo estas dos.",
            "La landing es una página única que contiene TODO: hero con presentación, grid de proyectos, skills y contacto. NO existe página de listado separada.",
            "is_list=false en TODAS las páginas sin excepción.",
            "Solo UNA página con is_detail=true para ver un proyecto individual.",
            "Opcional según el prompt: about o contact como página separada. Máximo 3 páginas en total.",
            "La de detalle siempre con url que contenga <pk>.",
            "Nombres en snake_case. URLs en kebab-case.",
            "Cada página: name, url, template, view_name, description, is_list, is_detail.",
        ]
    elif site_type == "dashboard":
        rules = [
            "Devuelve SOLO JSON con key 'pages' (lista de páginas).",
            "MÍNIMO OBLIGATORIO: panel principal (home) + listado de datos + detalle.",
            "CRÍTICO: la página home es el panel de control, no el listado completo.",
            "El listado completo va SIEMPRE en página separada con is_list=true.",
            "Solo UNA página con is_list=true. Solo UNA con is_detail=true.",
            "La de detalle siempre con url que contenga <pk>.",
            "Opcionales según el prompt: estadísticas, reportes, configuración. Máximo 5 páginas.",
            "Nombres en snake_case. URLs en kebab-case.",
            "Cada página: name, url, template, view_name, description, is_list, is_detail.",
        ]
    else:
        # catalog, blog, other
        rules = [
            "Devuelve SOLO JSON con key 'pages' (lista de páginas).",
            "MÍNIMO OBLIGATORIO: home + listado + detalle. Siempre estas tres.",
            "CRÍTICO: la página 'home' es una portada o landing; no debe ser el listado completo.",
            "CRÍTICO: el listado completo va SIEMPRE en una página separada con is_list=true.",
            "Opcionales según el prompt: about, contact, categorías, búsqueda, faq. Máximo 6 páginas.",
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
        "  Si un campo se llama '*_url' pero hay otro campo con el mismo prefijo sin '_url' que contiene el valor legible (ej: 'language' vs 'languages_url'), usa el campo sin '_url' como CharField y descarta el que acaba en '_url'.",
        "  Texto largo o HTML → TextField(blank=True)",
        "  Texto corto → CharField(max_length=500, blank=True)",
        "  Entero → IntegerField(null=True, blank=True)",
        "  Decimal/precio → DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)",
        "  Fecha → DateField(null=True, blank=True)",
        "  Booleano → BooleanField(null=True, blank=True)",
        "  OBJETO ANIDADO (dict con subkeys) → CharField(max_length=500, blank=True) guardando solo el valor más representativo como string.",
        "  LISTA de valores (array) → crea UN SOLO campo IntegerField(null=True, blank=True) con el nombre original más sufijo '_count' (ej: episode → episode_count, characters → characters_count). ELIMINA el campo original, NO lo dupliques. NUNCA uses CharField ni JSONField para una lista.",
        "Todos los campos opcionales (blank=True / null=True).",
        "Si existe un campo que actúe como identificador único del registro (url, isbn, código, id externo...), añádele unique=True para evitar duplicados al ejecutar load_data varias veces.",
        "Añade created_at = models.DateTimeField(auto_now_add=True).",
        "__str__ devuelve el campo más representativo.",
        "Nombres de campo en snake_case. NO uses 'id' como nombre.",
        "Solo importa 'from django.db import models'.",
        "NUNCA uses JSONField para ningún campo. NUNCA uses CharField para guardar una lista — usa siempre IntegerField con el count.",
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
        "La view de listado acepta búsqueda server-side: q = request.GET.get('q', ''). Si q no está vacío, filtra usando Q objects (from django.db.models import Q) combinados con |. Ejemplo: Item.objects.filter(Q(name__icontains=q) | Q(status__icontains=q)). NUNCA uses el operador | entre querysets completos (filter(...) | filter(...)). NUNCA uses lookups relacionales como campo__name__icontains. Usa siempre campo__icontains directamente. Pasa 'q' al contexto.",
        "La view de listado DEBE usar paginación:",
        "  from django.core.paginator import Paginator",
        "  queryset = Item.objects.all().order_by('-id')",
        "  paginator = Paginator(queryset, 12)",
        "  page_number = request.GET.get('page', 1)",
        "  page_obj = paginator.get_page(page_number)",
        "Pasar SOLO 'page_obj' al contexto. NUNCA uses 'items' como nombre de variable.",
        "La view de detalle: recibe pk y usa get_object_or_404(Item, pk=pk).",
        "La view de detalle ADEMÁS pasa 'related' al contexto: related = Item.objects.exclude(pk=item.pk).order_by('?')[:3]",
        "Páginas no-listado no-detalle (home, about...): pasa SIEMPRE la variable con nombre exacto 'featured' al contexto: featured = Item.objects.all().order_by('-id')[:6]. NUNCA uses 'items' como nombre de variable.",        
        "Cada view pasa 'site_title' al contexto.",
        "Sin autenticación, sin formularios complejos.",
        "CRÍTICO: usa ÚNICAMENTE function-based views. PROHIBIDO usar clases, métodos como get_context_data, o cualquier herencia de View, ListView, DetailView o similar.",
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

def prompt_base_template(*, site_title, site_type, user_prompt, all_pages, design_system=None):
    nav_pages = [p for p in all_pages if not p.get("is_detail")]
    nav_info = json.dumps(
        [{"name": p["name"], "url": p["url"], "view_name": p["view_name"]} for p in nav_pages],
        ensure_ascii=False,
    )
    priority_rules_text = build_priority_rules_text()
    theme_rules_text = build_theme_rules_text()
    
    rules = [
        f"CRÍTICO ABSOLUTO: el tipo de sitio es '{site_type}'. " + (
            "Es un PORTFOLIO PÚBLICO. PROHIBIDO incluir cualquier elemento de autenticación: "
            "sin login, sin logout, sin registro, sin {% if user.is_authenticated %}. "
            "La nav solo tiene links a las secciones del portfolio. IGNORA cualquier regla posterior sobre auth."
            if site_type == "portfolio" else
            "Incluye login y logout en la navegación."
        ),
        "CRÍTICO: usa EXCLUSIVAMENTE clases Tailwind CSS estándar válidas para CDN. PROHIBIDO inventar clases custom como 'card_base', 'container_narrow', 'badge_base' o cualquier nombre que no sea una utilidad Tailwind real.",
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con '<!doctype html>'. Sin nada antes.",
        "CRÍTICO: PROHIBIDO usar ```, ```html o cualquier bloque Markdown. HTML puro.",
        "Incluye <script src='https://cdn.tailwindcss.com'></script> en <head>.",
        "TIPOGRAFÍA: si el usuario indica combinación tipográfica concreta (serif, sans, mono, etc.), refléjala en el documento. Si no indica ninguna, usa Inter como fallback razonable.",
        "META TAGS OBLIGATORIOS en <head>: charset, viewport, description con site_title, og:title.",
        "FAVICON: añade <link rel='icon' href='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>'.",
        "NAVBAR: clara, usable y coherente con la estética del usuario. Puede ser sobria, minimalista, editorial o visual, pero debe incluir navegación funcional.",
        "NAVBAR ACTIVO: usa request.path para marcar el link activo con el tratamiento visual que mejor encaje con el estilo pedido.",
    ] + ([
        f"NAVBAR AUTH: incluye SIEMPRE esta lógica Django exacta, pero adapta sus clases al diseño pedido por el usuario:\n{_AUTH_BLOCK}",
    ] if site_type != "portfolio" else []) + [
        "Links del navbar usan {% url 'view_name' %}.",
        "COLORES: si el usuario da colores HEX o paleta concreta, aplícalos explícitamente en fondo, texto, links, botones y estados activos usando clases Tailwind y/o valores arbitrarios como bg-[#111111].",
        "Si no hay indicación de colores, usa una base neutra y coherente con el tipo de sitio; no fuerces oscuro por defecto salvo que tenga sentido.",
        "LAYOUT OBLIGATORIO: el <body> debe tener las clases 'min-h-screen flex flex-col'. El <main> debe tener la clase 'flex-1'. Esto garantiza que el footer siempre queda pegado al fondo aunque el contenido no llene la pantalla.",
        "Incluye {% block content %}{% endblock %} dentro del <main class='flex-1'> bien proporcionado. El ancho del contenido interior puede ser estrecho, medio o amplio según el prompt del usuario.",
        "FOOTER OBLIGATORIO: nombre del sitio + navegación básica + copyright con © {% now 'Y' %} {{ site_title }}.",
        "ANIMACIONES: si las usas, deben ser discretas. Puedes añadir utilidades CSS mínimas para fade-in suave, pero evita efectos llamativos si el prompt es sobrio o editorial.",
        "NO uses JavaScript propio salvo necesidad mínima estructural.",
    ]

    design_system_text = ""
    if design_system:
        lines = ["SISTEMA DE CLASES (úsalos exactamente para estos elementos, sin inventar alternativas):"]
        labels = {
            "container": "Contenedor principal",
            "card": "Tarjeta",
            "h1": "Título H1",
            "h2": "Título H2",
            "h3": "Título H3",
            "text_muted": "Texto secundario/metadatos",
            "badge_positive": "Badge positivo/activo",
            "badge_negative": "Badge negativo/error",
            "badge_neutral": "Badge neutro",
            "btn_primary": "Botón primario",
            "btn_secondary": "Botón secundario",
            "input": "Input de formulario",
            "link": "Enlace",
            "divider": "Separador",
        }
        for key, label in labels.items():
            if key in design_system:
                lines.append(f"  - {label}: {design_system[key]}")
        design_system_text = "\n".join(lines)

    user_text = "\n".join(
        [
            f"SITIO: {site_title}  |  TIPO: {site_type}",
            "",
            "REGLAS DE PRIORIDAD:",
            priority_rules_text,
            "",
            design_system_text,
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
    design_system=None,
    preset_description="",
    preset_id="",
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
            "CONTEXTO: 'page_obj' (queryset paginado de Item), 'site_title' y opcionalmente 'q'.\n"
            "CRÍTICO: usa SIEMPRE {% for item in page_obj %} para iterar. NUNCA uses 'items'.\n"
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
            "CONTEXTO: 'site_title' y 'featured' (lista de los primeros 6 items para destacados).\n"
            "CRÍTICO: usa SIEMPRE {% for item in featured %} para iterar los destacados. NUNCA uses 'items'.\n"
            "Es la portada del sitio. Debe presentar el proyecto y facilitar la exploración del contenido."
        )

    page_kind = "list" if is_list else ("detail" if is_detail else ("home" if page["name"] == "home" else "other"))
    page_requirements_text = build_page_requirements(page_kind)
    tailwind_guidance_text = build_tailwind_guidance()
    priority_rules_text = build_priority_rules_text()
    theme_rules_text = build_theme_rules_text()

    rules = [
        "CRÍTICO: tu respuesta debe empezar EXACTAMENTE con {% extends 'base.html' %}. Sin nada antes.",
        "CRÍTICO: base.html ya contiene navbar y footer. PROHIBIDO añadir <header>, <nav>, <footer> o cualquier navbar/footer propio dentro del {% block content %}. Solo mete contenido de página.",
        "CRÍTICO: PROHIBIDO usar ```, ```html o cualquier bloque Markdown. HTML puro.",
        "USA {% extends 'base.html' %} y {% block content %}...{% endblock %}.",
        "USA Tailwind CSS (CDN ya en base.html). Sin <style> extenso.",
        "DISEÑO: sigue fielmente el estilo indicado en el prompt del usuario para colores, tipografía, layout y tono visual.",
        "Si no hay indicación de colores, usa una paleta neutra y coherente con el tipo de sitio; no fuerces diseño oscuro salvo que sea razonable.",
        context_hint,
        "Usa condicionales Django para campos opcionales cuando haga falta.",
        "Nombres de campo: usa los 'key' del schema directamente como atributos del modelo.",
        "CRÍTICO: usa EXCLUSIVAMENTE clases Tailwind CSS estándar válidas para CDN. PROHIBIDO inventar clases custom como 'card_base', 'container_narrow', 'badge_base' o cualquier nombre que no sea una utilidad Tailwind real.",
        "CRÍTICO: PROHIBIDO inventar clases Tailwind que no existen. En concreto: hover:glow-*, hover:shimmer, hover:neon-*, hover:pulse-*, hover:float, hover:levitate NO son clases Tailwind reales. Para efectos hover usa exclusivamente: hover:opacity-*, hover:scale-*, hover:shadow-*, hover:ring-*, hover:bg-*, hover:text-*.",
        "CRÍTICO ABSOLUTO: el SISTEMA DE CLASES proporcionado arriba es OBLIGATORIO. Para cada elemento (tarjeta, contenedor, título, badge, botón, input, enlace) debes usar EXACTAMENTE las clases indicadas en el sistema, sin excepción. No las sustituyas, no las combines con inventos, no las ignores.",
        "VERIFICACIÓN MENTAL OBLIGATORIA: antes de escribir cualquier clase CSS, pregúntate '¿es esta una utilidad Tailwind real?'. Si no estás seguro, usa las clases del SISTEMA DE CLASES o utilidades básicas como flex, grid, p-4, text-sm, font-bold.",
        "CRÍTICO: todos los campos del modelo son strings o tipos simples, NUNCA objetos. NUNCA uses item.campo.subcampo ni item.campo.atributo. Si origin, location o cualquier campo similar existe, accede como {{ item.origin }}, nunca como {{ item.origin.name }}.",
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

    design_system_text = ""
    if design_system:
        lines = ["SISTEMA DE CLASES (úsalos exactamente para estos elementos, sin inventar alternativas):"]
        labels = {
            "container": "Contenedor principal",
            "card": "Tarjeta",
            "h1": "Título H1",
            "h2": "Título H2",
            "h3": "Título H3",
            "text_muted": "Texto secundario/metadatos",
            "badge_positive": "Badge positivo/activo",
            "badge_negative": "Badge negativo/error",
            "badge_neutral": "Badge neutro",
            "btn_primary": "Botón primario",
            "btn_secondary": "Botón secundario",
            "input": "Input de formulario",
            "link": "Enlace",
            "divider": "Separador",
        }
        for key, label in labels.items():
            if key in design_system:
                lines.append(f"  - {label}: {design_system[key]}")
        design_system_text = "\n".join(lines)

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
            preset_description,
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

    #example_kind = "list" if is_list else ("detail" if is_detail else "home")
    #example_html = get_example(site_type, example_kind, user_prompt)
    #if example_html:
    #    example_html = example_html[:1500]
    #    user_text += (
    #        "\n\nEJEMPLO DE REFERENCIA (inspiración estructural y visual secundaria — "
    #        "adapta los campos reales y NO contradigas el prompt del usuario; "
    #        "NO copies esto tal cual):\n"
    #    )
    #    user_text += example_html

    # Snippets de referencia
    preset_id = preset_id or ""
    page_kind = "list_row" if is_list else ("card" if is_detail else "hero")
    snippet = get_snippet(preset_id, page_kind)
    if snippet:
        user_text += (
            "\n\nSNIPPET DE REFERENCIA (patrón visual del preset — "
            "adapta los campos reales, NO COPIES ESTO TAL CUAL):\n"
        )
        user_text += snippet

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
        f"CRÍTICO: el comando hace GET EXACTAMENTE a esta URL: '{api_url}'. No uses otra URL aunque conozcas APIs similares. Esta URL es la fuente de datos real del proyecto.",
        "PAGINACIÓN: muchas APIs devuelven los datos paginados con un campo 'next' (u otro nombre) que contiene la URL de la siguiente página. Si existe ese campo en la respuesta, itera siguiendo esa URL hasta que sea null/None para cargar todos los datos, no solo la primera página.",
        "CRITICO: usa get_or_create separando campos en defaults:",
        "Item.objects.get_or_create(campo_id=valor, defaults={'campo1': val1, 'campo2': val2})",
        "Si no hay campo único identificador, usa update_or_create o simplemente create().",
        "Si un campo del dataset es una LISTA (array), guarda solo la longitud como entero: len(raw_item['campo']) o 0 si es None. El campo en el modelo se llamará con sufijo '_count' si así lo define el modelo (ej: episode_count = len(raw_item.get('episode') or [])).",
        "CRÍTICO: el JSON ya viene parseado como dict Python. NUNCA uses json.loads() sobre un campo que ya es dict.",
        "Accede directamente: raw_item['origin']['name'], NO json.loads(raw_item['origin'])['name'].",
        "Ejemplo: rating = {'rate': 4.5, 'count': 120} → guardar str(raw_item['rating']['rate'])",
        "Limpia valores: precios → Decimal(str(valor).replace('$','').strip()), el precio puede venir como float o como string con '$', usa siempre str() primero para evitar errores. Fechas → parsear, enteros → int().",
        "Si falla la conversión → None (no romper el comando).",
        "CRÍTICO: para campos CharField/TextField NUNCA guardes None. Usa string vacío como fallback: raw_item.get('campo') or ''. Reserva None solo para IntegerField, DecimalField, DateField o BooleanField.",
        "Informa del progreso: dentro del bucle usa self.stdout.write() para indicar cuántos registros se han procesado en esa página (ej: f'Página procesada: {len(results)} registros'). Al FINAL del handle(), fuera del bucle, escribe un mensaje de éxito con el total acumulado.",
        "try/except general que capture CUALQUIER excepción (except Exception as e), no solo requests.RequestException. Así si falla una conversión de tipo o un get_or_create, el error se muestra pero no rompe el comando entero.",
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


# ── 7) DESIGN SYSTEM ───────────────────────────────────────────────────────

def prompt_design_system(*, site_type, user_prompt, preset_description=""):
    system = (
        "Eres un experto en diseño web y Tailwind CSS. "
        "Devuelves SOLO un objeto JSON válido, sin Markdown ni texto extra. "
        "PROHIBIDO usar ```. Tu respuesta empieza directamente con { y termina con }."
    )

    keys = [
        "container", "card", "h1", "h2", "h3", "text_muted",
        "badge_positive", "badge_negative", "badge_neutral",
        "btn_primary", "btn_secondary", "input", "link", "divider",
    ]

    examples = [
        {
            "user_prompt": "Dark background, pure black (#0a0a0a), white text, emerald green accents (#10b981), bold typography",
            "site_type": "catalog",
            "output": {
                "container": "max-w-7xl mx-auto px-6 sm:px-8",
                "card": "rounded-2xl border border-[#222222] bg-[#111111] p-4",
                "h1": "text-4xl font-bold tracking-tight text-white",
                "h2": "text-2xl font-semibold text-white",
                "h3": "text-lg font-bold text-white",
                "text_muted": "text-sm text-[#6b7280]",
                "badge_positive": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-[#10b981] text-white",
                "badge_negative": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-red-500 text-white",
                "badge_neutral": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-blue-500 text-white",
                "btn_primary": "inline-block px-4 py-2 rounded-xl bg-[#10b981] text-white font-semibold hover:bg-[#0f9d65] transition-colors",
                "btn_secondary": "inline-block px-4 py-2 rounded-xl border border-[#10b981] text-[#10b981] font-semibold hover:bg-[#10b981] hover:text-white transition-colors",
                "input": "w-full rounded-xl border border-[#222222] bg-[#111111] px-4 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-[#10b981]",
                "link": "text-[#10b981] hover:text-[#0f9d65] transition-colors",
                "divider": "border-t border-[#222222] my-8",
            }
        },
        {
            "user_prompt": "Minimal editorial style, white background, serif typography, no colors, clean and sober",
            "site_type": "blog",
            "output": {
                "container": "max-w-3xl mx-auto px-6",
                "card": "border-b border-gray-200 py-8",
                "h1": "text-5xl font-serif font-bold tracking-tight text-gray-900",
                "h2": "text-3xl font-serif font-bold text-gray-900",
                "h3": "text-xl font-serif font-semibold text-gray-900",
                "text_muted": "text-sm text-gray-500",
                "badge_positive": "text-xs uppercase tracking-widest text-green-700",
                "badge_negative": "text-xs uppercase tracking-widest text-red-700",
                "badge_neutral": "text-xs uppercase tracking-widest text-gray-500",
                "btn_primary": "inline-block px-6 py-2 border border-gray-900 text-sm font-medium text-gray-900 hover:bg-gray-900 hover:text-white transition-colors",
                "btn_secondary": "inline-block text-sm underline underline-offset-4 text-gray-700 hover:text-black",
                "input": "w-full border-b border-gray-300 bg-transparent px-0 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-gray-900",
                "link": "underline underline-offset-4 text-gray-800 hover:text-black",
                "divider": "border-t border-gray-200 my-10",
            }
        },
        {
            "user_prompt": "Modern dashboard, dark slate (#1e293b), electric blue accents (#3b82f6), cards with shadow, data-heavy",
            "site_type": "dashboard",
            "output": {
                "container": "max-w-7xl mx-auto px-8",
                "card": "rounded-xl bg-[#0f172a] shadow-lg border border-slate-700 p-6",
                "h1": "text-3xl font-bold text-white",
                "h2": "text-xl font-semibold text-white",
                "h3": "text-base font-semibold text-slate-200",
                "text_muted": "text-sm text-slate-400",
                "badge_positive": "inline-flex items-center rounded-md px-2 py-1 text-xs font-mono bg-green-500/20 text-green-400",
                "badge_negative": "inline-flex items-center rounded-md px-2 py-1 text-xs font-mono bg-red-500/20 text-red-400",
                "badge_neutral": "inline-flex items-center rounded-md px-2 py-1 text-xs font-mono bg-blue-500/20 text-blue-400",
                "btn_primary": "inline-block px-4 py-2 rounded-lg bg-[#3b82f6] text-white text-sm font-medium hover:bg-blue-700 transition-colors",
                "btn_secondary": "inline-block px-4 py-2 rounded-lg border border-slate-600 text-slate-300 text-sm font-medium hover:border-blue-500 hover:text-blue-400 transition-colors",
                "input": "w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-[#3b82f6]",
                "link": "text-[#3b82f6] hover:text-blue-400 transition-colors",
                "divider": "border-t border-slate-700 my-6",
            }
        },
    ]

    examples_text = json.dumps(examples, ensure_ascii=False, indent=2)
    keys_text = ", ".join(f'"{k}"' for k in keys)

    user_text = "\n".join([
        f"TIPO DE SITIO: {site_type}",
        "",
        "INSTRUCCIÓN DEL USUARIO:",
        f"{user_prompt or '(sin instrucciones — usa criterio según el tipo de sitio)'}",
        "",
        preset_description,
        "",
        f"KEYS OBLIGATORIOS (devuelve exactamente estos, ni más ni menos): {keys_text}",
        "",
        "REGLAS:",
        "- Todas las clases deben ser utilidades Tailwind CSS válidas para CDN.",
        "- PROHIBIDO inventar clases custom como 'card_base', 'container_narrow' o similares.",
        "- Usa valores arbitrarios Tailwind como bg-[#111111] cuando el usuario especifique colores HEX.",
        "- El sistema debe ser coherente: colores, radios y tipografía deben ser consistentes entre keys.",
        "- Si el usuario no especifica colores, usa una paleta neutra coherente con el tipo de sitio.",
        "",
        "EJEMPLOS (prompt → JSON de output):",
        examples_text,
        "",
        "Genera el design system para el sitio descrito ahora:",
    ])

    return system, user_text