# 🛠️ Guía de Implementación Técnica - WebBuilder Wizard

## Roadmap de Implementación

Esta guía te llevará paso a paso por la implementación del nuevo sistema de wizard. Cada fase es independiente y puede ser desarrollada/testeada por separado.

---

## FASE 0: Preparación (1-2 días)

### Tareas

1. **Crear branch de desarrollo**
```bash
git checkout -b feature/wizard-redesign
```

2. **Backup de archivos actuales**
```bash
mkdir -p backups/
cp -r WebBuilder/templates/WebBuilder/assistant.html backups/
cp -r WebBuilder/views/assistant.py backups/
cp -r WebBuilder/static/css/assistant.css backups/
cp -r WebBuilder/static/js/assistant.js backups/
```

3. **Crear estructura de directorios**
```bash
mkdir -p WebBuilder/templates/WebBuilder/wizard/
mkdir -p WebBuilder/templates/WebBuilder/components/
mkdir -p WebBuilder/static/css/wizard/
mkdir -p WebBuilder/static/js/wizard/
mkdir -p WebBuilder/utils/wizard/
```

4. **Extender modelo APIRequest**

```python
# models.py

class APIRequest(models.Model):
    # Campos existentes
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    raw_data = models.TextField(blank=True, null=True)
    parsed_data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    response_summary = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    field_mapping = models.JSONField(blank=True, null=True)
    
    # NUEVOS CAMPOS
    project_name = models.CharField(
        max_length=200, 
        default="Mi Proyecto",
        verbose_name="Nombre del Proyecto"
    )
    
    source_metadata = models.JSONField(
        blank=True, 
        null=True,
        help_text="Metadata de la fuente (tipo, count, campos frecuentes, etc.)"
    )
    
    content_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Path al contenido principal (ej: 'data.results')"
    )
    
    template_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        choices=[
            ('directory', 'Directorio'),
            ('catalog', 'Catálogo'),
            ('blog', 'Blog/Noticias'),
            ('landing', 'Landing Page'),
            ('custom', 'Personalizado'),
        ]
    )
    
    template_config = models.JSONField(
        blank=True, 
        null=True,
        help_text="Configuración de páginas y features"
    )
    
    behavior_rules = models.JSONField(
        blank=True, 
        null=True,
        help_text="Reglas de comportamiento (URLs, orden, fallbacks, etc.)"
    )
    
    publication_status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('published', 'Publicada'),
            ('archived', 'Archivada'),
        ],
        default='draft'
    )
    
    django_project_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True
    )
    
    deployment_url = models.URLField(blank=True, null=True)
    
    current_step = models.IntegerField(
        default=1,
        help_text="Paso actual del wizard (1-6)"
    )
    
    completed_steps = models.JSONField(
        default=list,
        help_text="Lista de pasos completados"
    )
```

5. **Crear y aplicar migración**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## FASE 1: Layout Base del Wizard (3-4 días)

### Objetivo
Crear la estructura visual del wizard con navegación, header y footer funcionales.

### 1.1 Template Base del Wizard

```html
<!-- templates/WebBuilder/wizard/base.html -->
{% extends 'WebBuilder/base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/wizard/wizard.css' %}">
{% endblock %}

{% block content %}
<div class="wizard-container">
  
  <!-- Header del Wizard -->
  {% include 'WebBuilder/components/wizard_header.html' %}
  
  <!-- Layout principal -->
  <div class="wizard-layout">
    
    <!-- Navegación lateral -->
    <aside class="wizard-sidebar">
      {% include 'WebBuilder/components/wizard_nav.html' %}
    </aside>
    
    <!-- Contenido del paso actual -->
    <main class="wizard-main">
      
      <!-- Mensajes -->
      {% if messages %}
        <div class="wizard-messages">
          {% for message in messages %}
            <div class="wb-message wb-message--{{ message.tags }}">
              <span class="message-icon">
                {% if message.tags == 'success' %}✓{% endif %}
                {% if message.tags == 'error' %}✕{% endif %}
                {% if message.tags == 'warning' %}⚠{% endif %}
                {% if message.tags == 'info' %}ℹ{% endif %}
              </span>
              <span class="message-content">{{ message }}</span>
            </div>
          {% endfor %}
        </div>
      {% endif %}
      
      <!-- Contenido específico del paso -->
      {% block wizard_content %}{% endblock %}
      
    </main>
    
  </div>
  
  <!-- Footer del Wizard -->
  {% include 'WebBuilder/components/wizard_footer.html' %}
  
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/wizard/wizard.js' %}"></script>
{% endblock %}
```

