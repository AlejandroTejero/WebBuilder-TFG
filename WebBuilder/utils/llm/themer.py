from __future__ import annotations

import json
import re

from .client import chat_completion, LLMError


class ThemeError(Exception):
    pass


def _strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _extract_json_object(text: str) -> str:
    t = _strip_code_fences(text)
    if t.startswith("{") and t.endswith("}"):
        return t
    start = t.find("{")
    end   = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ThemeError("No se encontró un objeto JSON en la respuesta del LLM.")
    return t[start : end + 1]


def _repair_common_json(text: str) -> str:
    t = text.strip()
    t = re.sub(r",\s*([}\]])", r"\1", t)
    t = t.replace(": True",  ": true")
    t = t.replace(": False", ": false")
    t = t.replace(": None",  ": null")
    return t


def _sanitize_template(s: str) -> str:
    """Elimina tags de herencia/includes que romperían el render inline."""
    if not s:
        return ""
    s = re.sub(r"{%\s*extends\s+.*?%}",  "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*include\s+.*?%}",  "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*load\s+.*?%}",     "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*block\s+.*?%}",    "", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"{%\s*endblock\s*.*?%}", "", s, flags=re.IGNORECASE | re.DOTALL)
    return s.strip()


def _ensure_base_placeholders(base_html: str) -> str:
    """
    Garantiza que base_html sea un documento HTML completo con
    {{ css }} en <head> y {{ content }} en <body>.
    """
    s   = (base_html or "").strip()
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
    """Comprueba que home_html tenga un bucle for sobre items."""
    return bool(re.search(r'\{%\s*for\s+\w+\s+in\s+items', home_html))


def _fallback_theme() -> dict:
    """Tema mínimo funcional que siempre funciona si el LLM falla."""
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
            '<h1>{{ site.title }}</h1>\n'
            '<ul>\n'
            '{% for it in items %}\n'
            '  <li><a href="/sites/{{ site.id }}/item/{{ it.index }}/">{{ it.title }}</a></li>\n'
            '{% endfor %}\n'
            '</ul>'
        ),
        "detail_html": (
            '<p><a href="/sites/{{ site.id }}/">← Volver</a></p>\n'
            '<h1>{{ item.title }}</h1>\n'
            '{% if item.date %}<div>{{ item.date }}</div>{% endif %}\n'
            '{% if item.image %}<div><strong>image:</strong> {{ item.image }}</div>{% endif %}\n'
            '{% if item.content %}<p>{{ item.content }}</p>{% endif %}'
        ),
        "css": (
            '*, *::before, *::after { box-sizing: border-box; }\n'
            'body { font-family: system-ui, sans-serif; margin: 0; padding: 0; }\n'
            'a { color: inherit; }\n'
            'h1 { margin-top: 0; }'
        ),
    }


def generate_site_theme(
    *,
    site_title: str,
    site_type: str,
    design_hint: str,
    pages: list[str],
    mapping: dict,
    sample_items: list[dict],
    retries: int = 1,
) -> dict:
    """
    Genera base_html, home_html, detail_html y css usando el LLM.
    Si el LLM falla o devuelve algo inservible, devuelve _fallback_theme().
    """
    system = (
        "Eres un diseñador FRONTEND experto en templates Django. "
        "Devuelve SOLO un objeto JSON válido, sin Markdown ni texto extra. "
        "DEBES usar sintaxis Django pura: {% for %}, {% if %}, {{ variable }}. "
        "NUNCA uses sintaxis Python como items(), item.get(), item['key'] o f-strings."
    )

    # Ejemplo concreto que el LLM puede copiar y adaptar
    example_home = (
        "<h1>{{ site.title }}</h1>\n"
        "<div class=\"grid\">\n"
        "{% for it in items %}\n"
        "  <div class=\"card\">\n"
        "    <a href=\"/sites/{{ site.id }}/item/{{ it.index }}/\">\n"
        "      <h2>{{ it.title }}</h2>\n"
        "    </a>\n"
        "    {% if it.content %}<p>{{ it.content }}</p>{% endif %}\n"
        "    {% if it.date %}<small>{{ it.date }}</small>{% endif %}\n"
        "  </div>\n"
        "{% endfor %}\n"
        "</div>"
    )

    example_detail = (
        "<p><a href=\"/sites/{{ site.id }}/\">← Volver</a></p>\n"
        "<h1>{{ item.title }}</h1>\n"
        "{% if item.date %}<p><small>{{ item.date }}</small></p>{% endif %}\n"
        "{% if item.image %}<img src=\"{{ item.image }}\" alt=\"{{ item.title }}\">{% endif %}\n"
        "{% if item.content %}<div>{{ item.content }}</div>{% endif %}"
    )

    rules = [
        "Devuelve SOLO JSON válido (un único objeto con 4 keys: base_html, home_html, detail_html, css).",
        "PROHIBIDO: {% extends %}, {% include %}, {% load %}, {% block %}.",
        "OBLIGATORIO en home_html: usar {% for it in items %} ... {% endfor %} para iterar los items.",
        "OBLIGATORIO en home_html: enlace a detalle con /sites/{{ site.id }}/item/{{ it.index }}/",
        "OBLIGATORIO en detail_html: enlace de vuelta con /sites/{{ site.id }}/",
        "Variables en items: it.index, it.title, it.content, it.image, it.date (todos strings).",
        "Variables en item (detalle): item.index, item.title, item.content, item.image, item.date.",
        "base_html debe ser HTML completo (<!doctype html>...) con {{ css }} en <head> y {{ content }} en <body>.",
        "home_html y detail_html son FRAGMENTOS sin <html>/<head>/<body>.",
        "css es CSS puro sin tags <style>.",
        "NUNCA uses sintaxis Python: nada de items(), item.get('x'), item['x'], f-strings.",
    ]

    user_text = "\n".join([
        "HINT DE DISEÑO:",
        (design_hint or "").strip() or "(sin hint: diseño limpio y moderno)",
        "",
        "META DEL SITIO:",
        json.dumps({"title": site_title, "site_type": site_type, "pages": pages}, ensure_ascii=False, indent=2),
        "",
        "MAPPING DE CAMPOS:",
        json.dumps(mapping or {}, ensure_ascii=False, indent=2),
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
                "base_html":   "HTML completo con <!doctype html>, <style>{{ css }}</style> y {{ content }}",
                "home_html":   "fragmento con {% for it in items %}...{% endfor %}",
                "detail_html": "fragmento con {{ item.title }}, {{ item.content }}, etc.",
                "css":         "CSS puro sin <style>",
            },
            ensure_ascii=False,
            indent=2,
        ),
    ])

    last_error = None
    for attempt in range(retries + 1):
        try:
            raw = chat_completion(user_text=user_text, system_text=system, temperature=0.5)

            json_text = _extract_json_object(raw)
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError:
                data = json.loads(_repair_common_json(json_text))

            if not isinstance(data, dict):
                raise ThemeError("El JSON no era un objeto.")

            base_html   = _sanitize_template(str(data.get("base_html",   "") or ""))
            home_html   = _sanitize_template(str(data.get("home_html",   "") or ""))
            detail_html = _sanitize_template(str(data.get("detail_html", "") or ""))
            css         = str(data.get("css", "") or "")

            if not base_html or not home_html or not detail_html:
                raise ThemeError("Faltan campos base_html / home_html / detail_html.")

            # Validar que home_html tiene el bucle for obligatorio
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

        except (LLMError, ThemeError, ValueError, json.JSONDecodeError) as e:
            last_error = f"{type(e).__name__}: {e}"
            if attempt >= retries:
                return _fallback_theme()

    return _fallback_theme()
