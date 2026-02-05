# 📋 Instrucciones de Integración - Navbar WebBuilder

## 📁 Archivos Creados

1. **navbar_new.html** - Template de la navbar con desplegables
2. **navbar_new.css** - Estilos completos para la navbar
3. **INSTRUCCIONES.md** - Este archivo

---

## 🔧 Cómo Integrar la Navbar

### 1. Reemplazar archivos existentes

**Opción A - Reemplazo directo:**
```bash
# Reemplazar navbar HTML
cp navbar_new.html WebBuilder/project/WebBuilder/templates/WebBuilder/navbarOriginal.html

# Reemplazar navbar CSS
cp navbar_new.css WebBuilder/project/WebBuilder/static/css/navbarOriginal.css
```

**Opción B - Crear nuevos archivos (recomendado para testing):**
```bash
# Copiar como archivos nuevos
cp navbar_new.html WebBuilder/project/WebBuilder/templates/WebBuilder/navbar_modern.html
cp navbar_new.css WebBuilder/project/WebBuilder/static/css/navbar_modern.css
```

---

### 2. Actualizar base.html

Si estás usando un include para la navbar, asegúrate de que en `base.html` tengas:

```django
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}WebBuilder{% endblock %}</title>
    
    <!-- CSS de la navbar -->
    <link rel="stylesheet" href="{% static 'css/navbarOriginal.css' %}">
    
    <!-- Otros CSS -->
    <link rel="stylesheet" href="{% static 'css/fondos.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    
    <!-- Incluir navbar -->
    {% include 'WebBuilder/navbarOriginal.html' %}
    
    <!-- Contenido -->
    {% block content %}{% endblock %}
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

### 3. Configurar URLs necesarias

Asegúrate de que estas URLs estén definidas en tu `urls.py`:

```python
# WebBuilder/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('assistant/', views.assistant, name='assistant'),
    path('history/', views.history, name='history'),
    path('preview/<int:api_request_id>/', views.preview, name='preview'),
    path('login/', ..., name='login'),
    path('logout/', ..., name='logout'),
    path('register/', views.register, name='register'),
]
```

---

### 4. Ajustar el CSS global (opcional)

Si tu `fondos.css` o CSS global tiene un `padding-top` en el body, **elimínalo** porque la navbar nueva ya lo aplica automáticamente:

```css
/* ❌ ELIMINAR o comentar esto en fondos.css */
body {
    padding-top: 80px; /* <-- Quitar esto */
}

/* ✅ La navbar_new.css ya incluye esto */
```

---

## 🎨 Características de la Nueva Navbar

### ✅ Diseño
- **Fondo negro** (#0a0a0a) que se integra con el fondo del asistente
- **Texto blanco** con opacidad para jerarquía visual
- **Acentos azules** (#4a9eff) para botones y elementos activos
- **Altura fija** de 64px
- **Sticky/Fixed** en la parte superior

### ✅ Menús Desplegables

**Inicio** - Sin desplegable, link directo

**Asistente** - Con 3 opciones:
- Nuevo Proyecto
- Cargar API  
- Proyectos Recientes

**Historial** - Con 3 opciones:
- Todos los Proyectos
- Preview (solo si hay proyecto activo)
- Webs Recientes

**Ayuda** - Con 4 opciones:
- Documentación
- FAQ
- Contacto
- Reportar un problema

### ✅ Usuario Autenticado
Si el usuario está logueado, se muestra:
- Avatar circular con inicial del username
- Dropdown con: Mis Proyectos, Configuración, Cerrar Sesión

Si NO está logueado:
- Botón "Sign In"
- Botón "Registrarse" (primary style)

### ✅ Responsive
- Desktop: menú horizontal completo
- Mobile: menú hamburguesa colapsable
- Tablet: diseño adaptativo

---

## 🔍 Verificar la Integración

### 1. Prueba visual
Navega a cualquier página y verifica:
- [ ] La navbar aparece en la parte superior
- [ ] El fondo es negro (#0a0a0a)
- [ ] Los textos son blancos
- [ ] El logo se muestra correctamente

### 2. Prueba de dropdowns
- [ ] Haz clic en "Asistente" → Se abre menú con 3 opciones
- [ ] Haz clic en "Historial" → Se abre menú con opciones
- [ ] Haz clic en "Ayuda" → Se abre menú con 4 opciones
- [ ] Haz clic fuera → Se cierra el menú

### 3. Prueba de navegación
- [ ] Click en "Inicio" → Va a home
- [ ] Click en cada opción del dropdown → Va a la URL correcta
- [ ] El link activo se resalta con fondo más claro

### 4. Prueba responsive (móvil)
- [ ] Aparece el botón hamburguesa
- [ ] Click en hamburguesa → Se despliega menú vertical
- [ ] Los dropdowns funcionan en móvil

---

## 🐛 Solución de Problemas

### Problema: La navbar no se muestra
**Solución:** Verifica que los archivos estén en las rutas correctas:
```
WebBuilder/project/WebBuilder/
├── templates/
│   └── WebBuilder/
│       └── navbarOriginal.html  ← Aquí
├── static/
│   └── css/
│       └── navbarOriginal.css   ← Aquí
```

### Problema: Los dropdowns no funcionan
**Solución:** El JavaScript está integrado en el HTML. Verifica que no haya conflictos con otros scripts.

### Problema: El logo no se muestra
**Solución:** Verifica la ruta del logo en `static/images/logo.png` y ejecuta:
```bash
python manage.py collectstatic
```

### Problema: Hay doble navbar
**Solución:** Asegúrate de no tener dos includes de navbar en `base.html`

### Problema: Los estilos no se aplican
**Solución:** 
1. Limpia la caché del navegador (Ctrl+Shift+R)
2. Ejecuta `python manage.py collectstatic`
3. Verifica que la ruta del CSS sea correcta en el `<link>`

---

## 🎯 Próximos Pasos Opcionales

### 1. Añadir efecto scroll
Añadir al final del `<body>` en `base.html`:
```javascript
<script>
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.wb-navbar');
  if (window.scrollY > 20) {
    navbar.classList.add('wb-navbar--scrolled');
  } else {
    navbar.classList.remove('wb-navbar--scrolled');
  }
});
</script>
```

### 2. Añadir notificaciones/badges
En el HTML de la navbar, puedes añadir:
```html
<div class="wb-nav-link">
  Historial
  <span class="wb-badge">3</span>
  <span class="wb-nav-arrow"></span>
</div>
```

Y en el CSS:
```css
.wb-badge {
  background: #ff4444;
  color: white;
  font-size: 0.7rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-weight: 700;
}
```

### 3. Personalizar colores
Edita las variables CSS en `navbar_new.css`:
```css
:root {
  --navbar-bg: #0a0a0a;           /* Fondo navbar */
  --navbar-accent: #4a9eff;        /* Color acento (azul) */
  --navbar-text: #ffffff;          /* Color texto */
  /* ... */
}
```

---

## 📞 ¿Necesitas Ayuda?

Si encuentras algún problema o quieres personalizar algo más, avísame y te ayudo! 😊
