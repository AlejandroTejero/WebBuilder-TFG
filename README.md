# WebBuilder

**WebBuilder** es una aplicación web en **Django** que te permite pegar la **URL de una API (JSON o XML)**, analizar automáticamente su estructura y **mapear campos** (title, description, image, date, etc.) para generar una web adapatada.

> ⚠️ Proyecto en desarrollo

---

## Tabla de contenidos
- [Qué hace](#qué-hace)
- [Características actuales](#características-actuales)
- [Stack y dependencias](#stack-y-dependencias)

---

## Qué hace
1. **Introduces una URL** (de una API que devuelve JSON o XML).
2. WebBuilder **descarga** la respuesta (`requests`) y detecta el formato.
3. **Parsea** el contenido:
   - JSON → `json.loads`
   - XML → validación segura (`defusedxml`) + conversión a dict (`xmltodict`)
4. Analiza la estructura para:
   - Encontrar la **colección principal de items** (lista de objetos)
   - Detectar keys comunes
   - Sugerir automáticamente qué campos podrían corresponder a cada “rol” (title, description, image…)
5. Permite configurar un **mapping** (wizard) y evalúa su **calidad** (score /100 + avisos).
6. Genera una **preview** con items **normalizados** (para poder renderizar siempre con el mismo formato).
7. Guarda el historial de análisis del usuario.

---

## Características actuales
- **Login/Register**
- **Asistente por pasos**:
  - Paso 1: introducir URL
  - Paso 2: configurar mapping (con sugerencias)
  - Paso 3: preview de items normalizados
  - Paso 4: “Generar Web” (*en desarrollo*)
- Soporte **JSON y XML** y datos Excel a futuro.
- Guardado de análisis en BD por usuario:
  - URL, fecha, estado, raw_data, parsed_data, resumen, errores
- **Validación de mapping**:
  - Asigna campos y evita duplicados en roles sensibles.
- **Indicador de calidad del mapping**
- **Historial** de análisis (ordenado por fecha)

---

## Stack y dependencias
- **Python 3**
- **Django 5.1.7**
- Base de datos **SQLite**
- Librerías usadas:
  - `requests`
  - `xmltodict`
  - `defusedxml`

