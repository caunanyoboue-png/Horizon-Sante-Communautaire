// JS minimal (sans framework)
// Ici on pourra ajouter plus tard : validation guidée des formulaires, UI notifications, etc.

(() => {
  const body = document.body;

  const navToggle = document.querySelector('[data-nav-toggle]');
  const navOverlay = document.querySelector('[data-nav-overlay]');
  const publicToggle = document.querySelector('[data-public-nav-toggle]');
  const publicPanel = document.querySelector('[data-public-nav-panel]');

  const closeAuthNav = () => body.classList.remove('nav-open');
  const toggleAuthNav = () => body.classList.toggle('nav-open');

  const closePublicNav = () => body.classList.remove('public-nav-open');
  const togglePublicNav = () => body.classList.toggle('public-nav-open');

  if (navToggle) {
    navToggle.addEventListener('click', (e) => {
      e.preventDefault();
      toggleAuthNav();
    });
  }

  if (navOverlay) {
    navOverlay.addEventListener('click', (e) => {
      e.preventDefault();
      closeAuthNav();
    });
  }

  if (publicToggle) {
    publicToggle.addEventListener('click', (e) => {
      e.preventDefault();
      togglePublicNav();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAuthNav();
      closePublicNav();
    }
  });

  if (publicPanel) {
    publicPanel.addEventListener('click', (e) => {
      const target = e.target;
      if (target && target.matches('a')) {
        closePublicNav();
      }
    });
  }
})();
