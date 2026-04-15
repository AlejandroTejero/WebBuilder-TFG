"""
theme_rules.py — Base visual y reglas de tema para generación con LLM.

Objetivo:
- Dar al LLM una base visual coherente y reutilizable.
- Reducir errores típicos al generar clases Tailwind.
- Centralizar combinaciones seguras de layout, color y componentes.
- Servir como apoyo al prompt, no como sustituto del prompt del usuario.
"""

from __future__ import annotations

import json


# ── REGLAS CRÍTICAS DE USO DE COLOR ────────────────────────────────────────

SAFE_COLOR_USAGE_RULES = [
    "Si usas colores HEX en Tailwind, usa siempre sintaxis de valores arbitrarios válida: bg-[#111111], text-[#10b981], border-[#222222].",
    "Nunca uses clases inválidas como bg-#111111, text-#10b981, border-#222222, hover:text-#10b981 o hover:border-#10b981/50.",
    "Si el usuario da colores explícitos, aplícalos de forma consistente en fondo, texto, borde, links, botones, badges y estados activos.",
    "Si el usuario no da colores, usa una paleta neutra y coherente con el tipo de sitio.",
    "No fuerces modo oscuro por defecto salvo que el prompt del usuario o el tipo de sitio lo justifiquen.",
]


# ── TOKENS VISUALES BASE ───────────────────────────────────────────────────

BASE_THEME_RULES = {
    "container_base": "mx-auto max-w-6xl px-4 sm:px-6 lg:px-8",
    "container_narrow": "mx-auto max-w-3xl px-4 sm:px-6 lg:px-8",
    "section_spacing": "py-12 md:py-16",
    "section_spacing_compact": "py-8 md:py-10",
    "card_base": "rounded-2xl border",
    "card_soft": "rounded-2xl border shadow-sm",
    "panel_base": "rounded-2xl border",
    "input_base": "rounded-xl border px-4 py-2",
    "button_base": "inline-flex items-center justify-center rounded-xl px-4 py-2 font-medium transition-colors",
    "badge_base": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border",
    "table_base": "w-full border-collapse",
    "light_background": "bg-white text-black",
    "light_surface": "bg-white border border-gray-200",
    "dark_background": "bg-[#0a0a0a] text-white",
    "dark_surface": "bg-[#111111] border border-[#222222]",
    "muted_text_light": "text-gray-600",
    "muted_text_dark": "text-gray-400",
    "title_strong": "text-3xl md:text-5xl font-bold tracking-tight",
    "title_medium": "text-2xl md:text-3xl font-semibold tracking-tight",
    "body_base": "text-sm md:text-base leading-7",
}


# ── VARIANTES DE ESTILO ORIENTATIVAS ───────────────────────────────────────

STYLE_VARIANTS = {
    "editorial": [
        "Prioriza tipografía, ritmo vertical, márgenes amplios y lectura cómoda.",
        "Evita efectos visuales llamativos, sombras fuertes, gradientes agresivos y cards innecesariamente decorativas.",
        "Puede encajar mejor un contenedor estrecho como container_narrow.",
    ],
    "catalog": [
        "Prioriza grid claro, cards consistentes, imágenes bien recortadas y navegación de exploración sencilla.",
        "Los metadatos y badges pueden ayudar si no recargan visualmente.",
        "Las cards pueden tener más presencia visual si el prompt del usuario lo pide.",
    ],
    "minimal": [
        "Reduce adornos y componentes innecesarios.",
        "Prioriza limpieza, contraste, alineación y jerarquía clara.",
        "Evita sobrecargar con badges, iconos o secciones redundantes.",
    ],
    "dashboard": [
        "Prioriza legibilidad rápida, bloques claros y jerarquía de datos.",
        "Usa paneles y métricas con coherencia visual, sin decorar en exceso.",
    ],
}


# ── PATRONES BASE DE COMPONENTE ────────────────────────────────────────────

COMPONENT_PATTERNS = {
    "navbar": [
        "La navbar debe ser clara, usable y visualmente coherente con el prompt del usuario.",
        "No conviertas la navbar en un bloque pesado si el estilo pedido es sobrio o editorial.",
    ],
    "cards": [
        "Las cards deben adaptarse al tipo de sitio: visuales en catálogo, sobrias en editorial, técnicas en fichas o dashboards.",
        "Usa imágenes en cards solo si el prompt del usuario y el dataset lo justifican.",
    ],
    "badges": [
        "Los badges deben usarse cuando realmente ayudan a clasificar o resumir información.",
        "Evita exceso de badges decorativos en estilos sobrios o minimalistas.",
    ],
    "detail_layout": [
        "En páginas de detalle, usa una jerarquía clara entre título, imagen, metadatos y cuerpo principal.",
        "El layout puede ser más visual o más técnico según el prompt del usuario.",
    ],
}


# ── HELPERS PARA INYECTAR EN PROMPTS ───────────────────────────────────────

def build_theme_rules_text() -> str:
    lines = ["REGLAS SEGURAS DE TEMA Y COLOR:"]
    lines.extend(f"- {rule}" for rule in SAFE_COLOR_USAGE_RULES)
    lines.append("")
    lines.append("BASE VISUAL REUTILIZABLE:")
    for key, value in BASE_THEME_RULES.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("VARIANTES DE ESTILO ORIENTATIVAS:")
    for variant, rules in STYLE_VARIANTS.items():
        lines.append(f"- {variant}:")
        lines.extend(f"  - {rule}" for rule in rules)
    lines.append("")
    lines.append("PATRONES BASE DE COMPONENTE:")
    for component, rules in COMPONENT_PATTERNS.items():
        lines.append(f"- {component}:")
        lines.extend(f"  - {rule}" for rule in rules)
    return "\n".join(lines)


def export_theme_rules_json() -> str:
    payload = {
        "safe_color_usage_rules": SAFE_COLOR_USAGE_RULES,
        "base_theme_rules": BASE_THEME_RULES,
        "style_variants": STYLE_VARIANTS,
        "component_patterns": COMPONENT_PATTERNS,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)