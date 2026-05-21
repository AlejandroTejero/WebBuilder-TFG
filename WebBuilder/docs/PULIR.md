# Errores e inconsistencias a pulir en WebBuilder

> Revisión centrada en fallos que un usuario podría notar durante el uso normal del proyecto: botones que no reflejan el estado real, redirecciones inesperadas, mensajes poco claros, flujos duplicados o estados incoherentes entre asistente, editor, visor de código, despliegue y n8n.

## Prioridad alta

### 1. El selector de LLM vuelve a mostrarse como “Predeterminado” aunque el usuario elija otro modelo

**Síntoma para el usuario**  
El usuario abre el modal, elige por ejemplo `Qwen3 Coder` o `Llama 3.3`, pero después de analizar/regenerar la página vuelve a mostrar “Modelo: Predeterminado”. Da la sensación de que la selección no se ha aplicado.

**Causa probable**  
En `WebBuilder/templates/WebBuilder/partials/assistant/input.html`, el texto del botón está hardcodeado como `Predeterminado`:

```html
{% trans "Modelo:" %} <span id="llm-label-display">{% trans "Predeterminado" %}</span>
```

Además, en `WebBuilder/templates/WebBuilder/assistant.html`, la opción `Predeterminado` aparece siempre marcada con `llm-modal__option--selected`, independientemente de `selected_llm_choice`.

**Archivos implicados**

- `WebBuilder/templates/WebBuilder/partials/assistant/input.html`
- `WebBuilder/templates/WebBuilder/assistant.html`
- `WebBuilder/static/js/assistant.js`
- `WebBuilder/views/assistant.py`

**Qué pulir**

- Calcular una etiqueta real para el modelo seleccionado en backend o template.
- Pintar el botón con el modelo seleccionado.
- Marcar `Predeterminado`, `Elegir modelo` o la card concreta según `selected_llm_choice`.
- Evitar que el estado visual diga una cosa y el input oculto tenga otra.

**Prueba recomendada**

1. Entrar al asistente.
2. Elegir manualmente `Qwen3 Coder`.
3. Analizar una API.
4. Comprobar que el botón sigue mostrando `Qwen3 Coder` después del render.
5. Regenerar schema y confirmar que se mantiene.

---

### 2. La elección del LLM solo afecta al schema, no a la generación final del código

**Síntoma para el usuario**  
Aunque el usuario seleccione otro modelo, la generación final del proyecto Django puede seguir usando el modelo definido en `.env` como `LLM_MODEL`. Esto hace que la selección parezca decorativa o parcialmente funcional.

**Causa probable**  
En `WebBuilder/views/assistant.py`, `_resolve_llm()` se usa para generar el plan/schema. Sin embargo, en la generación final, `WebBuilder/utils/generator/llm_wrappers.py` llama a `chat_completion()` sin pasar `model`, `base_url` ni `api_key`, por lo que se usan los valores globales de `settings`.

También `GenerationLog` guarda `settings.LLM_MODEL`, no el modelo realmente seleccionado por el usuario.

**Archivos implicados**

- `WebBuilder/views/assistant.py`
- `WebBuilder/views/edit.py`
- `WebBuilder/utils/generator/llm_wrappers.py`
- `WebBuilder/utils/generator/project_generator.py`
- `WebBuilder/utils/generator/notifications.py`
- `WebBuilder/models.py`

**Qué pulir**

- Guardar en `field_mapping` o en `GeneratedSite` el modelo elegido: `llm_choice`, `llm_model`, `llm_base_url`.
- Pasar esos datos a `generate_project_files()`.
- Hacer que `llm_call()`, `llm_call_logged()` y `notify_generation_done()` usen el modelo real del sitio.
- Mostrar en métricas y en la pantalla de sitio el modelo realmente usado.

**Prueba recomendada**

1. Elegir un modelo distinto al predeterminado.
2. Generar el schema.
3. Publicar el sitio.
4. Revisar `GenerationLog.llm_model`.
5. Confirmar que coincide con la selección del usuario.

---

### 3. El selector ofrece modelos de distintos proveedores, pero solo usa una API key global

