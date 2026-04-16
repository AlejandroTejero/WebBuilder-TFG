# Diagnóstico WebBuilder — Revisión de generación LLM

Archivos analizados:
- `utils/llm/consistency_checker.py`
- `utils/llm/examples/catalog.py` (+ `examples/__init__.py` como contexto)
- `utils/generator/project_generator.py`
- `utils/llm/generator_prompts.py`

He leído también, para contrastar, `field_extractor.py`, `enrich_prompt.py`, `llm_wrappers.py`, `fallbacks.py` y `static_files.py`, porque los cuatro archivos principales no se entienden bien sin ellos. El informe está ordenado por severidad, no por archivo: primero los bugs que rompen o degradan resultados reales, luego inconsistencias entre ficheros, y al final mejoras de calidad.

Dentro de cada apartado cada problema tiene: **qué**, **dónde**, **por qué importa**. Nada más. Cuando me ha parecido útil, añado cómo reproducirlo.

---

## 1. BUGS que rompen o degradan la generación

### 1.1 🔴 `\\n` literal en `context_hint` del prompt de template

**Dónde:** `generator_prompts.py`, función `prompt_template`, líneas ~490–507.

**Qué:** En las ramas `is_list` y `else` (home/other), las cadenas que construyen `context_hint` terminan con `\\n` en vez de `\n`:

```python
# is_list  (líneas 491-495)
context_hint = (
    "CONTEXTO: 'page_obj' (queryset paginado de Item), 'site_title' y opcionalmente 'q'.\\n"
    "CRÍTICO: usa SIEMPRE {% for item in page_obj %} para iterar. NUNCA uses 'items'.\\n"
    f"Enlace a detalle: {{% url '{detail_url_name}' item.pk %}}"
)
```

En cambio, la rama `is_detail` usa `\n` correctamente. Es una asimetría clara.

**Por qué importa:** `\\n` dentro de un string literal Python (no raw) es la secuencia de dos caracteres `\` + `n`, no un salto de línea. Al LLM le llega *literalmente* la cadena:

```
CONTEXTO: 'page_obj' (...) y opcionalmente 'q'.\nCRÍTICO: usa SIEMPRE {% for item in page_obj %} (...)\nEnlace a detalle: ...
```

Resultado práctico: las tres instrucciones más críticas para listados y home (incluida "usa SIEMPRE {% for item in page_obj %}" y "NUNCA uses 'items'") se le envían al LLM pegadas en una sola línea con basura visual. El LLM probablemente las sigue entendiendo a nivel semántico, pero pierden todo el énfasis que les da una línea propia, y el prompt se llena de ruido.

Este bug encaja perfectamente con el síntoma que describe el propio sistema de checks: los templates de listado acaban usando `{% for item in items %}` en vez de `page_obj` (hay una regla entera en `check_template_structure` dedicada a detectar eso). Es plausible que parte de ese fallo venga de aquí.

---

### 1.2 🔴 `translate_prompt_to_english` se ejecuta pero el checker lo ignora

**Dónde:** 
- `project_generator.py` línea 90 hace `user_prompt_normalized = translate_prompt_to_english(user_prompt)`. 
- Línea 292 pasa a `run_all_checks` el `user_prompt` **original** (sin traducir).
- `consistency_checker.py` línea 245 tiene los sets `_NEGATION_WORDS = {"without", "no", "avoid", "remove", "eliminate", "none", "don't", "dont", "exclude"}` y el comentario justo encima dice: *"Solo palabras en ingles, ya que se traduce el prompt"*.

**Qué:** El comentario asume que el prompt que llega al checker está en inglés. La realidad es que llega en el idioma original. Si el usuario escribe *"catálogo sin imágenes y sin precios"*, el chequeo de `check_prompt_contradictions` busca `without`, `avoid`, `no`, `image`, `price` y no encuentra nada. El chequeo queda efectivamente muerto para prompts en español.

**Por qué importa:** La mitad de los usuarios escribirán en español (el proyecto es un TFG en español, los prompts de ejemplo están en español, el propio prompt enriquecido está en español). Toda la validación de contradicciones contra el prompt está rota para ellos.

**Extra:** Incluso para prompts ya en inglés, la detección es frágil. `_prompt_bans` hace:

```python
words = set(prompt.lower().split())
```

Con `.split()` sin regex, un prompt como *"no-image listings"* queda como `{'no-image', 'listings'}`; ni `no` ni `image` matchean. Y *"without any prices"* sí funciona, pero *"don't include prices"* no, porque `don't` queda partido de forma extraña dependiendo de la puntuación. El comentario lo predice (`"don't", "dont"`) pero sigue sin cubrir casos reales.

---

### 1.3 🔴 Desalineación entre `name` y `view_name` en los URL patterns

**Dónde:** 
- `static_files.py`, función `build_app_urls`, líneas 315 y 319: `f"path('{url}', views.{view_name}, name='{name}')"`.
- `project_generator.py` línea 174: `real_url_names = {page["name"]: page["view_name"] for page in pages}`.
- `project_generator.py` línea 291: `valid_url_names = set(real_url_names.values()) | {"login", "logout", "register"}`.

**Qué:** Las páginas tienen dos campos: `name` y `view_name`. En `build_app_urls` se registra el patrón con `name=page["name"]`. Pero `real_url_names` es un diccionario cuyas **values** son `view_name`, no `name`. Luego el validador de URLs usa `real_url_names.values()`, es decir los `view_name`s.

**Por qué importa:** Si el LLM generador de estructura devuelve para una página cualquier cosa donde `name != view_name` (por ejemplo `name="home"` y `view_name="home_view"`, o variaciones por typos), entonces:

