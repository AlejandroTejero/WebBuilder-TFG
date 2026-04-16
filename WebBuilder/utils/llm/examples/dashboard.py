# -*- coding: utf-8 -*-
"""
Reusable Django + Tailwind dashboard templates for automatic site generation.

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

DASHBOARD_HOME_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="flex flex-col gap-6 border-b border-gray-800 pb-10 lg:flex-row lg:items-end lg:justify-between">
            <div class="max-w-3xl">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                    Resumen general
                </p>
                <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                    Panel principal
                </h1>
                <p class="mt-4 text-base leading-8 text-gray-300">
                    Una portada de dashboard con métricas destacadas, contexto rápido y una tabla reciente para
                    inspeccionar registros sin perder densidad informativa.
                </p>
            </div>
            <div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-400">
                    Ver listado completo
                </a>
            </div>
        </header>

        {% with items.0 as first_item %}
            <div class="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
                <article class="rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <p class="text-sm font-medium text-gray-400">Registros visibles</p>
                    <p class="mt-4 text-3xl font-bold tracking-tight text-white">
                        {{ items|length }}
                    </p>
                </article>

                <article class="rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <p class="text-sm font-medium text-gray-400">Estado reciente</p>
                    {% if first_item and first_item.CAMPO_ESTADO %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-white">
                            {{ first_item.CAMPO_ESTADO }} {# campo estado o badge #}
                        </p>
                    {% else %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-white">Sin estado</p>
                    {% endif %}
                </article>

                <article class="rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <p class="text-sm font-medium text-gray-400">Valor reciente</p>
                    {% if first_item and first_item.CAMPO_VALOR %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-white">
                            {{ first_item.CAMPO_VALOR }} {# campo numérico o métrica #}
                        </p>
                    {% else %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-white">Sin valor</p>
                    {% endif %}
                </article>

                <article class="rounded-3xl border border-gray-800 bg-gray-900 p-6">
                    <p class="text-sm font-medium text-gray-400">Categoría reciente</p>
                    {% if first_item and first_item.CAMPO_CATEGORIA %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-white">
                            {{ first_item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                        </p>
                    {% else %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-white">Sin categoría</p>
                    {% endif %}
                </article>
            </div>
        {% endwith %}

        <section class="mt-12">
            <div class="mb-6 flex items-end justify-between gap-4">
                <div>
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                        Actividad reciente
                    </p>
                    <h2 class="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
                        Últimos registros
                    </h2>
                </div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="hidden text-sm font-semibold text-blue-400 transition hover:text-blue-300 sm:inline">
                    Ir al listado
                </a>
            </div>

            <div class="overflow-hidden rounded-3xl border border-gray-800 bg-gray-900">
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-800">
                        <thead class="bg-gray-950/50">
                            <tr>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                    Título
                                </th>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                    Categoría
                                </th>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                    Estado
                                </th>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                    Valor
                                </th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-800">
                            {% for item in items|slice:":10" %}
                                <tr class="transition hover:bg-gray-800/50">
                                    <td class="px-6 py-4 align-top">
                                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="font-semibold text-white transition hover:text-blue-300">
                                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                                        </a>
                                        {% if item.CAMPO_FECHA %}
                                            <p class="mt-1 text-sm text-gray-400">
                                                {{ item.CAMPO_FECHA }} {# campo fecha #}
                                            </p>
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 align-top text-sm text-gray-300">
                                        {% if item.CAMPO_CATEGORIA %}
                                            {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                        {% else %}
                                            —
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 align-top text-sm">
                                        {% if item.CAMPO_ESTADO %}
                                            <span class="inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 font-medium text-blue-300">
                                                {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                                            </span>
                                        {% else %}
                                            <span class="text-gray-500">—</span>
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 align-top text-sm text-gray-300">
                                        {% if item.CAMPO_VALOR %}
                                            {{ item.CAMPO_VALOR }} {# campo numérico o métrica #}
                                        {% else %}
                                            —
                                        {% endif %}
                                    </td>
                                </tr>
                            {% empty %}
                                <tr>
                                    <td colspan="4" class="px-6 py-12 text-center">
                                        <h3 class="text-lg font-semibold text-white">No hay registros recientes</h3>
                                        <p class="mt-3 text-sm text-gray-400">
                                            Cuando existan elementos, esta tabla mostrará automáticamente los diez más recientes.
                                        </p>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · LIGHT
# ---------------------------------------------------------------------------

DASHBOARD_HOME_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="flex flex-col gap-6 border-b border-gray-200 pb-10 lg:flex-row lg:items-end lg:justify-between">
            <div class="max-w-3xl">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                    Resumen general
                </p>
                <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                    Panel principal
                </h1>
                <p class="mt-4 text-base leading-8 text-gray-600">
                    Una vista de inicio clara y estructurada para resumir métricas, destacar registros recientes y
                    facilitar el acceso al listado completo.
                </p>
            </div>
            <div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800">
                    Ver listado completo
                </a>
            </div>
        </header>

        {% with items.0 as first_item %}
            <div class="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
                <article class="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <p class="text-sm font-medium text-gray-500">Registros visibles</p>
                    <p class="mt-4 text-3xl font-bold tracking-tight text-gray-900">
                        {{ items|length }}
                    </p>
                </article>

                <article class="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <p class="text-sm font-medium text-gray-500">Estado reciente</p>
                    {% if first_item and first_item.CAMPO_ESTADO %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-gray-900">
                            {{ first_item.CAMPO_ESTADO }} {# campo estado o badge #}
                        </p>
                    {% else %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-gray-900">Sin estado</p>
                    {% endif %}
                </article>

                <article class="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <p class="text-sm font-medium text-gray-500">Valor reciente</p>
                    {% if first_item and first_item.CAMPO_VALOR %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-gray-900">
                            {{ first_item.CAMPO_VALOR }} {# campo numérico o métrica #}
                        </p>
                    {% else %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-gray-900">Sin valor</p>
                    {% endif %}
                </article>

                <article class="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                    <p class="text-sm font-medium text-gray-500">Categoría reciente</p>
                    {% if first_item and first_item.CAMPO_CATEGORIA %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-gray-900">
                            {{ first_item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                        </p>
                    {% else %}
                        <p class="mt-4 text-2xl font-semibold tracking-tight text-gray-900">Sin categoría</p>
                    {% endif %}
                </article>
            </div>
        {% endwith %}

        <section class="mt-12">
            <div class="mb-6 flex items-end justify-between gap-4">
                <div>
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                        Actividad reciente
                    </p>
                    <h2 class="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                        Últimos registros
                    </h2>
                </div>
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="hidden text-sm font-semibold text-gray-900 transition hover:text-gray-700 sm:inline">
                    Ir al listado
                </a>
            </div>

            <div class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                    Título
                                </th>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                    Categoría
                                </th>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                    Estado
                                </th>
                                <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                    Valor
                                </th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            {% for item in items|slice:":10" %}
                                <tr class="transition hover:bg-gray-50">
                                    <td class="px-6 py-4 align-top">
                                        <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="font-semibold text-gray-900 transition hover:text-gray-700">
                                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                                        </a>
                                        {% if item.CAMPO_FECHA %}
                                            <p class="mt-1 text-sm text-gray-500">
                                                {{ item.CAMPO_FECHA }} {# campo fecha #}
                                            </p>
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 align-top text-sm text-gray-600">
                                        {% if item.CAMPO_CATEGORIA %}
                                            {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                        {% else %}
                                            —
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 align-top text-sm">
                                        {% if item.CAMPO_ESTADO %}
                                            <span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 font-medium text-gray-700">
                                                {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                                            </span>
                                        {% else %}
                                            <span class="text-gray-400">—</span>
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 align-top text-sm text-gray-600">
                                        {% if item.CAMPO_VALOR %}
                                            {{ item.CAMPO_VALOR }} {# campo numérico o métrica #}
                                        {% else %}
                                            —
                                        {% endif %}
                                    </td>
                                </tr>
                            {% empty %}
                                <tr>
                                    <td colspan="4" class="px-6 py-12 text-center">
                                        <h3 class="text-lg font-semibold text-gray-900">No hay registros recientes</h3>
                                        <p class="mt-3 text-sm text-gray-600">
                                            Cuando existan elementos, esta tabla mostrará automáticamente los diez más recientes.
                                        </p>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# HOME · EDITORIAL
# ---------------------------------------------------------------------------

DASHBOARD_HOME_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-stone-200 pb-10">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Resumen general
            </p>
            <h1 class="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Vista editorial del dashboard
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-stone-600">
                Una portada sobria y tipográfica para revisar la actividad reciente desde una tabla clara y
                densa, sin recurrir a tarjetas de métricas visuales.
            </p>
            <div class="mt-8">
                <a href="{% url 'NOMBRE_URL_LISTADO' %}"
                   class="inline-flex items-center justify-center rounded-full bg-stone-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-stone-800">
                    Ver listado completo
                </a>
            </div>
        </header>

        <section class="mt-12">
            <div class="mb-6">
                <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                    Registros recientes
                </p>
                <h2 class="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                    Últimos movimientos
                </h2>
            </div>

            <div class="overflow-x-auto border-y border-stone-200">
                <table class="min-w-full divide-y divide-stone-200">
                    <thead>
                        <tr>
                            <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                                Título
                            </th>
                            <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                                Categoría
                            </th>
                            <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                                Estado
                            </th>
                            <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                                Valor
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-stone-200">
                        {% for item in items|slice:":10" %}
                            <tr>
                                <td class="px-4 py-5 align-top">
                                    <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="font-semibold text-stone-900 transition hover:text-stone-700">
                                        {{ item.CAMPO_TITULO }} {# campo título principal #}
                                    </a>
                                    {% if item.CAMPO_FECHA %}
                                        <p class="mt-1 text-sm text-stone-500">
                                            {{ item.CAMPO_FECHA }} {# campo fecha #}
                                        </p>
                                    {% endif %}
                                </td>
                                <td class="px-4 py-5 align-top text-sm text-stone-600">
                                    {% if item.CAMPO_CATEGORIA %}
                                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                                <td class="px-4 py-5 align-top text-sm text-stone-600">
                                    {% if item.CAMPO_ESTADO %}
                                        {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                                <td class="px-4 py-5 align-top text-sm text-stone-600">
                                    {% if item.CAMPO_VALOR %}
                                        {{ item.CAMPO_VALOR }} {# campo numérico o métrica #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="4" class="px-4 py-12 text-center">
                                    <h3 class="text-lg font-semibold text-stone-900">No hay registros recientes</h3>
                                    <p class="mt-3 text-sm text-stone-600">
                                        Cuando existan elementos, esta tabla mostrará una selección de los últimos registros.
                                    </p>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </section>
    </div>
</section>
{% endblock %}"""

