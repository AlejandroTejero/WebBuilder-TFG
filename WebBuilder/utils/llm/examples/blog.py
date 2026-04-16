# -*- coding: utf-8 -*-
"""
Reusable Django + Tailwind blog templates for automatic site generation.

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

BLOG_HOME_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-800 pb-10">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-400">
                Publicaciones
            </p>
            <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                Un blog con presencia visual, lectura clara y jerarquía editorial.
            </h1>
            <p class="mt-6 max-w-3xl text-lg leading-8 text-gray-300">
                Esta portada destaca un artículo principal y acompaña la lectura con una selección reciente
                en un entorno oscuro y elegante.
            </p>
            <div class="mt-8">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400">
                    Ver todas las publicaciones
                </a>
            </div>
        </header>

        {% with items.0 as featured %}
            {% if featured %}
                <section class="mt-12 grid gap-8 lg:grid-cols-12 lg:items-stretch">
                    <div class="overflow-hidden rounded-3xl border border-gray-800 bg-gray-900 lg:col-span-7">
                        {% if featured.CAMPO_IMAGEN %}
                            <div class="aspect-[16/10] overflow-hidden bg-gray-800">
                                <img src="{{ featured.CAMPO_IMAGEN }}" alt="{{ featured.CAMPO_TITULO }}" class="h-full w-full object-cover">
                            </div>
                        {% endif %}
                        <div class="p-8">
                            <div class="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                                {% if featured.CAMPO_FECHA %}
                                    <span>{{ featured.CAMPO_FECHA }} {# campo fecha #}</span>
                                {% endif %}
                                {% if featured.CAMPO_AUTOR %}
                                    <span>{{ featured.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                                {% endif %}
                                {% if featured.CAMPO_CATEGORIA %}
                                    <span>{{ featured.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                                {% endif %}
                            </div>

                            <h2 class="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
                                {{ featured.CAMPO_TITULO }} {# campo título principal #}
                            </h2>

                            {% if featured.CAMPO_DESCRIPCION %}
                                <p class="mt-5 text-base leading-8 text-gray-300">
                                    {{ featured.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                </p>
                            {% endif %}

                            {% if featured.CAMPO_EXTRA %}
                                <p class="mt-4 text-sm text-gray-400">
                                    {{ featured.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </p>
                            {% endif %}

                            <div class="mt-8">
                                <a href="{% url 'NOMBRE_URL_DETALLE' featured.pk %}"
                                   class="inline-flex items-center text-sm font-semibold text-indigo-400 transition hover:text-indigo-300">
                                    Leer artículo
                                </a>
                            </div>
                        </div>
                    </div>

                    <aside class="lg:col-span-5">
                        <div class="rounded-3xl border border-gray-800 bg-gray-900 p-6">
                            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-400">
                                Recientes
                            </p>
                            <div class="mt-6 space-y-6">
								{% for item in featured %}
                                    <article class="border-b border-gray-800 pb-6 last:border-b-0 last:pb-0">
                                        <div class="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                                            {% if item.CAMPO_FECHA %}
                                                <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                            {% endif %}
                                            {% if item.CAMPO_AUTOR %}
                                                <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                                            {% endif %}
                                        </div>

                                        <h3 class="mt-3 text-lg font-semibold tracking-tight text-white">
                                            <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-indigo-300">
                                                {{ item.CAMPO_TITULO }} {# campo título principal #}
                                            </a>
                                        </h3>

                                        {% if item.CAMPO_CATEGORIA %}
                                            <p class="mt-2 text-sm text-indigo-400">
                                                {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                            </p>
                                        {% endif %}
                                    </article>
                                {% empty %}
                                    <div class="rounded-2xl border border-dashed border-gray-800 px-4 py-8 text-center">
                                        <h3 class="text-lg font-semibold text-white">No hay artículos recientes</h3>
                                        <p class="mt-3 text-sm text-gray-400">
                                            Las publicaciones más recientes aparecerán aquí automáticamente.
                                        </p>
                                    </div>
                                {% endfor %}
                            </div>
                        </div>
                    </aside>
                </section>
            {% else %}
                <section class="mt-12">
                    <div class="rounded-3xl border border-dashed border-gray-800 bg-gray-900 px-6 py-12 text-center">
                        <h2 class="text-2xl font-semibold text-white">Todavía no hay artículos publicados</h2>
                        <p class="mt-4 text-sm text-gray-400">
                            Cuando el blog tenga contenido, esta portada mostrará un artículo destacado y varias entradas recientes.
                        </p>
                    </div>
                </section>
            {% endif %}
        {% endwith %}
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · LIGHT
# ---------------------------------------------------------------------------

BLOG_HOME_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-200 pb-10">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                Blog
            </p>
            <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                Un espacio limpio y luminoso para compartir artículos con claridad.
            </h1>
            <p class="mt-6 max-w-3xl text-lg leading-8 text-gray-600">
                La portada presenta un artículo principal y acompaña con una selección reciente en un diseño
                sereno, espacioso y fácil de recorrer.
            </p>
            <div class="mt-8">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800">
                    Ver todas las publicaciones
                </a>
            </div>
        </header>

        {% with items.0 as featured %}
            {% if featured %}
                <section class="mt-12 grid gap-8 lg:grid-cols-12 lg:items-stretch">
                    <div class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200 lg:col-span-7">
                        {% if featured.CAMPO_IMAGEN %}
                            <div class="aspect-[16/10] overflow-hidden bg-gray-100">
                                <img src="{{ featured.CAMPO_IMAGEN }}" alt="{{ featured.CAMPO_TITULO }}" class="h-full w-full object-cover">
                            </div>
                        {% endif %}
                        <div class="p-8">
                            <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                                {% if featured.CAMPO_FECHA %}
                                    <span>{{ featured.CAMPO_FECHA }} {# campo fecha #}</span>
                                {% endif %}
                                {% if featured.CAMPO_AUTOR %}
                                    <span>{{ featured.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                                {% endif %}
                                {% if featured.CAMPO_CATEGORIA %}
                                    <span>{{ featured.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                                {% endif %}
                            </div>

                            <h2 class="mt-4 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                                {{ featured.CAMPO_TITULO }} {# campo título principal #}
                            </h2>

                            {% if featured.CAMPO_DESCRIPCION %}
                                <p class="mt-5 text-base leading-8 text-gray-600">
                                    {{ featured.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                </p>
                            {% endif %}

                            {% if featured.CAMPO_EXTRA %}
                                <p class="mt-4 text-sm text-gray-500">
                                    {{ featured.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </p>
                            {% endif %}

                            <div class="mt-8">
                                <a href="{% url 'NOMBRE_URL_DETALLE' featured.pk %}"
                                   class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                                    Leer artículo
                                </a>
                            </div>
                        </div>
                    </div>

                    <aside class="lg:col-span-5">
                        <div class="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                                Recientes
                            </p>
                            <div class="mt-6 space-y-6">
								{% for item in featured %}
                                    <article class="border-b border-gray-200 pb-6 last:border-b-0 last:pb-0">
                                        <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                                            {% if item.CAMPO_FECHA %}
                                                <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                            {% endif %}
                                            {% if item.CAMPO_AUTOR %}
                                                <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                                            {% endif %}
                                        </div>

                                        <h3 class="mt-3 text-lg font-semibold tracking-tight text-gray-900">
                                            <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-gray-700">
                                                {{ item.CAMPO_TITULO }} {# campo título principal #}
                                            </a>
                                        </h3>

                                        {% if item.CAMPO_CATEGORIA %}
                                            <p class="mt-2 text-sm text-gray-500">
                                                {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                            </p>
                                        {% endif %}
                                    </article>
                                {% empty %}
                                    <div class="rounded-2xl border border-dashed border-gray-300 px-4 py-8 text-center">
                                        <h3 class="text-lg font-semibold text-gray-900">No hay artículos recientes</h3>
                                        <p class="mt-3 text-sm text-gray-600">
                                            Las publicaciones recientes aparecerán aquí automáticamente.
                                        </p>
                                    </div>
                                {% endfor %}
                            </div>
                        </div>
                    </aside>
                </section>
            {% else %}
                <section class="mt-12">
                    <div class="rounded-3xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
                        <h2 class="text-2xl font-semibold text-gray-900">Todavía no hay artículos publicados</h2>
                        <p class="mt-4 text-sm text-gray-600">
                            Cuando existan publicaciones, esta portada destacará una entrada principal y varias recientes.
                        </p>
                    </div>
                </section>
            {% endif %}
        {% endwith %}
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · EDITORIAL
# ---------------------------------------------------------------------------

BLOG_HOME_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-stone-200 pb-10">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Revista
            </p>
            <h1 class="mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                Una portada editorial sobria para presentar ideas, análisis y relatos con contexto.
            </h1>
            <p class="mt-6 max-w-3xl text-lg leading-8 text-stone-600">
                Diseñada para proyectos donde la tipografía, la firma y la fecha importan tanto como el contenido.
            </p>
            <div class="mt-8">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-full bg-stone-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-stone-800">
                    Ir al archivo completo
                </a>
            </div>
        </header>

        {% with items.0 as featured %}
            {% if featured %}
                <section class="mt-12 grid gap-10 lg:grid-cols-12">
                    <div class="lg:col-span-8">
                        <article class="border-b border-stone-200 pb-10">
                            <div class="flex flex-wrap items-center gap-4 text-sm text-stone-500">
                                {% if featured.CAMPO_FECHA %}
                                    <span>{{ featured.CAMPO_FECHA }} {# campo fecha #}</span>
                                {% endif %}
                                {% if featured.CAMPO_AUTOR %}
                                    <span>{{ featured.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                                {% endif %}
                                {% if featured.CAMPO_CATEGORIA %}
                                    <span>{{ featured.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                                {% endif %}
                            </div>

                            <h2 class="mt-4 text-4xl font-semibold leading-tight tracking-tight text-stone-900">
                                <a href="{% url 'NOMBRE_URL_DETALLE' featured.pk %}" class="transition hover:text-stone-700">
                                    {{ featured.CAMPO_TITULO }} {# campo título principal #}
                                </a>
                            </h2>

                            {% if featured.CAMPO_IMAGEN %}
                                <div class="mt-8 overflow-hidden rounded-3xl border border-stone-200 bg-white">
                                    <img src="{{ featured.CAMPO_IMAGEN }}" alt="{{ featured.CAMPO_TITULO }}" class="h-full w-full object-cover">
                                </div>
                            {% endif %}

                            {% if featured.CAMPO_DESCRIPCION %}
                                <p class="mt-8 max-w-3xl text-lg leading-8 text-stone-700">
                                    {{ featured.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                </p>
                            {% endif %}

                            {% if featured.CAMPO_EXTRA %}
                                <p class="mt-4 text-sm text-stone-500">
                                    {{ featured.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                                </p>
                            {% endif %}
                        </article>
                    </div>

                    <aside class="lg:col-span-4">
                        <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                            Recientes
                        </p>
                        <div class="mt-6 divide-y divide-stone-200 border-y border-stone-200">
							{% for item in featured %}
                                <article class="py-6">
                                    <div class="flex flex-wrap items-center gap-3 text-sm text-stone-500">
                                        {% if item.CAMPO_FECHA %}
                                            <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                        {% endif %}
                                        {% if item.CAMPO_AUTOR %}
                                            <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                                        {% endif %}
                                    </div>

                                    <h3 class="mt-3 text-xl font-semibold leading-tight tracking-tight text-stone-900">
                                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-stone-700">
                                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                                        </a>
                                    </h3>

                                    {% if item.CAMPO_CATEGORIA %}
                                        <p class="mt-2 text-sm text-stone-500">
                                            {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                        </p>
                                    {% endif %}
                                </article>
                            {% empty %}
                                <div class="py-10 text-center">
                                    <h3 class="text-lg font-semibold text-stone-900">No hay artículos recientes</h3>
                                    <p class="mt-3 text-sm text-stone-600">
                                        La portada editorial mostrará aquí las entradas más recientes.
                                    </p>
                                </div>
                            {% endfor %}
                        </div>
                    </aside>
                </section>
            {% else %}
                <section class="mt-12">
                    <div class="border border-dashed border-stone-300 px-6 py-12 text-center">
                        <h2 class="text-2xl font-semibold text-stone-900">Todavía no hay artículos publicados</h2>
                        <p class="mt-4 text-sm text-stone-600">
                            Esta portada mostrará un artículo principal y varias piezas recientes cuando existan registros.
                        </p>
                    </div>
                </section>
            {% endif %}
        {% endwith %}
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · DARK
# ---------------------------------------------------------------------------

BLOG_LIST_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-800 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-400">
                Archivo
            </p>
            <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                Todas las publicaciones
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-gray-300">
                Recorre el archivo completo del blog en una lista vertical pensada para lectura y contexto.
            </p>
        </header>

        <div class="mt-8 divide-y divide-gray-800">
			{% for item in page_obj %}
                <article class="py-8">
                    <div class="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                        {% if item.CAMPO_FECHA %}
                            <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                        {% endif %}
                        {% if item.CAMPO_AUTOR %}
                            <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                        {% endif %}
                        {% if item.CAMPO_CATEGORIA %}
                            <span class="text-indigo-400">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                        {% endif %}
                    </div>

                    <h2 class="mt-4 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-indigo-300">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </a>
                    </h2>

                    {% if item.CAMPO_DESCRIPCION %}
                        <p class="mt-4 text-base leading-8 text-gray-300">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    {% endif %}

                    {% if item.CAMPO_EXTRA %}
                        <p class="mt-4 text-sm text-gray-400">
                            {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                        </p>
                    {% endif %}

                    <div class="mt-5">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                           class="inline-flex items-center text-sm font-semibold text-indigo-400 transition hover:text-indigo-300">
                            Leer más
                        </a>
                    </div>
                </article>
            {% empty %}
                <div class="py-12 text-center">
                    <h2 class="text-lg font-semibold text-white">No hay publicaciones disponibles</h2>
                    <p class="mt-3 text-sm text-gray-400">
                        El archivo mostrará aquí las entradas del blog cuando existan artículos publicados.
                    </p>
                </div>
            {% endfor %}
        </div>

        {% if page_obj %}
            <nav class="mt-10 flex flex-wrap items-center justify-center gap-3" aria-label="Paginación">
                {% if page_obj.has_previous %}
                    <a href="?page={{ page_obj.previous_page_number }}"
                       class="inline-flex items-center rounded-xl border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800">
                        Anterior
                    </a>
                {% endif %}

                <span class="inline-flex items-center rounded-xl border border-gray-800 px-4 py-2 text-sm text-gray-300">
                    Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
                </span>

                {% if page_obj.has_next %}
                    <a href="?page={{ page_obj.next_page_number }}"
                       class="inline-flex items-center rounded-xl border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800">
                        Siguiente
                    </a>
                {% endif %}
            </nav>
        {% endif %}
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · LIGHT
# ---------------------------------------------------------------------------

BLOG_LIST_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-white text-gray-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                Archivo
            </p>
            <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                Todas las publicaciones
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-gray-600">
                Un listado claro y ordenado para recorrer artículos, fechas, firmas y categorías sin distracciones.
            </p>
        </header>

        <div class="mt-8 space-y-6">
			{% for item in page_obj %}
                <article class="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-gray-200">
                    <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                        {% if item.CAMPO_FECHA %}
                            <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                        {% endif %}
                        {% if item.CAMPO_AUTOR %}
                            <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                        {% endif %}
                        {% if item.CAMPO_CATEGORIA %}
                            <span>{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                        {% endif %}
                    </div>

                    <h2 class="mt-4 text-2xl font-semibold tracking-tight text-gray-900 sm:text-3xl">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-gray-700">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </a>
                    </h2>

                    {% if item.CAMPO_DESCRIPCION %}
                        <p class="mt-4 text-base leading-8 text-gray-600">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    {% endif %}

                    {% if item.CAMPO_EXTRA %}
                        <p class="mt-4 text-sm text-gray-500">
                            {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                        </p>
                    {% endif %}

                    <div class="mt-5">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                           class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                            Leer más
                        </a>
                    </div>
                </article>
            {% empty %}
                <div class="rounded-3xl border border-dashed border-gray-300 bg-gray-50 px-6 py-12 text-center">
                    <h2 class="text-lg font-semibold text-gray-900">No hay publicaciones disponibles</h2>
                    <p class="mt-3 text-sm text-gray-600">
                        Esta página mostrará el listado completo del blog cuando existan artículos.
                    </p>
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
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · EDITORIAL
# ---------------------------------------------------------------------------

BLOG_LIST_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-stone-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Archivo editorial
            </p>
            <h1 class="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Todas las publicaciones
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-stone-600">
                Un listado vertical denso y sobrio, pensado para navegar por fecha, autoría y categoría con comodidad.
            </p>
        </header>

        <div class="mt-8 divide-y divide-stone-200">
			{% for item in page_obj %}
                <article class="py-8">
                    <div class="flex flex-wrap items-center gap-4 text-sm text-stone-500">
                        {% if item.CAMPO_FECHA %}
                            <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                        {% endif %}
                        {% if item.CAMPO_AUTOR %}
                            <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                        {% endif %}
                        {% if item.CAMPO_CATEGORIA %}
                            <span>{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                        {% endif %}
                    </div>

                    <h2 class="mt-4 text-2xl font-semibold leading-tight tracking-tight text-stone-900 sm:text-3xl">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-stone-700">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </a>
                    </h2>

                    {% if item.CAMPO_DESCRIPCION %}
                        <p class="mt-4 max-w-3xl text-base leading-8 text-stone-700">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    {% endif %}

                    {% if item.CAMPO_EXTRA %}
                        <p class="mt-4 text-sm text-stone-500">
                            {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                        </p>
                    {% endif %}

                    <div class="mt-5">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}"
                           class="text-sm font-semibold text-stone-900 transition hover:text-stone-700">
                            Leer artículo
                        </a>
                    </div>
                </article>
            {% empty %}
                <div class="py-12 text-center">
                    <h2 class="text-lg font-semibold text-stone-900">No hay publicaciones disponibles</h2>
                    <p class="mt-3 text-sm text-stone-600">
                        El archivo editorial aparecerá aquí cuando el blog tenga artículos publicados.
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

BLOG_DETAIL_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-3xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-indigo-400 transition hover:text-indigo-300">
                ← Volver al listado
            </a>
        </div>

        <article>
            <header class="border-b border-gray-800 pb-8">
                <div class="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                    {% if item.CAMPO_FECHA %}
                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                    {% endif %}
                    {% if item.CAMPO_AUTOR %}
                        <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                    {% endif %}
                    {% if item.CAMPO_CATEGORIA %}
                        <span class="text-indigo-400">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                    {% endif %}
                </div>

                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                {% if item.CAMPO_EXTRA %}
                    <p class="mt-4 text-sm text-gray-400">
                        {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                    </p>
                {% endif %}
            </header>

            {% if item.CAMPO_IMAGEN %}
                <div class="mt-10 overflow-hidden rounded-3xl border border-gray-800 bg-gray-900">
                    <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                </div>
            {% endif %}

            {% if item.CAMPO_DESCRIPCION %}
                <section class="mt-10">
                    <div class="prose prose-invert max-w-none">
                        <div class="text-base leading-8 text-gray-300">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </div>
                    </div>
                </section>
            {% endif %}
        </article>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · LIGHT
# ---------------------------------------------------------------------------

BLOG_DETAIL_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-white text-gray-900">
    <div class="mx-auto max-w-3xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                ← Volver al listado
            </a>
        </div>

        <article>
            <header class="border-b border-gray-200 pb-8">
                <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                    {% if item.CAMPO_FECHA %}
                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                    {% endif %}
                    {% if item.CAMPO_AUTOR %}
                        <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                    {% endif %}
                    {% if item.CAMPO_CATEGORIA %}
                        <span>{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                    {% endif %}
                </div>

                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                {% if item.CAMPO_EXTRA %}
                    <p class="mt-4 text-sm text-gray-500">
                        {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                    </p>
                {% endif %}
            </header>

            {% if item.CAMPO_IMAGEN %}
                <div class="mt-10 overflow-hidden rounded-3xl bg-gray-50 shadow-sm ring-1 ring-gray-200">
                    <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                </div>
            {% endif %}

            {% if item.CAMPO_DESCRIPCION %}
                <section class="mt-10">
                    <div class="text-base leading-8 text-gray-700">
                        {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                    </div>
                </section>
            {% endif %}
        </article>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · EDITORIAL
# ---------------------------------------------------------------------------

BLOG_DETAIL_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-3xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-10">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-stone-900 transition hover:text-stone-700">
                ← Volver al archivo
            </a>
        </div>

        <article>
            <header class="border-b border-stone-200 pb-8">
                <div class="flex flex-wrap items-center gap-4 text-sm text-stone-500">
                    {% if item.CAMPO_FECHA %}
                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                    {% endif %}
                    {% if item.CAMPO_AUTOR %}
                        <span>{{ item.CAMPO_AUTOR }} {# campo autor o firma #}</span>
                    {% endif %}
                    {% if item.CAMPO_CATEGORIA %}
                        <span>{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</span>
                    {% endif %}
                </div>

                <h1 class="mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                {% if item.CAMPO_EXTRA %}
                    <p class="mt-4 text-sm text-stone-500">
                        {{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}
                    </p>
                {% endif %}
            </header>

            {% if item.CAMPO_IMAGEN %}
                <div class="mt-10 overflow-hidden rounded-3xl border border-stone-200 bg-white">
                    <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                </div>
            {% endif %}

            {% if item.CAMPO_DESCRIPCION %}
                <section class="mt-10">
                    <div class="text-base leading-8 text-stone-700">
                        {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                    </div>
                </section>
            {% endif %}
        </article>
    </div>
</section>
{% endblock %}"""

__all__ = [
    "BLOG_HOME_DARK",
    "BLOG_HOME_LIGHT",
    "BLOG_HOME_EDITORIAL",
    "BLOG_LIST_DARK",
    "BLOG_LIST_LIGHT",
    "BLOG_LIST_EDITORIAL",
    "BLOG_DETAIL_DARK",
    "BLOG_DETAIL_LIGHT",
    "BLOG_DETAIL_EDITORIAL",
]