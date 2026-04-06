"""
template_examples.py — Ejemplos HTML de referencia por tipo de sitio.
Se inyectan en el prompt de generación de templates como inspiración estructural.
El LLM debe adaptar el diseño a los campos reales del dataset, no copiar este ejemplo.

IMPORTANTE PARA EL LLM:
- Los campos usados aquí (item.title, item.price...) son GENÉRICOS.
  Sustitúyelos por los campos reales del modelo que se te han indicado.
- El estilo visual sí debe inspirarte: estructura, espaciado, jerarquía, componentes.
- Adapta los colores al prompt del usuario y al site_type.
"""


# ── CATALOG ───────────────────────────────────────────────────────────────────

CATALOG_HOME_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Hero con gradiente -->
<section class="relative py-24 px-8 rounded-3xl mb-16 overflow-hidden bg-gradient-to-br from-gray-900 via-gray-950 to-black text-center">
  <div class="relative z-10">
    <span class="inline-block text-xs font-semibold tracking-widest uppercase px-4 py-1.5 rounded-full mb-6 bg-green-400/10 text-green-400">
      Bienvenido
    </span>
    <h1 class="text-6xl font-black text-white mb-4 leading-tight">
      Descubre nuestro<br>
      <span class="bg-gradient-to-r from-green-400 to-emerald-300 bg-clip-text text-transparent">catálogo completo</span>
    </h1>
    <p class="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
      {{ site_title }} — Explora todos los productos con información detallada.
    </p>
    <a href="{% url 'catalog' %}"
       class="inline-block bg-gradient-to-r from-green-500 to-emerald-400 text-black font-bold px-10 py-4 rounded-2xl hover:opacity-90 transition-opacity text-lg">
      Ver catálogo completo →
    </a>
  </div>
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

<!-- Destacados -->
<section>
  <div class="flex items-center justify-between mb-8">
    <h2 class="text-2xl font-bold text-white">Destacados</h2>
    <a href="{% url 'catalog' %}" class="text-sm text-gray-400 hover:text-white transition-colors">Ver todos →</a>
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for item in items %}
    <a href="{% url 'detail' item.pk %}"
       class="group block bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-green-400/50 hover:shadow-2xl hover:shadow-green-400/5 hover:-translate-y-1 transition-all duration-300">
      {% if item.image_url %}
      <div class="aspect-video overflow-hidden">
        <img src="{{ item.image_url }}" alt="{{ item.title }}"
             class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
      </div>
      {% else %}
      <div class="aspect-video bg-gradient-to-br from-gray-800 to-gray-700 flex items-center justify-center">
        <svg class="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"/>
        </svg>
      </div>
      {% endif %}
      <div class="p-5">
        <h3 class="text-white font-bold text-lg mb-1 group-hover:text-green-400 transition-colors">{{ item.title }}</h3>
        <p class="text-gray-400 text-sm">{{ item.description|truncatechars:70 }}</p>
        <div class="mt-4 flex items-center justify-between">
          <span class="text-green-400 font-black">{{ item.price }}</span>
          <span class="text-xs text-gray-600 group-hover:text-gray-400 transition-colors">Ver más →</span>
        </div>
      </div>
    </a>
    {% endfor %}
  </div>
</section>

{% endblock %}
'''

CATALOG_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Cabecera -->
<div class="flex items-center justify-between mb-10">
  <div>
    <h1 class="text-3xl font-black text-white">Catálogo</h1>
    <p class="text-gray-400 mt-1 text-sm">{{ items|length }} items encontrados</p>
  </div>
</div>

<!-- Grid de cards -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {% for item in items %}
  <a href="{% url 'detail' item.pk %}"
     class="group flex flex-col bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-green-400/50 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
    {% if item.image_url %}
    <div class="aspect-video overflow-hidden flex-shrink-0">
      <img src="{{ item.image_url }}" alt="{{ item.title }}"
           class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
    </div>
    {% else %}
    <div class="aspect-video bg-gradient-to-br from-gray-800 to-gray-700 flex items-center justify-center flex-shrink-0">
      <svg class="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"/>
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
        <span class="text-xs text-gray-600">Ver →</span>
      </div>
      {% endif %}
    </div>
  </a>
  {% empty %}
  <div class="col-span-full py-24 text-center">
    <svg class="w-16 h-16 text-gray-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
    </svg>
    <p class="text-gray-500 text-lg font-medium">No hay items disponibles</p>
    <p class="text-gray-600 text-sm mt-1">Ejecuta el comando load_data para cargar los datos.</p>
  </div>
  {% endfor %}
</div>

{% endblock %}
'''

