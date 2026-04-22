# Migración de SQLite a PostgreSQL en WebBuilder

## Introducción

Durante el desarrollo del TFG, la base de datos utilizada inicialmente fue **SQLite**, la opción por defecto de Django. SQLite es adecuada para desarrollo y pruebas locales, pero presenta limitaciones importantes de cara a un entorno de producción real: no soporta conexiones concurrentes, no escala bien con múltiples usuarios simultáneos, y su soporte de tipos de datos avanzados como `JSONField` es limitado (almacena JSON como texto plano sin capacidad de indexación ni consulta sobre los campos).

Por estas razones se decidió migrar a **PostgreSQL**, un sistema de gestión de bases de datos relacional de código abierto, robusto y ampliamente utilizado en producción. PostgreSQL ofrece soporte nativo de JSON con índices y consultas sobre campos JSON, mejor rendimiento en entornos concurrentes, y es el estándar de facto en proyectos Django de producción.

El proyecto WebBuilder hace un uso intensivo de `JSONField` en varios modelos (`APIRequest`, `GeneratedSite`, `SiteVersion`, `GenerationLog`), lo que refuerza la idoneidad de PostgreSQL frente a SQLite o MySQL.

---

## Entorno de trabajo

- **Sistema operativo:** Ubuntu 24.04 LTS
- **Python:** 3.12
- **Django:** 5.1.7
- **Entorno virtual:** `entorno/` en `~/Desktop/TFG/`
- **Directorio del proyecto:** `~/Desktop/TFG/WebBuilder/project/`
- **PostgreSQL instalado:** 16.13

---

## Paso 1 — Exportar los datos existentes de SQLite

Antes de realizar ningún cambio, se exportaron todos los datos de la base de datos SQLite a un fichero JSON como copia de seguridad. Esto garantiza que ningún dato se pierde durante la migración.

Se utilizó el comando `dumpdata` de Django, excluyendo las tablas internas `auth.permission` y `contenttypes`. Estas tablas se excluyen deliberadamente porque Django las regenera automáticamente al ejecutar las migraciones, y si se incluyen en el fixture causan errores de integridad referencial al importar en una base de datos nueva.

```bash
cd ~/Desktop/TFG/WebBuilder/project
source ~/Desktop/TFG/entorno/bin/activate
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > backup_sqlite.json
```

**Verificación del backup:**

```bash
wc -l backup_sqlite.json
# Resultado: 71597 backup_sqlite.json
```

El fichero `backup_sqlite.json` contiene 71.597 líneas, lo que confirma que el volcado incluye todos los datos de la aplicación: usuarios, análisis, sitios generados, logs de generación, versiones y métricas.

---

## Paso 2 — Instalación de PostgreSQL

Se instaló PostgreSQL y su paquete de utilidades adicionales mediante el gestor de paquetes de Ubuntu:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

El instalador creó automáticamente el cluster de base de datos `16/main` con configuración regional `en_US.UTF-8` y zona horaria `Europe/Madrid`.

**Verificación del servicio:**

```bash
sudo systemctl status postgresql
```

Resultado esperado:

```
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/usr/lib/systemd/system/postgresql.service; enabled; preset: enabled)
     Active: active (exited) since Wed 2026-04-22 17:40:18 CEST; 13s ago
```

El estado `active (exited)` es el comportamiento correcto en systemd para servicios que lanzan procesos hijos — el servidor PostgreSQL está activo y funcionando.

---

## Paso 3 — Creación de la base de datos y el usuario

Se accedió a la consola interactiva de PostgreSQL como el superusuario del sistema (`postgres`):

```bash
sudo -u postgres psql
```

### Incidencia durante la creación

Durante la primera sesión de psql se produjo un error por omitir el punto y coma (`;`) al final del comando `CREATE DATABASE`, lo que hizo que PostgreSQL interpretara las dos instrucciones como una sola:

```sql
-- INCORRECTO (sin ; al final de la primera línea)
CREATE DATABASE webbuilder_db
CREATE USER webbuilder_user WITH PASSWORD 'webbuilder1234';
-- ERROR: syntax error at or near "CREATE"
```

Como consecuencia, el usuario `webbuilder_user` se creó correctamente (`CREATE ROLE`) pero la base de datos no llegó a crearse. Al intentar hacer el `GRANT` sobre una base de datos inexistente, se obtuvo el error `database "webbuilder_db" does not exist`.

### Resolución

Se salió de psql con `\q` y se volvió a entrar para ejecutar los comandos correctamente, con punto y coma en cada línea:

