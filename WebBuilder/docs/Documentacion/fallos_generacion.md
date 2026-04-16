# Fallos y aprendizajes en la generación de WebBuilder

## Documento de memoria técnica

Este documento recoge todos los problemas detectados durante las pruebas de generación del sistema WebBuilder, con explicación del porqué de cada fallo y las soluciones aplicadas o pendientes. El objetivo es que sirva como referencia para no repetir los mismos errores y para justificar decisiones técnicas en el TFG.

---

## 1. Errores de limitación del LLM

### 1.1. Error HTTP 429 — Rate Limit Exceeded (Tokens por Minuto)

**Cuándo ocurre:** Cuando el sistema manda demasiadas llamadas al LLM en poco tiempo y supera el límite de tokens por minuto (TPM) del modelo.

**Modelo afectado:** `openai/gpt-oss-120b` via Groq — límite de 8.000 TPM.

**Síntoma en logs:**
```
LLM falló en 'template_character_catalog': LLM HTTP 429
Rate limit reached: Limit 8000, Used 2870, Requested 6732
```

**Por qué ocurre:** El prompt de `prompt_template` es muy grande — incluye el `enriched_prompt`, los campos del modelo, los datos de ejemplo y el ejemplo HTML completo. Cuando ese prompt supera los tokens disponibles en el minuto actual, la llamada falla.

**Consecuencia:** El template afectado cae al fallback vacío, generando una página prácticamente en blanco.

**Solución aplicada:**
- Reducir `_MAX_ENRICHED_CHARS` de 3000 a 1000 en `enrich_prompt.py`
- Eliminar `sample_items` del prompt de `prompt_pages_structure` — no son necesarios para decidir la estructura de páginas
- Truncar el ejemplo HTML a 1500 caracteres antes de inyectarlo en `prompt_template`

**Solución pendiente:** Implementar `_simplify_example()` para reducir el ejemplo HTML quitando clases Tailwind largas y comentarios, manteniendo la estructura completa pero con menos tokens.

---

### 1.2. Error HTTP 413 — Request Entity Too Large

**Cuándo ocurre:** Cuando el prompt supera el límite de tamaño de petición HTTP del modelo, independientemente de los tokens por minuto.

**Modelo afectado:** `groq/compound` — límite de tamaño de request muy restrictivo.

**Síntoma en logs:**
```
LLM falló en 'translate_prompt': LLM HTTP 413: Request Entity Too Large
LLM falló en 'models': LLM HTTP 413: Request Entity Too Large
LLM falló en 'base.html': LLM HTTP 413: Request Entity Too Large
```

**Por qué ocurre:** El modelo `groq/compound` tiene un límite de tamaño de petición HTTP muy bajo. Aunque tiene 70K TPM, rechaza peticiones que superan cierto tamaño en bytes antes de procesarlas. Esto afectaba incluso a prompts relativamente pequeños como `models.py`.

**Consecuencia:** Prácticamente toda la generación falla y el proyecto resultante está vacío o lleno de fallbacks.

**Solución:** No usar `groq/compound` para generación de código. Usar `meta-llama/llama-4-scout-17b-16e-instruct` que tiene 30K TPM y no tiene este problema de tamaño de request.

---

### 1.3. Comparativa de modelos disponibles en Groq

| Modelo | TPM | RPD | Observaciones |
|--------|-----|-----|---------------|
| `groq/compound` | 70K | Sin límite | Límite de tamaño de request muy restrictivo. No recomendado. |
| `groq/compound-mini` | 70K | Sin límite | Mismo problema que compound. |
| `openai/gpt-oss-120b` | 8K | 200K | Buena calidad pero TPM muy bajo. Falla en prompts grandes. |
| `openai/gpt-oss-20b` | 8K | 200K | Mismo límite que 120b, menor calidad. |
| `meta-llama/llama-4-scout-17b-16e-instruct` | 30K | 500K | **Recomendado.** Buen equilibrio calidad/límites. Sin problemas de tamaño de request. |
| `llama-3.3-70b-versatile` | 12K | 100K | Aceptable pero con menos margen que llama-4-scout. |
| `meta-llama/llama-prompt-guard-2-22m` | 15K | 500K | Modelo de guardia, no apto para generación. |

**Modelo recomendado actualmente:** `meta-llama/llama-4-scout-17b-16e-instruct`

---

### 1.4. El parámetro `time.sleep` en `llm_wrappers.py`

**Qué es:** Un sleep entre llamadas al LLM para evitar superar el límite de TPM.

**Valor correcto:** 12-15 segundos. Con 8-9 llamadas por generación, el tiempo total es de 2-3 minutos, manejable sin que el servidor corte la conexión por timeout.

