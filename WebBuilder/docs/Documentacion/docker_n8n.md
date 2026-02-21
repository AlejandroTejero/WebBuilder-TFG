# Descarga n8n en docker local (21/02)

# http://localhost:5678

## Índice

- [Actualizamos el pc](#1-actualizamos-el-pc)
- [Crear directorios](#2-crear-directorios)
- [Creamos fichero configuracion](#3-creamos-fichero-configuracion)
- [Ejecuccion del contendor](#4-ejecuccion-del-contendor)


## 1. Actualizamos el pc

```bash 
sudo apt update && sudo apt upgrade
```

## 2. Crear directorios

- En mi caso esta al nivel del proyecto de django, debemos hacer:

```bash
ls : WebBuilder / entorno
mkdir docker
cd docker
mkdir n8n
```

## 3. Creamos fichero configuracion

```bash
cd n8n
vi docker-compose.yml
```

```bash
services:
  n8n:
    image: n8nio/n8n:latest
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
      - N8N_ENCRYPTION_KEY=CONTRASEÑA PRIVADA LARGA
      - N8N_SECURE_COOKIE=false
    volumes:
      - n8n_data:/home/node/.n8n
      - ./local-files:/files

volumes:
  n8n_data:
```

## 4. Ejecuccion del contendor
 
- Decarga el contenedor y la imagen de n8n, mostramos todos los contenedores disponibles con ps

```bash
sudo docker compose up -d
sudo docker ps
```

- Ver configuracion y como acceder al contenedor

```bash
sudo docker logs (2 primeros digitios del id del contendor)
```

- Entramos a la app con el enlace del final del mensaje anterior, que sera algo como:

```bash
http://localhost:5678
```