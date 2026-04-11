(function () {

  const CFG = window.CV_CONFIG || {};

  let currentPath    = null;
  let originalContent = null;
  let monacoEditor   = null;
  let monacoLoaded   = false;

  const fileContents = {};

  function qs(sel)  { return document.querySelector(sel); }
  function qsa(sel) { return Array.from(document.querySelectorAll(sel)); }

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
    setTimeout(() => { el.style.display = 'none'; }, 3000);
  }

  /* ── ÁRBOL ── */
  function buildTree(paths) {
    const root = {};
    paths.forEach(path => {
      const parts = path.split('/');
      let node = root;
      parts.forEach((part, i) => {
        if (i === parts.length - 1) { node[part] = null; }
        else { if (!node[part]) node[part] = {}; node = node[part]; }
      });
    });
    return root;
  }

  function renderTree(node, container, prefix, depth) {
    const entries = Object.entries(node);
    const folders = entries.filter(([, v]) => v !== null).sort(([a], [b]) => a.localeCompare(b));
    const files   = entries.filter(([, v]) => v === null).sort(([a], [b]) => a.localeCompare(b));

    [...folders, ...files].forEach(([name, value]) => {
      const fullPath = prefix ? `${prefix}/${name}` : name;
      const isFile   = value === null;
      const item     = document.createElement('div');
      item.style.paddingLeft = `${depth * 12}px`;

      if (isFile) {
        item.className      = 'sr-tree__item';
        item.dataset.path   = fullPath;
        item.dataset.content = fileContents[fullPath] || '';
        item.addEventListener('click', () => srSelectFile(item));
        const label = document.createElement('span');
        label.className  = 'sr-tree__name';
        label.textContent = name;
        item.appendChild(label);
      } else {
        item.className = 'sr-tree__folder';
        const header   = document.createElement('div');
        header.className = 'sr-tree__folder-header';
        const arrow    = document.createElement('span');
        arrow.className  = 'sr-tree__arrow';
        arrow.textContent = '▾';
        const label    = document.createElement('span');
        label.className  = 'sr-tree__folder-name';
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
    try { parsed = JSON.parse(dataEl.textContent); }
    catch (e) { console.error('sr-files-data JSON inválido', e); return; }
    const files = parsed.files || [];
    files.forEach(f => { fileContents[f.path] = f.content; });
    const paths = files.map(f => f.path);
    const tree  = buildTree(paths);
    const container = document.getElementById('sr-tree');
    if (container) renderTree(tree, container, '', 0);
  }

  /* ── VISOR ── */
  function srSelectFile(el) {
    qsa('.sr-tree__item').forEach(i => i.classList.remove('sr-tree__item--active'));
    el.classList.add('sr-tree__item--active');

    currentPath     = el.dataset.path;
    originalContent = el.dataset.content;

    document.getElementById('sr-empty').style.display     = 'none';
    document.getElementById('sr-header').style.display    = 'flex';
    document.getElementById('sr-code-wrap').style.display = 'block';
    document.getElementById('sr-filename').textContent    = currentPath;
    document.getElementById('sr-save-feedback').style.display = 'none';

    const lang  = langFromPath(currentPath);
    const codeEl = document.getElementById('sr-code');
    codeEl.className  = `language-${lang}`;
    codeEl.textContent = originalContent;
    if (window.Prism) Prism.highlightElement(codeEl);
  }

  /* ── MONACO ── */
  require.config({
    paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
  });

  function srStartEdit() {
    if (!currentPath) return;
    document.getElementById('sr-modal-filename').textContent     = currentPath;
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
    if (monacoEditor) { monacoEditor.dispose(); monacoEditor = null; }
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
    if (monacoEditor) { monacoEditor.dispose(); monacoEditor = null; }
  }

  async function srSave() {
    if (!monacoEditor) return;
    const content  = monacoEditor.getValue();
    const saveBtn  = document.getElementById('sr-btn-save');
    const feedback = document.getElementById('sr-save-feedback-modal');
    saveBtn.textContent = 'Guardando…';
    saveBtn.disabled    = true;
    try {
      const res  = await fetch(CFG.updateFileUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrfToken },
        body: JSON.stringify({ path: currentPath, content }),
      });
      const data = await res.json();
      if (data.ok) {
        fileContents[currentPath] = content;
        const item = document.querySelector(`.sr-tree__item[data-path="${CSS.escape(currentPath)}"]`);
        if (item) item.dataset.content = content;
        originalContent = content;
        const lang   = langFromPath(currentPath);
        const codeEl = document.getElementById('sr-code');
        codeEl.className  = `language-${lang}`;
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
    saveBtn.disabled    = false;
  }

  /* ── INIT ── */
  function init() {
    initTree();

    const editBtn   = document.getElementById('sr-btn-edit');
    const cancelBtn = document.getElementById('sr-btn-cancel');
    const saveBtn   = document.getElementById('sr-btn-save');
    if (editBtn)   editBtn.addEventListener('click', srStartEdit);
    if (cancelBtn) cancelBtn.addEventListener('click', srCancelEdit);
    if (saveBtn)   saveBtn.addEventListener('click', srSave);

    document.addEventListener('keydown', e => {
      const modal = document.getElementById('sr-modal');
      if (e.key === 'Escape' && modal && modal.classList.contains('sr-modal--open')) {
        srCancelEdit();
      }
    });
  }

  init();
})();