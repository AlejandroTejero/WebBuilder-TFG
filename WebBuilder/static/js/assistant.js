/**
 * WebBuilder — Asistente
 * Funciones del asistente: chips de URL, loading overlay y scroll automático.
 */

/**
 * Rellena el input de URL con un ejemplo predefinido.
 * @param {string} url - URL a insertar
 */
function fillUrl(url) {
  const input = document.querySelector('#form-analyze input[type="url"]');
  if (input) {
    input.value = url;
    input.focus();
  }
}

function fillPrompt(text) {
  const textarea = document.querySelector('#form-analyze textarea');
  if (textarea) {
    textarea.value = text;
    textarea.focus();
  }
}

function switchInputMode(mode) {
    const fieldUrl = document.getElementById('field-url') // necesitamos añadir este id
    const fieldFile = document.getElementById('field-file')
    const btnUrl = document.getElementById('btn-mode-url')
    const btnFile = document.getElementById('btn-mode-file')

    if (mode === 'url') {
        fieldUrl.style.display = 'block'
        fieldFile.style.display = 'none'
        btnUrl.classList.add('active')
        btnFile.classList.remove('active')
    } else {
        fieldUrl.style.display = 'none'
        fieldFile.style.display = 'block'
        btnUrl.classList.remove('active')
        btnFile.classList.add('active')
    }
}

/**
 * Muestra el overlay de carga y anima los pasos secuencialmente.
 * Se llama desde el onclick del botón de submit.
 */
function showLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (!overlay) return;

  overlay.classList.add('active');

  const stepIds = ['ls-1', 'ls-2', 'ls-3'];
  const steps = stepIds.map(id => document.getElementById(id));

  steps.forEach((step, i) => {
    setTimeout(() => {
      // Marcar el anterior como completado
      if (i > 0 && steps[i - 1]) {
        steps[i - 1].classList.remove('active');
        steps[i - 1].classList.add('done');
      }
      // Activar el actual
      if (step) step.classList.add('active');
    }, i * 2400);
  });
}

/**
 * Al cargar la página, si hay resultado (schema o análisis),
 * hace scroll suave hasta él para que el usuario lo vea sin buscar.
 */
document.addEventListener('DOMContentLoaded', () => {
  const target =
    document.getElementById('block-schema') ||
    document.getElementById('block-analysis');

  if (target) {
    setTimeout(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 350);
  }
});

// ── WIZARD DE PROMPT GUIADO ──────────────────────────────────────────────────

function switchPromptMode(mode) {
  const modes = ['free', 'examples', 'guided'];
  modes.forEach(m => {
    document.getElementById(`prompt-mode-${m}`).style.display = m === mode ? 'block' : 'none';
  });

  const btns = document.querySelectorAll('#prompt-mode-toggle .asst-toggle-btn');
  btns.forEach((btn, i) => {
    btn.classList.toggle('active', modes[i] === mode);
  });
}

function fillPromptAndSwitch(text) {
  fillPrompt(text);
  switchPromptMode('free');
}

function wizardNext(step) {
  [1, 2, 3].forEach(i => {
    document.getElementById(`wpanel-${i}`).style.display = i === step ? 'block' : 'none';
    const dot = document.getElementById(`wdot-${i}`);
    dot.classList.toggle('active', i === step);
    dot.classList.toggle('done', i < step);
  });
}

function wizardBuild() {
  const parts = [];

  // Paso 1: fondo y color
  const bg    = document.querySelector('[data-group="bg"].asst-wizard__opt--selected');
  const color = document.querySelector('[data-group="color"].asst-wizard__opt--selected');
  if (bg)    parts.push(bg.dataset.value);
  if (color) parts.push(color.dataset.value);

  // Paso 2: elementos destacados
  const checks = document.querySelectorAll('.asst-wizard__check input:checked');
  const hints  = Array.from(checks).map(c => c.dataset.hint);
  if (hints.length) parts.push(`destacar: ${hints.join(', ')}`);

  // Paso 3: personalidad
  const style = document.querySelector('[data-group="style"].asst-wizard__opt--selected');
  if (style) parts.push(style.dataset.value);

  // Extra opcional
  const extra = document.getElementById('wizard-extra').value.trim();
  if (extra) parts.push(extra);

  const prompt = parts.join('. ') + '.';
  fillPrompt(prompt);
  switchPromptMode('free');
}

// Selección exclusiva dentro de cada grupo
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('click', e => {
    const btn = e.target.closest('.asst-wizard__opt');
    if (!btn || !btn.dataset.group) return;
    const group = btn.dataset.group;
    document.querySelectorAll(`[data-group="${group}"]`).forEach(b => {
      b.classList.remove('asst-wizard__opt--selected');
    });
    btn.classList.add('asst-wizard__opt--selected');
  });
});