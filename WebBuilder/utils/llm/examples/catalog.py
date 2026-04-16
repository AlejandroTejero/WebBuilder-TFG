# -*- coding: utf-8 -*-
"""
Reusable Django + Tailwind catalog templates for automatic site generation.

This module exposes 9 HTML template constants organized by:
- 3 page types: home, list, detail
- 3 visual styles: dark, light, editorial

Each template:
- Extends ``base.html``
- Uses Django template tags and generic field placeholders
- Avoids assuming concrete model field names
- Is intended as a high-quality starting point for generated projects
"""

# ---------------------------------------------------------------------------
# HOME · DARK
# ---------------------------------------------------------------------------

CATALOG_HOME_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="grid gap-10 lg:grid-cols-12 lg:items-end">
            <div class="lg:col-span-7">
                <p class="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400">
                    Colección destacada
                </p>
                <h1 class="max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                    Explora una selección visual de contenidos con una presentación sólida y contemporánea.
                </h1>
                <p class="mt-6 max-w-2xl text-base leading-8 text-gray-300 sm:text-lg">
                    Esta portada prioriza impacto visual, jerarquía clara y una llamada a la acción directa hacia el
                    catálogo completo.
                </p>
                <div class="mt-8 flex flex-wrap items-center gap-4">
                    <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                       class="inline-flex items-center justify-center rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-gray-950 transition hover:bg-emerald-400">
                        Ver listado completo
                    </a>
                    <a href="{% url 'NOMBRE_URL_HOME' %}"
                       class="inline-flex items-center justify-center rounded-xl border border-gray-800 px-5 py-3 text-sm font-semibold text-white transition hover:border-gray-700 hover:bg-gray-900">
                        Volver al inicio
                    </a>
                </div>
            </div>
            <div class="lg:col-span-5">
                <div class="rounded-3xl border border-gray-800 bg-gray-900 p-6 shadow-2xl">
                    <p class="text-sm font-medium text-gray-400">Resumen</p>
                    <div class="mt-4 space-y-4">
                        <div class="rounded-2xl border border-gray-800 bg-gray-950 p-4">
                            <p class="text-sm text-gray-400">Diseño</p>
                            <p class="mt-2 text-lg font-semibold text-white">Oscuro, visual y enfocado en tarjetas</p>
                        </div>
                        <div class="rounded-2xl border border-gray-800 bg-gray-950 p-4">
                            <p class="text-sm text-gray-400">Uso ideal</p>
                            <p class="mt-2 text-lg font-semibold text-white">Catálogos, portfolios y colecciones dinámicas</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-16 flex items-end justify-between gap-4">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400">Destacados</p>
                <h2 class="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
                    Selección principal
                </h2>
            </div>
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="hidden text-sm font-semibold text-emerald-400 transition hover:text-emerald-300 sm:inline">
                Ver todo
            </a>
        </div>

        <div class="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
			{% for item in featured %}
                <article class="overflow-hidden rounded-3xl border border-gray-800 bg-gray-900 shadow-xl">
                    {% if item.CAMPO_IMAGEN %}
                        <div class="aspect-[16/10] overflow-hidden bg-gray-800">
                            <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                        </div>
                    {% endif %}

                    <div class="p-6">
                        {% if item.CAMPO_CATEGORIA %}
                            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-400">
                                {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                            </p>
                        {% endif %}

                        <h3 class="mt-3 text-xl font-semibold tracking-tight text-white">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h3>

                        {% if item.CAMPO_DESCRIPCION %}
                            <p class="mt-3 line-clamp-3 text-sm leading-7 text-gray-300">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        {% endif %}

                        <div class="mt-5 flex flex-wrap items-center gap-3 text-sm text-gray-400">
                            {% if item.CAMPO_PRECIO %}
                                <span class="rounded-full border border-gray-800 px-3 py-1">
                                    {{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <span class="rounded-full border border-gray-800 px-3 py-1">
                                    {{ item.CAMPO_FECHA }} {# campo fecha #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <span class="rounded-full border border-gray-800 px-3 py-1">
                                    {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </span>
                            {% endif %}
                        </div>

                        <div class="mt-6">
                            <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                               class="inline-flex items-center text-sm font-semibold text-emerald-400 transition hover:text-emerald-300">
                                Ver detalle
                            </a>
                        </div>
                    </div>
                </article>
            {% empty %}
                <div class="md:col-span-2 xl:col-span-3">
                    <div class="rounded-3xl border border-dashed border-gray-800 bg-gray-900 px-6 py-12 text-center">
                        <h3 class="text-lg font-semibold text-white">Todavía no hay elementos destacados</h3>
                        <p class="mt-3 text-sm text-gray-400">
                            Cuando existan registros disponibles, aparecerán aquí los primeros resultados del catálogo.
                        </p>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · LIGHT
# ---------------------------------------------------------------------------

CATALOG_HOME_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="max-w-3xl">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                Bienvenida
            </p>
            <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                Una portada clara y elegante para presentar tu catálogo con orden y confianza.
            </h1>
            <p class="mt-6 text-lg leading-8 text-gray-600">
                Este diseño prioriza espacios amplios, lectura cómoda y una navegación sencilla hacia el listado
                completo y sus fichas de detalle.
            </p>
            <div class="mt-8 flex flex-wrap gap-4">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800">
                    Explorar listado
                </a>
                <a href="{% url 'NOMBRE_URL_HOME' %}"
                   class="inline-flex items-center justify-center rounded-xl border border-gray-300 bg-white px-5 py-3 text-sm font-semibold text-gray-900 transition hover:bg-gray-100">
                    Inicio
                </a>
            </div>
        </div>

        <div class="mt-16 flex items-end justify-between gap-4">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Selección</p>
                <h2 class="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                    Elementos destacados
                </h2>
            </div>
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="hidden text-sm font-semibold text-gray-900 transition hover:text-gray-700 sm:inline">
                Ver todos
            </a>
        </div>

        <div class="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
			{% for item in featured %}
                <article class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
                    {% if item.CAMPO_IMAGEN %}
                        <div class="aspect-[16/10] overflow-hidden bg-gray-100">
                            <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                        </div>
                    {% endif %}

                    <div class="p-6">
                        {% if item.CAMPO_CATEGORIA %}
                            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                            </p>
                        {% endif %}

                        <h3 class="mt-3 text-xl font-semibold tracking-tight text-gray-900">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h3>

                        {% if item.CAMPO_DESCRIPCION %}
                            <p class="mt-3 line-clamp-3 text-sm leading-7 text-gray-600">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        {% endif %}

                        <div class="mt-5 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                            {% if item.CAMPO_PRECIO %}
                                <span class="rounded-full bg-gray-100 px-3 py-1">
                                    {{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <span class="rounded-full bg-gray-100 px-3 py-1">
                                    {{ item.CAMPO_FECHA }} {# campo fecha #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <span class="rounded-full bg-gray-100 px-3 py-1">
                                    {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </span>
                            {% endif %}
                        </div>

                        <div class="mt-6">
                            <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                               class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                                Abrir detalle
                            </a>
                        </div>
                    </div>
                </article>
            {% empty %}
                <div class="md:col-span-2 xl:col-span-3">
                    <div class="rounded-3xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
                        <h3 class="text-lg font-semibold text-gray-900">No hay elementos destacados todavía</h3>
                        <p class="mt-3 text-sm text-gray-600">
                            Esta sección mostrará automáticamente los primeros elementos disponibles del catálogo.
                        </p>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · EDITORIAL
# ---------------------------------------------------------------------------

CATALOG_HOME_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="border-b border-stone-200 pb-10">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Edición principal
            </p>
            <h1 class="mt-5 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                Una portada editorial que pone el foco en la lectura, el contexto y la selección cuidada.
            </h1>
            <p class="mt-6 max-w-3xl text-lg leading-8 text-stone-600">
                Ideal para proyectos con narrativa, archivos culturales, blogs temáticos o catálogos donde el texto
                y los metadatos necesitan respirar.
            </p>
            <div class="mt-8 flex flex-wrap gap-4">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-full bg-stone-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-stone-800">
                    Ir al listado
                </a>
                <a href="{% url 'NOMBRE_URL_HOME' %}"
                   class="inline-flex items-center justify-center rounded-full border border-stone-300 px-5 py-3 text-sm font-semibold text-stone-900 transition hover:bg-stone-100">
                    Portada
                </a>
            </div>
        </div>

        <div class="mt-12">
            <div class="mb-8 flex items-end justify-between gap-4">
                <div>
                    <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">Selección</p>
                    <h2 class="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                        Destacados recientes
                    </h2>
                </div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="hidden text-sm font-semibold text-stone-900 transition hover:text-stone-700 sm:inline">
                    Ver archivo completo
                </a>
            </div>

            <div class="divide-y divide-stone-200 border-y border-stone-200">
				{% for item in featured %}
                    <article class="py-8">
                        <div class="grid gap-4 md:grid-cols-12">
                            <div class="md:col-span-3">
                                <div class="flex flex-wrap items-center gap-3 text-sm text-stone-500">
                                    {% if item.CAMPO_CATEGORIA %}
                                        <span>{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                                    {% endif %}
                                    {% if item.CAMPO_FECHA %}
                                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                    {% endif %}
                                </div>
                            </div>
                            <div class="md:col-span-9">
                                <h3 class="text-2xl font-semibold leading-tight tracking-tight text-stone-900">
                                    <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-stone-700">
                                        {{ item.CAMPO_TITULO }} {# campo título principal #}
                                    </a>
                                </h3>

                                {% if item.CAMPO_DESCRIPCION %}
                                    <p class="mt-3 max-w-3xl text-base leading-8 text-stone-600">
                                        {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                    </p>
                                {% endif %}

                                <div class="mt-4 flex flex-wrap items-center gap-4 text-sm text-stone-500">
                                    {% if item.CAMPO_PRECIO %}
                                        <span>{{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}</span>
                                    {% endif %}
                                    {% if item.CAMPO_EXTRA %}
                                        <span>{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</span>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </article>
                {% empty %}
                    <div class="px-2 py-12 text-center">
                        <h3 class="text-lg font-semibold text-stone-900">No hay contenidos para destacar</h3>
                        <p class="mt-3 text-sm text-stone-600">
                            La portada editorial mostrará aquí una selección automática de hasta seis elementos.
                        </p>
                    </div>
                {% endfor %}
            </div>
        </div>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · DARK
# ---------------------------------------------------------------------------

CATALOG_LIST_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="flex flex-col gap-6 border-b border-gray-800 pb-8 md:flex-row md:items-end md:justify-between">
            <div class="max-w-3xl">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                    Archivo completo
                </p>
                <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                    Listado general
                </h1>
                <p class="mt-4 text-base leading-8 text-gray-300">
                    Recorre todos los elementos disponibles en una vista visual con acceso rápido al detalle.
                </p>
            </div>
            <div class="w-full max-w-md">
                <label for="search-input" class="mb-2 block text-sm font-medium text-gray-300">
                    Buscar en el listado
                </label>
                <input
                    id="search-input"
                    type="search"
                    placeholder="Buscar por título, categoría o información adicional"
                    class="w-full rounded-2xl border border-gray-800 bg-gray-900 px-4 py-3 text-sm text-white placeholder:text-gray-500 focus:border-blue-400 focus:outline-none"
                >
            </div>
        </div>

        <div class="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
			{% for item in page_obj %}
                <article
                    class="search-item overflow-hidden rounded-3xl border border-gray-800 bg-gray-900 shadow-xl"
                    data-search="{{ item.CAMPO_TITULO }} {% if item.CAMPO_CATEGORIA %}{{ item.CAMPO_CATEGORIA }}{% endif %} {% if item.CAMPO_EXTRA %}{{ item.CAMPO_EXTRA }}{% endif %} {% if item.CAMPO_DESCRIPCION %}{{ item.CAMPO_DESCRIPCION }}{% endif %}"
                >
                    {% if item.CAMPO_IMAGEN %}
                        <div class="aspect-[16/10] overflow-hidden bg-gray-800">
                            <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                        </div>
                    {% endif %}

                    <div class="p-6">
                        {% if item.CAMPO_CATEGORIA %}
                            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
                                {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                            </p>
                        {% endif %}

                        <h2 class="mt-3 text-xl font-semibold tracking-tight text-white">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h2>

                        {% if item.CAMPO_DESCRIPCION %}
                            <p class="mt-3 line-clamp-3 text-sm leading-7 text-gray-300">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        {% endif %}

                        <div class="mt-5 flex flex-wrap items-center gap-3 text-sm text-gray-400">
                            {% if item.CAMPO_PRECIO %}
                                <span class="rounded-full border border-gray-800 px-3 py-1">
                                    {{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <span class="rounded-full border border-gray-800 px-3 py-1">
                                    {{ item.CAMPO_FECHA }} {# campo fecha #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <span class="rounded-full border border-gray-800 px-3 py-1">
                                    {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </span>
                            {% endif %}
                        </div>

                        <div class="mt-6">
                            <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                               class="inline-flex items-center text-sm font-semibold text-blue-400 transition hover:text-blue-300">
                                Abrir ficha
                            </a>
                        </div>
                    </div>
                </article>
            {% empty %}
                <div class="md:col-span-2 xl:col-span-3">
                    <div class="rounded-3xl border border-dashed border-gray-800 bg-gray-900 px-6 py-12 text-center">
                        <h2 class="text-lg font-semibold text-white">No hay elementos disponibles</h2>
                        <p class="mt-3 text-sm text-gray-400">
                            Cuando el catálogo tenga registros, aparecerán aquí con acceso directo a su detalle.
                        </p>
                    </div>
                </div>
            {% endfor %}
        </div>

        {% if page_obj %}
            <nav class="mt-10 flex flex-wrap items-center justify-center gap-3" aria-label="Paginación">
                {% if page_obj.has_previous %}
                    <a href="?page={{ page_obj.previous_page_number }}"
                       class="inline-flex items-center rounded-xl border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:border-gray-700 hover:bg-gray-800">
                        Anterior
                    </a>
                {% endif %}

                <span class="inline-flex items-center rounded-xl border border-gray-800 px-4 py-2 text-sm text-gray-300">
                    Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
                </span>

                {% if page_obj.has_next %}
                    <a href="?page={{ page_obj.next_page_number }}"
                       class="inline-flex items-center rounded-xl border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:border-gray-700 hover:bg-gray-800">
                        Siguiente
                    </a>
                {% endif %}
            </nav>
        {% endif %}
    </div>
</section>

<script>
    document.addEventListener('DOMContentLoaded', function () {
        const input = document.getElementById('search-input');
        const items = document.querySelectorAll('.search-item');

        if (!input) {
            return;
        }

        input.addEventListener('input', function () {
            const value = input.value.toLowerCase().trim();

            items.forEach(function (card) {
                const content = (card.getAttribute('data-search') || '').toLowerCase();
                const visible = content.includes(value);
                card.style.display = visible ? '' : 'none';
            });
        });
    });
</script>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · LIGHT
# ---------------------------------------------------------------------------

CATALOG_LIST_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-white text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="flex flex-col gap-6 border-b border-gray-200 pb-8 md:flex-row md:items-end md:justify-between">
            <div class="max-w-3xl">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                    Catálogo
                </p>
                <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                    Todos los elementos
                </h1>
                <p class="mt-4 text-base leading-8 text-gray-600">
                    Una vista limpia y espaciosa para navegar cómodamente por el contenido disponible.
                </p>
            </div>
            <div class="w-full max-w-md">
                <label for="search-input" class="mb-2 block text-sm font-medium text-gray-700">
                    Buscar en el listado
                </label>
                <input
                    id="search-input"
                    type="search"
                    placeholder="Buscar por título, categoría o información adicional"
                    class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-gray-900 focus:outline-none"
                >
            </div>
        </div>

        <div class="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
			{% for item in page_obj %}
                <article
                    class="search-item overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200"
                    data-search="{{ item.CAMPO_TITULO }} {% if item.CAMPO_CATEGORIA %}{{ item.CAMPO_CATEGORIA }}{% endif %} {% if item.CAMPO_EXTRA %}{{ item.CAMPO_EXTRA }}{% endif %} {% if item.CAMPO_DESCRIPCION %}{{ item.CAMPO_DESCRIPCION }}{% endif %}"
                >
                    {% if item.CAMPO_IMAGEN %}
                        <div class="aspect-[16/10] overflow-hidden bg-gray-100">
                            <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                        </div>
                    {% endif %}

                    <div class="p-6">
                        {% if item.CAMPO_CATEGORIA %}
                            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                            </p>
                        {% endif %}

                        <h2 class="mt-3 text-xl font-semibold tracking-tight text-gray-900">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h2>

                        {% if item.CAMPO_DESCRIPCION %}
                            <p class="mt-3 line-clamp-3 text-sm leading-7 text-gray-600">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        {% endif %}

                        <div class="mt-5 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                            {% if item.CAMPO_PRECIO %}
                                <span class="rounded-full bg-gray-100 px-3 py-1">
                                    {{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <span class="rounded-full bg-gray-100 px-3 py-1">
                                    {{ item.CAMPO_FECHA }} {# campo fecha #}
                                </span>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <span class="rounded-full bg-gray-100 px-3 py-1">
                                    {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </span>
                            {% endif %}
                        </div>

                        <div class="mt-6">
                            <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                               class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                                Ver detalle
                            </a>
                        </div>
                    </div>
                </article>
            {% empty %}
                <div class="md:col-span-2 xl:col-span-3">
                    <div class="rounded-3xl border border-dashed border-gray-300 bg-gray-50 px-6 py-12 text-center">
                        <h2 class="text-lg font-semibold text-gray-900">No hay elementos para mostrar</h2>
                        <p class="mt-3 text-sm text-gray-600">
                            El catálogo está vacío por ahora. Esta vista mostrará automáticamente los registros cuando existan.
                        </p>
                    </div>
                </div>
            {% endfor %}
        </div>

        {% if page_obj %}
            <nav class="mt-10 flex flex-wrap items-center justify-center gap-3" aria-label="Paginación">
                {% if page_obj.has_previous %}
                    <a href="?page={{ page_obj.previous_page_number }}"
                       class="inline-flex items-center rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-900 transition hover:bg-gray-100">
                        Anterior
                    </a>
                {% endif %}

                <span class="inline-flex items-center rounded-xl border border-gray-300 px-4 py-2 text-sm text-gray-600">
                    Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
                </span>

                {% if page_obj.has_next %}
                    <a href="?page={{ page_obj.next_page_number }}"
                       class="inline-flex items-center rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-900 transition hover:bg-gray-100">
                        Siguiente
                    </a>
                {% endif %}
            </nav>
        {% endif %}
    </div>
</section>

<script>
    document.addEventListener('DOMContentLoaded', function () {
        const input = document.getElementById('search-input');
        const items = document.querySelectorAll('.search-item');

        if (!input) {
            return;
        }

        input.addEventListener('input', function () {
            const value = input.value.toLowerCase().trim();

            items.forEach(function (card) {
                const content = (card.getAttribute('data-search') || '').toLowerCase();
                const visible = content.includes(value);
                card.style.display = visible ? '' : 'none';
            });
        });
    });
</script>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · EDITORIAL
# ---------------------------------------------------------------------------

CATALOG_LIST_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="border-b border-stone-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Archivo
            </p>
            <h1 class="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Listado editorial
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-stone-600">
                Una vista sobria y vertical, pensada para priorizar lectura, contexto y navegación entre piezas.
            </p>
        </div>

        <div class="divide-y divide-stone-200">
			{% for item in page_obj %}
                <article class="py-8">
                    <div class="grid gap-4 md:grid-cols-12">
                        <div class="md:col-span-3">
                            <div class="flex flex-wrap items-center gap-3 text-sm text-stone-500">
                                {% if item.CAMPO_CATEGORIA %}
                                    <span>{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                                {% endif %}
                                {% if item.CAMPO_FECHA %}
                                    <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                {% endif %}
                            </div>
                        </div>

                        <div class="md:col-span-9">
                            <h2 class="text-2xl font-semibold leading-tight tracking-tight text-stone-900">
                                <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-stone-700">
                                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                                </a>
                            </h2>

                            {% if item.CAMPO_DESCRIPCION %}
                                <p class="mt-3 max-w-3xl text-base leading-8 text-stone-600">
                                    {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                </p>
                            {% endif %}

                            <div class="mt-4 flex flex-wrap items-center gap-4 text-sm text-stone-500">
                                {% if item.CAMPO_PRECIO %}
                                    <span>{{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}</span>
                                {% endif %}
                                {% if item.CAMPO_EXTRA %}
                                    <span>{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</span>
                                {% endif %}
                            </div>

                            <div class="mt-5">
                                <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                                   class="text-sm font-semibold text-stone-900 transition hover:text-stone-700">
                                    Leer detalle
                                </a>
                            </div>
                        </div>
                    </div>
                </article>
            {% empty %}
                <div class="py-12 text-center">
                    <h2 class="text-lg font-semibold text-stone-900">No hay entradas disponibles</h2>
                    <p class="mt-3 text-sm text-stone-600">
                        Esta vista editorial mostrará cada elemento en formato vertical cuando existan registros.
                    </p>
                </div>
            {% endfor %}
        </div>

        {% if page_obj %}
            <nav class="mt-10 flex flex-wrap items-center justify-center gap-3" aria-label="Paginación">
                {% if page_obj.has_previous %}
                    <a href="?page={{ page_obj.previous_page_number }}"
                       class="inline-flex items-center rounded-full border border-stone-300 px-4 py-2 text-sm font-semibold text-stone-900 transition hover:bg-stone-100">
                        Anterior
                    </a>
                {% endif %}

                <span class="inline-flex items-center rounded-full border border-stone-300 px-4 py-2 text-sm text-stone-600">
                    Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
                </span>

                {% if page_obj.has_next %}
                    <a href="?page={{ page_obj.next_page_number }}"
                       class="inline-flex items-center rounded-full border border-stone-300 px-4 py-2 text-sm font-semibold text-stone-900 transition hover:bg-stone-100">
                        Siguiente
                    </a>
                {% endif %}
            </nav>
        {% endif %}
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · DARK
# ---------------------------------------------------------------------------

CATALOG_DETAIL_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-emerald-400 transition hover:text-emerald-300">
                ← Volver al listado
            </a>
        </div>

        <article class="grid gap-10 lg:grid-cols-12">
            <header class="lg:col-span-5">
                {% if item.CAMPO_CATEGORIA %}
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400">
                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                    </p>
                {% endif %}

                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                <div class="mt-6 flex flex-wrap items-center gap-3 text-sm text-gray-400">
                    {% if item.CAMPO_FECHA %}
                        <span class="rounded-full border border-gray-800 px-3 py-1">
                            {{ item.CAMPO_FECHA }} {# campo fecha #}
                        </span>
                    {% endif %}
                    {% if item.CAMPO_PRECIO %}
                        <span class="rounded-full border border-gray-800 px-3 py-1">
                            {{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}
                        </span>
                    {% endif %}
                    {% if item.CAMPO_EXTRA %}
                        <span class="rounded-full border border-gray-800 px-3 py-1">
                            {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                        </span>
                    {% endif %}
                </div>

                {% if item.CAMPO_DESCRIPCION %}
                    <div class="mt-8 rounded-3xl border border-gray-800 bg-gray-900 p-6">
                        <h2 class="text-lg font-semibold text-white">Descripción</h2>
                        <p class="mt-4 text-base leading-8 text-gray-300">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    </div>
                {% endif %}
            </header>

            <div class="lg:col-span-7">
                {% if item.CAMPO_IMAGEN %}
                    <div class="overflow-hidden rounded-3xl border border-gray-800 bg-gray-900 shadow-2xl">
                        <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                    </div>
                {% endif %}

                <div class="mt-8 rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <h2 class="text-lg font-semibold text-white">Atributos</h2>
                    <dl class="mt-6 divide-y divide-gray-800">
                        {% if item.CAMPO_CATEGORIA %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-400">Categoría</dt>
                                <dd class="text-sm text-white">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_PRECIO %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-400">Valor</dt>
                                <dd class="text-sm text-white">{{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_FECHA %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-400">Fecha</dt>
                                <dd class="text-sm text-white">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_EXTRA %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-400">Información adicional</dt>
                                <dd class="text-sm text-white">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
                            </div>
                        {% endif %}
                    </dl>
                </div>
            </div>
        </article>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · LIGHT
# ---------------------------------------------------------------------------

CATALOG_DETAIL_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                ← Volver al listado
            </a>
        </div>

        <article class="grid gap-10 lg:grid-cols-12">
            <header class="lg:col-span-5">
                {% if item.CAMPO_CATEGORIA %}
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                    </p>
                {% endif %}

                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                <div class="mt-6 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                    {% if item.CAMPO_FECHA %}
                        <span class="rounded-full bg-white px-3 py-1 shadow-sm ring-1 ring-gray-200">
                            {{ item.CAMPO_FECHA }} {# campo fecha #}
                        </span>
                    {% endif %}
                    {% if item.CAMPO_PRECIO %}
                        <span class="rounded-full bg-white px-3 py-1 shadow-sm ring-1 ring-gray-200">
                            {{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}
                        </span>
                    {% endif %}
                    {% if item.CAMPO_EXTRA %}
                        <span class="rounded-full bg-white px-3 py-1 shadow-sm ring-1 ring-gray-200">
                            {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                        </span>
                    {% endif %}
                </div>

                {% if item.CAMPO_DESCRIPCION %}
                    <div class="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                        <h2 class="text-lg font-semibold text-gray-900">Descripción</h2>
                        <p class="mt-4 text-base leading-8 text-gray-600">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    </div>
                {% endif %}
            </header>

            <div class="lg:col-span-7">
                {% if item.CAMPO_IMAGEN %}
                    <div class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
                        <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                    </div>
                {% endif %}

                <div class="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900">Ficha técnica</h2>
                    <dl class="mt-6 divide-y divide-gray-200">
                        {% if item.CAMPO_CATEGORIA %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-500">Categoría</dt>
                                <dd class="text-sm text-gray-900">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_PRECIO %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-500">Valor</dt>
                                <dd class="text-sm text-gray-900">{{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_FECHA %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-500">Fecha</dt>
                                <dd class="text-sm text-gray-900">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_EXTRA %}
                            <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between">
                                <dt class="text-sm font-medium text-gray-500">Información adicional</dt>
                                <dd class="text-sm text-gray-900">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
                            </div>
                        {% endif %}
                    </dl>
                </div>
            </div>
        </article>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · EDITORIAL
# ---------------------------------------------------------------------------

CATALOG_DETAIL_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-4xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-10">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-stone-900 transition hover:text-stone-700">
                ← Volver al archivo
            </a>
        </div>

        <article>
            <header class="border-b border-stone-200 pb-8">
                {% if item.CAMPO_CATEGORIA %}
                    <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                    </p>
                {% endif %}

                <h1 class="mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                <div class="mt-6 flex flex-wrap items-center gap-4 text-sm text-stone-500">
                    {% if item.CAMPO_FECHA %}
                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                    {% endif %}
                    {% if item.CAMPO_PRECIO %}
                        <span>{{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}</span>
                    {% endif %}
                    {% if item.CAMPO_EXTRA %}
                        <span>{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</span>
                    {% endif %}
                </div>
            </header>

            {% if item.CAMPO_IMAGEN %}
                <div class="mt-10 overflow-hidden rounded-3xl border border-stone-200 bg-white">
                    <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                </div>
            {% endif %}

            <div class="mt-10 grid gap-10 lg:grid-cols-12">
                <div class="lg:col-span-8">
                    {% if item.CAMPO_DESCRIPCION %}
                        <section>
                            <h2 class="text-xl font-semibold text-stone-900">Texto completo</h2>
                            <div class="mt-5 text-base leading-8 text-stone-700">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </div>
                        </section>
                    {% endif %}
                </div>

                <aside class="lg:col-span-4">
                    <div class="rounded-3xl border border-stone-200 bg-white p-6">
                        <h2 class="text-lg font-semibold text-stone-900">Metadatos</h2>
                        <dl class="mt-6 space-y-5">
                            {% if item.CAMPO_CATEGORIA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Categoría</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_PRECIO %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Valor</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_PRECIO }} {# campo precio o valor numérico #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Fecha</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Información adicional</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
                                </div>
                            {% endif %}
                        </dl>
                    </div>
                </aside>
            </div>
        </article>
    </div>
</section>
{% endblock %}"""

__all__ = [
    "CATALOG_HOME_DARK",
    "CATALOG_HOME_LIGHT",
    "CATALOG_HOME_EDITORIAL",
    "CATALOG_LIST_DARK",
    "CATALOG_LIST_LIGHT",
    "CATALOG_LIST_EDITORIAL",
    "CATALOG_DETAIL_DARK",
    "CATALOG_DETAIL_LIGHT",
    "CATALOG_DETAIL_EDITORIAL",
]