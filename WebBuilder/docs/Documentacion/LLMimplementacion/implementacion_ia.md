# Implementacion sistema IA en el proyecto django (19/02)

- FINALIDAD: Conectar la ia con el proyecto para poder ver sus respuestas de prueba. Los pasos a seguir son los explicados en este fichero.

## Índice

- [OpenRouter](#1-openrouter)
- [.env](#2-env)
- [Comprobar que django ve la configuracion del paso 2](#3-comprobar-que-django-ve-la-configuracion-del-paso-2)
- [Crear el asistente en el proyecto de Django](#4-crear-el-asistente-en-el-proyecto-de-django)
- [Probar cliente llm desde la shell de django](#5-probar-cliente-llm-desde-la-shell-de-django)
- [Añadimos campos necesarios para que se vea el llm en el proyecto](#6-añadimos-campos-necesarios-para-que-se-vea-el-llm-en-el-proyecto)

## 1. OpenRouter

1) Inicio en la pagina web de OpenRouter (https://openrouter.ai/) para la creacion de la key para poder probar la conexion con algunas ias de prueba (creado en API Keys con el nombre de WebBuilder key)

2) Prueba de conexion a un modelo concreto con la key. El modelo probado es liquid...

```bash
export OPENROUTER_API_KEY="TU_KEY"
export MODEL="liquid/lfm-2.5-1.2b-instruct:free"

curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "HTTP-Referer: http://localhost:8000" \
  -H "X-Title: WebBuilder" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [
      {\"role\":\"user\",\"content\":\"Responde solo con: OK\"}
    ]
  }"
```

- Si se devuelve algo como content OK o los datos de tu key como id etc se conecto correctamente, tbm tienes la posibilidad de al ser IA publica este colpasada de usos y te lo dice como error con un: 429 “rate-limited upstream”.

## 2. .env y .env.example

1) Debemos crear un entorno con las siguientes variables para facilicitar la conexion, pero primero debemos instalar en nuestro entorno de python/django dotenv, para q pueda leer variables de .env
2) IMPORTANTE: El .env debe estar al nivel de manage.py 

```bash
python -m pip install python-dotenv
python -m pip show python-dotenv (Comprobar instalacion)
```

```bash
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=KEY_HERE
LLM_MODEL=liquid/lfm-2.5-1.2b-instruct:free
```

3) Qué significa cada campo
- LLM_BASE_URL: “dónde está la API”
- LLM_API_KEY: “tu token”
- LLM_MODEL: “qué modelo usar” (cambiable sin tocar código)

4) Debemos hacer que la app django cargue el .env, para eso debemos añadir lo siguiente en manage.py

```bash
from dotenv import load_dotenv
load_dotenv()
```

5) Debemos hacer que settings tambien sea capaz de leer las variables, para eso añadimos:

```bash
import os

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "liquid/lfm-2.5-1.2b-instruct:free")
```
- El campo LLM_API_KEY asi tal cual, no hay que añadir la key entre los "" 

6) Creo el .env.example que es lo mismo q el .env pero sin mi key, para poder subir la estrcutura del .env a github y no subir mi key

## 3. Comprobar que django ve la configuracion del paso 2

- En la carpeta del manage.py y con nuestro entorno django activado, en una terminal ejecutamos:

```bash
python manage.py shell

from django.conf import settings
settings.LLM_BASE_URL, settings.LLM_MODEL, settings.LLM_API_KEY[:6]
```

- Si se muestran los 6 primeros caracteres de nuestra key, es que todo esta correcto (podemos variar los 6 caracteres en el campo de la linea setings.LLM_BASE...)


## 4. Crear el asistente en el proyecto de Django

- En mi caso tengo la carpeta utils, con las siguientes carpetas:
1. analysis - builder/constants/detection/helpers/suggestions_heuristic
2. ingest - parsers/url_reader
- Creamos una tercera carpeta encargada del manejo del llm
3. llm - client

- Este archivo client.py tiene un funcion llamada chat_completion() que hace POST a:
{LLM_BASE_URL}/chat/completions y devuelve choices[0].message.content.

## 5. Probar cliente llm desde la shell de django

- En una nueva shell probamos si funciona la conexion con el llm, si devuelve Hola perfecto.

```bash
from WebBuilder.utils.llm.client import chat_completion
chat_completion("Responde solo con: hola", system_text="Responde en español.")
```

## 6. Añadimos campos necesarios para que se vea el llm en el proyecto

1) Añadimos el user_prompt en forms.py, dentro del ApiRquest, para que forme parte del analisis de la url

```bash
user_prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 4,
            "class": "form-control",  # opcional, para que se vea igual que api_url
            "placeholder": "Describe qué web quieres y cómo la quieres..."
        })
    )
```

2) Añadimos lo necesario en el html para que se vea

- html para escrbir el prompt
```bash
<div class="wb-form-group">
  <label class="wb-label" for="{{ form.user_prompt.id_for_label }}">
    Prompt del usuario (opcional)
  </label>
  <div class="wb-input-wrapper">
    {{ form.user_prompt }}
    {% if form.user_prompt.errors %}
      <div class="wb-error">{{ form.user_prompt.errors }}</div>
    {% endif %}
  </div>
  <p class="wb-hint">
    Ejemplo: "Quiero un portfolio minimalista con 3 secciones (inicio, proyectos, contacto) y que muestre imágenes y fechas."
  </p>
</div>
```

- html para ver el resultado del analisis: 
```bash
{% if llm_reply %}
  <h3>Respuesta del LLM</h3>
  <pre style="white-space: pre-wrap;">{{ llm_reply }}</pre>
{% endif %}

{% if llm_error %}
  <div class="alert alert-danger">Error LLM: {{ llm_error }}</div>
{% endif %}
```

3) Modificar render_assistant para que acepte los campos:
- llm_reply
- llm_error

4) Modificar analyz_url para llamar al llm: 
- recoges user_prompt = form.cleaned_data.get("user_prompt")
- si hay prompt → chat_completion(...)
- guardas/mandas llm_reply al render