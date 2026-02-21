# Enlaces relacionados con el LLM
https://lmstudio.ai/
https://github.com/cheahjs/free-llm-api-resources
https://openrouter.ai/

# Enlaces de datos
JSON
https://jsonplaceholder.typicode.com/posts
https://dummyjson.com/users

XML
https://www.w3schools.com/xml/plant_catalog.xml
http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml

CSV
Buscar enlaces e implementar parseo

# Enlaces aprendizaje n8n

## Video despliegue en DOCKER
https://www.youtube.com/watch?v=oEfc5shhE6Q&utm_source=chatgpt.com

## Video 1
- n8n Beginner Course (2/9) – Introduction to APIs and Webhooks
- Te enseña justo lo que necesitas para tu arquitectura: recibir un evento (Webhook) y llamar a tu Django (HTTP request)
https://www.youtube.com/watch?v=y_cpFMF1pzk&utm_source=chatgpt.com

Qué mirar pensando en tu proyecto:
Cómo crear un Webhook Trigger que reciba un request_id
Cómo responder con un 200 rápido (y luego seguir el flujo en background)
Cómo estructurar el JSON que llega/sale (tu plan/mapping)
Concepto API vs Webhook (para defenderlo en el TFG)

## Video 2
- n8n Tutorial #5: Access any API using the HTTP Request Node
- Esto es clave para que n8n pueda llamar a endpoints de tu Django: /api/requests/<id>/generate, /api/requests/<id>/deploy, /api/requests/<id>/status, etc.
https://www.youtube.com/watch?v=4Ac5LlxNS8M&utm_source=chatgpt.com

Qué apuntar:
Auth (headers/bearer)
Manejo de respuestas JSON
Reintentos / timeouts
Cómo pasar datos entre nodos (expressions)

# Video 3
N8N Webhooks Masterclass: Beginner to Pro…
Más “práctico” y centrado en webhooks para que n8n actúe como “orquestador de backend”
https://www.youtube.com/watch?v=NcFOck4R6zw&utm_source=chatgpt.com