### 1.2 Componente: Wizard Header

```html
<!-- templates/WebBuilder/components/wizard_header.html -->
<div class="wizard-header">
  <div class="wizard-header__project">
    <h1 
      class="project-name" 
      contenteditable="true"
      data-project-id="{{ api_request.id }}"
      id="projectName"
    >
      {{ api_request.project_name|default:"Mi Proyecto" }}
    </h1>
    <button class="edit-icon" aria-label="Editar nombre">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
      </svg>
    </button>
  </div>
  
  <div class="wizard-header__progress">
    <div class="progress-bar">
      <div 
        class="progress-fill" 
        style="width: {{ progress_percentage }}%"
      ></div>
    </div>
    <span class="progress-label">
      Paso {{ current_step }} de 6
    </span>
  </div>
</div>
```

### 1.3 Componente: Wizard Navigation

```html
<!-- templates/WebBuilder/components/wizard_nav.html -->
<nav class="wizard-nav">
  {% for step in wizard_steps %}
    <button 
      class="wizard-nav__step" 
      data-step="{{ step.number }}"
      data-state="{% if step.number < current_step %}completed{% elif step.number == current_step %}current{% else %}pending{% endif %}"
      {% if step.number > current_step and step.number not in accessible_steps %}disabled{% endif %}
    >
      <span class="step-number">{{ step.number }}</span>
      <span class="step-label">{{ step.label }}</span>
      <span class="step-icon">
        {% if step.number < current_step %}✓{% endif %}
        {% if step.number == current_step %}●{% endif %}
      </span>
    </button>
  {% endfor %}
</nav>
```

### 1.4 Componente: Wizard Footer

```html
<!-- templates/WebBuilder/components/wizard_footer.html -->
<div class="wizard-footer">
  <div class="footer-left">
    {% if current_step > 1 %}
      <button 
        class="btn btn-secondary" 
        onclick="navigateToStep({{ current_step|add:'-1' }})"
      >
        ← Atrás
      </button>
    {% endif %}
  </div>
  
  <div class="footer-actions">
    <button 
      class="btn btn-secondary" 
      id="saveDraft"
    >
      💾 Guardar borrador
    </button>
    
    <button 
      class="btn btn-primary" 
      id="continueBtn"
      {% if not can_continue %}disabled{% endif %}
    >
      Continuar →
    </button>
  </div>
</div>
```

### 1.5 JavaScript Base del Wizard

