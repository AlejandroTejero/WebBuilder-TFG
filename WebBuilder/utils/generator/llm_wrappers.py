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
        # propagar en vez de pasar
        raise   


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
    error_msg = ""
    result = ""

    try:
        result = llm_call(system, user_text, label, temperature)
    except LLMError as e:
        error_msg = str(e)   # ← capturamos el error real aquí
        logger.error(f"[generator] Error capturado en '{label}': {error_msg}")

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
                raw_output=result[:5000] if result else f"[ERROR] {error_msg}",  # ← el error queda visible
            )
        except Exception:
            pass

    return result  # sigue devolviendo "" cuando falla, el flujo no se rompe

def strip_markdown_fences(code: str) -> str:
    code = code.strip()

    # Extraer interior de bloque completo
    match = re.search(r"```(?:\w+)?\n(.*?)```", code, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Eliminar líneas que sean solo fences
    lines = code.splitlines()
    clean = [line for line in lines if not re.match(r"^\s*```", line)]
    code = "\n".join(clean).strip()

    # ← NUEVO: eliminar artefactos típicos del LLM al final del archivo
    artifacts = {"EOF", "# end of file", "# EOF", "# fin", "# end"}
    final_lines = code.splitlines()
    while final_lines and final_lines[-1].strip() in artifacts:
        final_lines.pop()

    return "\n".join(final_lines).strip()


def extract_requirements(code: str) -> tuple[str, list[str]]:
    """
    Extrae las librerías extra que el LLM indica con ##REQUIREMENTS:
    Devuelve (código_limpio, lista_de_requirements)
    """
    requirements = []
    clean_lines = []
    
    for line in code.splitlines():
        if line.strip().startswith("##REQUIREMENTS:"):
            value = line.strip().replace("##REQUIREMENTS:", "").strip()
            if value and value.lower() != "none":
                reqs = [r.strip() for r in value.split(",") if r.strip()]
                requirements.extend(reqs)
        else:
            clean_lines.append(line)
    
    return "\n".join(clean_lines).strip(), requirements