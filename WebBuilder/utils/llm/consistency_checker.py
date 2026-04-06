"""
consistency_checker.py — Valida y corrige los archivos generados por el LLM.

Dos responsabilidades:
  1. check_consistency — detecta campos inválidos en views y templates
  2. fix_template      — limpia el output del LLM antes de guardarlo
"""
import re


def fix_template(html: str) -> str:
    """
    Limpia y corrige el output HTML del LLM antes de guardarlo.
    No llama al LLM — solo correcciones de texto.
    """
    if not html or not html.strip():
        return html

    # 1. Quitar bloques markdown que se cuelen (```html, ```django, ```)
    html = re.sub(r'```[\w]*\n?', '', html)
    html = re.sub(r'```', '', html)

    # 2. Asegurar que {% extends %} está en la primera línea
    #    El LLM a veces mete texto o líneas vacías antes
    if '{% extends' in html and not html.strip().startswith('{% extends'):
        match = re.search(r'\{%\s*extends\s+[\'"][^\'"]+[\'"]\s*%\}', html)
        if match:
            extends_tag = match.group(0)
            html = html[:match.start()].replace(extends_tag, '')
            html = extends_tag + '\n' + html

    # 3. Quitar líneas vacías excesivas (más de 2 seguidas)
    html = re.sub(r'\n{3,}', '\n\n', html)

    # 4. Corregir tags Django sin cerrar: {% endif, {% endfor, {% endblock sin %}
    html = re.sub(r'\{%-?\s*(endif|endfor|endblock|endwith|endblock)\s*\n', r'{% \1 %}\n', html)
    
    return html.strip()


def check_consistency(files: dict[str, str]) -> list[str]:
    """
    Recibe el dict {ruta: contenido} del proyecto generado.
    Devuelve lista de strings con los problemas encontrados.
    Lista vacía = sin problemas detectados.
    """
    errors = []

    # Extraer campos del models.py
    models_code  = next((v for k, v in files.items() if k.endswith("models.py")), "")
    model_fields = set(re.findall(r'^\s+(\w+)\s*=\s*models\.', models_code, re.MULTILINE))
    model_fields -= {"created_at", "updated_at", "id"}

    if not model_fields:
        return []

    # Atributos de Django que no son campos del modelo
    django_attrs = {"pk", "__str__", "objects", "save", "delete"}

    # Comprobar views.py
    views_code = next((v for k, v in files.items() if k.endswith("views.py")), "")
    view_refs   = re.findall(r'item\.(\w+)', views_code)
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