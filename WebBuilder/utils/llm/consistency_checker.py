"""
consistency_checker.py — Valida que los campos usados en views.py y templates
coinciden con los definidos en models.py.
No ejecuta código — solo análisis de texto.
"""
import re


def check_consistency(files: dict[str, str]) -> list[str]:
    """
    Recibe el dict {ruta: contenido} del proyecto generado.
    Devuelve lista de strings con los problemas encontrados.
    Lista vacía = sin problemas detectados.
    """
    errors = []

    # Extraer campos del models.py
    models_code = next((v for k, v in files.items() if k.endswith("models.py")), "")
    model_fields = set(re.findall(r'^\s+(\w+)\s*=\s*models\.', models_code, re.MULTILINE))
    model_fields -= {"created_at", "updated_at", "id"}

    if not model_fields:
        return []

    # Excluir atributos de Django que no son campos del modelo
    django_attrs = {"pk", "__str__", "objects", "save", "delete"}

    # Comprobar views.py
    views_code = next((v for k, v in files.items() if k.endswith("views.py")), "")
    view_refs = re.findall(r'item\.(\w+)', views_code)
    for ref in set(view_refs):
        if ref not in model_fields and ref not in django_attrs:
            errors.append(f"views.py usa item.{ref} pero no existe en models.py")

    # Comprobar templates HTML
    for path, content in files.items():
        if not path.endswith(".html"):
            continue
        template_refs = re.findall(r'item\.(\w+)', content)
        for ref in set(template_refs):
            if ref not in model_fields and ref not in django_attrs:
                errors.append(f"{path} usa item.{ref} pero no existe en models.py")

    return errors