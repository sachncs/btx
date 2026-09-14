# btx — Product Site

The premium product marketing site for [btx](https://github.com/sachncs/btx),
a pure-Python toolkit for the Bitcoin secp256k1 stack.

Built with [Astro](https://astro.build) and [Tailwind CSS](https://tailwindcss.com),
deployed to [GitHub Pages](https://pages.github.com/).

## Stack

| Layer        | Choice                                       |
| ------------ | -------------------------------------------- |
| Framework    | Astro 4 (static output, islands architecture)|
| Styling      | Tailwind CSS 3 with custom design tokens     |
| Typography   | Inter + JetBrains Mono via Google Fonts      |
| Animation    | CSS keyframes + IntersectionObserver         |
| Deployment   | GitHub Actions → GitHub Pages                |

## Develop

```bash
cd site
npm install
npm run dev          # local dev server (http://localhost:4321/btx)
npm run build        # production build → site/dist
npm run preview      # preview the production build
```

## Capture screenshots (optional)

The `scripts/screenshot.mjs` helper uses puppeteer-core to capture
multi-viewport screenshots for QA:

```bash
node scripts/screenshot.mjs http://localhost:4321/btx/ out.png 1440 900
```

## Project layout

```
site/
├── astro.config.mjs      Astro config (base path /btx, GitHub Pages URL)
├── tailwind.config.cjs   Design tokens, custom utilities, animations
├── public/               Static assets served as-is
│   ├── favicon.svg
│   └── og-image.svg
└── src/
    ├── layouts/          Base HTML layout with SEO, fonts, meta
    ├── components/       Nav, Hero, Features, Code, Architecture,
    │                     Security, Metrics, UseCases, CTA, Footer
    ├── pages/            /index.astro (single-page experience)
    └── styles/global.css Design tokens, components, utilities
```

## Deployment

Every push to `master` that touches `site/**` (or this workflow file)
triggers `.github/workflows/deploy-site.yml`, which:

1. Installs dependencies in `site/`
2. Builds to `site/dist/`
3. Publishes the artifact to GitHub Pages

The site is served at <https://sachncs.github.io/btx/>.

## Design system

- **Background**: deep ink (`#060a0d`) with subtle radial glows
- **Accent**: signature emerald (`#5fd0a4` → `#7ce2c8`) — matches the
  bespoke `btx` logo curve
- **Type scale**: clamp() based fluid typography, tightest letter
  spacing on display sizes
- **Spacing**: 8px rhythm, generous `py-24 sm:py-32` between sections
- **Cards**: hairline borders + spotlight pointer tracking + subtle
  lift on hover
- **Motion**: staggered fade-up reveals via IntersectionObserver;
  reduced-motion respected