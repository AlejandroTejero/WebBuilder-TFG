# Instalación y configuración de pgAdmin 4 para WebBuilder

## Introducción

Una vez completada la migración de SQLite a PostgreSQL, se procedió a instalar **pgAdmin 4** como herramienta de administración y visualización de la base de datos. 

A diferencia de SQLite, donde toda la base de datos reside en un único fichero visible en el sistema de archivos (`db.sqlite3`), PostgreSQL funciona como un servicio del sistema operativo que gestiona los datos internamente en su propio directorio (`/var/lib/postgresql/16/main/`). Estos ficheros son internos del motor y no están pensados para accederse directamente. Por tanto, para inspeccionar, consultar y administrar la base de datos de forma visual es necesaria una herramienta dedicada.

pgAdmin 4 es la herramienta oficial de administración de PostgreSQL. Es de código abierto y ofrece una interfaz web completa desde la que se pueden explorar tablas, ejecutar consultas SQL, visualizar estadísticas del servidor en tiempo real, gestionar usuarios y permisos, y mucho más.

---

## Diferencia entre pgAdmin y el panel de administración de Django

Es importante distinguir estas dos herramientas, ya que aunque visualmente pueden parecer similares, operan en capas completamente distintas:

| Característica | Django Admin (`/admin`) | pgAdmin 4 |
|---|---|---|
| Capa de acceso | ORM de Django | PostgreSQL directo |
| Tablas visibles | Solo las definidas en `models.py` | Todas, incluidas las internas de Django |
| Relaciones | Las entiende y las muestra | Muestra claves foráneas como valores numéricos |
| Consultas | No permite SQL libre | Permite SQL puro completo |
| Métricas del servidor | No | Sí (sesiones, transacciones, I/O...) |
| Uso principal | Gestión de datos de la aplicación | Administración técnica de la base de datos |

En resumen: el admin de Django es para gestionar los datos de la aplicación; pgAdmin es para gestionar la base de datos en sí a nivel técnico.

---

## Entorno de trabajo

- **Sistema operativo:** Ubuntu 24.04 LTS (noble)
- **PostgreSQL:** 16.13
- **pgAdmin 4:** versión web (`pgadmin4-web`)
- **Servidor web:** Apache (configurado automáticamente por pgAdmin)
- **URL de acceso:** `http://localhost/pgadmin4`

---

## Paso 1 — Intento de instalación desde repositorios por defecto

El primer intento de instalación se realizó con el gestor de paquetes estándar de Ubuntu:

```bash
sudo apt install pgadmin4
```

**Resultado:**

```
Package pgadmin4 is not available, but is referred to by another package.
E: Package 'pgadmin4' has no installation candidate
```

pgAdmin 4 no está incluido en los repositorios oficiales de Ubuntu 24.04. Es necesario añadir el repositorio oficial del proyecto pgAdmin antes de poder instalarlo.

---

## Paso 2 — Añadir el repositorio oficial de pgAdmin

Se añadió la clave GPG del repositorio y la fuente de paquetes oficial:

```bash
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/noble pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

sudo apt update
```

El primer comando descarga la clave pública del repositorio y la almacena en formato binario en `/usr/share/keyrings/`. El segundo añade el repositorio a la lista de fuentes de apt, referenciando esa clave para verificar la autenticidad de los paquetes. El `apt update` refresca la lista de paquetes disponibles incluyendo ya el nuevo repositorio.

---

## Paso 3 — Instalación de pgAdmin 4 en modo web

Se optó por la versión web (`pgadmin4-web`) en lugar de la de escritorio (`pgadmin4-desktop`) por las siguientes razones:

- No requiere entorno gráfico dedicado
- Es accesible desde el navegador, lo que facilita demostraciones y capturas para la memoria
- Es la modalidad más habitual en entornos de servidor

```bash
sudo apt install pgadmin4-web
```

---

## Paso 4 — Configuración inicial

Tras la instalación, se ejecutó el script de configuración incluido con pgAdmin:

```bash
sudo /usr/pgadmin4/bin/setup-web.sh
```

El script realizó las siguientes acciones:

1. Creó los directorios de almacenamiento y logs de pgAdmin
2. Preguntó si se deseaba configurar Apache como servidor web — se confirmó con `y`
3. Habilitó el módulo `wsgi` de Apache
4. Montó la aplicación pgAdmin 4 en la ruta `/pgadmin4`
5. Solicitó un email y contraseña para la cuenta de administrador de pgAdmin

Apache actúa como servidor web que sirve la aplicación pgAdmin (que internamente es una aplicación Python/Flask) a través del módulo WSGI, de forma similar a como Django puede servirse con Gunicorn + Nginx.

---

## Paso 5 — Acceso a pgAdmin

Una vez configurado, pgAdmin es accesible desde el navegador en:

```
http://localhost/pgadmin4
```

Se accede con el email y contraseña definidos durante la configuración.

---

## Paso 6 — Conexión a la base de datos WebBuilder

Dentro de pgAdmin se creó una nueva conexión al servidor PostgreSQL local:

1. Clic en **"Agregar un Nuevo Servidor"**
2. **Pestaña General:**
   - Nombre: `WebBuilder`
3. **Pestaña Conexión:**

| Campo | Valor |
|-------|-------|
| Host / Dirección | `localhost` |
| Puerto | `5432` |
| Base de datos | `webbuilder_db` |
| Usuario | `webbuilder_user` |
| Contraseña | `webbuilder1234` |

Tras guardar, pgAdmin estableció la conexión y mostró el dashboard del servidor con métricas en tiempo real: sesiones activas, transacciones por segundo, tuples de entrada/salida y estadísticas de Block I/O.

---

## Paso 7 — Exploración de la base de datos

La estructura de la base de datos es accesible desde el árbol del panel izquierdo navegando por:

```
Servers
└── WebBuilder
    └── Bases de Datos (2)
        ├── postgres          ← BD interna del sistema, no tocar
        └── webbuilder_db     ← BD de la aplicación
            └── Esquemas
                └── public
                    └── Tablas (16)
                        ├── WebBuilder_apirequest
                        ├── WebBuilder_generatedsite
                        ├── WebBuilder_generationlog
                        ├── WebBuilder_siteuser
                        ├── WebBuilder_siteversion
                        ├── WebBuilder_userprofile
                        ├── auth_group
                        ├── auth_group_permissions
                        ├── auth_permission
                        ├── auth_user
                        ├── auth_user_groups
                        ├── auth_user_user_permissions
                        ├── django_admin_log
                        ├── django_content_type
                        ├── django_migrations
                        └── django_session
```

> **Nota importante:** En el árbol aparecen dos bases de datos — `postgres` y `webbuilder_db`. La BD `postgres` es la base de datos interna del sistema PostgreSQL y no debe modificarse. Toda la información de la aplicación WebBuilder reside en `webbuilder_db`.

Para consultar el contenido de cualquier tabla: clic derecho sobre la tabla → **Ver/Editar datos** → **Todas las filas**.

---

## Resumen de comandos ejecutados

```bash
# 1. Añadir clave GPG del repositorio oficial
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

# 2. Añadir repositorio
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/noble pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

# 3. Actualizar lista de paquetes
sudo apt update

# 4. Instalar pgAdmin 4 web
sudo apt install pgadmin4-web

# 5. Configurar Apache y crear cuenta de administrador
sudo /usr/pgadmin4/bin/setup-web.sh

# 6. Acceder desde el navegador
# http://localhost/pgadmin4
```
