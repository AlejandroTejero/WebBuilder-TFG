from __future__ import annotations

import json
from typing import Any, Optional

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import APIRequest


# ====================
# Utils de presentación (truncado + pretty JSON)
# ====================

def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "\n\n...[truncado]..."


def _pretty_json(data: Any, max_len: int = 12000) -> str:
    try:
        txt = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        txt = str(data)
    return _truncate(txt, max_len)


def _pre_block(text: str) -> str:
    # Nota: usamos format_html para evitar inyección HTML (escapa contenido).
    return format_html(
        "<pre style='white-space:pre-wrap; max-width:1100px; overflow:auto;'>{}</pre>",
        text,
    )


# ====================
# Admin principal: APIRequest
# ====================

@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    # ====================
    # Config de navegación (listado)
    # ====================

    list_display = (
        "id",
        "user",
        "status_badge",
        "api_url_short",
        "date",
        "fmt",
        "root_type",
        "main_items_hint",
        "has_mapping",
        "raw_chars",
        "preview_link",
    )

    list_filter = ("status", "date")
    date_hierarchy = "date"
    search_fields = ("api_url", "user__username", "user__email")
    ordering = ("-date",)
    list_select_related = ("user",)
    list_per_page = 50

    # ====================
    # Vista detalle (edit)
    # ====================

    fieldsets = (
        ("Identificación", {
            "fields": ("user", "api_url", "status", "date"),
        }),
        ("Resumen", {
            "fields": ("response_summary", "error_message"),
        }),
        ("Diagnóstico rápido", {
            "fields": ("fmt", "root_type", "main_items_hint", "raw_chars", "has_mapping"),
        }),
        ("Datos (crudo y parseado)", {
            "classes": ("collapse",),
            "fields": ("raw_data_pretty", "parsed_data_pretty"),
        }),
        ("Mapping (wizard)", {
            "classes": ("collapse",),
            "fields": ("field_mapping_pretty",),
        }),
    )

    readonly_fields = (
        "date",
        "fmt",
        "root_type",
        "main_items_hint",
        "raw_chars",
        "has_mapping",
        "raw_data_pretty",
        "parsed_data_pretty",
        "field_mapping_pretty",
        "preview_link",
    )

    # Ocultamos los campos grandes para que no aparezcan como inputs enormes
    exclude = ("raw_data", "parsed_data", "field_mapping")

    # ====================
    # Helpers para list_display
    # ====================

    @admin.display(description="ESTADO")
    def status_badge(self, obj: APIRequest) -> str:
        status = (obj.status or "").lower()
        if status == "processed":
            cls = "background:#143; border:1px solid #2a6; color:#dff7e3;"
        elif status == "error":
            cls = "background:#411; border:1px solid #a55; color:#ffe1e1;"
        elif status == "pending":
            cls = "background:#223; border:1px solid #66a; color:#e7ecff;"
        else:
            cls = "background:#222; border:1px solid #444; color:#eee;"

        return format_html(
            "<span style='display:inline-block; padding:2px 8px; border-radius:999px; font-weight:600; {}'>{}</span>",
            cls,
            obj.status or "-",
        )

    @admin.display(description="URL")
    def api_url_short(self, obj: APIRequest) -> str:
        url = obj.api_url or ""
        if len(url) <= 70:
            return url
        return url[:67] + "..."

    @admin.display(description="RAW CHARS")
    def raw_chars(self, obj: APIRequest) -> int:
        raw = getattr(obj, "raw_data", "") or ""
        return len(raw)

    @admin.display(description="FORMATO")
    def fmt(self, obj: APIRequest) -> str:
        raw = (getattr(obj, "raw_data", "") or "").lstrip()
        if raw.startswith("{") or raw.startswith("["):
            return "json"
        if raw.startswith("<"):
            return "xml"
        return "-"

    @admin.display(description="RAÍZ")
    def root_type(self, obj: APIRequest) -> str:
        data = getattr(obj, "parsed_data", None)
        if isinstance(data, dict):
            return "dict"
        if isinstance(data, list):
            return "list"
        return "-"

    @admin.display(description="ITEMS")
    def main_items_hint(self, obj: APIRequest) -> str:
        """
        Hint rápido (sin recalcular todo el análisis en admin).
        - Si la raíz es lista => len(list)
        - Si la raíz es dict => intenta detectar listas típicas 1 nivel (data/results/items)
        """
        data = getattr(obj, "parsed_data", None)

        if isinstance(data, list):
            return f"root list ({len(data)})"

        if isinstance(data, dict):
            # heurística simple de admin: mirar 1 nivel en keys comunes
            for k in ("results", "items", "data", "entries"):
                v = data.get(k)
                if isinstance(v, list):
                    return f"{k} list ({len(v)})"
                if isinstance(v, dict):
                    for kk in ("results", "items", "entries"):
                        vv = v.get(kk)
                        if isinstance(vv, list):
                            return f"{k}→{kk} list ({len(vv)})"

        return "—"

    @admin.display(description="MAPPING", boolean=True)
    def has_mapping(self, obj: APIRequest) -> bool:
        m = getattr(obj, "field_mapping", None)
        return bool(m)

    @admin.display(description="PREVIEW")
    def preview_link(self, obj: APIRequest) -> str:
        """
        Link a tu vista preview si existe el url name 'preview'.
        Si por cualquier razón no está, devolvemos '-'.
        """
        try:
            url = reverse("preview", args=[obj.id])
        except Exception:
            return "-"
        return format_html("<a href='{}' target='_blank'>Abrir</a>", url)

    # ====================
    # Pretty fields (read-only) para detalle
    # ====================

    @admin.display(description="RAW DATA (preview)")
    def raw_data_pretty(self, obj: APIRequest) -> str:
        raw = getattr(obj, "raw_data", None) or ""
        if not raw:
            return "—"
        shown = _truncate(raw, 8000)
        return _pre_block(shown)

    @admin.display(description="PARSED DATA (pretty)")
    def parsed_data_pretty(self, obj: APIRequest) -> str:
        data = getattr(obj, "parsed_data", None)
        if data is None:
            return "—"
        return _pre_block(_pretty_json(data, max_len=12000))

    @admin.display(description="FIELD MAPPING (wizard)")
    def field_mapping_pretty(self, obj: APIRequest) -> str:
        mapping = getattr(obj, "field_mapping", None)
        if not mapping:
            return "—"
        return _pre_block(_pretty_json(mapping, max_len=12000))
