"""
templates.py — Plantillas base Dark & Sharp con Tailwind CDN.

Cada plantilla tiene el diseño ya hecho. El LLM solo rellena dos fragmentos:
  - HOME_FIELDS_PLACEHOLDER  → bloque de campos dentro de cada card del listado
  - DETAIL_FIELDS_PLACEHOLDER → bloque de campos en la vista de detalle

Plantillas disponibles:
  - catalog  → grid de cards con hover iluminado
  - blog     → lista vertical de artículos
  - portfolio → grid asimétrico con overlay
  - other    → tabla limpia de filas
"""

from __future__ import annotations

HOME_FIELDS_PLACEHOLDER   = "%%HOME_FIELDS%%"
DETAIL_FIELDS_PLACEHOLDER = "%%DETAIL_FIELDS%%"

# ─────────────────────────── BASE HTML compartido ────────────────────────────
# Todas las plantillas comparten el mismo base_html: fondo oscuro, Tailwind CDN,
# navbar mínima con el título del sitio y {{ content }} en el centro.

BASE_HTML = """\
<!doctype html>
<html lang="es" class="bg-[#0a0a0a]">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ site.title }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    body { font-family: 'Inter', sans-serif; }
    .neon-border { box-shadow: 0 0 0 1px #22c55e, 0 0 12px 0 rgba(34,197,94,0.15); }
    .card-hover { transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .card-hover:hover { transform: translateY(-2px); }
    {{ css }}
  </style>
</head>
<body class="bg-[#0a0a0a] text-gray-100 min-h-screen">
  <nav class="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
    <span class="text-green-400 font-mono font-bold tracking-wider text-sm uppercase">{{ site.title }}</span>
    <span class="text-xs text-gray-600 font-mono">{{ site.type }}</span>
  </nav>
  <main class="max-w-7xl mx-auto px-6 py-10">
    {{ content }}
  </main>
</body>
</html>"""


# ─────────────────────────── CATALOG ────────────────────────────────────────
# Grid de cards oscuras. Hover con borde verde neón.

CATALOG_HOME = """\
<div class="mb-8">
  <h1 class="text-3xl font-black text-white tracking-tight">{{ site.title }}</h1>
  <p class="text-gray-500 font-mono text-sm mt-1">{{ site.type }}</p>
</div>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
{% for it in items %}
  <a href="/edit/{{ site.id }}/render/{{ it.index }}/"
     class="block bg-[#111] border border-gray-800 rounded-xl p-5 card-hover hover:neon-border group">
    <div class="space-y-2">
      """ + HOME_FIELDS_PLACEHOLDER + """
    </div>
    <div class="mt-4 flex items-center text-green-400 text-xs font-mono opacity-0 group-hover:opacity-100 transition-opacity">
      Ver detalle →
    </div>
  </a>
{% endfor %}
</div>"""

CATALOG_DETAIL = """\
<div class="mb-6">
  <a href="/edit/{{ site.id }}/render/"
     class="text-green-400 font-mono text-sm hover:text-green-300 transition-colors">← Volver</a>
</div>
<div class="bg-[#111] border border-gray-800 rounded-2xl p-8 max-w-2xl">
  <div class="space-y-4">
    """ + DETAIL_FIELDS_PLACEHOLDER + """
  </div>
</div>"""


# ─────────────────────────── BLOG ───────────────────────────────────────────
# Lista vertical de artículos. Fecha y categoría en verde neón.

BLOG_HOME = """\
<div class="mb-10">
  <h1 class="text-4xl font-black text-white tracking-tight">{{ site.title }}</h1>
  <div class="w-12 h-1 bg-green-400 mt-3 rounded-full"></div>
</div>
<div class="space-y-4">
{% for it in items %}
  <a href="/edit/{{ site.id }}/render/{{ it.index }}/"
     class="block bg-[#111] border border-gray-800 rounded-xl p-6 card-hover hover:neon-border group">
    <div class="flex items-start justify-between gap-4">
      <div class="space-y-2 flex-1">
        """ + HOME_FIELDS_PLACEHOLDER + """
      </div>
      <span class="text-green-400 font-mono text-lg opacity-0 group-hover:opacity-100 transition-opacity shrink-0">→</span>
    </div>
  </a>
{% endfor %}
</div>"""