```javascript
// static/js/wizard/wizard.js

class WizardManager {
  constructor() {
    this.currentStep = parseInt(document.body.dataset.currentStep) || 1
    this.projectId = document.getElementById('projectName')?.dataset.projectId
    this.setupEventListeners()
  }
  
  setupEventListeners() {
    // Edición del nombre del proyecto
    const projectName = document.getElementById('projectName')
    if (projectName) {
      let saveTimeout
      projectName.addEventListener('input', (e) => {
        clearTimeout(saveTimeout)
        saveTimeout = setTimeout(() => {
          this.saveProjectName(e.target.textContent)
        }, 500)
      })
    }
    
    // Navegación entre pasos
    document.querySelectorAll('.wizard-nav__step').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const targetStep = parseInt(btn.dataset.step)
        const state = btn.dataset.state
        
        if (state === 'completed' || state === 'current') {
          this.navigateToStep(targetStep)
        }
      })
    })
    
    // Guardar borrador
    document.getElementById('saveDraft')?.addEventListener('click', () => {
      this.saveDraft()
    })
    
    // Continuar
    document.getElementById('continueBtn')?.addEventListener('click', () => {
      this.continueToNextStep()
    })
  }
  
  async saveProjectName(name) {
    try {
      const response = await fetch('/wizard/save-project-name/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({
          project_id: this.projectId,
          name: name
        })
      })
      
      if (response.ok) {
        this.showMessage('Nombre guardado', 'success')
      }
    } catch (error) {
      console.error('Error saving project name:', error)
    }
  }
  
  navigateToStep(step) {
    window.location.href = `/wizard/step/${step}/?project=${this.projectId}`
  }
  
  async saveDraft() {
    // Implementar según el paso actual
    this.showMessage('Borrador guardado', 'success')
  }
  
  continueToNextStep() {
    // Validar antes de continuar
    if (this.validateCurrentStep()) {
      this.navigateToStep(this.currentStep + 1)
    }
  }
  
  validateCurrentStep() {
    // Implementar validaciones por paso
    return true
  }
  
  showMessage(text, type = 'info') {
    const messagesContainer = document.querySelector('.wizard-messages') || 
                             this.createMessagesContainer()
    
    const message = document.createElement('div')
    message.className = `wb-message wb-message--${type}`
    message.innerHTML = `
      <span class="message-icon">${this.getIconForType(type)}</span>
      <span class="message-content">${text}</span>
    `
    
    messagesContainer.appendChild(message)
    
    setTimeout(() => {
      message.remove()
    }, 5000)
  }
  
  createMessagesContainer() {
    const container = document.createElement('div')
    container.className = 'wizard-messages'
    document.querySelector('.wizard-main').prepend(container)
    return container
  }
  
  getIconForType(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    }
    return icons[type] || icons.info
  }
  
  getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';')
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  window.wizardManager = new WizardManager()
})
```

### 1.6 Vista Principal del Wizard