**Síntoma para el usuario**  
El usuario puede elegir un modelo de Groq u OpenRouter, pero si la API key configurada pertenece a otro proveedor, la petición falla. Desde la interfaz no queda claro por qué un modelo “disponible” no funciona.

**Causa probable**  
En `WebBuilder/utils/llm/llm_catalog.py`, cada modelo tiene su `base_url`, pero en `WebBuilder/views/assistant.py` todos los modelos del catálogo usan `settings.LLM_API_KEY`.

**Archivos implicados**

- `WebBuilder/utils/llm/llm_catalog.py`
- `WebBuilder/views/assistant.py`
- `.env.example`
- `project/settings.py`

**Qué pulir**

- Opción simple: dejar en catálogo solo modelos del proveedor configurado.
- Opción mejor: añadir claves separadas, por ejemplo `OPENROUTER_API_KEY` y `GROQ_API_KEY`.
- Mostrar en el modal si un proveedor no está configurado.
- Evitar que el usuario pueda seleccionar modelos que no tienen credenciales válidas.

---

### 4. El modelo personalizado está soportado en backend, pero no se puede seleccionar realmente desde el modal

**Síntoma para el usuario**  
El modal muestra “Modelo personalizado”, pero al pulsarlo manda al perfil. Incluso si el usuario ya lo tiene configurado, no parece haber una forma clara de decir: “usa mi modelo personalizado para este análisis”.

**Causa probable**  
`_resolve_llm()` soporta `llm_choice == "custom"`, pero en el modal el bloque de modelo personalizado hace `window.location.href='{% url 'profile' %}'` en lugar de llamar a `setLLMValue('custom', ...)`.

**Archivos implicados**

- `WebBuilder/templates/WebBuilder/assistant.html`
- `WebBuilder/static/js/assistant.js`
- `WebBuilder/views/assistant.py`
- `WebBuilder/templates/WebBuilder/profile.html`

**Qué pulir**

- Si el perfil tiene modelo configurado, permitir seleccionarlo directamente.
- Si no está configurado, entonces sí mandar al perfil.
- Mostrar una etiqueta clara: `Modelo personalizado: <nombre>`.

---

### 5. A veces “Ver código” puede mandar al login o no devolver al usuario a la página esperada

**Síntoma para el usuario**  
El usuario está trabajando, pulsa “Ver código” y se encuentra en login. Aunque esto pueda deberse a sesión/cookie, desde UX parece que la app “olvida” que el usuario estaba registrado.

**Causas probables a revisar**

1. `site_code_viewer` está protegido con `@login_required`, lo cual es correcto, pero si la sesión no llega por cookie se redirige a login.
2. El formulario de login usa `action="{% url 'login' %}"`, por lo que si el usuario llega a `/login?next=/site/1/codigo/`, al enviar el formulario puede perderse el parámetro `next`.
3. Si se alterna entre `localhost`, `127.0.0.1` u otro host/puerto, la cookie de sesión puede no coincidir.
4. En despliegue WSGI/ASGI, `.env` no se carga explícitamente como en `manage.py`; si `SECRET_KEY` no está bien configurada, las sesiones pueden fallar o invalidarse.

**Archivos implicados**

- `WebBuilder/views/site.py`
- `WebBuilder/templates/WebBuilder/site_render.html`
- `WebBuilder/templates/registration/login.html`
- `project/settings.py`
- `project/wsgi.py`
- `project/asgi.py`

**Qué pulir**

- En login, mantener el parámetro `next`:

```html
<form method="post" action="{{ request.get_full_path }}" class="auth-fields" novalidate>
```

  o añadir un hidden:

```html
<input type="hidden" name="next" value="{{ request.GET.next }}">
```

- Revisar que siempre se accede con el mismo host: `localhost` o `127.0.0.1`, pero no mezclados.
- Cargar `.env` también en `wsgi.py` y `asgi.py`, o asegurar variables reales en el entorno.
- Si el usuario no tiene sesión, mostrar mensaje claro: “Tu sesión ha caducado, inicia sesión para volver al código”.

**Prueba recomendada**

1. Entrar por `http://localhost:8000`.
2. Generar un sitio.
3. Pulsar “Ver código”.
4. Repetir entrando por `http://127.0.0.1:8000`.
5. Comprobar si en uno de los dos casos se pierde sesión.

