"""
field_extractor.py — Extrae los nombres reales de campos del models.py generado.
Se usan para inyectarlos en los prompts siguientes y evitar inconsistencias.
"""
import re


def extract_model_fields(models_code: str) -> list[str]:
    """
    Extrae los nombres de campo reales del models.py generado.
    Devuelve lista de strings como ['title', 'pub_date', 'image_url']
    """
    pattern = r'^\s+(\w+)\s*=\s*models\.'
    fields = re.findall(pattern, models_code, re.MULTILINE)

    # Excluir campos meta que no son datos del dataset
    excluded = {'created_at', 'updated_at', 'id', 'pk'}
    return [f for f in fields if f not in excluded]