```python
# views/wizard.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import APIRequest

WIZARD_STEPS = [
    {'number': 1, 'label': 'Fuente', 'url_name': 'wizard_step_1'},
    {'number': 2, 'label': 'Contenido', 'url_name': 'wizard_step_2'},
    {'number': 3, 'label': 'Páginas', 'url_name': 'wizard_step_3'},
    {'number': 4, 'label': 'Campos', 'url_name': 'wizard_step_4'},
    {'number': 5, 'label': 'Reglas', 'url_name': 'wizard_step_5'},
    {'number': 6, 'label': 'Publicar', 'url_name': 'wizard_step_6'},
]


def get_wizard_context(api_request, current_step):
    """
    Construye el contexto común para todos los pasos del wizard
    """
    completed_steps = api_request.completed_steps if api_request else []
    accessible_steps = list(range(1, current_step + 1)) + completed_steps
    
    progress_percentage = (current_step / 6) * 100
    
    return {
        'api_request': api_request,
        'wizard_steps': WIZARD_STEPS,
        'current_step': current_step,
        'completed_steps': completed_steps,
        'accessible_steps': accessible_steps,
        'progress_percentage': progress_percentage,
        'can_continue': False,  # Cada paso lo modifica según su validación
    }


@login_required
def wizard_home(request):
    """
    Página inicial del wizard - crea nuevo proyecto o carga uno existente
    """
    project_id = request.GET.get('project')
    
    if project_id:
        # Cargar proyecto existente
        api_request = get_object_or_404(APIRequest, id=project_id, user=request.user)
        return redirect('wizard_step', step=api_request.current_step)
    
    # Nuevo proyecto
    return redirect('wizard_step', step=1)


@login_required
def wizard_step(request, step):
    """
    Router principal del wizard - redirige al template del paso correspondiente
    """
    if step < 1 or step > 6:
        messages.error(request, "Paso inválido")
        return redirect('wizard_home')
    
    # Cargar o crear APIRequest
    project_id = request.GET.get('project')
    api_request = None
    
    if project_id:
        api_request = get_object_or_404(APIRequest, id=project_id, user=request.user)
        
        # Verificar que el paso sea accesible
        if step > api_request.current_step + 1 and step not in api_request.completed_steps:
            messages.warning(request, "Completa los pasos anteriores primero")
            return redirect('wizard_step', step=api_request.current_step)
    
    # Delegar a la vista específica de cada paso
    step_views = {
        1: wizard_step_1_source,
        2: wizard_step_2_content,
        3: wizard_step_3_template,
        4: wizard_step_4_mapping,
        5: wizard_step_5_rules,
        6: wizard_step_6_publish,
    }
    
    view_func = step_views.get(step)
    if view_func:
        return view_func(request, api_request)
    
    messages.error(request, "Paso no implementado")
    return redirect('wizard_home')


@login_required
@require_http_methods(["POST"])
def save_project_name(request):
    """
    Guarda el nombre del proyecto (AJAX)
    """
    import json
    
    data = json.loads(request.body)
    project_id = data.get('project_id')
    name = data.get('name', '').strip()
    
    if not name:
        return JsonResponse({'error': 'Nombre vacío'}, status=400)
    
    api_request = get_object_or_404(APIRequest, id=project_id, user=request.user)
    api_request.project_name = name
    api_request.save()
    
    return JsonResponse({'success': True})


# Placeholder para las vistas de cada paso
# Estas se implementarán en las siguientes fases

def wizard_step_1_source(request, api_request):
    """Paso 1: Fuente de datos"""
    context = get_wizard_context(api_request, 1)
    return render(request, 'WebBuilder/wizard/step1_source.html', context)

def wizard_step_2_content(request, api_request):
    """Paso 2: Selección de contenido"""
    context = get_wizard_context(api_request, 2)
    return render(request, 'WebBuilder/wizard/step2_content.html', context)

def wizard_step_3_template(request, api_request):
    """Paso 3: Tipo de plantilla"""
    context = get_wizard_context(api_request, 3)
    return render(request, 'WebBuilder/wizard/step3_template.html', context)

def wizard_step_4_mapping(request, api_request):
    """Paso 4: Mapping de campos"""
    context = get_wizard_context(api_request, 4)
    return render(request, 'WebBuilder/wizard/step4_mapping.html', context)

def wizard_step_5_rules(request, api_request):
    """Paso 5: Reglas de comportamiento"""
    context = get_wizard_context(api_request, 5)
    return render(request, 'WebBuilder/wizard/step5_rules.html', context)

def wizard_step_6_publish(request, api_request):
    """Paso 6: Preview y publicar"""
    context = get_wizard_context(api_request, 6)
    return render(request, 'WebBuilder/wizard/step6_publish.html', context)
```

### 1.7 URLs del Wizard

```python
# urls.py

from django.urls import path
from .views import wizard

urlpatterns = [
    # ... otras URLs existentes ...
    
    # Wizard
    path('wizard/', wizard.wizard_home, name='wizard_home'),
    path('wizard/step/<int:step>/', wizard.wizard_step, name='wizard_step'),
    path('wizard/save-project-name/', wizard.save_project_name, name='save_project_name'),
]
```

### 1.8 CSS Base del Wizard

```css
/* static/css/wizard/wizard.css */

/* Importar variables y componentes */
@import 'variables.css';
@import 'components/header.css';
@import 'components/navigation.css';
@import 'components/footer.css';
@import 'components/messages.css';

.wizard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
}

.wizard-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 250px 1fr;
  overflow: hidden;
}

.wizard-sidebar {
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
}

.wizard-main {
  overflow-y: auto;
  padding: var(--spacing-xl);
}

/* Responsive */
@media (max-width: 768px) {
  .wizard-layout {
    grid-template-columns: 1fr;
  }
  
  .wizard-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .wizard-sidebar.is-open {
    transform: translateX(0);
  }
}
```

---

## FASE 2: Implementar Pasos 1-3 (5-6 días)

### 2.1 Paso 1: Fuente de Datos

