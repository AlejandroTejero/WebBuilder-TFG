# Memoria Técnica: Despliegue Automático en WebBuilder

> Documentación interna del sistema de despliegue automático de proyectos Django generados por WebBuilder usando n8n y Docker.

---

## Índice

1. [Arquitectura general del sistema](#1-arquitectura-general-del-sistema)
2. [Instalación y configuración desde cero](#2-instalación-y-configuración-desde-cero)
3. [Cómo arrancar el entorno en local](#3-cómo-arrancar-el-entorno-en-local)
4. [Cómo funciona el generador de proyectos Django](#4-cómo-funciona-el-generador-de-proyectos-django)
5. [Cómo funciona el workflow de n8n paso a paso](#5-cómo-funciona-el-workflow-de-n8n-paso-a-paso)
6. [Problemas encontrados y soluciones aplicadas](#6-problemas-encontrados-y-soluciones-aplicadas)

---

## 1. Arquitectura general del sistema

WebBuilder es una aplicación Django 5.1 que permite a un usuario introducir una URL de API pública, analizar su estructura con un LLM, generar un proyecto Django completo adaptado a esos datos y desplegarlo automáticamente en local.

### Componentes

```
┌─────────────────────────────────────────────────┐
│                  MÁQUINA LOCAL                  │
│                                                 │
│  ┌──────────────────┐     ┌──────────────────┐  │
│  │   WebBuilder     │     │   n8n            │  │
│  │   Django 5.1     │────▶│   Docker         │  │
│  │   puerto 8000    │     │   puerto 5678    │  │
│  └──────────────────┘     └────────┬─────────┘  │
│          │                         │            │
│          │ guarda ZIP              │ build/run  │
│          ▼                         ▼            │
│  ┌──────────────────┐     ┌──────────────────┐  │
│  │  Carpeta         │     │  Contenedores    │  │
│  │  local-files/    │     │  generados       │  │
│  │  deploys/        │     │  puerto 8100+    │  │
│  └──────────────────┘     └──────────────────┘  │
└─────────────────────────────────────────────────┘
```

| Componente | Tecnología | Puerto | Cómo corre |
|---|---|---|---|
| WebBuilder | Django 5.1 + Python 3.12 | 8000 | Directamente en la máquina |
| n8n | Docker (imagen `n8n-custom`) | 5678 | Contenedor Docker |
| Proyectos generados | Django + Gunicorn | 8100–8999 | Contenedores Docker creados por n8n |

### Flujo completo de despliegue

1. El usuario genera un proyecto Django desde WebBuilder
2. El usuario pulsa **Desplegar**
3. Django guarda el ZIP del proyecto en `local-files/deploys/<nombre>/`
4. Django llama al webhook de n8n con `{ "project_name": "..." }`
5. n8n descomprime el ZIP, hace `docker build` y `docker run`
6. n8n devuelve la `preview_url` a Django
7. Django muestra al usuario el enlace al sitio desplegado

### Carpeta compartida

La carpeta `/home/alejandro/Desktop/TFG/docker/n8n/local-files` está montada en `/files` dentro del contenedor de n8n. Esto permite que Django (que corre en la máquina) escriba el ZIP y n8n (que corre en Docker) lo lea sin transferencia de red.

```
local-files/
└── deploys/
    └── <project_name>/
        ├── <project_name>.zip      ← Django escribe aquí
        └── src/                    ← n8n descomprime aquí
            └── <project_name>/
                ├── Dockerfile
                ├── entrypoint.sh
                ├── requirements.txt
                ├── manage.py
                ├── <project_name>/
                └── siteapp/
```

---

## 2. Instalación y configuración desde cero

### 2.1 Requisitos previos

- Python 3.12
- Docker y Docker Compose
- Git

### 2.2 Clonar y configurar WebBuilder

```bash
git clone <repo>
cd WebBuilder/project

# Crear y activar el entorno virtual
python3 -m venv entorno
source entorno/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

Editar `.env` con los valores correctos:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=tu_api_key
LLM_MODEL=llama-3.3-70b-versatile
N8N_DEPLOY_WEBHOOK=http://localhost:5678/webhook/webbuilder-deploy
N8N_LOCAL_FILES_PATH=/home/alejandro/Desktop/TFG/docker/n8n/local-files
```

Aplicar migraciones:

```bash
python manage.py migrate
python manage.py createsuperuser  # opcional
```

### 2.3 Construir la imagen personalizada de n8n

La imagen personalizada añade `docker-cli` a la imagen oficial de n8n para que pueda ejecutar comandos Docker desde los nodos Code.

El `Dockerfile` se encuentra en `/home/alejandro/Desktop/TFG/docker/n8n/`:

```dockerfile
FROM n8nio/n8n:latest
USER root
RUN cd /tmp && \
    wget -O docker.tgz https://download.docker.com/linux/static/stable/x86_64/docker-27.0.3.tgz && \
    tar xzf docker.tgz && \
    mv docker/docker /usr/local/bin/docker && \
    chmod +x /usr/local/bin/docker && \
    rm -rf /tmp/docker.tgz /tmp/docker
```

Construir la imagen:

```bash
cd /home/alejandro/Desktop/TFG/docker/n8n
docker build -t n8n-custom .
```

### 2.4 Configurar docker-compose.yml

El `docker-compose.yml` está en `/home/alejandro/Desktop/TFG/docker/n8n/`:

```yaml
services:
  n8n:
    image: n8n-custom
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - TZ=Europe/Madrid
      - NODE_ENV=production
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - N8N_ENCRYPTION_KEY=4f0f7c41e64ecf553a3f8e4ca4f8278cd71bf1150480bcff9e6cb89d868427dd
      - N8N_SECURE_COOKIE=false
      - NODE_FUNCTION_ALLOW_BUILTIN=*
      - NODE_FUNCTION_ALLOW_EXTERNAL=*
      - N8N_RUNNERS_HEARTBEAT_INTERVAL=300
    volumes:
      - n8n_data:/home/node/.n8n
      - ./local-files:/files
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  n8n_data:
```

Variables de entorno clave:

| Variable | Valor | Para qué sirve |
|---|---|---|
| `NODE_FUNCTION_ALLOW_BUILTIN=*` | `*` | Permite usar `fs`, `child_process` etc. en nodos Code |
| `NODE_FUNCTION_ALLOW_EXTERNAL=*` | `*` | Permite módulos npm externos en nodos Code |
| `N8N_RUNNERS_HEARTBEAT_INTERVAL` | `300` | Evita que n8n mate nodos Code que tardan más de 30s (docker build) |
| `/var/run/docker.sock` | montado | Permite a n8n ejecutar comandos Docker en la máquina host |
| `./local-files:/files` | montado | Carpeta compartida entre Django y n8n |

### 2.5 Importar el workflow en n8n

1. Arrancar n8n (ver sección 3)
2. Abrir `http://localhost:5678`
3. Ir a **Workflows → Import from file**
4. Importar el archivo `webbuilder_deploy_v2.json`
5. Activar el workflow con el toggle **Published**

### 2.6 Permisos de la carpeta compartida

```bash
sudo chmod -R 777 /home/alejandro/Desktop/TFG/docker/n8n/local-files
```

Esto es necesario porque n8n corre como root dentro del contenedor y crea archivos que Django (corriendo como tu usuario) necesita poder leer/escribir.

---

## 3. Cómo arrancar el entorno en local

Cada vez que quieras trabajar con WebBuilder necesitas levantar dos cosas: n8n y Django.

### Paso 1: Arrancar n8n

```bash
cd /home/alejandro/Desktop/TFG/docker/n8n
docker compose up -d
```

Verificar que está corriendo:

```bash
docker ps
# Debe aparecer el contenedor "n8n" en estado "Up"
```

### Paso 2: Arrancar WebBuilder

```bash
cd /home/alejandro/Desktop/TFG/WebBuilder/project
source entorno/bin/activate
python manage.py runserver
```

WebBuilder queda disponible en `http://localhost:8000`.

### Paso 3: Verificar que n8n está activo

Abrir `http://localhost:5678`, ir al workflow **webbuilder - deploy** y confirmar que el toggle dice **Published** (no solo guardado).

### Para parar el entorno

```bash
# Parar n8n
cd /home/alejandro/Desktop/TFG/docker/n8n
docker compose down

# Django se para con Ctrl+C en su terminal
```

### Limpiar un despliegue anterior (si hay conflictos)

Si quieres redesplegar un proyecto que ya existe:

```bash
# Borrar el contenedor y la imagen del proyecto generado
docker rm -f wb_<project_name>
docker rmi wb_<project_name>:latest

# Borrar los archivos en disco
sudo rm -rf /home/alejandro/Desktop/TFG/docker/n8n/local-files/deploys/<project_name>
```

---

## 4. Cómo funciona el generador de proyectos Django

El generador vive en `WebBuilder/utils/generator/project_generator.py` y es el núcleo de la plataforma. Toma un objeto `GeneratedSite` con el plan aprobado por el usuario y produce un diccionario `{ ruta: contenido }` con todos los archivos del proyecto.

### Flujo de generación (7 pasos)

```
Plan aprobado
     │
     ▼
[Paso 1] LLM → estructura de páginas (home, catalog, detail...)
     │
     ▼
[Paso 2] LLM → models.py  ──▶  _generate_initial_migration()
     │
     ▼
[Paso 3] LLM → views.py
     │
     ▼
[Paso 4] LLM → base.html
     │
     ▼
[Paso 5] LLM → template por cada página
     │
     ▼
[Paso 6] LLM → load_data.py (management command)
     │
     ▼
[Paso 7] Python → archivos fijos (settings, urls, Dockerfile, entrypoint...)
     │
     ▼
dict { ruta: contenido } → guardado en GeneratedSite.project_files
```

### Archivos generados por proyecto

| Archivo | Generado por |
|---|---|
| `manage.py` | Python (fijo) |
| `<project>/settings.py` | Python (fijo) |
| `<project>/urls.py` | Python (fijo) |
| `<project>/wsgi.py` | Python (fijo) |
| `requirements.txt` | Python (fijo) |
| `Dockerfile` | Python (fijo) |
| `entrypoint.sh` | Python (fijo) |
| `siteapp/models.py` | LLM |
| `siteapp/migrations/0001_initial.py` | Python (parseando models.py) |
| `siteapp/views.py` | LLM |
| `siteapp/urls.py` | Python (a partir de páginas del LLM) |
| `siteapp/templates/base.html` | LLM |
| `siteapp/templates/siteapp/*.html` | LLM (uno por página) |
| `siteapp/management/commands/load_data.py` | LLM |

### Generación de migraciones

Un punto crítico: el LLM genera `models.py` pero no genera las migraciones. Sin el archivo `0001_initial.py`, cuando el contenedor ejecuta `python manage.py migrate` no hay nada que migrar y las tablas nunca se crean, lo que causa `OperationalError: no such table`.

La función `_generate_initial_migration()` resuelve esto parseando el `models.py` generado con expresiones regulares, extrayendo los campos del modelo `Item` y construyendo un `0001_initial.py` válido para Django automáticamente.

### entrypoint.sh

Cada proyecto generado incluye este script que se ejecuta al arrancar el contenedor:

```sh
#!/bin/sh
set -e

echo '--- Aplicando migraciones ---'
python manage.py migrate --noinput

echo '--- Cargando datos ---'
python manage.py load_data

echo '--- Arrancando servidor ---'
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 <project>.wsgi:application
```

El orden es importante: primero `migrate` crea las tablas, luego `load_data` las rellena con datos de la API original, y finalmente arranca Gunicorn.

---

## 5. Cómo funciona el workflow de n8n paso a paso

El workflow **webbuilder - deploy** recibe una petición POST de Django y orquesta todo el proceso de build y arranque del contenedor.

### Nodos del workflow

```
Webhook → Descomprimir Zip → Restablecer Contenedor → Elegir Puerto
       → Docker Build → Docker Run → Verificar Docker → Respond to Webhook
```

### Nodo 1: Webhook

- **Tipo:** Webhook
- **Método:** POST
- **Path:** `webbuilder-deploy`
- **URL completa:** `http://localhost:5678/webhook/webbuilder-deploy`

Recibe el JSON de Django:
```json
{ "project_name": "docker_test", "site_id": "1" }
```

### Nodo 2: Descomprimir Zip

Construye las rutas a partir del `project_name` y descomprime el ZIP que Django ya dejó en disco:

```javascript
const body = $input.first().json.body;
const projectName = body.project_name;
const deployDir = `/files/deploys/${projectName}`;
const zipPath = `${deployDir}/${projectName}.zip`;

execSync(`mkdir -p ${deployDir}/src`);
execSync(`unzip -o ${zipPath} -d ${deployDir}/src`);
```

El ZIP lo escribió Django directamente en esa ruta antes de llamar al webhook, por lo que n8n no necesita manipular binarios.

### Nodo 3: Restablecer Contenedor

Si ya existía un contenedor con ese nombre de un despliegue anterior, lo para y lo elimina para poder redesplegar limpiamente:

```javascript
try {
  execSync(`docker stop ${containerName}`);
  execSync(`docker rm ${containerName}`);
} catch(e) {
  // Si no existe, no pasa nada
}
```

### Nodo 4: Elegir Puerto

Busca un puerto libre entre 8100 y 8999 comprobando los puertos ya usados por contenedores en ejecución:

```javascript
for (let p = 8100; p <= 8999; p++) {
  const result = execSync(`docker ps --format "{{.Ports}}"`).toString();
  if (!result.includes(`:${p}->`)) {
    port = p;
    break;
  }
}
```

### Nodo 5: Docker Build

Localiza el subdirectorio dentro de `src/` donde está el `Dockerfile` y construye la imagen:

```javascript
const srcDir = deployDir + '/src';
const subdir = execSync(`ls ${srcDir}`).toString().trim().split('\n')[0];
const buildDir = srcDir + '/' + subdir;

execSync(`docker build -t ${containerName}:latest ${buildDir}`, { timeout: 120000 });
```

El timeout es de 120 segundos. La variable `N8N_RUNNERS_HEARTBEAT_INTERVAL=300` en el docker-compose evita que n8n considere el nodo como "unresponsive" durante builds largos.

### Nodo 6: Docker Run

Arranca el contenedor con el puerto asignado:

```javascript
execSync(`docker run -d --name ${containerName} -p ${port}:8000 ${containerName}:latest`);
```

El puerto 8000 interno del contenedor (Gunicorn) se mapea al puerto libre elegido en el paso anterior.

### Nodo 7: Verificar Docker

Espera 4 segundos a que el contenedor arranque y verifica que está corriendo:

```javascript
await new Promise(resolve => setTimeout(resolve, 4000));
const status = execSync(`docker ps --filter name=${containerName} --format "{{.Status}}"`).toString().trim();
if (!status) throw new Error(`El contenedor ${containerName} no está corriendo`);
```

### Nodo 8: Respond to Webhook

Devuelve la respuesta JSON a Django con la URL de preview:

```json
{
  "preview_url": "http://localhost:8101",
  "container": "wb_docker_test",
  "port": 8101
}
```

Django recibe esta respuesta, guarda la `preview_url` en el modelo `GeneratedSite` y la muestra al usuario.

---

## 6. Qué ocurre cuando el usuario pulsa "Desplegar"

Esta sección explica paso a paso qué sucede internamente desde que el usuario hace clic en el botón hasta que el sitio está disponible en `localhost:810X`.

### Paso a paso completo

```
Usuario pulsa "Desplegar"
         │
         ▼
[Django - site_deploy()]
  1. Construye el ZIP del proyecto en memoria (BytesIO)
  2. Crea la carpeta:
     local-files/deploys/<project_name>/
  3. Escribe el ZIP en:
     local-files/deploys/<project_name>/<project_name>.zip
  4. Hace POST a http://localhost:5678/webhook/webbuilder-deploy
     con JSON: { "project_name": "docker_test" }
  5. Espera la respuesta (timeout 120s)
         │
         ▼
[n8n - workflow webbuilder-deploy]
  6. Webhook recibe el JSON
  7. Descomprimir Zip:
     unzip local-files/deploys/docker_test/docker_test.zip
          → local-files/deploys/docker_test/src/
  8. Restablecer Contenedor:
     docker stop wb_docker_test  (si existía)
     docker rm wb_docker_test    (si existía)
  9. Elegir Puerto:
     busca el primer puerto libre entre 8100 y 8999
     → asigna por ejemplo el 8101
 10. Docker Build:
     docker build -t wb_docker_test:latest
          local-files/deploys/docker_test/src/docker_test/
     Durante el build, el Dockerfile hace:
       - pip install -r requirements.txt
       - copia el código
       - prepara entrypoint.sh
 11. Docker Run:
     docker run -d --name wb_docker_test -p 8101:8000 wb_docker_test:latest
     Al arrancar el contenedor, entrypoint.sh ejecuta:
       a. python manage.py migrate      → crea las tablas en SQLite
       b. python manage.py load_data    → descarga datos de la API original
       c. gunicorn --bind 0.0.0.0:8000  → arranca el servidor web
 12. Verificar Docker:
     espera 4 segundos y comprueba que el contenedor está corriendo
 13. Respond to Webhook:
     devuelve { "preview_url": "http://localhost:8101", ... }
         │
         ▼
[Django - site_deploy() continúa]
 14. Recibe la preview_url de n8n
 15. Guarda preview_url en GeneratedSite.preview_url
 16. Muestra al usuario el enlace al sitio desplegado
         │
         ▼
Usuario accede a http://localhost:8101
  → El contenedor Docker sirve el sitio generado con sus datos
```

### Lo que contiene el contenedor desplegado

Cada proyecto desplegado es un contenedor Docker completamente independiente con:

- Su propio Django + Gunicorn corriendo en el puerto 8000 interno
- Su propia base de datos SQLite con los datos cargados desde la API original
- Sus propios templates, modelos y vistas generados por el LLM
- Mapeado a un puerto único en la máquina host (8100, 8101, 8102...)

### Ver los contenedores desplegados

```bash
docker ps
# Muestra todos los contenedores corriendo, incluyendo los wb_*
```

```bash
docker logs wb_<project_name>
# Muestra los logs del entrypoint: migraciones, carga de datos, arranque de gunicorn
```

### Redesplegar un proyecto existente

Si el proyecto ya fue desplegado antes y quieres actualizarlo:

1. Desde WebBuilder, regenera el proyecto (para que el LLM genere código nuevo)
2. Pulsa Desplegar — n8n detectará el contenedor existente, lo parará, lo eliminará y creará uno nuevo con el código actualizado

O manualmente desde terminal:

```bash
docker rm -f wb_<project_name>
docker rmi wb_<project_name>:latest
sudo rm -rf /home/alejandro/Desktop/TFG/docker/n8n/local-files/deploys/<project_name>
```

---

## 7. Problemas encontrados y soluciones aplicadas

### Problema 1: El nodo Read/Write Files from Disk no escribe el ZIP

**Síntoma:** Error `"The file is not writable"` aunque el directorio tenía permisos 777.

**Causa:** El nodo nativo de n8n verifica si el archivo existe antes de crearlo usando `fs.access()`. Si el archivo no existe aún, la comprobación falla y el nodo aborta.

**Solución intentada:** Reemplazarlo por un nodo Code usando `fs.writeFileSync()`.

**Resultado:** Parcialmente resuelto, pero llevó al problema 2.

---

### Problema 2: El binario llega como referencia `filesystem-v2`, no como base64

**Síntoma:** `binaryData.data` contiene el string `"filesystem-v2"` en vez del contenido base64 del ZIP.

**Causa:** n8n almacena los binarios grandes en su sistema de archivos interno en vez de inline. El valor `"filesystem-v2"` es un identificador de referencia, no el dato real. `Buffer.from("filesystem-v2", "base64")` produce un buffer corrupto, de ahí el error `unzip: short read`.

**Solución intentada:** Usar `this.helpers.getBinaryDataBuffer()` en el nodo Code, que sabe resolver tanto referencias `filesystem-v2` como base64 inline.

**Resultado:** Parcialmente resuelto, pero el nodo seguía dando "unknown error" de forma inconsistente debido al modo de ejecución del nodo.

---

### Problema 3: Modo de ejecución del nodo Code

**Síntoma:** Con modo `"Run Once for All Items"` el nodo devolvía vacío. Con modo `"Run Once for Each Item"` daba `"Can't use .first() here"`.

**Causa:** Cada modo requiere una API diferente: `.first()` solo funciona en modo "All Items", mientras que en modo "Each Item" hay que usar `$input.item`.

**Resultado:** Se resolvió cambiando al modo correcto y adaptando el código, pero la inconsistencia del `getBinaryDataBuffer` persistía.

---

### Problema 4: Arquitectura incorrecta — n8n no debería manipular binarios

**Causa raíz de los problemas 1-3:** El diseño original mandaba el ZIP como `multipart/form-data` al webhook de n8n, obligando a n8n a escribirlo en disco. n8n no está diseñado para ser un servidor de archivos y su manejo de binarios en nodos Code es frágil e inconsistente entre versiones.

**Solución definitiva:** Invertir la responsabilidad. Django guarda el ZIP directamente en la carpeta compartida (`local-files/deploys/`) antes de llamar al webhook. n8n recibe solo un JSON con el `project_name` y lee el ZIP de disco directamente. Esto elimina completamente la necesidad de manipular binarios en n8n.

**Cambios aplicados:**
- `views/site.py`: la función `site_deploy` guarda el ZIP en disco y llama al webhook con `json=` en vez de `files=`
- `settings.py`: nueva variable `N8N_LOCAL_FILES_PATH`
- `.env`: nueva variable `N8N_LOCAL_FILES_PATH`
- Workflow n8n: eliminados los nodos Preparar Variables, Crear Directorio y Guardar Zip

---

### Problema 5: docker build timeout — nodo Code "unresponsive"

**Síntoma:** Error `"Task execution aborted because runner became unresponsive"` en el nodo Docker Build.

**Causa:** n8n tiene un heartbeat de 30 segundos por defecto. Si un nodo Code no responde en ese tiempo (como ocurre durante un `docker build`), n8n lo considera colgado y lo mata.

**Solución:** Añadir `N8N_RUNNERS_HEARTBEAT_INTERVAL=300` en el `docker-compose.yml` para subir el intervalo a 5 minutos.

---

### Problema 6: `no such table` — migraciones no generadas

**Síntoma:** El sitio desplegado lanzaba `OperationalError: no such table: siteapp_item` al acceder a él.

**Causa:** El generador de proyectos creaba `models.py` con los modelos Django pero no creaba la carpeta `migrations/` con el archivo `0001_initial.py`. Sin ese archivo, `python manage.py migrate` no crea ninguna tabla.

**Solución:** Añadir la función `_generate_initial_migration()` en `project_generator.py` que parsea el `models.py` generado por el LLM, extrae los campos del modelo `Item` y construye dinámicamente el archivo de migración inicial.

---

### Problema 7: Imagen de n8n sin docker-cli

**Síntoma:** Error `/bin/sh: docker: not found` en el nodo Elegir Puerto.

**Causa:** Al reconstruir el entorno se usó la imagen oficial `n8nio/n8n:latest` en vez de la imagen personalizada `n8n-custom` que tiene `docker-cli` instalado.

**Solución:** Reconstruir la imagen `n8n-custom` con el Dockerfile que instala `docker-cli` y actualizar el `docker-compose.yml` para usar `image: n8n-custom` en vez de `image: n8nio/n8n:latest`. También añadir el montaje de `/var/run/docker.sock` que es imprescindible para que Docker funcione dentro del contenedor.

---

*Documento generado el 16/03/2026*