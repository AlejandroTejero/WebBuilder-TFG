import json
import requests
from django.conf import settings


class LLMError(Exception):
    pass


def chat_completion(
    user_text: str,
    system_text: str | None = None,
    *,
    temperature: float = 0.2,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Minimal OpenAI-compatible client for OpenRouter.
    Returns assistant text.
    """
    _effective_api_key = api_key or settings.LLM_API_KEY
    if not _effective_api_key:
        raise LLMError("LLM_API_KEY está vacío. Revisa .env y load_dotenv().")

    _base_url = base_url or settings.LLM_BASE_URL
    _model = model or settings.LLM_MODEL

    url = f"{_base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {_effective_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "WebBuilder",
    }

    messages = []
    if system_text:
        messages.append({"role": "system", "content": system_text})
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": _model,
        "messages": messages,
        "temperature": temperature,
    }

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
    except requests.RequestException as e:
        raise LLMError(f"Error de red llamando al LLM: {e}") from e

    if resp.status_code >= 400:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise LLMError(f"LLM HTTP {resp.status_code}: {err}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise LLMError(f"Respuesta inesperada del LLM: {data}") from e