**Template:**
```html
<!-- templates/WebBuilder/wizard/step1_source.html -->
{% extends 'WebBuilder/wizard/base.html' %}

{% block wizard_content %}
<div class="wizard-workspace">
  
  <div class="workspace-column workspace-column--data">
    <div class="column-header">
      <h2>Conecta tu fuente de datos</h2>
      <p class="column-subtitle">Introduce la URL de una API que devuelva JSON o XML</p>
    </div>
    
    <div class="column-content">
      <form method="post" id="sourceForm">
        {% csrf_token %}
        
        <div class="form-group">
          <label for="api_url">URL de la API</label>
          <input 
            type="url" 
            id="api_url" 
            name="api_url"
            value="{{ api_request.api_url|default:'' }}"
            placeholder="https://api.example.com/items"
            required
          />
          <p class="form-hint">
            ℹ️ Soportamos JSON y XML. No necesitas configurar nada.
          </p>
        </div>
        
        <button type="submit" class="btn btn-primary">
          Probar Conexión
        </button>
      </form>
    </div>
  </div>
  
  <div class="workspace-column workspace-column--preview">
    <div class="column-header">
      <h2>Resultado</h2>
      <p class="column-subtitle">Información detectada de tu fuente</p>
    </div>
    
    <div class="column-content">
      {% if api_request and api_request.status == 'processed' %}
        <div class="source-result source-result--success">
          <div class="result-icon">✓</div>
          <h3>Conexión exitosa</h3>
          
          <div class="result-metadata">
            <h4>📊 Datos detectados:</h4>
            <ul>
              <li>Formato: <strong>{{ source_metadata.type }}</strong></li>
              <li>Elementos: <strong>{{ source_metadata.elements_count }}</strong></li>
              {% if source_metadata.frequent_fields %}
                <li>Campos frecuentes:
                  <ul class="field-list">
                    {% for field in source_metadata.frequent_fields %}
                      <li><code>{{ field }}</code></li>
                    {% endfor %}
                  </ul>
                </li>
              {% endif %}
            </ul>
          </div>
          
          <div class="result-sample">
            <h4>📋 Ejemplo de un elemento:</h4>
            <pre><code>{{ sample_element|safe }}</code></pre>
            <button class="btn-link" id="viewFullSample">
              Ver ejemplo completo ↗
            </button>
          </div>
        </div>
      {% elif api_request and api_request.status == 'error' %}
        <div class="source-result source-result--error">
          <div class="result-icon">✕</div>
          <h3>Error al conectar</h3>
          <p>{{ api_request.error_message }}</p>
        </div>
      {% else %}
        <div class="source-result source-result--empty">
          <p>Introduce una URL y prueba la conexión para ver los resultados</p>
        </div>
      {% endif %}
    </div>
  </div>
  
</div>
{% endblock %}
```

**Vista:**
```python
def wizard_step_1_source(request, api_request):
    """Paso 1: Validar y analizar fuente de datos"""
    
    if request.method == 'POST':
        api_url = request.POST.get('api_url', '').strip()
        
        if not api_url:
            messages.error(request, "Por favor introduce una URL")
            return redirect('wizard_step', step=1)
        
        # Crear o actualizar APIRequest
        if not api_request:
            api_request = APIRequest.objects.create(
                user=request.user,
                api_url=api_url,
                status='pending',
                current_step=1
            )
        else:
            api_request.api_url = api_url
            api_request.status = 'pending'
            api_request.save()
        
        # Intentar descargar y analizar
        try:
            from ..utils.url_reader import fetch_url
            from ..utils.parsers import parse_raw
            from ..utils.wizard.source_analyzer import analyze_source
            
            raw_text, fetch_summary = fetch_url(api_url)
            data_format, parsed_payload = parse_raw(raw_text)
            source_metadata = analyze_source(parsed_payload, data_format)
            
            api_request.raw_data = raw_text
            api_request.parsed_data = parsed_payload
            api_request.source_metadata = source_metadata
            api_request.status = 'processed'
            api_request.response_summary = fetch_summary
            
            # Marcar paso 1 como completado
            if 1 not in api_request.completed_steps:
                api_request.completed_steps.append(1)
            
            api_request.save()
            
            messages.success(request, "✓ Conexión exitosa. Datos analizados correctamente.")
            
        except Exception as e:
            api_request.status = 'error'
            api_request.error_message = str(e)
            api_request.save()
            messages.error(request, f"Error: {e}")
        
        return redirect('wizard_step', step=1) + f'?project={api_request.id}'
    
    # GET
    context = get_wizard_context(api_request, 1)
    
    if api_request and api_request.status == 'processed':
        context['can_continue'] = True
        context['source_metadata'] = api_request.source_metadata
        
        # Generar sample element formateado
        if api_request.parsed_data:
            import json
            first_element = api_request.parsed_data[0] if isinstance(api_request.parsed_data, list) else api_request.parsed_data
            context['sample_element'] = json.dumps(first_element, indent=2, ensure_ascii=False)
    
    return render(request, 'WebBuilder/wizard/step1_source.html', context)
```

