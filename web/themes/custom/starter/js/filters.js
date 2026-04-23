((Drupal, once) => {
  const debounce = (fn, delay) => {
    let t = null;
    return (...args) => {
      if (t) {
        clearTimeout(t);
      }
      t = setTimeout(() => fn(...args), delay);
    };
  };

  Drupal.behaviors.starterFilters = {
    attach(context) {
      const containers = once(
        'starter-filters',
        context.querySelectorAll('.c-annuaire, .c-cards-grid')
      );
      containers.forEach((container) => {
        const groups = container.querySelectorAll('.c-chips[data-filter-group]');
        if (!groups.length) {
          return;
        }
        const items = container.querySelectorAll('.c-card');
        if (!items.length) {
          return;
        }

        const activeFilters = {};
        groups.forEach((group) => {
          activeFilters[group.dataset.filterGroup] = '';
        });

        const apply = debounce(() => {
          items.forEach((item) => {
            let match = true;
            for (const key in activeFilters) {
              const val = activeFilters[key];
              if (!val) {
                continue;
              }
              if (item.dataset[key] !== val) {
                match = false;
                break;
              }
            }
            if (match) {
              item.removeAttribute('hidden');
            } else {
              item.setAttribute('hidden', '');
            }
          });
        }, 80);

        groups.forEach((group) => {
          const groupKey = group.dataset.filterGroup;
          const chips = group.querySelectorAll('.c-chip');
          chips.forEach((chip) => {
            chip.addEventListener('click', (e) => {
              e.preventDefault();
              const value = chip.dataset.filterValue || '';
              chips.forEach((c) => c.classList.remove('is-active'));
              chip.classList.add('is-active');
              activeFilters[groupKey] = value;
              apply();
            });
          });
        });
      });
    },
  };
})(Drupal, once);
