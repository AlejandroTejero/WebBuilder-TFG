Estoy desarrollando una app Django llamada WebBuilder. Ya tengo integrado un LLM con OpenRouter y funciona en /asistente: el usuario mete una URL (JSON/XML) + un prompt y el LLM responde texto.

Quiero avanzar a una fase 2 más sólida y defendible:
1) El LLM debe devolver SOLO JSON válido con este contrato:
   - site_type (blog/portfolio/catalog/dashboard/other)
   - pages (lista de slugs)
   - mapping (title/content/image/date) donde cada valor sea:
     - el nombre exacto de una clave existente del dataset, o null
2) Para evitar inventos, quiero pasar al LLM:
   - available_keys (lista de claves más frecuentes)
   - 1-3 items de ejemplo recortados
   - path de la colección principal si existe
3) En backend:
   - validar JSON (json.loads)
   - si falla, reintentar 1 vez con el error
   - guardar el JSON validado en BD (field_mapping o llm_plan)
4) En la UI:
   - mostrar el JSON en /asistente y permitir “Regenerar” y “Aceptar plan”

Dame los pasos exactos y los cambios mínimos por archivo para implementarlo (assistant.py, client/planner, templates, models si hace falta). Quiero hacerlo incremental y sin romper lo que ya funciona.