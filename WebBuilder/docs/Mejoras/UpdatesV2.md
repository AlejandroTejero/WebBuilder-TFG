# Implementaciones esenciales
0. Separar bien los css, aplicar a cada html su css/js y no cargar todo en base, y hacer un base.css con los colores root de todo el proyecto.
1. Mejora visual de proyecto: Adapar todo el proyecto al estilo del home (monocromatico y algo de color), terminar 
de traducir el contenido y acicalar el modo claro.
2. Reseñas y comentarios: Actualmente existen los usuarios, pero hay que meterles cosas que poder hacer (votos / valoraciones).
3. Login con credenciales de google.
4. Preview en vivo del sitio generado, ver si merece la pena o con el auto-despligue es suficiente
5. Chat de refinamiento post-generación: En lugar de solo regenerar el plan con un prompt, un mini-chat donde el usuario diga "quiero que la home tenga un hero más grande" o "añade un filtro por categoría" y el LLM modifique solo el fichero relevante.


# Implementaciones secundarias
1. Página 404 y 500 personalizadas: Templates html con el estilo de WebBuilder en vez de la página genérica de Django.
2. Dashboard de usuario: página personalizada al usuario, que muestre análisis, proyectos generados, etc
3. Editor de código integrado (tipo Monaco/CodeMirror)


# Implementaciones a preguntar
1. Exportación a otros formatos: Ahora exportas un proyecto Django. Podrías añadir opción de exportar como sitio estático (HTML/CSS/JS puro) para casos simples. Mucho más fácil de desplegar para usuarios no técnicos.


# Investigacion 
1. Prompting LLM: Investigar tecticas de prompting para añadir en la memoria