"""
Themer — genera base_html, home_html, detail_html y css a partir del schema dinámico.

Recibe el schema ya validado (site_type, site_title, fields) y genera
templates Django adaptados a los campos reales del dataset.

Variables disponibles en los templates generados:
  home_html:   {{ site.id }}, {{ site.title }}, {{ site.type }}
               {% for it in items %} → it.<key> para cada field del schema
  detail_html: {{ item.<key> }} para cada field del schema
  base_html:   {{ css }}, {{ content }}
"""

from __future__ import annotations

import json
import re

from .client import chat_completion, LLMError
from .llm_utils import parse_llm_json


class ThemeError(Exception):
    pass


# ─────────────────────────── sanitización ────────────────────────────

def _sanitize_template(s: str) -> str:
    """Elimina tags de herencia/includes que romperían el render inline."""
    if not s:
        return ""
    s = re.sub(r"{%\s*extends\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*include\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*load\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*block\s+.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*endblock\s*.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    return s.strip()


def _ensure_base_placeholders(base_html: str) -> str:
    """Garantiza que base_html sea HTML completo con {{ css }} y {{ content }}."""
    s = (base_html or "").strip()
    low = s.lower()

    if "<html" not in low or "<body" not in low:
        return (
            '<!doctype html>\n'
            '<html lang="es">\n'
            '<head>\n'
            '  <meta charset="utf-8">\n'
            '  <meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '  <title>{{ site.title }}</title>\n'
            '  <style>{{ css }}</style>\n'
            '</head>\n'
            '<body>\n'
            '{{ content }}\n'
            '</body>\n'
            '</html>'
        )

    if "{{ css" not in s:
        if "</head>" in low:
            s = re.sub(r"</head>", "<style>{{ css }}</style>\n</head>", s, flags=re.IGNORECASE, count=1)
        else:
            s = "<head><style>{{ css }}</style></head>\n" + s

    if "{{ content" not in s:
        if "</body>" in s.lower():
            s = re.sub(r"</body>", "\n{{ content }}\n</body>", s, flags=re.IGNORECASE, count=1)
        else:
            s += "\n{{ content }}\n"

    if "</body>" not in s.lower():
        s += "\n</body>"
    if "</html>" not in s.lower():
        s += "\n</html>"

    return s


def _validate_home_html(home_html: str) -> bool:
    return bool(re.search(r'\{%\s*for\s+\w+\s+in\s+items', home_html))


# ─────────────────────────── fallback ────────────────────────────────

def _fallback_theme(fields: list[dict]) -> dict:
    """Tema mínimo funcional que siempre funciona si el LLM falla."""
    first_key = fields[0]["key"] if fields else "id"

    detail_rows = "\n".join(
        f'{{% if item.{f["key"]} %}}'
        f'<div class="field-row"><span class="field-label">{f["label"]}</span>'
        f'<span class="field-value">{{{{ item.{f["key"]} }}}}</span></div>'
        f'{{% endif %}}'
        for f in fields
    )

    home_rows = "\n".join(
        f'{{% if it.{f["key"]} %}}'
        f'<div><small>{f["label"]}:</small> {{{{ it.{f["key"]} }}}}</div>'
        f'{{% endif %}}'
        for f in fields[1:5]
    )

    return {
        "base_html": (
            '<!doctype html>\n'
            '<html lang="es">\n'
            '<head>\n'
            '  <meta charset="utf-8">\n'
            '  <meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '  <title>{{ site.title }}</title>\n'
            '  <style>{{ css }}</style>\n'
            '</head>\n'
            '<body>\n'
            '  <main style="max-width:1100px;margin:0 auto;padding:16px;">\n'
            '    {{ content }}\n'
            '  </main>\n'
            '</body>\n'
            '</html>'
        ),
        "home_html": (
            f'<h1>{{{{ site.title }}}}</h1>\n'
            f'<div class="grid">\n'
            f'{{% for it in items %}}\n'
            f'  <div class="card">\n'
            f'    <a href="/edit/{{{{ site.id }}}}/render/{{{{ it.index }}}}/">\n'
            f'      <h2>{{{{ it.{first_key} }}}}</h2>\n'
            f'    </a>\n'
            f'    {home_rows}\n'
            f'  </div>\n'
            f'{{% endfor %}}\n'
            f'</div>'
        ),
        "detail_html": (
            f'<p><a href="/edit/{{{{ site.id }}}}/render/">← Volver</a></p>\n'
            f'<h1>{{{{ item.{first_key} }}}}</h1>\n'
            f'<div class="detail-fields">\n'
            f'{detail_rows}\n'
            f'</div>'
        ),
        "css": (
            '*, *::before, *::after { box-sizing: border-box; }\n'
            'body { font-family: system-ui, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }\n'
            'main { padding: 2rem; }\n'
            'h1 { margin-top: 0; }\n'
            'a { color: #2563eb; text-decoration: none; }\n'
            'a:hover { text-decoration: underline; }\n'
            '.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 1rem; }\n'
            '.card { background: #fff; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,.1); }\n'
            '.card h2 { font-size: 1rem; margin: 0 0 .5rem; }\n'
            '.card small { color: #666; font-size: .8rem; }\n'
            '.detail-fields { display: flex; flex-direction: column; gap: .5rem; margin-top: 1rem; }\n'
            '.field-row { display: flex; gap: 1rem; padding: .4rem 0; border-bottom: 1px solid #eee; }\n'
            '.field-label { font-weight: 600; min-width: 120px; color: #444; }\n'
            '.field-value { color: #222; word-break: break-word; }\n'
        ),
    }


# ─────────────────────────── prompt ──────────────────────────────────

def _build_theme_prompt(
    *,
    site_title: str,
    site_type: str,
    design_hint: str,
    fields: list[dict],
    sample_items: list[dict],
) -> tuple[str, str]:

    system = (
        "Eres un diseñador FRONTEND experto en templates Django. "
        "Devuelve SOLO un objeto JSON válido, sin Markdown ni texto extra. "
        "DEBES usar sintaxis Django pura: {% for %}, {% if %}, {{ variable }}. "
        "NUNCA uses sintaxis Python como items(), item.get(), item['key'] o f-strings."
    )

    field_vars_home = ", ".join(f"it.{f['key']}" for f in fields)
    field_vars_detail = ", ".join(f"item.{f['key']}" for f in fields)

    first_key = fields[0]["key"] if fields else "id"
    example_home_rows = "\n".join(
        f'    {{% if it.{f["key"]} %}}<p><strong>{f["label"]}:</strong> {{{{ it.{f["key"]} }}}}</p>{{% endif %}}'
        for f in fields[1:4]
    )
    example_home = (
        f'<h1>{{{{ site.title }}}}</h1>\n'
        f'<div class="grid">\n'
        f'{{% for it in items %}}\n'
        f'  <div class="card">\n'
        f'    <a href="/edit/{{{{ site.id }}}}/render/{{{{ it.index }}}}/">\n'
        f'      <h2>{{{{ it.{first_key} }}}}</h2>\n'
        f'    </a>\n'
        f'{example_home_rows}\n'
        f'  </div>\n'
        f'{{% endfor %}}\n'
        f'</div>'
    )

    example_detail_rows = "\n".join(
        f'{{% if item.{f["key"]} %}}'
        f'<div class="field"><span class="label">{f["label"]}</span> <span>{{{{ item.{f["key"]} }}}}</span></div>'
        f'{{% endif %}}'
        for f in fields
    )
    example_detail = (
        f'<p><a href="/edit/{{{{ site.id }}}}/render/">← Volver</a></p>\n'
        f'<h1>{{{{ item.{first_key} }}}}</h1>\n'
        f'<div class="fields">\n'
        f'{example_detail_rows}\n'
        f'</div>'
    )

    rules = [
        "Devuelve SOLO JSON válido con 4 keys: base_html, home_html, detail_html, css.",
        "PROHIBIDO: {% extends %}, {% include %}, {% load %}, {% block %}.",
        f"OBLIGATORIO en home_html: usar {{% for it in items %}} ... {{% endfor %}}.",
        f"OBLIGATORIO en home_html: enlace a detalle con /edit/{{{{ site.id }}}}/render/{{{{ it.index }}}}/",
        "OBLIGATORIO en detail_html: enlace de vuelta con /edit/{{ site.id }}/render/",
        f"Variables en items (home): it.index, {field_vars_home}",
        f"Variables en item (detalle): item.index, {field_vars_detail}",
        "base_html debe ser HTML completo (<!doctype html>...) con {{ css }} en <head> y {{ content }} en <body>.",
        "home_html y detail_html son FRAGMENTOS sin <html>/<head>/<body>.",
        "css es CSS puro sin tags <style>.",
        "NUNCA uses sintaxis Python: nada de items(), item.get('x'), item['x'], f-strings.",
        "Diseña pensando en los datos reales. Si hay imágenes, muéstralas. Si hay precios, destácalos. Si hay fechas, fórmalas bien.",
        "El diseño debe ser coherente con el site_type y el hint de diseño.",
        "USA los fields definidos para construir el HTML. No inventes variables que no están en la lista.",
    ]

    fields_info = json.dumps(
        [{"key": f["key"], "label": f["label"]} for f in fields],
        ensure_ascii=False, indent=2
    )

    user_text = "\n".join([
        "HINT DE DISEÑO:",
        (design_hint or "").strip() or "(sin hint: diseño limpio y moderno)",
        "",
        "META DEL SITIO:",
        json.dumps({"title": site_title, "site_type": site_type}, ensure_ascii=False, indent=2),
        "",
        "SCHEMA DE CAMPOS (estos son los únicos campos disponibles en los items):",
        fields_info,
        "",
        "ITEMS DE EJEMPLO (así llegan los datos al template):",
        json.dumps(sample_items[:4], ensure_ascii=False, indent=2),
        "",
        "REGLAS OBLIGATORIAS:",
        "\n".join(f"- {r}" for r in rules),
        "",
        "EJEMPLO DE home_html CORRECTO (adáptalo con tu diseño, NO copies literalmente):",
        example_home,
        "",
        "EJEMPLO DE detail_html CORRECTO (adáptalo con tu diseño, NO copies literalmente):",
        example_detail,
        "",
        "CONTRATO JSON (devuelve EXACTAMENTE estas 4 keys):",
        json.dumps(
            {
                "base_html": "HTML completo con <!doctype html>, <style>{{ css }}</style> y {{ content }}",
                "home_html": f"fragmento con {{% for it in items %}}...{{% endfor %}}",
                "detail_html": "fragmento con los campos del schema",
                "css": "CSS puro sin <style>",
            },
            ensure_ascii=False, indent=2,
        ),
    ])

    return system, user_text


# ─────────────────────────── función pública ─────────────────────────

def generate_site_theme(
    *,
    site_title: str,
    site_type: str,
    design_hint: str,
    fields: list[dict],
    sample_items: list[dict],
    retries: int = 1,
) -> dict:
    """
    Genera base_html, home_html, detail_html y css usando el LLM.

    Recibe el schema dinámico (fields=[{key, label},...]) ya validado.
    Si el LLM falla o devuelve algo inservible, devuelve _fallback_theme(fields).
    """
    system, user_text = _build_theme_prompt(
        site_title=site_title,
        site_type=site_type,
        design_hint=design_hint,
        fields=fields,
        sample_items=sample_items,
    )

    for attempt in range(retries + 1):
        try:
            raw = chat_completion(user_text=user_text, system_text=system, temperature=0.5)
            data = parse_llm_json(raw, exc_class=ThemeError)

            if not isinstance(data, dict):
                raise ThemeError("El JSON no era un objeto.")

            base_html   = _sanitize_template(str(data.get("base_html",   "") or ""))
            home_html   = _sanitize_template(str(data.get("home_html",   "") or ""))
            detail_html = _sanitize_template(str(data.get("detail_html", "") or ""))
            css         = str(data.get("css", "") or "")

            if not base_html or not home_html or not detail_html:
                raise ThemeError("Faltan campos base_html / home_html / detail_html.")

            if not _validate_home_html(home_html):
                raise ThemeError(
                    "home_html no contiene '{% for ... in items %}'. "
                    "El LLM olvidó el bucle de iteración."
                )

            base_html = _ensure_base_placeholders(base_html)

            return {
                "base_html":   base_html,
                "home_html":   home_html,
                "detail_html": detail_html,
                "css":         css,
            }

        except (LLMError, ThemeError, ValueError, json.JSONDecodeError):
            if attempt >= retries:
                return _fallback_theme(fields)

    return _fallback_theme(fields)