1. En el urls.py real de la app se registra `name='home'`.
2. Pero `valid_url_names` contiene `'home_view'`.
3. El check `check_django_syntax` valida `{% url 'home' %}` contra `{'home_view', ...}` → marca como inválido un URL que sí existe. **Falso positivo**, y dispara `_regenerate_with_errors` innecesariamente.
4. O al revés: el template usa `{% url 'home_view' %}` pero urls.py solo conoce `'home'` → Django peta en runtime, pero el checker lo da por bueno. **Falso negativo**.

En los ejemplos mostrados al LLM (`prompt_pages_structure`, líneas 180–207) `name` y `view_name` coinciden siempre, así que el modelo probablemente los iguala casi siempre. Pero cuando no coincidan (cualquier página extra con nombre un poco distinto, cualquier mutación creativa del LLM), el sistema produce errores fantasma o errores escondidos.

También afecta a los prompts: `prompt_template` construye las URLs que presenta al LLM usando `view_name` (línea 549 `url_rules += f"  - {{% url '{view_name}' %}}\n"`), pero esas URL names solo existen en el `path()` generado si `view_name == name`. Coherencia cero.

**Decisión de diseño pendiente:** ¿`name` y `view_name` son de verdad conceptos distintos, o son un duplicado histórico? Si son lo mismo, sobra uno.

---

### 1.4 🟠 `prompt_template` durante el retry se llama sin `design_system`

**Dónde:** `project_generator.py`, función `_regenerate_with_errors`, líneas 385–395.

**Qué:** La primera llamada a `prompt_template` (línea 197) pasa `design_system=design_system`. La segunda llamada, en el retry, **no** lo pasa:

```python
system, user_text = prompt_template(
    page=page,
    fields=fields,
    sample_items=sample_items,
    site_type=site_type,
    site_title=site_title,
    user_prompt=user_prompt,
    all_pages=pages,
    real_fields=real_fields,
    real_url_names=real_url_names,
)   # <-- falta design_system
```

**Por qué importa:** `prompt_template` considera el design system *"CRÍTICO ABSOLUTO"* (línea 527 del prompt: *"el SISTEMA DE CLASES proporcionado arriba es OBLIGATORIO. Para cada elemento debes usar EXACTAMENTE las clases indicadas"*). En el retry desaparece. Resultado: el template regenerado usa clases Tailwind arbitrarias que **ya no son coherentes con base.html ni con el resto de templates**. Y lo irónico es que se regenera precisamente porque el primer intento tenía errores; el segundo intento se hace con menos contexto.

Lo mismo se podría aplicar a views.py retry (no necesita design_system, ok, eso está bien), pero en templates es un agujero claro.

---

### 1.5 🟠 `time.sleep(20)` bloqueante antes de cada llamada al LLM

**Dónde:** `llm_wrappers.py` línea 25, dentro de `llm_call`.

**Qué:** Cada llamada al LLM duerme 20 segundos antes de ejecutarse.

**Por qué importa:** Una generación típica hace:
- 1 llamada para pages_structure
- 1 para design_system
- 1 para models
- 1 para views
- 1 para base.html
- 3+ para templates (home + list + detail, mínimo)
- 1 para load_data
- Posible traducción del prompt (1 llamada extra)
- Posible retry de views y retry de cada template con errores

Son **10+ llamadas mínimo**. 10 × 20s = **200 segundos solo de sleep**, sin contar el tiempo real de inferencia del LLM ni los retries. En un TFG esto probablemente se añadió para esquivar rate limits del proveedor, pero así es completamente bloqueante y sin adaptarse: duerme aunque sea la primera llamada del día, duerme aunque la API no esté rate-limitada, duerme aunque falle. Además, lo hace **antes** de la request, no después, así que si una llamada falla inmediatamente por otro motivo (400, clave inválida...), aún así ha esperado 20 segundos.

Es un comentario de performance más que un bug funcional, pero para un TFG donde el usuario está mirando una pantalla de "generando...", son 3+ minutos de latencia artificial mínima.

---

### 1.6 🟠 `fix_template` regex frágiles y aplicadas al ciego

**Dónde:** `consistency_checker.py` líneas 87–94.

**Qué:**

1. **Extends movido "al primer sitio" rompe orden:**

```python
if '{% extends' in html and not html.strip().startswith('{% extends'):
    match = re.search(r'\{%\s*extends\s+[\'"][^\'"]+[\'"]\s*%\}', html)
    if match:
        extends_tag = match.group(0)
        html = extends_tag + '\n' + html[:match.start()] + html[match.end():]
```

Si el LLM devuelve:

```
{% load static %}
{% extends 'base.html' %}
{% block content %}...{% endblock %}
```

Después del fix queda:

```
{% extends 'base.html' %}
{% load static %}
{% block content %}...{% endblock %}
```

Eso parece correcto, pero **pierde cualquier comentario o estructura previa**. Más importante: si había **dos** `{% extends %}` por error (cosa rara pero posible en outputs de LLM), solo mueve el primero, dejando el segundo duplicado. El regex `re.search` solo captura el primero.

2. **Regex de cierres incompletos es incorrecto:**

```python
html = re.sub(r'\{%-?\s*(endif|endfor|endblock|endwith)\s*\n', r'{% \1 %}\n', html)
```

Esta línea intenta reparar un `{% endif` sin cerrar el `%}`. Pero:

   - El patrón requiere `\n` al final, así que un `{% endif` al final del archivo sin newline no se arregla.
   - Si ya estaba bien escrito `{% endif %}`, no matchea (porque el `%}` rompe el patrón antes del `\n`), así que no duplica, bien.
   - Pero si el LLM devuelve `{% endif }` (tag abierto con `}` solo), tampoco lo arregla.
   - Más grave: `{%-\s*endif\s*\n` también matchea el caso `{%- endif` (con guión, que es trim de whitespace en Django), y lo reemplaza por `{% endif %}` sin el guión, perdiendo intención. Poco probable pero posible.