CATALOG_DETAIL_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Breadcrumb -->
<nav class="flex items-center gap-2 text-sm text-gray-500 mb-10">
  <a href="{% url 'home' %}" class="hover:text-white transition-colors">Inicio</a>
  <span>›</span>
  <a href="{% url 'catalog' %}" class="hover:text-white transition-colors">Catálogo</a>
  <span>›</span>
  <span class="text-gray-300">{{ item.title|truncatechars:30 }}</span>
</nav>

<!-- Layout 2 columnas -->
<div class="lg:grid lg:grid-cols-2 lg:gap-16 items-start">

  <!-- Imagen -->
  <div class="mb-8 lg:mb-0">
    {% if item.image_url %}
    <div class="rounded-2xl overflow-hidden border border-gray-800 bg-gray-900">
      <img src="{{ item.image_url }}" alt="{{ item.title }}" class="w-full aspect-square object-cover">
    </div>
    {% else %}
    <div class="rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-800 aspect-square flex items-center justify-center">
      <svg class="w-24 h-24 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"/>
      </svg>
    </div>
    {% endif %}
  </div>

  <!-- Información -->
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

    <!-- Metadatos en tabla -->
    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-3 mb-8">
      <h3 class="text-white font-semibold text-xs uppercase tracking-widest mb-4 text-gray-500">Detalles</h3>
      {% if item.rating %}
      <div class="flex justify-between text-sm py-2 border-b border-gray-800">
        <span class="text-gray-500">Valoración</span>
        <span class="text-white font-medium">{{ item.rating }}</span>
      </div>
      {% endif %}
      {% if item.date %}
      <div class="flex justify-between text-sm py-2">
        <span class="text-gray-500">Fecha</span>
        <span class="text-white font-medium">{{ item.date }}</span>
      </div>
      {% endif %}
    </div>

    <a href="{% url 'catalog' %}"
       class="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Volver al catálogo
    </a>
  </div>
</div>

{% endblock %}
'''


# ── BLOG ──────────────────────────────────────────────────────────────────────

BLOG_HOME_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Hero editorial -->
<section class="py-20 mb-16 border-b border-gray-800">
  <span class="text-xs font-semibold tracking-widest uppercase text-blue-400 mb-4 block">Blog</span>
  <h1 class="text-6xl font-black text-white leading-tight mb-6 max-w-3xl">
    {{ site_title }}
  </h1>
  <p class="text-xl text-gray-400 max-w-2xl mb-8">
    Artículos, análisis y reflexiones sobre los temas que importan.
  </p>
  <a href="{% url 'catalog' %}"
     class="inline-block border border-gray-600 text-gray-300 hover:border-white hover:text-white px-8 py-3 rounded-xl transition-all font-medium">
    Ver todos los artículos
  </a>
</section>

<!-- Artículo destacado -->
{% if items %}
{% with items.0 as featured %}
<section class="mb-16">
  <div class="group grid lg:grid-cols-2 gap-10 bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-700 transition-all">
    {% if featured.image_url %}
    <div class="overflow-hidden">
      <img src="{{ featured.image_url }}" alt="{{ featured.title }}"
           class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 min-h-64">
    </div>
    {% endif %}
    <div class="p-10 flex flex-col justify-center">
      {% if featured.category %}
      <span class="text-xs font-semibold text-blue-400 uppercase tracking-widest mb-4">{{ featured.category }}</span>
      {% endif %}
      <h2 class="text-3xl font-black text-white mb-4 leading-tight">{{ featured.title }}</h2>
      <p class="text-gray-400 leading-relaxed mb-6">{{ featured.summary|truncatechars:150 }}</p>
      <a href="{% url 'detail' featured.pk %}"
         class="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium transition-colors">
        Leer artículo
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </a>
    </div>
  </div>
</section>
{% endwith %}
{% endif %}

<!-- Recientes -->
<section>
  <h2 class="text-xl font-bold text-white mb-8">Más recientes</h2>
  <div class="space-y-6">
    {% for item in items|slice:"1:5" %}
    <a href="{% url 'detail' item.pk %}"
       class="group flex gap-6 p-5 bg-gray-900 border border-gray-800 rounded-xl hover:border-gray-700 transition-all">
      {% if item.image_url %}
      <img src="{{ item.image_url }}" alt="{{ item.title }}" class="w-24 h-24 object-cover rounded-lg flex-shrink-0">
      {% endif %}
      <div>
        {% if item.category %}
        <span class="text-xs text-blue-400 font-semibold uppercase tracking-wide">{{ item.category }}</span>
        {% endif %}
        <h3 class="text-white font-bold mt-1 group-hover:text-blue-400 transition-colors">{{ item.title }}</h3>
        <p class="text-gray-500 text-sm mt-1">{{ item.summary|truncatechars:80 }}</p>
      </div>
    </a>
    {% endfor %}
  </div>
</section>

{% endblock %}
'''

