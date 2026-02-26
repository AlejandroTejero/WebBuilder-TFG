from __future__ import annotations

import json
from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import APIRequest, GeneratedSite


# ══════════════════════════════════════════════════════════════════
# Título del admin
# ══════════════════════════════════════════════════════════════════
admin.site.site_header  = "WebBuilder Admin"
admin.site.site_title   = "WebBuilder"
admin.site.index_title  = "Panel de administración"


# ══════════════════════════════════════════════════════════════════
# Utils
# ══════════════════════════════════════════════════════════════════

def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ""
    return text if len(text) <= max_len else text[:max_len] + "\n\n...[truncado]..."


def _pretty_json(data: Any, max_len: int = 12000) -> str:
    try:
        txt = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        txt = str(data)
    return _truncate(txt, max_len)


def _pre(text: str) -> str:
    return format_html(
        "<pre style='white-space:pre-wrap;max-width:1100px;overflow:auto;"
        "background:#0d0d0d;border:1px solid #222;border-radius:8px;"
        "padding:1rem;font-size:0.78rem;color:#94a3b8;'>{}</pre>",
        text,
    )


def _badge(label: str, color: str) -> str:
    colors = {
        "green":  ("rgba(34,197,94,0.1)",   "rgba(34,197,94,0.25)",  "#4ade80"),
        "red":    ("rgba(239,68,68,0.1)",    "rgba(239,68,68,0.25)",  "#f87171"),
        "orange": ("rgba(251,146,60,0.1)",   "rgba(251,146,60,0.25)", "#fb923c"),
        "purple": ("rgba(139,92,246,0.1)",   "rgba(139,92,246,0.25)", "#a78bfa"),
        "blue":   ("rgba(59,130,246,0.1)",   "rgba(59,130,246,0.25)", "#60a5fa"),
        "gray":   ("rgba(255,255,255,0.05)", "rgba(255,255,255,0.1)", "#64748b"),
    }
    bg, border, fg = colors.get(color, colors["gray"])
    return format_html(
        "<span style='display:inline-block;padding:2px 10px;border-radius:999px;"
        "font-size:0.75rem;font-weight:600;background:{};border:1px solid {};color:{};'>"
        "{}</span>",
        bg, border, fg, label,
    )


# ══════════════════════════════════════════════════════════════════
# APIRequest
# ══════════════════════════════════════════════════════════════════

@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status_badge",
        "api_url_short",
        "date",
        "fmt",
        "root_type",
        "main_items_hint",
        "has_mapping_badge",
        "plan_accepted_badge",
        "raw_chars",
        "edit_link",
    )

    list_filter   = ("status", "plan_accepted", "date", "user")
    date_hierarchy = "date"
    search_fields  = ("api_url", "user__username", "user__email")
    ordering       = ("-date",)
    list_select_related = ("user",)
    list_per_page  = 40
    actions = ["mark_pending"]

    fieldsets = (
        ("Identificación", {
            "fields": ("user", "api_url", "status", "plan_accepted", "date"),
        }),
        ("Resumen", {
            "fields": ("response_summary", "error_message"),
        }),
        ("Diagnóstico rápido", {
            "fields": ("fmt", "root_type", "main_items_hint", "raw_chars", "has_mapping_badge"),
        }),
        ("Datos crudos y parseados", {
            "classes": ("collapse",),
            "fields": ("raw_data_pretty", "parsed_data_pretty"),
        }),
        ("Field mapping / schema", {
            "classes": ("collapse",),
            "fields": ("field_mapping_pretty",),
        }),
    )

    readonly_fields = (
        "date", "fmt", "root_type", "main_items_hint", "raw_chars",
        "has_mapping_badge", "plan_accepted_badge",
        "raw_data_pretty", "parsed_data_pretty", "field_mapping_pretty",
        "edit_link",
    )

    exclude = ("raw_data", "parsed_data", "field_mapping")

    @admin.display(description="Estado")
    def status_badge(self, obj):
        color = {"processed": "green", "error": "red", "pending": "orange"}.get(obj.status or "", "gray")
        return _badge(obj.status or "-", color)

    @admin.display(description="URL")
    def api_url_short(self, obj):
        url = obj.api_url or ""
        return url[:70] + "..." if len(url) > 70 else url

    @admin.display(description="Chars")
    def raw_chars(self, obj):
        return len(obj.raw_data or "")

    @admin.display(description="Fmt")
    def fmt(self, obj):
        raw = (obj.raw_data or "").lstrip()
        if raw.startswith(("{", "[")): return "json"
        if raw.startswith("<"): return "xml"
        return "-"

    @admin.display(description="Raíz")
    def root_type(self, obj):
        if isinstance(obj.parsed_data, dict): return "dict"
        if isinstance(obj.parsed_data, list): return "list"
        return "-"

    @admin.display(description="Items")
    def main_items_hint(self, obj):
        data = obj.parsed_data
        if isinstance(data, list):
            return f"root list ({len(data)})"
        if isinstance(data, dict):
            for k in ("results", "items", "data", "entries"):
                v = data.get(k)
                if isinstance(v, list):
                    return f"{k} ({len(v)})"
        return "—"

    @admin.display(description="Schema")
    def has_mapping_badge(self, obj):
        if obj.field_mapping:
            fields = obj.field_mapping.get("fields", [])
            return _badge(f"✓ {len(fields)} campos", "purple")
        return _badge("sin schema", "gray")

    @admin.display(description="Publicado")
    def plan_accepted_badge(self, obj):
        return _badge("✓ sí", "blue") if obj.plan_accepted else _badge("no", "gray")

    @admin.display(description="Editor")
    def edit_link(self, obj):
        try:
            url = reverse("edit", args=[obj.id])
            return format_html("<a href='{}' target='_blank'>Abrir →</a>", url)
        except Exception:
            return "-"

    @admin.display(description="Raw data")
    def raw_data_pretty(self, obj):
        return _pre(_truncate(obj.raw_data or "", 8000)) if obj.raw_data else "—"

    @admin.display(description="Parsed data")
    def parsed_data_pretty(self, obj):
        return _pre(_pretty_json(obj.parsed_data)) if obj.parsed_data is not None else "—"

    @admin.display(description="Field mapping")
    def field_mapping_pretty(self, obj):
        return _pre(_pretty_json(obj.field_mapping)) if obj.field_mapping else "—"

    @admin.action(description="Marcar como pendiente")
    def mark_pending(self, request, queryset):
        updated = queryset.update(status="pending", plan_accepted=False)
        self.message_user(request, f"{updated} análisis marcados como pendiente.")


