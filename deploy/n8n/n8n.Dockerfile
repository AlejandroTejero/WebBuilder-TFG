# Imagen base oficial de n8n
FROM n8nio/n8n:latest

# Instalar Docker CLI como root
# (necesario para que el workflow de deploy pueda ejecutar docker build/run)
USER root
RUN apk add --no-cache docker-cli

# Volver al usuario node por seguridad
USER node
