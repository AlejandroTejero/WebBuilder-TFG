# Permite usar anotaciones de tipos como strings
from __future__ import annotations

# Importa urlparse para validar el esquema de la URL
from urllib.parse import urlparse

# Importa requests para hacer peticiones HTTP
import requests

# Límite máximo de bytes permitidos (1MB)
MAX_BYTES = 1_000_000
# Timeout por defecto en segundos
DEFAULT_TIMEOUT = 8
# Cabeceras por defecto para la petición
DEFAULT_HEADERS = {"User-Agent": "WebBuilder/1.0"}


# Valida que la URL use http o https
def validate_url(api_url: str) -> None:
    # Parsea la URL para inspeccionar sus partes
    parsed_url = urlparse(api_url)
    # Comprueba si el esquema es válido
    if parsed_url.scheme not in ("http", "https"):
        # Lanza error si no es http/https
        raise ValueError("La URL debe empezar por http:// o https://.")


# Descarga una URL y devuelve (texto_crudo, resumen)
def fetch_url(api_url: str, *, timeout: int = DEFAULT_TIMEOUT, max_bytes: int = MAX_BYTES) -> tuple[str, str]:
    # Valida la URL antes de pedirla
    validate_url(api_url)

    # Intenta hacer la petición HTTP y capturar errores comunes
    try:
        # Ejecuta la petición GET con timeout y headers
        http_response = requests.get(api_url, timeout=timeout, headers=DEFAULT_HEADERS)
        # Lanza excepción si el status code es 4xx/5xx
        http_response.raise_for_status()
    # Captura timeout explícitamente
    except requests.exceptions.Timeout:
        # Lanza error controlado para la UI
        raise ValueError("La URL ha tardado demasiado en responder (timeout).")
    # Captura fallo de conexión (DNS, red, etc.)
    except requests.exceptions.ConnectionError:
        # Lanza error controlado para la UI
        raise ValueError("No se pudo conectar con la URL (fallo de conexión).")
    # Captura errores HTTP (404, 500, etc.)
    except requests.exceptions.HTTPError as exc:
        # Lanza error controlado con detalle
        raise ValueError(f"Error HTTP al acceder a la URL: {exc}")

    # Obtiene el texto de respuesta (decodificado por requests)
    raw_text = http_response.text
    # Calcula el tamaño real en bytes (UTF-8)
    raw_size_bytes = len(raw_text.encode("utf-8"))
    # Comprueba el límite de tamaño
    if raw_size_bytes > max_bytes:
        # Lanza error si supera el límite
        raise ValueError(f"Respuesta demasiado grande. Límite {max_bytes} bytes.")

    # Construye un resumen corto para mostrar en UI/historial
    summary = f"HTTP {http_response.status_code}. {len(raw_text)} caracteres."
    # Devuelve el texto crudo y el resumen
    return raw_text, summary


# Devuelve una previsualización truncada del texto
def make_preview(raw_text: str, max_chars: int = 600) -> str:
    # Devuelve los primeros caracteres como preview
    return raw_text[:max_chars]