**Utility: Source Analyzer**
```python
# utils/wizard/source_analyzer.py

def analyze_source(parsed_data, data_format):
    """
    Analiza la fuente de datos y extrae metadata útil
    
    Returns:
        {
            'type': 'JSON',
            'elements_count': 150,
            'frequent_fields': ['id', 'title', 'date'],
            'auth_required': False,
            'nested_level': 2
        }
    """
    metadata = {
        'type': data_format.upper(),
        'elements_count': 0,
        'frequent_fields': [],
        'auth_required': False,
        'nested_level': 0
    }
    
    # Contar elementos
    if isinstance(parsed_data, list):
        metadata['elements_count'] = len(parsed_data)
    elif isinstance(parsed_data, dict):
        # Buscar arrays en el dict
        for key, value in parsed_data.items():
            if isinstance(value, list):
                metadata['elements_count'] = max(metadata['elements_count'], len(value))
    
    # Detectar campos frecuentes
    all_fields = set()
    
    def collect_fields(obj, depth=0):
        metadata['nested_level'] = max(metadata['nested_level'], depth)
        
        if isinstance(obj, dict):
            all_fields.update(obj.keys())
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    collect_fields(value, depth + 1)
        elif isinstance(obj, list) and obj:
            collect_fields(obj[0], depth)
    
    collect_fields(parsed_data)
    metadata['frequent_fields'] = sorted(list(all_fields))[:10]  # Top 10
    
    return metadata
```

### 2.2 Paso 2: Selección de Contenido

**Utilidad para detectar candidatos:**
```python
# utils/wizard/content_detection.py

def detect_content_candidates(parsed_data):
    """
    Detecta posibles paths de contenido principal
    
    Returns:
        [
            {
                'path': 'data.results',
                'count': 150,
                'fields': ['id', 'title', 'date'],
                'samples': [...] # 3 elementos
            },
            ...
        ]
    """
    candidates = []
    
    def explore(obj, path=''):
        if isinstance(obj, list) and len(obj) >= 3:
            # Es un candidato potencial
            sample = obj[0] if obj else None
            
            if isinstance(sample, dict):
                candidates.append({
                    'path': path or 'root',
                    'count': len(obj),
                    'fields': list(sample.keys()),
                    'samples': obj[:3]
                })
        
        elif isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                explore(value, new_path)
    
    explore(parsed_data)
    
    # Ordenar por count descendente
    return sorted(candidates, key=lambda x: x['count'], reverse=True)
```