**Error cometido:** Subir el sleep a 60 segundos pensando que así se evitaría el límite de TPM. Resultado: el servidor web cortaba la conexión por timeout antes de que terminara la generación, manifestándose como errores 413 o conexiones rotas.

**Conclusión:** El sleep no debe superar los 20 segundos. La solución correcta para el límite de TPM es reducir el tamaño de los prompts, no aumentar el tiempo de espera.

---

## 2. Errores en el código generado por el LLM

### 2.1. Acceso a subcampos de objetos anidados — `item.campo.subcampo`

**Cuándo ocurre:** Cuando el dataset tiene campos que son objetos anidados (por ejemplo, `origin: {name: "Earth", url: "..."}`) y el LLM los trata como objetos Django en el template.

**Ejemplo concreto — API Rick and Morty:**
El campo `origin` en la API es un dict con `name` y `url`. El modelo Django lo guarda como `CharField` con solo el nombre. Sin embargo, el LLM genera en el template:
```html
{{ item.origin.name }}  {# INCORRECTO — origin es un string, no un objeto #}
```

**Consecuencia:** Error en runtime al intentar acceder a `.name` sobre un string.

**Por qué el checker no lo detecta:** `check_consistency` busca `item.\w+` pero no detecta el patrón `item.campo.subcampo`. Solo comprueba que el primer nivel de campo exista en el modelo.

**Solución pendiente:** Mejorar `check_consistency` para detectar patrones `item.campo.subcampo` y marcarlos como error cuando `campo` es un `CharField` o `TextField` en el modelo.

**Solución inmediata en el prompt:** Reforzar la regla en `generator_prompts.py`:
```
CRÍTICO: todos los campos del modelo son strings o tipos simples. NUNCA uses item.campo.subcampo.
```
Esta regla ya existe pero el LLM la ignora cuando el dataset tiene campos claramente anidados.

---

### 2.2. URLs hardcodeadas incorrectas en templates

**Cuándo ocurre:** El LLM usa nombres de URL genéricos como `{% url 'detail' %}` o `{% url 'catalog' %}` cuando las URLs reales tienen nombres distintos como `character_detail` o `character_catalog`.

**Ejemplo:**
```html
{# INCORRECTO — la URL real se llama 'character_detail' #}
<a href="{% url 'detail' item.pk %}">Ver detalle</a>
```

**Consecuencia:** Error `NoReverseMatch` en runtime al intentar resolver la URL.

**Por qué ocurre:** El LLM tiende a usar nombres genéricos aunque el prompt le indique los nombres exactos. Ocurre especialmente cuando el template falla y cae al fallback, o cuando la llamada al LLM tiene errores de tokens.

**Solución aplicada:** `check_django_syntax` ahora valida que todos los `{% url 'nombre' %}` del template correspondan a URLs reales del proyecto, usando `valid_url_names` que se construye en el Paso 8 de `project_generator.py`.

**Solución pendiente:** Cuando se detecta una URL incorrecta en la autocorrección, pasar `valid_url_names` explícitamente en el mensaje de corrección al LLM.

---

### 2.3. `json.loads` sobre un dict ya parseado en `load_data.py`

**Cuándo ocurre:** Cuando el dataset tiene campos que son objetos anidados y el LLM intenta parsearlos como si fueran strings JSON.

**Ejemplo concreto — API Rick and Morty:**
```python
# INCORRECTO — origin ya es un dict, no un string JSON
origin = json.loads(raw_item['origin'])

# CORRECTO
origin_name = raw_item['origin']['name']
```

**Consecuencia:** `json.JSONDecodeError` al intentar parsear un dict como string. Todos los items fallan silenciosamente y no se carga ningún dato.

**Por qué ocurre:** El LLM detecta que el campo `origin` es un objeto anidado y asume que viene serializado como string JSON, cuando en realidad `response.json()` ya lo ha deserializado completamente.

**Solución:** No existe validación automática de este error actualmente. Habría que revisar manualmente el `load_data.py` generado cuando no se cargan datos.

**Mejora pendiente:** Añadir en el prompt de `prompt_load_data` una regla explícita:
```
CRÍTICO: response.json() ya deserializa todo el JSON incluyendo objetos anidados.
NUNCA uses json.loads() sobre campos del resultado — ya son dicts o listas Python.
Para acceder a subcampos usa directamente raw_item['campo']['subclave'].
```

---

### 2.4. Paginación — la API solo devuelve la primera página

**Cuándo ocurre:** Cuando la API tiene paginación y el `load_data.py` solo hace una petición a la URL base.

**Ejemplo — API Rick and Morty:**
La API devuelve 20 personajes por página con un campo `info.next` que apunta a la siguiente página. El LLM generó solo una petición a `https://rickandmortyapi.com/api/character`, cargando solo 20 de los 826 personajes disponibles.

