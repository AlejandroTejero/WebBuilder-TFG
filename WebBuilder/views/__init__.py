"""
WebBuilder Views Package
Organiza las vistas en módulos separados por funcionalidad
"""

# Autenticación
from .auth import register

# Páginas simples
from .pages import home

# Asistente (wizard completo)
from .assistant import (
    assistant,
    get_assistant,
    analyze_url,
    save_mapping,
    render_assistant,
)

# Preview
from .preview import (
    preview,
    preview_cards,
)

# Historial
from .history import history


# Lista de exports públicos
__all__ = [
    # Auth
    'register',
    
    # Pages
    'home',
    
    # Assistant
    'assistant',
    'get_assistant',
    'analyze_url',
    'save_mapping',
    'render_assistant',
    
    # Preview
    'preview',
    'preview_cards',
    
    # History
    'history',
]
