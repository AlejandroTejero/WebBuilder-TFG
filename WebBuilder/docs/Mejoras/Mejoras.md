# Implementaciones esenciales

## Mejora del historial y boton de eliminar proyectos 
- Añadir paginacion, busqueda por filtros, es decir, hacerlo bonito y util
- IMPORTANTE: Posibilidad de eliminar el pryoecto de la cuenta, que ahora solo se puede desde /admin.

## Lectura de datos
- Implementacion de lectura: CSV y GEOJson.
- Implementacion de adjuntar ficheros, no solo a traves de enlace.
- Implementacion del codigo directo.

## Usuarios
- Introducir opcion de creacion automatica de usuario / super usuarios, para que al iniciar la pagina existan ya.
- Posibilidad de reseñas, comentarios y demas sobre los articulos.

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