**Solución manual:**
```python
url = 'https://rickandmortyapi.com/api/character'
while url:
    response = requests.get(url)
    data = response.json()
    for raw_item in data['results']:
        # ... crear items
    url = data['info']['next']  # None cuando no hay más páginas
```

**Mejora pendiente:** Detectar en `prompt_load_data` si la API tiene paginación (campo `next` o `pages` en la respuesta) e incluir lógica de paginación automáticamente.

---

### 2.5. La view de `home` pasa `featured` al contexto pero el template espera `items`

**Cuándo ocurre:** Cuando el LLM genera la view de home pasando una variable con nombre distinto al que espera el template.

**Ejemplo:**
```python
# En views.py — el LLM pasó 'featured'
context = {'featured': Item.objects.all()[:6]}

# En home.html — el template espera 'items'
{% for item in items %}  {# items está vacío, featured se ignora #}
```

**Consecuencia:** La home aparece vacía aunque haya datos en la base de datos.

**Por qué ocurre:** El LLM a veces usa nombres semánticamente más descriptivos (`featured`, `recent`, `latest`) en lugar del nombre estándar `items` que usan los templates.

**Solución aplicada:** En `prompt_views` se especifica explícitamente que la variable del contexto debe llamarse `items` en todos los casos. En `prompt_template` el context hint también lo indica.

**Mejora pendiente:** Añadir un check en `check_consistency` que verifique que las variables pasadas en el contexto de cada view coinciden con las variables que usa su template correspondiente.

---

## 3. Errores de arquitectura y diseño

### 3.1. El `enriched_prompt` era demasiado largo

**Problema:** `enrich_user_prompt` construía un texto muy largo combinando el prompt del usuario, las reglas de prioridad, el contexto del dataset y todas las sugerencias. Con `_MAX_ENRICHED_CHARS = 3000` y datasets con muchos campos, el prompt enriquecido podía superar los 2000-3000 tokens solo en esta parte.

**Solución aplicada:**
- Reducir `_MAX_ENRICHED_CHARS` a 1000
- Eliminar `_DATASET_PRIORITY_RULES` del `enriched_prompt` — esas reglas ya se inyectan en cada prompt de generación desde `generator_prompts.py`, así que estaban duplicadas
- Mejorar `_matches` para evitar falsos positivos usando split por `_` en lugar de búsqueda de substring

---

### 3.2. `theme_rules_text` inyectado en `prompt_views`

**Problema:** `prompt_views` incluía las reglas de diseño visual de Tailwind (`theme_rules_text`) aunque `views.py` es un archivo Python puro donde esas reglas no tienen ningún sentido. Solo añadían tokens y podían confundir al LLM mezclando contextos visuales con lógica de negocio.

**Solución aplicada:** Eliminar `theme_rules_text` de `prompt_views`. Se mantiene únicamente en `prompt_base_template` y `prompt_template` donde sí aplica.

---

### 3.3. `run_all_checks` usaba `enriched_prompt` para validar contradicciones

**Problema:** La validación de `check_prompt_contradictions` comparaba el HTML generado contra el `enriched_prompt`, que mezcla el prompt real del usuario con sugerencias del dataset y defaults del sistema. Esto podía generar falsos positivos — el validador detectaba "contradicciones" contra texto que no era una petición explícita del usuario.

**Solución aplicada:** `run_all_checks` recibe el `user_prompt` original limpio, no el `enriched_prompt`. El `enriched_prompt` solo se usa para generar, el `user_prompt` para validar.

---

### 3.4. Bug en `fix_template` — reposicionamiento de `{% extends %}`

**Problema:** Cuando el LLM generaba texto antes del `{% extends 'base.html' %}`, la función intentaba moverlo al principio pero lo hacía incorrectamente:

```python
# INCORRECTO
html = html[:match.start()].replace(extends_tag, '')
html = extends_tag + '\n' + html
```

Esto dejaba el `extends_tag` en su posición original Y lo añadía al principio, duplicándolo o corrompiendo el template.

**Solución aplicada:**
```python
# CORRECTO
html = extends_tag + '\n' + html[:match.start()] + html[match.end():]
```

---

### 3.5. `check_template_structure` — comparación poco fiable del bucle `{% for %}`

**Problema:**
```python
if "{% for item in items %}" not in content and \
   "{% for item in items %}" not in content.replace("  ", " "):
```
El segundo `replace` solo elimina dobles espacios pero el LLM puede generar el tag con saltos de línea, tabulaciones u otros espacios. Ambas condiciones eran casi idénticas y el check era poco fiable.

**Solución aplicada:** Normalizar el contenido completo antes de buscar:
```python
content_normalized = re.sub(r'\s+', ' ', content)
if "{% for item in items %}" not in content_normalized:
```

