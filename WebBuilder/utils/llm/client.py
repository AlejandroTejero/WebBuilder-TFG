import json
import requests
from django.conf import settings


class LLMError(Exception):
    pass


def chat_completion(user_text: str, system_text: str | None = None) -> str:
    """
    Minimal OpenAI-compatible client for OpenRouter.
    Returns assistant text.
    """
    if not settings.LLM_API_KEY:
        raise LLMError("LLM_API_KEY está vacío. Revisa .env y load_dotenv().")

    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "WebBuilder",
    }

    messages = []
    if system_text:
        messages.append({"role": "system", "content": system_text})
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
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