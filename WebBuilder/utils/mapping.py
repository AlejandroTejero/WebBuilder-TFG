# Permite usar anotaciones de tipos como strings
from __future__ import annotations

# Importa Any para tipar entradas flexibles (p.ej. request.POST)
from typing import Any

# Importa el modelo donde guardamos el mapping en BD
from ..models import APIRequest
# Importa la fuente de verdad de roles del análisis
from .analysis import ROLE_DEFS

# Clave de sesión donde guardamos el mapping del usuario
SESSION_MAPPING_KEY = "field_mapping"
# Clave de sesión donde guardamos el último APIRequest analizado (fallback al guardar mapping)
SESSION_LAST_REQUEST_ID_KEY = "last_api_request_id"
# Clave para el mamping de tipo blog, protfolio, etc.
SESSION_INTENT_KEY = "mapping_intent"


# Lee map_<role> del POST y devuelve un dict (role -> key)
def read_mapping(post_data: Any) -> dict:
    # Inicializa el dict del mapping
    field_mapping: dict[str, str] = {}
    # Recorre todos los roles definidos
    for role_name in ROLE_DEFS.keys():
        # Lee el valor del select map_<role> (o vacío si falta)
        field_mapping[role_name] = post_data.get(f"map_{role_name}", "")
    # Devuelve el mapping final
    return field_mapping


# Guarda el mapping en la sesión del usuario
def store_mapping(request, field_mapping: dict) -> None:
    # Escribe el dict en la sesión bajo la clave acordada
    request.session[SESSION_MAPPING_KEY] = field_mapping


# Carga el mapping desde la sesión del usuario
def get_mapping(request) -> dict:
    # Devuelve dict guardado o dict vacío
    return request.session.get(SESSION_MAPPING_KEY, {}) or {}

def store_intent(request, intent: str) -> None:
    request.session[SESSION_INTENT_KEY] = (intent or "").strip().lower()


def get_intent(request) -> str:
    return (request.session.get(SESSION_INTENT_KEY) or "").strip().lower()


# Decide qué api_request_id usar al guardar mapping (POST primero, sesión después)
def resolve_api_id(request, *, post_api_request_id: str | None = None) -> str | None:
    # Si viene id por POST, tiene prioridad
    if post_api_request_id:
        # Devuelve el id del POST
        return post_api_request_id
    # Si no, usa fallback en sesión
    return request.session.get(SESSION_LAST_REQUEST_ID_KEY)


# Guarda el mapping en BD dentro de APIRequest.field_mapping si existe y pertenece al usuario
def save_mapping_to_db(*, user, api_request_id: str | int | None, field_mapping: dict) -> APIRequest | None:
    # Si no hay id, no se puede guardar en BD
    if not api_request_id:
        # Devuelve None para indicar que no se guardó
        return None

    # Busca el APIRequest por id y usuario (seguridad)
    api_request_obj = APIRequest.objects.filter(id=api_request_id, user=user).first()
    # Si no existe el registro, no guardamos nada
    if not api_request_obj:
        # Devuelve None para indicar que no se guardó
        return None

    # Escribe el mapping en el JSONField
    api_request_obj.field_mapping = field_mapping
    # Guarda solo ese campo para no tocar otros
    api_request_obj.save(update_fields=["field_mapping"])
    # Devuelve el objeto actualizado
    return api_request_obj

def build_role_options(
    analysis_result: dict | None,
    field_mapping: dict,
    *,
    roles: list[str] | None = None,
    role_sections: dict[str, str] | None = None,
    role_ui_map: dict[str, dict] | None = None,
) -> list[dict]:
    """
    Construye opciones de selección por rol para el wizard de mapping.

    - Si se pasa `roles`, se usa ese orden (guiado por intención).
    - Si no, se usa el orden por defecto del análisis (analysis_result["roles"]).
    - `role_sections` permite agrupar en UI: required / recommended / optional / other
    - `role_ui_map` permite mostrar label/help humanos.
    """
    if not analysis_result:
        return []

    all_keys: list[str] = analysis_result.get("keys", {}).get("all", []) or []
    role_select_options: list[dict] = []

    roles_to_use = roles if roles is not None else (analysis_result.get("roles", []) or [])

    for role_name in roles_to_use:
        suggested_keys = (analysis_result.get("suggestions", {}).get(role_name, []) or [])[:5]

        selected_key = field_mapping.get(role_name) or (suggested_keys[0] if suggested_keys else "")

        options_keys: list[str] = []
        seen: set[str] = set()

        # 1) Primero, el seleccionado actual (aunque no sea sugerido / aunque no exista ya)
        if selected_key:
            seen.add(selected_key)
            options_keys.append(selected_key)

        # 2) Luego, sugerencias
        for k in suggested_keys:
            if k and k not in seen:
                seen.add(k)
                options_keys.append(k)

        # 3) Por último, todas las keys detectadas
        for k in all_keys:
            if k and k not in seen:
                seen.add(k)
                options_keys.append(k)

        ui = (role_ui_map or {}).get(role_name, {"label": role_name, "help": ""})
        section = (role_sections or {}).get(role_name, "other")

        role_select_options.append(
            {
                "role": role_name,
                "label": ui.get("label", role_name),
                "help": ui.get("help", ""),
                "section": section,
                "options": [
                    {
                        "key": k,
                        "is_selected": (k == selected_key),
                        "is_suggested": (k in suggested_keys),
                    }
                    for k in options_keys
                ],
                "none_selected": (selected_key == ""),
            }
        )

    return role_select_options

