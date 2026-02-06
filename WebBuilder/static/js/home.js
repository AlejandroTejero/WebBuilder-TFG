
document.addEventListener('DOMContentLoaded', function() {
  const faqItems = document.querySelectorAll('.faq-item');
  
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    
    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');
      
      // Cerrar todas
      faqItems.forEach(otherItem => {
        otherItem.classList.remove('active');
      });
      
      // Abrir la clickeada si no estaba abierta
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
});