```sql
CREATE DATABASE webbuilder_db;
GRANT ALL PRIVILEGES ON DATABASE webbuilder_db TO webbuilder_user;
\q
```

El usuario ya existía del intento anterior, por lo que no fue necesario recrearlo. El error `role "webbuilder_user" already exists` que apareció al intentar crearlo de nuevo es informativo y no supone ningún problema.

**Resumen de la configuración de la base de datos:**

| Parámetro | Valor |
|-----------|-------|
| Nombre de la BD | `webbuilder_db` |
| Usuario | `webbuilder_user` |
| Contraseña | `webbuilder1234` |
| Host | `localhost` |
| Puerto | `5432` |

---

## Paso 4 — Instalación del driver de Python para PostgreSQL

Con el entorno virtual activo, se instaló `psycopg2-binary`, el adaptador de PostgreSQL para Python que Django necesita para comunicarse con la base de datos:

```bash
pip install psycopg2-binary
```

Se instaló la versión `2.9.12`. La variante `binary` incluye las librerías compiladas de PostgreSQL, evitando la necesidad de tener instaladas las cabeceras de desarrollo del sistema.

> **Nota:** Al estar el entorno virtual activo (indicado por el prefijo `(entorno)` en el prompt), la instalación queda confinada al entorno virtual y no afecta al sistema.

---

## Paso 5 — Configuración de variables de entorno y settings

### Fichero `.env`

Se añadieron las credenciales de PostgreSQL al fichero `.env` del proyecto (`WebBuilder/project/.env`), siguiendo el mismo patrón que el resto de variables de entorno ya existentes:

```env
DB_NAME=webbuilder_db
DB_USER=webbuilder_user
DB_PASSWORD=webbuilder1234
DB_HOST=localhost
DB_PORT=5432
```

### Fichero `settings.py`

Se modificó el bloque `DATABASES` en `project/settings.py` para reemplazar la configuración de SQLite por PostgreSQL, leyendo las credenciales desde las variables de entorno:

