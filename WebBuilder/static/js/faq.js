document.addEventListener('DOMContentLoaded', () => {

  // ── Acordeón ──
  document.querySelectorAll('.faq-item').forEach(item => {
    item.addEventListener('click', () => {
      item.classList.toggle('open');
    });
  });

  // ── Sidebar: clic fuerza activo inmediatamente ──
  const navItems = document.querySelectorAll('.faq-sidenav__item');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
    });
  });

  // ── Sidebar: scroll actualiza activo ──
  const sections = document.querySelectorAll('.faq-section');

  const observer = new IntersectionObserver((entries) => {
    // De todas las secciones visibles, cogemos la más cercana al top
    const visible = entries
      .filter(e => e.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

    if (visible.length > 0) {
      const id = visible[0].target.id;
      navItems.forEach(i => i.classList.remove('active'));
      const active = document.querySelector(`.faq-sidenav__item[href="#${id}"]`);
      if (active) active.classList.add('active');
    }
  }, {
    threshold: 0,
    rootMargin: '-10% 0px -60% 0px'
  });

  sections.forEach(s => observer.observe(s));

});