BLOG_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<div class="max-w-3xl mx-auto">
  <div class="mb-12">
    <h1 class="text-4xl font-black text-white">Todos los artículos</h1>
    <p class="text-gray-400 mt-2">{{ items|length }} artículos publicados</p>
  </div>

  <div class="space-y-10">
    {% for item in items %}
    <article class="group border-b border-gray-800 pb-10">
      {% if item.image_url %}
      <a href="{% url 'detail' item.pk %}" class="block mb-5 rounded-xl overflow-hidden aspect-video">
        <img src="{{ item.image_url }}" alt="{{ item.title }}"
             class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
      </a>
      {% endif %}
      <div class="flex items-center gap-3 mb-3">
        {% if item.category %}
        <span class="text-xs font-semibold text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded-full">{{ item.category }}</span>
        {% endif %}
        {% if item.pub_date %}
        <span class="text-xs text-gray-600">{{ item.pub_date }}</span>
        {% endif %}
      </div>
      <h2 class="text-2xl font-black text-white leading-snug mb-3">
        <a href="{% url 'detail' item.pk %}" class="hover:text-blue-400 transition-colors">{{ item.title }}</a>
      </h2>
      <p class="text-gray-400 leading-relaxed">{{ item.summary|truncatechars:140 }}</p>
      <a href="{% url 'detail' item.pk %}"
         class="inline-flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300 mt-4 transition-colors">
        Leer más <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      </a>
    </article>
    {% empty %}
    <p class="text-gray-500 py-16 text-center">No hay artículos disponibles.</p>
    {% endfor %}
  </div>
</div>

{% endblock %}
'''

BLOG_DETAIL_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<div class="max-w-3xl mx-auto">

  <!-- Breadcrumb -->
  <nav class="flex items-center gap-2 text-sm text-gray-500 mb-10">
    <a href="{% url 'home' %}" class="hover:text-white transition-colors">Inicio</a>
    <span>›</span>
    <a href="{% url 'catalog' %}" class="hover:text-white transition-colors">Artículos</a>
    <span>›</span>
    <span class="text-gray-300">{{ item.title|truncatechars:30 }}</span>
  </nav>

  <article>
    <!-- Meta -->
    <div class="flex items-center gap-3 mb-5">
      {% if item.category %}
      <span class="text-xs font-semibold text-blue-400 bg-blue-400/10 px-3 py-1 rounded-full">{{ item.category }}</span>
      {% endif %}
      {% if item.pub_date %}
      <span class="text-sm text-gray-500">{{ item.pub_date }}</span>
      {% endif %}
    </div>

    <h1 class="text-5xl font-black text-white leading-tight mb-6">{{ item.title }}</h1>

    {% if item.summary %}
    <p class="text-xl text-gray-400 leading-relaxed mb-10 border-l-4 border-blue-400 pl-6">{{ item.summary }}</p>
    {% endif %}

    {% if item.image_url %}
    <div class="rounded-2xl overflow-hidden mb-10 aspect-video">
      <img src="{{ item.image_url }}" alt="{{ item.title }}" class="w-full h-full object-cover">
    </div>
    {% endif %}

    <div class="text-gray-300 leading-relaxed text-lg space-y-4">
      {{ item.content }}
    </div>
  </article>

  <div class="mt-12 pt-8 border-t border-gray-800">
    <a href="{% url 'catalog' %}"
       class="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Volver a artículos
    </a>
  </div>
</div>

{% endblock %}
'''


# ── PORTFOLIO ─────────────────────────────────────────────────────────────────

PORTFOLIO_HOME_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Hero minimalista -->
<section class="py-32 mb-20">
  <h1 class="text-8xl font-black text-white leading-none mb-6 tracking-tight">
    {{ site_title }}
  </h1>
  <p class="text-2xl text-gray-500 max-w-xl mb-12">
    Selección de proyectos y trabajos recientes.
  </p>
  <a href="{% url 'catalog' %}"
     class="inline-flex items-center gap-3 text-white border-b border-white pb-1 hover:text-gray-400 hover:border-gray-400 transition-all text-lg font-medium">
    Ver todos los proyectos
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7"/>
    </svg>
  </a>
