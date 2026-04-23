((Drupal, once) => {
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  Drupal.behaviors.starterNewsletter = {
    attach(context) {
      const forms = once(
        'starter-newsletter',
        context.querySelectorAll('form.c-newsletter__form')
      );
      forms.forEach((form) => {
        let status = form.querySelector('.c-newsletter__status');
        if (!status) {
          status = document.createElement('div');
          status.className = 'c-newsletter__status';
          form.appendChild(status);
        }
        status.setAttribute('aria-live', 'polite');

        const submit = form.querySelector('[type="submit"]');

        const setStatus = (message, isSuccess) => {
          status.textContent = message;
          status.classList.remove('is-success', 'is-error');
          status.classList.add(isSuccess ? 'is-success' : 'is-error');
        };

        form.addEventListener('submit', (e) => {
          e.preventDefault();
          const emailField = form.querySelector('input[type="email"], input[name="email"]');
          const email = emailField ? String(emailField.value || '').trim() : '';
          if (!EMAIL_RE.test(email)) {
            setStatus(Drupal.t('Adresse email invalide.'), false);
            return;
          }

          if (submit) {
            submit.disabled = true;
          }

          const done = (ok) => {
            if (submit) {
              submit.disabled = false;
            }
            if (ok) {
              setStatus(Drupal.t('Inscription confirmée. Merci.'), true);
              form.reset();
            } else {
              setStatus(Drupal.t('Une erreur est survenue. Réessayez.'), false);
            }
          };

          if (form.action) {
            fetch(form.action, {
              method: 'POST',
              body: new FormData(form),
            })
              .then((res) => done(res.ok))
              .catch(() => done(false));
          } else {
            setTimeout(() => done(true), 400);
          }
        });
      });
    },
  };
})(Drupal, once);
