# Variación de LLM — Documentación para la Memoria

## Descripción de la funcionalidad

Se ha implementado un sistema de selección dinámica de modelos LLM en WebBuilder, permitiendo al usuario elegir con qué modelo de lenguaje se genera su sitio web. Anteriormente el modelo estaba fijado en el fichero `.env` y no era modificable sin acceso al servidor.

---

## Motivación

El sistema estaba acoplado a un único modelo LLM definido en variables de entorno. Esto impedía comparar resultados entre modelos, limitar el coste según el caso de uso, o permitir que usuarios avanzados usasen su propio proveedor. Dado que WebBuilder ya utilizaba la API de OpenAI-compatible para todas las llamadas al LLM, el sistema era agnóstico al modelo en teoría, pero no en la práctica.

---

## Cambios en la configuración del entorno

### `.env`

El fichero `.env` mantiene la configuración por defecto del servidor, que actúa como fallback cuando el usuario no selecciona un modelo personalizado:

```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=...
LLM_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
```

Se ha añadido además una nueva variable para el cifrado de API keys de usuarios:

```
FIELD_ENCRYPTION_KEY=...
```

Esta clave se genera una única vez con Fernet (librería de criptografía simétrica de Python) y se usa para cifrar las API keys que los usuarios guardan en su perfil. Si se pierde o cambia, las claves guardadas quedan ilegibles.

### `settings.py`

Se han añadido dos nuevas variables leídas desde el entorno:

```python
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY  = os.getenv("LLM_API_KEY", "")
LLM_MODEL    = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", "")
```

La variable `FIELD_ENCRYPTION_KEY` es leída por la librería `django-encrypted-model-fields`, que la usa automáticamente para cifrar y descifrar los campos marcados como `EncryptedCharField` en los modelos de Django.

---

## Dependencias añadidas

### `django-encrypted-model-fields`

Librería que permite cifrar campos de modelos Django de forma transparente. Se instala en el entorno virtual:

```bash
pip install django-encrypted-model-fields
```

Y se registra en `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'encrypted_model_fields',
]
```

El cifrado es simétrico (AES-128 con Fernet). El campo se almacena cifrado en la base de datos y se descifra automáticamente al acceder desde el ORM de Django, sin necesidad de código adicional.

---

## Nuevo modelo en base de datos: `UserProfile`

Se ha creado un modelo `UserProfile` con relación `OneToOne` al modelo `User` de Django. Almacena la configuración de LLM personalizado del usuario:

- `custom_llm_base_url` — URL base del proveedor OpenAI-compatible
- `custom_llm_model` — nombre del modelo a usar
- `custom_llm_api_key` — API key cifrada con `EncryptedCharField`

Este modelo sienta además las bases para un futuro dashboard de usuario, donde se podrán añadir más campos de preferencias o estadísticas personales.

La migración correspondiente es `0014_userprofile.py`, generada automáticamente por Django.

---

## Arquitectura de la selección de modelos

### Catálogo de modelos (`llm_catalog.py`)

Se ha creado un fichero centralizado con los modelos disponibles. Cada entrada define el identificador del modelo, el proveedor, la URL base de su API, y una descripción con pros y contras para mostrar al usuario. Añadir un nuevo modelo al catálogo es suficiente para que aparezca automáticamente en el formulario sin tocar ningún otro fichero.

### Resolución del modelo (`_resolve_llm`)

En cada petición al asistente, se ejecuta una función que determina qué modelo, URL y API key usar según la elección del usuario:

- Si elige un modelo del catálogo, se usa la API key del servidor (`.env`).
- Si elige "modelo personalizado", se recuperan los datos cifrados de su `UserProfile`.

Esto mantiene la lógica de selección centralizada y separada del resto del flujo.

### Propagación por el flujo de generación

Los parámetros `model`, `base_url` y `api_key` se propagan desde la vista del asistente hasta el cliente HTTP (`client.py`), pasando por el planificador (`planner.py`). Todos estos componentes los aceptan como parámetros opcionales, usando los valores de `settings` como fallback si no se proporcionan, lo que garantiza compatibilidad con el resto del sistema.

---

## Seguridad

Las API keys de usuarios se almacenan cifradas en base de datos usando cifrado simétrico AES-128. La clave de cifrado reside únicamente en el servidor (variable de entorno), por lo que un volcado de la base de datos sin acceso al servidor no expone las claves de los usuarios.