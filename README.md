# WebBuilder

**WebBuilder** es una aplicación web en **Django** que permite pegar la **URL de una API (JSON o XML)**, analizar automáticamente su estructura y generar un **proyecto web completo y funcional** adaptado a los datos de esa API.

> Proyecto en desarrollo

---

## Tabla de contenidos
- [Qué hace](#qué-hace)
- [Características actuales](#características-actuales)
- [Stack y dependencias](#stack-y-dependencias)
- [Configuración](#configuración)

---

## Qué hace

1. **Introduces una URL** de una API que devuelve JSON o XML.
2. WebBuilder **descarga** la respuesta y detecta el formato automáticamente.
3. **Parsea** el contenido:
   - JSON → `json.loads`
   - XML → validación segura (`defusedxml`) + conversión a dict (`xmltodict`)
4. Un **LLM** analiza la estructura del dataset y genera un plan con:
   - Tipo de sitio recomendado (blog, catálogo, portfolio, dashboard...)
   - Campos relevantes del dataset y sus etiquetas
   - Vista previa de los datos normalizados
5. El usuario **revisa y acepta el plan**, o lo regenera con un prompt personalizado.
6. WebBuilder **genera un proyecto Django completo** listo para ejecutar:
   - `models.py`, `views.py`, `urls.py` adaptados al dataset
   - Templates HTML con Tailwind CSS
   - Management command `load_data` que descarga y carga los datos desde la API
   - `Dockerfile` y `entrypoint.sh` para despliegue
7. El proyecto se descarga como **ZIP**.
8. Todo el historial de análisis queda guardado por usuario.

---

## Características actuales

- **Login / Register** con notificaciones por correo via n8n (bienvenida al registrarse, confirmación al iniciar sesión)
- **Asistente de generación**:
  - Paso 1: introducir URL de la API
  - Paso 2: el LLM analiza el dataset y propone un schema (tipo de sitio + campos)
  - Paso 3: el usuario revisa la preview y acepta o regenera el plan con un prompt
  - Paso 4: generación del proyecto Django completo
- **Generador de proyectos**: produce todos los archivos necesarios para arrancar el sitio generado de forma independiente
- **Descarga en ZIP** del proyecto generado
- Soporte **JSON y XML**
- Guardado en base de datos de cada análisis:
  - URL, fecha, estado, raw data, parsed data, resumen, errores
- **Historial** de análisis del usuario ordenado por fecha

---

## Stack y dependencias

- **Python 3**
- **Django 5.1.7**
- **SQLite**
- **n8n** (automatización: correos de bienvenida y login)
- **LLM via OpenRouter o Groq** (compatible con cualquier proveedor con API formato OpenAI)
- Librerías Python:
  - `requests`
  - `xmltodict`
  - `defusedxml`

---

## Configuración

Crea un archivo `.env` en la raiz del proyecto a partir de `.env.example`:

```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=tu_api_key
LLM_MODEL=llama-3.3-70b-versatile
```

El cliente LLM es compatible con cualquier proveedor que implemente el formato OpenAI (`/chat/completions`), como OpenRouter, Groq o cualquier otro. Solo hay que cambiar las tres variables del `.env`.