# ══════════════════════════════════════════════════════════════════
# GeneratedSite
# ══════════════════════════════════════════════════════════════════

@admin.register(GeneratedSite)
class GeneratedSiteAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "site_title",
        "site_type_badge",
        "owner",
        "fields_count",
        "has_theme_badge",
        "created_at",
        "updated_at",
        "view_link",
        "edit_link",
    )

    list_filter   = ("created_at",)
    search_fields = ("project_source__api_url", "project_source__user__username", "theme_prompt")
    ordering      = ("-created_at",)
    list_select_related = ("project_source", "project_source__user")
    list_per_page = 40
    date_hierarchy = "created_at"
    actions = ["clear_theme"]

    fieldsets = (
        ("Origen", {
            "fields": ("project_source", "public_id", "created_at", "updated_at"),
        }),
        ("Plan aceptado", {
            "fields": ("site_title", "site_type_badge", "fields_count", "accepted_plan_pretty"),
        }),
        ("Tema generado", {
            "fields": ("theme_prompt", "has_theme_badge", "theme_css_pretty"),
        }),
        ("Templates HTML", {
            "classes": ("collapse",),
            "fields": ("theme_templates_pretty",),
        }),
    )

    readonly_fields = (
        "public_id", "created_at", "updated_at",
        "site_title", "site_type_badge", "fields_count", "has_theme_badge", "owner",
        "accepted_plan_pretty", "theme_css_pretty", "theme_templates_pretty",
        "view_link", "edit_link",
    )

    exclude = ("accepted_plan", "theme_templates", "theme_css")

    @admin.display(description="Título")
    def site_title(self, obj):
        plan = obj.accepted_plan or {}
        return plan.get("site_title") or plan.get("site_type") or "—"

    @admin.display(description="Tipo")
    def site_type_badge(self, obj):
        plan = obj.accepted_plan or {}
        t = plan.get("site_type") or "other"
        color = {"catalog": "blue", "blog": "green", "portfolio": "purple", "dashboard": "orange"}.get(t, "gray")
        return _badge(t, color)

    @admin.display(description="Usuario")
    def owner(self, obj):
        return obj.project_source.user.username

    @admin.display(description="Campos")
    def fields_count(self, obj):
        return f"{len((obj.accepted_plan or {}).get('fields') or [])} campos"

    @admin.display(description="Tema")
    def has_theme_badge(self, obj):
        if obj.theme_templates:
            return _badge(f"✓ {len(obj.theme_templates)} templates", "green")
        return _badge("sin tema", "red")

    @admin.display(description="Ver sitio")
    def view_link(self, obj):
        try:
            url = reverse("site_render", args=[obj.project_source.id])
            return format_html("<a href='{}' target='_blank'>Ver →</a>", url)
        except Exception:
            return "-"

    @admin.display(description="Editor")
    def edit_link(self, obj):
        try:
            url = reverse("edit", args=[obj.project_source.id])
            return format_html("<a href='{}' target='_blank'>Editar →</a>", url)
        except Exception:
            return "-"

    @admin.display(description="Plan aceptado")
    def accepted_plan_pretty(self, obj):
        return _pre(_pretty_json(obj.accepted_plan)) if obj.accepted_plan else "—"

    @admin.display(description="Theme CSS")
    def theme_css_pretty(self, obj):
        return _pre(_truncate(obj.theme_css or "", 6000)) if obj.theme_css else "—"

    @admin.display(description="Templates HTML")
    def theme_templates_pretty(self, obj):
        return _pre(_pretty_json(obj.theme_templates)) if obj.theme_templates else "—"

    @admin.action(description="Limpiar tema (forzar regeneración)")
    def clear_theme(self, request, queryset):
        updated = queryset.update(theme_templates={}, theme_css="", theme_prompt="")
        self.message_user(request, f"Tema limpiado en {updated} sitios.")


# ══════════════════════════════════════════════════════════════════
# User — extender con info de proyectos
# ══════════════════════════════════════════════════════════════════

class APIRequestInline(admin.TabularInline):
    model = APIRequest
    extra = 0
    fields = ("api_url", "status", "plan_accepted", "date")
    readonly_fields = ("api_url", "status", "plan_accepted", "date")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Análisis del usuario"
    ordering = ("-date",)
    max_num = 10


class CustomUserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + (APIRequestInline,)
    list_display = (
        "username", "email", "is_staff", "is_active",
        "date_joined", "total_analyses", "total_sites",
    )

    @admin.display(description="Análisis")
    def total_analyses(self, obj):
        return obj.api_requests.count()

    @admin.display(description="Sitios")
    def total_sites(self, obj):
        return GeneratedSite.objects.filter(project_source__user=obj).count()


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
