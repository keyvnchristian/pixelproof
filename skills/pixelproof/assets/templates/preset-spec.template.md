# Pixelproof presets — design spec

> Generated from `assets/presets/gallery/`. The rendered pages in `gallery/build/` are the source of truth: `<page>--<preset>.html`, plus `index.html` with page and preset switchers.

## What the presets are
Three original visual systems that share one component stylesheet. A preset is a set of CSS custom properties on `[data-preset="…"]`. The components never change between presets; only the tokens do.

| Preset | Use it for | Character |
|---|---|---|
| `lumen` | Product UI: dashboards, settings, forms, files, auth | Light, floating panels on a cool canvas, violet only for primary actions, selection and counts, dense data |
| `linen` | Product UI or marketing that should feel warm and editorial | Warm neutrals, generous rounding, black pill actions, large numerals, saffron highlights |
| `nocturne` | Marketing pages, dark product UI | Deep indigo canvas with a glow, glassy surfaces, violet actions. Pairs with `lumen` product screenshots |

Pages built with them:

{{REFERENCES}}

## 0. Rules
1. **Brand color:** apply the user's brand by overriding `--accent`, `--accent-hover`, `--accent-soft`, and `--accent-ink` (and `--btn-solid*` for `lumen`/`nocturne`). Keep text contrast at 4.5:1 or higher; `/pixelproof theme` does the math.
2. **Values:** use only the tokens below. Never hard-code a color, radius, or shadow in a component.
3. **Presets:** one preset per surface. A marketing page may embed a product screenshot in another preset by wrapping it in `data-preset="lumen"`; tokens re-scope automatically.
4. **Icons:** only sprite icons (24×24, stroke 1.6, round caps). Draw new icons in the same style.
5. **Copy:** sentence case, plain verbs, and specific error messages that say what went wrong and how to fix it.
6. **Quality floor**, verified by `render.py --deep --strict` at 1440, 1024, and 390:
   - text contrast AA
   - no text under 12px
   - tap targets of 44px or more on mobile
   - no page overflow

## 1. Tokens (per preset)
Every preset defines the same names:

| Group | Tokens |
|---|---|
| Type | `--font`, `--font-display`, `--display-weight`, `--display-tracking`, `--title-weight` |
| Surfaces | `--canvas` (page), `--surface` (cards), `--surface-2` (panel heads, side), `--surface-3` (chips, tiles, tracks), `--line`, `--line-strong` |
| Text | `--ink`, `--ink-2`, `--ink-3` (secondary, AA on every surface), `--ink-4` (placeholders only) |
| Brand | `--accent`, `--accent-hover`, `--accent-soft`, `--accent-ink`, `--on-accent`, `--btn-solid`, `--btn-solid-hover`, `--on-btn-solid`, `--accent-gradient` |
| Status | `--success`, `--warning`, `--danger`, `--info`, each with a `-soft` background |
| Shape | `--r-panel`, `--r-card`, `--r-control`, `--r-chip`, `--shadow-panel`, `--shadow-float`, `--shadow-accent` |
| Density | `--row-h`, `--control-h`, `--gap`, `--pad` |
| Component | `--brand-mark-ink`, `--nav-active-bg`, `--nav-active-ink`, `--nav-active-shadow`, `--stat-size`, `--stat-weight`, `--bar-fill`, `--cta-btn-bg`, `--cta-btn-ink`, `--site-bg` (nocturne) |

## 2. CSS (components + the three presets)

```css
{{CSS}}
```

## 3. Icons

{{ICON_LIST}}

```html
{{SPRITE}}
```

## 4. Components

{{COMPONENTS}}

## 5. Which pattern to use

| Need | Use |
|---|---|
| App layout | `.shell` > `.side` + `.main` (floating panels) |
| Page header | `.topbar` (crumbs + actions), then `.page-head` (title, subtitle, period `.segmented`) |
| Headline numbers | `.grid.grid-3` of `.card` with `.stat-head`, `.stat-value`, `.stat-foot` |
| Records | `.panel` > `.panel-head` + `.table-wrap` > `.table`; status as `.chip-*` |
| Breakdown or summary | `.panel` with `.big-number` and `.rows` |
| Highlight card | `.plan-card` (gradient, one per screen) |
| Settings | `.dialog` with `.dialog-side` (scope `.segmented` + nav) and `.dialog-main` |
| Edit forms | `.form-row` (label and help on the left, controls on the right) |
| Sign-in flows | `.auth` split (form + `.auth-aside`); OTP, reset, and register as `.card` states |
| Files | `.dropzone`, `.files` > `.file` (done, progress, error, queued), `.thumbs` |
| Empty state | `.card.card-soft` with a tile, title, one sentence, and one action |
| Marketing | `.site-nav`, `.hero` (+ `.hero-shot`), `.logos`, `.bento`, `.steps`, `.quote`, `.pricing`, `.faq`, `.cta`, `.footer` |

## 6. Responsive
- **≤1100px:** `.split` stacks, bento cards go to 2 columns, and state cards go to 2 columns.
- **≤900px:**
  - `.shell` becomes one column, and `.side` becomes a top bar showing only the brand. The app keeps its own mobile menu.
  - The dialog stacks, with its nav scrolling sideways.
  - Form rows stack, and auth hides its aside.
  - Marketing nav links are hidden, and steps, pricing, and the footer stack.
- **≤560px:**
  - buttons, inputs, nav items, segmented buttons, and row links are all at least 44px tall
  - the hero shot is hidden
  - bento cards go to 1 column

## 7. Verification

{{VERIFY}}
