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
}

// ==================== PREVIEW ====================

/**
 * Carga el preview dinámicamente mediante AJAX
 */
function loadPreview() {
  const container = document.getElementById('previewContainer');

  if (!analysisData || !analysisData.id) {
    container.innerHTML = '<div class="wb-message wb-message--error">No hay datos para mostrar</div>';
    return;
  }

  const hiddenId = document.querySelector('input[name="api_request_id"]')?.value;
  const id = hiddenId || analysisData.id;
  const url = `/preview-cards/${id}`;

  fetch(url, {
    credentials: 'same-origin',
    cache: 'no-store',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(async (response) => {
      const html = await response.text();

      // DEBUG: log en consola del navegador
      if (window.DEBUG) {
        console.log('PREVIEW FETCH:', {
          status: response.status,
          url: response.url,
          redirected: response.redirected,
          first200: html.slice(0, 200)
        });
      }

      // Si hay redirección (login), avisar
      if (response.redirected || response.url.includes('login')) {
        container.innerHTML =
          '<div class="wb-message wb-message--warning">El preview ha redirigido (posible login / sesión). Abre la consola (F12) y mira PREVIEW FETCH.</div>';
        return;
      }

      // El snippet ya devuelve el HTML listo, lo insertamos directamente
      if (html.trim()) {
        container.innerHTML = html;
        
        // Log para debugging
        if (window.DEBUG) {
          const items = container.querySelectorAll('.wb-preview-item');
          console.log('Items cargados en preview:', items.length);
        }
      } else {
        container.innerHTML = '<div class="wb-message wb-message--warning">No se encontraron items para mostrar</div>';
      }
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
