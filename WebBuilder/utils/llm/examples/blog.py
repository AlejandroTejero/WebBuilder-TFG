"""Ejemplos HTML para sitios tipo blog."""

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