---

### 6. La página de “Ver código” parece corrupta: contiene CSS de historial pegado dentro del HTML

**Síntoma para el usuario**  
Al abrir el visor de código pueden aparecer textos raros, estilos rotos o una página visualmente incoherente.

**Causa probable**  
En `WebBuilder/templates/WebBuilder/code_viewer.html`, después del modal aparece CSS de `history.css` pegado directamente en el body, sin etiqueta `<style>` ni archivo CSS separado. Empieza justo después de:

```html
</div>/* =============================================================
   WebBuilder — Historial (history.css)
```

**Archivo implicado**

- `WebBuilder/templates/WebBuilder/code_viewer.html`

**Qué pulir**

- Eliminar todo el CSS pegado accidentalmente dentro de `code_viewer.html`.
- Mantener los estilos solo en `WebBuilder/static/css/code_viewer.css`.
- Revisar visualmente el visor tras limpiar el template.

---

### 7. El modo fichero usa la caché de URL y puede reutilizar datos de otro fichero

**Síntoma para el usuario**  
El usuario sube un fichero distinto, pero el análisis puede salir con datos anteriores o incoherentes. También el historial puede mostrar entradas sin URL clara.

**Causa probable**  
En `WebBuilder/views/assistant.py`, el `cache_key` se calcula siempre con `api_url`:

```python
cache_key = _get_cache_key(api_url)
```

Si el usuario trabaja en modo fichero y `api_url` está vacío, todos los ficheros comparten la misma clave de caché basada en string vacío.

**Archivos implicados**

- `WebBuilder/views/assistant.py`
- `WebBuilder/forms.py`
- `WebBuilder/models.py`
- `WebBuilder/templates/WebBuilder/partials/assistant/input.html`

**Qué pulir**

- Separar claramente `input_type = url/file` antes de calcular caché.
- Para ficheros, usar hash del contenido o desactivar caché.
- Guardar `file_name` en `APIRequest` para historial y depuración.
- No crear `APIRequest` con `api_url=""` sin una representación clara del fichero.

**Prueba recomendada**

1. Subir `datos_a.json`.
2. Subir `datos_b.json` totalmente distinto.
3. Confirmar que el segundo análisis no reutiliza nada del primero.

---

### 8. La validación frontend del formulario no bloquea bien el envío

**Síntoma para el usuario**  
El usuario introduce una URL inválida o no sube fichero, ve un comportamiento raro: puede salir overlay, recargar la página o mostrarse error tarde.

**Causa probable**  
El botón usa:

```html
onclick="showLoading()"
```

pero `showLoading()` devuelve `false` en algunos casos y ese valor no se retorna al navegador. Para que bloquee el submit debería ser:

```html
onclick="return showLoading()"
```

Además, en modo fichero no se valida en frontend que realmente haya fichero.

**Archivos implicados**

- `WebBuilder/static/js/assistant.js`
- `WebBuilder/templates/WebBuilder/partials/assistant/input.html`

**Qué pulir**

- Cambiar a `onsubmit` del formulario en vez de `onclick` del botón.
- Validar URL si el modo activo es URL.
- Validar fichero si el modo activo es fichero.
- Cambiar el texto del botón según modo: “Analizar URL” / “Analizar fichero”.

---

### 9. Se aceptan CSV y GeoJSON, pero parte de la interfaz sigue diciendo solo JSON/XML

**Síntoma para el usuario**  
El input permite `.csv` y `.geojson`, y el parser también contempla esos formatos, pero varios textos dicen que solo soporta JSON y XML. Esto genera duda sobre qué formatos son reales.

**Archivos implicados**

- `WebBuilder/forms.py`
- `WebBuilder/utils/ingest/parsers.py`
- `WebBuilder/templates/WebBuilder/partials/assistant/input.html`
- `README.md`
- Memoria del TFG, si se menciona soporte de formatos.

**Qué pulir**

- Cambiar textos a “JSON, XML, CSV y GeoJSON”.
- Revisar ejemplos y validaciones.
- Confirmar si GeoJSON se normaliza bien.

**Detalle técnico**

