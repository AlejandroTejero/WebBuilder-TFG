# 🎨 Arquitectura UX - WebBuilder
## Sistema de Wizard Guiado para Usuarios No Técnicos

**Versión:** 2.0  
**Fecha:** Febrero 2026  
**Objetivo:** Rediseño completo del mapping + wizard con feedback inmediato vía preview

---

## 📋 TABLA DE CONTENIDOS

1. [Visión y Principios](#vision-y-principios)
2. [Arquitectura del Wizard](#arquitectura-del-wizard)
3. [Especificación de Componentes](#especificacion-de-componentes)
4. [Flujo de Datos](#flujo-de-datos)
5. [Detalle de los 6 Pasos](#detalle-de-los-6-pasos)
6. [Sistema de Preview Integrado](#sistema-de-preview-integrado)
7. [Microcopy y Mensajes](#microcopy-y-mensajes)
8. [Autocompletado y Sugerencias](#autocompletado-y-sugerencias)
9. [Plan de Implementación](#plan-de-implementacion)
10. [Anexos Técnicos](#anexos-tecnicos)

---

## 🎯 VISIÓN Y PRINCIPIOS

### Visión del Producto
**"Mis datos → Mi web"** sin entender nada de Django.

El usuario llega con una URL que devuelve datos. Sale con una web funcional desplegada. Todo el proceso debe sentirse como una conversación guiada, no como configurar tecnología.

### Principios UX Fundamentales

1. **No es configuración técnica, es construcción guiada**
   - El sistema pregunta "¿qué quieres mostrar?" no "configura el serializer"
   - Cada decisión tiene preview inmediato

2. **Siempre responder a 3 preguntas**
   - ¿Qué tengo? → Datos claros con ejemplos reales
   - ¿Qué quiero? → Tipo de web y estructura
   - ¿Cómo se conecta? → Mapping visual por huecos

3. **Feedback constante y progresivo**
   - El usuario ve su web construyéndose paso a paso
   - Validaciones en tiempo real, no al final
   - Puede volver atrás sin perder trabajo

4. **Lenguaje humano, cero jerga**
   - Evitar: model, view, serializer, field, queryset
   - Usar: elemento, contenido, listado, ficha, campos

---

## 🏗️ ARQUITECTURA DEL WIZARD

### Estructura General

```
┌─────────────────────────────────────────────────────────────┐
│                    HEADER PERSISTENTE                        │
│  [Nombre Proyecto ✏️]          [━━━━━●━━━━━━]  6/6 pasos   │
└─────────────────────────────────────────────────────────────┘
┌──────────────────┬──────────────────────────────────────────┐
│   NAVEGACIÓN     │            ÁREA DE TRABAJO                │
│                  │                                            │
│  [1] Fuente ✓    │  ┌────────────────┬──────────────────┐   │
│  [2] Contenido ● │  │  TUS DATOS     │   TU WEB         │   │
│  [3] Páginas     │  │                │                  │   │
│  [4] Campos      │  │  (ejemplos     │   (preview +     │   │
│  [5] Reglas      │  │   reales)      │    huecos)       │   │
│  [6] Publicar    │  │                │                  │   │
│                  │  └────────────────┴──────────────────┘   │
└──────────────────┴──────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│              FOOTER CON ACCIONES                             │
│  [← Atrás]           [Guardar borrador]      [Continuar →]  │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Clave

#### 1. Header Wizard
- **Nombre del proyecto** (editable inline)
- **Barra de progreso** con indicador visual del paso actual
- **Contador** de pasos (ej: "3 de 6")
- Estado persistente durante toda la sesión

#### 2. Navegación Lateral
- Menú de pasos con estados:
  - **Completado** ✓ (verde)
  - **Actual** ● (azul, enfatizado)
  - **Pendiente** (gris)
  - **Bloqueado** 🔒 (si falta info obligatoria)
- Click directo para navegar entre pasos ya completados
- Indicador visual de validación por paso

#### 3. Área de Trabajo (Two-Column Layout)
- **Columna Izquierda: "Tus Datos"**
  - Muestra estructura de datos con ejemplos reales
  - Explorador de campos interactivo
  - Búsqueda y filtrado
  
- **Columna Derecha: "Tu Web"**
  - Preview en vivo
  - Huecos para mapping
  - Tabs de páginas (Listado | Ficha | Categorías)

#### 4. Footer de Acciones
- **Atrás:** Volver al paso anterior
- **Guardar borrador:** Persistir estado sin validar
- **Continuar:** Validar y avanzar (deshabilitado si falta info crítica)

---

## 🔧 ESPECIFICACIÓN DE COMPONENTES

### Component: WizardHeader

```html
<div class="wizard-header">
  <div class="wizard-header__project">
    <h1 class="project-name" contenteditable="true">
      Mi Proyecto
    </h1>
    <button class="edit-icon" aria-label="Editar nombre">✏️</button>
  </div>
  
  <div class="wizard-header__progress">
    <div class="progress-bar">
      <div class="progress-fill" style="width: 33%"></div>
    </div>
    <span class="progress-label">Paso 2 de 6</span>
  </div>
</div>
```

**Comportamiento:**
- El nombre se guarda automáticamente (debounce 500ms)
- La barra se actualiza en cada cambio de paso
- Animación suave de transición

---

### Component: WizardNavigation

```html
<nav class="wizard-nav">
  <button class="wizard-nav__step" data-step="1" data-state="completed">
    <span class="step-number">1</span>
    <span class="step-label">Fuente</span>
    <span class="step-icon">✓</span>
  </button>
  
  <button class="wizard-nav__step" data-step="2" data-state="current">
    <span class="step-number">2</span>
    <span class="step-label">Contenido</span>
    <span class="step-icon">●</span>
  </button>
  
  <button class="wizard-nav__step" data-step="3" data-state="pending">
    <span class="step-number">3</span>
    <span class="step-label">Páginas</span>
  </button>
  
  <!-- ... resto de pasos -->
</nav>
```

**Estados:**
- `completed`: Verde, clickeable, muestra ✓
- `current`: Azul destacado, muestra ●
- `pending`: Gris, puede o no ser clickeable
- `locked`: Gris + 🔒, no clickeable

**Lógica de navegación:**
- Solo se puede volver a pasos completados
- No se puede saltar a pasos bloqueados
- Click en paso actual = scroll al inicio de ese paso

---

### Component: TwoColumnLayout

```html
<div class="wizard-workspace">
  <div class="workspace-column workspace-column--data">
    <div class="column-header">
      <h2>Tus Datos</h2>
      <p class="column-subtitle">Fuente conectada y ejemplos reales</p>
    </div>
    
    <div class="column-content">
      <!-- Contenido dinámico según el paso -->
    </div>
  </div>
  
  <div class="workspace-column workspace-column--preview">
    <div class="column-header">
      <h2>Tu Web</h2>
      <p class="column-subtitle">Vista previa en tiempo real</p>
    </div>
    
    <div class="column-content">
      <!-- Preview + huecos de mapping -->
    </div>
  </div>
</div>
```

**Responsive:**
- Desktop: 40% | 60% (datos | preview)
- Tablet: Tabs en lugar de columnas
- Mobile: Stack vertical con tabs

---

### Component: FieldExplorer (Paso 4)

```html
<div class="field-explorer">
  <div class="field-explorer__search">
    <input type="text" placeholder="Buscar campo..." />
  </div>
  
  <div class="field-explorer__tree">
    <div class="field-item" data-path="title">
      <div class="field-item__header">
        <span class="field-icon">📝</span>
        <span class="field-name">title</span>
        <span class="field-type">string</span>
      </div>
      <div class="field-item__examples">
        <div class="example">"Título de ejemplo 1"</div>
        <div class="example">"Título de ejemplo 2"</div>
        <div class="example">"Título de ejemplo 3"</div>
      </div>
      <button class="field-item__drag" draggable="true">⋮⋮</button>
    </div>
    
    <!-- Más campos... -->
  </div>
</div>
```

**Funcionalidad:**
- **Búsqueda** filtra en tiempo real
- **Ejemplos** muestran 3 valores reales del dataset
- **Drag handle** permite arrastrar a huecos
- **Iconos semánticos** por tipo:
  - 📝 String
  - 🔢 Number
  - 🖼️ Image URL
  - 📅 Date
  - 🔗 Link
  - 📋 Object/Array

---

### Component: MappingSlot (Paso 4)

```html
<div class="mapping-slot" data-role="title" data-required="true">
  <label class="slot-label">
    Título
    <span class="required-badge">Obligatorio</span>
  </label>
  
  <div class="slot-input" data-state="empty">
    <select class="slot-select">
      <option value="">Elegir campo...</option>
      <option value="title">title</option>
      <option value="name">name</option>
      <option value="headline">headline</option>
    </select>
    
    <button class="slot-suggest">
      ✨ Sugerir automáticamente
    </button>
  </div>
  
  <div class="slot-preview">
    <!-- Se muestra cuando hay mapping -->
    <div class="slot-preview__value">
      "Título de ejemplo del dato real"
    </div>
    <div class="slot-preview__path">
      Usando: <code>data.items[0].title</code>
    </div>
  </div>
  
  <div class="slot-validation">
    <!-- Mensajes de error/warning -->
  </div>
</div>
```

**Estados del slot:**
- `empty`: Sin mapear, fondo gris claro
- `mapped`: Mapeado, muestra preview del valor
- `error`: Campo obligatorio sin mapear, borde rojo
- `warning`: Posible problema (ej: tipo no ideal)

**Interacciones:**
1. **Drag & Drop** desde el explorador
2. **Select manual** del dropdown
3. **Auto-sugerencia** con explicación

---

### Component: PreviewPanel

```html
<div class="preview-panel">
  <div class="preview-tabs">
    <button class="preview-tab" data-tab="list" data-active="true">
      Listado
    </button>
    <button class="preview-tab" data-tab="detail">
      Ficha
    </button>
    <button class="preview-tab" data-tab="categories">
      Categorías
    </button>
  </div>
  
  <div class="preview-content" data-current-tab="list">
    <div class="preview-list">
      <!-- Cards de preview generadas dinámicamente -->
      <div class="preview-card">
        <img class="card-image" src="..." />
        <h3 class="card-title">{{ mapped_title }}</h3>
        <p class="card-description">{{ mapped_description }}</p>
        <a class="card-link">Ver más</a>
      </div>
      <!-- Más cards... -->
    </div>
  </div>
  
  <div class="preview-controls">
    <button class="preview-refresh">🔄 Actualizar preview</button>
    <button class="preview-test">🎲 Probar con otro elemento</button>
  </div>
</div>
```

**Actualización del preview:**
- **Automática:** Al cambiar cualquier mapping (debounce 300ms)
- **Manual:** Botón de refresh explícito
- **Test aleatorio:** Carga otro elemento del dataset para verificar

---

## 📊 FLUJO DE DATOS

### Modelo de Datos Actualizado

Necesitamos extender el modelo `APIRequest` para soportar el wizard completo:

```python
class APIRequest(models.Model):
    # Campos existentes
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    raw_data = models.TextField(blank=True, null=True)
    parsed_data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # NUEVOS CAMPOS PARA EL WIZARD
    
    # Paso 1: Metadata de la fuente
    source_metadata = models.JSONField(blank=True, null=True)
    # {
    #   "type": "JSON",
    #   "elements_count": 150,
    #   "frequent_fields": ["id", "title", "date"],
    #   "auth_required": false
    # }
    
    # Paso 2: Selección de contenido principal
    content_path = models.CharField(max_length=500, blank=True, null=True)
    # Ej: "data.results", "items", etc.
    
    # Paso 3: Tipo de plantilla elegida
    template_type = models.CharField(max_length=50, blank=True, null=True)
    # Opciones: "directory", "catalog", "blog", "landing"
    
    template_config = models.JSONField(blank=True, null=True)
    # {
    #   "pages": ["list", "detail", "categories"],
    #   "features": ["search", "filters", "pagination"]
    # }
    
    # Paso 4: Mapping por huecos
    field_mapping = models.JSONField(blank=True, null=True)
    # {
    #   "title": "data.items.title",
    #   "image": "data.items.thumbnail_url",
    #   "description": "data.items.summary",
    #   "link": "data.items.slug",
    #   "date": "data.items.published_at",
    #   "extra_fields": {
    #     "author": "data.items.author.name",
    #     "category": "data.items.category"
    #   }
    # }
    
    # Paso 5: Reglas de comportamiento
    behavior_rules = models.JSONField(blank=True, null=True)
    # {
    #   "url_generation": "use_slug",  # o "generate_from_title"
    #   "sort_by": "date",
    #   "sort_order": "desc",
    #   "fallback_image": "/static/images/placeholder.jpg",
    #   "hide_empty_sections": true,
    #   "auto_refresh_hours": 24
    # }
    
    # Paso 6: Estado de publicación
    publication_status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Borrador"),
            ("published", "Publicada"),
            ("archived", "Archivada"),
        ],
        default="draft"
    )
    
    # Proyecto Django generado (si existe)
    django_project_path = models.CharField(max_length=500, blank=True, null=True)
    deployment_url = models.URLField(blank=True, null=True)
    
    # Wizard progress tracking
    current_step = models.IntegerField(default=1)  # 1-6
    completed_steps = models.JSONField(default=list)  # [1, 2, 3]
    
    # Nombre del proyecto (editable por usuario)
    project_name = models.CharField(max_length=200, default="Mi Proyecto")
```

### Sesión de Usuario

Durante el wizard, mantener en sesión:

```python
request.session['wizard_state'] = {
    'api_request_id': 123,
    'current_step': 2,
    'temp_mapping': {...},  # Cambios no guardados
    'preview_element_index': 0,  # Qué elemento mostrar en preview
}
```

---

## 📝 DETALLE DE LOS 6 PASOS

### PASO 1: FUENTE DE DATOS

#### Objetivo
Conectar con la fuente de datos y validar que es compatible.

#### Diseño de Pantalla

**Columna Izquierda: Formulario**
```
┌─────────────────────────────────────┐
│ Conecta tu fuente de datos          │
│                                     │
│ URL de tu API:                      │
│ [https://api.example.com/items   ]  │
│                                     │
│ [Probar Conexión]                   │
│                                     │
│ ℹ️ Soportamos JSON y XML           │
│ ✓ No necesitas configurar nada     │
└─────────────────────────────────────┘
```

**Columna Derecha: Resultados** (aparece tras probar)
```
┌─────────────────────────────────────┐
│ ✓ Conexión exitosa                  │
│                                     │
│ 📊 Datos detectados:                │
│   • Formato: JSON                   │
│   • Elementos: 150 items            │
│   • Campos frecuentes:              │
│     - id, title, date, image_url    │
│                                     │
│ 📋 Ejemplo de un elemento:          │
│ {                                   │
│   "id": 1,                          │
│   "title": "Ejemplo...",            │
│   "date": "2026-01-15"              │
│ }                                   │
│                                     │
│ [Ver ejemplo completo ↗]            │
└─────────────────────────────────────┘
```

#### Validaciones y Diagnósticos

Si la conexión falla, mostrar diagnóstico humano:

| Error Técnico | Mensaje Usuario |
|--------------|-----------------|
| `ConnectionError` | "No pudimos conectar con esa URL. ¿Está bien escrita? ¿Requiere VPN?" |
| `401 Unauthorized` | "Esta API requiere autenticación. Por ahora no soportamos APIs privadas." |
| `Response is HTML` | "Esta URL devuelve una página web, no datos. Busca el endpoint de la API." |
| `Timeout` | "La API tarda mucho en responder. ¿Está caída? Intenta más tarde." |
| `Invalid JSON/XML` | "Los datos que devuelve no tienen un formato válido." |

#### Acciones del Footer

- **Atrás:** Volver a home (con confirmación si hay datos)
- **Guardar borrador:** Guardar URL introducida
- **Continuar:** Solo activo si conexión exitosa

---

### PASO 2: ELEGIR CONTENIDO PRINCIPAL

#### Objetivo
Identificar qué parte de los datos es "el contenido principal" (la lista de elementos a mostrar).

#### Diseño de Pantalla

**Columna Izquierda: Candidatos**
```
┌─────────────────────────────────────┐
│ ¿Cuál es tu contenido principal?    │
│                                     │
│ Detectamos estas listas:            │
│                                     │
│ ○ data.results                      │
│   📊 150 elementos                  │
│   Campos: id, title, image          │
│   [Ver 3 ejemplos ↓]                │
│                                     │
│ ◉ data.items                        │
│   📊 42 elementos                   │
│   Campos: id, name, description     │
│   [Ver 3 ejemplos ↓]                │
│                                     │
│ ○ featured_posts                    │
│   📊 5 elementos                    │
│   Campos: title, author             │
│   [Ver 3 ejemplos ↓]                │
└─────────────────────────────────────┘
```

**Columna Derecha: Preview del Candidato**
```
┌─────────────────────────────────────┐
│ Vista previa: data.items            │
│                                     │
│ Así se verían tus elementos:        │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [IMG] Elemento 1                │ │
│ │       Descripción breve...      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [IMG] Elemento 2                │ │
│ │       Descripción breve...      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [IMG] Elemento 3                │ │
│ │       Descripción breve...      │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### Lógica de Detección Automática

El sistema debe analizar la estructura y sugerir candidatos:

```python
def detect_content_candidates(parsed_data):
    """
    Busca arrays en la estructura que parezcan
    contenido principal (>3 elementos, con campos típicos)
    """
    candidates = []
    
    # Explorar recursivamente
    for path, value in explore_structure(parsed_data):
        if isinstance(value, list) and len(value) >= 3:
            # Analizar primer elemento
            sample = value[0]
            if has_typical_fields(sample):  # title, name, id, etc.
                candidates.append({
                    'path': path,
                    'count': len(value),
                    'fields': list(sample.keys()),
                    'samples': value[:3]
                })
    
    return sorted(candidates, key=lambda x: x['count'], reverse=True)
```

#### Interacción

- Click en un candidato → actualiza preview a la derecha
- Doble-click o botón "Elegir este" → avanza al paso 3
- Preview muestra hasta 3 tarjetas con datos reales

---

### PASO 3: ELEGIR TIPO DE WEB

#### Objetivo
Seleccionar la plantilla/estructura de la web a generar.

#### Diseño de Pantalla

**Cards de Tipos de Web**
```
┌──────────────────────────────────────────────────────────────┐
│ ¿Qué tipo de web quieres crear?                              │
│                                                              │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│ │ 📂          │  │ 🛍️          │  │ 📰          │          │
│ │ DIRECTORIO  │  │ CATÁLOGO    │  │ BLOG        │          │
│ │             │  │             │  │             │          │
│ │ • Listado   │  │ • Listado   │  │ • Listado   │          │
│ │ • Ficha     │  │ • Ficha     │  │ • Artículo  │          │
│ │ • Buscador  │  │ • Categorías│  │ • Autor     │          │
│ │             │  │ • Filtros   │  │ • Fecha     │          │
│ │ [Elegir]    │  │ [Elegir]    │  │ [Elegir]    │          │
│ └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│ ┌─────────────┐  ┌─────────────┐                           │
│ │ 🏠          │  │ ⚙️          │                           │
│ │ LANDING     │  │ AVANZADO    │                           │
│ │             │  │             │                           │
│ │ • Una página│  │ Configurar  │                           │
│ │ • Secciones │  │ desde cero  │                           │
│ │ • CTA       │  │             │                           │
│ │ [Elegir]    │  │ [Elegir]    │                           │
│ └─────────────┘  └─────────────┘                           │
└──────────────────────────────────────────────────────────────┘
```

**Panel de Configuración** (aparece tras elegir tipo)
```
┌─────────────────────────────────────┐
│ ✓ Has elegido: CATÁLOGO             │
│                                     │
│ Páginas incluidas:                  │
│ ☑ Listado principal                │
│ ☑ Ficha de producto                │
│ ☑ Categorías                        │
│ ☐ Buscador (opcional)               │
│ ☐ Comparador (opcional)             │
│                                     │
│ [Personalizar →]                    │
└─────────────────────────────────────┘
```

#### Recomendación Automática

El sistema puede sugerir según los campos detectados:

```python
def recommend_template(detected_fields):
    """
    Sugiere plantilla según campos comunes
    """
    if 'category' in detected_fields or 'price' in detected_fields:
        return 'catalog'  # Catálogo de productos
    
    if 'author' in detected_fields or 'published_at' in detected_fields:
        return 'blog'  # Blog/noticias
    
    if 'location' in detected_fields or 'address' in detected_fields:
        return 'directory'  # Directorio
    
    return 'directory'  # Default seguro
```

Mostrar recomendación como:
```
💡 Recomendación: Detectamos campos de productos (precio, categoría).
   ¿Quieres crear un CATÁLOGO?
```

---

### PASO 4: MAPPING POR HUECOS ⭐

**Este es el paso CRÍTICO del wizard.**

#### Objetivo
Conectar cada campo del dataset con cada "hueco" de la plantilla elegida.

#### Diseño de Pantalla (Layout Completo)

```
┌────────────────────────────────────────────────────────────────────┐
│ COLUMNA IZQUIERDA                │ COLUMNA DERECHA                  │
│ "Tus Datos"                      │ "Tu Web"                         │
├──────────────────────────────────┼──────────────────────────────────┤
│                                  │                                  │
│ 🔍 [Buscar campos...]            │ Tabs: [Listado] [Ficha] [Cats] │
│                                  │                                  │
│ Campos disponibles:              │ ┌──────────────────────────────┐ │
│                                  │ │  HUECOS DEL LISTADO         │ │
│ 📝 title (string)                │ │                              │ │
│    "Título ejemplo 1"            │ │  Imagen                      │ │
│    "Título ejemplo 2"            │ │  [Elegir campo... ▼]         │ │
│    "Título ejemplo 3"            │ │  ✨ Sugerir                  │ │
│    [⋮⋮]  ← drag handle           │ │                              │ │
│                                  │ │  Título *obligatorio         │ │
│ 🔢 id (number)                   │ │  [title ▼]                   │ │
│    1, 2, 3                       │ │  ✓ "Título ejemplo 1"        │ │
│    [⋮⋮]                          │ │  Usando: data.items.title    │ │
│                                  │ │                              │ │
│ 🖼️ image_url (string)            │ │  Resumen                     │ │
│    "http://..."                  │ │  [description ▼]             │ │
│    "http://..."                  │ │  ✓ "Descripción ejemplo..."  │ │
│    [⋮⋮]                          │ │                              │ │
│                                  │ │  Botón / Enlace              │ │
│ 📅 date (date)                   │ │  [slug ▼]                    │ │
│    2026-01-15                    │ │  ⚠️ Este campo parece un ID  │ │
│    2026-01-14                    │ │  ¿Seguro que es la URL?      │ │
│    [⋮⋮]                          │ │                              │ │
│                                  │ │  [Ver preview completo →]    │ │
│ 📋 author (object)               │ └──────────────────────────────┘ │
│    ↳ 📝 name                     │                                  │
│       "Juan Pérez"               │  Preview en vivo:                │
│       [⋮⋮]                       │  ┌────────────────────────────┐ │
│    ↳ 🔗 profile_url              │  │ [IMG] Título ejemplo 1     │ │
│       "/users/juan"              │  │       Descripción...       │ │
│       [⋮⋮]                       │  │       [Ver más →]          │ │
│                                  │  └────────────────────────────┘ │
│ [Mostrar solo campos no usados]  │  ┌────────────────────────────┐ │
│                                  │  │ [IMG] Título ejemplo 2     │ │
└──────────────────────────────────┴──────────────────────────────────┘
```

#### Huecos por Tipo de Página

**Listado:**
- Imagen (opcional)
- Título (obligatorio)
- Resumen (opcional)
- Botón/URL de ficha (obligatorio)

**Ficha:**
- Imagen (opcional)
- Título (obligatorio)
- Subtítulo (opcional)
- Contenido principal (opcional)
- Campos extra (accordion) (opcional)

**Categorías** (si aplica):
- Nombre de categoría
- Imagen de categoría
- Contador de elementos

#### Interacciones de Mapping

**1. Drag & Drop**
```javascript
// Usuario arrastra campo desde explorador
onDragStart(fieldPath) {
  dataTransfer.setData('field-path', fieldPath)
}

// Usuario suelta en hueco
onDrop(slotRole, fieldPath) {
  updateMapping(slotRole, fieldPath)
  updatePreview()  // Refresca preview con nuevo dato
}
```

**2. Selector Manual**
```html
<select class="slot-select" data-role="title">
  <option value="">Elegir campo...</option>
  <option value="title">title</option>
  <option value="name">name</option>
  <option value="headline">headline</option>
</select>
```

**3. Auto-sugerencia**
```javascript
function autoSuggestField(slotRole) {
  const suggestions = {
    title: ['title', 'name', 'headline', 'subject'],
    image: ['image', 'image_url', 'thumbnail', 'photo'],
    description: ['description', 'summary', 'excerpt', 'content'],
    date: ['date', 'published_at', 'created_at', 'timestamp'],
    link: ['slug', 'url', 'permalink', 'id']
  }
  
  const candidates = suggestions[slotRole]
  const found = findFirstMatch(availableFields, candidates)
  
  if (found) {
    showSuggestionDialog({
      message: `Elegí "${found}" porque parece un ${slotRole}`,
      field: found,
      onAccept: () => updateMapping(slotRole, found)
    })
  }
}
```

#### Validaciones en Tiempo Real

Al mapear un campo, validar:

**1. Tipo de dato**
```
image_url mapeado a "title" → ⚠️ Este campo parece texto, no una imagen. 
                                 ¿Quieres usarlo igual?
```

**2. Duplicados (si está prohibido)**
```
"title" ya usado en Título → ❌ No puedes usar el mismo campo en Título y 
                                 Subtítulo. Elige otro.
```

**3. Campos obligatorios**
```
Título sin mapear → ❌ El título es obligatorio para continuar.
```

**4. Transformaciones necesarias**
```
Campo "tags" es una lista → 💡 ¿Quieres unir los tags con comas?
                               [Sí, unir] [No, usar el primero]
```

#### Preview Actualizado en Vivo

Cada vez que se mapea un campo:
1. Se actualiza el preview con el valor real (debounce 300ms)
2. Se muestra la ruta del campo bajo el hueco
3. Se valida el tipo/compatibilidad

**Preview con datos parciales:**
```html
<div class="preview-card">
  <img src="{{ mapped_image or placeholder }}" />
  <h3>{{ mapped_title or "Sin título" }}</h3>
  <p>{{ mapped_description or "Sin descripción" }}</p>
  <a href="#">{{ mapped_link or "#" }}</a>
</div>
```

**Estados visuales:**
- Título mapeado: texto negro, normal
- Título sin mapear: texto gris, placeholder
- Campo con error: borde rojo

---

### PASO 5: REGLAS DE COMPORTAMIENTO

#### Objetivo
Configurar comportamientos especiales sin tecnicismos.

#### Diseño de Pantalla

**Cards de Configuración**
```
┌──────────────────────────────────────────────────────────────┐
│ Personaliza el comportamiento de tu web                      │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔗 URLs de las fichas                                   │ │
│ │                                                         │ │
│ │ ○ Usar campo existente: [slug ▼]                       │ │
│ │                                                         │ │
│ │ ◉ Generar desde título                                 │ │
│ │   Ejemplo: /items/titulo-de-ejemplo/                   │ │
│ │            /items/otro-ejemplo/                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📊 Orden del listado                                    │ │
│ │                                                         │ │
│ │ Ordenar por: [date ▼]                                  │ │
│ │ Dirección: ◉ Más reciente primero ○ Más antiguo       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🖼️ Fallbacks                                            │ │
│ │                                                         │ │
│ │ Imagen por defecto cuando falta:                       │ │
│ │ [📁 Subir imagen] o usar placeholder genérico          │ │
│ │                                                         │ │
│ │ ☑ Ocultar secciones vacías                            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔄 Actualizaciones                                      │ │
│ │                                                         │ │
│ │ ○ Manual (yo actualizo cuando quiera)                  │ │
│ │ ◉ Automático cada: [24 ▼] horas                       │ │
│ │                                                         │ │
│ │ ℹ️ La web se reconectará a la API para traer datos    │ │
│ │    actualizados.                                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [⚙️ Modo avanzado (opcional)] ←────────────────────────────│ │
└──────────────────────────────────────────────────────────────┘
```

#### Modo Avanzado (Colapsado por Defecto)

Si el usuario es más técnico o quiere control fino:

```
┌─────────────────────────────────────┐
│ ⚙️ Configuración avanzada            │
│                                     │
│ Transformaciones:                   │
│ • Formatear fechas:                 │
│   [date ▼] → formato: [d/m/Y ▼]    │
│                                     │
│ • Unir listas:                      │
│   [tags ▼] → separador: [, ]       │
│                                     │
│ • Extraer de objetos anidados:      │
│   [author.name ▼]                   │
└─────────────────────────────────────┘
```

#### Validaciones

- URL generation: Si elige "usar campo", verificar que existe
- Sort by: Solo permitir campos numéricos/fecha
- Auto-refresh: Advertir si la API es lenta/tiene rate limits

---

### PASO 6: PREVIEW & PUBLICAR

#### Objetivo
Revisar la web completa antes de generar y opcionalmente publicar.

#### Diseño de Pantalla

**Checklist de Calidad** (Izquierda)
```
┌─────────────────────────────────────┐
│ Checklist de calidad                │
│                                     │
│ ✓ Conexión a la API OK              │
│ ✓ 150 elementos detectados          │
│ ✓ Título mapeado                    │
│ ⚠️ 15% sin imagen (se usará default)│
│ ✓ URLs correctamente generadas      │
│ ✓ 3 páginas configuradas            │
│                                     │
│ Todo listo para generar 🎉          │
└─────────────────────────────────────┘
```

**Preview Navegable** (Derecha)
```
┌─────────────────────────────────────┐
│ Vista previa final                  │
│                                     │
│ Tabs: [Listado] [Ficha] [Categorías]│
│                                     │
│ [Ver preview completo en nueva      │
│  ventana ↗]                         │
│                                     │
│ [🎲 Probar con otro elemento]       │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [Simulación de la web]          │ │
│ │                                 │ │
│ │ [IMG] Elemento 1                │ │
│ │ [IMG] Elemento 2                │ │
│ │ ...                             │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Acciones Principales**
```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│        [← Volver a editar mapping]                       │
│                                                          │
│        [✨ GENERAR MI WEB]  ← CTA principal              │
│                                                          │
│        [💾 Guardar borrador]                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### Post-Generación: Pantalla de Éxito

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                 🎉 ¡Tu web está lista!                   │
│                                                          │
│  Tu proyecto "Mi Catálogo de Productos" ha sido         │
│  generado exitosamente.                                 │
│                                                          │
│  Accesos rápidos:                                        │
│                                                          │
│  [👁️ Ver mi web]  [⚙️ Panel admin]  [💻 Ver código]     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Próximos pasos:                                    │ │
│  │                                                    │ │
│  │ 1. Personaliza el diseño visual                   │ │
│  │ 2. Configura un dominio propio                    │ │
│  │ 3. Añade analytics                                │ │
│  │                                                    │ │
│  │ [Ir a configuración avanzada →]                   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [← Volver al dashboard]  [🔄 Crear otra web]           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 SISTEMA DE PREVIEW INTEGRADO

### Principios del Preview

1. **Siempre accesible:** Panel visible desde el paso 2 en adelante
2. **Datos reales:** Usa elementos del dataset, no placeholders
3. **Actualización inmediata:** Refleja cambios de mapping sin recargar página
4. **Estados claros:** Muestra qué falta y qué está bien

### Arquitectura del Preview

#### Backend: Endpoint de Preview

```python
# views/preview.py

@login_required
def preview_cards(request):
    """
    Genera preview cards con el mapping actual
    
    GET params:
    - api_request_id: ID del análisis
    - element_index: Qué elemento mostrar (default: 0)
    - page_type: "list" | "detail" | "categories"
    """
    api_request_id = request.GET.get('api_request_id')
    element_index = int(request.GET.get('element_index', 0))
    page_type = request.GET.get('page_type', 'list')
    
    # Cargar análisis y mapping
    api_request = get_object_or_404(APIRequest, id=api_request_id, user=request.user)
    mapping = api_request.field_mapping or get_mapping(request)
    
    # Extraer elementos del dataset
    content_path = api_request.content_path
    elements = extract_elements(api_request.parsed_data, content_path)
    
    if not elements:
        return JsonResponse({'error': 'No hay elementos'}, status=400)
    
    # Elemento a mostrar
    element = elements[element_index % len(elements)]
    
    # Resolver valores según mapping
    preview_data = resolve_mapping_values(element, mapping)
    
    # Renderizar template según tipo
    if page_type == 'list':
        template = 'WebBuilder/preview_cards_snippet.html'
        context = {
            'elements': [preview_data],  # Para consistencia
            'mapping': mapping
        }
    elif page_type == 'detail':
        template = 'WebBuilder/preview_detail_snippet.html'
        context = {
            'element': preview_data,
            'mapping': mapping
        }
    
    return render(request, template, context)


def resolve_mapping_values(element, mapping):
    """
    Aplica el mapping a un elemento y devuelve valores resueltos
    
    Args:
        element: Dict con datos del elemento
        mapping: Dict con el mapping (role → path)
    
    Returns:
        Dict con valores resueltos
    """
    resolved = {}
    
    for role, path in mapping.items():
        try:
            value = extract_value_by_path(element, path)
            resolved[role] = value
        except KeyError:
            resolved[role] = None  # Fallback
    
    return resolved
```

#### Frontend: Actualización del Preview

```javascript
// assistant.js

class PreviewManager {
  constructor() {
    this.apiRequestId = null
    this.currentTab = 'list'
    this.currentElementIndex = 0
    this.debounceTimer = null
  }
  
  // Actualizar preview cuando cambia mapping
  updatePreview(mapping) {
    // Debounce para no saturar el servidor
    clearTimeout(this.debounceTimer)
    
    this.debounceTimer = setTimeout(() => {
      this.fetchPreview(mapping)
    }, 300)
  }
  
  // Llamar al endpoint de preview
  async fetchPreview(mapping) {
    const params = new URLSearchParams({
      api_request_id: this.apiRequestId,
      element_index: this.currentElementIndex,
      page_type: this.currentTab
    })
    
    // También enviar mapping actual vía POST
    const response = await fetch(`/preview/cards/?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ mapping })
    })
    
    const html = await response.text()
    
    // Actualizar DOM
    document.querySelector('.preview-content').innerHTML = html
  }
  
  // Cambiar de elemento (botón "Probar con otro")
  testRandomElement() {
    const maxElements = parseInt(this.dataset.totalElements) || 10
    this.currentElementIndex = Math.floor(Math.random() * maxElements)
    this.updatePreview(getCurrentMapping())
  }
  
  // Cambiar de tab (List | Detail | Categories)
  switchTab(tab) {
    this.currentTab = tab
    this.updatePreview(getCurrentMapping())
  }
}

// Instanciar
const previewManager = new PreviewManager()

// Escuchar cambios de mapping
document.addEventListener('mapping:changed', (e) => {
  previewManager.updatePreview(e.detail.mapping)
})

// Botón "Probar con otro"
document.querySelector('.preview-test').addEventListener('click', () => {
  previewManager.testRandomElement()
})
```

### Templates de Preview

#### List Preview
```html
<!-- preview_cards_snippet.html -->
<div class="preview-list">
  {% for element in elements %}
    <div class="preview-card">
      {% if element.image %}
        <img class="card-image" src="{{ element.image }}" alt="" />
      {% else %}
        <div class="card-image-placeholder">Sin imagen</div>
      {% endif %}
      
      <h3 class="card-title">
        {{ element.title|default:"Sin título" }}
      </h3>
      
      <p class="card-description">
        {{ element.description|default:"Sin descripción"|truncatewords:20 }}
      </p>
      
      <a class="card-link" href="#">
        Ver más →
      </a>
    </div>
  {% endfor %}
</div>
```

#### Detail Preview
```html
<!-- preview_detail_snippet.html -->
<div class="preview-detail">
  {% if element.image %}
    <img class="detail-image" src="{{ element.image }}" alt="" />
  {% endif %}
  
  <h1 class="detail-title">{{ element.title|default:"Sin título" }}</h1>
  
  {% if element.subtitle %}
    <h2 class="detail-subtitle">{{ element.subtitle }}</h2>
  {% endif %}
  
  <div class="detail-meta">
    {% if element.author %}
      <span>Por {{ element.author }}</span>
    {% endif %}
    
    {% if element.date %}
      <span>{{ element.date|date:"d/m/Y" }}</span>
    {% endif %}
  </div>
  
  <div class="detail-content">
    {{ element.content|default:"Sin contenido"|safe }}
  </div>
  
  {% if element.extra_fields %}
    <div class="detail-accordion">
      <h3>Información adicional</h3>
      {% for key, value in element.extra_fields.items %}
        <div class="accordion-item">
          <strong>{{ key }}:</strong> {{ value }}
        </div>
      {% endfor %}
    </div>
  {% endif %}
</div>
```

---

## 💬 MICROCOPY Y MENSAJES

### Principio: Hablar Como Humano

**Evitar:**
- "El serializer no pudo parsear el JSON"
- "Field mapping incompleto"
- "Validación de schema fallida"

**Usar:**
- "No pudimos entender los datos que devuelve esa URL"
- "Falta elegir el título para continuar"
- "Los datos no tienen el formato esperado"

### Mensajes por Contexto

#### Paso 1: Errores de Conexión

| Situación | Mensaje |
|-----------|---------|
| URL mal formada | "Verifica que la URL esté completa (debe empezar con http:// o https://)" |
| 404 Not Found | "Esa URL no existe. ¿La copiaste bien?" |
| 500 Server Error | "La API tuvo un problema. Intenta de nuevo en unos minutos." |
| Timeout | "La conexión tardó demasiado. ¿La API está disponible?" |
| Auth requerida | "Esta API requiere autenticación. Por ahora no soportamos APIs privadas." |
| Devuelve HTML | "Esta URL devuelve una página web, no datos. Busca el endpoint `/api/` de tu servicio." |

#### Paso 2: Detección de Contenido

| Situación | Mensaje |
|-----------|---------|
| No se detectan listas | "No encontramos listas de elementos en los datos. ¿Seguro que esta URL devuelve una colección?" |
| Lista vacía | "Esta lista no tiene elementos. ¿Está vacía o requiere parámetros?" |
| Estructura compleja | "Detectamos varias listas. ¿Cuál es tu contenido principal?" |

#### Paso 4: Validaciones de Mapping

| Situación | Mensaje |
|-----------|---------|
| Título sin mapear | "❌ El título es obligatorio. Elige un campo para continuar." |
| Campo duplicado | "⚠️ Ya usaste 'title' en otro hueco. ¿Seguro que quieres repetirlo?" |
| Tipo incompatible | "⚠️ Este campo parece un número, no una imagen. ¿Quieres usarlo igual?" |
| Lista en campo simple | "💡 Este campo contiene varios valores. ¿Quieres usar el primero o unirlos?" |
| Fecha sin formato | "💡 Detectamos una fecha. ¿Quieres formatearla? (ej: 15/01/2026)" |

#### Paso 5: Configuración

| Situación | Mensaje |
|-----------|---------|
| Auto-refresh muy frecuente | "⚠️ Actualizar cada hora puede sobrecargar la API. ¿Seguro?" |
| Sin imagen default | "ℹ️ Si eliges no subir imagen por defecto, se usará un placeholder genérico." |

#### Paso 6: Generación

| Situación | Mensaje |
|-----------|---------|
| Generación exitosa | "🎉 ¡Tu web está lista! Ya puedes verla y compartirla." |
| Error al generar | "😕 Hubo un problema al generar la web. Revisa que todos los datos estén bien." |
| Warning de calidad | "⚠️ 25% de tus elementos no tienen imagen. Considera subir una por defecto." |

---

## ✨ AUTOCOMPLETADO Y SUGERENCIAS

### Sistema de Sugerencias Inteligentes

#### Lógica de Matching

```python
# utils/suggestions.py

# Diccionario de campos típicos por rol
ROLE_PATTERNS = {
    'title': {
        'exact': ['title', 'name', 'headline', 'subject'],
        'contains': ['titulo', 'nombre', 'titulo', 'encabezado'],
        'type': 'string'
    },
    'image': {
        'exact': ['image', 'image_url', 'thumbnail', 'photo', 'picture'],
        'contains': ['img', 'imagen', 'foto', 'thumb'],
        'type': 'string',
        'pattern': r'https?://.*\.(jpg|png|gif|webp)'
    },
    'description': {
        'exact': ['description', 'summary', 'excerpt', 'body', 'content'],
        'contains': ['desc', 'resumen', 'extracto', 'contenido'],
        'type': 'string'
    },
    'date': {
        'exact': ['date', 'published_at', 'created_at', 'updated_at', 'timestamp'],
        'contains': ['fecha', 'publicado', 'creado'],
        'type': 'date'
    },
    'link': {
        'exact': ['slug', 'url', 'permalink', 'link', 'href'],
        'contains': ['enlace', 'vinculo'],
        'type': 'string'
    },
    'author': {
        'exact': ['author', 'creator', 'by', 'writer'],
        'contains': ['autor', 'creador', 'escritor'],
        'type': 'string'
    },
    'category': {
        'exact': ['category', 'tag', 'type', 'section'],
        'contains': ['categoria', 'etiqueta', 'seccion'],
        'type': 'string'
    }
}

def suggest_mapping(available_fields, role):
    """
    Sugiere el mejor campo para un rol dado
    
    Args:
        available_fields: Lista de campos disponibles con metadata
            [{'path': 'title', 'type': 'string', 'samples': [...]}, ...]
        role: Rol del hueco ('title', 'image', etc.)
    
    Returns:
        {
            'field': 'title',
            'confidence': 0.95,
            'reason': 'Es un campo llamado "title" de tipo texto'
        }
    """
    patterns = ROLE_PATTERNS.get(role, {})
    
    # 1. Buscar match exacto
    for field in available_fields:
        if field['path'].lower() in patterns.get('exact', []):
            return {
                'field': field['path'],
                'confidence': 0.95,
                'reason': f'Es un campo llamado "{field["path"]}" de tipo {field["type"]}'
            }
    
    # 2. Buscar por contenido del nombre
    for field in available_fields:
        for pattern_word in patterns.get('contains', []):
            if pattern_word in field['path'].lower():
                return {
                    'field': field['path'],
                    'confidence': 0.75,
                    'reason': f'El nombre "{field["path"]}" contiene "{pattern_word}"'
                }
    
    # 3. Buscar por tipo y patrón de datos
    if 'pattern' in patterns:
        import re
        for field in available_fields:
            if field['type'] == 'string':
                # Revisar samples
                for sample in field.get('samples', [])[:3]:
                    if re.match(patterns['pattern'], str(sample)):
                        return {
                            'field': field['path'],
                            'confidence': 0.60,
                            'reason': f'Los valores parecen {role}s (ej: {sample[:50]}...)'
                        }
    
    return None  # No hay sugerencia


def auto_suggest_all_mappings(available_fields):
    """
    Genera sugerencias para todos los roles
    
    Returns:
        {
            'title': {'field': 'title', 'confidence': 0.95, 'reason': '...'},
            'image': {'field': 'image_url', 'confidence': 0.95, 'reason': '...'},
            ...
        }
    """
    suggestions = {}
    
    for role in ROLE_PATTERNS.keys():
        suggestion = suggest_mapping(available_fields, role)
        if suggestion and suggestion['confidence'] > 0.5:
            suggestions[role] = suggestion
    
    return suggestions
```

#### UI de Sugerencias

**Botón de auto-sugerencia por hueco:**
```html
<div class="mapping-slot" data-role="title">
  <label>Título <span class="required">*</span></label>
  
  <select class="slot-select">
    <option value="">Elegir campo...</option>
    <!-- opciones -->
  </select>
  
  <button class="slot-suggest" data-role="title">
    ✨ Sugerir automáticamente
  </button>
</div>

<script>
document.querySelector('.slot-suggest').addEventListener('click', async (e) => {
  const role = e.target.dataset.role
  
  const response = await fetch('/api/suggest-mapping/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      api_request_id: currentApiRequestId,
      role: role
    })
  })
  
  const suggestion = await response.json()
  
  if (suggestion.field) {
    showSuggestionDialog({
      title: `Sugerencia para ${role}`,
      message: `Elegí "${suggestion.field}" porque ${suggestion.reason}`,
      confidence: suggestion.confidence,
      onAccept: () => {
        // Aplicar sugerencia
        document.querySelector(`select[data-role="${role}"]`).value = suggestion.field
        updateMapping(role, suggestion.field)
      },
      onReject: () => {
        // Usuario elige otro
      }
    })
  } else {
    showMessage('No encontré una sugerencia clara. Elige manualmente.', 'info')
  }
})
</script>
```

**Modal de sugerencia:**
```html
<div class="suggestion-dialog">
  <div class="dialog-icon">✨</div>
  <h3>Sugerencia para Título</h3>
  
  <p class="suggestion-reason">
    Elegí <strong>"title"</strong> porque es un campo llamado "title" de tipo texto.
  </p>
  
  <div class="suggestion-confidence">
    Confianza: 
    <div class="confidence-bar">
      <div class="confidence-fill" style="width: 95%"></div>
    </div>
    95%
  </div>
  
  <div class="dialog-actions">
    <button class="btn-secondary">No, elegir otro</button>
    <button class="btn-primary">Sí, usar "title"</button>
  </div>
