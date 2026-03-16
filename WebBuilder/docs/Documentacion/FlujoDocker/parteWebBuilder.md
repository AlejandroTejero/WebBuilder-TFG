# WebBuilder — Despliegue automático con n8n + Docker

Documentación del sistema de despliegue automático de proyectos generados por WebBuilder usando n8n como orquestador y Docker para levantar los contenedores.

---

## Índice

- [Arquitectura general](#arquitectura-general)
- [Requisitos previos](#requisitos-previos)
- [Cambios en Django](#cambios-en-django)
- [Workflow de n8n](#workflow-de-n8n)
- [Cómo arrancar n8n](#cómo-arrancar-n8n)

---

## Arquitectura general

El flujo completo cuando el usuario pulsa "Desplegar preview" es:

```
Usuario → Django (site_deploy) → n8n webhook → Docker build + run → preview_url → Django → Usuario
```

1. El usuario pulsa el botón **Desplegar preview** en `site_render.html`
2. Django construye el ZIP del proyecto en memoria y lo manda a n8n via POST multipart
3. n8n recibe el ZIP, lo guarda en disco, lo descomprime, hace `docker build` y `docker run`
4. n8n devuelve `{"preview_url": "http://localhost:PUERTO"}` a Django
5. Django guarda la URL en `site.preview_url` y muestra el botón **Abrir preview**

---

## Requisitos previos

- n8n corriendo con la imagen custom `n8n-custom` (tiene `docker-cli` instalado)
- Socket de Docker montado en el contenedor de n8n (`/var/run/docker.sock`)
- Carpeta `/home/alejandro/Desktop/TFG/docker/n8n/local-files` montada en `/files`
- Carpeta `/files/deploys` creada dentro del contenedor:

```bash
docker exec -it n8n mkdir -p /files/deploys
```

---

## Cambios en Django

### 1. `views/site.py`

**Imports añadidos** (después de `import zipfile`):

```python
import requests as http_requests

from django.conf import settings
```

**Constante del webhook** (después de los imports):

```python
N8N_DEPLOY_WEBHOOK = getattr(settings, "N8N_DEPLOY_WEBHOOK", "http://localhost:5678/webhook/webbuilder-deploy")
```

**Función `site_deploy`** (al final del archivo, después de `site_download_zip`):

```python
@login_required
def site_deploy(request, api_request_id: int):
    if request.method != "POST":
        return redirect("site_render", api_request_id=api_request_id)

    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    site = get_object_or_404(GeneratedSite, project_source=api_request)

    if site.generation_status != "ready" or not site.project_files:
        messages.error(request, "El proyecto debe estar generado antes de desplegarlo.")
        return redirect("site_render", api_request_id=api_request_id)

    # Construir ZIP en memoria
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in (site.project_files or {}).items():
            safe_path = str(path).lstrip("/").replace("..", "")
            zf.writestr(safe_path, content or "")
    buf.seek(0)

    zip_name = f"{site.project_name or 'generated_site'}.zip".replace(" ", "_")

    # Mandar el ZIP a n8n como multipart/form-data
    try:
        response = http_requests.post(
            N8N_DEPLOY_WEBHOOK,
            files={"file": (zip_name, buf, "application/zip")},
            data={
                "project_name": site.project_name or "generated_site",
                "site_id": str(site.pk),
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        preview_url = data.get("preview_url") or ""
    except http_requests.exceptions.Timeout:
        messages.error(request, "n8n tardó demasiado en responder (timeout 120s).")
        return redirect("site_render", api_request_id=api_request_id)
    except http_requests.exceptions.ConnectionError:
        messages.error(request, "No se pudo conectar con n8n. ¿Está corriendo?")
        return redirect("site_render", api_request_id=api_request_id)
    except Exception as exc:
        messages.error(request, f"Error al desplegar: {exc}")
        return redirect("site_render", api_request_id=api_request_id)

    if not preview_url:
        messages.error(request, "n8n no devolvió una preview_url. Revisa el workflow.")
        return redirect("site_render", api_request_id=api_request_id)

    site.preview_url = preview_url
    site.save(update_fields=["preview_url"])

    messages.success(request, f"Proyecto desplegado. Preview: {preview_url}")
    return redirect("site_render", api_request_id=api_request_id)
```

### 2. `views/__init__.py`

Añadir `site_deploy` a la línea de imports:

```python
from .site import site_render, site_generate, site_download_zip, site_status, site_deploy
```

### 3. `urls.py`

Añadir después de la ruta de status:

```python
path("site/<int:api_request_id>/deploy/", views.site_deploy, name="site_deploy"),
```

### 4. `templates/WebBuilder/site_render.html`

Añadir el botón de despliegue justo antes del bloque de preview:

```html
<!-- Desplegar en Docker via n8n -->
{% if site.generation_status == "ready" %}
  <form method="post" action="{% url 'site_deploy' api_request.id %}" style="margin:0;" id="deploy-form">
    {% csrf_token %}
    <button class="asst-btn asst-btn--primary" type="submit" id="deploy-btn">
      Desplegar preview
    </button>
  </form>
{% endif %}
```

Y el JS del overlay antes del `})();` final:

```javascript
// Botón desplegar → overlay de espera
const deployForm = document.getElementById('deploy-form');
if (deployForm) {
  deployForm.addEventListener('submit', () => {
    const btn = document.getElementById('deploy-btn');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Desplegando...';
    }
    const title = document.querySelector('.asst-loading__title');
    const sub   = document.querySelector('.asst-loading__sub');
    if (title) title.textContent = 'Desplegando en Docker...';
    if (sub)   sub.textContent   = 'n8n está haciendo build y arrancando el contenedor';
    overlay.classList.add('active');
  });
}
```

### 5. `.env`

```
N8N_DEPLOY_WEBHOOK=http://localhost:5678/webhook/webbuilder-deploy
```

### 6. `settings.py`

```python
N8N_DEPLOY_WEBHOOK = os.getenv("N8N_DEPLOY_WEBHOOK", "http://localhost:5678/webhook/webbuilder-deploy")
```

---

## Workflow de n8n

**Nombre:** `WebBuilder - Dockers`

### Nodos en orden

#### 1. Webhook
- **Type**: Webhook
- **HTTP Method**: POST
- **Path**: `webbuilder-deploy`
- **Authentication**: None
- **Respond**: Using Respond to Webhook Node

#### 2. Preparar Variables
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const body = $input.first().json.body;
const projectName = (body.project_name || 'generated_site')
  .replace(/[^a-zA-Z0-9_-]/g, '_')
  .toLowerCase();

return [{
  json: {
    project_name: projectName,
    zip_filename: projectName + '.zip',
    deploy_dir: '/files/deploys/' + projectName,
    container_name: 'wb_' + projectName,
  },
  binary: $input.first().binary
}];
```

#### 3. Guardar ZIP
- **Type**: Read/Write Files from Disk
- **Operation**: Write File to Disk
- **File Path**: `={{ $('Preparar Variables').item.json.deploy_dir + '/' + $('Preparar Variables').item.json.zip_filename }}`
- **Input Binary Field**: `data`

#### 4. Descomprimir ZIP
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const { execSync } = require('child_process');

const deployDir = $('Preparar Variables').item.json.deploy_dir;
const zipFilename = $('Preparar Variables').item.json.zip_filename;

execSync(`mkdir -p ${deployDir}/src`);
execSync(`unzip -o ${deployDir}/${zipFilename} -d ${deployDir}/src`);

return $input.all();
```

#### 5. Restablecer Contenedor
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const { execSync } = require('child_process');

const containerName = $('Preparar Variables').item.json.container_name;

try {
  execSync(`docker stop ${containerName}`);
  execSync(`docker rm ${containerName}`);
} catch(e) {
  // Si no existe el contenedor no pasa nada, continuamos
}

return $input.all();
```

#### 6. Elegir Puerto
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const { execSync } = require('child_process');

const containerName = $('Preparar Variables').item.json.container_name;
const deployDir = $('Preparar Variables').item.json.deploy_dir;
const projectName = $('Preparar Variables').item.json.project_name;

// Buscar un puerto libre entre 8100 y 8999
let port = null;
for (let p = 8100; p <= 8999; p++) {
  try {
    execSync(`docker ps --format "{{.Ports}}" | grep ":${p}->"`, { stdio: 'pipe' });
  } catch(e) {
    port = p;
    break;
  }
}

if (!port) throw new Error('No hay puertos libres entre 8100 y 8999');

return [{
  json: {
    ...$('Preparar Variables').item.json,
    port,
    preview_url: `http://localhost:${port}`,
  }
}];
```

#### 7. Docker Build
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const { execSync } = require('child_process');

const containerName = $('Elegir Puerto').item.json.container_name;
const deployDir = $('Elegir Puerto').item.json.deploy_dir;

const srcDir = deployDir + '/src';
const output = execSync(`ls ${srcDir}`).toString().trim();
const subdir = output.split('\n')[0];
const buildDir = srcDir + '/' + subdir;

execSync(`docker build -t ${containerName}:latest ${buildDir}`, { timeout: 120000 });

return [{
  json: {
    ...$('Elegir Puerto').item.json,
    build_dir: buildDir,
  }
}];
```

#### 8. Docker Run
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const { execSync } = require('child_process');

const containerName = $('Elegir Puerto').item.json.container_name;
const port = $('Elegir Puerto').item.json.port;

execSync(`docker run -d --name ${containerName} -p ${port}:8000 ${containerName}:latest`);

return $input.all();
```

#### 9. Verificar docker
- **Type**: Code (JavaScript, Run Once for All Items)

```javascript
const { execSync } = require('child_process');

const containerName = $('Elegir Puerto').item.json.container_name;

await new Promise(resolve => setTimeout(resolve, 4000));

const status = execSync(`docker ps --filter name=${containerName} --format "{{.Status}}"`)
  .toString()
  .trim();

if (!status) throw new Error(`El contenedor ${containerName} no está corriendo`);

return [{
  json: {
    ...$('Elegir Puerto').item.json,
    container_status: status,
  }
}];
```

#### 10. Respond to Webhook
- **Type**: Respond to Webhook
- **Respond With**: JSON
- **Response Body**:
```
={{ JSON.stringify({ preview_url: $('Elegir Puerto').item.json.preview_url, container: $('Elegir Puerto').item.json.container_name, port: $('Elegir Puerto').item.json.port }) }}
```

---

## Cómo arrancar n8n

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v n8n_n8n_data:/home/node/.n8n \
  -v /home/alejandro/Desktop/TFG/docker/n8n/local-files:/files \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --user root \
  n8n-custom
```

> La imagen `n8n-custom` se buildea con el Dockerfile que instala `docker-cli` sobre la imagen oficial de n8n.

### Dockerfile de n8n-custom

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

### Rebuildar la imagen si hay cambios

```bash
cd /home/alejandro/Desktop/TFG/docker/n8n
docker build -t n8n-custom .
docker stop n8n && docker rm n8n
# Volver a ejecutar el docker run de arriba
```