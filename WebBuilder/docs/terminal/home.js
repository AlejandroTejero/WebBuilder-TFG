/**
 * WebBuilder — Home (home.js)
 * FAQ accordion + animaciones de entrada al hacer scroll.
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── FAQ ACCORDION ─────────────────────────────────────────────────
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');

    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Cerrar todas
      faqItems.forEach(other => other.classList.remove('active'));

      // Abrir la clickeada si no estaba abierta
      if (!isActive) item.classList.add('active');
    });
  });

  // ── FADE-IN AL HACER SCROLL ───────────────────────────────────────
  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll(
    '.step-card, .feature-card, .ai-card, .n8n-usecase, .personal-item, .faq-item'
  ).forEach((el, i) => {
    el.style.transitionDelay = `${(i % 4) * 60}ms`;
    el.classList.add('scroll-fade');
    observer.observe(el);
  });

  // ── SMOOTH SCROLL para los links de ancla ─────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── TERMINAL — líneas aparecen desde abajo, altura fija ──────────
  const scrollEl = document.getElementById('terminal-scroll');

  if (scrollEl) {
    const MAX_LINES = 13; // Cuántas líneas caben visualmente en los 260px

    const lines = [
      { text: '# Analizando dataset...',                        color: '#64748b' },
      { text: '→ Formato: JSON',                                color: '#86efac' },
      { text: '→ Colección: products[20]',                      color: '#86efac' },
      { text: '→ Campos: id, title, price, category, rating',   color: '#86efac' },
      { text: '',                                                color: '' },
      { text: '# Generando schema con IA...',                   color: '#64748b' },
      { text: '✦ site_type:  catalog',                          color: '#c4b5fd' },
      { text: '✦ site_title: Products Store',                   color: '#c4b5fd' },
      { text: '✦ fields:     title → Nombre',                   color: '#c4b5fd' },
      { text: '              price → Precio',                   color: '#c4b5fd' },
      { text: '',                                                color: '' },
      { text: '# Generando models.py...',                       color: '#64748b' },
      { text: 'class Item(models.Model):',                      color: '#93c5fd' },
      { text: '    title    = CharField(max_length=500)',        color: '#e2e8f0' },
      { text: '    price    = DecimalField(...)',                color: '#e2e8f0' },
      { text: '    category = CharField(max_length=500)',        color: '#e2e8f0' },
      { text: '',                                                color: '' },
      { text: '# Generando views.py...',                        color: '#64748b' },
      { text: 'def catalog(request):',                          color: '#93c5fd' },
      { text: '    items = Item.objects.all()',                  color: '#e2e8f0' },
      { text: '    return render(request, "catalog.html", ...)', color: '#e2e8f0' },
      { text: '',                                                color: '' },
      { text: '✔ 14 archivos generados. Listo para descargar.', color: '#86efac' },
    ];

    let idx = 0;

    function addLine() {
      if (idx >= lines.length) {
        // Pausa 3s y reinicia
        setTimeout(() => {
          scrollEl.innerHTML = '';
          idx = 0;
          setTimeout(addLine, 400);
        }, 3000);
        return;
      }

      const { text, color } = lines[idx];
      idx++;

      const span = document.createElement('span');
      span.className = 'mockup-terminal__line';
      span.style.color = color || '#e2e8f0';
      span.textContent = text === '' ? '\u00a0' : text; // línea vacía → espacio

      scrollEl.appendChild(span);

      // Si hay demasiadas líneas, eliminar la primera (efecto scroll real)
      const allLines = scrollEl.querySelectorAll('.mockup-terminal__line');
      if (allLines.length > MAX_LINES) {
        allLines[0].remove();
      }

      // Delay entre líneas: más larga tras comentarios o líneas vacías
      const delay = text === '' ? 120 : text.startsWith('#') ? 500 : text.startsWith('✔') ? 200 : 90;
      setTimeout(addLine, delay);
    }

    setTimeout(addLine, 900);
  }

});