---

## 4. Decisiones de diseño tomadas durante el desarrollo

### 4.1. Traducción del prompt del usuario al inglés

**Decisión:** Traducir el `user_prompt` a inglés antes de procesarlo, usando el propio LLM.

**Por qué:** Los sets de palabras clave en `check_prompt_contradictions` y en el futuro `_detect_style` de `get_example` deben funcionar en un idioma único. Mantener palabras clave en español e inglés escala mal y es propenso a errores.

**Implementación:** `translate_prompt_to_english` en `llm_wrappers.py`. Si falla, usa el prompt original sin traducir — el sistema no se rompe, solo pierde la normalización.

**Consecuencia:** Los sets de palabras clave en `consistency_checker.py` solo necesitan estar en inglés.

---

### 4.2. Librería de ejemplos con múltiples estilos

**Decisión:** Crear tres variantes de cada ejemplo (dark, light, editorial) en lugar de un único ejemplo por tipo de página.

**Por qué:** El LLM se "contagia" del estilo del ejemplo. Si el único ejemplo disponible es oscuro con gradientes verdes, tiende a generar algo similar aunque el usuario haya pedido algo minimalista y claro.

**Implementación:** `_detect_style(user_prompt)` en `examples/__init__.py` analiza el prompt traducido y elige el ejemplo más adecuado. Por defecto devuelve `light` como estilo más neutro.

**Importante:** Los ejemplos usan placeholders genéricos (`CAMPO_TITULO`, `CAMPO_IMAGEN`, `NOMBRE_URL_LISTADO`) en lugar de nombres de campo concretos, para no confundir al LLM con campos que pueden no existir en el modelo real.

---

### 4.3. Truncado de ejemplos a 1500 caracteres

**Decisión:** Truncar el ejemplo HTML a 1500 caracteres antes de inyectarlo en `prompt_template`.

**Por qué:** Los ejemplos completos pueden tener 5000-8000 caracteres. Inyectarlos completos dispara el tamaño del prompt y puede causar errores de TPM o de tamaño de request.

**Contrapartida:** Los primeros 1500 caracteres cubren la estructura principal (cabecera, primera card, inicio del grid) pero pueden no incluir la paginación o el empty state. Por eso estos elementos se especifican explícitamente en las reglas del prompt.

**Mejora pendiente:** Implementar `_simplify_example()` que en lugar de truncar por caracteres, elimine clases Tailwind largas y comentarios manteniendo la estructura completa.

---

## 5. Resumen de mejoras implementadas en esta sesión

| Área | Mejora | Estado |
|------|--------|--------|
| `consistency_checker.py` | Fix bug `fix_template` en `{% extends %}` | ✅ Hecho |
| `consistency_checker.py` | `check_prompt_contradictions` más flexible con sets de palabras | ✅ Hecho |
| `consistency_checker.py` | `check_template_structure` normalización de espacios | ✅ Hecho |
| `consistency_checker.py` | `check_consistency` detecta `filter__` en views | ✅ Hecho |
| `consistency_checker.py` | `check_django_syntax` valida nombres de URL reales | ✅ Hecho |
| `generator_prompts.py` | Eliminar `theme_rules_text` de `prompt_views` | ✅ Hecho |
| `generator_prompts.py` | Truncar ejemplos HTML a 1500 chars | ✅ Hecho |
| `generator_prompts.py` | Pasar `user_prompt` a `get_example` para elegir estilo | ✅ Hecho |
| `project_generator.py` | Paso 8 actualizado con `valid_url_names` | ✅ Hecho |
| `project_generator.py` | Traducción del prompt a inglés antes de enriquecer | ✅ Hecho |
| `enrich_prompt.py` | Eliminar reglas de prioridad duplicadas | ✅ Hecho |
| `enrich_prompt.py` | `_matches` más preciso con split por `_` | ✅ Hecho |
| `enrich_prompt.py` | Truncado del prompt enriquecido a 1000 chars | ✅ Hecho |
| `examples/` | Nueva librería con 3 estilos × 3 páginas × 4 site_types | ✅ Hecho |
| `examples/__init__.py` | `_detect_style` y `get_example` con selección por estilo | ✅ Hecho |
| `consistency_checker.py` | Detectar `item.campo.subcampo` | ⏳ Pendiente |
| `load_data.py` | Regla anti `json.loads` sobre dicts ya parseados | ⏳ Pendiente |
| `load_data.py` | Detección y soporte de paginación en APIs | ⏳ Pendiente |
| `prompt_template` | `_simplify_example()` para reducir ejemplos manteniendo estructura | ⏳ Pendiente |
| `check_consistency` | Validar coincidencia de variables entre view y template | ⏳ Pendiente |
