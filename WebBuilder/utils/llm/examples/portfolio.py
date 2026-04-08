"""Ejemplos HTML para sitios tipo portfolio."""

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
