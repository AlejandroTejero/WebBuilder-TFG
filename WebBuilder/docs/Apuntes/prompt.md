## WebBuilder — Estado actual y próximos pasos

### Qué es el proyecto
Aplicación Django que permite generar sitios web a partir de APIs públicas (JSON/XML). El usuario mete una URL, un LLM analiza los datos y genera un schema dinámico, el usuario ajusta el schema en un editor visual y al aceptar se genera un sitio con HTML/CSS creado por IA. La finalidad final es que el sitio sea descargable como proyecto Django independiente.

### Stack
Django · SQLite · Bootstrap 5 (en preview/history) · CSS propio (home/assistant) · LLM via OpenRouter · Dos modelos: APIRequest y GeneratedSite

---

### Lo que está implementado y funcionando

**Schema dinámico (cambio principal)**
- Antes el mapping era fijo: 4 campos (title, content, image, date)
- Ahora el LLM elige libremente qué campos del dataset mostrar y en qué orden
- El nuevo contrato del field_mapping es:
{
  "site_type": "catalog",
  "site_title": "Nombre del sitio",
  "fields": [
    {"key": "COMMON", "label": "Nombre"},
    {"key": "PRICE", "label": "Precio"}
  ]
}
- Validación anti-alucinación en backend: cualquier key no presente en available_keys se descarta silenciosamente

**Archivos modificados:**
- utils/llm/planner.py — nuevo schema dinámico libre
- utils/llm/themer.py — recibe fields[] en vez de mapping fijo, genera HTML/CSS adaptado al dataset real
- views/assistant.py — muestra el schema generado en card legible
- views/preview.py — editor visual con drag & drop de campos, checkboxes activar/desactivar, añadir campos no incluidos
- views/render.py — nuevo, vista a pantalla completa con barra WebBuilder
- views/history.py — muestra GeneratedSites reales con enlaces
- views/__init__.py — sin referencias a sites.py
- urls.py — sin rutas de sites/, solo render
- templatetags/wb_extras.py — filtros custom: get_item y split
- templates/WebBuilder/preview.html — editor visual completo
- templates/WebBuilder/site_render.html — pantalla completa con barra negra, botón cambiar diseño, chips de hints
- templates/WebBuilder/history.html — muestra sites reales
- templates/WebBuilder/assistant.html — card del schema generado

**Flujo actual completo:**
/asistente → mete URL + prompt
    ↓
análisis (fetch + parse + detect estructura)
    ↓
LLM planner → schema dinámico validado
    ↓
/preview/<id> → editor visual del schema (drag&drop, activar/desactivar campos)
    ↓
Aceptar y publicar → LLM themer genera HTML/CSS adaptado al schema
    ↓
/preview/<id>/render/ → sitio a pantalla completa con barra WebBuilder
    - botón "Cambiar diseño" → regenera solo el tema sin tocar el schema
    - botón "← Editor" → vuelve al preview

**Lo que se eliminó:**
- Rutas sites/<id>/ y sites/<id>/item/<index>/
- site_view.html
- Referencias a site_home y site_detail en templates

**Notas técnicas importantes:**
- sites.py sigue en el proyecto pero no está importado ni en urls ni en __init__.py, se puede borrar
- templatetags/__init__.py debe llamarse exactamente así (había un bug con el nombre invertido __init.py__)
- render.py usa GeneratedSite.objects.filter(...).first() en vez de getattr para evitar caché del ORM
- La migración de schema antiguo (formato mapping) a nuevo (formato fields) se hace automáticamente en preview.py

---

### Próximos pasos acordados

**1. Rediseño visual de WebBuilder** (siguiente inmediato)
- Todo oscuro, estilo herramienta SaaS moderna (referencia: linear.app, vercel.com)
- Fondo base #0a0a0f o #0f0f15
- Acentos azul eléctrico #2563eb o morado #7c3aed
- Cards con borde sutil rgba(255,255,255,0.08)
- Afecta a: home.html, assistant.html, preview.html, history.html y sus CSS

**2. Prompt de rediseño en el render** (momento 2 del flujo)
- Campo de texto en site_render.html para que el usuario describa el estilo que quiere
- Ya está implementado con los chips de hints (oscuro, minimalista, etc.)
- Pendiente de mejorar el prompt del themer para que genere diseños más ricos y adaptados al tipo de dato

**3. Generador de proyecto Django descargable** (objetivo final)
- Botón "Descargar proyecto" que genera un .zip con estructura real Django
- models.py con campos dinámicos según el schema
- views.py con lista y detalle
- urls.py, settings.py, manage.py
- Los templates del LLM escritos como archivos físicos
- Los datos de la API pre-cargados en la BD del proyecto descargable

**4. Mejoras pendientes menores**
- Navegación anterior/siguiente en la vista de detalle de items
- Indicador visual cuando el tema está desactualizado respecto al schema
- Historial de temas generados para poder volver atrás

---

### Archivos que NO tocar
- models.py — no hay migraciones pendientes, el JSONField ya soporta el nuevo schema
- utils/llm/client.py — cliente OpenRouter, no cambiar
- utils/analysis/ — detección de estructura, funciona bien
- utils/ingest/ — fetch y parse de URLs, funciona bien