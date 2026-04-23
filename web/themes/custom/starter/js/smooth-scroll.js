((Drupal, once) => {
  Drupal.behaviors.starterSmoothScroll = {
    attach(context) {
      const links = once(
        'starter-smooth-scroll',
        context.querySelectorAll('a[href^="#"]')
      );
      links.forEach((link) => {
        const href = link.getAttribute('href');
        if (!href || href === '#') {
          return;
        }
        link.addEventListener('click', (e) => {
          const target = href.slice(1);
          if (!target) {
            return;
          }
          let el = null;
          try {
            el = document.getElementById(target) || document.querySelector(href);
          } catch (_) {
            el = null;
          }
          if (!el) {
            return;
          }
          e.preventDefault();
          const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          el.scrollIntoView({
            behavior: reduce ? 'auto' : 'smooth',
            block: 'start',
          });
          if (window.history && typeof window.history.pushState === 'function') {
            window.history.pushState(null, '', href);
          }
        });
      });
    },
  };
})(Drupal, once);
