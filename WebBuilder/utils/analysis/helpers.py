from __future__ import annotations  # Usar todo como strings
import re                           # Para _is_date


# ========================== PATHS / NAVEGACION ==========================

# Dado un dict/list navega y ofrece el contenido de cada campo
def get_by_path(parsed_data: object, path: list):
    # Empieza en la raíz
    node = parsed_data
    
    for step in path:
        # Si el paso es un índice
        if isinstance(step, int):
            if not isinstance(node, list) or step < 0 or step >= len(node):
                return None
            node = node[step]
            
        # Si el paso es una key de dict
        elif isinstance(step, str):
            if not isinstance(node, dict) or step not in node:
                return None
            node = node[step]
            
        # Si el paso no es int ni str, devolvemos None
        else:
            return None
            
    return node

# ========================== DETECCIONES ==========================

# Normaliza una key para comparaciones insensibles a mayúsculas/espacios
def _normalize_key(text: str) -> str:
    return text.strip().lower()

# Detecta si un valor parece a una URL o no
def _is_url(value: object) -> bool:
    # Solo tiene sentido si es string
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    return lowered.startswith("http://") or lowered.startswith("https://")

# Detecta si un valor parece una fecha
def _is_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    # Busca patrón YYYY-MM-DD o YYYY/MM/DD
    if re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", text):
        return True
    # Busca patrón ISO con T (YYYY-MM-DDTHH:MM:SS)
    if re.search(r"\d{4}-\d{2}-\d{2}T", text):
        return True
    return False

# Detecta si un valor es numérico
def _is_number(value: object) -> bool:
    # True si es int/float pero no bool
    return isinstance(value, (int, float)) and not isinstance(value, bool)

# Formatea un path para mostrarlo en UI de forma legible
def _path_display(path: list | None) -> str:
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
