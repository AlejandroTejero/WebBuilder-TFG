"""
llm_wrappers.py — Wrappers de llamada al LLM y limpieza de respuestas.

Centraliza:
  - _llm_call: llamada básica con manejo de errores
  - _llm_json_call: llamada esperando JSON
  - _llm_call_logged: llamada con guardado de log en BD
  - strip_markdown_fences: limpieza de fences Markdown en la respuesta
"""
from __future__ import annotations

import re
import time
import logging

from ..llm.client import chat_completion, LLMError
from ..llm.llm_utils import parse_llm_json

logger = logging.getLogger(__name__)


def llm_call(system: str, user_text: str, label: str, temperature: float = 0.3) -> str:
    """Llamada básica al LLM. Devuelve '' si falla."""
    try:
        time.sleep(10)
        return chat_completion(
            user_text=user_text,
            system_text=system,
            temperature=temperature,
        )
    except LLMError as e:
        logger.error(f"[generator] LLM falló en '{label}': {e}")
        return ""


def llm_json_call(system: str, user_text: str, label: str) -> dict:
    """Llama al LLM esperando JSON. Devuelve {} si falla o si el JSON es inválido."""
    raw = llm_call(system, user_text, label, temperature=0.0)
    if not raw:
        return {}
    try:
        return parse_llm_json(raw)
    except Exception as e:
        logger.error(f"[generator] JSON parse falló en '{label}': {e}")
        return {}


def llm_call_logged(
    system: str,
    user_text: str,
    label: str,
    temperature: float,
    site=None,
) -> str:
    """Llama al LLM y guarda el log en BD si se pasa un objeto site."""
    result = llm_call(system, user_text, label, temperature)

    if site is not None:
        try:
            from ...models import GenerationLog
            from django.conf import settings
            GenerationLog.objects.create(
                site=site,
                step=label,
                llm_model=settings.LLM_MODEL,
                system_prompt=system[:2000],
                user_prompt=user_text[:2000],
                raw_output=result[:5000],
            )
        except Exception:
            pass  # El log nunca puede romper la generación

    return result


def strip_markdown_fences(code: str) -> str:
    """
    Limpieza definitiva de fences Markdown en respuestas del LLM.

    Estrategia: eliminar cualquier línea que sea únicamente un fence (```xxx),
    sin tocar el código real. Funciona independientemente de dónde ponga
    el LLM los fences.
    """
    code = code.strip()

    # Primero intentar extraer el interior de un bloque completo
    match = re.search(r"```(?:\w+)?\n(.*?)```", code, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Si no hay bloque completo, eliminar línea a línea cualquier fence
    lines = code.splitlines()
    clean = [line for line in lines if not re.match(r"^\s*```", line)]
    return "\n".join(clean).strip()
