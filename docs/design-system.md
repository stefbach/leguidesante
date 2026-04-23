# Design system — Le Guide Santé

Référence développeur pour le thème `starter`. Source de vérité tokens : `web/themes/custom/starter/scss/_tokens.scss`.

## 1. Palette

| Token | Hex | Swatch | Usage |
|---|---|---|---|
| `--c-ink` | `#0B1F3A` | ![#0B1F3A](https://placehold.co/32x24/0B1F3A/0B1F3A.png) | Bleu nuit. Hero, footer, titres, texte corps |
| `--c-ink-2` | `#12304F` | ![#12304F](https://placehold.co/32x24/12304F/12304F.png) | Bleu nuit +1. Cards sombres, hover |
| `--c-accent` | `#00C28C` | ![#00C28C](https://placehold.co/32x24/00C28C/00C28C.png) | Vert techno. CTA, liens, accents |
| `--c-accent-2` | `#00E3A4` | ![#00E3A4](https://placehold.co/32x24/00E3A4/00E3A4.png) | Vert hover |
| `--c-paper` | `#F7F6F1` | ![#F7F6F1](https://placehold.co/32x24/F7F6F1/F7F6F1.png) | Fond clair (crème journal) |
| `--c-paper-2` | `#FFFFFF` | ![#FFFFFF](https://placehold.co/32x24/FFFFFF/FFFFFF.png) | Fond card clair |
| `--c-line` | `#E6E3DA` | ![#E6E3DA](https://placehold.co/32x24/E6E3DA/E6E3DA.png) | Divider clair |
| `--c-muted` | `#5A6676` | ![#5A6676](https://placehold.co/32x24/5A6676/5A6676.png) | Texte secondaire |
| `--c-warn` | `#E0654A` | ![#E0654A](https://placehold.co/32x24/E0654A/E0654A.png) | Alerte, tag controverse |

### Accents par pilier

| Pilier | Token | Hex |
|---|---|---|
| Science & preuves | `--c-pilier-science` | `#00C28C` |
| Clinique & terrain | `--c-pilier-clinique` | `#4A90E2` |
| Politique de santé | `--c-pilier-politique` | `#E0654A` |
| Innovations | `--c-pilier-innovations` | `#9B6BFF` |

Contrastes vérifiés WCAG AA :
- `--c-ink` sur `--c-paper` : 14.1:1 (AAA body)
- `--c-accent` sur `--c-ink` : 6.8:1 (AA CTA)
- `--c-muted` sur `--c-paper` : 4.7:1 (AA body)

## 2. Typographie

- **Fraunces** (variable, opsz 9..144, wght 300..900, SOFT 0..100) — serif éditorial
- **Inter** (400/500/600/700) — sans UI

| Rôle | Token | Fallback |
|---|---|---|
| Titres, citations, dropcap | `--ff-serif` | Fraunces, Georgia, Times, serif |
| Body, UI, meta | `--ff-sans` | Inter, system-ui, -apple-system, Segoe UI, Roboto |

### Échelle (clamp, fluid)

| Rôle | Token | Valeur |
|---|---|---|
| h1 | `--fs-h1` | `clamp(2.25rem, 2vw + 2rem, 4rem)` |
| h2 | `--fs-h2` | `clamp(1.75rem, 1.2vw + 1.4rem, 2.5rem)` |
| h3 | `--fs-h3` | `clamp(1.25rem, .6vw + 1.1rem, 1.625rem)` |
| body | `--fs-body` | `1.0625rem` |
| lede | `--fs-lede` | `clamp(1.125rem, .4vw + 1rem, 1.375rem)` |
| small | `--fs-small` | `.9rem` |

Line-height : titres `1.1` · body `1.65` · lede `1.5`.

## 3. Espacement, radius, shadow

Échelle `--sp-1..10` : 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px, 128px.

Radius : `--r-sm: 4px` · `--r-md: 10px` · `--r-lg: 20px` · `--r-pill: 999px`.

Shadow : `--sh-1` (élément flottant léger) · `--sh-2` (card hover) · `--sh-3` (modal/overlay).

## 4. Grille et breakpoints

- Container : `max-width: 1200px`, padding inline fluide.
- Breakpoints (SCSS) : `$bp-sm 480` · `$bp-md 768` · `$bp-lg 1024` · `$bp-xl 1280`.
- Grid CSS 12 col, gap `--grid-gap: 2rem`.

Mobile-first strict : tout composant doit être lisible dès 375px.

## 5. Composants

### Header
```html
<header class="c-header">
  <div class="c-header__brand">
    <a href="/"><img src="/logo.svg" alt="Le Guide Santé"></a>
  </div>
  <nav class="c-nav" aria-label="Principal">
    <button id="c-nav-toggle" aria-expanded="false">Menu</button>
    <ul class="c-nav__list">
      <li><a class="c-nav__link c-nav__link--active" href="/tribunes">Tribunes</a></li>
    </ul>
  </nav>
</header>
```

### Hero éditorial
```html
<section class="c-hero">
  <div class="c-hero__body">
    <span class="c-hero__eyebrow">Tribune · Science & preuves</span>
    <h1 class="c-hero__title">Titre éditorial</h1>
    <p class="c-hero__lede">Le chapô d'accroche, italique, serif.</p>
    <a class="c-btn c-btn--primary" href="...">Lire la tribune</a>
  </div>
  <img class="c-hero__portrait" src="..." alt="Dr Bach">
</section>
```

### 4 piliers
```html
<section class="c-pillars">
  <a class="c-pillars__item" href="/thematique/science-preuves" data-pilier="science-preuves">
    <svg class="c-icon">…</svg>
    <h3>Science & preuves</h3>
    <p>Blurb 1 ligne.</p>
  </a>
</section>
```

### Card tribune (teaser)
```html
<article class="c-card" data-thematique="science-preuves">
  <a href="/tribune/slug" class="c-card__link">
    <img class="c-card__image" src="..." alt="">
    <div class="c-card__body">
      <span class="c-tag c-tag--science-preuves">Science & preuves</span>
      <div class="c-card__meta">23 avr. 2026 · 6 min</div>
      <h3 class="c-card__title">Titre de la tribune</h3>
      <p class="c-card__excerpt">Lede tronqué…</p>
      <span class="c-card__cta">Lire</span>
    </div>
  </a>
</article>
```

### Tribune (full)
```html
<article class="c-tribune">
  <div class="c-tribune__byline">
    <img class="c-tribune__avatar" src="...">
    <span>Dr Stéphane Bach</span>
    <time>23 avril 2026</time>
    <span>6 min</span>
  </div>
  <h1>Titre</h1>
  <p class="c-tribune__lede lede">Chapô italique.</p>
  <div class="c-tribune__body">…corps…</div>
  <blockquote class="c-tribune__pullquote">Citation forte.</blockquote>
  <details class="c-tribune__sources"><summary>Sources</summary>…</details>
</article>
```

### Annuaire compact
```html
<section class="c-annuaire">
  <div class="c-chips" data-filter-group="specialite">
    <button class="c-chip is-active" data-filter-value="">Tous</button>
    <button class="c-chip" data-filter-value="cardio">Cardiologie</button>
  </div>
  <ul class="c-annuaire__list">
    <li class="c-annuaire__row" data-specialite="cardio">…</li>
  </ul>
</section>
```

### Newsletter
```html
<form class="c-newsletter__form" action="/newsletter/subscribe" method="post">
  <label class="u-sr-only" for="nl-email">Email</label>
  <input id="nl-email" class="c-newsletter__field" type="email" name="email" required>
  <button class="c-btn c-btn--primary" type="submit">S'abonner</button>
  <p class="c-newsletter__status" aria-live="polite"></p>
</form>
```

### Boutons
- `.c-btn` (base)
- `.c-btn--primary` — fond vert, texte bleu nuit
- `.c-btn--ghost` — bord blanc sur bleu nuit
- `.c-btn--dark` — bleu nuit sur clair

### Tags
- `.c-tag` (base, pill)
- `.c-tag--science-preuves` · `.c-tag--clinique-terrain` · `.c-tag--politique-sante` · `.c-tag--innovations`

### Utilities
- `.u-container` — wrap large
- `.u-grid`, `.u-grid--2`, `.u-grid--3`, `.u-grid--4` — CSS grid responsive
- `.u-flex`, `.u-flex-between`, `.u-flex-center`
- `.u-stack-4`, `.u-stack-6` — rythme vertical (margin-top enfants)
- `.u-sr-only`, `.u-sr-only--focusable` — skip-link, accessible
- `.u-lede`, `.u-dropcap`, `.u-small`

## 6. Libraries Drupal (dans `starter.libraries.yml`)

- `starter/global` — auto-chargée via `starter.info.yml` (CSS + nav + smooth-scroll)
- `starter/nav` — toggle menu mobile
- `starter/filters` — chips filtre annuaire / grid
- `starter/newsletter` — submit form async
- `starter/smooth-scroll` — anchor links `a[href^="#"]`

Usage Twig : `{{ attach_library('starter/filters') }}` dans le template qui en a besoin.

## 7. Accessibilité

- `:focus-visible` ring vert 2px (token `--focus-ring-color`) sur tous les interactifs.
- `.u-sr-only--focusable` pour skip-link en haut de `page.html.twig`.
- Contrastes ≥ 4.5:1 pour body, ≥ 3:1 pour headings > 18pt.
- `prefers-reduced-motion: reduce` désactive animations et `scroll-behavior: smooth`.
- Icônes SVG décoratives : `aria-hidden="true"` + `focusable="false"`.
- Formulaires : chaque `input` a un `<label>` explicite (peut être `.u-sr-only`).

## 8. Build

Le SCSS est compilé vers `css/starter.css` (compressé, ~36 KB). Pour recompiler :

```bash
npx sass web/themes/custom/starter/scss/starter.scss \
         web/themes/custom/starter/css/starter.css \
         --style=compressed --no-source-map
```

Le fichier CSS compilé est commité — pas de pipeline de build requis côté Drupal.

## 9. Conventions

- **BEM léger**, préfixe `c-` pour composants, `u-` pour utilities.
- **Modifiers** via classes `c-xxx--yyy`, **états** via `.is-active` / `.is-open` / `.is-loading`.
- **Data attributes** pour filtrage et variantes dynamiques (`data-pilier`, `data-specialite`).
- Pas de styles inline sauf cas exceptionnels (background-image de card).
- `!important` uniquement sur `.u-sr-only` et reset reduced-motion.
