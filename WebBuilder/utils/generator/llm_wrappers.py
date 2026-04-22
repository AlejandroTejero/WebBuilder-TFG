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


#def llm_call(system: str, user_text: str, label: str, temperature: float = 0.3) -> str:
#    """Llamada básica al LLM. Devuelve '' si falla."""
#    try:
#        time.sleep(20)
#        return chat_completion(
#            user_text=user_text,
#            system_text=system,
#            temperature=temperature,
#        )
#    except LLMError as e:
#        logger.error(f"[generator] LLM falló en '{label}': {e}")
#        # propagar en vez de pasar
#        raise   

# INCREMENTAL EN TIEMPO POR CADA ERROR
def llm_call(system: str, user_text: str, label: str, temperature: float = 0.3) -> str:
    delays = [5, 15, 30]  # esperas entre reintentos si hay 429
    for attempt, delay in enumerate(delays, 1):
        try:
            return chat_completion(
                user_text=user_text,
                system_text=system,
                temperature=temperature,
            )
        except LLMError as e:
            is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
            if is_rate_limit and attempt < len(delays):
                logger.warning(f"[generator] Rate limit en '{label}', reintentando en {delay}s (intento {attempt})")
                time.sleep(delay)
            else:
                raise

# En vez de chuks que devuleva todo de golpe

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


def translate_prompt_to_english(user_prompt: str) -> str:
    """
    Traduce el prompt del usuario a inglés usando el LLM.
    Si falla o el prompt ya está en inglés, devuelve el original.
    """
    if not user_prompt or not user_prompt.strip():
        return user_prompt

    # Heurística: si >95% de los caracteres son ASCII, ya está en inglés
    ascii_ratio = sum(1 for c in user_prompt if ord(c) < 128) / len(user_prompt)
    if ascii_ratio > 0.95:
        return user_prompt
    
    system = (
        "You are a translator. Your only job is to translate the user's text to English. "
        "Return ONLY the translated text, nothing else. "
        "No explanations, no preamble, no quotes. "
        "If the text is already in English, return it exactly as is."
    )

    try:
        result = llm_call(system, user_prompt, "translate_prompt", temperature=0.0)
        return result.strip() if result.strip() else user_prompt
    except LLMError:
        logger.warning("[generator] Traducción del prompt falló, usando original")
        return user_prompt
    

def llm_design_system_call(*, user_prompt: str, site_type: str, preset_description: str = "") -> dict:
    """
    Genera el design system de clases Tailwind para el proyecto.
    Devuelve un dict con los keys fijos del sistema de diseño.
    Si falla, devuelve un fallback genérico neutro.
    """
    from ..llm.generator_prompts import prompt_design_system

    _DESIGN_SYSTEM_FALLBACK = {
        "container": "max-w-7xl mx-auto px-6 sm:px-8",
        "card": "rounded-2xl border border-gray-200 bg-white p-4",
        "h1": "text-4xl font-bold tracking-tight text-gray-900",
        "h2": "text-2xl font-semibold text-gray-900",
        "h3": "text-lg font-bold text-gray-900",
        "text_muted": "text-sm text-gray-500",
        "badge_positive": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-green-100 text-green-700",
        "badge_negative": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-red-100 text-red-700",
        "badge_neutral": "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600",
        "btn_primary": "inline-block px-4 py-2 rounded-xl bg-gray-900 text-white font-semibold hover:bg-gray-700 transition-colors",
        "btn_secondary": "inline-block px-4 py-2 rounded-xl border border-gray-900 text-gray-900 font-semibold hover:bg-gray-100 transition-colors",
        "input": "w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-gray-900",
        "link": "text-gray-900 underline underline-offset-4 hover:text-gray-600 transition-colors",
        "divider": "border-t border-gray-200 my-8",
    }

    try:
        system, user_text = prompt_design_system(
            site_type=site_type,
            user_prompt=user_prompt,
            preset_description=preset_description,
        )
        result = llm_json_call(system, user_text, "design_system")

        # Validar que tiene todos los keys esperados
        expected_keys = set(_DESIGN_SYSTEM_FALLBACK.keys())
        if not expected_keys.issubset(result.keys()):
            missing = expected_keys - result.keys()
            logger.warning("[generator] Design system incompleto, keys faltantes: %s", missing)
            # Rellenar los que faltan con el fallback
            for key in missing:
                result[key] = _DESIGN_SYSTEM_FALLBACK[key]

        logger.info("[generator] Design system generado correctamente")
        return result

    except Exception as e:
        logger.warning("[generator] Design system falló (%s), usando fallback neutro", e)
        return _DESIGN_SYSTEM_FALLBACK