</div>
```

#### Sugerencia Global (Aplicar Todo)

Opción para que el sistema mapee todo automáticamente:

```html
<div class="auto-suggest-banner">
  <div class="banner-icon">🎯</div>
  <div class="banner-content">
    <h4>¿Quieres que mapeemos todo automáticamente?</h4>
    <p>Detectamos campos típicos y podemos configurar el mapping por ti.</p>
  </div>
  <button class="btn-primary" id="autoSuggestAll">
    Mapear automáticamente
  </button>
</div>

<script>
document.getElementById('autoSuggestAll').addEventListener('click', async () => {
  const response = await fetch('/api/auto-suggest-all/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      api_request_id: currentApiRequestId
    })
  })
  
  const suggestions = await response.json()
  
  // Mostrar modal con preview de sugerencias
  showAutoSuggestPreview(suggestions)
})

function showAutoSuggestPreview(suggestions) {
  const modal = `
    <div class="auto-suggest-preview">
      <h3>Sugerencias automáticas</h3>
      <p>Revisa y ajusta antes de aplicar:</p>
      
      <table class="suggestions-table">
        <thead>
          <tr>
            <th>Hueco</th>
            <th>Campo sugerido</th>
            <th>¿Por qué?</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${Object.entries(suggestions).map(([role, suggestion]) => `
            <tr>
              <td><strong>${role}</strong></td>
              <td><code>${suggestion.field}</code></td>
              <td>${suggestion.reason}</td>
              <td>
                <select data-role="${role}">
                  <option value="${suggestion.field}" selected>${suggestion.field}</option>
                  <!-- otras opciones -->
                </select>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      
      <div class="modal-actions">
        <button class="btn-secondary">Cancelar</button>
        <button class="btn-primary" id="applyAllSuggestions">
          Aplicar sugerencias
        </button>
      </div>
    </div>
  `
  
  showModal(modal)
  
  document.getElementById('applyAllSuggestions').addEventListener('click', () => {
    // Leer valores de los selects y aplicar
    const finalMapping = {}
    document.querySelectorAll('.suggestions-table select').forEach(select => {
      finalMapping[select.dataset.role] = select.value
    })
    
    applyMapping(finalMapping)
    closeModal()
    showMessage('✓ Mapping aplicado automáticamente', 'success')
  })
}
</script>
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Fase 1: Estructura Base del Wizard (Sprint 1-2)

**Objetivos:**
- Implementar layout de 6 pasos
- Navegación lateral con estados
- Header con progreso
- Footer con acciones

**Entregables:**
1. Componente `WizardLayout`
2. Navegación funcional entre pasos
3. Persistencia de estado en sesión
4. CSS responsive

**Archivos a crear/modificar:**
```
WebBuilder/
├── templates/WebBuilder/
│   ├── wizard/
│   │   ├── base.html (nuevo)
│   │   ├── step1_source.html (nuevo)
│   │   ├── step2_content.html (nuevo)
│   │   ├── step3_template.html (nuevo)
│   │   ├── step4_mapping.html (nuevo)
│   │   ├── step5_rules.html (nuevo)
│   │   └── step6_publish.html (nuevo)
│   └── components/
│       ├── wizard_header.html (nuevo)
│       ├── wizard_nav.html (nuevo)
│       └── wizard_footer.html (nuevo)
├── static/
│   ├── css/
│   │   └── wizard.css (nuevo)
│   └── js/
│       └── wizard.js (nuevo)
└── views/
    └── wizard.py (nuevo)
```

---

### Fase 2: Pasos 1-3 (Sprint 3-4)

**Objetivos:**
- Paso 1: Validación de fuente mejorada
- Paso 2: Detección de contenido con preview
- Paso 3: Selector de plantillas

**Entregables:**
1. Detección automática de candidatos de contenido
2. Cards de tipos de plantilla
3. Recomendación automática de tipo
4. Preview básico de listado

**Archivos clave:**
```python
# utils/detection.py (nuevo)
def detect_content_candidates(parsed_data)
def detect_data_type(field_value)
def recommend_template_type(fields)

# models.py (extender)
class APIRequest:
    source_metadata = models.JSONField(...)
    content_path = models.CharField(...)
    template_type = models.CharField(...)
    template_config = models.JSONField(...)
```

---

### Fase 3: Paso 4 - Mapping Visual (Sprint 5-7) ⭐

**Este es el corazón del proyecto.**

**Objetivos:**
- Field explorer con búsqueda
- Mapping slots con drag & drop
- Sistema de sugerencias
- Preview en tiempo real

**Entregables:**
1. Componente `FieldExplorer`
2. Componente `MappingSlot`
3. Sistema de drag & drop
4. Auto-sugerencias con explicación
5. Validaciones en tiempo real
6. Actualización de preview (debounced)

**Archivos clave:**
```python
# utils/suggestions.py (nuevo)
ROLE_PATTERNS = {...}
def suggest_mapping(available_fields, role)
def auto_suggest_all_mappings(available_fields)

# views/wizard.py
def suggest_field(request)  # Endpoint AJAX
def apply_auto_suggestions(request)  # Endpoint AJAX
```

```javascript
// static/js/mapping.js (nuevo)
class FieldExplorer {
  search(query)
  renderFields(fields)
}

class MappingSlot {
  onDrop(fieldPath)
  onSelect(fieldPath)
  validate()
  updatePreview()
}

class DragDropManager {
  initDraggable(element)
  handleDrop(event)
}
```

---

### Fase 4: Preview Integrado (Sprint 8-9)

**Objetivos:**
- Preview panel con tabs
- Actualización AJAX sin recargar
- Soporte para estados parciales
- Botón "Probar con otro elemento"

**Entregables:**
1. Endpoint `/preview/cards/`
2. Templates de preview (list, detail, categories)
3. `PreviewManager` JS
4. Soporte para mapping incompleto

**Archivos clave:**
```python
# views/preview.py (extender)
def preview_cards(request)
def resolve_mapping_values(element, mapping)

# templates/WebBuilder/
#   preview_list_snippet.html
#   preview_detail_snippet.html
#   preview_categories_snippet.html
```

```javascript
// static/js/preview.js (nuevo)
class PreviewManager {
  updatePreview(mapping)
  fetchPreview(mapping)
  testRandomElement()
  switchTab(tab)
}
```

---

### Fase 5: Pasos 5-6 (Sprint 10-11)

**Objetivos:**
- Configuración de reglas sin tecnicismos
- Checklist de calidad
- Generación final
- Pantalla de éxito

**Entregables:**
1. Configuración de URLs, orden, fallbacks
2. Validación pre-generación
3. Generación de proyecto Django
4. Post-generación con accesos

**Archivos clave:**
```python
# utils/generator.py (nuevo o extender)
def generate_django_project(api_request)
def validate_pre_generation(api_request)
def calculate_quality_score(api_request)

# models.py
class APIRequest:
    behavior_rules = models.JSONField(...)
    publication_status = models.CharField(...)
    django_project_path = models.CharField(...)
```

---

### Fase 6: Pulido y Testing (Sprint 12)

**Objetivos:**
- Microcopy final
- Animaciones y transiciones
- Testing de flujos completos
- Documentación

**Entregables:**
1. Guía de microcopy aplicada
2. Animaciones CSS pulidas
3. Tests end-to-end
4. Video tutorial del wizard

---

## 📚 ANEXOS TÉCNICOS

### A. Estructura de Datos Completa

#### APIRequest Model (Extendido)
```python
class APIRequest(models.Model):
    # Core
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=200, default="Mi Proyecto")
    api_url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    
    # Paso 1
    raw_data = models.TextField(blank=True, null=True)
    parsed_data = models.JSONField(blank=True, null=True)
    source_metadata = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Paso 2
    content_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Paso 3
    template_type = models.CharField(max_length=50, blank=True, null=True)
    template_config = models.JSONField(blank=True, null=True)
    
    # Paso 4
    field_mapping = models.JSONField(blank=True, null=True)
    
    # Paso 5
    behavior_rules = models.JSONField(blank=True, null=True)
    
    # Paso 6
    publication_status = models.CharField(max_length=20, default="draft")
    django_project_path = models.CharField(max_length=500, blank=True, null=True)
    deployment_url = models.URLField(blank=True, null=True)
    
    # Wizard state
    current_step = models.IntegerField(default=1)
    completed_steps = models.JSONField(default=list)
