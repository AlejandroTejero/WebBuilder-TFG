"""
migrations_generator.py — Generación de la migración inicial 0001_initial.py.

Parsea el models.py generado por el LLM y construye la migración correspondiente.

NOTA: Este módulo está pendiente de eliminar cuando las migraciones
se generen íntegramente por el LLM.
"""
from __future__ import annotations

import re


# Tipos de campo soportados para el parseo
_FIELD_TYPE_MAP = {
    "CharField":           "models.CharField",
    "TextField":           "models.TextField",
    "IntegerField":        "models.IntegerField",
    "FloatField":          "models.FloatField",
    "BooleanField":        "models.BooleanField",
    "DateTimeField":       "models.DateTimeField",
    "URLField":            "models.URLField",
    "EmailField":          "models.EmailField",
    "DecimalField":        "models.DecimalField",
    "PositiveIntegerField": "models.PositiveIntegerField",
}


def generate_initial_migration(models_code: str, app: str = "siteapp") -> str:
    """
    Genera un 0001_initial.py básico parseando los campos del models.py generado.

    Soporta CharField, TextField, IntegerField, FloatField, BooleanField,
    DateTimeField, URLField, EmailField, DecimalField.
    Siempre añade id AutoField y created_at DateTimeField si no están presentes.
    """
    field_lines = _extract_fields(models_code)
    migration_fields = _build_migration_fields(field_lines)
    fields_str = "\n".join(migration_fields)

    return f"""from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
{fields_str}
            ],
        ),
    ]
"""


def _extract_fields(models_code: str) -> list[tuple[str, str, str]]:
    """Extrae las tuplas (nombre, tipo, args) de los campos del modelo."""
    field_lines = []
    in_model = False

    for line in models_code.splitlines():
        stripped = line.strip()

        if re.match(r"class \w+\(models\.Model\)", stripped):
            in_model = True
            continue

        if in_model:
            if stripped.startswith("class ") and in_model:
                break

            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith("def")
                and not stripped.startswith("class")
                and "=" in stripped
            ):
                field_match = re.match(r"(\w+)\s*=\s*models\.(\w+)\((.*)\)", stripped)
                if field_match:
                    fname, ftype, fargs = field_match.groups()
                    if fname == "id":
                        continue
                    if ftype in _FIELD_TYPE_MAP:
                        field_lines.append((fname, ftype, fargs))

    return field_lines


def _build_migration_fields(field_lines: list[tuple[str, str, str]]) -> list[str]:
    """Construye las líneas de campos para incluir en la migración."""
    migration_fields = [
        "                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),",
    ]

    for fname, ftype, fargs in field_lines:
        migration_fields.append(f"                ('{fname}', models.{ftype}({fargs})),")

    # Asegurar created_at si no está presente en el modelo
    has_created_at = any(f[0] == "created_at" for f in field_lines)
    if not has_created_at:
        migration_fields.append(
            "                ('created_at', models.DateTimeField(auto_now_add=True)),"
        )

    return migration_fields
