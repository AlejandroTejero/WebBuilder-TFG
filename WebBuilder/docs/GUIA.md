Eres mi asistente técnico para mi TFG: una app Django llamada WebBuilder. Objetivo final: a partir de una URL que devuelva datos (JSON/XML), generar una web Django “perfecta” y adaptada a lo que pide el usuario. Ya NO quiero un wizard manual de mapping; quiero que un LLM sugiera el mapping (y más adelante el tipo de web y la estructura). También quiero explorar n8n local como orquestador del flujo (gratis).

========================
1) ESTADO ACTUAL (repo)
========================
Proyecto Django en WebBuilder/project/ con app principal WebBuilder.

Rutas actuales (WebBuilder/urls.py):
- "/" home
- "/asistente" assistant (MVP: solo análisis)
- "/historial" history
- "/login" "/registro"
- "/preview/<int:api_request_id>" existe SOLO como placeholder (devuelve 404 controlado). Se mantiene para que no rompan enlaces del navbar/historial/admin.

Vistas importantes:
- WebBuilder/views/assistant.py: MVP análisis-only.
  - POST: recibe api_url, hace fetch+parse, build_analysis, guarda en BD, muestra resumen.
  - Cache 1h por URL (hash MD5).
  - No hay mapping/intents/preview real aquí todavía.
- WebBuilder/views/preview.py: placeholder (HttpResponseNotFound).
- WebBuilder/views/history.py: historial de APIRequest por usuario.

Modelo:
- WebBuilder/models.py -> APIRequest:
  - user, api_url, date
  - raw_data (text), parsed_data (JSONField)
  - status (pending/processed/error), response_summary, error_message
  - field_mapping (JSONField) -> aquí guardaremos el mapping que devuelva el LLM.

Form:
- APIRequestForm: solo api_url.

Templates:
- templates/WebBuilder/assistant.html: UI pelada con:
  - formulario URL
  - bloque “Resultado del análisis” (count, format/summary, path)
  - No hay wizard, ni mapping, ni preview.
- navbar.html y history.html todavía enlazan a “preview” (por eso dejamos preview placeholder).

CSS:
- static/css/assistant.css está reducido solo a lo que usa el HTML actual.

Utils (estructura nueva):
- WebBuilder/utils/ingest/
  - url_reader.py -> fetch_url() (descarga segura) devuelve (raw_text, fetch_summary)
  - parsers.py -> parse_raw() devuelve (format, parsed_payload), summarize_data(), detect_format()
- WebBuilder/utils/analysis/
  - builder.py -> build_analysis(parsed_data, raw_text) devuelve dict estable con:
    - format, root_type, message
    - main_collection: found/path/count/top_keys/sample_keys/path_display
    - keys: all/top
    - roles: list(ROLE_DEFS)
    - suggestions: (todavía heurístico) via suggestions_heuristic.suggest_mapping_smart()
  - detection.py -> find_main_items() (detecta colección principal)
  - helpers.py -> get_by_path() etc.
  - constants.py -> ROLE_DEFS y constantes de analysis.
  - suggestions_heuristic.py -> heurística legacy de mapping (fallback/baseline).
- WebBuilder/utils/llm/
  - solo __init__.py por ahora (pendiente de implementar).

Notas:
- tests eliminados (estaban desactualizados).
- utils_old puede existir pero IGNORAR; no depende ya.

========================
2) NUEVA DIRECCIÓN (LLM-first)
========================
Queremos mantener determinista:
- descarga, parseo JSON/XML, detección de colección principal (candidatos), normalización básica de datos.
Y delegar al LLM:
- sugerir el mapping semántico (title/body/image/date/link/price/etc.) según el dataset.
Opcional futuro:
- sugerir “site_type” (blog/portfolio/catalog/landing) y secciones.
- generar plantillas y contenido (copy), y eventualmente generar un mini-proyecto Django “site” dentro del sistema.
- n8n local para orquestar el pipeline (webhook -> LLM -> generación -> deploy).

Idea clave:
- NO pedir al LLM “parsear” texto raw si ya podemos parsear nosotros. El LLM debe interpretar, no inventar/parsear.
- Diseñar un contrato JSON estable (schema) para la salida del LLM.
- Validar siempre la respuesta del LLM (JSON válido, paths existentes en samples, roles permitidos, etc.).
- Guardar trazabilidad: payload enviado al LLM + respuesta + modelo utilizado + errores.

========================
3) LO QUE HAY QUE IMPLEMENTAR AHORA (próximo sprint)
========================
A) Implementar capa LLM (WebBuilder/utils/llm/)
- client.py:
  - Soportar LM Studio local (OpenAI-compatible) y OpenRouter (cloud).
  - Config por variables de entorno:
    - LLM_PROVIDER (lmstudio/openrouter)
    - LLM_BASE_URL, LLM_API_KEY
    - LLM_MODEL
    - LLM_TIMEOUT
