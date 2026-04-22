# Implementación del workflow `health-check`

## Descripción general

El workflow `health-check` es una automatización programada en n8n que genera y envía diariamente un informe de estado del sistema al administrador de WebBuilder. A diferencia de la página de métricas de la aplicación —que requiere acceso manual y es de naturaleza reactiva— este flujo actúa de forma proactiva: monitoriza el sistema de manera autónoma y alerta al administrador ante degradaciones del rendimiento sin necesidad de intervención humana.

Las métricas recopiladas cubren tanto la calidad de las generaciones (tasa de éxito, tasa de retry, duración media) como el estado de la infraestructura (contenedores activos, uso de disco), y se acompañan de un sistema de alertas automáticas con umbrales configurables.

---

## Arquitectura del flujo

El workflow sigue una estructura lineal de cuatro nodos:

```
Diario 09:00 ──► Pedir resumen a Django ──► Evaluar alertas ──► Email informe
```

A diferencia del workflow `generation-done`, en este caso la linealidad es correcta: el flujo está completamente desacoplado de Django (no hay ninguna petición HTTP esperando respuesta), por lo que no existe el problema de bloqueo descrito en el workflow anterior.

### Nodos del workflow

| Nodo | Tipo | Función |
|---|---|---|
| Diario 09:00 | `n8n-nodes-base.scheduleTrigger` | Dispara el flujo cada día a las 09:00 mediante cron (`0 9 * * *`) |
| Pedir resumen a Django | `n8n-nodes-base.httpRequest` | Realiza GET al endpoint interno `/internal/health-summary/` con token de autenticación |
| Evaluar alertas | `n8n-nodes-base.code` | Aplica reglas de alerta sobre las métricas recibidas y construye el contexto del email |
| Email informe | `n8n-nodes-base.emailSend` | Envía el informe HTML al administrador, con cabecera verde (OK) o roja (alerta) |

### Reglas de alerta

El nodo **Evaluar alertas** aplica las siguientes reglas sobre los datos recibidos:

| Condición | Alerta generada |
|---|---|
| `success_rate_24h < 70%` y al menos 3 generaciones | Tasa de éxito baja |
| `retry_rate_24h > 40%` | Degradación del LLM detectada |
| `active_containers > 15` | Demasiados contenedores activos |
| `disk_used_mb > 2000` | Uso de disco elevado |
| `failed_generations >= 5` | Múltiples generaciones fallidas |

Si ninguna regla se activa, el email se envía con cabecera verde y el estado `OK`. Si alguna regla se activa, la cabecera es roja y se lista cada alerta de forma explícita.

---

## Implementación en Django

### 1. Endpoint interno `/internal/health-summary/`

Se creó el fichero `WebBuilder/views/internal.py` con la vista `health_summary`, que calcula y devuelve las métricas del sistema en formato JSON. El acceso está protegido mediante un token de autenticación incluido en la cabecera `X-Internal-Token`.

```python
@require_GET
def health_summary(request):
    if not _check_token(request):
        return JsonResponse({"error": "Forbidden"}, status=403)

    since = timezone.now() - timedelta(hours=24)
    sites_24h = GeneratedSite.objects.filter(created_at__gte=since)
    total = sites_24h.count()

    # Cálculo de métricas...

    return JsonResponse({
        "generations_last_24h":  total,
        "success_rate_24h":      success_rate,
        "retry_rate_24h":        retry_rate,
        "avg_duration_seconds":  avg_duration,
        "failed_generations":    failed,
        "active_containers":     active_containers,
        "disk_used_mb":          disk_used_mb,
        "errors_last_24h":       errors_last_24h,
    })
```

Todas las métricas se calculan a partir de los modelos `GeneratedSite` y `GenerationLog` ya existentes en la base de datos, sin necesidad de nuevas migraciones.

### 2. Autenticación por token

Para evitar que el endpoint quede expuesto públicamente, se implementó un mecanismo de autenticación basado en un token secreto compartido entre Django y n8n.

