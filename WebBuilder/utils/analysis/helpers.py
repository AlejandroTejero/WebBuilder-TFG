"""
Funciones auxiliares para análisis de datos
Incluye navegación de paths, normalización y detección de tipos
"""

from __future__ import annotations
import re


def get_by_path(parsed_data: object, path: list):
    """
    Navega parsed_data siguiendo un path de keys/índices
    
    Args:
        parsed_data: Datos parseados (dict, list, etc.)
        path: Lista de pasos (strings para keys, ints para índices)
        
    Returns:
        El nodo en esa posición, o None si el path no existe
        
    Examples:
        >>> data = {"users": [{"name": "Ana"}, {"name": "Bob"}]}
        >>> get_by_path(data, ["users", 0, "name"])
        "Ana"
    """
    # Empieza en la raíz
    node = parsed_data
    
    # Recorre cada paso del path
    for step in path:
        # Si el paso es un índice
        if isinstance(step, int):
            # Si el nodo actual no es lista o índice inválido, devuelve None
            if not isinstance(node, list) or step < 0 or step >= len(node):
                return None
            # Avanza al elemento indexado
            node = node[step]
            
        # Si el paso es una key de dict
        elif isinstance(step, str):
            # Si el nodo actual no es dict o no existe la key, devuelve None
            if not isinstance(node, dict) or step not in node:
                return None
            # Avanza al valor de esa key
            node = node[step]
            
        # Si el paso no es int ni str, devolvemos None
        else:
            return None
            
    # Devuelve el nodo final
    return node


def _normalize_key(text: str) -> str:
    """
    Normaliza una key para comparaciones insensibles a mayúsculas/espacios
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado (lowercase, sin espacios extra)
    """
    return text.strip().lower()


def _is_url(value: object) -> bool:
    """
    Heurística: detecta si un valor parece una URL
    
    Args:
        value: Valor a analizar
        
    Returns:
        True si parece URL (comienza con http:// o https://)
    """
    # Solo tiene sentido si es string
    if not isinstance(value, str):
        return False
        
    # Normaliza el string
    lowered = value.strip().lower()
    
    # Comprueba prefijo http/https
    return lowered.startswith("http://") or lowered.startswith("https://")


def _is_date(value: object) -> bool:
    """
    Heurística: detecta si un valor parece una fecha
    
    Args:
        value: Valor a analizar
        
    Returns:
        True si parece fecha (formato ISO, YYYY-MM-DD, etc.)
    """
    # Solo tiene sentido si es string
    if not isinstance(value, str):
        return False
        
    # Recorta espacios
    text = value.strip()
    
    # Busca patrón YYYY-MM-DD o YYYY/MM/DD
    if re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", text):
        return True
        
    # Busca patrón ISO con T (YYYY-MM-DDTHH:MM:SS)
    if re.search(r"\d{4}-\d{2}-\d{2}T", text):
        return True
        
    # Si no cuadra, no es fecha
    return False


def _is_number(value: object) -> bool:
    """
    Heurística: detecta si un valor es numérico
    
    Args:
        value: Valor a analizar
        
    Returns:
        True si es int/float (pero no bool)
    """
    # True si es int/float pero no bool
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _path_display(path: list | None) -> str:
    """
    Formatea un path para mostrarlo en UI de forma legible
    
    Args:
        path: Lista con el path (keys y/o índices), o None
        
    Returns:
        String formateado para mostrar
        
    Examples:
        >>> _path_display(None)
        "—"
        >>> _path_display([])
        "(raíz)"
        >>> _path_display(["users", 0, "name"])
        "users → [0] → name"
    """
    if path is None:
        return "—"
    if path == []:
        return "(raíz)"
        
    parts: list[str] = []
    for p in path:
        if isinstance(p, int):
            parts.append(f"[{p}]")
        else:
            parts.append(str(p))
            
    return " → ".join(parts)
