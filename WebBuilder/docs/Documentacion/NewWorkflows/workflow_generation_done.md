# Implementación del workflow `generation-done`

## Descripción general

El workflow `generation-done` es una automatización implementada en n8n que notifica al usuario por correo electrónico cuando la generación de su proyecto Django ha finalizado correctamente. Su propósito es desacoplar la notificación del ciclo de vida de la petición HTTP, permitiendo que el usuario abandone la pantalla durante el proceso de generación —que puede durar varios minutos— y reciba el resultado de forma asíncrona.

Este workflow complementa la arquitectura existente de WebBuilder, que ya disponía de flujos n8n para el registro de usuarios y el inicio de sesión.

---

## Arquitectura del flujo

El flujo sigue una estructura de cuatro nodos en dos ramas paralelas:

```
Webhook ──► Preparar datos ──► Enviar email
       └──► Responder OK
```

La bifurcación es deliberada: el nodo **Responder OK** se conecta directamente al Webhook para que Django reciba la confirmación HTTP de forma inmediata, sin bloquear la espera del envío del correo. El envío del email ocurre en paralelo, de forma asíncrona desde el punto de vista de Django.

### Nodos del workflow

| Nodo | Tipo | Función |
|---|---|---|
| Webhook | `n8n-nodes-base.webhook` | Recibe el POST de Django con los datos de la generación |
| Preparar datos | `n8n-nodes-base.code` | Valida el payload, formatea duración y número de items, humaniza el tipo de sitio |
| Enviar email | `n8n-nodes-base.emailSend` | Envía el correo HTML al usuario con las estadísticas de la generación |
| Responder OK | `n8n-nodes-base.respondToWebhook` | Responde 200 a Django inmediatamente |

---

## Implementación en Django

### 1. Variable de entorno

Se añadió la URL del webhook de n8n como variable de entorno para desacoplar la configuración del código:

```env
N8N_WEBHOOK_GENERATION_DONE=http://localhost:5678/webhook/webbuilder-generation-done
```

Y su correspondiente lectura en `settings.py`:

```python
N8N_WEBHOOK_GENERATION_DONE = os.environ.get("N8N_WEBHOOK_GENERATION_DONE", "")
```

### 2. Módulo `notifications.py`

Se creó el fichero `WebBuilder/utils/generator/notifications.py` con la función `notify_generation_done`, responsable de construir el payload y realizar la llamada HTTP al webhook:

```python
def notify_generation_done(site, duration_seconds: int = 0) -> None:
    webhook_url = getattr(settings, "N8N_WEBHOOK_GENERATION_DONE", "")
    if not webhook_url:
        return

    plan = site.accepted_plan or {}
    fields = plan.get("fields") or []
    source = site.project_source

    payload = {
        "email":            source.user.email,
        "username":         source.user.username,
        "site_title":       plan.get("site_title", "Tu sitio"),
        "site_type":        plan.get("site_type", "other"),
        "api_url":          source.api_url,
        "preview_url":      site.preview_url or "",
        "zip_url":          f"/site/{site.public_id}/download/",
        "num_items":        len((plan.get("_meta") or {}).get("sample_items") or []),
        "num_fields":       len(fields),
        "duration_seconds": duration_seconds,
        "llm_model":        getattr(settings, "LLM_MODEL", ""),
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=30)
        logger.info("[notify] generation-done enviado → %s", resp.status_code)
    except Exception as e:
        logger.warning("[notify] Fallo al notificar generation-done: %s", e)
```

El bloque `try/except` garantiza que un fallo en la notificación nunca interrumpa ni afecte al resultado de la generación.

### 3. Integración en `_run_generation`

La llamada a `notify_generation_done` se integró en la función `_run_generation` de `views/site.py`, que ejecuta la generación en un hilo secundario. Se añadió medición del tiempo de generación mediante `time.time()`:

```python
import time

def _run_generation(site_id: int):
    from ..models import GeneratedSite
    from ..utils.generator.notifications import notify_generation_done

    start_time = time.time()

    try:
        site = GeneratedSite.objects.get(pk=site_id)
        files = generate_project_files(site)
        site.project_files = files
        site.generation_status = "ready"
        site.generation_error = ""
        site.save(update_fields=["project_files", "generation_status", "generation_error"])

        duration = int(time.time() - start_time)
        notify_generation_done(site, duration_seconds=duration)

    except Exception as e:
        ...
```

La notificación se realiza tras el `save()` para garantizar que el estado en base de datos es consistente antes de informar al usuario.

---

## Problemas encontrados durante la implementación

### 1. Timeout por arquitectura secuencial del workflow

**Síntoma:** Django registraba el error `HTTPConnectionPool: Read timed out` a los 30 segundos, aunque n8n recibía correctamente el payload.

**Causa:** El workflow tenía una arquitectura lineal (`Webhook → Preparar datos → Enviar email → Responder OK`), lo que hacía que Django bloqueara la espera hasta que n8n terminaba de enviar el correo. El envío SMTP puede tardar más de 30 segundos.

**Solución:** Se reestructuró el workflow para que el nodo **Responder OK** se conecte directamente al Webhook en paralelo con el resto del flujo, implementando un patrón *fire and forget*. Django recibe el 200 inmediatamente y n8n continúa el procesamiento de forma independiente.

### 2. Workflows no registrados tras publicación en caliente

**Síntoma:** Tras publicar el workflow en n8n, los logs de Docker seguían mostrando `0 published workflows` y el webhook no respondía.

**Causa:** n8n registra los webhooks al arrancar, no cuando se publica un workflow en caliente. Los workflows publicados después del arranque no quedan registrados hasta el siguiente reinicio.

**Solución:** Reiniciar el contenedor de n8n tras publicar nuevos workflows:

```bash
docker restart <container_id>
```

### 3. Credenciales SMTP incorrectas

**Síntoma:** El nodo de envío de email fallaba con `The connection timed out`.

**Causa:** Las credenciales SMTP configuradas en n8n usaban la contraseña de cuenta de Google en lugar de una contraseña de aplicación (*App Password*), requerida cuando la verificación en dos pasos está activa.

**Solución:** Generar una contraseña de aplicación desde la configuración de seguridad de Google (`Cuenta de Google → Seguridad → Verificación en dos pasos → Contraseñas de aplicación`) y configurarla en las credenciales SMTP de n8n con los siguientes parámetros:

| Parámetro | Valor |
|---|---|
| Host | `smtp.gmail.com` |
| Port | `465` |
| SSL | Activado |
| User | Dirección de Gmail |
| Password | App Password de 16 caracteres |
