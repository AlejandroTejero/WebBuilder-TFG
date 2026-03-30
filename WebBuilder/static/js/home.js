document.addEventListener('DOMContentLoaded', () => {
  const panels = ['weather', 'pokemon', 'countries', 'posts', 'sites', 'new'];
  const sbMap = {
    weather: 'sb-weather',
    pokemon: 'sb-pokemon',
    countries: 'sb-countries',
    posts: 'sb-posts',
    sites: 'sb-sites',
    new: 'sb-new',
  };
  const botMap = {
    weather: 'bot-weather',
    pokemon: 'bot-pokemon',
    countries: 'bot-countries',
    posts: 'bot-posts',
    sites: 'bot-sites',
    new: 'bot-new',
  };

  window.switchTab = function (tabEl, id) {
    panels.forEach((p) => {
      const panel = document.getElementById(`panel-${p}`);
      const bot = document.getElementById(botMap[p]);
      if (panel) panel.classList.remove('active');
      if (bot) bot.style.display = 'none';
    });

    document.querySelectorAll('.wb-vsc-tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.wb-sidebar-item').forEach((t) => t.classList.remove('active'));

    const panel = document.getElementById(`panel-${id}`);
    const bot = document.getElementById(botMap[id]);

    if (panel) panel.classList.add('active');
    if (bot) bot.style.display = 'flex';
    if (tabEl) tabEl.classList.add('active');

    const sbEl = document.getElementById(sbMap[id]);
    if (sbEl) sbEl.classList.add('active');
  };

  window.toggleField = function (card, countId) {
    card.classList.toggle('selected');
    const panel = card.closest('.wb-panel-view');
    if (!panel) return;
    const count = panel.querySelectorAll('.wb-field-card.selected').length;
    const counter = document.getElementById(countId);
    if (counter) counter.textContent = count;
  };

  window.fillAndGo = function (url) {
    const input = document.getElementById('new-url');
    if (input) input.value = url;
    setTimeout(() => {
      const weatherTab = document.querySelector('.wb-vsc-tab[data-tab="weather"]');
      window.switchTab(weatherTab, 'weather');
    }, 300);
  };

  window.goAnalyze = function () {
    const input = document.getElementById('new-url');
    if (!input || !input.value.trim()) return;
    const weatherTab = document.querySelector('.wb-vsc-tab[data-tab="weather"]');
    window.switchTab(weatherTab, 'weather');
  };

  window.handleDragOver = function (e) {
    e.preventDefault();
    const dz = document.getElementById('drop-zone');
    if (!dz) return;
    dz.style.borderColor = 'rgba(255,255,255,0.28)';
    dz.style.background = 'rgba(255,255,255,0.03)';
  };

  window.handleDragLeave = function () {
    const dz = document.getElementById('drop-zone');
    if (!dz) return;
    dz.style.borderColor = '';
    dz.style.background = '';
  };

  window.handleDrop = function (e) {
    e.preventDefault();
    window.handleDragLeave();
    const file = e.dataTransfer.files[0];
    if (file) showFileName(file.name);
  };

  window.handleFileSelect = function (e) {
    const file = e.target.files[0];
    if (file) showFileName(file.name);
  };

  function showFileName(name) {
    const el = document.getElementById('drop-filename');
    if (!el) return;
    el.textContent = `📄 ${name}`;
    el.style.display = 'inline-block';

    setTimeout(() => {
      const weatherTab = document.querySelector('.wb-vsc-tab[data-tab="weather"]');
      window.switchTab(weatherTab, 'weather');
    }, 600);
  }

  window.setStep = function (index) {
    document.querySelectorAll('.wb-how-step').forEach((step, i) => {
      step.classList.toggle('active', i === index);
    });
  };

  document.querySelectorAll('.wb-flow-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      const flowId = tab.dataset.flow;

      document.querySelectorAll('.wb-flow-tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll('.wb-flow-content').forEach((c) => c.classList.remove('active'));

      tab.classList.add('active');
      const target = document.getElementById(`flow-${flowId}`);
      if (target) target.classList.add('active');
    });
  });

  document.querySelectorAll('.wb-llm-item, .wb-llm-custom').forEach((item) => {
    item.addEventListener('click', () => {
      const panelId = item.dataset.panel;

      document.querySelectorAll('.wb-llm-item, .wb-llm-custom').forEach((el) => el.classList.remove('active'));
      document.querySelectorAll('.wb-llm-detail, .wb-llm-custom-detail').forEach((panel) => {
        panel.classList.remove('active');
      });

      item.classList.add('active');
      const panel = document.getElementById(panelId);
      if (panel) panel.classList.add('active');
    });
  });

  document.querySelectorAll('.wb-provider-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      const provider = tab.dataset.provider;

      document.querySelectorAll('.wb-provider-tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll('.wb-provider-fields').forEach((f) => f.classList.remove('active'));

      tab.classList.add('active');
      const fields = document.getElementById(`fields-${provider}`);
      if (fields) fields.classList.add('active');
    });
  });

  document.querySelectorAll('.wb-home a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
});