# Configuración de Docker en n8n para WebBuilder

Integración de Docker con n8n para el despliegue automático de proyectos generados (03/03)

## Índice

- [Objetivo](#1-objetivo)
- [Problema: n8n dentro de Docker](#2-problema-n8n-dentro-de-docker)
- [Solución: montar el socket de Docker](#3-solución-montar-el-socket-de-docker)
- [Problema: docker-cli no disponible](#4-problema-docker-cli-no-disponible)
- [Solución definitiva: imagen personalizada](#5-solución-definitiva-imagen-personalizada)
- [Comandos de referencia](#6-comandos-de-referencia)


## 1. Objetivo

El flujo de despliegue automático que queremos conseguir es:

```
Usuario pulsa "Desplegar" en WebBuilder
        ↓
Django empaqueta el proyecto en un ZIP y lo manda a n8n
        ↓
n8n descomprime el ZIP, ejecuta docker build y docker run
        ↓
El contenedor arranca en un puerto libre local
        ↓
n8n devuelve la URL del preview a Django
        ↓
Django guarda la URL y aparece el botón "Abrir preview"
```

Para que n8n pueda ejecutar comandos Docker necesita dos cosas:
- Acceso al **socket de Docker** del host (`/var/run/docker.sock`)
- El **cliente Docker** (`docker-cli`) instalado dentro del contenedor


## 2. Problema: n8n dentro de Docker

n8n corre dentro de un contenedor Docker, que por defecto está completamente aislado del sistema. Esto significa que no puede ver ni ejecutar nada fuera de él, incluido el Docker Engine del host.

```
Tu máquina (host)
├── Docker Engine  ← gestiona todo
└── Contenedor n8n ← aislado, no ve nada fuera
```

Si desde n8n intentamos ejecutar `docker build` o `docker run`, el comando no existe dentro del contenedor.


## 3. Solución: montar el socket de Docker

El socket `/var/run/docker.sock` es un canal de comunicación directo con el Docker Engine del host. Al montarlo dentro del contenedor de n8n, n8n puede pedirle al Docker del host que construya y arranque contenedores.

```
Tu máquina (host)
├── Docker Engine
│   └── /var/run/docker.sock  ← canal de comunicación
└── Contenedor n8n
    └── /var/run/docker.sock montado ← n8n puede usarlo
```

### Cómo ver la configuración actual del contenedor

Antes de recrear el contenedor hay que conocer su configuración para no perder nada:

```bash
# Ver volúmenes montados
docker inspect n8n --format '{{json .HostConfig.Binds}}'

# Ver política de reinicio
docker inspect n8n --format '{{json .HostConfig.RestartPolicy}}'
```

En este proyecto la configuración era:
- Volumen de datos: `n8n_n8n_data:/home/node/.n8n`
- Carpeta local: `/home/alejandro/Desktop/TFG/docker/n8n/local-files:/files`
- Restart policy: `unless-stopped`

### Recrear el contenedor con el socket montado

Los datos de n8n (workflows, credenciales) están en el volumen `n8n_n8n_data`, no en el contenedor. Parar y borrar el contenedor no borra los datos.

```bash
docker stop n8n
docker rm n8n

docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v n8n_n8n_data:/home/node/.n8n \
  -v /home/alejandro/Desktop/TFG/docker/n8n/local-files:/files \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --user root \
  n8nio/n8n:latest
```

La línea clave es `-v /var/run/docker.sock:/var/run/docker.sock`.

`--user root` es necesario para tener permisos de escritura en el socket y para poder instalar herramientas dentro del contenedor.

> **Importante:** Los workflows pueden desaparecer de la interfaz al cambiar de versión de imagen aunque los datos sigan en el volumen. Esto es un problema de migraciones de base de datos entre versiones. La solución es exportar los workflows en JSON antes de cualquier cambio (tres puntitos → Download en cada workflow).


## 4. Problema: docker-cli no disponible

Aunque el socket esté montado, la imagen de n8n no incluye el cliente Docker (`docker` como comando). El socket es el canal de comunicación pero sin el cliente no hay forma de enviar mensajes por ese canal.

```bash
docker exec -it n8n docker ps
# OCI runtime exec failed: exec: "docker": executable file not found in $PATH
```

### Intentos fallidos

La imagen `n8nio/n8n:latest` usa **Docker Hardened Images (Alpine 3.22)**, una versión de Alpine con el gestor de paquetes bloqueado por seguridad. Esto impide instalar paquetes con los métodos habituales:

```bash
# No funciona — gestor bloqueado en Hardened Images
apk add --no-cache docker-cli

# No funciona — no es Debian
apt-get install docker.io

# No funciona — no es RedHat
microdnf install docker
```

### Solución temporal (no persistente)

Se puede instalar el binario de Docker manualmente descargándolo directamente:

```bash
docker exec -it --user root n8n sh -c "cd /tmp && \
  wget -O docker.tgz https://download.docker.com/linux/static/stable/x86_64/docker-27.0.3.tgz && \
  tar xzf docker.tgz && \
  mv docker/docker /usr/local/bin/docker && \
  chmod +x /usr/local/bin/docker && \
  rm -rf /tmp/docker.tgz /tmp/docker"
```

El problema es que esta instalación es efímera: al reiniciar el contenedor desaparece porque se instala en el sistema de archivos del contenedor, que se resetea en cada arranque.


## 5. Solución definitiva: imagen personalizada

La solución permanente es crear una imagen personalizada basada en `n8nio/n8n:latest` que ya tenga el docker-cli instalado. Así cada vez que arranque el contenedor ya lo tiene disponible sin hacer nada.

### Dockerfile

Crear el archivo `/home/alejandro/Desktop/TFG/docker/n8n/Dockerfile`:

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

### Construir la imagen

```bash
cd /home/alejandro/Desktop/TFG/docker/n8n/
docker build -t n8n-custom .
```

### Arrancar el contenedor con la imagen personalizada

```bash
docker stop n8n
docker rm n8n

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

### Verificar que funciona

```bash
docker exec -it n8n docker ps
```

Si sale la lista de contenedores corriendo, n8n puede hablar con Docker del host correctamente.


## 6. Comandos de referencia

```bash
# Ver contenedores corriendo
docker ps

# Ver logs de n8n
docker logs n8n --tail 50

# Entrar dentro del contenedor
docker exec -it n8n sh

# Verificar que n8n puede usar Docker
docker exec -it n8n docker ps

# Reconstruir la imagen personalizada (si se modifica el Dockerfile)
cd /home/alejandro/Desktop/TFG/docker/n8n/
docker build -t n8n-custom .

# Reiniciar n8n
docker restart n8n
```

## Pendiente

- Crear workflow **WebBuilder - Deploy** en n8n con los nodos para recibir el ZIP, ejecutar `docker build` y `docker run`
- Añadir view `site_deploy` en Django y botón "Desplegar" en `site_render.html`
- Gestionar puertos libres para cada contenedor desplegado
- Guardar la URL del preview en `GeneratedSite.preview_url`