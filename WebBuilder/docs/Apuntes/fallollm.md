(entorno) alejandro@alejandrotejero:~/Desktop/TFG/WebBuilder/project$ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 02, 2026 - 16:06:02
Django version 5.2.6, using settings 'project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.
For more information on production servers see: https://docs.djangoproject.com/en/5.2/howto/deployment/
[02/Mar/2026 16:06:46] "GET / HTTP/1.1" 200 26494
[02/Mar/2026 16:06:48] "GET /asistente HTTP/1.1" 302 0
[02/Mar/2026 16:06:48] "GET /login?next=/asistente HTTP/1.1" 200 3703
[02/Mar/2026 16:06:52] "POST /login HTTP/1.1" 302 0
[02/Mar/2026 16:06:52] "GET / HTTP/1.1" 200 34323
[02/Mar/2026 16:06:53] "GET /asistente HTTP/1.1" 200 16066
[02/Mar/2026 16:06:58] "POST /asistente HTTP/1.1" 200 30257
[02/Mar/2026 16:07:01] "GET /edit/277 HTTP/1.1" 200 34058
[02/Mar/2026 16:07:10] "POST /edit/277 HTTP/1.1" 302 0
[02/Mar/2026 16:07:11] "GET /edit/277 HTTP/1.1" 200 34356
[02/Mar/2026 16:07:14] "POST /edit/277 HTTP/1.1" 302 0
[02/Mar/2026 16:07:14] "GET /site/277 HTTP/1.1" 200 21266
[generator] LLM falló en 'pages_structure': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] Páginas inválidas, usando fallback
[generator] LLM falló en 'models': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] LLM falló en 'views': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] LLM falló en 'base.html': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] LLM falló en 'template_home': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] LLM falló en 'template_catalog': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] LLM falló en 'template_detail': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[generator] LLM falló en 'load_data': LLM HTTP 429: {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'meta-llama/llama-3.3-70b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Venice', 'is_byok': False}}, 'user_id': 'user_39wX2ijscSkvIqWB2viEl5veMmo'}
[02/Mar/2026 16:07:26] "POST /site/277/generate/ HTTP/1.1" 302 0
[02/Mar/2026 16:07:26] "GET /site/277 HTTP/1.1" 200 26509
[02/Mar/2026 16:07:35] "GET /site/277/download/ HTTP/1.1" 200 7069