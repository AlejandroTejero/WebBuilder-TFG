# WebBuilder

**WebBuilder** es una plataforma web desarrollada como Trabajo de Fin de Grado que permite convertir cualquier API pública en un sitio web completo y desplegable, utilizando **IA generativa** para analizar los datos, proponer una arquitectura adecuada y generar automáticamente todo el código necesario.

> 🚧 Proyecto en desarrollo activo

---

## Tabla de contenidos

- [Motivación](#motivación)
- [Qué hace](#qué-hace)
- [El papel de la IA](#el-papel-de-la-ia)
- [Automatizaciones](#automatizaciones)
- [Características actuales](#características-actuales)
- [Stack y dependencias](#stack-y-dependencias)
- [Configuración](#configuración)

---

## Motivación

Crear un sitio web a partir de datos de una API es una tarea repetitiva que sigue siempre el mismo patrón: entender la estructura de los datos, decidir qué tipo de interfaz tiene sentido, escribir modelos, vistas, templates y configuración de despliegue. WebBuilder automatiza todo ese proceso.

La idea central es que **la IA actúe como un desarrollador guiado**: recibe los datos, entiende su estructura, propone un plan razonado y genera código real y funcional. El usuario supervisa, corrige y aprueba en cada paso.

---

## Qué hace

1. **Introduces una URL** de una API que devuelve JSON o XML.
2. WebBuilder **descarga y detecta el formato** automáticamente.
3. **Parsea el contenido** de forma segura:
   - JSON → `json.loads`
   - XML → validación segura con `defusedxml` + conversión a dict con `xmltodict`
4. Un **LLM analiza la estructura del dataset** y genera un plan que incluye:
   - Tipo de sitio recomendado (blog, catálogo, portfolio, dashboard...)
   - Campos relevantes del dataset y sus etiquetas
   - Vista previa de los datos normalizados
5. El usuario **revisa y acepta el plan**, o lo regenera con un prompt personalizado en lenguaje natural.
6. WebBuilder **genera un proyecto Django completo** listo para ejecutar:
   - `models.py`, `views.py`, `urls.py` adaptados al dataset
   - Templates HTML con Tailwind CSS
   - Management command `load_data` que descarga y carga los datos desde la API
   - `Dockerfile` y `entrypoint.sh` para despliegue
7. El proyecto se descarga como **ZIP**.
8. Todo el historial de análisis queda **guardado por usuario**.

---

## El papel de la IA

El LLM es el núcleo del sistema y participa en dos fases críticas del flujo:

### Fase de análisis

El modelo recibe el dataset parseado y un prompt diseñado para extraer el máximo valor de los datos. Se le instruye para:

- Identificar el tipo de contenido (eventos, productos, noticias, personas, lugares...)
- Determinar qué campos son relevantes y cuáles son ruido
- Proponer un tipo de interfaz adecuada al contenido
- Normalizar y etiquetar los campos con nombres legibles
- Devolver un plan estructurado que el usuario pueda revisar

### Fase de generación

Una vez aprobado el plan, el modelo genera el código fuente completo del proyecto. Los prompts de generación están diseñados con:

- **Instrucciones detalladas** sobre la estructura esperada de cada fichero
- **Restricciones explícitas** de estilo y buenas prácticas (Tailwind, Django patterns...)
- **Contexto del dataset** para que el código generado sea semánticamente correcto
- **Ejemplos de referencia** (few-shot) para guiar el estilo del output

La calidad del código generado depende en gran medida de la ingeniería de prompts: cuanto más preciso y rico en contexto es el prompt, más profesional y coherente es el proyecto resultante. Por eso, **una parte central del trabajo del TFG es el diseño, iteración y refinamiento de estos prompts**.

El sistema es compatible con cualquier LLM que implemente el formato OpenAI (`/chat/completions`), lo que permite comparar resultados entre modelos y elegir el más adecuado para cada tarea.

---

## Automatizaciones

WebBuilder integra **n8n** como motor de automatización para flujos que van más allá del ciclo petición-respuesta de Django:

- **Correo de bienvenida** al registrarse: n8n escucha el evento de registro y envía un email personalizado al nuevo usuario.
- **Confirmación de sesión** al iniciar sesión: notificación automática cada vez que el usuario accede a la plataforma.

Esta arquitectura desacopla la lógica de notificaciones de la aplicación principal, permitiendo añadir nuevos flujos (alertas, resúmenes, integraciones externas) sin modificar el core de Django.

---

## Características actuales

- **Autenticación completa**: Login y Register con notificaciones automáticas por correo vía n8n
- **Asistente de generación paso a paso**:
  - Paso 1: introducir URL de la API
  - Paso 2: el LLM analiza el dataset y propone un schema (tipo de sitio + campos)
  - Paso 3: el usuario revisa la preview, acepta o regenera el plan con un prompt personalizado
  - Paso 4: generación del proyecto Django completo
- **Generador de proyectos**: produce todos los archivos necesarios para arrancar el sitio generado de forma totalmente independiente
- **Descarga en ZIP** del proyecto generado
- **Soporte JSON y XML** con parsing seguro
- **Persistencia de análisis** por usuario:
  - URL, fecha, estado, raw data, parsed data, resumen LLM, errores
- **Historial de análisis** ordenado por fecha

---

## Stack y dependencias

| Categoría | Tecnología |
|-----------|------------|
| Backend | Python 3, Django 5.1.7 |
| Base de datos | SQLite |
| IA / LLM | OpenRouter, Groq (cualquier proveedor formato OpenAI) |
| Automatización | n8n |
| Frontend | HTML, Tailwind CSS (en proyectos generados) |
| Parsing | `requests`, `xmltodict`, `defusedxml` |

---

## Configuración

Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example`:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=tu_api_key
LLM_MODEL=llama-3.3-70b-versatile
```

El cliente LLM es compatible con cualquier proveedor que implemente el formato OpenAI (`/chat/completions`), como OpenRouter, Groq o cualquier otro. Solo hay que cambiar las tres variables del `.env`.