# Implementaciones esenciales

## Mejora visual
- Adaptar todo el proyecto al estilo del home (monocromatico con colores vivos en parte puqueñas)

## Mejora del historial y boton de eliminar proyectos 
- IMPORTANTE: Posibilidad de eliminar el pryoecto de la cuenta, que ahora solo se puede desde /admin.

## Lectura de datos
- Implementacion de lectura: CSV y GEOJson.
- Implementacion del codigo directo.

## Usuarios
- Introducir opcion de creacion automatica de usuario / super usuarios, para que al iniciar la pagina existan ya.
- Posibilidad de reseñas, comentarios y demas sobre los articulos.

## Botos y valoraciones
- No estaria mal que al crear la pagina indiques tu futuro usuario, y cuando se cree la pagina con login y 
todo puedas acceder, votar y todo lo demas

## IAs personalizadas
- Investigar la configuracion de las IA "bascias" - OpenRouter, OpenAI, etc. Para poder seguir el patron para una IA personalizada.

## Modo oscuro / claro - Idiomas
- La pagina esta creada en modo oscuro, tener la posibilidad de poner modo claro 
- Intentar poner boton de cambio de idioma

## Login con credenciales de google
- Que exista la posibilidad de poder iniciar sesion con google u otros mecanismos conocidos.

## Posibilidad de regenerar proyecto sin borrar el anterior
- Ahora mismo si regenero, sobreescribo. Guardar historial de versiones.



# Implementaciones secundarias

### Sencillo
1. Página 404 y 500 personalizadas — templates 404.html y 500.html con el estilo de WebBuilder en vez de la página genérica de Django.
2. Dashboard de usuario — página de inicio personalizada que muestre tus últimos análisis, proyectos generados y estado de despliegues de un vistazo
3. Preview de los datos antes de analizar.

### Medio 
4. Panel de administración personalizado — extender el admin de Django con estadísticas: cuántos análisis por usuario, tasa de éxito del LLM, modelos más usados. Útil para defender el TFG con métricas reales
5. Comparador de modelos LLM — permitir lanzar el mismo análisis con dos modelos distintos y ver los resultados en paralelo. Muy potente para el TFG, demuestra que el sistema es agnóstico al modelo
6. Editor de archivos generados antes de desplegar — ahora site_render.html ya tiene site_update_file, pero si hay un editor de código en la UI (tipo CodeMirror) el usuario podría retocar el código antes de hacer el ZIP o desplegar

### Dificiles
7. Galería pública de proyectos generados — que los usuarios puedan marcar un proyecto como público y aparecer en una galería con el tipo de sitio, la API de origen y un screenshot. Da vida al proyecto visualmente
8. Tests automáticos del código generado — después de generar el proyecto, ejecutarlo en un contenedor efímero y verificar que responde HTTP 200 antes de marcarlo como "ready". Cierra el loop de calidad end-to-end



# Investigacion 

## LLM de groq
- Buscar un LLM mas potente capaz de mejorar la vision de las paginas

## Prompting LLM
- Investigar tecticas de prompting para añadir en la memoria


# Claude (2, 3, 4, 5, 9)

1. Preview en vivo del sitio generado
Ahora mismo el usuario descarga un ZIP y tiene que levantarlo él. Con n8n ya tienes la infraestructura de despliegue montada — podrías mostrar un iframe dentro de la propia app con el site renderizado al momento. Muy vistoso en una demo del TFG.
2. Editor de código integrado (tipo Monaco/CodeMirror)
Tienes el endpoint site_update_file implementado pero el frontend seguramente es un textarea básico. Integrar Monaco Editor (el de VS Code) daría un salto visual enorme y es relativamente fácil de añadir vía CDN. Syntax highlighting, autocompletado, todo.
3. Chat de refinamiento post-generación
En lugar de solo regenerar el plan con un prompt, un mini-chat donde el usuario diga "quiero que la home tenga un hero más grande" o "añade un filtro por categoría" y el LLM modifique solo el fichero relevante. Sería la funcionalidad estrella del TFG.

⚡ Útiles y relativamente rápidas de implementar
4. Comparador de modelos LLM
Como ya soportas cualquier proveedor OpenAI-compatible, podrías añadir un modo "benchmark" que mande el mismo prompt a dos modelos distintos y muestre los resultados lado a lado. Muy relevante académicamente para el TFG.
5. Galería pública de sitios generados
Una página tipo showcase donde se listen los GeneratedSite marcados como públicos, con screenshot y enlace. Da contexto de lo que puede hacer la herramienta sin necesidad de registrarse.
6. Exportación a otros formatos
Ahora exportas un proyecto Django. Podrías añadir opción de exportar como sitio estático (HTML/CSS/JS puro) para casos simples. Mucho más fácil de desplegar para usuarios no técnicos.
7. Detección automática de paginación en la API
Si la API tiene next, page, cursor... detectarlo y ofrecer cargar más datos antes de generar el sitio. Ahora mismo imagino que solo procesas la primera respuesta.

🎨 Vistosas para la demo
8. Modo "paso a paso" animado
Una progress bar real que muestre en tiempo real qué fichero está generando el LLM en cada momento (ya tienes GenerationLog con el campo step). Hace que la espera sea mucho más engaging.
9. Historial de versiones del proyecto generado
Guardar snapshots de project_files antes de cada regeneración, con opción de volver a una versión anterior. Git-like pero sin Git.
10. Thumbnails automáticos del sitio generado
Usar Playwright o Puppeteer (desde n8n o un microservicio) para hacer un screenshot automático del site desplegado y mostrarlo en el historial. Transforma completamente cómo se ve la página de historial.