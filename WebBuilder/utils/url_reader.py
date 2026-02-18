from __future__ import annotations  # Usar todo como strings
from urllib.parse import urlparse   # Descomponer url en partes y sirve para validad
import requests                     # resquest para hacer peticiones http


# ========================== CONSTANTES ==========================

# Límite máximo de bytes permitidos (1MB), para evitar caidas del server
MAX_BYTES = 1_000_000
# Timeout por defecto en segundos
DEFAULT_TIMEOUT = 8
# Cabeceras por defecto para la petición
DEFAULT_HEADERS = {"User-Agent": "WebBuilder/1.0"}

# ========================== VALIDACION ==========================

# Valida que la URL use http o https
def validate_url(api_url: str) -> None:
    parsed_url = urlparse(api_url)
    if parsed_url.scheme not in ("http", "https"):
        raise ValueError("La URL debe empezar por http:// o https://.")

# ========================== DESCARGA + TEXTO CRUDO -> CONTROLADO ==========================


# Validamos la url, decargamos contenido en raw, y 
def fetch_url(api_url: str, *, timeout: int = DEFAULT_TIMEOUT, max_bytes: int = MAX_BYTES) -> tuple[str, str]:
    validate_url(api_url)

    try:
        # Ejecuta la petición GET con timeout y max_bytes, vemos tbm el status (2xx,3xx,4xx,5xx).
        http_response = requests.get(api_url, timeout=timeout, headers=DEFAULT_HEADERS, stream=True)
        http_response.raise_for_status()

        # Comprobamos que tenemos contenido y contamos cuando para ver si pasa del max
        content_length = http_response.headers.get("Content-Length")
        if content_length is not None:
            try:
                content_length_int = int(content_length)
            except (TypeError, ValueError):
                content_length_int = None

            if content_length_int is not None and content_length_int > max_bytes:
                raise ValueError(f"Respuesta demasiado grande. Límite {max_bytes} bytes.")

    # Capturamos errores tipicos
    except requests.exceptions.Timeout:
        raise ValueError("La URL ha tardado demasiado en responder (timeout).")
    except requests.exceptions.ConnectionError:
        raise ValueError("No se pudo conectar con la URL (fallo de conexión).")
    except requests.exceptions.HTTPError as exc:
        raise ValueError(f"Error HTTP al acceder a la URL: {exc}")

    try:
        # Descarga el body en chunks de tamaño (8192)
        raw_bytes = bytearray()
        for chunk in http_response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            raw_bytes.extend(chunk)
            if len(raw_bytes) > max_bytes:
                raise ValueError(f"Respuesta demasiado grande. Límite {max_bytes} bytes.")

        # Decodifica usando la codificación que requests haya detectado si es posible.
        encoding = http_response.encoding or "utf-8"
        raw_text = raw_bytes.decode(encoding, errors="replace")

        summary = f"HTTP {http_response.status_code}. {len(raw_text)} caracteres. ({len(raw_bytes)} bytes)"
        return raw_text, summary
    finally:
        # Cerramos la conexion
        http_response.close()


# Devuelve una previsualización truncada del texto de los 600 primeros CARACTERES
def make_preview(raw_text: str, max_chars: int = 600) -> str:
    return raw_text[:max_chars]
