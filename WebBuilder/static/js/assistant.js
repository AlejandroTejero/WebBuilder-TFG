/**
 * WebBuilder Assistant - JavaScript Module
 * Maneja la navegación del wizard, transiciones y carga de preview
 */

// ==================== ESTADO GLOBAL ====================

let currentStep = 1;
let analysisData = null;

// ==================== NAVEGACIÓN ENTRE PASOS ====================

/**
 * Navega a un paso específico del wizard
 * @param {number} stepNumber - Número del paso (1-4)
 */
function goToStep(stepNumber) {
  if (stepNumber < 1 || stepNumber > 4) return;
  
  // Validaciones básicas
  if (stepNumber === 2 && !analysisData) {
    alert('Primero debes analizar una URL');
    return;
  }
  
  showStep(stepNumber, true);
}

/**
 * Muestra un paso con o sin animación de transición
 * @param {number} stepNumber - Número del paso a mostrar
 * @param {boolean} withTransition - Si debe mostrar animación
 */
function showStep(stepNumber, withTransition = true) {
  const overlay = document.getElementById('transitionOverlay');
  const progressFill = document.getElementById('progressBarFill');
  const transitionText = document.getElementById('transitionText');
  
  if (withTransition) {
    // Mostrar overlay
    overlay.classList.add('wb-transition-overlay--active');
    progressFill.style.width = '0%';
    transitionText.textContent = 'Cargando...';
    
    // Animar progreso
    let progress = 0;
    const interval = setInterval(() => {
      progress += 2;
      progressFill.style.width = progress + '%';
      
      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          performStepChange(stepNumber);
          overlay.classList.remove('wb-transition-overlay--active');
        }, 200);
      }
    }, 10);
  } else {
    performStepChange(stepNumber);
  }
}

/**
 * Realiza el cambio efectivo de paso
 * @param {number} stepNumber - Número del paso
 */
function performStepChange(stepNumber) {
  // Ocultar todos los pasos
  document.querySelectorAll('.wb-step').forEach(step => {
    step.style.display = 'none';
  });
  
  // Mostrar paso actual
  const currentStepEl = document.getElementById('step' + stepNumber);
  if (currentStepEl) {
    currentStepEl.style.display = 'block';
    currentStepEl.classList.add('wb-step--active');
  }
  
  // Actualizar navegación lateral
  document.querySelectorAll('.wb-step-nav').forEach(nav => {
    nav.classList.remove('wb-step-nav--active', 'wb-step-nav--completed');
    const navStep = parseInt(nav.dataset.step);
    
    if (navStep === stepNumber) {
      nav.classList.add('wb-step-nav--active');
    } else if (navStep < stepNumber) {
      nav.classList.add('wb-step-nav--completed');
    }
  });
  
  currentStep = stepNumber;
  
  // Cargar preview si es paso 3
  if (stepNumber === 3 && analysisData) {
    loadPreview();
  }
  
  // Inicializar controles del Paso 3
  if (stepNumber === 3) {
    setTimeout(initPreviewControls, 300);
  }
}

// ==================== PREVIEW ====================

/**
 * Carga el preview dinámicamente mediante AJAX
 */function loadPreview(index = 0) {
  const container = document.getElementById('previewContainer');

  if (!analysisData || !analysisData.id) {
    container.innerHTML = '<div class="wb-message wb-message--error">No hay datos para mostrar</div>';
    return;
  }

  const hiddenId = document.querySelector('input[name="api_request_id"]')?.value;
  const id = hiddenId || analysisData.id;

  const url = `/preview-cards/${id}?index=${encodeURIComponent(index)}`;

  fetch(url, {
    credentials: 'same-origin',
    cache: 'no-store',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(async (response) => {
      const html = await response.text();

      if (window.DEBUG) {
        console.log('PREVIEW FETCH:', { status: response.status, url: response.url });
      }

      if (response.redirected || response.url.includes('login')) {
        container.innerHTML =
          '<div class="wb-message wb-message--warning">El preview ha redirigido (posible login / sesión).</div>';
        return;
      }

      if (!html.trim()) {
        container.innerHTML = '<div class="wb-message wb-message--warning">No se encontraron items para mostrar</div>';
        return;
      }

      container.innerHTML = html;

      // Enganchar clicks a las cards para recargar con otro index
      container.querySelectorAll('.js-preview-item').forEach((el) => {
        const idx = parseInt(el.dataset.index || '0', 10);

        el.addEventListener('click', () => loadPreview(idx));
        el.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            loadPreview(idx);
          }
        });
      });
    })
    .catch((error) => {
      console.error('Error loading preview:', error);
      container.innerHTML = '<div class="wb-message wb-message--error">Error al cargar el preview: ' + error.message + '</div>';
    });
}


// ==================== CONFIRMACIÓN ====================

/**
 * Confirma el mapping y avanza al siguiente paso
 */
function confirmMapping() {
  if (confirm('¿Confirmas que el mapping es correcto?')) {
    goToStep(4);
  }
}

// ==================== SIDEBAR ====================

/**
 * Inicializa el toggle del sidebar
 */
function initSidebarToggle() {
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('wb-sidebar--collapsed');
      menuToggle.classList.toggle('wb-menu-toggle--collapsed');
      document.querySelector('.wb-main').classList.toggle('wb-main--expanded');
    });
  }
}

// ==================== NAVEGACIÓN LATERAL ====================

/**
 * Inicializa los event listeners de la navegación lateral
 */
function initStepNavigation() {
  document.querySelectorAll('.wb-step-nav').forEach(nav => {
    nav.addEventListener('click', () => {
      const step = parseInt(nav.dataset.step);
      goToStep(step);
    });
  });
}