La detección de GeoJSON intenta hacer `json.loads(trimmed[:500])`. En muchos GeoJSON reales, los primeros 500 caracteres no son un JSON completo válido, por lo que puede detectarse como JSON genérico y no como GeoJSON.

---

### 10. Acceder manualmente a `/site/<id>` antes de crear un sitio puede provocar estado roto

**Síntoma para el usuario**  
Si alguien abre una URL de sitio generado antes de haber aceptado/publicado el plan, puede aparecer error interno o una pantalla incoherente.

**Causa probable**  
En `WebBuilder/views/site.py`, `site_render()` hace:

```python
site, _ = GeneratedSite.objects.get_or_create(project_source=api_request)
```

pero `GeneratedSite.accepted_plan` es obligatorio y no tiene default en el modelo.

**Archivos implicados**

- `WebBuilder/views/site.py`
- `WebBuilder/models.py`

**Qué pulir**

- No usar `get_or_create()` en `site_render()` sin defaults válidos.
- Si no existe sitio, redirigir al editor con mensaje: “Primero debes publicar el schema”.
- O añadir `default=dict`/`blank=True` a `accepted_plan`, si tiene sentido.

---

### 11. Guardar usuarios puede crear un `GeneratedSite` falso antes de publicar

**Síntoma para el usuario**  
El usuario guarda usuarios de la app antes de publicar el sitio. Esto puede crear un registro de sitio aunque aún no exista proyecto generado. Después puede aparecer en historial como “sitio publicado” o generar estados raros.

**Causa probable**  
En `site_users_save()`, se hace:

```python
site, _ = GeneratedSite.objects.get_or_create(
    project_source=api_request,
    defaults={"accepted_plan": False}
)
```

`accepted_plan=False` es JSON válido, pero semánticamente no es un plan.

**Archivos implicados**

- `WebBuilder/views/site.py`
- `WebBuilder/templates/WebBuilder/edit.html`
- `WebBuilder/static/js/edit.js`
- `WebBuilder/views/history.py`

**Qué pulir**

- No crear `GeneratedSite` al guardar usuarios si el plan no está publicado.
- Guardar usuarios temporalmente en otro modelo asociado al análisis, o exigir que exista `GeneratedSite` real.
- Evitar que `history_sites` cuente sitios sin generación real.

---

### 12. Contraseñas de usuarios del sitio generado guardadas y mostradas en claro

**Síntoma para el usuario/profesor**  
En el editor aparecen contraseñas ya guardadas dentro de inputs de tipo password, pero el valor está en la base de datos en claro. Para un TFG puede ser aceptable como demo, pero conviene justificarlo o pulirlo.

**Archivos implicados**

- `WebBuilder/models.py`
- `WebBuilder/templates/WebBuilder/edit.html`
- `WebBuilder/views/site.py`

**Qué pulir**

- Indicar claramente que son credenciales semilla para el proyecto generado.
- Mejor opción: no mostrar la contraseña ya guardada; permitir “reemplazar contraseña”.
- Si se mantienen, documentarlo como limitación.

---

### 13. Los mensajes globales están comentados en `base.html`

**Síntoma para el usuario**  
Algunas acciones hacen `messages.success()` o `messages.error()`, pero en determinadas páginas no se ve nada. El usuario pulsa un botón y no sabe si funcionó.

**Causa probable**  
En `WebBuilder/templates/WebBuilder/base.html`, el bloque global de mensajes está comentado.

**Archivo implicado**

- `WebBuilder/templates/WebBuilder/base.html`

**Qué pulir**

- Restaurar un componente global de mensajes bonito y no intrusivo.
- Evitar duplicarlo en todas las páginas.
- Mantener mensajes específicos solo cuando aporten contexto extra.

---

### 14. Hay dos caminos de generación de proyecto con comportamientos distintos

**Síntoma para el usuario/desarrollador**  
Dependiendo de si se genera desde el editor o desde el endpoint `/site/<id>/generate/`, pueden cambiar logs, snapshots, notificaciones y estados.

**Causa probable**  
Hay generación en:

- `WebBuilder/views/edit.py`, dentro de `action == "accept_plan"`.
- `WebBuilder/views/site.py`, en `site_generate()` y `_run_generation()`.

