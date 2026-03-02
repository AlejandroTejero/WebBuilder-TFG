# Implementación n8n — Workflows de Email (26/02)

Configuración de los workflows de n8n para el envío automático de emails en WebBuilder.

## Índice

- [Configuración de credenciales SMTP](#1-configuración-de-credenciales-smtp)
- [Workflow: WebBuilder - Register](#2-workflow-webbuilder---register)
- [Conectar Django con n8n](#3-conectar-django-con-n8n)


## 1. Configuración de credenciales SMTP

Para que n8n pueda enviar emails necesita acceso a una cuenta de correo. En este caso se usa Gmail con SMTP.

### Contraseña de aplicación de Google

Gmail no permite usar la contraseña normal de la cuenta. Hay que generar una contraseña de aplicación específica:

1. Ir a **myaccount.google.com/apppasswords**
2. Verificación en dos pasos debe estar activada (requisito de Google)
3. Poner de nombre **n8n** y darle a Crear
4. Google genera una contraseña de 16 caracteres — copiarla, solo se muestra una vez

### Configuración SMTP en n8n

En el nodo **Send an Email** → **Credential to connect with** → **Create new credential**:

- **User** — email de Gmail completo (`tumail@gmail.com`)
- **Password** — la contraseña de aplicación de 16 caracteres generada en el paso anterior
- **Host** — `smtp.gmail.com`
- **Port** — `587`
- **SSL/TLS** — desactivado

> Si en el futuro se quiere cambiar a un correo del proyecto, solo hay que editar esta credencial en **Credentials** de n8n. No hay que tocar nada del workflow ni del código de Django.


## 2. Workflow: WebBuilder - Register

Workflow que se dispara cuando un usuario se registra en WebBuilder y le manda un email de bienvenida.

### Nodo 1 — Webhook

El webhook es el punto de entrada del workflow. Está escuchando constantemente esperando que Django lo llame.

Configuración:
- **HTTP Method** — `POST`
- **Path** — `WebBuilder-Register`

Esto genera dos URLs:
- **Test URL** — para usar mientras se desarrolla: `http://localhost:5678/webhook-test/WebBuilder-Register`
- **Production URL** — para cuando el workflow está activo: `http://localhost:5678/webhook/WebBuilder-Register`

Los datos que llegan del webhook vienen dentro de `$json.body`:
- `$json.body.username` — nombre de usuario
- `$json.body.email` — email del usuario

### Nodo 2 — Send an Email

Configuración:
- **Credential to connect with** — SMTP account (configurada en el paso anterior)
- **Operation** — Send
- **From Email** — tu email de Gmail
- **To Email** — `{{ $json.body.email }}`
- **Subject** — `¡Bienvenido a WebBuilder, {{ $json.body.username }}!`
- **Email Format** — HTML
- **HTML** — plantilla de email adaptada al diseño de WebBuilder (fondo oscuro, acentos morados)

### Flujo completo
```
Usuario se registra en Django
        ↓
Django llama al webhook con { username, email }
        ↓
Nodo Webhook recibe los datos
        ↓
Nodo Send an Email manda el correo de bienvenida
```

### Activar el workflow

Una vez probado y funcionando correctamente:

1. Cerrar el panel del nodo
2. Darle a **Save** con Ctrl+S
3. Activar el workflow con el toggle de arriba a la derecha
4. Cambiar la URL en `auth.py` de Test URL a Production URL


## 3. Conectar Django con n8n

En `auth.py` las URLs de los webhooks se definen como variables al principio del archivo:
```python
N8N_WEBHOOK_REGISTRO = "http://localhost:5678/webhook-test/WebBuilder-Register"
N8N_WEBHOOK_LOGIN    = "TU_URL_WEBHOOK_LOGIN"  # pendiente
```

- Durante el desarrollo se usa la **Test URL** — el workflow no necesita estar activo
- En producción se cambia a la **Production URL** — el workflow debe estar activo con el toggle


## Pendiente

- Crear workflow **WebBuilder - Login** con su webhook y email de aviso
- Cambiar URLs de Test a Production en `auth.py` cuando el proyecto esté listo
- Implementar workflow de **recuperación de contraseña** con n8n