**Variable de entorno en `.env`:**

```env
INTERNAL_TOKEN_METRICS=metricas-diarias-WebBuilder
```

**Lectura en `settings.py`:**

```python
INTERNAL_TOKEN_METRICS = os.environ.get("INTERNAL_TOKEN_METRICS", "")
```

**Verificación en la vista:**

```python
def _check_token(request) -> bool:
    token = request.headers.get("X-Internal-Token", "")
    return token == getattr(settings, "INTERNAL_TOKEN_METRICS", "")
```

n8n incluye este token en cada petición al endpoint mediante la cabecera `X-Internal-Token`.

### 3. Registro de la URL

Se añadió la ruta al fichero `urls.py` de la aplicación, separada semánticamente del resto de rutas de usuario:

```python
path("internal/health-summary/", views.health_summary, name="health_summary"),
```

---

## Problemas encontrados durante la implementación

### 1. Conectividad entre n8n (Docker) y Django (runserver)

**Síntoma:** n8n no podía establecer conexión con el endpoint Django. El error devuelto era `The connection cannot be established, this usually occurs due to an incorrect host (domain) value`.

**Causa:** Django arrancado con `runserver` por defecto solo escucha en `127.0.0.1` (loopback), lo que hace que sea inaccesible desde redes externas, incluida la red interna de Docker. Adicionalmente, el uso de `localhost` o `127.0.0.1` como host en la URL de n8n apunta al propio contenedor, no a la máquina host.

**Solución en dos pasos:**

**Paso 1:** Arrancar Django escuchando en todas las interfaces:

```bash
python manage.py runserver 0.0.0.0:8000
```

**Paso 2:** Determinar la IP del gateway de Docker para usarla como host en n8n:

```bash
docker inspect <container_id> | grep Gateway
# → "Gateway": "172.18.0.1"
```

La URL correcta para el nodo de n8n resultó ser `http://172.18.0.1:8000/internal/health-summary/`.

### 2. Cabecera `ALLOWED_HOSTS` rechazando la IP de Docker

**Síntoma:** Django respondía con `HTTP 400 Bad Request` e indicaba en los logs: `Invalid HTTP_HOST header: '172.18.0.1:8000'. You may need to add '172.18.0.1' to ALLOWED_HOSTS`.

**Causa:** Django valida que el header `Host` de cada petición entrante esté incluido en la lista `ALLOWED_HOSTS` de `settings.py`. Al recibir peticiones desde Docker con la IP `172.18.0.1`, esta no estaba incluida.

**Solución:** Añadir la IP del gateway de Docker a `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '172.18.0.1']
```

### 3. Restricción de red con UFW

**Síntoma:** Incluso con Django escuchando en `0.0.0.0:8000`, las conexiones desde el contenedor de Docker eran rechazadas a nivel de red.

**Causa:** El firewall UFW de Ubuntu estaba bloqueando las conexiones entrantes al puerto 8000 desde redes distintas al loopback.

**Solución:** Configurar UFW para permitir conexiones al puerto 8000 exclusivamente desde la subred de Docker, sin exponer el puerto a internet:

```bash
sudo ufw allow from 172.18.0.0/24 to any port 8000
```

Esta configuración es segura para un entorno de desarrollo: restringe el acceso al puerto 8000 únicamente a la red interna de Docker (`172.18.0.0/24`), impidiendo conexiones externas no autorizadas.

### 4. Credenciales SMTP incorrectas en el nodo Email informe

**Síntoma:** El nodo de envío de email fallaba con `The connection timed out` a pesar de que los datos llegaban correctamente al nodo.

**Causa:** El nodo tenía asignadas las credenciales SMTP antiguas, configuradas antes de la corrección de las credenciales de Gmail descrita en la implementación del workflow `generation-done`.

**Solución:** Actualizar las credenciales del nodo **Email informe** para que usen la cuenta SMTP correctamente configurada con App Password de Gmail.
