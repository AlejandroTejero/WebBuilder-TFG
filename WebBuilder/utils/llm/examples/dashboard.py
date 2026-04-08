"""Ejemplos HTML para sitios tipo dashboard."""

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