- schema.py:
  - Definir contrato de respuesta:
    {
      "main_collection_path": "string o '' si root-list",
      "mapping": { "<role>": "<path>" },
      "site_type": "opcional",
      "confidence": "opcional 0..1",
      "notes": ["opcional"]
    }
  - Reglas:
    - mapping solo usa roles existentes en ROLE_DEFS
    - paths deben existir al menos en 1 sample
- prompts.py:
  - Prompt corto, robusto, obliga salida JSON ONLY.
  - Incluir roles + descripción usuario + candidatos + samples (recortados).
- mapping_suggester.py:
  - función suggest_mapping_llm(analysis_payload, user_description=None) -> dict (schema)
  - Manejo de errores: timeout, JSON inválido, respuesta vacía.
  - Fallback: usar suggestions_heuristic.suggest_mapping_smart() si el LLM falla.

B) Preparar el input del LLM (determinista)
- En analysis/builder.py (o módulo nuevo):
  - construir “llm_payload” con:
    - candidate_collections (top 3 paths) + 2–3 items por path (recortados: strings max N chars)
    - keys/tipos
    - roles (ROLE_DEFS)
    - formato detectado (json/xml)
  - guardar llm_payload en BD para reproducibilidad (ideal: nuevo JSONField en APIRequest o nuevo modelo LLMRun).

C) Integrar LLM en el flujo
- En views/assistant.py:
  - tras build_analysis, llamar a suggest_mapping_llm(...) y guardar resultado en APIRequest.field_mapping (y quizá site_type).
  - Mostrar en UI (mínimo): “Mapping sugerido (JSON)” en el assistant, o al menos guardarlo.
  - Añadir un campo opcional en el formulario: “Descripción de la web” (user intent). Puede ser:
    - un campo extra en el form (no model) o guardarlo en sesión o en APIRequest (nuevo campo).
- Mantener preview placeholder por ahora.

D) Validación
- Implementar validación mínima del mapping:
  - roles permitidos
  - no duplicados si aplica (por ejemplo title no duplicado)
  - path existe en samples (get_by_path)
  - si no cumple, fallback a heurística o dejar roles vacíos.

========================
4) PLAN n8n (cuando el LLM funcione local)
========================
Objetivo: orquestar el pipeline con n8n local (gratuito).
Diseño sugerido:
- Django expone endpoints:
  - POST /api/analyze (ya existe implícito en assistant; se puede separar)
  - POST /api/llm-map (dado api_request_id -> devuelve mapping)
  - POST /api/generate-site (futuro)
- n8n:
  1) Webhook trigger (o cron)
  2) Llama a Django para obtener llm_payload (o parsed_data+analysis)
  3) Llama al LLM (LM Studio u OpenRouter)
  4) Devuelve mapping a Django (update APIRequest.field_mapping)
  5) (futuro) desencadena generación de plantillas y deploy

========================
5) OBJETIVO FINAL (fase generación)
========================
Con mapping (y site_type), generar una web Django adaptada:
- elegir “tema” (blog/portfolio/catalog/landing)
- generar templates y estructura de secciones
- normalizar items a un formato estándar para render
- permitir refinamiento por el usuario (descripción/estilo)
- (opcional) desplegar automáticamente (fase avanzada)

========================
6) CONSTRICCIONES / REGLAS
========================
- Priorizar robustez (no depender solo del LLM).
- Guardar trazabilidad para TFG (inputs/outputs/errores).
- Evitar prompts gigantes: usar muestras recortadas.
- No reintroducir wizard manual por ahora.
- Mantener preview placeholder y enlaces para no romper UI/admin.

========================
7) EJEMPLOS PARA PROBAR
========================
JSON: https://jsonplaceholder.typicode.com/posts
XML: https://www.w3schools.com/xml/plant_catalog.xml

========================
8) QUÉ NECESITO DE TI (asistente)
========================
- Proponer el schema exacto del JSON de salida del LLM + validación.
- Proponer prompts robustos (LM Studio + OpenRouter).
- Indicar cambios mínimos en builder.py/assistant.py/models/forms/templates para integrar LLM sin romper.
- Proponer cómo guardar llm_payload + llm_response (nuevo campo o modelo).
- Plan concreto de endpoints para integrarlo con n8n.
- Mantener el proyecto “limpio” y sin barro: cambios pequeños, iterables, con fallback.

Comienza revisando ROLE_DEFS (utils/analysis/constants.py) y build_analysis (utils/analysis/builder.py) para diseñar el payload del LLM y el schema de respuesta.
