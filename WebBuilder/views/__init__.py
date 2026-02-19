# Autenticación
from .auth import register

# Páginas simples
from .pages import home

# Asistente (MVP: solo análisis)
from .assistant import (
    assistant,
    get_assistant,
    analyze_url,
    render_assistant,
)

# Historial
from .history import history

# Preview
from .preview import preview


__all__ = [
    # Auth
    "register",

    # Pages
    "home",

    # Assistant
    "assistant",
    "get_assistant",
    "analyze_url",
    "render_assistant",

    # History
    "history",

    # Preview
    "preview",
]
