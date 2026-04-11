# Implementaciones esenciales
1. Ver si vale la pena sacar un history.html para lo repetido (HEADER)
2. Factorizar css para sacar cosas generales, ver si es necesario o no
3. Repasar que cada html no tiene css ni js inline
5. Apañar el modo claro de todo el proyecto



# Implementaciones paginas finales
1. Posibilidad de reseñas y comentarios para los usuarios creados
2. Chat de refinamiento post-generación: En lugar de solo regenerar el plan con un prompt, un mini-chat donde el usuario diga "quiero que la home tenga un hero más grande" o "añade un filtro por categoría" y el LLM modifique solo el fichero relevante.


# Implementaciones secundarias
1. Página 404 y 500 personalizadas: Templates html con el estilo de WebBuilder en vez de la página genérica de Django.
2. Dashboard de usuario: página personalizada al usuario, que muestre análisis, proyectos generados, etc
3. Editor de código integrado (tipo Monaco/CodeMirror)


# Implementaciones a preguntar
1. Exportación a otros formatos: Ahora exportas un proyecto Django. Podrías añadir opción de exportar como sitio estático (HTML/CSS/JS puro) para casos simples. Mucho más fácil de desplegar para usuarios no técnicos.


# Implementaciones n8n
1. Notificación cuando la generación termina — ahora mismo el usuario tiene que quedarse mirando la pantalla. Un email de "tu sitio está listo, descárgalo aquí" con el link directo sería muy natural y lo usarías de verdad.
2. Resumen semanal de uso — un workflow programado (cron) que cada semana envíe al admin cuántos sitios se generaron, con qué LLMs, tasa de error... Esto justifica n8n como herramienta de monitorización y es fácil de implementar.
3. Webhook de error de generación — si el pipeline falla, n8n alerta al admin. Útil en producción y muy fácil de argumentar en la memoria.

- De estos tres, el de notificación de generación completada es el que más valor visible aporta al usuario y el más fácil de conectar: ya tienes el estado generation_status = "ready" en la BD, solo necesitas que Django haga un POST a n8n cuando cambie a ese estado.


# Investigacion 
1. Prompting LLM: Investigar tecticas de prompting para añadir en la memoria