**Template Paso 2:**
```html
<!-- templates/WebBuilder/wizard/step2_content.html -->
{% extends 'WebBuilder/wizard/base.html' %}

{% block wizard_content %}
<div class="wizard-workspace">
  
  <div class="workspace-column workspace-column--data">
    <div class="column-header">
      <h2>¿Cuál es tu contenido principal?</h2>
      <p class="column-subtitle">Detectamos estas listas en tus datos</p>
    </div>
    
    <div class="column-content">
      <form method="post" id="contentForm">
        {% csrf_token %}
        <input type="hidden" name="content_path" id="selectedPath" value="{{ api_request.content_path|default:'' }}">
        
        <div class="candidates-list">
          {% for candidate in candidates %}
            <div class="candidate-card {% if candidate.path == api_request.content_path %}selected{% endif %}"
                 data-path="{{ candidate.path }}"
                 onclick="selectCandidate('{{ candidate.path }}')">
              <div class="candidate-header">
                <input 
                  type="radio" 
                  name="candidate" 
                  value="{{ candidate.path }}"
                  {% if candidate.path == api_request.content_path %}checked{% endif %}
                >
                <h3>{{ candidate.path }}</h3>
              </div>
              
              <div class="candidate-meta">
                <span class="meta-item">📊 {{ candidate.count }} elementos</span>
                <span class="meta-item">Campos: {{ candidate.fields|join:", " }}</span>
              </div>
              
              <button type="button" class="btn-link" onclick="toggleSamples(this)">
                Ver 3 ejemplos ↓
              </button>
              
              <div class="candidate-samples" style="display: none;">
                {% for sample in candidate.samples %}
                  <pre><code>{{ sample|safe }}</code></pre>
                {% endfor %}
              </div>
            </div>
          {% endfor %}
        </div>
        
        <button type="submit" class="btn btn-primary">
          Elegir este contenido
        </button>
      </form>
    </div>
  </div>
  
  <div class="workspace-column workspace-column--preview">
    <div class="column-header">
      <h2>Vista previa</h2>
      <p class="column-subtitle">Así se verían tus elementos</p>
    </div>
    
    <div class="column-content" id="previewContainer">
      <!-- Se actualiza vía AJAX al seleccionar candidato -->
    </div>
  </div>
  
</div>

<script>
function selectCandidate(path) {
  document.getElementById('selectedPath').value = path
  
  // Actualizar UI
  document.querySelectorAll('.candidate-card').forEach(card => {
    card.classList.remove('selected')
  })
  event.currentTarget.classList.add('selected')
  
  // Actualizar preview
  updatePreview(path)
}

function toggleSamples(btn) {
  const samples = btn.nextElementSibling
  samples.style.display = samples.style.display === 'none' ? 'block' : 'none'
  btn.textContent = samples.style.display === 'none' ? 'Ver 3 ejemplos ↓' : 'Ocultar ejemplos ↑'
}

async function updatePreview(path) {
  const response = await fetch(`/wizard/preview-content/?path=${encodeURIComponent(path)}&project=${projectId}`)
  const html = await response.text()
  document.getElementById('previewContainer').innerHTML = html
}
</script>
{% endblock %}
```

---

### 2.3 Paso 3: Tipo de Plantilla

Ver documento de arquitectura para diseño detallado.

---

## FASE 3: Paso 4 - Mapping Visual (8-10 días) ⭐

Esta es la fase más compleja e importante. Ver archivo separado `IMPLEMENTACION_MAPPING.md` para detalles completos.

---

## Testing Checklist

Al finalizar cada fase:

- [ ] Las migraciones se aplican sin errores
- [ ] La navegación entre pasos funciona
- [ ] El progreso se guarda en la base de datos
- [ ] Los mensajes de error son claros
- [ ] El diseño es responsive
- [ ] No hay errores en consola JS
- [ ] El wizard funciona sin JavaScript (degradado)

---

## Deployment Checklist

Antes de mergear a main:

- [ ] Todas las fases testeadas
- [ ] Migraciones aplicadas en staging
- [ ] CSS minificado y comprimido
- [ ] JS bundled y minificado
- [ ] Assets servidos con CDN
- [ ] Logs de errores configurados
- [ ] Analytics implementado
- [ ] Documentación actualizada

---

## Próximos Pasos

Continúa con la implementación detallada del **Paso 4: Mapping Visual** en el documento `IMPLEMENTACION_MAPPING.md`.
