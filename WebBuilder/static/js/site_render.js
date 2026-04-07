(function () {

  /* ══════════════════════════════════════════════════════════
     CONFIGURACIÓN — inyectada desde el template Django
  ══════════════════════════════════════════════════════════ */
  const CFG = window.SR_CONFIG || {};

  /* ══════════════════════════════════════════════════════════
     ESTADO GLOBAL
  ══════════════════════════════════════════════════════════ */
  let currentPath     = null;
  let originalContent = null;
  let monacoEditor    = null;
  let monacoLoaded    = false;

  // Mapa de rutas → contenido, construido al parsear el JSON
  const fileContents = {};

  /* ══════════════════════════════════════════════════════════
     ÁRBOL DE CARPETAS
  ══════════════════════════════════════════════════════════ */

  /**
   * Convierte la lista plana de rutas en un objeto anidado.
   * Ej: ["a/b/c.py", "a/d.py"] →
   *   { a: { b: { "c.py": null }, "d.py": null } }
   * null = es un archivo (hoja del árbol)
   */
  function buildTree(paths) {
    const root = {};
    paths.forEach(path => {
      const parts = path.split('/');
      let node = root;
      parts.forEach((part, i) => {
        if (i === parts.length - 1) {
          // archivo
          node[part] = null;
        } else {
          // carpeta
          if (!node[part]) node[part] = {};
          node = node[part];
        }
      });
    });
    return root;
  }

  /**
   * Renderiza el árbol en el DOM a partir del objeto anidado.
   * prefix acumula la ruta completa para archivos.
   * depth controla la indentación.
   */
  function renderTree(node, container, prefix, depth) {
    // Separar carpetas y archivos, ordenar alfabéticamente
    const entries = Object.entries(node);
    const folders = entries.filter(([, v]) => v !== null).sort(([a], [b]) => a.localeCompare(b));
    const files   = entries.filter(([, v]) => v === null).sort(([a], [b]) => a.localeCompare(b));

    // Primero carpetas, luego archivos (como VSCode)
    [...folders, ...files].forEach(([name, value]) => {
      const fullPath = prefix ? `${prefix}/${name}` : name;
      const isFile   = value === null;

      const item = document.createElement('div');
      item.style.paddingLeft = `${depth * 12}px`;

      if (isFile) {
        item.className       = 'sr-tree__item';
        item.dataset.path    = fullPath;
        item.dataset.content = fileContents[fullPath] || '';
        item.onclick         = () => srSelectFile(item);

        const label = document.createElement('span');
        label.className   = 'sr-tree__name';
        label.textContent = name;
        item.appendChild(label);

      } else {
        // Carpeta
        item.className = 'sr-tree__folder';

        const header = document.createElement('div');
        header.className = 'sr-tree__folder-header';

        const arrow = document.createElement('span');
        arrow.className   = 'sr-tree__arrow';
        arrow.textContent = '▾'; // abierta por defecto

        const label = document.createElement('span');
        label.className   = 'sr-tree__folder-name';
        label.textContent = name;

        header.appendChild(arrow);
        header.appendChild(label);

        const children = document.createElement('div');
        children.className = 'sr-tree__children';

        // Rellenar hijos recursivamente
        renderTree(value, children, fullPath, depth + 1);

        // Toggle al hacer clic en la cabecera
        header.onclick = () => {
          const open = children.style.display !== 'none';
          children.style.display = open ? 'none' : 'block';
          arrow.textContent      = open ? '▸' : '▾';
          header.classList.toggle('sr-tree__folder-header--closed', open);
        };

        item.appendChild(header);
        item.appendChild(children);
      }

      container.appendChild(item);
    });
  }

  /** Inicializa el árbol leyendo el JSON embebido en el HTML */
  function initTree() {
    const dataEl = document.getElementById('sr-files-data');
    if (!dataEl) return;

    let parsed;
    try {
      parsed = JSON.parse(dataEl.textContent);
    } catch (e) {
      console.error('sr-files-data JSON inválido', e);
      return;
    }

    const files = parsed.files || [];
    files.forEach(f => { fileContents[f.path] = f.content; });

    const paths = files.map(f => f.path);
    const tree  = buildTree(paths);
    const container = document.getElementById('sr-tree');
    if (container) renderTree(tree, container, '', 0);
  }

  /* ══════════════════════════════════════════════════════════
     VISOR — selección de archivo
  ══════════════════════════════════════════════════════════ */

  function langFromPath(path) {
    const ext = path.split('.').pop().toLowerCase();
    const map = {
      py: 'python', html: 'html', css: 'css',
      js: 'javascript', json: 'json', txt: 'plaintext',
      md: 'markdown', sh: 'shell', yml: 'yaml', yaml: 'yaml',
    };
    return map[ext] || 'plaintext';
  }

  window.srSelectFile = function(el) {
    // Quitar activo anterior
    document.querySelectorAll('.sr-tree__item').forEach(i => i.classList.remove('sr-tree__item--active'));
    el.classList.add('sr-tree__item--active');

    currentPath     = el.dataset.path;
    originalContent = el.dataset.content;

    document.getElementById('sr-empty').style.display     = 'none';
    document.getElementById('sr-header').style.display    = 'flex';
    document.getElementById('sr-code-wrap').style.display = 'block';
    document.getElementById('sr-filename').textContent    = currentPath;
    document.getElementById('sr-save-feedback').style.display = 'none';

    const lang   = langFromPath(currentPath);
    const codeEl = document.getElementById('sr-code');
    codeEl.className   = `language-${lang}`;
    codeEl.textContent = originalContent;
    if (window.Prism) Prism.highlightElement(codeEl);
  };

  /* ══════════════════════════════════════════════════════════
     EDITOR MONACO — modal pantalla completa
  ══════════════════════════════════════════════════════════ */

  require.config({
    paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
  });

  window.srStartEdit = function() {
    if (!currentPath) return;
    document.getElementById('sr-modal-filename').textContent      = currentPath;
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
  };

  function mountMonaco(lang) {
    const container = document.getElementById('monaco-container');
    if (monacoEditor) { monacoEditor.dispose(); monacoEditor = null; }

    monacoEditor = monaco.editor.create(container, {
      value:                originalContent,
      language:             lang,
      theme:                'vs-dark',
      fontSize:             13,
      lineHeight:           22,
      minimap:              { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout:      true,
      fontFamily:           "'Fira Code', 'Cascadia Code', Consolas, monospace",
      fontLigatures:        true,
      renderWhitespace:     'selection',
      tabSize:              4,
      wordWrap:             'off',
    });

    monacoEditor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
      () => srSave()
    );
  }

  window.srCancelEdit = function() {
    document.getElementById('sr-modal').classList.remove('sr-modal--open');
    document.body.style.overflow = '';
    if (monacoEditor) { monacoEditor.dispose(); monacoEditor = null; }
  };

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.getElementById('sr-modal').classList.contains('sr-modal--open')) {
      srCancelEdit();
    }
  });

  window.srSave = async function() {
    if (!monacoEditor) return;
    const content  = monacoEditor.getValue();
    const saveBtn  = document.getElementById('sr-btn-save');
    const feedback = document.getElementById('sr-save-feedback-modal');

    saveBtn.textContent = 'Guardando…';
    saveBtn.disabled    = true;

    try {
      const res  = await fetch(CFG.updateFileUrl, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrfToken },
        body:    JSON.stringify({ path: currentPath, content }),
      });
      const data = await res.json();

      if (data.ok) {
        // Actualizar el mapa en memoria y el data-content del item del árbol
        fileContents[currentPath] = content;
        const item = document.querySelector(`.sr-tree__item[data-path="${CSS.escape(currentPath)}"]`);
        if (item) item.dataset.content = content;
        originalContent = content;

        // Refrescar el visor de solo lectura
        const lang   = langFromPath(currentPath);
        const codeEl = document.getElementById('sr-code');
        codeEl.className   = `language-${lang}`;
        codeEl.textContent = content;
        if (window.Prism) Prism.highlightElement(codeEl);

        showFeedback(feedback, '✓ Guardado', 'success');
        setTimeout(() => srCancelEdit(), 800);
      } else {
        showFeedback(feedback, '✗ ' + (data.error || 'Error'), 'error');
      }
    } catch (e) {
      showFeedback(feedback, '✗ Error de red', 'error');
    }

    saveBtn.textContent = 'Guardar';
    saveBtn.disabled    = false;
  };

  function showFeedback(el, msg, type) {
    el.textContent   = msg;
    el.className     = `sr-save-feedback sr-save-feedback--inline sr-save-feedback--${type}`;
    el.style.display = 'inline-block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
  }

  /* ══════════════════════════════════════════════════════════
     OVERLAY — GENERACIÓN
  ══════════════════════════════════════════════════════════ */
  const genOverlay = document.getElementById('gen-loading-overlay');
  const genSteps   = ['gs-1','gs-2','gs-3','gs-4','gs-5','gs-6'].map(id => document.getElementById(id));

  if (CFG.currentGenStatus === 'generating') { showGenOverlay(); startGenPolling(); }

  const genForm = document.querySelector('form[action*="generate"]');
  if (genForm) genForm.addEventListener('submit', () => showGenOverlay());

  function showGenOverlay() {
    genOverlay.classList.add('active');
    genSteps.forEach((step, i) => {
      setTimeout(() => {
        if (i > 0 && genSteps[i-1]) { genSteps[i-1].classList.remove('active'); genSteps[i-1].classList.add('done'); }
        if (step) step.classList.add('active');
      }, i * 8000);
    });
  }

  function startGenPolling() {
    const iv = setInterval(async () => {
      try {
        const data = await (await fetch(CFG.genStatusUrl)).json();
        if (data.status === 'ready' || data.status === 'error') { clearInterval(iv); window.location.reload(); }
      } catch (_) {}
    }, 4000);
  }

  /* ══════════════════════════════════════════════════════════
     OVERLAY — DESPLIEGUE
  ══════════════════════════════════════════════════════════ */
  const deployOverlay = document.getElementById('deploy-loading-overlay');
  const DEPLOY_STEPS  = [
    { id:'ds-zip',   at:    0, progress: 10 },
    { id:'ds-unzip', at: 5000, progress: 30 },
    { id:'ds-build', at:15000, progress: 55 },
    { id:'ds-run',   at:90000, progress: 85 },
    { id:'ds-done',  at:    0, progress:100 },
  ];
  const progressBar   = document.getElementById('deploy-progress-bar');
  const progressLabel = document.getElementById('deploy-progress-label');
  const elapsedEl     = document.getElementById('deploy-elapsed');
  let deployTimer = null, deployStart = null, stepTimers = [];

  if (CFG.currentDeployStatus === 'deploying') { showDeployOverlay(); startDeployPolling(); }

  const deployForm = document.getElementById('deploy-form');
  if (deployForm) deployForm.addEventListener('submit', () => showDeployOverlay());

  function showDeployOverlay() {
    deployOverlay.classList.add('active');
    deployStart = Date.now();
    DEPLOY_STEPS.slice(0,-1).forEach((step, i) => {
      stepTimers.push(setTimeout(() => {
        if (i > 0) {
          const p = document.getElementById(DEPLOY_STEPS[i-1].id);
          if (p) { p.classList.remove('active'); p.classList.add('done'); }
        }
        const el = document.getElementById(step.id);
        if (el) el.classList.add('active');
        setProgress(step.progress);
      }, step.at));
    });
    deployTimer = setInterval(() => {
      const s = Math.floor((Date.now() - deployStart) / 1000);
      if (elapsedEl) elapsedEl.textContent =
        `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
    }, 1000);
  }

  function setProgress(pct) {
    if (progressBar)   progressBar.style.width   = pct + '%';
    if (progressLabel) progressLabel.textContent = pct + '%';
  }

  function finishDeployOverlay(success, previewUrl, errorMsg) {
    stepTimers.forEach(t => clearTimeout(t));
    clearInterval(deployTimer);
    if (success) {
      DEPLOY_STEPS.slice(0,-1).forEach(s => {
        const e = document.getElementById(s.id);
        if (e) { e.classList.remove('active'); e.classList.add('done'); }
      });
      const done = document.getElementById('ds-done');
      if (done) done.classList.add('active');
      setProgress(100);
      const t = document.getElementById('deploy-overlay-title');
      if (t) t.textContent = '¡Desplegado con éxito!';
      setTimeout(() => { deployOverlay.classList.remove('active'); window.location.reload(); }, 1800);
    } else {
      deployOverlay.classList.remove('active');
      const ae = document.getElementById('deploy-error-alert');
      const me = document.getElementById('deploy-error-msg');
      const pe = document.getElementById('deploy-status-pill');
      const ve = document.getElementById('deploy-status-value');
      if (me) me.textContent    = errorMsg || 'Error desconocido.';
      if (ae) ae.style.display  = 'flex';
      if (pe) pe.style.display  = '';
      if (ve) ve.textContent    = 'error';
    }
  }

  function startDeployPolling() {
    const iv = setInterval(async () => {
      try {
        const data = await (await fetch(CFG.deployStatusUrl)).json();
        if (data.deploy_status === 'done') {
          clearInterval(iv);
          const pe = document.getElementById('deploy-status-pill');
          const ve = document.getElementById('deploy-status-value');
          const le = document.getElementById('preview-link');
          if (pe) pe.style.display = '';
          if (ve) ve.textContent   = 'done';
          if (le && data.preview_url) { le.href = data.preview_url; le.style.display = ''; }
          finishDeployOverlay(true, data.preview_url);
        }
        if (data.deploy_status === 'error') {
          clearInterval(iv);
          finishDeployOverlay(false, '', data.deploy_error);
        }
      } catch (_) {}
    }, 3000);
  }

  /* ══════════════════════════════════════════════════════════
     INIT
  ══════════════════════════════════════════════════════════ */
  initTree();

})();

