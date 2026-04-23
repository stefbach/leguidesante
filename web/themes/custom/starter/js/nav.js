((Drupal, once) => {
  Drupal.behaviors.starterNav = {
    attach(context) {
      const toggles = once('starter-nav', context.querySelectorAll('#c-nav-toggle'));
      toggles.forEach((toggle) => {
        const header = document.querySelector('.c-header');
        const nav = document.querySelector('.c-nav');
        if (!nav || !header) {
          return;
        }

        const close = () => {
          nav.classList.remove('is-open');
          toggle.setAttribute('aria-expanded', 'false');
        };

        const open = () => {
          nav.classList.add('is-open');
          toggle.setAttribute('aria-expanded', 'true');
        };

        toggle.addEventListener('click', (e) => {
          e.stopPropagation();
          if (nav.classList.contains('is-open')) {
            close();
          } else {
            open();
          }
        });

        document.addEventListener('click', (e) => {
          if (!nav.classList.contains('is-open')) {
            return;
          }
          if (!header.contains(e.target)) {
            close();
          }
        });

        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && nav.classList.contains('is-open')) {
            close();
            toggle.focus();
          }
        });
      });
    },
  };
})(Drupal, once);
