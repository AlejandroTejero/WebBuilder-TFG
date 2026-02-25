# Autenticación
from .auth import register
# Páginas simples
from .pages import home
# Asistente
from .assistant import assistant
# Historial
from .history import history
# Editor de schema
from .edit import edit
# Render a pantalla completa
from .render import site_render, site_render_regen

__all__ = [
    "register",
    "home",
    "assistant",
    "history",
    "edit",
    "site_render",
    "site_render_regen",
]