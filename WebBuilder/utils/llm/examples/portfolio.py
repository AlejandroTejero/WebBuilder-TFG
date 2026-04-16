# -*- coding: utf-8 -*-
"""
Reusable Django + Tailwind portfolio templates for automatic site generation.

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

PORTFOLIO_HOME_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="grid gap-8 border-b border-gray-800 pb-12 lg:grid-cols-12 lg:items-end">
            <div class="lg:col-span-8">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-violet-400">
                    Portfolio
                </p>
                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                    Proyectos visuales con presencia fuerte, narrativa clara y detalle profesional.
                </h1>
                <p class="mt-6 max-w-3xl text-lg leading-8 text-gray-300">
                    Una portada pensada para mostrar trabajos destacados con impacto visual y una navegación clara
                    hacia la colección completa.
                </p>
                <div class="mt-8 flex flex-wrap gap-4">
                    <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                       class="inline-flex items-center justify-center rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-400">
                        Ver proyectos
                    </a>
                    <a href="{% url 'NOMBRE_URL_HOME' %}"
                       class="inline-flex items-center justify-center rounded-xl border border-gray-800 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-900">
                        Inicio
                    </a>
                </div>
            </div>
            <div class="lg:col-span-4">
                <div class="rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <p class="text-sm font-medium text-gray-400">Enfoque</p>
                    <p class="mt-3 text-lg font-semibold text-white">
                        Diseño oscuro, imágenes protagonistas y tarjetas con jerarquía visual.
                    </p>
                </div>
            </div>
        </header>

        <section class="mt-12">
            <div class="mb-8 flex items-end justify-between gap-4">
                <div>
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-violet-400">
                        Selección
                    </p>
                    <h2 class="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                        Proyectos destacados
                    </h2>
                </div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="hidden text-sm font-semibold text-violet-400 transition hover:text-violet-300 sm:inline">
                    Explorar todo
                </a>
            </div>

            <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
				{% for item in featured %}
                    <article class="group overflow-hidden rounded-3xl border border-gray-800 bg-gray-900">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="block">
                            <div class="relative aspect-[4/3] overflow-hidden bg-gray-800">
                                {% if item.CAMPO_IMAGEN %}
                                    <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover transition duration-500 group-hover:scale-105">
                                {% endif %}
                                <div class="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/50 to-transparent"></div>
                                <div class="absolute inset-x-0 bottom-0 p-6">
                                    {% if item.CAMPO_CATEGORIA %}
                                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-violet-300">
                                            {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                        </p>
                                    {% endif %}
                                    <h3 class="mt-3 text-xl font-semibold tracking-tight text-white">
                                        {{ item.CAMPO_TITULO }} {# campo título principal #}
                                    </h3>
                                    <div class="mt-3 flex flex-wrap items-center gap-3 text-sm text-gray-300">
                                        {% if item.CAMPO_CLIENTE %}
                                            <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                                        {% endif %}
                                        {% if item.CAMPO_FECHA %}
                                            <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </a>
                    </article>
                {% empty %}
                    <div class="md:col-span-2 xl:col-span-3">
                        <div class="rounded-3xl border border-dashed border-gray-800 bg-gray-900 px-6 py-12 text-center">
                            <h3 class="text-lg font-semibold text-white">No hay proyectos destacados</h3>
                            <p class="mt-3 text-sm text-gray-400">
                                Cuando existan proyectos disponibles, esta portada mostrará una selección visual automática.
                            </p>
                        </div>
                    </div>
                {% endfor %}
            </div>
        </section>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · LIGHT
# ---------------------------------------------------------------------------

PORTFOLIO_HOME_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="grid gap-8 border-b border-gray-200 pb-12 lg:grid-cols-12 lg:items-end">
            <div class="lg:col-span-8">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                    Portfolio
                </p>
                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                    Proyectos presentados con claridad, elegancia y una estructura visual cuidada.
                </h1>
                <p class="mt-6 max-w-3xl text-lg leading-8 text-gray-600">
                    Una portada limpia y espaciosa para mostrar trabajos recientes y guiar la navegación hacia el
                    listado completo del portfolio.
                </p>
                <div class="mt-8 flex flex-wrap gap-4">
                    <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                       class="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800">
                        Ver proyectos
                    </a>
                    <a href="{% url 'NOMBRE_URL_HOME' %}"
                       class="inline-flex items-center justify-center rounded-xl border border-gray-300 bg-white px-5 py-3 text-sm font-semibold text-gray-900 transition hover:bg-gray-100">
                        Inicio
                    </a>
                </div>
            </div>
            <div class="lg:col-span-4">
                <div class="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <p class="text-sm font-medium text-gray-500">Enfoque</p>
                    <p class="mt-3 text-lg font-semibold text-gray-900">
                        Diseño luminoso, grid equilibrado y tarjetas con sombra suave.
                    </p>
                </div>
            </div>
        </header>

        <section class="mt-12">
            <div class="mb-8 flex items-end justify-between gap-4">
                <div>
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                        Selección
                    </p>
                    <h2 class="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                        Proyectos destacados
                    </h2>
                </div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="hidden text-sm font-semibold text-gray-900 transition hover:text-gray-700 sm:inline">
                    Explorar todo
                </a>
            </div>

            <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
				{% for item in featured %}
                    <article class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="block">
                            <div class="aspect-[4/3] overflow-hidden bg-gray-100">
                                {% if item.CAMPO_IMAGEN %}
                                    <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover transition duration-500 hover:scale-105">
                                {% endif %}
                            </div>
                            <div class="p-6">
                                {% if item.CAMPO_CATEGORIA %}
                                    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                    </p>
                                {% endif %}
                                <h3 class="mt-3 text-xl font-semibold tracking-tight text-gray-900">
                                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                                </h3>
                                <div class="mt-3 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                                    {% if item.CAMPO_CLIENTE %}
                                        <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                                    {% endif %}
                                    {% if item.CAMPO_FECHA %}
                                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                    {% endif %}
                                </div>
                            </div>
                        </a>
                    </article>
                {% empty %}
                    <div class="md:col-span-2 xl:col-span-3">
                        <div class="rounded-3xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
                            <h3 class="text-lg font-semibold text-gray-900">No hay proyectos destacados</h3>
                            <p class="mt-3 text-sm text-gray-600">
                                Esta portada mostrará automáticamente una selección de proyectos cuando existan registros.
                            </p>
                        </div>
                    </div>
                {% endfor %}
            </div>
        </section>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · EDITORIAL
# ---------------------------------------------------------------------------

PORTFOLIO_HOME_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-stone-200 pb-12">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Portfolio editorial
            </p>
            <h1 class="mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                Una colección de proyectos presentada con foco en el nombre, el contexto y los metadatos.
            </h1>
            <p class="mt-6 max-w-3xl text-lg leading-8 text-stone-600">
                Ideal para portfolios donde la narrativa del trabajo y su posicionamiento importan tanto como la parte visual.
            </p>
            <div class="mt-8 flex flex-wrap gap-4">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-full bg-stone-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-stone-800">
                    Ver proyectos
                </a>
                <a href="{% url 'NOMBRE_URL_HOME' %}"
                   class="inline-flex items-center justify-center rounded-full border border-stone-300 px-5 py-3 text-sm font-semibold text-stone-900 transition hover:bg-stone-100">
                    Inicio
                </a>
            </div>
        </header>

        <section class="mt-12">
            <div class="mb-8">
                <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                    Selección
                </p>
                <h2 class="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                    Proyectos recientes
                </h2>
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
                                <div class="mt-3 flex flex-wrap items-center gap-4 text-sm text-stone-500">
                                    {% if item.CAMPO_CLIENTE %}
                                        <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                                    {% endif %}
                                    {% if item.CAMPO_EXTRA %}
                                        <span>{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</span>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </article>
                {% empty %}
                    <div class="py-12 text-center">
                        <h3 class="text-lg font-semibold text-stone-900">No hay proyectos destacados</h3>
                        <p class="mt-3 text-sm text-stone-600">
                            Esta portada mostrará una selección editorial de proyectos cuando existan elementos.
                        </p>
                    </div>
                {% endfor %}
            </div>
        </section>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · DARK
# ---------------------------------------------------------------------------

PORTFOLIO_LIST_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-800 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-violet-400">
                Archivo completo
            </p>
            <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                Todos los proyectos
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-gray-300">
                Un grid visual con imagen protagonista, identidad clara y una navegación directa hacia cada ficha.
            </p>
        </header>

        <div class="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
			{% for item in page_obj %}
                <article class="group overflow-hidden rounded-3xl border border-gray-800 bg-gray-900">
                    <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="block">
                        <div class="relative aspect-[4/3] overflow-hidden bg-gray-800">
                            {% if item.CAMPO_IMAGEN %}
                                <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover transition duration-500 group-hover:scale-105">
                            {% endif %}
                            <div class="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/50 to-transparent"></div>
                            <div class="absolute inset-x-0 bottom-0 p-6">
                                {% if item.CAMPO_CATEGORIA %}
                                    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-violet-300">
                                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                    </p>
                                {% endif %}
                                <h2 class="mt-3 text-xl font-semibold tracking-tight text-white">
                                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                                </h2>
                                <div class="mt-3 flex flex-wrap items-center gap-3 text-sm text-gray-300">
                                    {% if item.CAMPO_CLIENTE %}
                                        <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                                    {% endif %}
                                    {% if item.CAMPO_FECHA %}
                                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </a>
                </article>
            {% empty %}
                <div class="md:col-span-2 xl:col-span-3">
                    <div class="rounded-3xl border border-dashed border-gray-800 bg-gray-900 px-6 py-12 text-center">
                        <h2 class="text-lg font-semibold text-white">No hay proyectos disponibles</h2>
                        <p class="mt-3 text-sm text-gray-400">
                            El listado mostrará aquí la colección completa del portfolio cuando existan proyectos.
                        </p>
                    </div>
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

PORTFOLIO_LIST_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-white text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                Archivo completo
            </p>
            <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                Todos los proyectos
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-gray-600">
                Una galería limpia y equilibrada para presentar proyectos con imagen, categoría y detalle.
            </p>
        </header>

        <div class="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
			{% for item in page_obj %}
                <article class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
                    <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="block">
                        <div class="aspect-[4/3] overflow-hidden bg-gray-100">
                            {% if item.CAMPO_IMAGEN %}
                                <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover transition duration-500 hover:scale-105">
                            {% endif %}
                        </div>
                        <div class="p-6">
                            {% if item.CAMPO_CATEGORIA %}
                                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                    {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                </p>
                            {% endif %}
                            <h2 class="mt-3 text-xl font-semibold tracking-tight text-gray-900">
                                {{ item.CAMPO_TITULO }} {# campo título principal #}
                            </h2>
                            <div class="mt-3 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                                {% if item.CAMPO_CLIENTE %}
                                    <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                                {% endif %}
                                {% if item.CAMPO_FECHA %}
                                    <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
                                {% endif %}
                            </div>
                        </div>
                    </a>
                </article>
            {% empty %}
                <div class="md:col-span-2 xl:col-span-3">
                    <div class="rounded-3xl border border-dashed border-gray-300 bg-gray-50 px-6 py-12 text-center">
                        <h2 class="text-lg font-semibold text-gray-900">No hay proyectos disponibles</h2>
                        <p class="mt-3 text-sm text-gray-600">
                            Aquí aparecerá el listado completo del portfolio cuando existan trabajos publicados.
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
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · EDITORIAL
# ---------------------------------------------------------------------------

PORTFOLIO_LIST_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-stone-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Archivo editorial
            </p>
            <h1 class="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Todos los proyectos
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-stone-600">
                Un listado sobrio y vertical, sin imágenes, centrado en el nombre del proyecto y sus metadatos.
            </p>
        </header>

        <div class="mt-8 divide-y divide-stone-200">
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
                            <h2 class="text-2xl font-semibold leading-tight tracking-tight text-stone-900 sm:text-3xl">
                                <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="transition hover:text-stone-700">
                                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                                </a>
                            </h2>
                            <div class="mt-3 flex flex-wrap items-center gap-4 text-sm text-stone-500">
                                {% if item.CAMPO_CLIENTE %}
                                    <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                                {% endif %}
                                {% if item.CAMPO_EXTRA %}
                                    <span>{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</span>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </article>
            {% empty %}
                <div class="py-12 text-center">
                    <h2 class="text-lg font-semibold text-stone-900">No hay proyectos disponibles</h2>
                    <p class="mt-3 text-sm text-stone-600">
                        El archivo editorial aparecerá aquí cuando el portfolio tenga proyectos publicados.
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

PORTFOLIO_DETAIL_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-violet-400 transition hover:text-violet-300">
                ← Volver al listado
            </a>
        </div>

        <article class="grid gap-10 lg:grid-cols-12">
            <div class="lg:col-span-7">
                {% if item.CAMPO_IMAGEN %}
                    <div class="overflow-hidden rounded-3xl border border-gray-800 bg-gray-900">
                        <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                    </div>
                {% endif %}
            </div>

            <div class="lg:col-span-5">
                {% if item.CAMPO_CATEGORIA %}
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-violet-400">
                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                    </p>
                {% endif %}

                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                {% if item.CAMPO_DESCRIPCION %}
                    <div class="mt-8">
                        <h2 class="text-lg font-semibold text-white">Descripción</h2>
                        <p class="mt-4 text-base leading-8 text-gray-300">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    </div>
                {% endif %}

                <div class="mt-8 rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <h2 class="text-lg font-semibold text-white">Metadatos</h2>
                    <dl class="mt-6 space-y-5">
                        {% if item.CAMPO_CLIENTE %}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">Cliente</dt>
                                <dd class="mt-1 text-sm text-white">{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_FECHA %}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">Fecha</dt>
                                <dd class="mt-1 text-sm text-white">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_CATEGORIA %}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">Categoría</dt>
                                <dd class="mt-1 text-sm text-white">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_EXTRA %}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">Información adicional</dt>
                                <dd class="mt-1 text-sm text-white">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
                            </div>
                        {% endif %}
                    </dl>

                    {% if item.CAMPO_URL %}
                        <div class="mt-6">
                            <a href="{{ item.CAMPO_URL }}" target="_blank" rel="noopener noreferrer"
                               class="inline-flex items-center justify-center rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-400">
                                Ver proyecto externo
                            </a>
                        </div>
                    {% endif %}
                </div>
            </div>
        </article>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · LIGHT
# ---------------------------------------------------------------------------

PORTFOLIO_DETAIL_LIGHT = """{% extends 'base.html' %}
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
            <div class="lg:col-span-7">
                {% if item.CAMPO_IMAGEN %}
                    <div class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
                        <img src="{{ item.CAMPO_IMAGEN }}" alt="{{ item.CAMPO_TITULO }}" class="h-full w-full object-cover">
                    </div>
                {% endif %}
            </div>

            <div class="lg:col-span-5">
                {% if item.CAMPO_CATEGORIA %}
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                    </p>
                {% endif %}

                <h1 class="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                </h1>

                {% if item.CAMPO_DESCRIPCION %}
                    <div class="mt-8">
                        <h2 class="text-lg font-semibold text-gray-900">Descripción</h2>
                        <p class="mt-4 text-base leading-8 text-gray-600">
                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                        </p>
                    </div>
                {% endif %}

                <div class="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900">Metadatos</h2>
                    <dl class="mt-6 space-y-5">
                        {% if item.CAMPO_CLIENTE %}
                            <div>
                                <dt class="text-sm font-medium text-gray-500">Cliente</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_FECHA %}
                            <div>
                                <dt class="text-sm font-medium text-gray-500">Fecha</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_CATEGORIA %}
                            <div>
                                <dt class="text-sm font-medium text-gray-500">Categoría</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                            </div>
                        {% endif %}
                        {% if item.CAMPO_EXTRA %}
                            <div>
                                <dt class="text-sm font-medium text-gray-500">Información adicional</dt>
                                <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
                            </div>
                        {% endif %}
                    </dl>

                    {% if item.CAMPO_URL %}
                        <div class="mt-6">
                            <a href="{{ item.CAMPO_URL }}" target="_blank" rel="noopener noreferrer"
                               class="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800">
                                Ver proyecto externo
                            </a>
                        </div>
                    {% endif %}
                </div>
            </div>
        </article>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# DETAIL · EDITORIAL
