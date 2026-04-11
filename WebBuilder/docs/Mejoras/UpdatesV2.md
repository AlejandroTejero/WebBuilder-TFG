# Implementaciones esenciales
1. Ver si vale la pena sacar un history.html para lo repetido (HEADER)
2. Factorizar css para sacar cosas generales, ver si es necesario o no
3. Repasar que cada html no tiene css ni js inline
4. Terminar de traducir todo el contenido
5. Apañar el modo claro de todo el proyecto

6. Preview en vivo del sitio generado, ver si merece la pena o con el auto-despligue es suficiente


# Implementaciones paginas finales
1. Posibilidad de reseñas y comentarios para los usuarios creados
2. Chat de refinamiento post-generación: En lugar de solo regenerar el plan con un prompt, un mini-chat donde el usuario diga "quiero que la home tenga un hero más grande" o "añade un filtro por categoría" y el LLM modifique solo el fichero relevante.


# Implementaciones secundarias
1. Página 404 y 500 personalizadas: Templates html con el estilo de WebBuilder en vez de la página genérica de Django.
2. Dashboard de usuario: página personalizada al usuario, que muestre análisis, proyectos generados, etc
3. Editor de código integrado (tipo Monaco/CodeMirror)


# Implementaciones a preguntar
1. Exportación a otros formatos: Ahora exportas un proyecto Django. Podrías añadir opción de exportar como sitio estático (HTML/CSS/JS puro) para casos simples. Mucho más fácil de desplegar para usuarios no técnicos.


# Investigacion 
1. Prompting LLM: Investigar tecticas de prompting para añadir en la memoria