Pero no hacen exactamente lo mismo. Por ejemplo, `_run_generation()` notifica a n8n con `notify_generation_done()`, mientras que el flujo principal desde el editor no lo hace.

**Archivos implicados**

- `WebBuilder/views/edit.py`
- `WebBuilder/views/site.py`
- `WebBuilder/utils/generator/project_generator.py`
- `WebBuilder/utils/generator/notifications.py`

**Qué pulir**

- Centralizar la generación en una única función/servicio.
- Que todos los flujos creen snapshots igual.
- Que todos los flujos notifiquen igual a n8n.
- Eliminar endpoints no usados o conectarlos claramente a la interfaz.

---

### 15. El botón “Regenerar diseño” llama a una función JavaScript inexistente

**Síntoma para el usuario**  
Al pulsar “Regenerar diseño”, puede no aparecer el overlay esperado o salir error en consola.

**Causa probable**  
En `WebBuilder/templates/WebBuilder/edit.html` aparece:

```html
onclick="showPublishLoading()"
```

pero en `WebBuilder/static/js/edit.js` no existe una función `showPublishLoading()`.

**Archivos implicados**

- `WebBuilder/templates/WebBuilder/edit.html`
- `WebBuilder/static/js/edit.js`

**Qué pulir**

- Eliminar el `onclick` o implementar la función.
- Usar el mismo sistema de overlay/polling que el formulario inicial `publish-form`.
- Añadir `id="publish-form"` o una clase común a ambos formularios de publicación/regeneración.

---

### 16. La URL de preview del workflow n8n está hardcodeada a `localhost`

**Síntoma para el usuario**  
Si WebBuilder se usa desde otra máquina, una VM, Docker o una demo remota, el enlace de preview puede abrir `http://localhost:<puerto>` en el ordenador del usuario, no en el servidor donde corre Docker.

**Causa probable**  
En el workflow `webbuilder - deploy`, el nodo de elección de puerto construye:

```js
preview_url: `http://localhost:${port}`
```

**Archivos implicados**

- `WorkFlows/webbuilder - deploy.json`
- `WebBuilder/views/site.py`
- `.env.example`

**Qué pulir**

- Añadir variable `PREVIEW_BASE_URL`, por ejemplo `http://localhost` en local o dominio/IP en demo.
- Enviar esa base al workflow o configurarla en n8n.
- Mostrar error claro si `preview_url` no es accesible.

---

## Prioridad media

### 17. El historial llama “Publicado” a sitios que pueden no estar generados ni desplegados

**Síntoma para el usuario**  
En historial, “Publicado” puede confundirse con “generado”, “desplegado” o “plan aceptado”. Son estados distintos.

**Archivos implicados**

- `WebBuilder/templates/WebBuilder/partials/history/recent_analysis.html`
- `WebBuilder/templates/WebBuilder/partials/history/published_sites.html`
- `WebBuilder/views/history.py`

**Qué pulir**

Usar etiquetas separadas:

- `Schema generado`
- `Plan aceptado`
- `Código generado`
- `Desplegado`
- `Error de generación`

---

### 18. La pantalla de sitio generado muestra estados técnicos en inglés

**Síntoma para el usuario**  
En la sidebar aparece `ready`, `generating`, `pending`, `error`, etc. Esto rompe el tono visual del resto de la app.

**Archivo implicado**

- `WebBuilder/templates/WebBuilder/site_render.html`

**Qué pulir**

Mapear estados a etiquetas legibles:

- `pending` → `Pendiente`
- `generating` → `Generando`
- `ready` → `Listo`
- `error` → `Error`

---

### 19. El botón “Ver código” está demasiado escondido visualmente

**Síntoma para el usuario**  
Una acción importante aparece con `font-size:11px` y `opacity:.6`, por lo que puede parecer secundaria o deshabilitada.

**Archivo implicado**

- `WebBuilder/templates/WebBuilder/site_render.html`

**Qué pulir**

- Darle estilo equivalente a “Descargar ZIP”.
- Añadir texto de ayuda: “Revisa y edita los archivos generados”.
- No reducir opacidad si está disponible.

---