# ---------------------------------------------------------------------------

PORTFOLIO_DETAIL_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
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
                    {% if item.CAMPO_CLIENTE %}
                        <span>{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</span>
                    {% endif %}
                    {% if item.CAMPO_FECHA %}
                        <span>{{ item.CAMPO_FECHA }} {# campo fecha #}</span>
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
                            <h2 class="text-xl font-semibold text-stone-900">Descripción completa</h2>
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
                            {% if item.CAMPO_CLIENTE %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Cliente</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_CLIENTE }} {# campo cliente o destinatario #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Fecha</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_CATEGORIA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Categoría</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Información adicional</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
                                </div>
                            {% endif %}
                        </dl>

                        {% if item.CAMPO_URL %}
                            <div class="mt-6">
                                <a href="{{ item.CAMPO_URL }}" target="_blank" rel="noopener noreferrer"
                                   class="inline-flex items-center justify-center rounded-full bg-stone-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-stone-800">
                                    Ver proyecto externo
                                </a>
                            </div>
                        {% endif %}
                    </div>
                </aside>
            </div>
        </article>
    </div>
</section>
{% endblock %}"""

__all__ = [
    "PORTFOLIO_HOME_DARK",
    "PORTFOLIO_HOME_LIGHT",
    "PORTFOLIO_HOME_EDITORIAL",
    "PORTFOLIO_LIST_DARK",
    "PORTFOLIO_LIST_LIGHT",
    "PORTFOLIO_LIST_EDITORIAL",
    "PORTFOLIO_DETAIL_DARK",
    "PORTFOLIO_DETAIL_LIGHT",
    "PORTFOLIO_DETAIL_EDITORIAL",
]