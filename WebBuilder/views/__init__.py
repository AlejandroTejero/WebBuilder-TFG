# Autenticación
from .auth import register

# Páginas simples
from .pages import home

# Asistente
from .assistant import assistant, get_assistant, analyze_url, render_assistant

# Historial
from .history import history

# Preview (editor de schema)
from .preview import preview

# Render a pantalla completa
from .render import site_render, site_render_regen

__all__ = [
    "register",
    "home",
    "assistant",
    "get_assistant",
    "analyze_url",
    "render_assistant",
    "history",
    "preview",
    "site_render",
    "site_render_regen",
]