### 20. Varios enlaces de ayuda/documentación no hacen nada

**Síntoma para el usuario**  
El menú “Ayuda” y enlaces de footer parecen funcionales, pero llevan a `#`. Esto da sensación de prototipo incompleto.

**Archivos implicados**

- `WebBuilder/templates/WebBuilder/navbar.html`
- `WebBuilder/templates/WebBuilder/partials/home/cta.html`

**Qué pulir**

- O crear páginas reales de documentación/FAQ/contacto.
- O quitar temporalmente esos enlaces.
- O mostrar un modal simple “Próximamente”.

---

### 21. El README no está alineado con el estado actual del proyecto

**Síntoma para evaluación/entrega**  
El README dice que la base de datos es SQLite, pero `settings.py` usa PostgreSQL. También habla sobre todo de URL JSON/XML, mientras que el proyecto ya incluye fichero, CSV, GeoJSON, despliegue y métricas.

**Archivos implicados**

- `README.md`
- `project/settings.py`
- `.env.example`

**Qué pulir**

- Actualizar stack real.
- Añadir pasos de instalación.
- Añadir variables de entorno completas.
- Explicar cómo arrancar Django, PostgreSQL, n8n y Docker.

---

### 22. Falta un `requirements.txt` o equivalente

**Síntoma para evaluación/entrega**  
Al descomprimir el proyecto no hay forma directa de instalar dependencias. En una revisión limpia, `python manage.py check` no puede ejecutarse sin preparar manualmente el entorno.

**Qué pulir**

Crear `requirements.txt` con dependencias mínimas, por ejemplo:

```txt
Django==5.1.7
python-dotenv
requests
xmltodict
defusedxml
django-encrypted-model-fields
psycopg2-binary
```

Ajustar versiones reales según tu entorno.

---

### 23. `.env.example` está incompleto

**Síntoma para evaluación/entrega**  
El ejemplo solo contiene variables LLM. Faltan variables de base de datos, n8n, token interno, rutas de despliegue y secret key.

**Archivo implicado**

- `.env.example`

**Qué pulir**

Añadir al menos:

```env
SECRET_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
N8N_WEBHOOK_REGISTRO=
N8N_WEBHOOK_LOGIN=
N8N_DEPLOY_WEBHOOK=
N8N_WEBHOOK_GENERATION_DONE=
N8N_LOCAL_FILES_PATH=
INTERNAL_TOKEN=
PREVIEW_BASE_URL=http://localhost
```

---

### 24. El zip del proyecto contiene archivos que no deberían entregarse

**Riesgo**  
En el zip aparecen `.env`, `db.sqlite3`, `backup_sqlite.json`, `.git`, `.idea`, `__pycache__` y un archivo vacío llamado `git`.

**Qué pulir**

Preparar un zip limpio de entrega:

- Sin `.env` real.
- Sin base de datos local.
- Sin backups pesados.
- Sin `.git` ni `.idea`.
- Sin `__pycache__`.
- Con `.env.example`, `requirements.txt` y README actualizado.

---

### 25. Los endpoints internos quedan inseguros si `INTERNAL_TOKEN` no está configurado

**Síntoma/riesgo**  
Si `INTERNAL_TOKEN` está vacío, `_check_token()` compara el header vacío con el setting vacío, por lo que una petición sin token podría pasar.

**Archivo implicado**

- `WebBuilder/views/internal.py`

**Qué pulir**

Cambiar la comprobación para que un token vacío nunca sea válido:

```python
def _check_token(request) -> bool:
    expected = getattr(settings, "INTERNAL_TOKEN", "")
    received = request.headers.get("X-Internal-Token", "")
    return bool(expected) and received == expected
```

---

### 26. El auto-shutdown identifica sitios solo por `project_name`

**Síntoma/riesgo**  
Si dos usuarios generan sitios con el mismo título, pueden compartir `project_name`. Al apagar un contenedor, se puede marcar como idle el sitio equivocado.

**Archivo implicado**

- `WebBuilder/views/internal.py`
- `WorkFlows/webbuilder - auto-shutdown.json`

**Qué pulir**

- Incluir `site_id` o `public_id` en el nombre del contenedor.
- Guardar `container_name` en `GeneratedSite`.
- Buscar por `container_name`, no solo por `project_name`.

