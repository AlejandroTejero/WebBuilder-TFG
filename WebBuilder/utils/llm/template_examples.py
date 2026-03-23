"""
template_examples.py — Ejemplos HTML de referencia por tipo de sitio.
Se inyectan en el prompt de generación de templates como inspiración estructural.
El LLM debe adaptar el diseño libremente, no copiar el ejemplo.
"""


CATALOG_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  {% for item in items %}
    <a href="{% url 'detail' item.pk %}"
       class="block bg-gray-900 border border-gray-800 rounded-xl p-5
              hover:border-green-400 hover:shadow-lg transition-all">
      {% if item.image_url %}
        <img src="{{ item.image_url }}" class="w-full h-40 object-cover rounded-lg mb-4">
      {% endif %}
      <h2 class="text-white font-bold text-lg">{{ item.title }}</h2>
      <p class="text-gray-400 text-sm mt-1">{{ item.description|truncatechars:80 }}</p>
      <span class="text-green-400 font-bold mt-3 block">{{ item.price }}</span>
    </a>
  {% empty %}
    <p class="text-gray-500 col-span-3">No hay items todavía.</p>
  {% endfor %}
</div>
{% endblock %}
'''

CATALOG_DETAIL_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}
<div class="max-w-4xl mx-auto">
  <a href="{% url 'catalog' %}" class="text-green-400 text-sm hover:underline">← Volver</a>
  <div class="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-8 flex gap-8">
    {% if item.image_url %}
      <img src="{{ item.image_url }}" class="w-64 h-64 object-cover rounded-xl flex-shrink-0">
    {% endif %}
    <div>
      <h1 class="text-white text-3xl font-black">{{ item.title }}</h1>
      <p class="text-gray-400 mt-4">{{ item.description }}</p>
      <span class="text-green-400 text-2xl font-bold mt-6 block">{{ item.price }}</span>
    </div>
  </div>
</div>
{% endblock %}
'''

BLOG_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}
<div class="max-w-3xl mx-auto space-y-8">
  {% for item in items %}
    <article class="border-b border-gray-800 pb-8">
      <span class="text-green-400 text-xs uppercase tracking-widest">{{ item.category }}</span>
      <h2 class="text-white font-bold text-2xl mt-2">
        <a href="{% url 'detail' item.pk %}"
           class="hover:text-green-400 transition-colors">{{ item.title }}</a>
      </h2>
      <p class="text-gray-400 mt-2">{{ item.summary|truncatechars:120 }}</p>
      <span class="text-gray-600 text-xs mt-3 block">{{ item.pub_date }}</span>
    </article>
  {% endfor %}
</div>
{% endblock %}
'''

BLOG_DETAIL_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}
<div class="max-w-3xl mx-auto">
  <a href="{% url 'blog' %}" class="text-green-400 text-sm hover:underline">← Volver</a>
  <article class="mt-8">
    <h1 class="text-white text-4xl font-black">{{ item.title }}</h1>
    <span class="text-gray-500 text-sm mt-2 block">{{ item.pub_date }}</span>
    <div class="text-gray-300 mt-8 leading-relaxed">{{ item.content }}</div>
  </article>
</div>
{% endblock %}
'''

PORTFOLIO_LIST_EXAMPLE = '''
{% extends 'base.html' %}
{% block content %}
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  {% for item in items %}
    <a href="{% url 'detail' item.pk %}"
       class="group block bg-gray-900 border border-gray-800 rounded-xl overflow-hidden
              hover:border-green-400 transition-all">
      {% if item.image_url %}
        <img src="{{ item.image_url }}" class="w-full h-48 object-cover
             group-hover:opacity-80 transition-opacity">
      {% endif %}
      <div class="p-5">
        <h2 class="text-white font-bold text-lg">{{ item.title }}</h2>
        <p class="text-gray-400 text-sm mt-1">{{ item.description|truncatechars:80 }}</p>
      </div>
    </a>
  {% endfor %}
</div>
{% endblock %}
'''

EXAMPLES_BY_TYPE = {
    'catalog': {'list': CATALOG_LIST_EXAMPLE, 'detail': CATALOG_DETAIL_EXAMPLE},
    'blog':    {'list': BLOG_LIST_EXAMPLE,    'detail': BLOG_DETAIL_EXAMPLE},
    'portfolio': {'list': PORTFOLIO_LIST_EXAMPLE},
}


def get_example(site_type: str, page_kind: str) -> str | None:
    return EXAMPLES_BY_TYPE.get(site_type, {}).get(page_kind)