3. **Orden de limpieza:** el paso de quitar fences Markdown (`html = re.sub(r'```[\w]*\n?', '', html)`) se aplica antes del extends-shuffle. Si el LLM devolvió el HTML envuelto en ```html ... ``` con un comentario antes, el resultado del fix depende del orden, y puede dejar líneas huérfanas.

**Por qué importa:** `fix_template` se aplica a **todo** template guardado en el proyecto final. Un fallo silencioso aquí se propaga a todos los artefactos. Las regex son razonables para el caso normal pero frágiles en los bordes.

---

### 1.7 🟠 Catalog examples contradicen las reglas que el propio prompt exige

**Dónde:** `examples/catalog.py` (todas las variantes HOME), en contraste con `generator_prompts.py` línea 505 (`"CRÍTICO: usa SIEMPRE {% for item in featured %} para iterar los destacados. NUNCA uses 'items'"`).

**Qué:** El prompt le pide al LLM, cuando la página es "home/other", que use `{% for item in featured %}`. Pero los ejemplos de home (`CATALOG_HOME_DARK`, `CATALOG_HOME_LIGHT`, `CATALOG_HOME_EDITORIAL`) usan:

```django
{% for item in items|slice:":6" %}
```

Es decir, iteran `items`, justo la variable que el prompt prohíbe usar. Y lo hacen siempre, los tres estilos.

Estos ejemplos se inyectan al LLM al final del user_text como *"EJEMPLO DE REFERENCIA (inspiración estructural y visual secundaria — adapta los campos reales y NO contradigas el prompt del usuario; NO copies esto tal cual)"*. Suena bien, pero en la práctica los LLMs imitan muy bien lo que ven, especialmente en templates HTML donde el patrón estructural es fuerte.

**Por qué importa:** Hay un tira y afloja activo entre:
- La regla del prompt: `{% for item in featured %}`
- El ejemplo mostrado: `{% for item in items|slice:":6" %}`

El LLM tiene que elegir y va a tender a copiar el ejemplo. Esto hace que `views.py` pase `featured` al contexto (como dice el prompt, línea 319), pero la home-template itere `items`, que no existe en el contexto → la página queda vacía sin error visible, porque Django con template debug OFF simplemente no renderiza las iteraciones vacías.

Lo mismo pasa con las **páginas de listado**: los ejemplos (CATALOG_LIST_DARK, LIGHT, EDITORIAL) usan `{% for item in items %}`, mientras el prompt (línea 316) dice `"Pasar SOLO 'page_obj' al contexto. NUNCA uses 'items'"` y el check `check_template_structure` (línea 228) busca literalmente ese antipatrón para marcarlo como error.

Conclusión: **los ejemplos son el error** que el resto del sistema está intentando corregir. Sería más coherente que los ejemplos ya usen `page_obj` en listados y `featured` en home.

---

### 1.8 🟠 El LLM nunca ve el ejemplo completo (corte a 1500 chars)

**Dónde:** `generator_prompts.py` línea 622: `example_html = example_html[:1500]`.

**Qué:** Los templates de ejemplo en `catalog.py` oscilan entre **3000 y 6000 caracteres**. El corte duro a 1500 corta sistemáticamente por la mitad del template de ejemplo (normalmente justo dentro del primer `{% for %}`).

**Por qué importa:** El LLM recibe un ejemplo que ni siquiera cierra sus propios `{% endfor %}` ni `{% endblock %}`. Ese corte es invisible para el LLM, que puede replicar la estructura rota como si fuera el patrón deseado. Si se quiere limitar la longitud, lo mínimo sería cortar en un punto seguro (final de un bloque) o reducir directamente los ejemplos para que quepan enteros.

Además, si el objetivo del corte era ahorrar tokens, 1500 caracteres ≈ 400 tokens. En un prompt que ya incluye `priority_rules_text`, `_GLOBAL_STYLE_RULES`, `theme_rules_text`, `design_system_text`, `rules` (15+ reglas), `_fields_info`, `_samples_info`, `page_requirements`, `tailwind_guidance` y `nav_links`... ahorrar 400 tokens recortando el único ejemplo concreto del prompt es un mal trade-off.

---

## 2. INCONSISTENCIAS entre archivos

### 2.1 🟠 `extract_model_fields` duplicado e incoherente

**Dónde:**
- `field_extractor.py` define `extract_model_fields` (pública) que devuelve `list[str]` y excluye `{'created_at', 'updated_at', 'id', 'pk'}`.
- `consistency_checker.py` define `_extract_model_fields` (privada) que devuelve `set[str]` y excluye solo `{"created_at", "updated_at", "id"}` (sin `pk`).

**Por qué importa:**
1. Duplicación obvia: misma regex, misma responsabilidad.
2. El checker no filtra `pk`, pero `pk` sí se excluye en `field_extractor`. Los chequeos pueden aceptar una referencia `item.pk` como válida (bien, ya está en `_DJANGO_ATTRS`), pero si un modelo define `pk = ...` explícitamente (raro, pero posible), entran por caminos distintos.
3. `set` vs `list` obliga a convertir en los usos. En `project_generator.py` los `real_fields` se obtienen de `field_extractor` (list) y se pasan al prompt como string. Si en el checker se comparan con un set distinto, una divergencia futura entre ambas funciones crea bugs difíciles de encontrar.

---

### 2.2 🟠 El checker entiende solo un subset de las estructuras que el propio proyecto genera

**Dónde:** `consistency_checker.py`, `check_template_structure`, líneas 223–234.

**Qué:** El checker valida que páginas de listado tengan **alguna** de estas iteraciones:

```python
has_valid_loop = (
    "{% for item in page_obj %}" in content_normalized
    or "{% for item in featured %}" in content_normalized
)
```

Pero:

- Los fallbacks (`fallbacks.py` líneas 128–140 en `fallback_template` para `is_list`) generan `{% for item in items %}`. Si el LLM falla y se cae al fallback, el template fallback **falla el check**, se marca como error, se dispara regeneración con el LLM... que ya había fallado. Loop con humo.
- El `fallback_views` (línea 90) para páginas "other" pasa `items` al contexto, no `featured`. Así que si todo el paso 3 (views) se cae al fallback y el paso 5 (templates) se cae al fallback, la variable coincide (ambos usan `items`). Pero si una parte va por LLM y la otra por fallback, las variables no casan.

Es un acoplamiento débil muy peligroso: el checker, las reglas del prompt, los ejemplos y los fallbacks hablan lenguajes distintos sobre una misma decisión (cómo se llama la variable de contexto).

**Mapa rápido de la inconsistencia:**

| Componente | List page usa... | Home page usa... |
|---|---|---|
| Prompt views (regla) | `page_obj` | `featured` |
| Prompt template (regla) | `page_obj` | `featured` |
| Fallback views | `page_obj` | `items` |
| Fallback template | `items` | (n/a directamente) |
| Ejemplos catalog.py | `items` | `items|slice:":6"` |
| Checker acepta | `page_obj` o `featured` | (no chequea home) |

---

### 2.3 🟡 Los HEX arbitrarios de Tailwind chocan con la "lista negra" del checker

**Dónde:** 
- `consistency_checker.py` `_INVALID_TAILWIND_PATTERNS` prohíbe `bg-#xxxxxx`, `text-#xxxxxx`, etc.
- `prompt_design_system` (`generator_prompts.py` línea 789) enseña al LLM a usar valores arbitrarios como `bg-[#111111]`.
- El fallback del design system (`llm_wrappers.py`) no usa HEX, pero el prompt genera ejemplos que sí.

**Qué:** Las reglas del checker buscan exactamente `bg-#...` (HEX sin corchetes, la forma **inválida**). Los ejemplos del prompt usan `bg-[#...]` (HEX entre corchetes, la forma **válida** en Tailwind CDN). Eso está bien, las dos cosas no chocan directamente.

**El problema real:** un LLM que copie mal el ejemplo y genere `bg-#10b981` (sin corchetes) caerá en el patrón inválido correctamente. Pero **el mismo LLM que genere `bg-[#10b981]` estará bien**, y la forma arbitraria de Tailwind no se valida mucho más allá de la regex HEX. Un invento como `bg-[10b981]` (sin `#`) o `bg-[rgb(16,185,129)]` no se detecta. Es un problema menor, pero el checker es más permisivo de lo que parece en colores arbitrarios.

---

### 2.4 🟡 El checker permite `{% extends "base.html" %}` (dobles comillas) pero el fix_template asume single quote en otros sitios

**Dónde:** `consistency_checker.py` líneas 215–218. El check acepta tanto `'base.html'` como `"base.html"`. Pero el fallback (`fallbacks.py` línea 129) siempre usa `'base.html'`, y todos los ejemplos de `catalog.py` también `'base.html'`. Los prompts (línea 516) le dicen al LLM que empiece con `{% extends 'base.html' %}` (single quote).

No es un bug, es ruido: cinco sitios hablando con convenciones distintas que el checker acomoda, pero si un día alguien cambia el checker a solo aceptar single quote se rompen casos ya generados. Menor.

---

### 2.5 🟡 `run_all_checks` no sabe qué severidad tiene cada issue

**Dónde:** `consistency_checker.py` línea 309. `project_generator.py` línea 294.

**Qué:** `run_all_checks` devuelve `list[str]`. El generator dispara retry si hay *cualquier* cosa en la lista. Eso mete en el mismo saco:

- "views.py usa item.XXX pero no existe en models.py" (crítico real, el código no arrancará)
- "home.html: el prompt pide grid de 4 columnas, pero no se detecta una clase clara de 4 columnas" (puro aviso de calidad, no rompe nada)
- "home.html: falta {% block content %}" (rompe renderizado)
- "home.html: página de listado sin {% empty %}" (degrada UX, no rompe)

Un issue "decorativo" dispara una llamada LLM completa para regenerar un template. Esto multiplica el coste sin criterio. Sería razonable clasificar issues en al menos dos niveles (blocking vs warning) y que solo los blocking disparen retry.

---

### 2.6 🟡 El mapping `real_url_names` no incluye `login`, `logout`, `register` al prompt, pero sí al validador

**Dónde:** 
- `project_generator.py` línea 291: `valid_url_names = set(real_url_names.values()) | {"login", "logout", "register"}`.
- `generator_prompts.py` línea 547: el prompt que ve el LLM para generar templates solo enumera `real_url_names.items()`.

**Qué:** El LLM recibe una lista de URLs "válidas" sin incluir login/logout/register. Pero base.html (bien generado) sí usará `{% url 'logout' %}` porque el `_AUTH_BLOCK` lo exige (línea 119–128 del prompt). Si el LLM generando un template de página quiere por su cuenta enlazar al login (ej. "Inicia sesión para valorar este producto"), no tiene pista alguna de que `'login'` sea una URL válida en el proyecto.

Menor, pero es una asimetría real entre lo que el LLM "sabe" y lo que el checker acepta.

---

### 2.7 🟡 Prompt mezclado español/inglés

**Dónde:** `project_generator.py` línea 90 traduce a inglés, `enrich_user_prompt` vuelve a concatenar texto en español (_field_context, _dataset_hints, _default_style_for_site_type todos en español), y luego los prompts de `generator_prompts.py` también están en español.

**Qué:** Resultado final del prompt al LLM: mezcla de
- Instrucción del usuario traducida a inglés.
- Contexto del dataset en español ("Tipo de sitio", "Campos del dataset con valores reales", "Sugerencias basadas en el dataset").
- Reglas técnicas en español ("REGLAS DE PRIORIDAD", "CRÍTICO", "PROHIBIDO").

**Por qué importa:** Mezclar idiomas en el mismo prompt reduce la calidad de la salida. El LLM responde típicamente en el idioma predominante, pero también puede confundirse sobre qué tono usar para los textos generados (strings visibles en la UI). Por ejemplo, la página puede acabar con títulos en inglés ("Featured products") aunque el usuario quería el sitio en español, o al revés. No es un bug determinista, es ruido estocástico que baja calidad.

La traducción a inglés tiene sentido si el objetivo era simplificar los chequeos en `check_prompt_contradictions` (que ya vimos que usa palabras en inglés). Pero como ese chequeo recibe el prompt *original* sin traducir, la traducción acaba no sirviendo para nada útil y solo introduce el problema.

---

## 3. Oportunidades de mejora en calidad de generación

### 3.1 🟡 Diagnóstico simultáneo en `_regenerate_with_errors`: se regenera views **Y** templates, pero los templates vieron el views viejo

**Dónde:** `project_generator.py`, función `_regenerate_with_errors`.

**Qué:** Si views.py falla (referencia a un campo que no existe), se regenera. Si algún template falla, se regenera. Pero el template se regenera con **el mismo contexto que antes**, incluyendo `real_fields` correcto, pero sin información de que las views han cambiado también.

No es grave porque los templates no dependen de las views en sí (dependen de `real_fields` y `real_url_names`, que son estables), pero si en el futuro se añaden otros artefactos que sí dependen (por ejemplo, context_processors, middlewares generados por LLM), esta arquitectura secuencial "views primero, después cada template" puede empezar a producir desalineaciones.

También: el retry solo se ejecuta **una vez**. Si el segundo intento también tiene errores, se guardan tal cual sin volver a comprobarlos. Sería razonable al menos volver a pasar `run_all_checks` después del retry y loguear qué quedó sin arreglar.

---

### 3.2 🟡 `check_tailwind_validity` tiene falsos positivos probables

**Dónde:** `consistency_checker.py` líneas 32–40, `_INVENTED_CLASS_PATTERNS`.

**Qué:** Los patrones son:

```python
r'\b\w+_base\b',       # card_base, input_base, button_base...
r'\b\w+_soft\b',       # card_soft...
r'\b\w+_dark\b',       # muted_text_dark...
r'\b\w+_medium\b',     # title_medium...
r'\b\w+_strong\b',     # title_strong...
r'\bcontainer_\w+\b',  # container_base, container_narrow...
r'\bsection_\w+\b',    # section_spacing...
```

Estos patrones matchean **cualquier palabra** que termine en esos sufijos. Problemas:

1. `font_medium` no es una clase Tailwind (sería `font-medium` con guión), pero el regex `\w+_medium` matchea. Si un LLM, por error, usa `font_medium`, se detecta correctamente. Ok.
2. Pero `_dark` matchea también construcciones válidas que alguien pueda hacer en JavaScript dentro del mismo archivo HTML. Por ejemplo: `<script>const theme_dark = true;</script>` embebido → el regex busca dentro de atributos `class=`, así que este caso no se toca... pero solo porque el filtro superior extrae `class_attrs` primero. El patrón `r'\bcontainer_\w+\b'` tampoco restringe, y capturaría `container_id` o `container_name` si alguna vez aparecen dentro del class string (difícil pero posible con atributos HTML mezclados).
3. `section_spacing` y similares: el patrón `\bsection_\w+\b` matchearía también nombres de variables o data-attributes que contengan `section_`.

Los chequeos de clases CSS inventadas son útiles, pero la implementación actual está pensada para catchear casos muy concretos y genera ruido. Una lista explícita de "palabras prohibidas exactas" sería más predecible.

---

### 3.3 🟡 Duplicación de ~30 líneas de `design_system_text`

**Dónde:** `generator_prompts.py` líneas 388–409 (prompt_base_template) y 556–577 (prompt_template). Código idéntico.

**Qué:** El mismo bloque (cabecera + labels + loop que construye el texto del design system) está copy-pasted en los dos prompts. Cualquier cambio (añadir un nuevo key, cambiar un label) hay que hacerlo en los dos sitios, con el riesgo habitual de desincronización.

**Extra:** El dict `labels` es un dict Python ordenado en 3.7+, así que los labels salen en el orden declarado. Eso está bien para consistencia. Pero la comprobación `if key in design_system:` se hace por cada key esperada, aunque `design_system` siempre tiene todas las keys porque `llm_design_system_call` rellena las faltantes con el fallback. Ese `if` es redundante. Menor.

---

### 3.4 🟡 Los ejemplos de `catalog.py` están en español pero el prompt ya tradujo el prompt del usuario a inglés

**Dónde:** `examples/catalog.py`, todas las cadenas del ejemplo ("Colección destacada", "Explora una selección visual...", "Ver listado completo", etc.).

**Qué:** El LLM recibe:
- Instrucción del usuario en inglés (traducida)
- Ejemplo de referencia con textos hardcodeados en español

**Por qué importa:** Si el usuario pide *"a dark catalog site for my vinyl collection"*, el ejemplo HTML que se le muestra al LLM contiene *"Colección destacada"*, *"Ver listado completo"*, *"Explora una selección visual de contenidos..."*. El LLM puede interpretar que esos textos son parte del estilo pedido, y generar titulares en español en un sitio que pidieron en inglés. O al revés: usuario en español pide sitio, el prompt se traduce a inglés, y el LLM decide que el sitio va en inglés "porque el prompt está en inglés" pero el ejemplo está en español.

Es un vector de inconsistencia más del problema 2.7.

---

### 3.5 🟡 El checker no valida que `{% url %}` con pk pasa un pk válido

**Dónde:** `consistency_checker.py` `check_django_syntax`, línea 159.

**Qué:** El regex captura `{% url 'name' %}` pero acepta cualquier contenido después del nombre. Un template que genere `{% url 'detail' item.id %}` en vez de `{% url 'detail' item.pk %}` pasa el check. Pero `item.id` y `item.pk` son equivalentes en Django solo si no hay PK explícita, y ambos existen como atributos, pero la consistencia del prompt sí pide `item.pk` (línea 494 de `generator_prompts.py`). No es un bug funcional grave, pero es un hueco en la validación.

Más grave: si el template usa `{% url 'detail' %}` sin pasar el pk (muy fácil de equivocar para el LLM en una home con `featured`), Django peta en render con NoReverseMatch, y el check no lo captura.

---

### 3.6 🟡 `check_consistency` solo revisa `item.xxx`, nada más

**Dónde:** `consistency_checker.py` líneas 118–119 y 126.

**Qué:** Las referencias que valida son:

```python
view_refs = re.findall(r'item\.(\w+)', views_code)
filter_refs = re.findall(r'\.filter\([^)]*?(\w+)__', views_code)
```

Y en templates:

```python
template_refs = re.findall(r'item\.(\w+)', content)
```

No cubre:
- `{{ obj.xxx }}` si el LLM usa `obj` (porque usó DetailView mal adaptado). Aunque el prompt prohíbe CBV, un LLM podría colar `obj`.
- `{% for x in page_obj %}{{ x.xxx }}{% endfor %}` donde `x` no es `item`. Si el LLM respeta `page_obj` pero renombra la variable del for, los atributos no se validan.
- `related.xxx` en detail (el prompt define `related` como `Item.objects.exclude(...)[:3]`, así que `{% for r in related %}{{ r.xxx }}{% endfor %}` no se valida).
- `featured.xxx` análogo.

Es decir, el checker solo valida templates que **siguen exactamente el patrón `item.xxx`**. Cualquier iteración con variable renombrada queda fuera de validación, y justo las páginas de home (que iteran `featured`) y de detail (que iteran `related`) caen en ese hueco.

---

### 3.7 🟡 Los ejemplos de `catalog.py` tienen paginación incompleta

**Dónde:** `examples/catalog.py`, `CATALOG_LIST_*` (dark, light, editorial), bloques `<nav aria-label="Paginación">`.

**Qué:** La paginación en los ejemplos de lista solo muestra anterior/siguiente + "Página X de Y", sin selector de número de página. Para datasets medianos-grandes (>5 páginas) esto es fricción pura. No es un bug, es falta de profundidad en los templates de referencia. Un usuario generando un catálogo con 100 items (~9 páginas paginando de 12 en 12) va a tener que pinchar "Siguiente" 8 veces.

Además, los ejemplos no incluyen los otros parámetros del querystring al cambiar de página: si hay búsqueda activa (`q`), los links `?page=N` pierden el `q`. Resultado: cualquier búsqueda se resetea al paginar.

---

### 3.8 🟡 El prompt "No uses JSONField" es una regla correcta pero frágil

**Dónde:** `generator_prompts.py` línea 275: `"NUNCA uses JSONField para ningún campo."`.

**Qué:** La regla existe porque PostgreSQL JSONField requiere un backend específico y el proyecto usa SQLite (`db.sqlite3`). Tiene sentido. Pero:

1. No hay ningún check que lo valide. Si el LLM lo ignora (raro pero posible), el modelo generado pasa el pipeline y peta al hacer `makemigrations` o `migrate`.
2. No hay check equivalente para otros campos sensibles (ArrayField, HStoreField), que caerían igual.

Una validación simple (`if "JSONField" in models_code: flag_error`) sería una mejora trivial.

---

### 3.9 🟡 `check_prompt_contradictions` para grid de 4 columnas es muy específico

**Dónde:** `consistency_checker.py` líneas 268–272 y 288–298.

**Qué:**

```python
prompt_wants_four_cols = (
    "4 columnas" in prompt
    or "cuatro columnas" in prompt
    or "grid de 4 columnas" in prompt
)
```

Esta detección es en español, pero el prompt que llega al checker es el `user_prompt` original (que **puede** estar traducido si la traducción funcionó, o no). Además, no cubre "4 cols", "cuatro cols", "4-column grid", "4 col layout" etc.

Y el chequeo contra el HTML:

```python
has_four_col_hint = any(
    token in content
    for token in ["lg:grid-cols-4", "xl:grid-cols-4", "grid-cols-4"]
)
```

Le pide al template **exactamente** esas clases. Pero un diseño con 4 columnas también se puede hacer con `grid-cols-[repeat(4,minmax(0,1fr))]` o con flex. La detección está anclada a una implementación.

No es que esté mal, es que es un chequeo muy específico que no generaliza a otros casos similares ("5 columnas", "3 columnas") y no está documentado por qué solo se chequean 4.

---

### 3.10 🟡 `_GLOBAL_STYLE_RULES` y `_PRIORITY_RULES` se repiten mucho en cada prompt

**Dónde:** `generator_prompts.py`, líneas 159–165 y 110–117. Se usan en `prompt_pages_structure`, `prompt_views`, `prompt_base_template`, `prompt_template`, `prompt_load_data` (este último solo priority_rules).

**Qué:** Las mismas 5 reglas globales se envían al LLM en cada una de las 6–8 llamadas. Los proveedores cobran por token de input, y un prompt de template ya es grande. Revisar si estas reglas realmente cambian la salida del LLM para etapas donde no aplican (ej. `prompt_models` no parece necesitar `_GLOBAL_STYLE_RULES` porque es código Python sin estilo visual; sin embargo se usa `priority_rules_text` que incluye "1. La instrucción explícita del usuario tiene prioridad absoluta"... para generar models.py, donde la instrucción del usuario sobre estética es irrelevante).

Posible mejora: tener prompts segregados por tipo (técnico vs visual) y no enviar reglas de estilo a prompts que generan lógica.

---

### 3.11 🟡 Comentario `{# campo título principal #}` se queda en el HTML final

**Dónde:** `examples/catalog.py`, por todas partes (`{{ item.CAMPO_TITULO }} {# campo título principal #}`).

**Qué:** Los ejemplos usan placeholders como `CAMPO_TITULO`, `CAMPO_DESCRIPCION`, acompañados de comentarios Django `{# ... #}` explicando qué son. El prompt le dice al LLM: *"adapta los campos reales y NO contradigas el prompt del usuario; NO copies esto tal cual"*.

**Por qué importa:** En la práctica, los LLMs que imitan estructura visual tienden a mantener los comentarios `{# campo título principal #}` en el output generado, o reemplazan `CAMPO_TITULO` por un campo real pero dejan el comentario. Django ignora `{# ... #}` al renderizar, así que no rompe nada visualmente, pero el HTML fuente queda con comentarios basura que denotan que los templates fueron generados con un ejemplo de referencia. Poco profesional para un sitio generado.

Además el comentario no se puede deshabilitar, porque `{# ... #}` solo funciona en una línea. Si el LLM lo arrastra a una línea con el template tag `{{ ... }}`, queda `{{ item.title }} {# campo título principal #}` y el espacio extra se renderiza.

---

### 3.12 🟡 `strip_markdown_fences` puede eliminar código válido

**Dónde:** `llm_wrappers.py` líneas 83–102.

**Qué:** La función primero busca un bloque completo ` ```...``` ` con DOTALL y extrae el interior. Si no lo encuentra, elimina cualquier línea que sea solo ` ``` `. Luego elimina líneas finales con `EOF`, `# end`, etc.

Problema: el primer regex `r"```(?:\w+)?\n(.*?)```"` es *non-greedy*, así que si el LLM (por error) devolvió *dos* bloques de código por alguna razón, solo se captura el primero y el segundo se descarta. Y el segundo podría ser código válido.

Además, `re.DOTALL` con `.*?` y `\n` al inicio exige que el bloque tenga al menos una línea interior. Un ` ```{espacio}{espacio}``` ` sin saltos no matchea, y cae al segundo camino de "eliminar líneas que sean solo fences", que es más laxo.

Menor, pero no es bulletproof ante outputs extraños del LLM.

---

### 3.13 🟡 `check_django_syntax` no cierra todos los tags de bloque

**Dónde:** `consistency_checker.py` líneas 140–153.

**Qué:** Chequea balanceo de `{% for %}/{% endfor %}`, `{% if %}/{% endif %}`, `{% block %}/{% endblock %}`. Pero no chequea:

- `{% with %} / {% endwith %}` (el `fix_template` sí menciona `endwith` en el regex de reparación)
- `{% comment %} / {% endcomment %}`
- `{% verbatim %} / {% endverbatim %}`
- `{% spaceless %} / {% endspaceless %}`
- `{% autoescape %} / {% endautoescape %}`

Más impactante: no chequea `{% else %}` dentro de `{% if %}`. Si el LLM genera un if mal formado con `{% else %}` sin `{% endif %}` final, el contador de if/endif lo pilla (bien), pero si genera `{% elif %}` en vez de `{% elif %}` (que no existe en Django, lo correcto es `{% elif ... %}` dentro de un if... espera, sí existe), puede pasar.

Lo principal: sí chequea los tres pares más comunes. Es una limitación conocida, no un bug.

---

### 3.14 🟡 `_detect_style` en `examples/__init__.py` es heurística muy simple

**Dónde:** `examples/__init__.py` líneas 30–38.

**Qué:**

```python
def _detect_style(user_prompt: str) -> str:
    words = set(user_prompt.lower().split())
    if words & _EDITORIAL_WORDS:
        return "editorial"
    if words & _LIGHT_WORDS:
        return "light"
    if words & _DARK_WORDS:
        return "dark"
    return "light"
```

Problemas:

1. `.split()` sin más parte por whitespace. "dark-themed" queda como `{"dark-themed"}`, que no matchea con `"dark"` en `_DARK_WORDS`. Same for `night-mode`, `ultra-dark`, etc.
2. Si el prompt tiene palabras de dos grupos ("clean dark UI"), gana `editorial` (no hay editorial aquí), luego `light` (contiene "clean" → match), aunque el prompt claramente pide "dark". Orden arbitrario de evaluación.
3. No pesa por número de matches ni por posición. "I hate dark mode, give me a clean white design" clasifica como `editorial` si contiene "clean"... no, `_LIGHT_WORDS` contiene `clean`, así que `light` gana. Vale. Pero el prompt literal dice "dark", que aparece, y no se considera. Depende del orden.
4. El default si no hay match es `"light"`, lo cual es una decisión opinionada. Si alguien pide "funky gradient site", no hay match → default light. Puede no ser lo que quiere.
5. Las palabras no están en español. Un prompt en español puro no detectará ningún estilo.

Esta función decide qué de los 9 ejemplos se muestra al LLM. Es el único sitio donde se usa el estilo. Afinar esto tendría impacto alto en la calidad del output.

---

### 3.15 🟢 (Observación) Faltan tests

Los cuatro archivos principales son puramente algorítmicos: transformaciones de strings, balanceo de tags, construcción de prompts con plantillas. Son perfectos para tests unitarios. `test.py` existe y está vacío. Los chequeos de `consistency_checker.py` en particular son casos de escuela para TDD: para cada regla, un test positivo (detecta el problema), un test negativo (no falsea).

Sin tests, cada uno de los bugs de arriba se podría haber detectado sin tocar la infraestructura. Más importante en un TFG: tests son un entregable muy vendible.

---

### 3.16 🟢 (Observación) `logger.info` con datos potencialmente sensibles

**Dónde:** `project_generator.py` línea 151 (`logger.info("[generator] Campos reales extraídos: %s", real_fields)`), línea 175 (`logger.info("[generator] URLs reales: %s", real_url_names)`), línea 133 (`logger.info("[generator] Design system: %s", design_system)`).

Para un TFG no es un problema, pero loggear design systems completos y estructuras de páginas en INFO puede llenar logs muy rápido y, si el sistema se despliega, filtrar información sobre los datasets de los usuarios. Considerar mover a DEBUG o truncar.

---

## 4. Resumen por archivo

### `consistency_checker.py`
- 🔴 El detector de contradicciones del prompt solo funciona en inglés, pero recibe el prompt sin traducir (1.2).
- 🟠 `fix_template` tiene regex frágiles que pueden reordenar incorrectamente (1.6).
- 🟠 `check_template_structure` solo acepta `page_obj`/`featured`; incompatible con fallbacks y ejemplos que usan `items` (2.2).
- 🟡 `_extract_model_fields` duplica lógica con `field_extractor.py` (2.1).
- 🟡 Detección de clases inventadas con regex generales, propensos a falsos positivos (3.2).
- 🟡 `check_consistency` solo cubre `item.xxx`, deja `featured` y `related` sin validar (3.6).
- 🟡 `run_all_checks` no tiene niveles de severidad, todo dispara retry (2.5).
- 🟡 No valida `{% url %}` con pk, ni tags de bloque menos comunes (3.5, 3.13).
- 🟡 Reglas de 4 columnas en español, anclada a tokens Tailwind específicos (3.9).

### `examples/catalog.py`
- 🟠 HOME y LIST templates usan `{% for item in items %}` / `{% for item in items|slice:":6" %}`, directamente contra las reglas del prompt y contra `check_template_structure` (1.7, 2.2).
- 🟡 Comentarios `{# campo título principal #}` embebidos, se arrastran al output (3.11).
- 🟡 Textos hardcoded en español, incompatibles con prompt traducido a inglés (3.4).
- 🟡 Paginación básica sin preservar `q` ni selector de página (3.7).
- 🟡 Todos los ejemplos se cortan a 1500 chars al enviarse al LLM (1.8).

### `project_generator.py`
- 🔴 Pasa `user_prompt` sin traducir al checker, rompiendo `check_prompt_contradictions` para idiomas no-inglés (1.2).
- 🔴 Desalineación entre `page["name"]` (URL name real) y `page["view_name"]` (URL name que ve el validador y los prompts de retry) (1.3).
- 🟠 El retry de templates no pasa `design_system`, rompiendo la coherencia de estilos (1.4).
- 🟡 Retry único, sin verificar si quedó sin arreglar (3.1).
- 🟡 Logs posiblemente excesivos (3.16).

### `generator_prompts.py`
- 🔴 `\\n` literal en `context_hint` de list y home rompe el formato del prompt (1.1).
- 🟠 Duplicación de `design_system_text` en `prompt_base_template` y `prompt_template` (3.3).
- 🟡 Reglas globales inyectadas en prompts donde no aportan (coste de tokens) (3.10).
- 🟡 Prompts monolíticos en español con prompt del usuario ya traducido a inglés (2.7).

### Fuera de los 4 principales (contexto)
- 🟠 `llm_wrappers.py`: `time.sleep(20)` bloqueante por llamada (1.5).
- 🟠 `fallbacks.py`: usa `items` en todos los contextos, chocando con prompts y checker (2.2).
- 🟡 `examples/__init__.py` `_detect_style`: heurística frágil (3.14).
- 🟡 No hay tests (3.15).

---

## 5. Orden sugerido para ir abordando

Cuando me digas, iría en este orden (cada ítem es una sesión independiente):

1. **Fix del `\\n` literal** (1.1): cinco minutos, impacto alto. Es el único bug en los 4 archivos principales que probablemente está empeorando los outputs ahora mismo.
2. **Decidir qué hacer con la traducción del prompt** (1.2, 2.7): o se traduce de verdad todo el contexto a inglés, o se quita la traducción y se ponen las palabras del checker en español + inglés. No se puede dejar a medias.
3. **Unificar la variable de contexto** (2.2, 1.7): decidir si listados usan `page_obj` (ya es la decisión del prompt, mantenerla) y arreglar fallbacks y ejemplos en consecuencia. Arrastra cambios en `fallbacks.py`, `examples/*.py` y posiblemente el `_regenerate_with_errors` si quedan rastros.
4. **Unificar `name` vs `view_name`** (1.3): decidir si son lo mismo o no. Si son lo mismo, eliminar uno. Si no, arreglar `real_url_names` para que use el `name` real del path.
5. **Pasar `design_system` al retry** (1.4): una línea.
6. **Dar niveles de severidad al checker** (2.5): refactor chico con impacto grande en coste de LLM.
7. **Ajustar `fix_template` y añadir tests** (1.6, 3.15): perfecto para una sesión de TDD.
8. El resto (mejoras de calidad de ejemplos, tokens, heurísticas) en sesiones individuales cortas.

Dime cuál quieres atacar primero.
