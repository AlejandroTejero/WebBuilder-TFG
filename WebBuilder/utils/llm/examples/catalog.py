"""Ejemplos HTML para sitios tipo catálogo."""

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