</section>

<!-- Grid de proyectos -->
<section class="grid grid-cols-1 md:grid-cols-2 gap-8">
  {% for item in items %}
  <a href="{% url 'detail' item.pk %}"
     class="group block relative overflow-hidden rounded-2xl bg-gray-900 aspect-video border border-gray-800 hover:border-gray-600 transition-all duration-500">
    {% if item.image_url %}
    <img src="{{ item.image_url }}" alt="{{ item.title }}"
         class="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 opacity-80 group-hover:opacity-100">
    {% else %}
    <div class="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-700"></div>
    {% endif %}
    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
    <div class="absolute bottom-0 left-0 p-8">
      {% if item.category %}
      <span class="text-xs text-gray-400 uppercase tracking-widest mb-2 block">{{ item.category }}</span>
      {% endif %}
      <h2 class="text-white font-black text-2xl leading-tight group-hover:text-gray-200 transition-colors">{{ item.title }}</h2>
    </div>
  </a>
  {% endfor %}
</section>

{% endblock %}
'''

PORTFOLIO_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<div class="mb-12">
  <h1 class="text-5xl font-black text-white">Proyectos</h1>
  <p class="text-gray-500 mt-3">{{ items|length }} trabajos</p>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
  {% for item in items %}
  <a href="{% url 'detail' item.pk %}"
     class="group relative block overflow-hidden rounded-2xl aspect-video border border-gray-800 hover:border-gray-600 transition-all duration-500">
    {% if item.image_url %}
    <img src="{{ item.image_url }}" alt="{{ item.title }}"
         class="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 opacity-70 group-hover:opacity-100">
    {% else %}
    <div class="absolute inset-0 bg-gradient-to-br from-gray-800 via-gray-700 to-gray-900"></div>
    {% endif %}
    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
    <div class="absolute bottom-0 left-0 right-0 p-7 translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
      {% if item.category %}
      <span class="text-xs text-gray-400 uppercase tracking-widest mb-2 block">{{ item.category }}</span>
      {% endif %}
      <h2 class="text-white font-black text-xl leading-snug">{{ item.title }}</h2>
      {% if item.description %}
      <p class="text-gray-400 text-sm mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        {{ item.description|truncatechars:70 }}
      </p>
      {% endif %}
    </div>
  </a>
  {% empty %}
  <div class="col-span-full py-24 text-center text-gray-600">No hay proyectos disponibles.</div>
  {% endfor %}
</div>

{% endblock %}
'''

PORTFOLIO_DETAIL_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Volver -->
<a href="{% url 'catalog' %}"
   class="inline-flex items-center gap-2 text-gray-500 hover:text-white transition-colors text-sm mb-12">
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
  </svg>
  Proyectos
</a>

<!-- Imagen grande -->
{% if item.image_url %}
<div class="rounded-3xl overflow-hidden mb-16 aspect-video w-full">
  <img src="{{ item.image_url }}" alt="{{ item.title }}" class="w-full h-full object-cover">
</div>
{% endif %}

<!-- Info -->
<div class="max-w-3xl">
  {% if item.category %}
  <span class="text-xs text-gray-500 uppercase tracking-widest mb-4 block">{{ item.category }}</span>
  {% endif %}
  <h1 class="text-6xl font-black text-white leading-none mb-8">{{ item.title }}</h1>
  {% if item.description %}
  <p class="text-xl text-gray-400 leading-relaxed mb-12">{{ item.description }}</p>
  {% endif %}

  <!-- Detalles del proyecto -->
  <div class="grid grid-cols-2 gap-6 border-t border-gray-800 pt-10">
    {% if item.date %}
    <div>
      <span class="text-xs text-gray-600 uppercase tracking-widest block mb-1">Año</span>
      <span class="text-white font-medium">{{ item.date }}</span>
    </div>
    {% endif %}
    {% if item.client %}
    <div>
      <span class="text-xs text-gray-600 uppercase tracking-widest block mb-1">Cliente</span>
      <span class="text-white font-medium">{{ item.client }}</span>
    </div>
    {% endif %}
    {% if item.url %}
    <div>
      <span class="text-xs text-gray-600 uppercase tracking-widest block mb-1">Enlace</span>
      <a href="{{ item.url }}" target="_blank" class="text-blue-400 hover:underline font-medium">Ver proyecto →</a>
    </div>
    {% endif %}
  </div>
</div>

