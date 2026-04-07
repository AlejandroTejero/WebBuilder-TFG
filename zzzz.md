🗂️ Lista de mejoras ordenadas por utilidad
🔴 Imprescindibles para el TFG

Eliminar proyectos desde la cuenta — ahora mismo solo se puede desde /admin, lo cual es un bug de UX grave que cualquier evaluador notará. (Baja)
Páginas 404 y 500 personalizadas — dos templates con el estilo de WebBuilder en lugar de las páginas genéricas de Django. Lo notará cualquiera que navegue mal. (Baja)
Creación automática de usuario/superusuario al arrancar — un management command o señal en ready() para que la app arranque con datos. Imprescindible para demos y correcciones del TFG. (Baja)
Historial de versiones al regenerar — ahora sobreescribes project_files. Guardar snapshots antes de cada regeneración. El modelo GeneratedSite ya tiene la estructura, solo falta la lógica. (Media)
Preview de datos antes de analizar — ya tienes el flujo de ingestión, añadir un paso de vista previa antes de lanzar el análisis. Muy vistoso en demo. (Baja-Media)


🟠 Muy útiles y académicamente relevantes

Lectura de CSV y GeoJSON — ampliar parsers.py que ya soporta JSON/XML. Añadir dos formatos más amplía mucho el alcance del proyecto y da pie a un capítulo en la memoria. (Media)
Lectura de código directo — permitir pegar código como input además de URL o fichero. El modelo APIRequest ya tiene input_type, solo falta añadir la opción. (Media)
Dashboard de usuario — página de inicio personalizada con últimos análisis y proyectos. pages.py ya consulta recent_requests y recent_sites, es cuestión de diseñarlo bien. (Baja-Media)
Comparador de modelos LLM — lanzar el mismo análisis con dos modelos y ver resultados en paralelo. El LLMClient es agnóstico al modelo, así que es relativamente directo. Muy potente para defender el TFG académicamente. (Media)
Modo oscuro/claro — toggle CSS con prefers-color-scheme y una variable en localStorage. El proyecto ya está en oscuro, solo falta el switch. (Baja)


🟡 Mejoras de producto notables

Editor de código integrado (Monaco/CodeMirror) — ya tienes site_update_file implementado en el backend. Solo falta el frontend con el editor via CDN. Salto visual enorme. (Media)
Mejora visual global — adaptar el estilo monocromático del home al resto de vistas. Impacto alto en demo, trabajo principalmente de CSS/templates. (Media)
Panel de administración personalizado con métricas — extender el admin de Django con estadísticas reales (análisis por usuario, tasa de éxito del LLM…). El modelo GenerationLog ya guarda todo lo necesario. (Media)
Progress bar en tiempo real durante generación — GenerationLog ya tiene el campo step. Mostrar en la UI qué fichero está generando el LLM en cada momento con SSE o polling. (Media)
Chat de refinamiento post-generación — mini-chat para que el usuario pida cambios concretos y el LLM modifique solo el fichero relevante. Sería la funcionalidad estrella del TFG. (Alta)


🟢 Interesantes pero secundarias

Login con Google (OAuth2) — django-allauth lo hace en pocas líneas, pero requiere configurar credenciales en Google Cloud Console. (Media)
Votos y valoraciones sobre proyectos generados — requiere nuevo modelo, lógica y UI. Complementa bien la galería pública. (Media)
Galería pública de proyectos generados — listar GeneratedSite marcados como públicos con screenshot y enlace. Da vida al proyecto sin necesidad de registrarse. (Media-Alta)
Cambio de idioma (i18n) — django.middleware.locale + archivos .po. Tedioso pero estándar en Django. (Media)
IAs personalizadas / investigar OpenRouter — el client.py ya es compatible con cualquier endpoint OpenAI-compatible. Es más investigación que desarrollo. (Media)


⚫ Complejas o de largo plazo

Tests automáticos del código generado en contenedor efímero — levantar el proyecto generado en Docker, hacer una petición HTTP y verificar 200 OK. Infraestructura no trivial. (Muy Alta)
Thumbnails automáticos con Playwright/Puppeteer — screenshot automático del site desplegado para mostrarlo en el historial. Requiere microservicio o integración con n8n. (Alta)
Detección automática de paginación en APIs — detectar next, cursor, etc. y ofrecer cargar más datos. Requiere análisis heurístico del schema de respuesta. (Alta)