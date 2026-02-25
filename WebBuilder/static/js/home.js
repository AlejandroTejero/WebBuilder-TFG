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
  // Añade clase visible a elementos cuando entran en el viewport
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

});
