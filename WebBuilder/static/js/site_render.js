(function () {

  const CFG = window.SR_CONFIG || {};

  /* ══════════════════════════════════════════════════════════
     DEPLOY OVERLAY
  ══════════════════════════════════════════════════════════ */

  const deployOverlay = document.getElementById('deploy-loading-overlay');
  const DEPLOY_STEPS = [
    { id: 'ds-zip',   at: 0,     progress: 10 },
    { id: 'ds-unzip', at: 5000,  progress: 30 },
    { id: 'ds-build', at: 15000, progress: 55 },
    { id: 'ds-run',   at: 90000, progress: 85 },
    { id: 'ds-done',  at: 0,     progress: 100 },
  ];
  const progressBar   = document.getElementById('deploy-progress-bar');
  const progressLabel = document.getElementById('deploy-progress-label');
  const elapsedEl     = document.getElementById('deploy-elapsed');
  let deployTimer = null;
  let deployStart = null;
  let stepTimers  = [];

  function setProgress(pct) {
    if (progressBar)   progressBar.style.width = pct + '%';
    if (progressLabel) progressLabel.textContent = pct + '%';
  }

  function showDeployOverlay() {
    if (!deployOverlay) return;
    deployOverlay.classList.add('active');
    deployStart = Date.now();

    DEPLOY_STEPS.slice(0, -1).forEach((step, i) => {
      stepTimers.push(setTimeout(() => {
        if (i > 0) {
          const prev = document.getElementById(DEPLOY_STEPS[i - 1].id);
          if (prev) { prev.classList.remove('active'); prev.classList.add('done'); }
        }
        const el = document.getElementById(step.id);
        if (el) el.classList.add('active');
        setProgress(step.progress);
      }, step.at));
    });

    deployTimer = setInterval(() => {
      const s = Math.floor((Date.now() - deployStart) / 1000);
      if (elapsedEl) {
        elapsedEl.textContent = `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
      }
    }, 1000);
  }

  function finishDeployOverlay(success, previewUrl, errorMsg) {
    stepTimers.forEach(t => clearTimeout(t));
    stepTimers = [];
    clearInterval(deployTimer);

    if (success) {
      DEPLOY_STEPS.slice(0, -1).forEach(step => {
        const el = document.getElementById(step.id);
        if (el) { el.classList.remove('active'); el.classList.add('done'); }
      });
      const done = document.getElementById('ds-done');
      if (done) done.classList.add('active');
      setProgress(100);
      const title = document.getElementById('deploy-overlay-title');
      if (title) title.textContent = '¡Desplegado con éxito!';
      setTimeout(() => { window.location.reload(); }, 1800);
    } else {
      deployOverlay.classList.remove('active');
      const alertEl = document.getElementById('deploy-error-alert');
      const msgEl   = document.getElementById('deploy-error-msg');
      if (msgEl)   msgEl.textContent = errorMsg || 'Error desconocido.';
      if (alertEl) alertEl.style.display = 'flex';
    }
  }

  function startDeployPolling() {
    const interval = setInterval(async () => {
      try {
        const data = await (await fetch(CFG.deployStatusUrl)).json();
        if (data.deploy_status === 'done') {
          clearInterval(interval);
          finishDeployOverlay(true, data.preview_url);
        }
        if (data.deploy_status === 'error') {
          clearInterval(interval);
          finishDeployOverlay(false, '', data.deploy_error);
        }
      } catch (_) {}
    }, 3000);
  }

  /* ══════════════════════════════════════════════════════════
     VERSIONES
  ══════════════════════════════════════════════════════════ */

  async function loadVersions() {
    try {
      const res  = await fetch(CFG.versionsUrl);
      const data = await res.json();
      const list  = document.getElementById('versions-list');
      const count = document.getElementById('versions-count');
      if (!list) return;

      if (!data.versions.length) {
        list.innerHTML = '<div class="sr-versions__empty">Sin versiones guardadas</div>';
        if (count) count.textContent = '';
        return;
      }

      if (count) count.textContent = `(${data.versions.length})`;
      list.innerHTML = data.versions.map(v => `
        <div class="sr-versions__item"
             data-version-id="${v.id}"
             data-version-number="${v.version_number}"
             data-created-at="${v.created_at}">
          <span class="sr-versions__tag">v${v.version_number}</span>
          <span class="sr-versions__date">${v.created_at}</span>
        </div>
      `).join('');
    } catch (_) {}
  }

  function openVersionModal(id, number, date) {
    document.getElementById('version-modal-title').textContent = `v${number} — ${date}`;
    document.getElementById('version-modal-date').textContent  = date;
    document.getElementById('version-modal-restore').onclick   = () => restoreVersion(id);
    document.getElementById('version-modal-download').href     = `${CFG.restoreBaseUrl}${id}/download/`;
    document.getElementById('version-modal').style.display     = 'flex';
  }

  function closeVersionModal() {
    document.getElementById('version-modal').style.display = 'none';
  }

  async function restoreVersion(id) {
    if (!confirm('¿Restaurar esta versión? La actual se guardará como snapshot.')) return;
    const res  = await fetch(`${CFG.restoreBaseUrl}${id}/restore/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CFG.csrfToken },
    });
    const data = await res.json();
    if (data.ok) window.location.reload();
    else alert('Error al restaurar');
  }

  /* ══════════════════════════════════════════════════════════
     CHAT DE REFINAMIENTO
  ══════════════════════════════════════════════════════════ */

  function addChatMessage(text, type) {
    const box = document.getElementById('chat-messages');
    if (!box) return;
    const hint = box.querySelector('.sr-chat__hint');
    if (hint) hint.remove();
    const el = document.createElement('div');
    el.className = `sr-chat__msg sr-chat__msg--${type}`;
    el.textContent = text;
    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
    return el;
  }

  async function sendRefine() {
    const input  = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    if (!input || !sendBtn) return;

    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    sendBtn.disabled = true;
    addChatMessage(message, 'user');
    const thinking = addChatMessage('Pensando…', 'thinking');

    try {
      const res  = await fetch(CFG.refineUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken':  CFG.csrfToken,
        },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();

      if (thinking) thinking.remove();

      if (data.ok) {
        addChatMessage(`✓ Modificado: ${data.file} — Recargando preview…`, 'ai');
        // Recargar iframe
        const iframe = document.getElementById('site-iframe');
        if (iframe) {
          iframe.src = iframe.src;
        }
      } else {
        addChatMessage(`✗ Error: ${data.error}`, 'error');
      }
    } catch (e) {
      if (thinking) thinking.remove();
      addChatMessage('✗ Error de red', 'error');
    }

    sendBtn.disabled = false;
    input.focus();
  }

  function bindChatEvents() {
    const sendBtn = document.getElementById('chat-send');
    const input   = document.getElementById('chat-input');
    if (!sendBtn || !input) return;

    sendBtn.addEventListener('click', sendRefine);
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendRefine();
      }
    });
  }

  const GEN_STEP_MAP = [
    { id: 'gs-1', key: 'Analizando' },
    { id: 'gs-2', key: 'modelos' },
    { id: 'gs-3', key: 'vistas' },
    { id: 'gs-4', key: 'plantilla' },
    { id: 'gs-5', key: 'pagina' },
    { id: 'gs-6', key: 'Ensamblando' },
  ];

  function showGenOverlay() {
    const overlay = document.getElementById('gen-loading-overlay');
    if (overlay) overlay.classList.add('active');
  }

  function startGenPolling() {
    let currentStep = -1;
    const interval = setInterval(async () => {
      try {
        const data = await (await fetch(CFG.genStatusUrl)).json();

        if (data.step) {
          const idx = GEN_STEP_MAP.findIndex(s => data.step.includes(s.key));
          if (idx !== -1 && idx !== currentStep) {
            for (let i = 0; i < idx; i++) {
              const el = document.getElementById(GEN_STEP_MAP[i].id);
              if (el) { el.classList.remove('active'); el.classList.add('done'); }
            }
            const el = document.getElementById(GEN_STEP_MAP[idx].id);
            if (el) { el.classList.remove('done'); el.classList.add('active'); }
            currentStep = idx;
          }
        }

        if (data.status === 'ready' || data.status === 'error') {
          clearInterval(interval);
          window.location.reload();
        }
      } catch (_) {}
    }, 2000);
  }
  
  /* ══════════════════════════════════════════════════════════
     INIT
  ══════════════════════════════════════════════════════════ */

  function init() {
    // Deploy form overlay
    const deployForm = document.getElementById('deploy-form');
    if (deployForm) deployForm.addEventListener('submit', () => showDeployOverlay());

    // Deploy polling si está en curso
    if (CFG.currentDeployStatus === 'deploying') {
      showDeployOverlay();
      startDeployPolling();
    }

    // Gen overlay si está generando al cargar
    if (CFG.currentGenStatus === 'generating') {
      showGenOverlay();
      startGenPolling();
    }
    // Versiones
    loadVersions();
    const versionsList = document.getElementById('versions-list');
    if (versionsList) {
      versionsList.addEventListener('click', e => {
        const item = e.target.closest('.sr-versions__item');
        if (!item) return;
        openVersionModal(item.dataset.versionId, item.dataset.versionNumber, item.dataset.createdAt);
      });
    }

    const closeBtn      = document.getElementById('version-modal-close');
    const backdropEl    = document.getElementById('version-modal-backdrop');
    if (closeBtn)   closeBtn.addEventListener('click', closeVersionModal);
    if (backdropEl) backdropEl.addEventListener('click', closeVersionModal);

    // Chat
    bindChatEvents();
  }

  init();

})();