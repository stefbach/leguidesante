(() => {
  const toggle = document.getElementById('c-nav-toggle');
  const nav = document.querySelector('.c-nav');
  const header = document.querySelector('.c-header');
  if (!toggle || !nav) return;

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
    nav.classList.contains('is-open') ? close() : open();
  });

  document.addEventListener('click', (e) => {
    if (!nav.classList.contains('is-open')) return;
    if (header && !header.contains(e.target)) close();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) {
      close();
      toggle.focus();
    }
  });
})();

(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const href = a.getAttribute('href');
    if (href === '#' || href.length < 2) return;
    const target = document.querySelector(href);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    history.pushState(null, '', href);
  });
})();

(() => {
  const groups = document.querySelectorAll('[data-filter-group]');
  if (!groups.length) return;
  const state = {};
  let timer = null;

  const apply = (scope) => {
    const items = scope.querySelectorAll('[data-filterable]');
    items.forEach((item) => {
      const match = Object.entries(state).every(([key, val]) => {
        if (!val) return true;
        return item.dataset[key] === val;
      });
      item.hidden = !match;
    });
  };

  groups.forEach((group) => {
    const key = group.dataset.filterGroup;
    const scope = group.closest('[data-filter-scope]') || document;
    state[key] = '';
    group.querySelectorAll('[data-filter-value]').forEach((chip) => {
      chip.addEventListener('click', () => {
        group.querySelectorAll('[data-filter-value]').forEach((c) => c.classList.remove('is-active'));
        chip.classList.add('is-active');
        state[key] = chip.dataset.filterValue;
        clearTimeout(timer);
        timer = setTimeout(() => apply(scope), 80);
      });
    });
  });
})();

(() => {
  const forms = document.querySelectorAll('form.c-newsletter__form');
  if (!forms.length) return;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  forms.forEach((form) => {
    const status = form.querySelector('.c-newsletter__status') || (() => {
      const p = document.createElement('p');
      p.className = 'c-newsletter__status';
      p.setAttribute('aria-live', 'polite');
      form.appendChild(p);
      return p;
    })();
    const submit = form.querySelector('[type="submit"]');
    const email = form.querySelector('input[type="email"]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      status.classList.remove('is-success', 'is-error');
      if (!email || !re.test(email.value)) {
        status.textContent = 'Email invalide.';
        status.classList.add('is-error');
        return;
      }
      submit.disabled = true;
      try {
        if (form.action && form.action !== window.location.href) {
          await fetch(form.action, { method: 'POST', body: new FormData(form) });
        } else {
          await new Promise((r) => setTimeout(r, 400));
        }
        status.textContent = 'Merci. Vous recevrez la prochaine tribune.';
        status.classList.add('is-success');
        form.reset();
      } catch {
        status.textContent = 'Erreur. Réessayez dans un instant.';
        status.classList.add('is-error');
      } finally {
        submit.disabled = false;
      }
    });
  });
})();
