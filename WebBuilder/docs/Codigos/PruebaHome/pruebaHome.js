const panels = ['weather','pokemon','countries','posts','sites','new'];
const sbMap  = { weather:'sb-weather', pokemon:'sb-pokemon', countries:'sb-countries', posts:'sb-posts', sites:'sb-sites', new:'sb-new' };
const botMap = { weather:'bot-weather', pokemon:'bot-pokemon', countries:'bot-countries', posts:'bot-posts', sites:'bot-sites', new:'bot-new' };

function switchTab(tabEl, id) {
  panels.forEach(p => {
    const panel = document.getElementById('panel-'+p);
    const bot   = document.getElementById(botMap[p]);
    if (panel) panel.classList.remove('active');
    if (bot)   bot.style.display = 'none';
  });
  document.querySelectorAll('.vsc-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.sidebar-item').forEach(t => t.classList.remove('active'));

  const panel = document.getElementById('panel-'+id);
  const bot   = document.getElementById(botMap[id]);
  if (panel) panel.classList.add('active');
  if (bot)   bot.style.display = 'flex';
  if (tabEl) tabEl.classList.add('active');
  const sbEl = document.getElementById(sbMap[id]);
  if (sbEl) sbEl.classList.add('active');
}

function toggleField(card, countId, total) {
  card.classList.toggle('selected');
  const panel   = card.closest('.panel-view');
  const count   = panel.querySelectorAll('.field-card.selected').length;
  const counter = document.getElementById(countId);
  if (counter) counter.textContent = count;
}

function fillAndGo(url) {
  document.getElementById('new-url').value = url;
  setTimeout(() => {
    const weatherTab = document.querySelector('[data-tab="weather"]');
    switchTab(weatherTab, 'weather');
  }, 300);
}

function goAnalyze() {
  const url = document.getElementById('new-url').value.trim();
  if (!url) return;
  const weatherTab = document.querySelector('[data-tab="weather"]');
  switchTab(weatherTab, 'weather');
}

function handleDragOver(e) {
  e.preventDefault();
  const dz = document.getElementById('drop-zone');
  dz.style.borderColor = 'rgba(255,255,255,0.28)';
  dz.style.background  = 'rgba(255,255,255,0.03)';
}
function handleDragLeave(e) {
  const dz = document.getElementById('drop-zone');
  dz.style.borderColor = '';
  dz.style.background  = '';
}
function handleDrop(e) {
  e.preventDefault();
  handleDragLeave(e);
  const file = e.dataTransfer.files[0];
  if (file) showFileName(file.name);
}
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) showFileName(file.name);
}
function showFileName(name) {
  const el = document.getElementById('drop-filename');
  el.textContent = '📄 ' + name;
  el.style.display = 'inline-block';
  setTimeout(() => {
    const weatherTab = document.querySelector('[data-tab="weather"]');
    switchTab(weatherTab, 'weather');
  }, 600);
}

// ===== Secciones extra =====

// ── Provider tabs ──
function switchProvider(id) {
  ['openrouter','groq','ollama'].forEach(p => {
    document.getElementById('prov-'+p)?.classList.remove('active');
    const f = document.getElementById('fields-'+p);
    if (f) f.style.display = 'none';
  });
  document.getElementById('prov-'+id)?.classList.add('active');
  const fields = document.getElementById('fields-'+id);
  if (fields) fields.style.display = 'block';
}

// ── Steps ──
function setStep(i) {
  document.querySelectorAll('.how-step').forEach((s,j) => {
    s.classList.toggle('active', i === j);
  });
}

// ── N8N flows ──
function switchFlow(id) {
  const flowDiagram = document.querySelector('.flow-diagram');
  if (!flowDiagram) return;
  const flowTabs = flowDiagram.querySelectorAll('.flow-tabs .flow-tab');
  const flowPanels = flowDiagram.querySelectorAll('.flow-content');
  flowTabs.forEach(t => t.classList.remove('active'));
  flowPanels.forEach(c => c.classList.remove('active'));
  const activeTab = Array.from(flowTabs).find(t => t.textContent.trim().toLowerCase() === id.toLowerCase());
  if (activeTab) activeTab.classList.add('active');
  document.getElementById('flow-' + id)?.classList.add('active');
}

// ── LLM selection ──
function selectLLM(el, panelId) {
  document.querySelectorAll('.llm-item, .llm-custom').forEach(i => i.classList.remove('active'));
  document.querySelectorAll('.llm-detail, .llm-custom-detail').forEach(d => {
    d.classList.remove('active');
    d.style.display = 'none';
  });
  el.classList.add('active');
  const panel = document.getElementById(panelId);
  if (panel) {
    panel.style.display = 'flex';
    panel.classList.add('active');
  }
}

// init LLM display
document.querySelectorAll('.llm-detail, .llm-custom-detail').forEach(d => {
  if (!d.classList.contains('active')) d.style.display = 'none';
});