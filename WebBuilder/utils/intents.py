from __future__ import annotations      # Usar todo como strings
from dataclasses import dataclass       # Permite definir una clase de datos
from typing import Dict, List, Tuple    # Definicion de tipos (INTENT_PROFILES)

# Tipo de web por defecto para el NORMALIZE_INTENT
DEFAULT_INTENT_KEY = "custom"


"""
Creo una clase con campos para tener la configuracion en un unico objeto
key: id interno (“blog”, “portfolio”)
label: nombre para mostrar en UI
description: texto corto UI
required: roles obligatorios para ese intent
recommended: roles recomendados
optional: roles opcionales
"""
@dataclass(frozen=True)
class IntentProfile:
    key: str
    label: str
    description: str
    required: Tuple[str, ...]
    recommended: Tuple[str, ...]
    optional: Tuple[str, ...]


"""
Diccionario con los diferentes roles y sus campos sugeridos
Para que lo uso:
    - Para ordenar roles en el wizard
    - Para agrupar por secciones (required/recommended/optional)
    - Para mostrar UI más clara
"""
INTENT_PROFILES: Dict[str, IntentProfile] = {
    "blog": IntentProfile(
        key="blog",
        label="Blog",
        description="Entradas con título, contenido y fecha.",
        required=("title",),
        recommended=("description", "content", "date"),
        optional=("author", "image", "thumbnail", "tags", "category", "link", "id"),
    ),
    "portfolio": IntentProfile(
        key="portfolio",
        label="Portfolio",
        description="Proyectos visuales con descripción e imagen.",
        required=("title",),
        recommended=("description", "image", "thumbnail", "link"),
        optional=("content", "tags", "category", "date", "id"),
    ),
    "catalog": IntentProfile(
        key="catalog",
        label="Catálogo",
        description="Productos con precio e imagen.",
        required=("title",),
        recommended=("price", "currency", "image", "description"),
        optional=("category", "tags", "link", "id", "date", "thumbnail", "content"),
    ),
    "directory": IntentProfile(
        key="directory",
        label="Directorio",
        description="Listado de elementos con ficha y enlace.",
        required=("title",),
        recommended=("description", "category", "link"),
        optional=("image", "thumbnail", "tags", "date", "id", "content"),
    ),
    "custom": IntentProfile(
        key="custom",
        label="Personalizado",
        description="Tú decides qué campos usar.",
        required=("title",),
        recommended=(),
        optional=(),
    ),
}


# Ver que valor de web coger, solo permite los conocidos en INTENT_PROFILES
def normalize_intent(intent: str | None) -> str:
    if not intent:
        return DEFAULT_INTENT_KEY
    intent = str(intent).strip().lower()
    return intent if intent in INTENT_PROFILES else DEFAULT_INTENT_KEY


# Recoge el campo selecionado pasando por la verificacion de normalize_intent
def get_profile(intent: str | None) -> IntentProfile:
    return INTENT_PROFILES[normalize_intent(intent)]


# Actualiza los roles en orden de prioridad para el wizard, si es custom no hay orden
def roles_for_intent(intent: str | None) -> List[str]:
    profile = get_profile(intent)
    if profile.key == "custom":
        return []
    ordered = list(profile.required) + list(profile.recommended) + list(profile.optional)
    seen = set()
    out: List[str] = []
    for r in ordered:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


# Mini descripcion de cada campo
ROLE_UI = {
    "title": {
        "label": "Título",
        "help": "Nombre principal del elemento. Se verá en grande en listas y en la página de detalle.",
    },
    "subtitle": {
        "label": "Subtítulo",
        "help": "Texto corto secundario para complementar el título.",
    },
    "description": {
        "label": "Descripción corta",
        "help": "Resumen breve que aparecerá en la tarjeta/listado.",
    },
    "content": {
        "label": "Contenido",
        "help": "Texto largo para la página de detalle (cuerpo del post, descripción extensa, etc.).",
    },
    "image": {
        "label": "Imagen principal",
        "help": "Imagen destacada para tarjetas y cabecera de detalle.",
    },
    "thumbnail": {
        "label": "Miniatura",
        "help": "Imagen pequeña para listados (si existe una versión reducida).",
    },
    "images": {
        "label": "Galería",
        "help": "Lista de imágenes para mostrar un carrusel o galería en detalle.",
    },
    "date": {
        "label": "Fecha",
        "help": "Fecha de publicación/creación. Útil para ordenar y mostrar cronología.",
    },
    "author": {
        "label": "Autor",
        "help": "Persona responsable del contenido (si aplica).",
    },
    "category": {
        "label": "Categoría",
        "help": "Grupo principal para organizar el contenido.",
    },
    "tags": {
        "label": "Etiquetas",
        "help": "Lista de tags para filtrar o agrupar por temas/tecnologías.",
    },
    "price": {
        "label": "Precio",
        "help": "Precio del producto/servicio (si aplica).",
    },
    "currency": {
        "label": "Moneda",
        "help": "Moneda del precio (EUR, USD…).",
    },
    "link": {
        "label": "Enlace",
        "help": "URL para más información, compra o página externa.",
    },
    "id": {
        "label": "ID / Identificador",
        "help": "Identificador único del elemento. Útil para generar URLs estables.",
    },
    "slug": {
        "label": "Slug",
        "help": "Texto corto para URL (por ejemplo 'mi-primer-post').",
    },
}


# Se encarga de obtener el label indicado para cada campo (label)
def role_ui(role: str) -> dict:
    role = (role or "").strip().lower()
    data = ROLE_UI.get(role)
    if data:
        return data
    return {"label": role.replace("_", " ").title(), "help": ""}

# Recoge y muestra los campos required, recommended... segun la web seleccionada
def role_section(intent: str | None, role: str) -> str:
    profile = get_profile(intent)
    if role in profile.required:
        return "required"
    if role in profile.recommended:
        return "recommended"
    if role in profile.optional:
        return "optional"
    return "other"


"""
Construye un diccionario segun las entradas que reciba:
Entrada:
    - intent: "blog", "portfolio", etc.
    - roles: lista de roles que vas a mostrar en el wizard (["title","description","image","link"])
Salida:
{
  "title": "required",
  "description": "recommended",
  "image": "optional",
  "link": "optional",
  ...
}
"""
def sections_for_intent(intent: str | None, roles: list[str]) -> dict[str, str]:
    return {r: role_section(intent, r) for r in roles}
