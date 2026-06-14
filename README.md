<div align="center">

# 🧩 WebBuilder

**Convierte cualquier API pública en un sitio web Django completo, listo para desplegar — usando IA generativa.**

Trabajo de Fin de Grado · Ingeniería Telemática · Escuela de Ingeniería de Fuenlabrada · Universidad Rey Juan Carlos

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![n8n](https://img.shields.io/badge/n8n-Automation-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](LICENSE)

[Demo en vivo](http://178.104.248.235.nip.io) · [Landing page](https://alejandrotejero.github.io/WebBuilder-landing/) · [Memoria del TFG](https://alejandrotejero.github.io/WebBuilder-landing/static/docs/memoria.pdf)

</div>

---

## Índice

- [¿Qué es WebBuilder?](#-qué-es-webbuilder)
- [Flujo de uso](#-flujo-de-uso)
- [Características](#-características)
- [El papel de la IA](#-el-papel-de-la-ia)
- [Arquitectura](#-arquitectura)
- [Automatizaciones (n8n)](#-automatizaciones-n8n)
- [Ejemplos generados](#-ejemplos-generados)
- [Stack tecnológico](#-stack-tecnológico)
- [Puesta en marcha](#-puesta-en-marcha)
- [Configuración (.env)](#-configuración-env)
- [Despliegue en producción](#-despliegue-en-producción)
- [Licencia](#-licencia)

---

## ¿Qué es WebBuilder?

Crear un sitio web a partir de los datos de una API es un proceso repetitivo que sigue siempre el mismo patrón:

```
API → Datos → Modelos → Vistas → Templates → Deploy
```

**WebBuilder automatiza todo ese pipeline.** Le das la URL de una API pública (JSON, XML o CSV), una IA generativa analiza el dataset, propone un esquema de datos y un tipo de sitio adecuado (catálogo, blog, dashboard, portfolio...), y genera un **proyecto Django completo y funcional**: modelos, vistas, URLs, templates con Tailwind CSS, comando de carga de datos, `Dockerfile`... todo listo para revisar, editar y desplegar con un clic.

```
URL → IA → Código → Deploy
```

---

## Flujo de uso

| Paso | Descripción |
|------|-------------|
| **1. URL** | El usuario introduce la URL de una API pública |
| **2. Parseo** | WebBuilder descarga y parsea el contenido (JSON / XML / CSV) de forma segura |
| **3. Plan IA** | Un LLM analiza el dataset y propone un esquema (tipo de sitio + campos relevantes), que el usuario puede revisar, editar o regenerar con un prompt personalizado |
| **4. Código** | Se genera el proyecto Django completo: modelos, vistas, templates, comando `load_data`, Dockerfile... |
| **5. Deploy** | El proyecto se construye y se levanta en un contenedor Docker, accesible mediante una URL pública |

---

## Características

- **Autenticación completa**: registro, login y login social (Google / GitHub vía `django-allauth`), con notificaciones por correo automatizadas
- **Asistente de generación guiado** en 4 pasos, con revisión y edición del plan propuesto por la IA
- **Generador de proyectos Django**: modelos, vistas, URLs, templates con Tailwind CSS y comando `load_data` para poblar la base de datos desde la API original
- **Editor de código integrado**: visualiza y edita cualquier fichero del proyecto generado, con **refinamiento asistido por IA** archivo a archivo
- **Versionado de sitios**: cada cambio se guarda como una nueva versión, con opción de restaurar o descargar versiones anteriores
- **Descarga en ZIP** del proyecto generado en cualquier momento
- **Despliegue automatizado** del sitio generado mediante n8n + Docker, con preview en vivo y URL pública
- **Multi-LLM**: compatible con cualquier proveedor que implemente el formato OpenAI `/chat/completions` (Groq, OpenRouter, OpenAI...), seleccionable por el usuario
- **Panel de métricas**: actividad, uso por modelo LLM, tasas de éxito/reintento, generaciones, alertas del sistema...
- **Historial de análisis y sitios** por usuario, con estado, fecha y resultados
- **Internacionalización**: interfaz disponible en español e inglés
- **Mantenimiento automático**: *health checks* diarios y apagado automático de contenedores inactivos

---

## El papel de la IA

El LLM es el núcleo del sistema y participa en dos fases críticas:

### 1. Análisis del dataset
El modelo recibe los datos parseados y:
- Identifica el tipo de contenido (productos, personajes, eventos, criptoactivos...)
- Determina qué campos son relevantes y cuáles son ruido
- Propone un tipo de sitio adecuado (catálogo, dashboard, blog, portfolio...)
- Normaliza y etiqueta los campos con nombres legibles
- Devuelve un plan estructurado y editable

### 2. Generación del código
Una vez aprobado el plan, el modelo genera el proyecto Django completo siguiendo prompts diseñados con:
- Instrucciones detalladas sobre la estructura esperada de cada fichero
- Restricciones de estilo y buenas prácticas (Tailwind, patrones Django)
- Contexto del dataset para generar código semánticamente correcto
- Ejemplos de referencia (*few-shot*) por tipo de sitio
- Un **comprobador de consistencia** que valida y corrige el código generado antes de entregarlo

---

## Arquitectura

```
┌─────────────┐      ┌──────────────┐      ┌───────────────────┐
│   Django    │◄────►│     LLMs     │      │    n8n + Docker    │
│  (backend)  │      │ (IA generativa)│     │  (automatización)  │
│             │      │              │      │                    │
│ ORM         │      │ Motor        │      │ Workflows          │
│ Vistas      │      │ OpenAI       │      │ Deploy             │
│ Templates   │      │ OpenRouter   │      │ Notificaciones     │
│             │      │ Groq         │      │                    │
└──────┬──────┘      └──────────────┘      └─────────┬──────────┘
       │                                              │
       └──────────────── volumen compartido ─────────┘
                     (ZIPs del proyecto generado)
```

La aplicación principal (Django + PostgreSQL) corre detrás de Nginx, y se comunica con una instancia de **n8n** (con acceso al socket de Docker del host) a través de webhooks para desplegar los sitios generados, gestionar notificaciones y tareas de mantenimiento.

---

## Automatizaciones (n8n)

| Workflow | Disparador | Acción |
|----------|-----------|--------|
| **Register** | Alta de usuario | Envía email de bienvenida |
| **Login** | Inicio de sesión | Envía email de confirmación de acceso |
| **Deploy** | Sitio generado y aceptado | Construye y arranca el contenedor Docker del proyecto generado |
| **Generation done** | Generación de código finalizada | Notifica al usuario que su sitio está listo |
| **Health check** | Cron diario | Genera un informe del estado de los contenedores desplegados |
| **Auto-shutdown** | Cron periódico | Apaga automáticamente los contenedores inactivos |

Los workflows exportados se encuentran en [`/WorkFlows`](./WorkFlows).

---

## Ejemplos generados

WebBuilder ha sido probado generando sitios completos a partir de APIs públicas reales:

| Proyecto | API origen | Tipo de sitio |
|----------|-----------|---------------|
| **Personajes de Rick y Morty** | [rickandmortyapi.com](https://rickandmortyapi.com/api/character) | Catálogo |
| **Criptoactivos** | [api.coinlore.net](https://api.coinlore.net/api/tickers/) | Dashboard |
| **Cocktails Bar** | [thecocktaildb.com](https://www.thecocktaildb.com/api/json/v1/1/filter.php?c=Cocktail) | Catálogo |

> 🎥 Puedes ver el proceso completo en el [vídeo de demostración](https://alejandrotejero.github.io/WebBuilder-landing/) de la landing page.

---

## Stack tecnológico

| Categoría | Tecnología |
|-----------|------------|
| Backend | Python 3, Django 5.1 |
| Base de datos | PostgreSQL |
| Servidor | Gunicorn + Nginx |
| IA / LLM | Groq, OpenRouter (formato OpenAI `/chat/completions`) |
| Automatización | n8n + Docker |
| Autenticación | django-allauth (Google, GitHub) |
| Frontend | HTML, Tailwind CSS |
| Parsing de datos | `requests`, `xmltodict`, `defusedxml` |
| Seguridad | `django-encrypted-model-fields` (cifrado de claves API de usuario) |

---

## Puesta en marcha

### Requisitos
- Python 3.12+
- Docker y Docker Compose
- Una clave de API de un proveedor LLM compatible (Groq, OpenRouter...)

### Instalación local

```bash
git clone https://github.com/alejandrotejero/WebBuilder.git
cd WebBuilder/project

# Copia y rellena las variables de entorno
cp .env.example .env

# Levanta toda la plataforma (Django + PostgreSQL + n8n + Nginx)
docker compose up --build
```

La aplicación quedará disponible en `http://localhost`.

---

## Configuración (.env)

Las variables principales que necesitas configurar en tu `.env`:

```env
# Django
SECRET_KEY=...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=webbuilder_db
DB_USER=webbuilder_user
DB_PASSWORD=...

# Proveedor LLM (formato OpenAI /chat/completions)
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=...
LLM_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

# n8n
N8N_DEPLOY_WEBHOOK=http://n8n:5678/webhook/webbuilder-deploy
N8N_WEBHOOK_REGISTRO=http://n8n:5678/webhook/WebBuilder-Register
N8N_WEBHOOK_LOGIN=http://n8n:5678/webhook/WebBuilder-Login
N8N_WEBHOOK_GENERATION_DONE=http://n8n:5678/webhook/webbuilder-generation-done

# Cifrado de claves API de usuario
FIELD_ENCRYPTION_KEY=...

# OAuth (opcional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

Solo es necesario cambiar `LLM_BASE_URL`, `LLM_API_KEY` y `LLM_MODEL` para usar otro proveedor compatible con la API de OpenAI.

---

## Despliegue en producción

WebBuilder está pensado para desplegarse en un VPS mediante `docker-compose.yml`, que orquesta:

- **`db`** — PostgreSQL
- **`web`** — Django servido con Gunicorn
- **`n8n`** — automatizaciones y deploy de los sitios generados (con acceso al Docker del host)
- **`nginx`** — proxy inverso y servido de estáticos

Una demo activa está disponible en **http://178.104.248.235.nip.io**.

---

## Licencia

Este proyecto está publicado bajo licencia [CC0 1.0 Universal](LICENSE).

---

<div align="center">

Desarrollado por **Alejandro Tejero de la Morena** · Tutor: David Moreno Lumbreras
Trabajo de Fin de Grado 2025/2026 · Universidad Rey Juan Carlos

</div>