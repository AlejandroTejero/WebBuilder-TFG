# Integración de un LLM en WebBuilder (mapa mental + checklist)

## Objetivo
Conectar un LLM al flujo actual del **/asistente** para que:
1) el usuario pegue una URL,
2) tú hagas **fetch + parse + analysis** (determinista),
3) el LLM genere un **plan/mapping** (y luego código),
4) tú lo **valides/guardes**,
5) y se vea en la UI.

---

## Mapa mental (por capas)

### 1) UI y entrada del usuario
**Dónde:** `WebBuilder/forms.py` + `templates/WebBuilder/assistant.html`

- Añadir un campo al formulario:
  - `user_prompt` (textarea): “qué quieres construir y cómo”
- En `assistant.html`:
  - textarea + submit (o botón “Generar plan”)

**Objetivo:** que el prompt del usuario llegue al backend junto con la URL.

---

### 2) Persistencia y trazabilidad (defendible en TFG)
**Dónde:** `WebBuilder/models.py` (modelo `APIRequest`)

Campos mínimos recomendados:
- `user_prompt` (TextField)
- `llm_provider` (CharField) — `openrouter/groq/lmstudio`
- `llm_model` (CharField)
- `llm_plan_raw` (TextField o JSONField) — respuesta cruda
- `llm_plan` (JSONField) — respuesta validada (puedes reutilizar `field_mapping`)
- `llm_error` (TextField) — si falla

**Objetivo:** poder enseñar en defensa:
- qué se pidió,
- qué respondió,
- qué validaste,
- y qué guardaste.

---

### 3) Capa LLM (adaptador limpio)
**Dónde:** crear carpeta `WebBuilder/utils/llm/`

Estructura recomendada:

#### `utils/llm/client.py`
- Cliente genérico **OpenAI-compatible**:
  - usa `base_url`, `api_key`, `model`
  - función `chat(messages) -> text`
  - timeouts + manejo de errores

#### `utils/llm/planner.py`
- Construye el prompt con:
  - `analysis` (lo que ya produces)
  - `samples` (items recortados)
  - `user_prompt`
- Llama a `client.chat(...)`
- Devuelve texto crudo (primero) / JSON (después)

#### `utils/llm/schemas.py` (opcional al inicio, recomendado luego)
- Contrato del plan (JSON Schema / Pydantic)
- Valida y normaliza:
  - `site_type`, `pages`, `mapping`, `models`

#### `utils/llm/validator.py` (fase siguiente)
- Valida JSON + checks extra
- Fallback si el LLM falla (tu heurística actual)

**Objetivo:** que `assistant.py` no tenga lógica “sucia”; solo llame a `suggest_plan()`.

---

### 4) Configuración por settings (para cambiar proveedor sin tocar código)
**Dónde:** `project/settings.py` + `.env`

Variables típicas:
- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

**Objetivo:** cambiar cloud↔local o modelo↔modelo cambiando solo parámetros.

---

### 5) Integración en el flujo actual
**Dónde:** `WebBuilder/views/assistant.py`

Tu flujo actual:
- fetch → parse → build_analysis → guardar

Añadir después de `build_analysis()`:
- Si hay `user_prompt`:
  1) preparar payload (analysis + samples + user_prompt)
  2) llamar `utils/llm/planner.suggest_plan(...)`
  3) validar (al principio: texto; luego: JSON)
  4) guardar en `field_mapping` o `llm_plan`
  5) renderizar en la página

**Objetivo:** enviar el formulario y ver respuesta del LLM dentro del asistente.

---

## Flujo final (en una línea)
**Usuario URL + prompt → parse/analysis → LLM plan/mapping → validación/guardado → UI lo muestra**

---

## Checklist corto (mínimo para empezar)
1) `user_prompt` en `APIRequestForm` + textarea en `assistant.html`
2) Campos LLM mínimos en `APIRequest`
3) Crear `utils/llm/`:
   - `client.py`
   - `planner.py`
   - (opcional) `schemas.py`
4) Settings/env: provider + base_url + api_key + model
5) Bloque pequeño en `views/assistant.py` para llamar al planner y guardar/renderizar

---

## Estrategia para que hoy “responda algo” sin liarte
### Paso 1 (rápido)
- Pide al LLM **solo texto** (“dime qué tipo de web harías y por qué”)
- Muestra esa respuesta en `assistant.html`

### Paso 2 (después de confirmar conexión)
- Exige salida **JSON** (plan estructurado)
- Guardarlo en `field_mapping` / `llm_plan`
- Renderizarlo bonito (resumen + mapping)

---

## Nota clave
Si montas el cliente como OpenAI-compatible, cambiar proveedor/modelo suele ser:
- cambiar `LLM_BASE_URL`
- cambiar `LLM_API_KEY`
- cambiar `LLM_MODEL`

Sin tocar el resto del proyecto.