# ---------------------------------------------------------------------------
# LIST · DARK
# ---------------------------------------------------------------------------

DASHBOARD_LIST_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-800 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                Listado completo
            </p>
            <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                Tabla general de registros
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-gray-300">
                Una vista tabular densa y legible para revisar estado, categoría y valor de cada elemento.
            </p>
        </header>

        <div class="mt-8 overflow-hidden rounded-3xl border border-gray-800 bg-gray-900">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-800">
                    <thead class="bg-gray-950/50">
                        <tr>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                Título
                            </th>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                Categoría
                            </th>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                Estado
                            </th>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
                                Valor
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800">
                        {% for item in items %}
                            <tr class="transition hover:bg-gray-800/50">
                                <td class="px-6 py-4 align-top">
                                    <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="font-semibold text-white transition hover:text-blue-300">
                                        {{ item.CAMPO_TITULO }} {# campo título principal #}
                                    </a>
                                    {% if item.CAMPO_FECHA %}
                                        <p class="mt-1 text-sm text-gray-400">
                                            {{ item.CAMPO_FECHA }} {# campo fecha #}
                                        </p>
                                    {% endif %}
                                    {% if item.CAMPO_DESCRIPCION %}
                                        <p class="mt-2 text-sm text-gray-400">
                                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                        </p>
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 align-top text-sm text-gray-300">
                                    {% if item.CAMPO_CATEGORIA %}
                                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 align-top text-sm">
                                    {% if item.CAMPO_ESTADO %}
                                        <span class="inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 font-medium text-blue-300">
                                            {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                                        </span>
                                    {% else %}
                                        <span class="text-gray-500">—</span>
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 align-top text-sm text-gray-300">
                                    {% if item.CAMPO_VALOR %}
                                        {{ item.CAMPO_VALOR }} {# campo numérico o métrica #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="4" class="px-6 py-12 text-center">
                                    <h2 class="text-lg font-semibold text-white">No hay registros disponibles</h2>
                                    <p class="mt-3 text-sm text-gray-400">
                                        Cuando existan datos, este listado mostrará aquí la tabla completa del dashboard.
                                    </p>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
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

DASHBOARD_LIST_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-white text-gray-900">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-gray-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">
                Listado completo
            </p>
            <h1 class="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
                Tabla general de registros
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-gray-600">
                Una tabla limpia y clara para revisar información densa con buena jerarquía visual.
            </p>
        </header>

        <div class="mt-8 overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-200">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                Título
                            </th>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                Categoría
                            </th>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                Estado
                            </th>
                            <th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
                                Valor
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        {% for item in items %}
                            <tr class="transition hover:bg-gray-50">
                                <td class="px-6 py-4 align-top">
                                    <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="font-semibold text-gray-900 transition hover:text-gray-700">
                                        {{ item.CAMPO_TITULO }} {# campo título principal #}
                                    </a>
                                    {% if item.CAMPO_FECHA %}
                                        <p class="mt-1 text-sm text-gray-500">
                                            {{ item.CAMPO_FECHA }} {# campo fecha #}
                                        </p>
                                    {% endif %}
                                    {% if item.CAMPO_DESCRIPCION %}
                                        <p class="mt-2 text-sm text-gray-500">
                                            {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                        </p>
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 align-top text-sm text-gray-600">
                                    {% if item.CAMPO_CATEGORIA %}
                                        {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 align-top text-sm">
                                    {% if item.CAMPO_ESTADO %}
                                        <span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 font-medium text-gray-700">
                                            {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                                        </span>
                                    {% else %}
                                        <span class="text-gray-400">—</span>
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 align-top text-sm text-gray-600">
                                    {% if item.CAMPO_VALOR %}
                                        {{ item.CAMPO_VALOR }} {# campo numérico o métrica #}
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="4" class="px-6 py-12 text-center">
                                    <h2 class="text-lg font-semibold text-gray-900">No hay registros disponibles</h2>
                                    <p class="mt-3 text-sm text-gray-600">
                                        Cuando existan datos, este listado mostrará aquí la tabla completa del dashboard.
                                    </p>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
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

DASHBOARD_LIST_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-12">
        <header class="border-b border-stone-200 pb-8">
            <p class="text-sm font-semibold uppercase tracking-[0.25em] text-stone-500">
                Listado completo
            </p>
            <h1 class="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Tabla general de registros
            </h1>
            <p class="mt-4 max-w-3xl text-base leading-8 text-stone-600">
                Una tabla editorial y minimalista para consultar información con densidad, orden y tipografía protagonista.
            </p>
        </header>

        <div class="mt-8 overflow-x-auto border-y border-stone-200">
            <table class="min-w-full divide-y divide-stone-200">
                <thead>
                    <tr>
                        <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                            Título
                        </th>
                        <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                            Categoría
                        </th>
                        <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                            Estado
                        </th>
                        <th scope="col" class="px-4 py-4 text-left text-xs font-semibold uppercase tracking-[0.25em] text-stone-500">
                            Valor
                        </th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-stone-200">
                    {% for item in items %}
                        <tr>
                            <td class="px-4 py-5 align-top">
                                <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="font-semibold text-stone-900 transition hover:text-stone-700">
                                    {{ item.CAMPO_TITULO }} {# campo título principal #}
                                </a>
                                {% if item.CAMPO_FECHA %}
                                    <p class="mt-1 text-sm text-stone-500">
                                        {{ item.CAMPO_FECHA }} {# campo fecha #}
                                    </p>
                                {% endif %}
                                {% if item.CAMPO_DESCRIPCION %}
                                    <p class="mt-2 text-sm text-stone-500">
                                        {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                                    </p>
                                {% endif %}
                            </td>
                            <td class="px-4 py-5 align-top text-sm text-stone-600">
                                {% if item.CAMPO_CATEGORIA %}
                                    {{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}
                                {% else %}
                                    —
                                {% endif %}
                            </td>
                            <td class="px-4 py-5 align-top text-sm text-stone-600">
                                {% if item.CAMPO_ESTADO %}
                                    {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                                {% else %}
                                    —
                                {% endif %}
                            </td>
                            <td class="px-4 py-5 align-top text-sm text-stone-600">
                                {% if item.CAMPO_VALOR %}
                                    {{ item.CAMPO_VALOR }} {# campo numérico o métrica #}
                                {% else %}
                                    —
                                {% endif %}
                            </td>
                        </tr>
                    {% empty %}
                        <tr>
                            <td colspan="4" class="px-4 py-12 text-center">
                                <h2 class="text-lg font-semibold text-stone-900">No hay registros disponibles</h2>
                                <p class="mt-3 text-sm text-stone-600">
                                    Cuando existan datos, este listado mostrará aquí la tabla completa del dashboard.
                                </p>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
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

DASHBOARD_DETAIL_DARK = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-950 text-white">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-blue-400 transition hover:text-blue-300">
                ← Volver al listado
            </a>
        </div>

        <article class="rounded-3xl border border-gray-800 bg-gray-900 p-8">
            <header class="border-b border-gray-800 pb-8">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                        <h1 class="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h1>
                        {% if item.CAMPO_FECHA %}
                            <p class="mt-3 text-sm text-gray-400">
                                {{ item.CAMPO_FECHA }} {# campo fecha #}
                            </p>
                        {% endif %}
                    </div>

                    {% if item.CAMPO_ESTADO %}
                        <span class="inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm font-semibold text-blue-300">
                            {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                        </span>
                    {% endif %}
                </div>
            </header>

            <div class="mt-8 grid gap-8 lg:grid-cols-12">
                <div class="lg:col-span-7">
                    {% if item.CAMPO_DESCRIPCION %}
                        <section>
                            <h2 class="text-lg font-semibold text-white">Descripción</h2>
                            <p class="mt-4 text-base leading-8 text-gray-300">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        </section>
                    {% endif %}
                </div>

                <aside class="lg:col-span-5">
                    <div class="rounded-3xl border border-gray-800 bg-gray-950 p-6">
                        <h2 class="text-lg font-semibold text-white">Atributos</h2>
                        <dl class="mt-6 space-y-5">
                            {% if item.CAMPO_CATEGORIA %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-400">Categoría</dt>
                                    <dd class="mt-1 text-sm text-white">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_ESTADO %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-400">Estado</dt>
                                    <dd class="mt-1 text-sm text-white">{{ item.CAMPO_ESTADO }} {# campo estado o badge #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_VALOR %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-400">Valor</dt>
                                    <dd class="mt-1 text-sm text-white">{{ item.CAMPO_VALOR }} {# campo numérico o métrica #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-400">Fecha</dt>
                                    <dd class="mt-1 text-sm text-white">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-400">Información adicional</dt>
                                    <dd class="mt-1 text-sm text-white">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
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

# ---------------------------------------------------------------------------
# DETAIL · LIGHT
# ---------------------------------------------------------------------------

DASHBOARD_DETAIL_LIGHT = """{% extends 'base.html' %}
{% block content %}
<section class="bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-8">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-gray-900 transition hover:text-gray-700">
                ← Volver al listado
            </a>
        </div>

        <article class="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-gray-200">
            <header class="border-b border-gray-200 pb-8">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                        <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h1>
                        {% if item.CAMPO_FECHA %}
                            <p class="mt-3 text-sm text-gray-500">
                                {{ item.CAMPO_FECHA }} {# campo fecha #}
                            </p>
                        {% endif %}
                    </div>

                    {% if item.CAMPO_ESTADO %}
                        <span class="inline-flex items-center rounded-full bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700">
                            {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                        </span>
                    {% endif %}
                </div>
            </header>

            <div class="mt-8 grid gap-8 lg:grid-cols-12">
                <div class="lg:col-span-7">
                    {% if item.CAMPO_DESCRIPCION %}
                        <section>
                            <h2 class="text-lg font-semibold text-gray-900">Descripción</h2>
                            <p class="mt-4 text-base leading-8 text-gray-600">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        </section>
                    {% endif %}
                </div>

                <aside class="lg:col-span-5">
                    <div class="rounded-3xl bg-gray-50 p-6 ring-1 ring-gray-200">
                        <h2 class="text-lg font-semibold text-gray-900">Atributos</h2>
                        <dl class="mt-6 space-y-5">
                            {% if item.CAMPO_CATEGORIA %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Categoría</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_ESTADO %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Estado</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_ESTADO }} {# campo estado o badge #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_VALOR %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Valor</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_VALOR }} {# campo numérico o métrica #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_FECHA %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Fecha</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_FECHA }} {# campo fecha #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_EXTRA %}
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Información adicional</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ item.CAMPO_EXTRA }} {# cualquier otro campo relevante #}</dd>
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

# ---------------------------------------------------------------------------
# DETAIL · EDITORIAL
# ---------------------------------------------------------------------------

DASHBOARD_DETAIL_EDITORIAL = """{% extends 'base.html' %}
{% block content %}
<section class="bg-stone-50 text-stone-900">
    <div class="mx-auto max-w-5xl px-6 py-16 sm:px-8 lg:px-12">
        <div class="mb-10">
            <a href="{% url 'NOMBRE_URL_LISTADO' %}"
               class="inline-flex items-center text-sm font-semibold text-stone-900 transition hover:text-stone-700">
                ← Volver al listado
            </a>
        </div>

        <article class="border-y border-stone-200 py-10">
            <header class="border-b border-stone-200 pb-8">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                        <h1 class="text-4xl font-semibold tracking-tight text-stone-900 sm:text-5xl">
                            {{ item.CAMPO_TITULO }} {# campo título principal #}
                        </h1>
                        {% if item.CAMPO_FECHA %}
                            <p class="mt-3 text-sm text-stone-500">
                                {{ item.CAMPO_FECHA }} {# campo fecha #}
                            </p>
                        {% endif %}
                    </div>

                    {% if item.CAMPO_ESTADO %}
                        <span class="text-sm font-semibold text-stone-600">
                            {{ item.CAMPO_ESTADO }} {# campo estado o badge #}
                        </span>
                    {% endif %}
                </div>
            </header>

            <div class="mt-8 grid gap-8 lg:grid-cols-12">
                <div class="lg:col-span-7">
                    {% if item.CAMPO_DESCRIPCION %}
                        <section>
                            <h2 class="text-lg font-semibold text-stone-900">Descripción</h2>
                            <p class="mt-4 text-base leading-8 text-stone-700">
                                {{ item.CAMPO_DESCRIPCION }} {# campo texto largo #}
                            </p>
                        </section>
                    {% endif %}
                </div>

                <aside class="lg:col-span-5">
                    <div class="border border-stone-200 bg-white p-6">
                        <h2 class="text-lg font-semibold text-stone-900">Atributos</h2>
                        <dl class="mt-6 space-y-5">
                            {% if item.CAMPO_CATEGORIA %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Categoría</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_CATEGORIA }} {# campo categoría o tipo #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_ESTADO %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Estado</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_ESTADO }} {# campo estado o badge #}</dd>
                                </div>
                            {% endif %}
                            {% if item.CAMPO_VALOR %}
                                <div>
                                    <dt class="text-sm font-medium text-stone-500">Valor</dt>
                                    <dd class="mt-1 text-sm text-stone-900">{{ item.CAMPO_VALOR }} {# campo numérico o métrica #}</dd>
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
    "DASHBOARD_HOME_DARK",
    "DASHBOARD_HOME_LIGHT",
    "DASHBOARD_HOME_EDITORIAL",
    "DASHBOARD_LIST_DARK",
    "DASHBOARD_LIST_LIGHT",
    "DASHBOARD_LIST_EDITORIAL",
    "DASHBOARD_DETAIL_DARK",
    "DASHBOARD_DETAIL_LIGHT",
    "DASHBOARD_DETAIL_EDITORIAL",
]