```

#### Ejemplo de source_metadata
```json
{
  "type": "JSON",
  "status_code": 200,
  "response_time_ms": 234,
  "elements_count": 150,
  "frequent_fields": ["id", "title", "date", "image_url"],
  "auth_required": false,
  "nested_level": 2
}
```

#### Ejemplo de template_config
```json
{
  "type": "catalog",
  "pages": ["list", "detail", "categories"],
  "features": {
    "search": true,
    "filters": true,
    "pagination": true,
    "sorting": true
  }
}
```

#### Ejemplo de field_mapping
```json
{
  "title": "data.items[].title",
  "image": "data.items[].thumbnail_url",
  "description": "data.items[].summary",
  "link": "data.items[].slug",
  "date": "data.items[].published_at",
  "author": "data.items[].author.name",
  "category": "data.items[].category",
  "extra_fields": {
    "price": "data.items[].price",
    "stock": "data.items[].stock"
  }
}
```

#### Ejemplo de behavior_rules
```json
{
  "url_generation": "use_slug",
  "sort_by": "date",
  "sort_order": "desc",
  "fallback_image": "/static/images/placeholder.jpg",
  "hide_empty_sections": true,
  "auto_refresh_hours": 24,
  "transformations": {
    "date": {
      "format": "d/m/Y"
    },
    "tags": {
      "join_separator": ", "
    }
  }
}
```

---

### B. Endpoints API del Wizard

```python
# urls.py
urlpatterns = [
    # Wizard main
    path('wizard/', views.wizard_home, name='wizard_home'),
    path('wizard/step/<int:step>/', views.wizard_step, name='wizard_step'),
    
    # Step-specific actions
    path('wizard/analyze-source/', views.analyze_source, name='wizard_analyze_source'),
    path('wizard/select-content/', views.select_content, name='wizard_select_content'),
    path('wizard/select-template/', views.select_template, name='wizard_select_template'),
    path('wizard/save-mapping/', views.save_mapping, name='wizard_save_mapping'),
    path('wizard/save-rules/', views.save_rules, name='wizard_save_rules'),
    path('wizard/generate/', views.generate_project, name='wizard_generate'),
    
    # AJAX helpers
    path('api/suggest-field/', views.api_suggest_field, name='api_suggest_field'),
    path('api/auto-suggest-all/', views.api_auto_suggest_all, name='api_auto_suggest_all'),
    path('api/validate-mapping/', views.api_validate_mapping, name='api_validate_mapping'),
    path('api/preview/', views.api_preview, name='api_preview'),
]
```

---

### C. Checklist de Calidad UX

Antes de dar por terminado el wizard, verificar:

**✓ Lenguaje:**
- [ ] Cero términos técnicos de Django
- [ ] Mensajes de error en lenguaje humano
- [ ] Tooltips explicativos donde hace falta

**✓ Navegación:**
- [ ] Barra de progreso funcional
- [ ] Puedo volver atrás sin perder datos
- [ ] Steps bloqueados visualmente claros
- [ ] Shortcuts desde navegación lateral

**✓ Preview:**
- [ ] Se actualiza en < 500ms tras cambio
- [ ] Muestra datos reales, no placeholders
- [ ] Funciona con mapping incompleto
- [ ] Botón "Probar otro elemento" funciona

**✓ Mapping:**
- [ ] Drag & drop fluido
- [ ] Sugerencias automáticas útiles
- [ ] Validaciones claras e inmediatas
- [ ] Transformaciones explicadas

**✓ Responsive:**
- [ ] Mobile: tabs en lugar de columnas
- [ ] Tablet: layout adaptado
- [ ] Desktop: dos columnas funcionales

**✓ Accesibilidad:**
- [ ] Navegación por teclado
- [ ] Labels ARIA apropiados
- [ ] Contraste de colores OK
- [ ] Focus visible

---

### D. Glossario de Términos

**Para el usuario (lenguaje permitido):**
- Elemento
- Contenido
- Listado
- Ficha
- Campos
- Fuente de datos
- Tu web
- Plantilla/diseño
- Reglas
- Conectar
- Mapear (o mejor: "completar huecos")

**Prohibido (jerga técnica):**
- Model
- View
- Serializer
- Template (técnico)
- Field (usar "campo" está OK)
- Queryset
- Migration
- URL pattern
- Slug (explicar como "nombre en la URL")

---

## 🎬 CONCLUSIÓN

Este documento define la arquitectura UX completa para transformar WebBuilder en un sistema verdaderamente intuitivo. Los principios clave son:

1. **Guía conversacional**: El wizard pregunta y explica, no exige conocimientos técnicos
2. **Feedback inmediato**: El preview muestra la web construyéndose en tiempo real
3. **Sugerencias inteligentes**: El sistema ayuda activamente a completar el mapping
4. **Lenguaje humano**: Cero jerga, mensajes claros y empáticos

Con este rediseño, un usuario sin conocimientos de Django puede:
- Conectar una API en 1 minuto
- Mapear campos visualmente en 5 minutos
- Ver su web funcionando en 10 minutos
- Publicarla en 15 minutos

**El objetivo final: "Mis datos → Mi web" sin fricción técnica.**