// ==================== FORMULARIO PASO 2 ====================

/**
 * Maneja el submit del formulario de mapping (Paso 2)
 */
function initMappingFormSubmit(assistantUrl) {
  const form = document.getElementById('formStep2');
  
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
      const response = await fetch(assistantUrl, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
        cache: 'no-store'
      });

      if (!response.ok) {
        alert('Error al guardar el mapping');
        return;
      }

      // IMPORTANTE: el backend debería devolver JSON en AJAX
      const result = await response.json().catch(() => null);

      // 1) Fuente de verdad: hidden input del form
      const hiddenId = document.querySelector('input[name="api_request_id"]')?.value;
      if (hiddenId) {
        analysisData = analysisData || {};
        analysisData.id = parseInt(hiddenId, 10);
      }

      // 2) Si el backend devuelve el id (ideal), pisa con el real
      if (result && (result.api_request_id || result.id)) {
        analysisData = analysisData || {};
        analysisData.id = parseInt(result.api_request_id || result.id, 10);
      }

      goToStep(3);

    } catch (error) {
      console.error('Error:', error);
      alert('Error al guardar el mapping');
    }
  });
}

// ==================== INICIALIZACIÓN ====================

/**
 * Inicializa el módulo del asistente
 * @param {Object} config - Configuración inicial
 * @param {Object} config.analysisData - Datos del análisis actual
 * @param {number} config.initialStep - Paso inicial a mostrar
 * @param {string} config.assistantUrl - URL del endpoint del asistente
 * @param {boolean} config.debug - Modo debug (activa console.log)
 */
function initAssistant(config = {}) {
  // Configurar datos iniciales
  if (config.analysisData) {
    analysisData = config.analysisData;
  }
  
  if (config.initialStep) {
    currentStep = config.initialStep;
  }
  
  // Configurar modo debug
  window.DEBUG = config.debug || false;
  
  // Inicializar componentes
  initSidebarToggle();
  initStepNavigation();
  
  if (config.assistantUrl) {
    initMappingFormSubmit(config.assistantUrl);
  }
  
  // Mostrar paso inicial (sin transición)
  showStep(currentStep, false);
}

// ==================== EXPORTS ====================

// Si se usa como módulo, exportar funciones
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initAssistant,
    goToStep,
    showStep,
    loadPreview,
    confirmMapping
  };
}

// ==================== PASO 3 - PREVIEW INTERACTIVO ====================

/**
 * Inicializa los controles del preview del Paso 3
 */
function initPreviewControls() {
  console.log('Inicializando controles del preview...');
  
  // Referencias a layouts
  const layouts = {
    card: document.getElementById('cardLayout'),
    list: document.getElementById('listLayout'),
    timeline: document.getElementById('timelineLayout')
  };
  
  console.log('Layouts encontrados:', {
    card: !!layouts.card,
    list: !!layouts.list,
    timeline: !!layouts.timeline
  });
  
  // Estado actual
  let currentLayout = 'card';
  let currentColor = '#3b82f6';
  let currentFontScale = 1;
  
  // Cambiar layout
  const layoutButtons = document.querySelectorAll('.wb-layout-option');
  console.log('Botones de layout encontrados:', layoutButtons.length);
  
  layoutButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Click en layout:', this.dataset.layout);
      
      // Remover active de todos
      document.querySelectorAll('.wb-layout-option').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      const layout = this.dataset.layout;
      currentLayout = layout;
      
      // Ocultar todos los layouts
      if (layouts.card) layouts.card.classList.add('wb-preview-hidden');
      if (layouts.list) layouts.list.classList.add('wb-preview-hidden');
      if (layouts.timeline) layouts.timeline.classList.add('wb-preview-hidden');
      
      // Mostrar el seleccionado
      if (layouts[layout]) {
        layouts[layout].classList.remove('wb-preview-hidden');
        console.log('Layout cambiado a:', layout);
      }
    });
  });
  
  // Cambiar color
  const colorButtons = document.querySelectorAll('.wb-color-option');
  console.log('Botones de color encontrados:', colorButtons.length);
  
  colorButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Click en color:', this.dataset.color);
      
      document.querySelectorAll('.wb-color-option').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      currentColor = this.dataset.color;
      document.documentElement.style.setProperty('--accent-blue', currentColor);
      console.log('Color cambiado a:', currentColor);
    });
  });
  
  // Cambiar tamaño de fuente
  const fontSlider = document.getElementById('fontSizeSlider');
  console.log('Slider de fuente encontrado:', !!fontSlider);
  
  if (fontSlider) {
    fontSlider.addEventListener('input', function() {
      currentFontScale = this.value;
      document.documentElement.style.setProperty('--font-scale', currentFontScale);
      console.log('Escala de fuente cambiada a:', currentFontScale);
    });
  }
  
  // Toggle campos visibles
  const fieldCheckboxes = document.querySelectorAll('.wb-field-toggle input[type="checkbox"]');
  console.log('Checkboxes de campos encontrados:', fieldCheckboxes.length);
  
  fieldCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const field = this.id.replace('field-', '');
      const elements = document.querySelectorAll(`[data-field="${field}"]`);
      
      console.log(`Toggle campo ${field}:`, this.checked, 'elementos encontrados:', elements.length);
      
      elements.forEach(el => {
        if (this.checked) {
          el.style.display = '';
          el.style.removeProperty('display');
        } else {
          el.style.display = 'none';
        }
      });
    });
  });
  
  console.log('Controles del preview inicializados correctamente');
}
