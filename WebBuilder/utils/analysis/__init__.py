"""
Módulo de análisis de datos
Proporciona funciones para analizar APIs y sugerir mappings

Este módulo está dividido en submódulos para mejor organización:
- constants: Definiciones de roles y configuración
- helpers: Funciones auxiliares (navegación, detección de tipos)
- detection: Detección de la colección principal
- suggestions: Sugerencias de mapping automático
- quality: Cálculo de calidad del mapping
- builder: Orquestador principal que construye el análisis completo
"""

from __future__ import annotations

# Constantes
from .constants import ROLE_DEFS

# Helpers (funciones auxiliares públicas)
from .helpers import get_by_path

# Detección (principalmente uso interno, pero disponible)
from .detection import find_main_items

# Sugerencias
from .suggestions import suggest_mapping, suggest_mapping_smart

# Calidad
from .quality import calculate_mapping_quality

# Builder (función principal)
from .builder import build_analysis


# Exports públicos
__all__ = [
    # Constantes
    'ROLE_DEFS',
    
    # Funciones principales
    'build_analysis',
    'calculate_mapping_quality',
    
    # Helpers útiles
    'get_by_path',
    
    # Sugerencias (ambas versiones disponibles)
    'suggest_mapping',
    'suggest_mapping_smart',
    
    # Detección (disponible pero raramente usado directamente)
    'find_main_items',
]