---

### 27. El workflow n8n ejecuta comandos Docker con variables sin escapado fuerte

**Riesgo**  
Aunque `project_name` suele venir de `slugify`, los comandos como `docker build -t ${containerName}:latest ${buildDir}` y `docker run ...` son frágiles si alguna variable contiene caracteres inesperados o espacios.

**Archivo implicado**

- `WorkFlows/webbuilder - deploy.json`

**Qué pulir**

- Validar estrictamente `container_name`, `deploy_dir` y `project_name`.
- Usar listas de argumentos o quoting robusto si se mantiene `execSync`.
- Rechazar cualquier valor que no coincida con una regex segura.

---

### 28. El editor de código depende de CDNs externos

**Síntoma para el usuario**  
Si no hay internet o falla CDN, Prism/Monaco pueden no cargar y el visor/editor de código pierde funcionalidad.

**Archivo implicado**

- `WebBuilder/templates/WebBuilder/code_viewer.html`

**Qué pulir**

- Añadir fallback visual si Monaco no carga.
- Considerar servir assets locales para defensa/demo.
- Mostrar mensaje claro: “No se pudo cargar el editor”.

---

### 29. Algunos textos tienen pequeños errores o tono inconsistente

**Ejemplos detectados**

- `Introduzca la la URL o fichero de datos` → sobra un “la”.
- `boton` → debería ser `botón`.
- `Reset` → mejor `Restablecer` o `Deshacer cambios`.
- Mezcla de `schema`, `mapa`, `plan`, `sitio publicado`, `diseño generado`.

**Archivos implicados**

- `WebBuilder/templates/WebBuilder/partials/assistant/input.html`
- `WebBuilder/templates/WebBuilder/partials/assistant/preview.html`
- `WebBuilder/templates/WebBuilder/edit.html`
- `WebBuilder/templates/WebBuilder/site_render.html`

**Qué pulir**

Unificar vocabulario:

- `Schema` para campos detectados.
- `Plan` para propuesta completa de la IA.
- `Proyecto generado` para código Django.
- `Despliegue` para Docker/n8n.

---

## Checklist rápido de pruebas manuales

### Flujo URL

- [ ] Login con usuario normal.
- [ ] Analizar una URL JSON.
- [ ] Elegir LLM no predeterminado.
- [ ] Confirmar que el botón mantiene el modelo elegido.
- [ ] Regenerar schema.
- [ ] Editar campos.
- [ ] Guardar schema.
- [ ] Generar sitio.
- [ ] Abrir “Ver código”.
- [ ] Editar un archivo y guardar.
- [ ] Descargar ZIP.
- [ ] Desplegar.
- [ ] Abrir preview.

### Flujo fichero

- [ ] Subir JSON.
- [ ] Subir CSV.
- [ ] Subir GeoJSON.
- [ ] Repetir con dos ficheros distintos y comprobar que no se reutiliza caché.
- [ ] Confirmar que el historial muestra nombre de fichero o descripción clara.

### Sesión/login

- [ ] Entrar por `localhost` y probar “Ver código”.
- [ ] Entrar por `127.0.0.1` y repetir.
- [ ] Forzar logout y entrar a `/site/<id>/codigo/`.
- [ ] Confirmar que tras login vuelve a la URL original.

### Estados

- [ ] Abrir `/site/<id>` antes de publicar y confirmar que no da 500.
- [ ] Guardar usuarios antes de publicar y confirmar que no crea un sitio falso.
- [ ] Regenerar diseño y confirmar overlay/polling.
- [ ] Revisar historial: los estados deben distinguir schema, generación y despliegue.

## Orden sugerido de arreglo

1. Arreglar selector LLM visual y propagación del modelo a generación final.
2. Limpiar `code_viewer.html`.
3. Corregir login `next` y revisar sesión/host.
4. Separar flujo URL/fichero y caché.
5. Evitar creación de `GeneratedSite` falso.
6. Centralizar generación en un único servicio.
7. Actualizar README, `.env.example` y crear `requirements.txt`.
8. Limpiar zip de entrega.
9. Pulir textos, estados y enlaces muertos.