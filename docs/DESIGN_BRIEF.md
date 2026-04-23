# Brief design partagé — Le Guide Santé

Source de vérité pour toutes les sous-tâches (design, templates, JS, contenu). Aligne les noms de classes, tokens, libraries, et structures.

## 1. Identité

- **Titre** : Le Guide Santé
- **Sous-titre** : Tribune du Dr Stéphane Bach
- **Ton éditorial** : direct, clinique, engagé. Phrases courtes, vocabulaire médical précis mais accessible. Pas de langue de bois, pas de "wellness".

## 2. Palette (tokens)

| Token | Hex | Usage |
|---|---|---|
| `--c-ink` | `#0B1F3A` | Bleu nuit — fond hero, footer, titres |
| `--c-ink-2` | `#12304F` | Bleu nuit +1 — cards sombres |
| `--c-accent` | `#00C28C` | Vert techno — CTA, liens actifs, accents |
| `--c-accent-2` | `#00E3A4` | Vert hover |
| `--c-paper` | `#F7F6F1` | Fond clair (crème journal) |
| `--c-paper-2` | `#FFFFFF` | Fond card clair |
| `--c-line` | `#E6E3DA` | Divider clair |
| `--c-muted` | `#5A6676` | Texte secondaire |
| `--c-warn` | `#E0654A` | Alerte / tag controverse |

## 3. Typographie

- **Serif** : Fraunces (variable, 9..144 pt, slnt 0..-10). Titres, dropcaps, citations.
- **Sans** : Inter (variable). Courant, UI, meta.
- **Échelle (clamp)** : h1 `clamp(2.25rem, 2vw + 2rem, 4rem)` · h2 `clamp(1.75rem, 1.2vw + 1.4rem, 2.5rem)` · h3 `clamp(1.25rem, .6vw + 1.1rem, 1.625rem)` · body `1.0625rem` · small `.9rem`.
- **Line-height** : titres 1.1 · body 1.65 · leads 1.5.

## 4. Espace / radius / shadow

- Spacing scale (rem) : `0.25 / 0.5 / 0.75 / 1 / 1.5 / 2 / 3 / 4 / 6 / 8`.
- Radius : `--r-sm: 4px` · `--r-md: 10px` · `--r-lg: 20px` · `--r-pill: 999px`.
- Shadow : `--sh-1: 0 1px 2px rgba(11,31,58,.06)` · `--sh-2: 0 8px 24px rgba(11,31,58,.08)`.

## 5. Grille / breakpoints

- Container max : `1200px`.
- BP : `sm 480` · `md 768` · `lg 1024` · `xl 1280`.
- Mobile-first. Grid CSS 12 col, gap `2rem`.

## 6. 4 piliers (taxonomie `thematique`)

| Slug | Libellé | Couleur d'accent |
|---|---|---|
| `science-preuves` | Science & preuves | `--c-accent` (vert) |
| `clinique-terrain` | Clinique & terrain | `#4A90E2` (bleu ciel) |
| `politique-sante` | Politique de santé | `--c-warn` (orange) |
| `innovations` | Innovations | `#9B6BFF` (violet) |

## 7. Nom des composants (BEM léger, préfixe `c-`)

- `c-header`, `c-nav`, `c-nav__link`, `c-nav__link--active`
- `c-hero`, `c-hero__eyebrow`, `c-hero__title`, `c-hero__lede`, `c-hero__cta`
- `c-pillars`, `c-pillars__item`
- `c-card`, `c-card__meta`, `c-card__title`, `c-card__excerpt`, `c-card__cta`
- `c-tribune`, `c-tribune__byline`, `c-tribune__lede`, `c-tribune__body`, `c-tribune__pullquote`, `c-tribune__sources`
- `c-author`, `c-author__avatar`, `c-author__bio`
- `c-annuaire`, `c-annuaire__row`, `c-annuaire__filter`
- `c-newsletter`, `c-newsletter__form`, `c-newsletter__field`
- `c-footer`, `c-pagination`, `c-tag`, `c-chip`, `c-btn`, `c-btn--primary`, `c-btn--ghost`

Utility classes : `u-container`, `u-grid`, `u-flex`, `u-sr-only`, `u-visually-hidden`.

Modifier by pilier : `c-tag--science-preuves`, etc. (map color via SCSS).

## 8. Structure home (6 sections)

1. **Hero éditorial** — eyebrow "Tribune", titre du dernier édito, lede, bouton "Lire", portrait Dr Bach.
2. **4 piliers** — cartes cliquables vers `/thematique/<slug>`.
3. **Derniers articles** — 6 teasers tribunes (Views `latest_tribunes`).
4. **Travaux scientifiques** — 3 tuiles (BSD, BMN, COMPASS) + CTA `/travaux-scientifiques`.
5. **Annuaire compact** — 4 praticiens en vedette + lien vers annuaire complet (URL préservée).
6. **Newsletter + footer** — form inline + mentions.

## 9. Libraries Drupal exposées

- `starter/global` (auto, dans page.html.twig via hook)
- `starter/nav`
- `starter/filters` (attacher dans template annuaire + liste tribunes)
- `starter/newsletter` (attacher dans block newsletter)
- `starter/smooth-scroll` (auto si `a[href^="#"]` présent)

## 10. Accessibilité

- WCAG AA : contrastes ≥ 4.5:1 pour body, 3:1 pour headings > 18pt.
- `:focus-visible` obligatoire, ring `2px` vert techno.
- Skip-link `.u-sr-only.u-sr-only--focusable`.
- `prefers-reduced-motion: reduce` → désactive smooth-scroll.

## 11. URL & routes préservées

- `/annuaire/*` (annuaire praticiens) — inchangé.
- `/article/*` (anciens articles) — redirects 301 vers `/tribune/<slug>` gérés côté module `leguidesante_content` (optionnel, voir `redirect` module).
- Nouveaux : `/tribune/*`, `/thematique/<slug>`, `/dr-stephane-bach`, `/a-propos`, `/travaux-scientifiques`, `/newsletter`.

## 12. Types de contenu

- **tribune** : title, field_eyebrow (texte), field_lede (texte long résumé), body, field_image (media image), field_thematique (ref taxo), field_sources (texte long formaté), field_pullquote (texte court), field_author (ref user), created/changed.
- **travail_scientifique** : title, field_acronym (texte court : BSD / BMN / COMPASS), field_abstract (texte long), field_image, field_status (liste : "En cours" / "Publié" / "En recrutement"), field_related_tribunes (ref entity node:tribune), field_doi (url).

## 13. Taxonomie

- **thematique** (vocab) : 4 termes Science & preuves / Clinique & terrain / Politique de santé / Innovations. Chaque terme : `field_color_token` (texte court, ex: `--c-accent`), `field_icon` (texte court, slug).

## 14. Views

- `latest_tribunes` — 6 derniers nodes tribune, format teaser, tri par `created DESC`. Page `/tribunes` + bloc "Derniers articles".
- `tribunes_par_thematique` — page `/thematique/%`, filtre contextuel term taxonomy, 12 par page, pagination AJAX.

## 15. Conventions fichiers

- SCSS : `scss/_tokens.scss` (variables CSS), `scss/_mixins.scss`, `scss/_reset.scss`, `scss/_typography.scss`, `scss/components/_<nom>.scss`, `scss/starter.scss` (entry : forward + import).
- CSS compilé : `css/starter.css` (checked in — pas de build pipeline nécessaire).
- Twig : 2 espaces, pas de logique métier.
- JS : vanilla ES2020, `Drupal.behaviors.<name>`, `once('lgs-<name>', ...)`.