{% endblock %}
'''


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

DASHBOARD_HOME_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<!-- Header -->
<div class="flex items-center justify-between mb-10">
  <div>
    <h1 class="text-3xl font-black text-white">{{ site_title }}</h1>
    <p class="text-gray-500 mt-1 text-sm">Resumen general de datos</p>
  </div>
  <a href="{% url 'catalog' %}"
     class="text-sm bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl font-medium transition-colors">
    Ver todos los datos →
  </a>
</div>

<!-- Stat cards -->
<div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
  <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
    <div class="flex items-center gap-3 mb-3">
      <div class="w-9 h-9 bg-blue-500/10 rounded-xl flex items-center justify-center">
        <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
        </svg>
      </div>
      <span class="text-gray-400 text-sm">Total registros</span>
    </div>
    <div class="text-4xl font-black text-white">{{ items|length }}</div>
  </div>
  <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
    <div class="flex items-center gap-3 mb-3">
      <div class="w-9 h-9 bg-green-500/10 rounded-xl flex items-center justify-center">
        <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
        </svg>
      </div>
      <span class="text-gray-400 text-sm">Activos</span>
    </div>
    <div class="text-4xl font-black text-green-400">—</div>
  </div>
</div>

<!-- Tabla de datos recientes -->
<div class="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
  <div class="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
    <h2 class="text-white font-semibold">Registros recientes</h2>
    <a href="{% url 'catalog' %}" class="text-xs text-blue-400 hover:text-blue-300 transition-colors">Ver todos</a>
  </div>
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <tbody class="divide-y divide-gray-800">
        {% for item in items|slice:":10" %}
        <tr class="hover:bg-gray-800/50 transition-colors">
          <td class="px-6 py-4">
            <a href="{% url 'detail' item.pk %}" class="text-white font-medium hover:text-blue-400 transition-colors">
              {{ item.title }}
            </a>
          </td>
          <td class="px-6 py-4 text-gray-500">{{ item.category }}</td>
          <td class="px-6 py-4 text-right">
            <a href="{% url 'detail' item.pk %}" class="text-xs text-blue-400 hover:text-blue-300">Ver →</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

{% endblock %}
'''

DASHBOARD_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}

<div class="flex items-center justify-between mb-8">
  <div>
    <h1 class="text-2xl font-black text-white">Todos los registros</h1>
    <p class="text-gray-500 text-sm mt-1">{{ items|length }} entradas totales</p>
  </div>
</div>

<div class="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-gray-800 text-left">
          <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">#</th>
          <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
          <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Categoría</th>
          <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Valor</th>
          <th class="px-6 py-4"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-800">
        {% for item in items %}
        <tr class="hover:bg-gray-800/50 transition-colors">
          <td class="px-6 py-4 text-gray-600 font-mono">{{ forloop.counter }}</td>
          <td class="px-6 py-4">
            <span class="text-white font-medium">{{ item.title }}</span>
          </td>
          <td class="px-6 py-4">
            {% if item.category %}
            <span class="inline-block text-xs px-2 py-0.5 rounded-full bg-blue-400/10 text-blue-400 font-medium">
              {{ item.category }}
            </span>
            {% else %}
            <span class="text-gray-600">—</span>
            {% endif %}
          </td>
          <td class="px-6 py-4 text-gray-300 font-mono">{{ item.price }}</td>
          <td class="px-6 py-4 text-right">
            <a href="{% url 'detail' item.pk %}" class="text-xs text-blue-400 hover:text-blue-300 transition-colors">Ver →</a>
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="5" class="px-6 py-16 text-center text-gray-600">No hay datos disponibles.</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

{% endblock %}
'''


# ── REGISTRO DE EJEMPLOS ──────────────────────────────────────────────────────

EXAMPLES_BY_TYPE = {
    'catalog':   {'home': CATALOG_HOME_EXAMPLE,   'list': CATALOG_LIST_EXAMPLE,   'detail': CATALOG_DETAIL_EXAMPLE},
    'blog':      {'home': BLOG_HOME_EXAMPLE,       'list': BLOG_LIST_EXAMPLE,      'detail': BLOG_DETAIL_EXAMPLE},
    'portfolio': {'home': PORTFOLIO_HOME_EXAMPLE,  'list': PORTFOLIO_LIST_EXAMPLE, 'detail': PORTFOLIO_DETAIL_EXAMPLE},
    'dashboard': {'home': DASHBOARD_HOME_EXAMPLE,  'list': DASHBOARD_LIST_EXAMPLE},
}


def get_example(site_type: str, page_kind: str) -> str | None:
    return EXAMPLES_BY_TYPE.get(site_type, {}).get(page_kind)