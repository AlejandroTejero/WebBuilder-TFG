# 🚀 Plan de Mejoras — Generación de Páginas en WebBuilder

> Documento de referencia técnico con todas las mejoras identificadas para elevar la calidad visual y funcional de los sitios generados por el LLM. Ordenado de mayor a menor impacto. Cada mejora incluye el archivo afectado y qué cambiar exactamente.

---

## Índice

1. [Mejoras en los Prompts de Templates](#1-mejoras-en-los-prompts-de-templates)
2. [Mejoras en los Ejemplos Few-Shot](#2-mejoras-en-los-ejemplos-few-shot)
3. [Mejoras en el Enriquecimiento del Prompt](#3-mejoras-en-el-enriquecimiento-del-prompt)
4. [Nuevos Tipos de Sitio](#4-nuevos-tipos-de-sitio)
5. [Mejoras en la Estructura de Páginas](#5-mejoras-en-la-estructura-de-páginas)
6. [Sistema de Temas y Paletas de Color](#6-sistema-de-temas-y-paletas-de-color)
7. [Componentes Visuales Avanzados](#7-componentes-visuales-avanzados)
8. [Mejoras en el base.html](#8-mejoras-en-el-basehtml)
9. [Mejoras Funcionales en las Views](#9-mejoras-funcionales-en-las-views)
10. [Mejoras en los Fallbacks](#10-mejoras-en-los-fallbacks)
11. [Postprocesado del HTML Generado](#11-postprocesado-del-html-generado)
12. [Resumen de Impacto por Archivo](#12-resumen-de-impacto-por-archivo)

---

## 1. Mejoras en los Prompts de Templates

**Archivo:** `utils/llm/generator_prompts.py` → función `prompt_template`

Este es el cambio de mayor impacto. Actualmente el prompt le dice al LLM "diseño oscuro moderno" sin especificar qué componentes debe incluir. El LLM siempre elige lo más seguro y genérico. La solución es prescribir los componentes visuales obligatorios según el tipo de página.

### 1.1 — Añadir sección de componentes obligatorios por tipo de página

Añadir este bloque dentro de `prompt_template`, justo antes de las reglas técnicas:

```python
VISUAL_REQUIREMENTS = {
    "home": [
        "OBLIGATORIO: Hero section con título H1 grande (text-5xl o mayor), subtítulo en text-xl, y un botón CTA prominente que enlace al listado.",
        "OBLIGATORIO: Sección de características o highlights con 3-4 cards con icono SVG inline, título y descripción breve.",
        "OBLIGATORIO: Sección de featured items mostrando los primeros 6 items en grid (usa la variable 'items').",
        "OBLIGATORIO: Cada featured item en la home debe tener imagen (si existe), título y un badge o etiqueta.",
        "OBLIGATORIO: Los fondos del hero deben usar gradientes CSS (bg-gradient-to-br) no colores planos.",
        "OPCIONAL pero recomendado: una sección de stats con 2-3 números destacados (total items, categorías, etc.).",
    ],
    "list": [
        "OBLIGATORIO: Barra superior con el título de la sección, número de resultados ({{ items|length }} items) y controles visuales.",
        "OBLIGATORIO: Las cards del grid deben tener: imagen con object-cover si existe el campo, título en font-bold, descripción truncada, y un badge de categoría/estado si existe el campo.",
        "OBLIGATORIO: Hover effect en cards: hover:scale-105 hover:shadow-2xl transition-all duration-300.",
        "OBLIGATORIO: Si no hay items, mostrar un empty state visual atractivo con icono SVG y mensaje.",
        "OBLIGATORIO: El grid debe ser responsive: grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4.",
        "RECOMENDADO: Añadir un hero pequeño (py-12) con título y subtítulo antes del grid.",
    ],
    "detail": [
        "OBLIGATORIO: Layout de dos columnas en desktop (lg:grid lg:grid-cols-2 gap-12): imagen a la izquierda, info a la derecha.",
        "OBLIGATORIO: Breadcrumb de navegación arriba: Inicio > Listado > Item actual.",
        "OBLIGATORIO: La imagen debe mostrarse grande (h-96 object-cover rounded-2xl) con un placeholder si no existe.",
        "OBLIGATORIO: Mostrar TODOS los campos del modelo, agrupados por relevancia. Campos secundarios en una sección colapsable o en un grid de metadatos.",
        "OBLIGATORIO: Botón de volver al listado bien visible.",
        "RECOMENDADO: Sección de 'También te puede interesar' al final con 3 items relacionados (usa items[:3] si está disponible en contexto).",
    ],
    "other": [
        "OBLIGATORIO: Diseño limpio con hero section y contenido estructurado.",
        "OBLIGATORIO: Al menos un elemento visual destacado (stat, timeline, o grid de features).",
    ],
}

page_kind = "list" if is_list else ("detail" if is_detail else ("home" if page["name"] == "home" else "other"))
requirements = VISUAL_REQUIREMENTS.get(page_kind, VISUAL_REQUIREMENTS["other"])
requirements_text = "\n".join(f"  {r}" for r in requirements)
```

Y en el `user_text` añadir una sección clara:

```python
user_text = "\n".join([
    ...
    "", "COMPONENTES VISUALES OBLIGATORIOS (implementa TODOS los marcados como OBLIGATORIO):",
    requirements_text,
    ...
])
```

### 1.2 — Mejorar las instrucciones de diseño con directrices de Tailwind específicas

Reemplazar la regla genérica `"Hover en cards: hover:shadow-lg transition-all"` por un bloque más completo:

```python
tailwind_design_rules = [
    "TIPOGRAFÍA: Usa jerarquía clara: títulos principales text-4xl font-black, subtítulos text-xl font-semibold, cuerpo text-base text-gray-300.",
    "ESPACIADO: Secciones separadas con py-16 o py-20. Nunca aglomeres contenido.",
    "CARDS: Siempre border border-gray-800 rounded-2xl overflow-hidden, nunca esquinas cuadradas.",
    "BOTONES primarios: bg-gradient-to-r from-[color1] to-[color2] text-white font-bold px-8 py-3 rounded-xl hover:opacity-90 transition-opacity.",
    "BOTONES secundarios: border border-gray-600 text-gray-300 hover:border-white hover:text-white.",
    "IMÁGENES: Siempre con aspect-ratio fijo usando aspect-video o h-48/h-64, nunca dejar que rompan el layout.",
    "BADGES/ETIQUETAS: Pequeños pills con colores semánticos (verde=activo, amarillo=pendiente, rojo=inactivo).",
    "FONDOS de sección alternados: bg-gray-950 y bg-gray-900/50 para separar visualmente las secciones.",
    "SOMBRAS: Usa shadow-xl o shadow-2xl en elementos destacados, nunca shadow sin modificador.",
    "GRADIENTES: Prefiere gradientes de texto para títulos hero: bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent.",
]
```

### 1.3 — Añadir instrucción de iconos SVG inline

El LLM no usa iconos porque no le decimos que puede. Añadir:

```python
"ICONOS: Para features/stats/empty states, usa iconos SVG inline simples (20x20 o 24x24). "
"No necesitas librerías externas. Dibuja paths SVG básicos: círculos, checks, estrellas, flechas, etc. "
"Ejemplo: <svg class='w-6 h-6 text-green-400' fill='none' stroke='currentColor' viewBox='0 0 24 24'>"
"<path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 13l4 4L19 7'/></svg>",
```

---

## 2. Mejoras en los Ejemplos Few-Shot

**Archivo:** `utils/llm/template_examples.py`

Los ejemplos actuales son grids básicos que el LLM copia literalmente en estilo. Reescribir con diseños más elaborados.

### 2.1 — Nuevo CATALOG_HOME_EXAMPLE

Añadir ejemplo de página home (actualmente no existe ninguno):

```python
CATALOG_HOME_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Hero -->
<section class="py-20 text-center bg-gradient-to-br from-gray-900 via-gray-950 to-black rounded-3xl mb-16 px-8">
  <span class="inline-block bg-green-400/10 text-green-400 text-xs font-semibold px-4 py-1 rounded-full mb-6 uppercase tracking-widest">
    Bienvenido
  </span>
  <h1 class="text-6xl font-black text-white mb-4 leading-tight">
    Descubre nuestro<br>
    <span class="bg-gradient-to-r from-green-400 to-emerald-300 bg-clip-text text-transparent">catálogo completo</span>
  </h1>
  <p class="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
    {{ site_title }} — Explora todos los productos disponibles con información detallada.
  </p>
  <a href="{% url 'catalog' %}" 
     class="inline-block bg-gradient-to-r from-green-500 to-emerald-400 text-black font-bold px-10 py-4 rounded-2xl hover:opacity-90 transition-opacity text-lg">
    Ver catálogo completo →
  </a>
</section>

<!-- Stats -->
<section class="grid grid-cols-3 gap-6 mb-16">
  <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center">
    <div class="text-4xl font-black text-green-400">{{ items|length }}+</div>
    <div class="text-gray-400 mt-1 text-sm">Items disponibles</div>
  </div>
  <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center">
    <div class="text-4xl font-black text-blue-400">100%</div>
    <div class="text-gray-400 mt-1 text-sm">Datos actualizados</div>
  </div>
  <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center">
    <div class="text-4xl font-black text-purple-400">Free</div>
    <div class="text-gray-400 mt-1 text-sm">Acceso libre</div>
  </div>
</section>

<!-- Featured items -->
<section>
  <h2 class="text-2xl font-bold text-white mb-8">Destacados</h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for item in items %}
    <a href="{% url 'detail' item.pk %}"
       class="group block bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-green-400/50 hover:shadow-2xl hover:shadow-green-400/5 transition-all duration-300">
      {% if item.image_url %}
      <div class="aspect-video overflow-hidden">
        <img src="{{ item.image_url }}" alt="{{ item.title }}" 
             class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
      </div>
      {% endif %}
      <div class="p-5">
        <h3 class="text-white font-bold text-lg mb-2 group-hover:text-green-400 transition-colors">{{ item.title }}</h3>
        <p class="text-gray-400 text-sm">{{ item.description|truncatechars:80 }}</p>
        <div class="mt-4 flex items-center justify-between">
          <span class="text-green-400 font-bold">{{ item.price }}</span>
          <span class="text-xs text-gray-600 group-hover:text-gray-400 transition-colors">Ver más →</span>
        </div>
      </div>
    </a>
    {% endfor %}
  </div>
</section>

{% endblock %}
'''
```

### 2.2 — Reescribir CATALOG_LIST_EXAMPLE con más riqueza visual

```python
CATALOG_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Header de sección -->
<div class="flex items-center justify-between mb-10">
  <div>
    <h1 class="text-3xl font-black text-white">Catálogo</h1>
    <p class="text-gray-400 mt-1">{{ items|length }} items encontrados</p>
  </div>
</div>

<!-- Grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {% for item in items %}
  <a href="{% url 'detail' item.pk %}"
     class="group flex flex-col bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden
            hover:border-green-400/50 hover:shadow-2xl hover:shadow-black/50 hover:-translate-y-1
            transition-all duration-300">
    {% if item.image_url %}
    <div class="aspect-video overflow-hidden flex-shrink-0">
      <img src="{{ item.image_url }}" alt="{{ item.title }}"
           class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
    </div>
    {% else %}
    <div class="aspect-video bg-gradient-to-br from-gray-800 to-gray-700 flex items-center justify-center flex-shrink-0">
      <svg class="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"/>
      </svg>
    </div>
    {% endif %}
    <div class="p-5 flex flex-col flex-1">
      {% if item.category %}
      <span class="inline-block text-xs font-semibold text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full mb-2 w-fit">
        {{ item.category }}
      </span>
      {% endif %}
      <h2 class="text-white font-bold text-base leading-snug mb-2 group-hover:text-green-400 transition-colors">
        {{ item.title }}
      </h2>
      {% if item.description %}
      <p class="text-gray-500 text-sm flex-1">{{ item.description|truncatechars:70 }}</p>
      {% endif %}
      {% if item.price %}
      <div class="mt-4 pt-4 border-t border-gray-800 flex items-center justify-between">
        <span class="text-green-400 font-black text-lg">{{ item.price }}</span>
        <span class="text-xs text-gray-600">Ver detalle →</span>
      </div>
      {% endif %}
    </div>
  </a>
  {% empty %}
  <div class="col-span-full py-24 text-center">
    <svg class="w-16 h-16 text-gray-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
    </svg>
    <p class="text-gray-500 text-lg font-medium">No hay items disponibles</p>
    <p class="text-gray-600 text-sm mt-2">Ejecuta el management command load_data para cargar los datos.</p>
  </div>
  {% endfor %}
</div>

{% endblock %}
'''
```

### 2.3 — Reescribir CATALOG_DETAIL_EXAMPLE con layout de dos columnas

```python
CATALOG_DETAIL_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Breadcrumb -->
<nav class="flex items-center gap-2 text-sm text-gray-500 mb-8">
  <a href="{% url 'home' %}" class="hover:text-white transition-colors">Inicio</a>
  <span>›</span>
  <a href="{% url 'catalog' %}" class="hover:text-white transition-colors">Catálogo</a>
  <span>›</span>
  <span class="text-gray-300">{{ item.title|truncatechars:30 }}</span>
</nav>

<!-- Layout principal -->
<div class="lg:grid lg:grid-cols-2 lg:gap-16 items-start">

  <!-- Imagen -->
  <div class="mb-8 lg:mb-0">
    {% if item.image_url %}
    <div class="rounded-2xl overflow-hidden bg-gray-900 border border-gray-800">
      <img src="{{ item.image_url }}" alt="{{ item.title }}" class="w-full aspect-square object-cover">
    </div>
    {% else %}
    <div class="rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-800 aspect-square flex items-center justify-center">
      <svg class="w-24 h-24 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"/>
      </svg>
    </div>
    {% endif %}
  </div>

  <!-- Info -->
  <div>
    {% if item.category %}
    <span class="inline-block text-xs font-semibold text-green-400 bg-green-400/10 px-3 py-1 rounded-full mb-4">
      {{ item.category }}
    </span>
    {% endif %}

    <h1 class="text-4xl font-black text-white leading-tight mb-4">{{ item.title }}</h1>

    {% if item.price %}
    <div class="text-3xl font-black text-green-400 mb-6">{{ item.price }}</div>
    {% endif %}

    {% if item.description %}
    <p class="text-gray-400 leading-relaxed mb-8">{{ item.description }}</p>
    {% endif %}

    <!-- Metadatos -->
    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
      <h3 class="text-white font-semibold text-sm uppercase tracking-widest mb-4">Detalles</h3>
      {% if item.rating %}
      <div class="flex justify-between text-sm">
        <span class="text-gray-500">Valoración</span>
        <span class="text-white font-medium">{{ item.rating }}</span>
      </div>
      {% endif %}
      {% if item.date %}
      <div class="flex justify-between text-sm">
        <span class="text-gray-500">Fecha</span>
        <span class="text-white font-medium">{{ item.date }}</span>
      </div>
      {% endif %}
    </div>

    <!-- Volver -->
    <a href="{% url 'catalog' %}"
       class="mt-8 inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Volver al catálogo
    </a>
  </div>
</div>

{% endblock %}
'''
```

### 2.4 — Añadir ejemplos para los tipos que actualmente no tienen (dashboard, portfolio, other)

Crear ejemplos para `dashboard` con tablas y stat cards, y para `portfolio` con layout de masonry simulado con CSS grid.

---

## 3. Mejoras en el Enriquecimiento del Prompt

**Archivo:** `utils/llm/enrich_prompt.py`

El propio comentario del código dice: *"FALTA MUCHO POR MEJORAR, ES MUY LIMITADO"*. Esto es crítico porque el prompt enriquecido es lo que llega a TODOS los pasos de generación.

### 3.1 — Detección más rica de características del dataset

```python
def enrich_user_prompt(user_prompt, site_type, fields, sample_items):
    base_prompt = (user_prompt or "").strip()
    field_keys = [f["key"].lower() for f in fields]

    # Detección avanzada de características
    has_images    = any(k in ("image", "img", "photo", "thumbnail", "picture", "avatar", "cover", "poster") 
                        or any(img in k for img in ["image", "img", "photo", "thumb", "pic"])
                        for k in field_keys)
    has_price     = any(k in ("price", "cost", "amount", "fee", "rate", "salary", "budget")
                        or "price" in k or "cost" in k
                        for k in field_keys)
    has_date      = any(k in ("date", "created_at", "updated_at", "published", "timestamp", "year", "time")
                        or "date" in k or "time" in k
                        for k in field_keys)
    has_rating    = any(k in ("rating", "score", "stars", "votes", "rank") or "rating" in k for k in field_keys)
    has_category  = any(k in ("category", "type", "genre", "tag", "label", "group", "kind") for k in field_keys)
    has_location  = any(k in ("location", "city", "country", "address", "lat", "lng", "place") for k in field_keys)
    has_url       = any(k in ("url", "link", "website", "href") or k.endswith("_url") for k in field_keys)
    has_long_text = any(k in ("description", "content", "body", "summary", "bio", "about", "text") for k in field_keys)

    # Inferir paleta de color según el tipo de contenido si no hay prompt
    color_suggestions = {
        "catalog":   "colores: fondo oscuro #0f0f0f, acento verde esmeralda #10b981",
        "blog":      "colores: fondo blanco o gris muy claro, texto casi negro, acento azul índigo",
        "portfolio": "colores: fondo negro puro, texto blanco, acento dorado o amber",
        "dashboard": "colores: fondo gris oscuro #111827, acento azul eléctrico #3b82f6",
        "other":     "colores: fondo oscuro, acento púrpura o cian",
    }

    visual_hints = []
    if has_images:   visual_hints.append("el dataset tiene imágenes: úsalas como elemento visual principal con object-cover")
    if has_price:    visual_hints.append("hay precios: destácalos con color de acento y tipografía grande (text-2xl font-black)")
    if has_rating:   visual_hints.append("hay ratings/valoraciones: muéstralos con estrellas SVG o badge numérico")
    if has_category: visual_hints.append("hay categorías: añade filtros o badges de colores por categoría")
    if has_date:     visual_hints.append("hay fechas: muéstralas en formato legible, destacadas en las cards")
    if has_location: visual_hints.append("hay datos de ubicación: considera mostrar ciudad/país en las cards")
    if has_url:      visual_hints.append("hay URLs externas: añade botones 'Ver enlace' o 'Visitar'")
    if has_long_text:visual_hints.append("hay texto largo: usa truncatechars en listados, muestra completo en detalle")

    context_parts = [
        f"Tipo de sitio: {site_type}",
        color_suggestions.get(site_type, ""),
        f"Campos disponibles en orden de importancia: {', '.join(f['key'] for f in fields[:10])}",
    ] + visual_hints

    context = ". ".join(p for p in context_parts if p)

    if base_prompt:
        return f"{base_prompt}\n\nContexto técnico del dataset:\n{context}"
    else:
        defaults = {
            "catalog":   "Catálogo de productos moderno y elegante. Cards con imagen grande, precio destacado, hover effects suaves.",
            "blog":      "Blog limpio y legible. Tipografía cuidada, fechas visibles, categorías con color.",
            "portfolio": "Portfolio minimalista y elegante. Imágenes a pantalla completa, tipografía grande, mucho espacio en blanco.",
            "dashboard": "Dashboard profesional y compacto. Stat cards, tablas limpias, datos legibles de un vistazo.",
            "other":     "Sitio web moderno y bien estructurado. Diseño oscuro con acentos de color.",
        }
        base = defaults.get(site_type, defaults["other"])
        return f"{base}\n\nContexto técnico del dataset:\n{context}"
```

---

## 4. Nuevos Tipos de Sitio

**Archivos:** `utils/llm/planner.py`, `utils/llm/template_examples.py`, `utils/llm/generator_prompts.py`

Actualmente solo hay 5 tipos: `blog`, `portfolio`, `catalog`, `dashboard`, `other`. Añadir tipos más específicos mejoraría el resultado porque el LLM recibiría instrucciones más afinadas.

### 4.1 — Nuevos tipos propuestos

| Tipo nuevo | Cuándo usarlo | Diferencia de diseño |
|---|---|---|
| `directory` | APIs de personas, empresas, restaurantes | Cards compactas con avatar, contacto, mapa |
| `events` | APIs de eventos, conciertos, conferencias | Calendario visual, countdown, tickets |
| `news` | APIs de noticias, artículos de prensa | Hero article destacado, lista de recientes |
| `recipes` | APIs de recetas, menús | Ingredientes en chips, tiempo de preparación, ratings |
| `jobs` | APIs de ofertas de trabajo | Filtros por tipo/salario, badges de urgencia |

### 4.2 — Cómo añadirlos

En `planner.py`, ampliar `ALLOWED_SITE_TYPES`:
```python
ALLOWED_SITE_TYPES = ("blog", "portfolio", "catalog", "dashboard", "directory", "events", "news", "recipes", "jobs", "other")
```

Y la función `_normalize_site_type`:
```python
if "event" in s or "concert" in s or "show" in s: return "events"
if "news" in s or "article" in s or "press" in s: return "news"
if "recipe" in s or "food" in s or "cook" in s:   return "recipes"
if "job" in s or "career" in s or "work" in s:    return "jobs"
if "direct" in s or "person" in s or "people" in s: return "directory"
```

---

## 5. Mejoras en la Estructura de Páginas

**Archivo:** `utils/llm/generator_prompts.py` → función `prompt_pages_structure`

### 5.1 — Páginas adicionales por tipo de sitio

Actualmente el sistema genera home + listado + detalle siempre igual. Añadir páginas específicas según el tipo:

```python
SUGGESTED_EXTRA_PAGES = {
    "catalog": [
        {"name": "about", "description": "Página sobre el catálogo/marca", "is_list": False, "is_detail": False},
    ],
    "blog": [
        {"name": "categories", "description": "Listado de categorías del blog", "is_list": False, "is_detail": False},
    ],
    "dashboard": [
        {"name": "stats", "description": "Vista de estadísticas y métricas globales", "is_list": False, "is_detail": False},
    ],
    "directory": [
        {"name": "map", "description": "Vista alternativa en modo mapa/grid compacto", "is_list": True, "is_detail": False},
    ],
}
```

Añadirlos como sugerencia al final del prompt de estructura.

### 5.2 — Forzar una página 404 personalizada

Siempre incluir `404.html` en los archivos generados. No necesita LLM, puede ser un fallback estático pero bonito:

```python
# En project_generator.py, después del paso 5:
files[f"{project}/{app}/templates/404.html"] = generate_404_template(site_title, pages)
```

---

## 6. Sistema de Temas y Paletas de Color

**Archivo nuevo:** `utils/llm/theme_extractor.py`

Actualmente los colores dependen totalmente del LLM con instrucciones vagas. Crear un módulo que extraiga la paleta del prompt del usuario y la inyecte de forma consistente en TODOS los templates.

### 6.1 — Extractor de paleta desde el prompt

```python
# theme_extractor.py

PALETTE_KEYWORDS = {
    "verde":    {"primary": "#10b981", "primary_dark": "#059669", "accent": "#34d399"},
    "azul":     {"primary": "#3b82f6", "primary_dark": "#2563eb", "accent": "#60a5fa"},
    "rojo":     {"primary": "#ef4444", "primary_dark": "#dc2626", "accent": "#f87171"},
    "morado":   {"primary": "#8b5cf6", "primary_dark": "#7c3aed", "accent": "#a78bfa"},
    "naranja":  {"primary": "#f97316", "primary_dark": "#ea580c", "accent": "#fb923c"},
    "rosa":     {"primary": "#ec4899", "primary_dark": "#db2777", "accent": "#f472b6"},
    "amarillo": {"primary": "#eab308", "primary_dark": "#ca8a04", "accent": "#fde047"},
    "cian":     {"primary": "#06b6d4", "primary_dark": "#0891b2", "accent": "#22d3ee"},
    "dorado":   {"primary": "#d97706", "primary_dark": "#b45309", "accent": "#fbbf24"},
}

BACKGROUND_KEYWORDS = {
    "claro": {"bg": "#ffffff", "bg_secondary": "#f9fafb", "text": "#111827", "text_secondary": "#6b7280"},
    "light": {"bg": "#ffffff", "bg_secondary": "#f9fafb", "text": "#111827", "text_secondary": "#6b7280"},
    "oscuro": {"bg": "#030712", "bg_secondary": "#111827", "text": "#f9fafb", "text_secondary": "#9ca3af"},
    "dark": {"bg": "#030712", "bg_secondary": "#111827", "text": "#f9fafb", "text_secondary": "#9ca3af"},
    "gris": {"bg": "#111827", "bg_secondary": "#1f2937", "text": "#f9fafb", "text_secondary": "#9ca3af"},
}

def extract_theme(user_prompt: str, site_type: str) -> dict:
    prompt_lower = user_prompt.lower()
    
    # Detectar color primario
    palette = None
    for keyword, colors in PALETTE_KEYWORDS.items():
        if keyword in prompt_lower:
            palette = colors
            break
    
    # Default por site_type si no se especifica
    if not palette:
        defaults = {
            "catalog": PALETTE_KEYWORDS["verde"],
            "blog": PALETTE_KEYWORDS["azul"],
            "portfolio": PALETTE_KEYWORDS["dorado"],
            "dashboard": PALETTE_KEYWORDS["azul"],
            "other": PALETTE_KEYWORDS["morado"],
        }
        palette = defaults.get(site_type, PALETTE_KEYWORDS["verde"])
    
    # Detectar fondo
    bg = None
    for keyword, colors in BACKGROUND_KEYWORDS.items():
        if keyword in prompt_lower:
            bg = colors
            break
    if not bg:
        bg = BACKGROUND_KEYWORDS["oscuro"]  # default dark
    
    return {**palette, **bg}
```

### 6.2 — Inyectar el tema en los prompts de templates

En `prompt_base_template` y `prompt_template`, añadir al `user_text`:

```python
from ..llm.theme_extractor import extract_theme

theme = extract_theme(user_prompt, site_type)
theme_instruction = (
    f"PALETA DE COLORES EXACTA A USAR:\n"
    f"  - Color primario (botones, acentos, links hover): {theme['primary']}\n"
    f"  - Color primario oscuro (hover de botones): {theme['primary_dark']}\n"
    f"  - Color de acento suave (badges, highlights): {theme['accent']}\n"
    f"  - Fondo principal: {theme['bg']}\n"
    f"  - Fondo secundario (cards, nav): {theme['bg_secondary']}\n"
    f"  - Texto principal: {theme['text']}\n"
    f"  - Texto secundario: {theme['text_secondary']}\n"
    f"USA estos colores exactos con la sintaxis style='color: ...' o clases Tailwind equivalentes.\n"
    f"Convierte los hex a clases Tailwind cuando sea posible, o usa style='background-color: {theme['primary']}'."
)
```

---

## 7. Componentes Visuales Avanzados

### 7.1 — Sistema de búsqueda frontend en el listado

En el prompt del template de listado, añadir instrucción obligatoria:

```python
"OBLIGATORIO en página de listado: Añade un input de búsqueda simple con JavaScript vanilla que filtre "
"las cards en tiempo real por texto. Input con id='search-input' y cada card con class='search-item' "
"y un atributo data-search con los campos relevantes del item concatenados. "
"El JS debe escuchar el evento 'input' y mostrar/ocultar las cards según el texto. "
"Esto es JavaScript inline al final del {% block content %}, no en un archivo externo.",
```

Ejemplo del JS a generar (meterlo en el prompt como referencia):
```html
<script>
const inp = document.getElementById('search-input');
inp.addEventListener('input', () => {
  const q = inp.value.toLowerCase();
  document.querySelectorAll('.search-item').forEach(el => {
    el.style.display = el.dataset.search.toLowerCase().includes(q) ? '' : 'none';
  });
});
</script>
```

### 7.2 — Animaciones de entrada con CSS puro

Añadir a `prompt_base_template` la instrucción de incluir una `<style>` con animaciones CSS básicas:

```python
"Añade en el <head> un bloque <style> con estas animaciones CSS:"
"  @keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }"
"  .animate-in { animation: fadeInUp 0.5s ease-out forwards; }"
"  .animate-in-delay-1 { animation-delay: 0.1s; opacity: 0; animation: fadeInUp 0.5s 0.1s ease-out forwards; }"
"  .animate-in-delay-2 { animation-delay: 0.2s; opacity: 0; animation: fadeInUp 0.5s 0.2s ease-out forwards; }"
"Aplica animate-in a los elementos principales del hero y animate-in-delay-N a los siguientes.",
```

### 7.3 — Modo oscuro/claro con toggle

Añadir a `prompt_base_template`:

```python
"OPCIONAL pero muy recomendado: Añade un botón toggle de modo oscuro/claro en la navbar. "
"Implementa con JavaScript vanilla: al hacer click, añade/quita la clase 'dark' en <html>. "
"Guarda la preferencia en localStorage. El icono debe cambiar entre sol y luna usando SVG inline.",
```

### 7.4 — Indicador de scroll progress en páginas de detalle

Para páginas de detalle con contenido largo:

```python
"En la página de detalle, añade una barra de progreso de scroll fina (4px) en la parte superior "
"de color primario que se llena conforme el usuario hace scroll. "
"Implementar con JS: window.addEventListener('scroll', () => { barra.style.width = (scrollY / (document.body.scrollHeight - innerHeight) * 100) + '%' })",
```

---

## 8. Mejoras en el base.html

**Archivo:** `utils/llm/generator_prompts.py` → función `prompt_base_template`

### 8.1 — Meta tags y SEO básico

Añadir como regla obligatoria:

```python
"OBLIGATORIO: Incluir meta tags básicos en <head>:",
"  <meta name='description' content='{{ site_title }} — Explora nuestro sitio'>",
"  <meta property='og:title' content='{{ site_title }}'>",
"  <meta name='theme-color' content='#COLOR_PRIMARIO'>",
"  <link rel='icon' href='data:image/svg+xml,...'> (usa un emoji SVG como favicon)",
```

### 8.2 — Navbar con indicador de página activa

```python
"OBLIGATORIO: El navbar debe marcar la página actual como activa. "
"Usa {% url 'nombre' as url_name %} y compara con request.path para añadir "
"clases adicionales al link activo (text-white font-bold border-b-2 border-primary).",
```

### 8.3 — Footer más completo

```python
"OBLIGATORIO: El footer debe tener al menos dos columnas: "
"(1) Nombre del sitio + descripción breve, "
"(2) Links de navegación secundarios. "
"Separar del contenido con border-t border-gray-800. "
"Incluir copyright: © {{ 'now'|date:'Y' }} {{ site_title }}.",
```

### 8.4 — Loading state visual

```python
"RECOMENDADO: Añadir un indicador de carga global con CSS puro: "
"barra fina en el top del viewport con color de acento que aparece "
"en el evento beforeunload del window y desaparece al cargar.",
```

---

## 9. Mejoras Funcionales en las Views

**Archivo:** `utils/llm/generator_prompts.py` → función `prompt_views`

### 9.1 — Paginación en el listado

Añadir como regla explícita:

```python
"OBLIGATORIO: La view de listado debe usar paginación de Django:"
"  from django.core.paginator import Paginator"
"  paginator = Paginator(Item.objects.all().order_by('-id'), 12)"
"  page = request.GET.get('page', 1)"
"  items = paginator.get_page(page)"
"  Pasar también 'page_obj' al contexto para que el template pueda mostrar los controles de paginación.",
```

Y en el prompt del template de listado, instrucción de renderizar los controles:

```python
"Si hay paginación (page_obj disponible en contexto), añade controles de navegación: "
"botones Anterior/Siguiente con el número de página actual visible. "
"Centra los controles y usa estilos consistentes con el resto del sitio.",
```

### 9.2 — Búsqueda server-side (además de la client-side)

```python
"OPCIONAL: La view de listado puede aceptar ?q=texto en GET y filtrar con:"
"  q = request.GET.get('q', '')"
"  if q: items = items.filter(title__icontains=q) | items.filter(description__icontains=q)",
```

### 9.3 — Items relacionados en el detalle

```python
"RECOMENDADO: La view de detalle puede pasar items relacionados al contexto:"
"  related = Item.objects.exclude(pk=item.pk).order_by('?')[:3]"
"  Pasar 'related' al template para la sección 'También te puede interesar'.",
```

---

## 10. Mejoras en los Fallbacks

**Archivo:** `utils/generator/fallbacks.py`

Los fallbacks son el contenido de emergencia cuando el LLM falla. Actualmente son muy básicos y sin estilo. Si el LLM falla, el usuario ve algo horrible.

### 10.1 — Fallback de home con algo de estilo

El `fallback_base_html` actual devuelve un HTML muy desnudo. Aunque sea fallback, debe verse decente:

```python
def fallback_base_html(site_title: str, pages: list[dict]) -> str:
    # Añadir gradiente en el body, fuente Inter via Google Fonts,
    # navbar con backdrop-blur, y footer con copyright.
    # Ver el código completo en la sección de implementación.
    ...
```

### 10.2 — Fallback de template de listado con empty state visual

El fallback actual muestra `{{ item }}` (el `__str__` del modelo). Aunque es funcional, queda fatal. Mejorar para que al menos las cards tengan algo de estructura.

---

## 11. Postprocesado del HTML Generado

**Archivo nuevo:** `utils/generator/html_postprocessor.py`

Después de que el LLM genera los templates, aplicar un postprocesado automático que corrija problemas comunes sin necesidad de regenerar.

### 11.1 — Correcciones automáticas detectables con regex/string

```python
def postprocess_html(html: str, real_fields: list[str], real_url_names: dict) -> str:
    """
    Postprocesado del HTML generado por el LLM.
    Corrige errores comunes sin necesidad de llamar al LLM de nuevo.
    """
    
    # 1. Asegurar que no hay bloques de markdown que se colaron
    html = strip_markdown_fences(html)
    
    # 2. Reemplazar URLs hardcodeadas por template tags
    # El LLM a veces escribe href="/catalog/" en vez de {% url 'catalog' %}
    for name, view_name in real_url_names.items():
        html = re.sub(
            rf'href="/{name}/"',
            f'{{% url \'{view_name}\' %}}',
            html
        )
    
    # 3. Truncar descripciones que el LLM olvidó truncar en listados
    # Si hay {{ item.description }} sin truncatechars en una card (contexto de listado)
    # convertir a {{ item.description|truncatechars:100 }}
    
    # 4. Verificar que extends está al principio
    if "{% extends" in html and not html.strip().startswith("{% extends"):
        idx = html.find("{% extends")
        extends_line = html[idx:html.index("%}", idx) + 2]
        html = extends_line + "\n" + html[:idx] + html[idx + len(extends_line):]
    
    return html
```

Integrar en `project_generator.py`:

```python
# En el paso 5, después de cada template generado:
from ..generator.html_postprocessor import postprocess_html
html = postprocess_html(html, real_fields=real_fields, real_url_names=real_url_names)
files[f"{project}/{app}/templates/{page['template']}"] = html
```

### 11.2 — Validación de campos usados en templates

Antes de guardar, verificar que el template no usa `item.campo_inexistente`:

```python
def validate_template_fields(html: str, real_fields: list[str]) -> list[str]:
    """Detecta usos de item.campo que no existen en el modelo."""
    pattern = re.compile(r'\{\{\s*item\.(\w+)')
    used = set(pattern.findall(html))
    invalid = [f for f in used if f not in real_fields and f not in ("pk", "id")]
    return invalid
```

Si hay campos inválidos, loggear una advertencia y opcionalmente intentar autocorrección.

---

## 12. Resumen de Impacto por Archivo

| Archivo | Tipo de cambio | Impacto visual estimado | Dificultad |
|---|---|---|---|
| `generator_prompts.py` → `prompt_template` | Componentes visuales obligatorios por tipo | ⭐⭐⭐⭐⭐ | Media |
| `template_examples.py` | Reescribir ejemplos few-shot con diseño rico | ⭐⭐⭐⭐⭐ | Baja |
| `enrich_prompt.py` | Detección avanzada de características | ⭐⭐⭐⭐ | Baja |
| `theme_extractor.py` (nuevo) | Sistema de paletas de color consistente | ⭐⭐⭐⭐ | Media |
| `generator_prompts.py` → `prompt_base_template` | Meta SEO, navbar activo, footer completo | ⭐⭐⭐ | Baja |
| `generator_prompts.py` → `prompt_template` | Búsqueda client-side, animaciones CSS | ⭐⭐⭐ | Baja |
| `generator_prompts.py` → `prompt_views` | Paginación, búsqueda, relacionados | ⭐⭐⭐ | Media |
| `html_postprocessor.py` (nuevo) | Corrección automática de errores LLM | ⭐⭐ | Media |
| `planner.py` | Nuevos tipos de sitio | ⭐⭐ | Baja |
| `fallbacks.py` | Fallbacks con más estilo | ⭐ | Baja |

---

## Orden de implementación recomendado

**Fase 1 — Máximo impacto, mínimo esfuerzo** *(1-2 días)*
1. Reescribir `template_examples.py` con los nuevos ejemplos few-shot
2. Añadir `VISUAL_REQUIREMENTS` en `prompt_template`
3. Mejorar `enrich_prompt.py` con detección avanzada

**Fase 2 — Consistencia visual** *(2-3 días)*
4. Crear `theme_extractor.py` y conectarlo a los prompts
5. Mejorar `prompt_base_template` (meta tags, navbar activo, footer)
6. Añadir instrucciones de búsqueda client-side y animaciones en `prompt_template`

**Fase 3 — Funcionalidad añadida** *(3-5 días)*
7. Añadir paginación y búsqueda en `prompt_views`
8. Crear `html_postprocessor.py`
9. Ampliar tipos de sitio en `planner.py`
10. Añadir nuevos ejemplos para tipos nuevos en `template_examples.py`

---

*Documento generado a partir del análisis completo del código fuente de WebBuilder — abril 2026*
