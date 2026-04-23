function animateCounter(el, target, duration = 2000) {
  const start = 0;
  const step = target / (duration / 16);
  let current = start;
  const timer = setInterval(() => {
    current += step;
    if (current >= target) { 
        current = target; 
        clearInterval(timer); 
    }
    el.textContent = Math.floor(current).toLocaleString() + (el.dataset.suffix || '');
  }, 16);
}

document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll('.stat-number');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const targetValue = parseInt(el.dataset.target, 10);
        if(!el.classList.contains('animated')) {
            animateCounter(el, targetValue);
            el.classList.add('animated');
        }
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => observer.observe(counter));
});
