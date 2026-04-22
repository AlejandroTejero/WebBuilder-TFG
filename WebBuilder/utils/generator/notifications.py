"""
notifications.py — Notificaciones a n8n tras eventos del generador.
"""
from __future__ import annotations

import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def notify_generation_done(site, duration_seconds: int = 0) -> None:
    """
    Llama al webhook de n8n para notificar que la generación ha terminado.
    Si falla, solo loggea — nunca rompe la generación.
    """
    webhook_url = getattr(settings, "N8N_WEBHOOK_GENERATION_DONE", "")
    if not webhook_url:
        logger.info("[notify] N8N_WEBHOOK_GENERATION_DONE no configurado, omitiendo.")
        return

    plan = site.accepted_plan or {}
    fields = plan.get("fields") or []
    source = site.project_source

    payload = {
        "email":            source.user.email,
        "username":         source.user.username,
        "site_title":       plan.get("site_title", "Tu sitio"),
        "site_type":        plan.get("site_type", "other"),
        "api_url":          source.api_url,
        "preview_url":      site.preview_url or "",
        "zip_url":          f"/site/{site.public_id}/download/",
        "num_items":        len((plan.get("_meta") or {}).get("sample_items") or []),
        "num_fields":       len(fields),
        "duration_seconds": duration_seconds,
        "llm_model":        getattr(settings, "LLM_MODEL", ""),
    }

    try:
        logger.info("[notify] Llamando webhook: %s", webhook_url)
        logger.info("[notify] Payload: %s", payload)
        resp = requests.post(webhook_url, json=payload, timeout=30)
        logger.info("[notify] generation-done enviado → %s", resp.status_code)
    except Exception as e:
        logger.warning("[notify] Fallo al notificar generation-done: %s", e)