BLOG_DETAIL = """\
<div class="mb-8">
  <a href="/edit/{{ site.id }}/render/"
     class="text-green-400 font-mono text-sm hover:text-green-300 transition-colors">← Volver al listado</a>
</div>
<article class="max-w-2xl">
  <div class="bg-[#111] border border-gray-800 rounded-2xl p-8 space-y-5">
    """ + DETAIL_FIELDS_PLACEHOLDER + """
  </div>
</article>"""


# ─────────────────────────── PORTFOLIO ──────────────────────────────────────
# Grid de cards con imagen de fondo y overlay oscuro.

PORTFOLIO_HOME = """\
<div class="mb-8">
  <h1 class="text-4xl font-black text-white tracking-tight">{{ site.title }}</h1>
  <div class="w-12 h-1 bg-green-400 mt-3 rounded-full"></div>
</div>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
{% for it in items %}
  <a href="/edit/{{ site.id }}/render/{{ it.index }}/"
     class="block bg-[#111] border border-gray-800 rounded-2xl overflow-hidden card-hover hover:neon-border group">
    <div class="p-6 space-y-3">
      """ + HOME_FIELDS_PLACEHOLDER + """
    </div>
    <div class="px-6 pb-4">
      <span class="text-green-400 font-mono text-xs opacity-0 group-hover:opacity-100 transition-opacity">Ver proyecto →</span>
    </div>
  </a>
{% endfor %}
</div>"""

PORTFOLIO_DETAIL = """\
<div class="mb-8">
  <a href="/edit/{{ site.id }}/render/"
     class="text-green-400 font-mono text-sm hover:text-green-300 transition-colors">← Volver</a>
</div>
<div class="bg-[#111] border border-gray-800 rounded-2xl p-8 max-w-3xl">
  <div class="space-y-5">
    """ + DETAIL_FIELDS_PLACEHOLDER + """
  </div>
</div>"""


# ─────────────────────────── OTHER ──────────────────────────────────────────
# Tabla limpia con filas alternadas.

OTHER_HOME = """\
<div class="mb-8">
  <h1 class="text-3xl font-black text-white tracking-tight">{{ site.title }}</h1>
  <p class="text-gray-500 font-mono text-sm mt-1">{{ site.type }}</p>
</div>
<div class="bg-[#111] border border-gray-800 rounded-xl overflow-hidden">
{% for it in items %}
  <a href="/edit/{{ site.id }}/render/{{ it.index }}/"
     class="flex items-center gap-4 px-6 py-4 border-b border-gray-800 last:border-0 hover:bg-[#1a1a1a] hover:text-green-400 transition-colors group font-mono text-sm">
    <span class="text-gray-600 w-6 shrink-0">{{ it.index }}</span>
    <div class="flex-1 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      """ + HOME_FIELDS_PLACEHOLDER + """
    </div>
    <span class="text-green-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">→</span>
  </a>
{% endfor %}
</div>"""

OTHER_DETAIL = """\
<div class="mb-6">
  <a href="/edit/{{ site.id }}/render/"
     class="text-green-400 font-mono text-sm hover:text-green-300 transition-colors">← Volver</a>
</div>
<div class="bg-[#111] border border-gray-800 rounded-xl overflow-hidden max-w-2xl">
  <div class="divide-y divide-gray-800">
    """ + DETAIL_FIELDS_PLACEHOLDER + """
  </div>
</div>"""


# ─────────────────────────── REGISTRO ───────────────────────────────────────

TEMPLATES: dict[str, dict[str, str]] = {
    "catalog": {
        "base_html":   BASE_HTML,
        "home_html":   CATALOG_HOME,
        "detail_html": CATALOG_DETAIL,
    },
    "blog": {
        "base_html":   BASE_HTML,
        "home_html":   BLOG_HOME,
        "detail_html": BLOG_DETAIL,
    },
    "portfolio": {
        "base_html":   BASE_HTML,
        "home_html":   PORTFOLIO_HOME,
        "detail_html": PORTFOLIO_DETAIL,
    },
    "other": {
        "base_html":   BASE_HTML,
        "home_html":   OTHER_HOME,
        "detail_html": OTHER_DETAIL,
    },
}


def get_template(site_type: str) -> dict[str, str]:
    """Devuelve la plantilla base para el site_type dado. Fallback a 'other'."""
    return TEMPLATES.get(site_type, TEMPLATES["other"])