def _collect_allowed_keys_from_analysis(analysis_result: dict | None) -> set[str]:
    # Si no hay análisis, no podemos validar keys contra el dataset
    if not analysis_result:
        return set()

    allowed: set[str] = set()

    # 1) Preferimos las keys completas detectadas en la colección principal
    all_keys = analysis_result.get("keys", {}).get("all") or []
    for k in all_keys:
        if isinstance(k, str) and k.strip():
            allowed.add(k.strip())

    # 2) Fallback: sample_keys
    sample_keys = analysis_result.get("main_collection", {}).get("sample_keys") or []
    for k in sample_keys:
        if isinstance(k, str) and k.strip():
            allowed.add(k.strip())

    # 3) Fallback: top_keys (pares key,count)
    top_keys = analysis_result.get("main_collection", {}).get("top_keys") or []
    for pair in top_keys:
        if isinstance(pair, (list, tuple)) and len(pair) >= 1:
            k = pair[0]
            if isinstance(k, str) and k.strip():
                allowed.add(k.strip())

    return allowed


# ==================== ✨ VERSIÓN MEJORADA ✨ ====================
def validate_mapping(
    field_mapping: dict,
    *,
    analysis_result: dict | None = None,
    required_roles: tuple[str, ...] = ("title",),
    prevent_duplicates_in: tuple[str, ...] = ("title", "description", "subtitle", "content", "author"),
    allow_duplicate_in: tuple[str, ...] = ("id", "link", "date", "category", "tags"),
) -> dict:
    """
    Valida el mapping con detección MEJORADA de duplicados.
    
    MEJORAS vs versión anterior:
    - prevent_duplicates_in: Roles que NO pueden compartir key (genera ERROR)
    - allow_duplicate_in: Roles donde duplicados son razonables (sin warning)
    - Resto de duplicados generan WARNING
    
    Args:
        field_mapping: Mapping del usuario {role: key}
        analysis_result: Análisis de la API (opcional, para validar keys)
        required_roles: Roles obligatorios (por defecto solo "title")
        prevent_duplicates_in: Roles críticos que no pueden duplicar keys
        allow_duplicate_in: Roles donde duplicados son aceptables
    
    Returns:
        {
            "ok": bool,              # False si hay errores
            "errors": list[str],     # Errores que bloquean guardado
            "warnings": list[str],   # Advertencias que no bloquean
            "cleaned": dict,         # Mapping limpiado (strip)
        }
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Limpieza básica (strip de espacios)
    cleaned: dict[str, str] = {}
    for role_name, key_name in (field_mapping or {}).items():
        if isinstance(key_name, str):
            cleaned[role_name] = key_name.strip()
        else:
            cleaned[role_name] = ""

    # 1) Validar roles mínimos obligatorios
    for role in required_roles:
        if not cleaned.get(role):
            errors.append(f"El rol obligatorio '{role}' no puede quedar vacío.")

    # 2) Validar que las keys existan en el dataset analizado
    allowed_keys = _collect_allowed_keys_from_analysis(analysis_result)
    if allowed_keys:
        for role_name, key_name in cleaned.items():
            if not key_name:
                continue
            if key_name not in allowed_keys:
                warnings.append(
                    f"El rol '{role_name}' apunta a '{key_name}', pero esa key no aparece en la colección principal detectada."
                )

    # 3) ✨ DETECCIÓN DE DUPLICADOS MEJORADA
    seen: dict[str, str] = {}  # key_name -> primer role_name que la usó
    
    for role_name, key_name in cleaned.items():
        if not key_name:
            continue
        
        # Si esta key ya fue usada por otro rol
        if key_name in seen:
            previous_role = seen[key_name]
            
            # Caso A: Ambos roles están en lista de prevención → ERROR CRÍTICO
            if role_name in prevent_duplicates_in and previous_role in prevent_duplicates_in:
                errors.append(
                    f"⚠️ ERROR: Los roles '{role_name}' y '{previous_role}' no pueden usar el mismo campo '{key_name}'. "
                    f"Esto haría que tu web tenga contenido repetitivo y confuso para los usuarios."
                )
            
            # Caso B: Alguno está en lista de permitidos → SIN MENSAJE (es razonable)
            elif role_name in allow_duplicate_in or previous_role in allow_duplicate_in:
                # Duplicado razonable (ej: varios roles usando "id" o "date")
                # No generamos ni error ni warning
                pass
            
            # Caso C: Duplicado cuestionable pero no crítico → WARNING
            else:
                warnings.append(
                    f"Los roles '{role_name}' y '{previous_role}' usan el mismo campo '{key_name}'. "
                    f"¿Es esto intencional? Considera usar campos diferentes."
                )
        else:
            # Primera vez que vemos esta key, la registramos
            seen[key_name] = role_name

    return {
        "ok": (len(errors) == 0),
        "errors": errors,
        "warnings": warnings,
        "cleaned": cleaned,
    }
