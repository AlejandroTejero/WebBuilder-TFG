# Implementaciones esenciales

0. Separar bien los css, aplicar a cada html su css/js y no cargar todo en base, y hacer un base.css con los colores root de todo el proyecto.

1. Mejora visual de proyecto: Adapar todo el proyecto al estilo del home (monocromatico y algo de color), terminar 
de traducir el contenido y acicalar el modo claro.
2. Lectura de datos: Implementar lectura CSV, GEOJson, y posibilidad de meter codigo directo.
3. Reseñas y comentarios: Actualmente existen los usuarios, pero hay que meterles cosas que poder hacer (votos / valoraciones).
4. Login con credenciales de google.
5. Preview en vivo del sitio generado, ver si merece la pena o con el auto-despligue es suficiente

6. Chat de refinamiento post-generación: En lugar de solo regenerar el plan con un prompt, un mini-chat donde el usuario diga "quiero que la home tenga un hero más grande" o "añade un filtro por categoría" y el LLM modifique solo el fichero relevante.
7. Conectar los "generando proyecto" con los pasos de verdad, para saber el progreso y no un progreso inventado.


# Implementaciones secundarias
1. Página 404 y 500 personalizadas: Templates html con el estilo de WebBuilder en vez de la página genérica de Django.
2. Dashboard de usuario: página personalizada al usuario, que muestre análisis, proyectos generados, etc
3. Editor de código integrado (tipo Monaco/CodeMirror)


# Implementaciones a preguntar
1. Exportación a otros formatos: Ahora exportas un proyecto Django. Podrías añadir opción de exportar como sitio estático (HTML/CSS/JS puro) para casos simples. Mucho más fácil de desplegar para usuarios no técnicos.


# Investigacion 
1. Prompting LLM: Investigar tecticas de prompting para añadir en la memoria


# Refactors

- Vale la pena hacer ahora:
1. template_examples.py (703 líneas) es el archivo más largo del backend. Contiene los ejemplos few-shot para los prompts del LLM. No tiene lógica compleja, pero está todo mezclado en un solo fichero. Separarlo por tipo de página (list, detail, base, etc.) lo  haría mucho más navegable y fácil de ampliar, que es algo que claramente vas a seguir haciendo.
2. generator_prompts.py (404 líneas) tiene todos los prompts de generación juntos. Está bien organizado con funciones separadas, pero cada prompt es largo y el archivo es denso. Se podría separar en prompts/pages.py, prompts/models.py, prompts/views.py, etc. siguiendo la misma lógica que ya tiene internamente.


- Tiene menos urgencia pero está bien saberlo:
1. site.py (362 líneas) está bien estructurado. _run_generation y _run_deploy son las únicas funciones densas, pero tienen responsabilidades claras y no mezclan cosas. No lo tocaría.
2. edit.py y metrics.py están en un tamaño razonable y bien organizados. No necesitan nada.
3. planner.py (279 líneas) es el corazón del análisis LLM. Está bastante bien, solo _validate_and_normalize_schema es algo larga pero hace una sola cosa.


- No tocaría:
1. Todo utils/analysis/, utils/ingest/, views/auth.py, views/history.py, views/helpers.py — están en tamaños correctos y bien separados.