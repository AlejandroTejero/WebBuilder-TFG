"""
fallbacks.py — Contenido de emergencia cuando el LLM falla o devuelve vacío.

Cada función devuelve una versión mínima pero funcional del artefacto
correspondiente, garantizando que la generación nunca se rompa del todo.
"""
from __future__ import annotations

from django.utils.text import slugify


def fallback_pages(site_type: str) -> list[dict]:
    """Estructura de páginas mínima si el LLM falla."""
    if site_type == "portfolio":
        return [
            {
                "name": "home",
                "url": "/",
                "template": "siteapp/home.html",
                "view_name": "home",
                "description": "Landing principal con proyectos y contacto",
                "is_list": False,
                "is_detail": False,
            },
            {
                "name": "project_detail",
                "url": "/project/<pk>/",
                "template": "siteapp/project_detail.html",
                "view_name": "project_detail",
                "description": "Detalle de un proyecto",
                "is_list": False,
                "is_detail": True,
            },
        ]
    return [
        {
            "name": "home",
            "url": "/",
            "template": "siteapp/home.html",
            "view_name": "home",
            "description": "Portada del sitio",
            "is_list": False,
            "is_detail": False,
        },
        {
            "name": "catalog",
            "url": "/catalog/",
            "template": "siteapp/catalog.html",
            "view_name": "catalog",
            "description": "Listado de items",
            "is_list": True,
            "is_detail": False,
        },
        {
            "name": "detail",
            "url": "/item/<pk>/",
            "template": "siteapp/detail.html",
            "view_name": "detail",
            "description": "Detalle de un item",
            "is_list": False,
            "is_detail": True,
        },
    ]

def fallback_models(fields: list[dict]) -> str:
    """models.py mínimo si el LLM falla."""
    lines = ["from django.db import models", "", "class Item(models.Model):"]
    for f in fields:
        name = slugify(f["key"]).replace("-", "_") or "field"
        lines.append(f"    {name} = models.CharField(max_length=500, blank=True)")
    lines += [
        "    created_at = models.DateTimeField(auto_now_add=True)",
        "",
        "    def __str__(self):",
        "        return str(self.pk)",
        "",
    ]
    return "\n".join(lines)


def fallback_views(pages: list[dict]) -> str:
    """views.py mínimo si el LLM falla."""
    lines = [
        "from django.shortcuts import render, get_object_or_404",
        "from .models import Item",
        "",
    ]
    for page in pages:
        if page.get("is_detail"):
            lines += [
                f"def {page['view_name']}(request, pk):",
                "    item = get_object_or_404(Item, pk=pk)",
                f"    return render(request, '{page['template']}', {{'item': item, 'site_title': 'Mi Sitio'}})",
                "",
            ]
        elif page.get("is_list"):
            lines += [
                f"def {page['view_name']}(request):",
                "    from django.core.paginator import Paginator",
                "    queryset = Item.objects.all().order_by('-id')",
                "    paginator = Paginator(queryset, 12)",
                "    page_obj = paginator.get_page(request.GET.get('page', 1))",
                f"    return render(request, '{page['template']}', {{'page_obj': page_obj, 'site_title': 'Mi Sitio'}})",
                "",
            ]
        else:
            lines += [
                f"def {page['view_name']}(request):",
                "    items = Item.objects.all().order_by('-id')[:6]",
                f"    return render(request, '{page['template']}', {{'items': items, 'site_title': 'Mi Sitio'}})",
                "",
            ]
    return "\n".join(lines)


def fallback_base_html(site_title: str, pages: list[dict]) -> str:
    """base.html mínimo con Tailwind si el LLM falla."""
    nav_links = "\n".join(
        f'      <a href="{p["url"]}" class="text-gray-300 hover:text-green-400">{p["name"].title()}</a>'
        for p in pages if not p.get("is_detail")
    )
    return f"""<!doctype html>
<html lang="es" class="bg-gray-950">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{site_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
  <nav class="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
    <span class="text-green-400 font-bold">{site_title}</span>
    <div class="flex gap-6 text-sm">
{nav_links}
    </div>
  </nav>
  <main class="max-w-7xl mx-auto px-6 py-10">
    {{% block content %}}{{% endblock %}}
  </main>
  <footer class="text-center text-gray-600 text-xs py-8">{site_title}</footer>
</body>
</html>"""


def fallback_template(page: dict) -> str:
    """Template HTML mínimo para una página si el LLM falla."""
    if page.get("is_list"):
        return (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'>\n"
            "{% for item in items %}\n"
            "  <a href=\"{% url 'detail' item.pk %}\" "
            "class='block bg-gray-900 border border-gray-800 rounded-xl p-5 "
            "hover:border-green-400 transition-all'>\n"
            "    <p class='text-white font-semibold'>{{ item }}</p>\n"
            "  </a>\n"
            "{% endfor %}\n"
            "</div>\n"
            "{% endblock %}\n"
        )
    elif page.get("is_detail"):
        return (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<a href=\"{% url 'catalog' %}\" class='text-green-400 text-sm'>← Volver</a>\n"
            "<div class='bg-gray-900 border border-gray-800 rounded-xl p-8 mt-4'>\n"
            "  <p class='text-white text-2xl font-bold'>{{ item }}</p>\n"
            "</div>\n"
            "{% endblock %}\n"
        )
    else:
        return (
            "{% extends 'base.html' %}\n"
            "{% block content %}\n"
            "<div class='text-center py-20'>\n"
            "  <h1 class='text-5xl font-black text-white'>{{ site_title }}</h1>\n"
            "  <a href=\"{% url 'catalog' %}\" "
            "class='mt-8 inline-block bg-green-400 text-black px-8 py-3 "
            "rounded-lg font-bold hover:bg-green-300 transition-colors'>Ver catálogo</a>\n"
            "</div>\n"
            "{% endblock %}\n"
        )


def fallback_load_data(fields: list[dict], api_url: str) -> str:
    """management command load_data mínimo si el LLM falla."""
    mapping = {f["key"]: slugify(f["key"]).replace("-", "_") for f in fields}
    return (
        "from django.core.management.base import BaseCommand\n"
        "from siteapp.models import Item\n"
        "import requests\n"
        "\n"
        f"API_URL = '{api_url}'\n"
        f"MAPPING = {mapping!r}\n"
        "\n"
        "class Command(BaseCommand):\n"
        "    help = 'Carga datos desde la API'\n"
        "\n"
        "    def handle(self, *args, **options):\n"
        "        try:\n"
        "            data = requests.get(API_URL, timeout=30).json()\n"
        "        except Exception as e:\n"
        "            self.stderr.write(f'Error descargando datos: {e}')\n"
        "            return\n"
        "\n"
        "        items = data if isinstance(data, list) else (\n"
        "            next((v for v in data.values() if isinstance(v, list)), [])\n"
        "            if isinstance(data, dict) else []\n"
        "        )\n"
        "\n"
        "        created = 0\n"
        "        for raw in items:\n"
        "            if not isinstance(raw, dict):\n"
        "                continue\n"
        "            obj = {}\n"
        "            for api_key, field_name in MAPPING.items():\n"
        "                val = raw.get(api_key)\n"
        "                obj[field_name] = str(val) if val is not None else ''\n"
        "            Item.objects.create(**obj)\n"
        "            created += 1\n"
        "\n"
        "        self.stdout.write(self.style.SUCCESS(f'Creados {created} items.'))\n"
    )
