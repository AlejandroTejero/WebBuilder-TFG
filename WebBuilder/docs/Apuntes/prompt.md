Estoy desarrollando WebBuilder, una aplicación Django 5.1 que genera proyectos Django completos a partir de una URL de API pública y los empaqueta en un ZIP descargable.
Estoy implementando el despliegue automático de esos proyectos generados usando n8n + Docker en local (todo en la misma máquina).
Lo que tengo funcionando:

WebBuilder corriendo en local con Django
n8n corriendo en Docker con la imagen personalizada n8n-custom que tiene docker-cli instalado permanentemente
El socket de Docker montado en n8n (/var/run/docker.sock) para que n8n pueda hablar con el Docker del host
La carpeta /home/alejandro/Desktop/TFG/docker/n8n/local-files montada en /files dentro del contenedor de n8n
Workflows de Register y Login funcionando y publicados en n8n
El modelo GeneratedSite ya tiene el campo preview_url
El template site_render.html ya tiene el botón "Abrir preview" que aparece si preview_url tiene valor
Los ZIPs se generan en memoria en Django desde site.project_files (dict {ruta: contenido})

Lo que queda por hacer:

Crear la view site_deploy en Django (views/site.py) que construya el ZIP en memoria y lo mande a n8n via webhook como multipart/form-data
Añadir la URL site/<int:api_request_id>/deploy/ en urls.py
Añadir el botón "Desplegar" en site_render.html (solo visible cuando generation_status == 'ready')
Crear el workflow WebBuilder - Deploy en n8n con los nodos para recibir el ZIP, escribirlo en /files, descomprimirlo, ejecutar docker build y docker run en un puerto libre, y devolver la URL a Django
Que Django guarde la URL devuelta por n8n en site.preview_url

Archivos clave:

WebBuilder/views/site.py — donde está site_download_zip que ya construye el ZIP en memoria (reutilizar ese código)
WebBuilder/models.py — GeneratedSite con preview_url = models.URLField(blank=True, null=True)
WebBuilder/urls.py — donde hay que añadir la ruta de deploy
WebBuilder/templates/WebBuilder/site_render.html — donde hay que añadir el botón "Desplegar"