**Configuración anterior (SQLite):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Configuración nueva (PostgreSQL):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'webbuilder_db'),
        'USER': os.getenv('DB_USER', 'webbuilder_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

El uso de `os.getenv()` con valor por defecto garantiza que el proyecto puede arrancarse aunque alguna variable de entorno no esté definida, y facilita el despliegue en producción simplemente cambiando el `.env`.

---

## Paso 6 — Aplicación de migraciones

Se ejecutó el comando de migraciones de Django para crear todas las tablas en la nueva base de datos PostgreSQL:

```bash
python manage.py migrate
```

### Incidencia: permiso denegado en el schema public

En el primer intento, el comando falló con el siguiente error:

```
django.db.utils.ProgrammingError: permission denied for schema public
LINE 1: CREATE TABLE "django_migrations" ...
```

Este error es característico de **PostgreSQL 15 y versiones superiores**, donde se eliminó el privilegio `CREATE` en el schema `public` para usuarios no superadministradores, que anteriormente se concedía por defecto.

### Resolución

Se volvió a entrar en psql como superusuario para conceder los permisos necesarios:

```bash
sudo -u postgres psql
```

```sql
GRANT ALL ON SCHEMA public TO webbuilder_user;
ALTER DATABASE webbuilder_db OWNER TO webbuilder_user;
\q
```

#### Segunda incidencia durante la resolución

Al ejecutar el `ALTER DATABASE` también se omitió el `;` en la primera vez, repitiendo el mismo error de sintaxis del paso 3. Se repitió el comando correctamente:

```sql
ALTER DATABASE webbuilder_db OWNER TO webbuilder_user;
```

### Resultado de las migraciones

Con los permisos corregidos, el comando `migrate` completó con éxito las 33 migraciones del proyecto:

```
Applying contenttypes.0001_initial... OK
Applying auth.0001_initial... OK
Applying WebBuilder.0001_initial... OK
Applying WebBuilder.0002_rename_source_data_apirequest_error_message_and_more... OK
Applying WebBuilder.0003_apirequest_field_mapping... OK
Applying WebBuilder.0004_rename_raw_response_apirequest_raw_data... OK
Applying WebBuilder.0005_apirequest_plan_accepted... OK
Applying WebBuilder.0006_generatedsite... OK
Applying WebBuilder.0007_rename_plublic_id_generatedsite_public_id... OK
Applying WebBuilder.0008_rename_theme_css_generatedsite_generation_error_and_more... OK
Applying WebBuilder.0009_generatedsite_deploy_error_and_more... OK
Applying WebBuilder.0010_generationlog... OK
Applying WebBuilder.0011_apirequest_input_type... OK
Applying WebBuilder.0012_siteversion... OK
Applying WebBuilder.0013_siteuser... OK
Applying WebBuilder.0014_userprofile... OK
Applying WebBuilder.0015_generatedsite_generation_step... OK
Applying admin.0001_initial... OK
[...]
Applying sessions.0001_initial... OK
```

---

## Paso 7 — Concesión de permisos sobre secuencias

Antes de importar los datos, se concedieron permisos sobre las secuencias del schema `public`. Las secuencias son los contadores que PostgreSQL usa para generar los valores de los campos autoincrement (`id`). Sin este permiso, el `loaddata` fallaría al intentar actualizar los contadores de las claves primarias tras insertar los registros.

```bash
sudo -u postgres psql
```

```sql
\c webbuilder_db
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO webbuilder_user;
\q
```

---

## Paso 8 — Importación de los datos

Con la base de datos creada, las tablas migradas y los permisos correctos, se importaron los datos exportados en el paso 1:

```bash
python manage.py loaddata backup_sqlite.json
```

**Resultado:**

```
Installed 727 object(s) from 1 fixture(s)
```

Los 727 objetos corresponden a todos los registros de la aplicación: usuarios, perfiles, análisis de API, sitios generados, logs de generación, versiones de sitios, usuarios de sitios y registros de sesión.

---

## Verificación final

Se arrancó el servidor de desarrollo para comprobar que la aplicación funciona correctamente con PostgreSQL:

```bash
python manage.py runserver
```

Se verificó manualmente que:

- El historial de análisis y generaciones está íntegro.
- Las métricas muestran los datos correctamente.
- El login y la sesión funcionan con normalidad.
- Los sitios generados previamente son accesibles.

---

## Impacto sobre los workflows de n8n

Se analizaron los 6 workflows de n8n del proyecto para determinar si la migración afectaba a su funcionamiento:

- `WebBuilder - Login.json`
- `WebBuilder - Register.json`
- `webbuilder - auto-shutdown.json`
- `webbuilder - deploy.json`
- `webbuilder - generation-done.json`
- `webbuilder - health-check.json`

Los nodos utilizados son exclusivamente de tipo `webhook`, `httpRequest`, `emailSend`, `scheduleTrigger`, `code` y `respondToWebhook`. **Ningún workflow se conecta directamente a la base de datos** — toda la comunicación se realiza a través de la API HTTP de Django. Por tanto, el cambio de SQLite a PostgreSQL es completamente transparente para n8n y no requiere ninguna modificación en los workflows.

---

## Consideraciones para el despliegue en producción

La configuración actual funciona con PostgreSQL instalado localmente. De cara al despliegue en internet, existen dos opciones:

**Opción A — PostgreSQL en el mismo servidor:** Se instala PostgreSQL en la VPS o servidor donde se aloja la aplicación. La configuración es idéntica a la local, cambiando únicamente las credenciales en el `.env`.

**Opción B — PostgreSQL como servicio en la nube:** Se utiliza un proveedor gestionado como Supabase o Railway, que ofrecen PostgreSQL gratuito. En este caso, el bloque `DATABASES` del `settings.py` no requiere ningún cambio — simplemente se actualizan las variables de entorno del `.env` con las credenciales del proveedor. Esta opción es arquitectónicamente más robusta, ya que separa la base de datos del servidor de aplicación.

En ambos casos, el código Django permanece inalterado.

---

## Resumen de comandos ejecutados

```bash
# 1. Exportar datos de SQLite
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > backup_sqlite.json

# 2. Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 3. Crear BD y usuario (en psql)
sudo -u postgres psql
CREATE DATABASE webbuilder_db;
CREATE USER webbuilder_user WITH PASSWORD 'webbuilder1234';
GRANT ALL PRIVILEGES ON DATABASE webbuilder_db TO webbuilder_user;
\q

# 4. Instalar driver Python
pip install psycopg2-binary

# 5. Corregir permisos del schema public (en psql)
sudo -u postgres psql
GRANT ALL ON SCHEMA public TO webbuilder_user;
ALTER DATABASE webbuilder_db OWNER TO webbuilder_user;
\q

# 6. Aplicar migraciones
python manage.py migrate

# 7. Permisos sobre secuencias (en psql)
sudo -u postgres psql
\c webbuilder_db
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO webbuilder_user;
\q

# 8. Importar datos
python manage.py loaddata backup_sqlite.json
```
