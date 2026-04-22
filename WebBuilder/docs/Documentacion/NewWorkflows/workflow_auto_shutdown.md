# Implementación del workflow `auto-shutdown`

## Descripción general

El workflow `auto-shutdown` es una automatización programada en n8n que gestiona el ciclo de vida de los contenedores Docker levantados por WebBuilder durante el proceso de despliegue de previews. Su función es detectar contenedores inactivos —aquellos que llevan más de un tiempo configurable corriendo— y apagarlos automáticamente, liberando memoria RAM y puertos del sistema.

Sin este mecanismo, cada preview desplegado genera un contenedor Docker que permanece activo indefinidamente, independientemente de si el usuario sigue usándolo o no. En un entorno con múltiples usuarios esto provoca una acumulación progresiva de contenedores que degrada el rendimiento del servidor y agota los puertos disponibles (el rango configurado es 8100-8999).

Adicionalmente, el workflow notifica a Django tras cada apagado para mantener la base de datos consistente, y envía un resumen por email al administrador con el resultado de cada ejecución.

---

## Arquitectura del flujo

```
Cada 1 hora ──► Listar contenedores inactivos ──► ¿Hay contenedores?
                                                         │ true
                                                    Apagar contenedor
                                                         │
                                                    Notificar a Django
                                                         │
                                                       Resumen
                                                         │
                                                   Email al admin
```

El nodo **¿Hay contenedores?** actúa como filtro: si no hay contenedores que superen el umbral de tiempo, el flujo termina sin hacer nada. Si los hay, se procesan en bucle —un item por contenedor— y se agregan en el nodo **Resumen** antes de enviar el email.

### Nodos del workflow

| Nodo | Tipo | Función |
|---|---|---|
| Cada 1 hora | `n8n-nodes-base.scheduleTrigger` | Dispara el flujo cada hora |
| Listar contenedores inactivos | `n8n-nodes-base.code` | Ejecuta `docker ps` y filtra contenedores `wb_*` que superan el umbral de tiempo |
| ¿Hay contenedores? | `n8n-nodes-base.if` | Filtra items vacíos para evitar procesamiento innecesario |
| Apagar contenedor | `n8n-nodes-base.code` | Ejecuta `docker stop` y `docker rm` sobre cada contenedor |
| Notificar a Django | `n8n-nodes-base.httpRequest` | Llama al endpoint interno para actualizar el estado en BD |
| Resumen | `n8n-nodes-base.code` | Agrega los resultados del bucle en un único objeto |
| Email al admin | `n8n-nodes-base.emailSend` | Envía el informe de contenedores apagados al administrador |

### Parámetros configurables

| Parámetro | Valor | Descripción |
|---|---|---|
| `MAX_HOURS` | `1` | Horas de vida máxima de un contenedor antes de ser apagado |
| Filtro de nombre | `wb_*` | Solo se procesan contenedores cuyo nombre empiece por `wb_` |
| Frecuencia | Cada 1 hora | Intervalo del Schedule Trigger |

---

## Requisito de infraestructura

Para que n8n pueda ejecutar comandos Docker desde sus nodos de código, es necesario que el contenedor de n8n tenga acceso al socket Docker del host. Esto se configura en el `docker-compose.yml` mediante un volumen:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

Sin este montaje, los comandos `docker ps`, `docker stop` y `docker rm` ejecutados desde n8n fallarían con un error de acceso al daemon.

---

## Implementación en Django

### 1. Endpoint interno `/internal/container-shutdown/`

Se añadió la vista `container_shutdown` al fichero `WebBuilder/views/internal.py`. Este endpoint recibe el POST de n8n tras apagar cada contenedor y actualiza el `deploy_status` del sitio correspondiente en la base de datos, pasando de `"done"` a `"idle"` y limpiando la `preview_url`.

```python
@csrf_exempt
@require_POST
def container_shutdown(request):
    if not _check_token(request):
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    container_name = data.get("container_name", "").strip()
    if not container_name:
        return JsonResponse({"error": "container_name vacío"}, status=400)

    project_name = container_name.replace("wb_", "", 1)

    site = GeneratedSite.objects.filter(project_name=project_name).order_by('-created_at').first()
    if not site:
        logger.warning("[internal] Contenedor %s no encontrado en BD", container_name)
        return JsonResponse({"ok": False, "error": "Sitio no encontrado"}, status=404)

    site.deploy_status = "idle"
    site.preview_url = ""
    site.save(update_fields=["deploy_status", "preview_url"])
    logger.info("[internal] Contenedor %s marcado como idle", container_name)
    return JsonResponse({"ok": True, "project_name": project_name})
```

El endpoint reutiliza el mismo mecanismo de autenticación por token (`X-Internal-Token`) implementado para el endpoint `health-summary`, usando la variable de entorno `INTERNAL_TOKEN_METRICS`.

Se usa `filter().first()` en lugar de `get()` para evitar la excepción `MultipleObjectsReturned` en casos donde existan varios sitios con el mismo `project_name` en la base de datos, tomando siempre el más reciente.

### 2. Registro de la URL

```python
path("internal/container-shutdown/", views.container_shutdown, name="container_shutdown"),
```

### 3. Consistencia del estado en BD

El campo `deploy_status` del modelo `GeneratedSite` tiene los siguientes estados posibles:

| Estado | Significado |
|---|---|
| `idle` | Sin desplegar o contenedor apagado |
| `deploying` | Despliegue en curso |
| `done` | Contenedor activo y accesible |
| `error` | Error durante el despliegue |

Cuando el auto-shutdown apaga un contenedor, Django actualiza el estado de `"done"` a `"idle"` y limpia la `preview_url`, de forma que la interfaz refleje correctamente que el preview ya no está disponible en lugar de mostrar una URL inaccesible.

---

## Problemas encontrados durante la implementación

### 1. Conectividad entre n8n y Django

**Síntoma:** El nodo "Notificar a Django" fallaba con `The service refused the connection`.

**Causa y solución:** Mismo problema de red descrito en el workflow `health-check`. La solución aplicada fue idéntica: usar la IP del gateway de Docker (`172.18.0.1`) como host, arrancar Django con `runserver 0.0.0.0:8000` y configurar UFW para permitir conexiones desde la subred Docker al puerto 8000.

### 2. `MultipleObjectsReturned` al buscar el sitio por `project_name`

**Síntoma:** Django devolvía un error 500 con el mensaje `get() returned more than one GeneratedSite -- it returned 7`.

**Causa:** Durante las pruebas se habían generado múltiples proyectos con el mismo nombre (`project_name`), ya que este campo no tiene restricción de unicidad en el modelo. El uso de `GeneratedSite.objects.get(project_name=project_name)` falla cuando existe más de un resultado.

**Solución:** Sustituir `.get()` por `.filter().order_by('-created_at').first()`, tomando siempre el sitio más reciente en caso de duplicados:

```python
site = GeneratedSite.objects.filter(project_name=project_name).order_by('-created_at').first()
```

### 3. Umbral de tiempo para pruebas

**Síntoma:** Durante las pruebas el workflow no detectaba ningún contenedor porque el umbral era de 2 horas y los contenedores de prueba llevaban pocos minutos activos.

**Solución:** Reducir temporalmente `MAX_HOURS` a `0.08` (aproximadamente 5 minutos) para validar el flujo completo. Una vez verificado el funcionamiento, se estableció el valor definitivo en `1` hora.
