(function () {

  /* ══════════════════════════════════════════════════════════
     CONFIGURACIÓN — inyectada desde el template Django
  ══════════════════════════════════════════════════════════ */
  const CFG = window.SR_CONFIG || {};

  /* ══════════════════════════════════════════════════════════
     ESTADO GLOBAL
  ══════════════════════════════════════════════════════════ */
  let currentPath = null;
  let originalContent = null;
  let monacoEditor = null;
  let monacoLoaded = false;
  let deployTimer = null;
  let deployStart = null;
  let stepTimers = [];

  const fileContents = {};

  /* ══════════════════════════════════════════════════════════
     UTILIDADES
  ══════════════════════════════════════════════════════════ */

  function qs(selector) {
    return document.querySelector(selector);
  }

  function qsa(selector) {
    return Array.from(document.querySelectorAll(selector));
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function langFromPath(path) {
    const ext = path.split('.').pop().toLowerCase();
    const map = {
      py: 'python', html: 'html', css: 'css',
      js: 'javascript', json: 'json', txt: 'plaintext',
      md: 'markdown', sh: 'shell', yml: 'yaml', yaml: 'yaml',
    };
    return map[ext] || 'plaintext';
  }

  function showFeedback(el, msg, type) {
    if (!el) return;
    el.textContent = msg;
    el.className = `sr-save-feedback sr-save-feedback--inline sr-save-feedback--${type}`;
    el.style.display = 'inline-block';
    setTimeout(() => {
      el.style.display = 'none';
    }, 3000);
  }

  /* ══════════════════════════════════════════════════════════
     ÁRBOL DE CARPETAS
  ══════════════════════════════════════════════════════════ */

  function buildTree(paths) {
    const root = {};
    paths.forEach(path => {
      const parts = path.split('/');
      let node = root;
      parts.forEach((part, i) => {
        if (i === parts.length - 1) {
          node[part] = null;
        } else {
          if (!node[part]) node[part] = {};
          node = node[part];
        }
      });
    });
    return root;
  }

  function renderTree(node, container, prefix, depth) {
    const entries = Object.entries(node);
    const folders = entries.filter(([, value]) => value !== null).sort(([a], [b]) => a.localeCompare(b));
    const files = entries.filter(([, value]) => value === null).sort(([a], [b]) => a.localeCompare(b));

    [...folders, ...files].forEach(([name, value]) => {
      const fullPath = prefix ? `${prefix}/${name}` : name;
      const isFile = value === null;
      const item = document.createElement('div');
      item.style.paddingLeft = `${depth * 12}px`;

      if (isFile) {
        item.className = 'sr-tree__item';
        item.dataset.path = fullPath;
        item.dataset.content = fileContents[fullPath] || '';
        item.addEventListener('click', () => srSelectFile(item));

        const label = document.createElement('span');
        label.className = 'sr-tree__name';
        label.textContent = name;
        item.appendChild(label);
      } else {
        item.className = 'sr-tree__folder';

        const header = document.createElement('div');
        header.className = 'sr-tree__folder-header';

        const arrow = document.createElement('span');
        arrow.className = 'sr-tree__arrow';
        arrow.textContent = '▾';

        const label = document.createElement('span');
        label.className = 'sr-tree__folder-name';
        label.textContent = name;

        header.appendChild(arrow);
        header.appendChild(label);

        const children = document.createElement('div');
        children.className = 'sr-tree__children';
        renderTree(value, children, fullPath, depth + 1);

        header.addEventListener('click', () => {
          const open = children.style.display !== 'none';
          children.style.display = open ? 'none' : 'block';
          arrow.textContent = open ? '▸' : '▾';
          header.classList.toggle('sr-tree__folder-header--closed', open);
        });

        item.appendChild(header);
        item.appendChild(children);
      }

      container.appendChild(item);
    });
  }

  function initTree() {
    const dataEl = document.getElementById('sr-files-data');
    if (!dataEl) return;

    let parsed;
    try {
      parsed = JSON.parse(dataEl.textContent);
    } catch (error) {
      console.error('sr-files-data JSON inválido', error);
      return;
    }

    const files = parsed.files || [];
    files.forEach(file => {
      fileContents[file.path] = file.content;
    });

    const paths = files.map(file => file.path);
    const tree = buildTree(paths);
    const container = document.getElementById('sr-tree');
    if (container) renderTree(tree, container, '', 0);
  }

  /* ══════════════════════════════════════════════════════════
     VISOR — selección de archivo
  ══════════════════════════════════════════════════════════ */

  function srSelectFile(el) {
    qsa('.sr-tree__item').forEach(item => item.classList.remove('sr-tree__item--active'));
    el.classList.add('sr-tree__item--active');

    currentPath = el.dataset.path;
    originalContent = el.dataset.content;

    document.getElementById('sr-empty').style.display = 'none';
    document.getElementById('sr-header').style.display = 'flex';
    document.getElementById('sr-code-wrap').style.display = 'block';
    document.getElementById('sr-filename').textContent = currentPath;
    document.getElementById('sr-save-feedback').style.display = 'none';

    const lang = langFromPath(currentPath);
    const codeEl = document.getElementById('sr-code');
    codeEl.className = `language-${lang}`;
    codeEl.textContent = originalContent;
    if (window.Prism) Prism.highlightElement(codeEl);
  }

  /* ══════════════════════════════════════════════════════════
     EDITOR MONACO — modal pantalla completa
  ══════════════════════════════════════════════════════════ */

  require.config({
    paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
  });

  function srStartEdit() {
    if (!currentPath) return;

    document.getElementById('sr-modal-filename').textContent = currentPath;
    document.getElementById('sr-save-feedback-modal').style.display = 'none';
    document.getElementById('sr-modal').classList.add('sr-modal--open');
    document.body.style.overflow = 'hidden';

    const lang = langFromPath(currentPath);
    if (!monacoLoaded) {
      require(['vs/editor/editor.main'], function () {
        monacoLoaded = true;
        mountMonaco(lang);
      });
    } else {
      mountMonaco(lang);
    }
  }

  function mountMonaco(lang) {
    const container = document.getElementById('monaco-container');
    if (monacoEditor) {
      monacoEditor.dispose();
      monacoEditor = null;
    }

    monacoEditor = monaco.editor.create(container, {
      value: originalContent,
      language: lang,
      theme: 'vs-dark',
      fontSize: 13,
      lineHeight: 22,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
      fontLigatures: true,
      renderWhitespace: 'selection',
      tabSize: 4,
      wordWrap: 'off',
    });

    monacoEditor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
      () => srSave()
    );
  }

  function srCancelEdit() {
    document.getElementById('sr-modal').classList.remove('sr-modal--open');
    document.body.style.overflow = '';
    if (monacoEditor) {
      monacoEditor.dispose();
      monacoEditor = null;
    }
  }

  async function srSave() {
    if (!monacoEditor) return;

    const content = monacoEditor.getValue();
    const saveBtn = document.getElementById('sr-btn-save');
    const feedback = document.getElementById('sr-save-feedback-modal');

    saveBtn.textContent = 'Guardando…';
    saveBtn.disabled = true;

    try {
      const res = await fetch(CFG.updateFileUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': CFG.csrfToken,
        },
        body: JSON.stringify({ path: currentPath, content }),
      });
      const data = await res.json();

      if (data.ok) {
        fileContents[currentPath] = content;
        const item = document.querySelector(`.sr-tree__item[data-path="${CSS.escape(currentPath)}"]`);
        if (item) item.dataset.content = content;
        originalContent = content;

        const lang = langFromPath(currentPath);
        const codeEl = document.getElementById('sr-code');
        codeEl.className = `language-${lang}`;
        codeEl.textContent = content;
        if (window.Prism) Prism.highlightElement(codeEl);

        showFeedback(feedback, '✓ Guardado', 'success');
        setTimeout(() => srCancelEdit(), 800);
      } else {
        showFeedback(feedback, '✗ ' + (data.error || 'Error'), 'error');
      }
    } catch (_) {
      showFeedback(feedback, '✗ Error de red', 'error');
    }

    saveBtn.textContent = 'Guardar';
    saveBtn.disabled = false;
  }

  /* ══════════════════════════════════════════════════════════
     VERSIONES — listado, modal y restauración
  ══════════════════════════════════════════════════════════ */

  async function loadVersions() {
    const res = await fetch(CFG.versionsUrl);
    const data = await res.json();
    const list = document.getElementById('versions-list');
    const count = document.getElementById('versions-count');

    if (!data.versions.length) {
      list.innerHTML = '<div class="asst-versions__empty">Sin versiones guardadas</div>';
      count.textContent = '';
      return;
    }

    count.textContent = `(${data.versions.length})`;
    list.innerHTML = data.versions.map(version => `
      <div class="asst-versions__item" data-version-id="${version.id}" data-version-number="${version.version_number}" data-created-at="${escapeHtml(version.created_at)}">
        <span class="asst-versions__tag">v${version.version_number}</span>
        <span class="asst-versions__date">${escapeHtml(version.created_at)}</span>
      </div>
    `).join('');
  }

  function openVersionModal(versionId, versionNumber, createdAt) {
    document.getElementById('version-modal-title').textContent = `v${versionNumber} — ${createdAt}`;
    document.getElementById('version-modal-date').textContent = createdAt;
    document.getElementById('version-modal-restore').onclick = () => restoreVersion(versionId);
    document.getElementById('version-modal-download').href = `${CFG.restoreBaseUrl}${versionId}/download/`;
    document.getElementById('version-modal').style.display = 'flex';
  }

  function closeVersionModal() {
    document.getElementById('version-modal').style.display = 'none';
  }

  async function restoreVersion(versionId) {
    if (!confirm('¿Restaurar esta versión? La actual se guardará como snapshot.')) return;

    const res = await fetch(`${CFG.restoreBaseUrl}${versionId}/restore/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CFG.csrfToken },
    });
    const data = await res.json();

    if (data.ok) {
      window.location.reload();
    } else {
      alert('Error al restaurar');
    }
  }

  /* ══════════════════════════════════════════════════════════
     USUARIOS — filas dinámicas y guardado
  ══════════════════════════════════════════════════════════ */

  function createUserRow() {
    const row = document.createElement('div');
    row.className = 'site-user-row';
    row.innerHTML = `
      <input type="text" class="user-input" placeholder="Usuario">
      <input type="password" class="user-input" placeholder="Contraseña">
      <select class="user-select">
        <option value="normal">Normal</option>
        <option value="super">Superusuario</option>
      </select>
      <button class="sr-btn sr-btn--cancel" type="button" data-user-remove>✕</button>
    `;
    return row;
  }

  function addUserRow() {
    const list = document.getElementById('users-list');
    if (!list) return;
    list.appendChild(createUserRow());
  }

  function removeUserRow(button) {
    const row = button.closest('.site-user-row');
    if (row) row.remove();
  }

  function showUsersFeedback(msg, ok) {
    const el = document.getElementById('users-feedback');
    if (!el) return;
    el.textContent = msg;
    el.style.display = 'block';
    el.style.color = ok ? '#4ade80' : '#f87171';
    setTimeout(() => {
      el.style.display = 'none';
    }, 3000);
  }

  async function saveUsers() {
    const rows = qsa('.site-user-row');
    const users = [];

    for (const row of rows) {
      const inputs = row.querySelectorAll('.user-input');
      const select = row.querySelector('.user-select');
      const username = inputs[0].value.trim();
      const password = inputs[1].value.trim();
      const role = select.value;

      if (!username || !password) {
        showUsersFeedback('Todos los usuarios deben tener usuario y contraseña.', false);
        return;
      }

      users.push({ username, password, role });
    }

    const res = await fetch(CFG.usersSaveUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': CFG.csrfToken,
      },
      body: JSON.stringify({ users }),
    });
    const data = await res.json();

    if (data.ok) {
      showUsersFeedback(`✔ ${data.saved} usuario(s) guardados correctamente.`, true);
    } else {
      showUsersFeedback(`✗ Error: ${data.error}`, false);
    }
  }

  /* ══════════════════════════════════════════════════════════
     OVERLAY — GENERACIÓN
  ══════════════════════════════════════════════════════════ */

  const genOverlay = document.getElementById('gen-loading-overlay');
  const genSteps = ['gs-1', 'gs-2', 'gs-3', 'gs-4', 'gs-5', 'gs-6'].map(id => document.getElementById(id));

  function showGenOverlay() {
    if (!genOverlay) return;
    genOverlay.classList.add('active');
    genSteps.forEach((step, i) => {
      setTimeout(() => {
        if (i > 0 && genSteps[i - 1]) {
          genSteps[i - 1].classList.remove('active');
          genSteps[i - 1].classList.add('done');
        }
        if (step) step.classList.add('active');
      }, i * 8000);
    });
  }

  function startGenPolling() {
    const interval = setInterval(async () => {
      try {
        const data = await (await fetch(CFG.genStatusUrl)).json();
        if (data.status === 'ready' || data.status === 'error') {
          clearInterval(interval);
          window.location.reload();
        }
      } catch (_) {}
    }, 4000);
  }

  /* ══════════════════════════════════════════════════════════
     OVERLAY — DESPLIEGUE
  ══════════════════════════════════════════════════════════ */

  const deployOverlay = document.getElementById('deploy-loading-overlay');
  const DEPLOY_STEPS = [
    { id: 'ds-zip', at: 0, progress: 10 },
    { id: 'ds-unzip', at: 5000, progress: 30 },
    { id: 'ds-build', at: 15000, progress: 55 },
    { id: 'ds-run', at: 90000, progress: 85 },
    { id: 'ds-done', at: 0, progress: 100 },
  ];
  const progressBar = document.getElementById('deploy-progress-bar');
  const progressLabel = document.getElementById('deploy-progress-label');
  const elapsedEl = document.getElementById('deploy-elapsed');

  function setProgress(pct) {
    if (progressBar) progressBar.style.width = pct + '%';
    if (progressLabel) progressLabel.textContent = pct + '%';
  }

  function showDeployOverlay() {
    if (!deployOverlay) return;

    deployOverlay.classList.add('active');
    deployStart = Date.now();

    DEPLOY_STEPS.slice(0, -1).forEach((step, i) => {
      stepTimers.push(setTimeout(() => {
        if (i > 0) {
          const previous = document.getElementById(DEPLOY_STEPS[i - 1].id);
          if (previous) {
            previous.classList.remove('active');
            previous.classList.add('done');
          }
        }

        const el = document.getElementById(step.id);
        if (el) el.classList.add('active');
        setProgress(step.progress);
      }, step.at));
    });

    deployTimer = setInterval(() => {
      const seconds = Math.floor((Date.now() - deployStart) / 1000);
      if (elapsedEl) {
        elapsedEl.textContent = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
      }
    }, 1000);
  }

  function finishDeployOverlay(success, previewUrl, errorMsg) {
    stepTimers.forEach(timer => clearTimeout(timer));
    stepTimers = [];
    clearInterval(deployTimer);

    if (success) {
      DEPLOY_STEPS.slice(0, -1).forEach(step => {
        const el = document.getElementById(step.id);
        if (el) {
          el.classList.remove('active');
          el.classList.add('done');
        }
      });

      const done = document.getElementById('ds-done');
      if (done) done.classList.add('active');
      setProgress(100);

      const title = document.getElementById('deploy-overlay-title');
      if (title) title.textContent = '¡Desplegado con éxito!';

      setTimeout(() => {
        deployOverlay.classList.remove('active');
        window.location.reload();
      }, 1800);
    } else {
      deployOverlay.classList.remove('active');
      const alertEl = document.getElementById('deploy-error-alert');
      const msgEl = document.getElementById('deploy-error-msg');
      const pillEl = document.getElementById('deploy-status-pill');
      const valueEl = document.getElementById('deploy-status-value');
      if (msgEl) msgEl.textContent = errorMsg || 'Error desconocido.';
      if (alertEl) alertEl.style.display = 'flex';
      if (pillEl) pillEl.style.display = '';
      if (valueEl) valueEl.textContent = 'error';
    }
  }

  function startDeployPolling() {
    const interval = setInterval(async () => {
      try {
        const data = await (await fetch(CFG.deployStatusUrl)).json();

        if (data.deploy_status === 'done') {
          clearInterval(interval);
          const pillEl = document.getElementById('deploy-status-pill');
          const valueEl = document.getElementById('deploy-status-value');
          const linkEl = document.getElementById('preview-link');
          if (pillEl) pillEl.style.display = '';
          if (valueEl) valueEl.textContent = 'done';
          if (linkEl && data.preview_url) {
            linkEl.href = data.preview_url;
            linkEl.style.display = '';
          }
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
     EVENTOS — listeners del DOM
  ══════════════════════════════════════════════════════════ */

  function bindEditorEvents() {
    const editBtn = document.getElementById('sr-btn-edit');
    const cancelBtn = document.getElementById('sr-btn-cancel');
    const saveBtn = document.getElementById('sr-btn-save');

    if (editBtn) editBtn.addEventListener('click', srStartEdit);
    if (cancelBtn) cancelBtn.addEventListener('click', srCancelEdit);
    if (saveBtn) saveBtn.addEventListener('click', srSave);

    document.addEventListener('keydown', event => {
      const modal = document.getElementById('sr-modal');
      if (event.key === 'Escape' && modal && modal.classList.contains('sr-modal--open')) {
        srCancelEdit();
      }
    });
  }

  function bindUserEvents() {
    const addBtn = document.getElementById('users-add-btn');
    const saveBtn = document.getElementById('users-save-btn');
    const usersList = document.getElementById('users-list');

    if (addBtn) addBtn.addEventListener('click', addUserRow);
    if (saveBtn) saveBtn.addEventListener('click', saveUsers);
    if (usersList) {
      usersList.addEventListener('click', event => {
        const removeBtn = event.target.closest('[data-user-remove]');
        if (removeBtn) removeUserRow(removeBtn);
      });
    }
  }

  function bindVersionEvents() {
    const closeBtn = document.getElementById('version-modal-close');
    const versionsList = document.getElementById('versions-list');

    if (closeBtn) closeBtn.addEventListener('click', closeVersionModal);
    if (versionsList) {
      versionsList.addEventListener('click', event => {
        const item = event.target.closest('.asst-versions__item');
        if (!item) return;
        openVersionModal(item.dataset.versionId, item.dataset.versionNumber, item.dataset.createdAt);
      });
    }
  }

  function bindOverlayEvents() {
    const genForm = document.querySelector('form[action*="generate"]');
    const deployForm = document.getElementById('deploy-form');

    if (genForm) genForm.addEventListener('submit', () => showGenOverlay());
    if (deployForm) deployForm.addEventListener('submit', () => showDeployOverlay());
  }

  /* ══════════════════════════════════════════════════════════
     INIT
  ══════════════════════════════════════════════════════════ */

  function init() {
    initTree();
    bindEditorEvents();
    bindUserEvents();
    bindVersionEvents();
    bindOverlayEvents();
    loadVersions();

    if (CFG.currentGenStatus === 'generating') {
      showGenOverlay();
      startGenPolling();
    }

    if (CFG.currentDeployStatus === 'deploying') {
      showDeployOverlay();
      startDeployPolling();
    }
  }

  init();

})();