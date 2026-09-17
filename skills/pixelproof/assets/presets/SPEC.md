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

| Slice | Title | Shows |
|---|---|---|
| `gallery/build/dashboard--lumen.html` | Dashboard | App shell, stat cards, table panel, summary and plan cards, chart |
| `gallery/build/settings--lumen.html` | Settings | Settings dialog with segmented scope, side nav, filterable table |
| `gallery/build/form--lumen.html` | Form | Two-column form rows, checkboxes, tags, error state |
| `gallery/build/auth--lumen.html` | Log in | Split login with SSO, password, remember-me, brand panel |
| `gallery/build/auth-states--lumen.html` | Auth states | OTP, reset password with error, register with success |
| `gallery/build/upload--lumen.html` | Files | Dropzone, file rows (done, progress, error, queued), thumbnails, empty state |
| `gallery/build/landing--lumen.html` | Landing | Nav, hero with product shot, logos, bento, steps, testimonial, pricing, FAQ, CTA, footer |

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
/* =====================================================================
   Pixelproof presets — shared components.
   Every visual value comes from the preset tokens (lumen.css, linen.css, nocturne.css).
   Set the preset with <html data-preset="lumen|linen|nocturne">.
   ===================================================================== */

/* ================= Base ================= */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { min-height: 100%; }
body {
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.45;
  letter-spacing: -0.005em;
  color: var(--ink);
  background: var(--canvas);
  -webkit-font-smoothing: antialiased;
  font-feature-settings: "tnum" 1, "cv11" 1;
}
button, input, select, textarea { font: inherit; color: inherit; letter-spacing: inherit; }
button { cursor: pointer; background: none; border: 0; }
a { color: inherit; text-decoration: none; }
ul, ol { list-style: none; }
img { display: block; max-width: 100%; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
::selection { background: var(--accent-soft); }

.icon { width: 18px; height: 18px; flex-shrink: 0; fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
.icon-sm { width: 15px; height: 15px; }
.icon-lg { width: 22px; height: 22px; }
.muted { color: var(--ink-3); }
.num { font-variant-numeric: tabular-nums; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

/* ================= Buttons ================= */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  height: var(--control-h); padding: 0 16px;
  border-radius: var(--r-control);
  font-size: 14px; font-weight: 500; white-space: nowrap;
  transition: background-color .15s, border-color .15s, box-shadow .15s;
}
.btn-solid { background: var(--btn-solid); color: var(--on-btn-solid); box-shadow: var(--shadow-accent); }
.btn-solid:hover { background: var(--btn-solid-hover); }
.btn-accent { background: var(--accent); color: var(--on-accent); }
.btn-accent:hover { background: var(--accent-hover); }
.btn-line { background: var(--surface); color: var(--ink); border: 1px solid var(--line); }
.btn-line:hover { border-color: var(--line-strong); background: var(--surface-2); }
.btn-ghost { color: var(--ink-2); }
.btn-ghost:hover { background: var(--surface-3); }
.btn-soft { background: var(--accent-soft); color: var(--accent-ink); }
.btn-sm { height: 32px; padding: 0 12px; font-size: 13px; }
.btn-lg { height: 48px; padding: 0 22px; font-size: 15px; }
.btn-block { width: 100%; }
.btn-icon { width: var(--control-h); padding: 0; }
.link { color: var(--accent-ink); font-weight: 500; text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1px; }

/* ================= Chips, badges, status ================= */
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  height: 24px; padding: 0 9px;
  border-radius: var(--r-chip);
  font-size: 12px; font-weight: 500; white-space: nowrap;
  background: var(--surface-3); color: var(--ink-2);
}
.chip-accent { background: var(--accent-soft); color: var(--accent-ink); }
.chip-success { background: var(--success-soft); color: var(--success); }
.chip-warning { background: var(--warning-soft); color: var(--warning); }
.chip-danger { background: var(--danger-soft); color: var(--danger); }
.chip-info { background: var(--info-soft); color: var(--info); }
.chip-outline { background: transparent; border: 1px solid var(--line); }
.dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; flex-shrink: 0; }
.badge {
  display: inline-grid; place-items: center; min-width: 20px; height: 20px; padding: 0 6px;
  border-radius: 999px; background: var(--accent); color: var(--on-accent);
  font-size: 12px; font-weight: 600; letter-spacing: 0;
}
.delta { display: inline-flex; align-items: center; gap: 3px; font-weight: 600; }
.delta-up { color: var(--success); }
.delta-down { color: var(--danger); }

/* ================= Inputs ================= */
.field { display: grid; gap: 6px; }
.label { font-size: 13px; font-weight: 500; color: var(--ink-2); }
.hint { font-size: 12px; color: var(--ink-3); }
.input, .select, .textarea {
  width: 100%; height: var(--control-h); padding: 0 12px;
  border: 1px solid var(--line); border-radius: min(var(--r-control), 12px);
  background: var(--surface); color: var(--ink); outline: 0;
  transition: border-color .15s, box-shadow .15s;
}
.textarea { height: auto; min-height: 96px; padding: 10px 12px; resize: vertical; }
.input::placeholder, .textarea::placeholder { color: var(--ink-4); }
.input:focus, .select:focus, .textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.input.is-error { border-color: var(--danger); box-shadow: 0 0 0 3px var(--danger-soft); }
.error-text { font-size: 12px; color: var(--danger); }
.select {
  appearance: none; padding-right: 36px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%237a7888' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 12px center; background-size: 16px;
}
.input-group { position: relative; display: flex; align-items: center; }
.input-group > .icon { position: absolute; left: 12px; color: var(--ink-3); pointer-events: none; }
.input-group > .input { padding-left: 38px; }
.input-group > .kbd { position: absolute; right: 10px; }
.kbd { font-size: 12px; color: var(--ink-3); border: 1px solid var(--line); border-radius: 5px; padding: 1px 5px; background: var(--surface-2); }
.check { display: inline-flex; align-items: center; gap: 10px; font-size: 14px; color: var(--ink-2); cursor: pointer; }
.check input {
  appearance: none; width: 18px; height: 18px; margin: 0; flex-shrink: 0;
  border: 1.5px solid var(--line-strong); border-radius: 5px; background: var(--surface) center / 12px no-repeat; cursor: pointer;
}
.check input:checked {
  background-color: var(--accent); border-color: var(--accent);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12 5 5 9-10'/%3E%3C/svg%3E");
}
.segmented { display: inline-flex; padding: 3px; gap: 2px; border-radius: min(var(--r-control), 12px); background: var(--surface-3); }
.segmented button { height: 30px; padding: 0 14px; border-radius: min(calc(var(--r-control) - 2px), 10px); font-size: 13px; color: var(--ink-2); }
.segmented button[aria-pressed="true"] { background: var(--surface); color: var(--ink); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08); }

/* ================= Avatars & tiles ================= */
.avatar { display: grid; place-items: center; flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; color: #fff; font-size: 12px; font-weight: 600; }
.avatar-sm { width: 26px; height: 26px; font-size: 12px; letter-spacing: -0.02em; }
.avatar-lg { width: 40px; height: 40px; font-size: 14px; }
.avatar-stack { display: flex; }
.avatar-stack .avatar { box-shadow: 0 0 0 2px var(--surface); }
.avatar-stack .avatar + .avatar { margin-left: -8px; }
.tile { display: grid; place-items: center; flex-shrink: 0; width: 34px; height: 34px; border-radius: min(var(--r-card), 10px); background: var(--surface-3); color: var(--ink-2); }
.tile-accent { background: var(--accent-soft); color: var(--accent-ink); }
.brand-mark { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; background: var(--accent-gradient); color: var(--brand-mark-ink); box-shadow: var(--shadow-accent); }
.brand-mark svg { width: 18px; height: 18px; stroke-width: 2.2; }

/* ================= App shell (floating panels) ================= */
.shell { display: grid; grid-template-columns: 264px minmax(0, 1fr); gap: 10px; min-height: 100vh; padding: 10px; }
.side {
  position: sticky; top: 10px; height: calc(100vh - 20px);
  display: flex; flex-direction: column; gap: 4px;
  padding: 16px 12px; overflow-y: auto;
  background: var(--surface-2); border: 1px solid var(--line); border-radius: var(--r-panel);
}
.side-brand { display: flex; align-items: center; gap: 10px; padding: 2px 4px 14px; }
.side-brand small { display: block; font-size: 12px; color: var(--ink-3); }
.side-brand strong { display: block; font-size: 15px; font-weight: 600; letter-spacing: -0.02em; }
.side .input-group { margin-bottom: 6px; }
.side .input { background: var(--surface); }
.nav-label { padding: 14px 10px 6px; font-size: 12px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink-3); }
.nav-item {
  display: flex; align-items: center; gap: 10px; width: 100%;
  height: 38px; padding: 0 10px; border-radius: min(var(--r-control), 10px);
  font-size: 14px; color: var(--ink-2); text-align: left;
}
.nav-item:hover { background: var(--surface-3); }
.nav-item .icon { color: var(--ink-3); }
.nav-item .badge { margin-left: auto; }
.nav-item.is-active { background: var(--nav-active-bg); color: var(--nav-active-ink); font-weight: 500; box-shadow: var(--nav-active-shadow); }
.nav-item.is-active .icon { color: var(--accent); }
.side-user { margin-top: auto; display: flex; align-items: center; gap: 10px; padding: 12px 6px 4px; border-top: 1px solid var(--line); }
.side-user strong { display: block; font-size: 14px; font-weight: 600; }
.side-user div span { display: block; font-size: 12px; color: var(--ink-3); }

.main {
  min-width: 0; padding: 18px 20px 28px;
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-panel);
}
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.crumbs { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--ink-3); }
.crumbs .current { color: var(--ink); }
.actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin: 22px 0 18px; }
.page-title { font-family: var(--font-display); font-size: 26px; font-weight: var(--title-weight); letter-spacing: -0.03em; line-height: 1.15; }
.page-sub { margin-top: 4px; color: var(--ink-3); }

/* ================= Cards & panels ================= */
.grid { display: grid; gap: var(--gap); }
.grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.split { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: var(--gap); align-items: start; margin-top: var(--gap); }
.card { padding: var(--pad); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); box-shadow: var(--shadow-panel); }
.card-soft { background: var(--surface-2); }
.stat-head { display: flex; align-items: center; gap: 10px; color: var(--ink-2); }
.stat-head .chip { margin-left: auto; }
.stat-value { margin: 18px 0 8px; font-family: var(--font-display); font-size: var(--stat-size); font-weight: var(--stat-weight); letter-spacing: -0.035em; line-height: 1; font-variant-numeric: tabular-nums; }
.stat-foot { display: flex; align-items: center; gap: 8px; color: var(--ink-3); font-size: 13px; }

.panel { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); overflow: hidden; box-shadow: var(--shadow-panel); }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px var(--pad); border-bottom: 1px solid var(--line); background: var(--surface-2); }
.panel-title { font-size: 15px; font-weight: 600; letter-spacing: -0.015em; }
.panel-sub { font-size: 13px; color: var(--ink-3); margin-top: 2px; }
.panel-body { padding: var(--pad); }
.panel-foot { padding: 12px var(--pad); border-top: 1px solid var(--line); font-size: 13px; color: var(--ink-3); }

/* ================= Table ================= */
.table-wrap { overflow-x: auto; }
.table { width: 100%; min-width: 620px; border-collapse: collapse; }
.table th {
  height: 40px; padding: 0 var(--pad); text-align: left; white-space: nowrap;
  font-size: 12px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink-3);
  border-bottom: 1px solid var(--line);
}
.table td { height: var(--row-h); padding: 0 var(--pad); border-bottom: 1px solid var(--line); white-space: nowrap; }
.table tbody tr:last-child td { border-bottom: 0; }
.table tbody tr:hover { background: var(--surface-2); }
.table td.strong { font-weight: 600; }
.table td.end, .table th.end { text-align: right; }
.table .row-link { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 8px; color: var(--ink-3); }
.table .row-link:hover { background: var(--surface-3); color: var(--ink); }
.cell { display: flex; align-items: center; gap: 10px; }
.cell small { display: block; font-size: 12px; color: var(--ink-3); }

/* ================= Summary / breakdown ================= */
.big-number { font-family: var(--font-display); font-size: 36px; font-weight: 600; letter-spacing: -0.04em; line-height: 1; }
.rows { display: grid; gap: 10px; padding: 14px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); margin: 16px 0; }
.row { display: flex; justify-content: space-between; gap: 12px; color: var(--ink-2); }
.row b { font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }
.row b.neg { color: var(--danger); }
.plan-card {
  position: relative; overflow: hidden; padding: 18px; border-radius: var(--r-card);
  background: var(--accent-gradient); color: var(--on-btn-solid); box-shadow: var(--shadow-accent);
}
.plan-card::after { content: ""; position: absolute; right: -40px; top: -60px; width: 180px; height: 180px; border-radius: 50%; border: 28px solid rgba(255, 255, 255, 0.09); }
.plan-card .chip { background: rgba(255, 255, 255, 0.18); color: inherit; }
.plan-card .big-number { margin: 22px 0 18px; font-size: 22px; letter-spacing: 0.12em; }
.plan-meta { display: flex; justify-content: space-between; gap: 12px; font-size: 12px; opacity: 0.8; }
.plan-meta b { display: block; font-size: 14px; opacity: 1; }

/* ================= Bar chart (CSS only) ================= */
.bars { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; align-items: end; gap: 14px; height: 180px; margin-top: 18px; }
.bar { position: relative; display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }
.bar i { display: block; border-radius: min(var(--r-card), 12px); background: var(--surface-3); }
.bar i + i { margin-top: 4px; background: var(--bar-fill); }
.bar span { margin-top: 8px; text-align: center; font-size: 12px; color: var(--ink-3); }
.legend { display: flex; gap: 14px; font-size: 12px; color: var(--ink-3); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }

/* ================= Dialog (settings) ================= */
.dialog {
  display: grid; grid-template-columns: 250px minmax(0, 1fr);
  max-width: 980px; margin: 40px auto; overflow: hidden;
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-panel); box-shadow: var(--shadow-float);
}
.dialog-side { padding: 22px 14px; background: var(--surface-2); border-right: 1px solid var(--line); }
.dialog-side .segmented { display: flex; margin: 12px 0 14px; }
.dialog-side .segmented button { flex: 1; }
.dialog-main { display: flex; flex-direction: column; min-width: 0; }
.dialog-head { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; border-bottom: 1px solid var(--line); }
.dialog-body { padding: 20px 24px; }
.dialog-foot { display: flex; justify-content: flex-end; gap: 8px; margin-top: auto; padding: 14px 24px; border-top: 1px solid var(--line); }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
.toolbar .input-group { width: min(320px, 100%); }

/* ================= Form layout ================= */
.form-row { display: grid; grid-template-columns: minmax(0, 280px) minmax(0, 1fr); gap: 32px; padding: 22px 0; border-top: 1px solid var(--line); }
.form-row:first-of-type { border-top: 0; }
.form-row h3 { font-size: 14px; font-weight: 600; }
.form-row p { margin-top: 4px; font-size: 13px; color: var(--ink-3); max-width: 34ch; }
.form-control { display: grid; gap: 10px; max-width: 440px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }

/* ================= Auth ================= */
.auth { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); min-height: 100vh; padding: 10px; gap: 10px; }
.auth-form { display: flex; flex-direction: column; padding: 28px 40px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-panel); }
.auth-inner { width: min(380px, 100%); margin: auto; }
.auth-title { font-family: var(--font-display); font-size: 30px; font-weight: var(--display-weight); letter-spacing: var(--display-tracking); line-height: 1.1; margin: 22px 0 8px; }
.auth-inner form { display: grid; gap: 14px; margin-top: 24px; }
.divider { display: flex; align-items: center; gap: 12px; font-size: 12px; color: var(--ink-3); }
.divider::before, .divider::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.auth-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; font-size: 13px; }
.auth-foot { margin-top: 24px; font-size: 13px; color: var(--ink-3); text-align: center; }
.auth-aside {
  position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between;
  padding: 36px; border-radius: var(--r-panel); color: var(--on-btn-solid); background: var(--accent-gradient);
}
.auth-aside::before { content: ""; position: absolute; inset: auto -120px -160px auto; width: 420px; height: 420px; border-radius: 50%; border: 60px solid rgba(255, 255, 255, 0.07); }
.auth-quote { position: relative; max-width: 30ch; font-family: var(--font-display); font-size: 26px; font-weight: 500; letter-spacing: -0.025em; line-height: 1.2; }
.auth-aside .mini { position: relative; margin-top: 28px; color: var(--ink); box-shadow: var(--shadow-float); }
.otp { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.otp .input { height: 52px; padding: 0; text-align: center; font-size: 20px; font-weight: 600; border-radius: min(var(--r-control), 12px); }
.alert { display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; border-radius: min(var(--r-card), 12px); font-size: 13px; }
.alert-danger { background: var(--danger-soft); color: var(--danger); }
.alert-success { background: var(--success-soft); color: var(--success); }
.state-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--gap); padding: 10px; }
.state-grid .card { padding: 28px; }
.state-title { font-family: var(--font-display); font-size: 20px; font-weight: 600; letter-spacing: -0.02em; margin: 14px 0 6px; }

/* ================= Upload ================= */
.dropzone {
  display: grid; place-items: center; gap: 6px; padding: 32px 20px; text-align: center;
  border: 1.5px dashed var(--line-strong); border-radius: var(--r-card); background: var(--surface-2); cursor: pointer;
  transition: border-color .15s, background-color .15s;
}
.dropzone:hover, .dropzone.is-over { border-color: var(--accent); background: var(--accent-soft); }
.dropzone .tile { width: 44px; height: 44px; margin-bottom: 6px; background: var(--surface); border: 1px solid var(--line); }
.dropzone strong { font-weight: 600; }
.dropzone strong span { color: var(--accent-ink); }
.files { display: grid; gap: 8px; margin-top: 14px; }
.file { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 12px; padding: 12px; border: 1px solid var(--line); border-radius: min(var(--r-card), 12px); background: var(--surface); }
.file-type { display: grid; place-items: center; width: 38px; height: 42px; border-radius: 6px; font-size: 12px; font-weight: 700; letter-spacing: 0.02em; color: #fff; position: relative; }
.file-type::after { content: ""; position: absolute; top: 0; right: 0; width: 10px; height: 10px; background: rgba(255, 255, 255, 0.35); border-bottom-left-radius: 4px; }
.ft-pdf { background: #c0392f; } .ft-img { background: #23775a; } .ft-doc { background: #2f5fc4; } .ft-csv { background: #5e6b1c; }
.file-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-meta { font-size: 12px; color: var(--ink-3); }
.progress { height: 6px; margin-top: 8px; border-radius: 999px; background: var(--surface-3); overflow: hidden; }
.progress i { display: block; height: 100%; border-radius: inherit; background: var(--accent); }
.file.is-error { border-color: var(--danger); background: var(--danger-soft); }
.file.is-error .file-meta { color: var(--danger); }
.thumbs { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }
.thumb { overflow: hidden; border: 1px solid var(--line); border-radius: min(var(--r-card), 12px); background: var(--surface); }
.thumb-art { aspect-ratio: 4 / 3; display: grid; place-items: center; color: var(--ink-3); background: var(--surface-3); }
.thumb-art.a1 { background: linear-gradient(135deg, #d9d2ff, #f4e3ff); }
.thumb-art.a2 { background: linear-gradient(135deg, #cfeee0, #eef7d6); }
.thumb-art.a3 { background: linear-gradient(135deg, #ffe0c7, #ffd3d3); }
.thumb-cap { padding: 8px 10px; font-size: 12px; }
.thumb-cap small { display: block; font-size: 12px; color: var(--ink-3); }

/* ================= Landing ================= */
.site-wrap { width: min(1160px, calc(100% - 32px)); margin: 0 auto; }
.site-nav { position: sticky; top: 12px; z-index: 5; display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 12px; padding: 8px 8px 8px 16px; background: var(--surface); border: 1px solid var(--line); border-radius: min(var(--r-panel), 18px); box-shadow: var(--shadow-panel); }
.site-nav nav { display: flex; gap: 4px; }
.site-nav nav a { padding: 8px 12px; border-radius: 999px; font-size: 14px; color: var(--ink-2); }
.site-nav nav a:hover { background: var(--surface-3); color: var(--ink); }
.logo { display: flex; align-items: center; gap: 10px; min-height: 44px; font-weight: 600; font-size: 16px; letter-spacing: -0.02em; }
.logo .brand-mark { width: 28px; height: 28px; border-radius: 8px; }
.hero { padding: 88px 0 0; text-align: center; }
.hero > h1 { max-width: 18ch; margin: 18px auto 0; font-family: var(--font-display); font-size: clamp(40px, 6vw, 68px); font-weight: var(--display-weight); letter-spacing: var(--display-tracking); line-height: 1.02; text-wrap: balance; }
.hero > p { max-width: 54ch; margin: 20px auto 0; font-size: 17px; color: var(--ink-3); text-wrap: pretty; }
.hero > .actions { justify-content: center; margin-top: 28px; }
.hero-shot { position: relative; margin: 56px auto 0; max-width: 1040px; padding: 10px; border-radius: calc(var(--r-panel) + 8px); background: color-mix(in srgb, var(--canvas) 80%, transparent); border: 1px solid var(--line); box-shadow: var(--shadow-float); text-align: left; font-size: 14px; color: var(--ink); }
.hero-shot .shell { min-height: 0; padding: 0; }
.hero-shot .side { position: static; height: auto; }
.site { background: var(--site-bg, var(--canvas)); }
.logos { display: flex; flex-wrap: wrap; justify-content: center; gap: 18px 48px; padding: 56px 0 8px; color: var(--ink-3); font-size: 20px; font-weight: 600; letter-spacing: -0.03em; }
.logos span:nth-child(2) { font-style: italic; } .logos span:nth-child(3) { letter-spacing: 0.08em; font-size: 16px; } .logos span:nth-child(4) { font-weight: 800; }
.section { padding: 96px 0 0; }
.section-head { max-width: 640px; margin: 0 auto 36px; text-align: center; }
.section-head h2 { font-family: var(--font-display); font-size: clamp(30px, 4vw, 44px); font-weight: var(--display-weight); letter-spacing: var(--display-tracking); line-height: 1.06; text-wrap: balance; }
.section-head p { margin-top: 12px; font-size: 16px; color: var(--ink-3); }
.bento { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: var(--gap); }
.bento .card { display: flex; flex-direction: column; gap: 6px; min-height: 340px; padding: 26px; }
.bento .card:nth-child(1) { grid-column: span 4; }
.bento .card:nth-child(2) { grid-column: span 2; }
.bento .card:nth-child(n+3) { grid-column: span 2; }
.bento h3 { margin-top: auto; font-size: 19px; font-weight: 600; letter-spacing: -0.02em; }
.bento p { font-size: 14px; color: var(--ink-3); max-width: 42ch; }
.art { flex: 1; display: grid; place-items: center; min-height: 170px; padding: 8px; }
.art .mini { width: min(100%, 380px); }
.bubble { max-width: 240px; padding: 10px 14px; border-radius: 14px; background: var(--surface-3); font-size: 13px; }
.bubble.me { margin-left: auto; background: var(--btn-solid); color: var(--on-btn-solid); }
.chat { display: grid; gap: 8px; width: min(100%, 300px); }
.flow { display: grid; justify-items: center; gap: 10px; }
.flow-row { display: flex; gap: 10px; }
.steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--gap); counter-reset: step; }
.step { padding: 24px; border-top: 2px solid var(--line); }
.step::before { counter-increment: step; content: counter(step); display: grid; place-items: center; width: 32px; height: 32px; margin-bottom: 18px; border-radius: 50%; background: var(--btn-solid); color: var(--on-btn-solid); font-weight: 600; }
.step h3 { font-size: 17px; font-weight: 600; letter-spacing: -0.015em; }
.step p { margin-top: 6px; color: var(--ink-3); }
.quote { max-width: 860px; margin: 0 auto; text-align: center; }
.quote blockquote { font-family: var(--font-display); font-size: clamp(24px, 3vw, 34px); font-weight: var(--display-weight); letter-spacing: -0.025em; line-height: 1.2; text-wrap: balance; }
.quote figcaption { display: inline-flex; align-items: center; gap: 10px; margin-top: 22px; text-align: left; font-size: 14px; }
.quote figcaption small { display: block; font-size: 13px; color: var(--ink-3); }
.pricing { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--gap); align-items: stretch; }
.price { display: flex; flex-direction: column; gap: 14px; padding: 26px; }
.price.is-featured { background: var(--btn-solid); color: var(--on-btn-solid); border-color: transparent; box-shadow: var(--shadow-float); }
.price.is-featured .muted, .price.is-featured li { color: color-mix(in srgb, var(--on-btn-solid) 78%, transparent); }
.price.is-featured .btn-line { background: var(--surface); color: var(--ink); }
.price.is-featured .chip { background: rgba(0, 0, 0, 0.24); color: inherit; }
.price-amount { font-family: var(--font-display); font-size: 42px; font-weight: 600; letter-spacing: -0.04em; line-height: 1; }
.price-amount small { font-size: 14px; font-weight: 400; letter-spacing: 0; color: inherit; opacity: 0.7; }
.price ul { display: grid; gap: 8px; font-size: 14px; color: var(--ink-2); }
.price li { display: flex; gap: 8px; align-items: flex-start; }
.price li .icon { color: var(--accent); margin-top: 1px; }
.price .btn { margin-top: auto; }
.faq { max-width: 760px; margin: 0 auto; }
.faq details { border-bottom: 1px solid var(--line); overflow: clip; }
.faq summary { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 20px 6px 20px 0; font-size: 16px; font-weight: 500; cursor: pointer; list-style: none; }
.faq summary::-webkit-details-marker { display: none; }
.faq summary .icon { flex-shrink: 0; transition: transform .2s; color: var(--ink-3); }
.faq details[open] summary .icon { transform: rotate(45deg); }
.faq details p { padding: 0 0 20px; color: var(--ink-3); max-width: 64ch; }
.cta { margin-top: 96px; padding: 64px 32px; text-align: center; border-radius: calc(var(--r-panel) + 6px); background: var(--accent-gradient); color: var(--on-btn-solid); position: relative; overflow: hidden; }
.cta h2 { max-width: 20ch; margin: 0 auto; font-family: var(--font-display); font-size: clamp(28px, 4vw, 42px); font-weight: var(--display-weight); letter-spacing: var(--display-tracking); line-height: 1.08; }
.cta p { margin-top: 12px; opacity: 0.8; }
.cta .actions { justify-content: center; margin-top: 24px; }
.cta .btn-line { background: rgba(255, 255, 255, 0.1); color: inherit; border-color: rgba(255, 255, 255, 0.25); }
.cta .btn-solid { color: var(--cta-btn-ink); box-shadow: none; }
.cta .btn-solid { background: var(--cta-btn-bg); }
.footer { display: grid; grid-template-columns: 1.4fr repeat(3, 1fr); gap: 24px; padding: 56px 0 40px; margin-top: 56px; border-top: 1px solid var(--line); }
.footer h4 { font-size: 12px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 12px; }
.footer ul { display: grid; gap: 8px; font-size: 14px; color: var(--ink-2); }
.footer p { margin-top: 12px; max-width: 32ch; color: var(--ink-3); font-size: 14px; }
.mini { background: var(--surface); border: 1px solid var(--line); border-radius: min(var(--r-card), 14px); padding: 14px; }

/* ================= Responsive ================= */
@media (max-width: 1100px) {
  .split { grid-template-columns: 1fr; }
  .bento .card:nth-child(n) { grid-column: span 3; }
  .state-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 900px) {
  .shell { grid-template-columns: 1fr; }
  .side { position: static; height: auto; flex-direction: row; flex-wrap: wrap; align-items: center; }
  .side > :not(.side-brand) { display: none; }
  .side-brand { padding: 0; }
  .grid-3 { grid-template-columns: 1fr; }
  .dialog { grid-template-columns: 1fr; margin: 10px; }
  .dialog-side { border-right: 0; border-bottom: 1px solid var(--line); }
  .dialog-side nav { display: flex; overflow-x: auto; gap: 4px; }
  .dialog-side .nav-item { width: auto; flex-shrink: 0; }
  .form-row { grid-template-columns: 1fr; gap: 12px; }
  .auth { grid-template-columns: 1fr; }
  .auth-aside { display: none; }
  .auth-form { padding: 24px; }
  .site-nav nav { display: none; }
  .steps, .pricing { grid-template-columns: 1fr; }
  .footer { grid-template-columns: 1fr 1fr; }
  .hero { padding-top: 56px; }
}
@media (max-width: 560px) {
  .btn, .btn-sm { min-height: 44px; }
  .btn-icon { min-width: 44px; }
  .input, .select { height: 44px; }
  .segmented button { height: 44px; }
  .nav-item { height: 44px; }
  .table .row-link { width: 44px; height: 44px; }
  .panel-head .link, .auth-row .link, .footer li a { display: inline-flex; align-items: center; min-height: 44px; min-width: 44px; }
  .check { min-height: 44px; }
  .main { padding: 14px; }
  .bento .card:nth-child(n) { grid-column: span 6; min-height: 0; }
  .grid-2, .state-grid { grid-template-columns: 1fr; }
  .page-title { font-size: 22px; }
  .hero-shot { display: none; }
  .site-nav .btn-line { display: none; }
  .otp .input { height: 46px; font-size: 18px; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }

/* Lumen — light product UI. Floating panels on a cool canvas; violet only for primary action, selection, and counts. */
[data-preset="lumen"] {
  --font: "Geist", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-display: var(--font);
  --display-weight: 600;
  --display-tracking: -0.03em;
  --title-weight: 600;

  --canvas: #f2f2f5;
  --surface: #ffffff;
  --surface-2: #f8f8fa;
  --surface-3: #f0eff4;
  --line: #e7e6ec;
  --line-strong: #d9d8e0;
  --ink: #16151f;
  --ink-2: #3f3e4b;
  --ink-3: #6b6a78;
  --ink-4: #9f9eab;

  --accent: #6e56f8;
  --accent-hover: #5b43ea;
  --accent-soft: #efecfe;
  --accent-ink: #4a33d6;
  --on-accent: #ffffff;
  --btn-solid: var(--accent);
  --btn-solid-hover: var(--accent-hover);
  --on-btn-solid: #ffffff;
  --accent-gradient: linear-gradient(135deg, #8b78ff 0%, #6e56f8 55%, #5a41e8 100%);

  --success: #127a4a; --success-soft: #e3f5ec;
  --warning: #a2570b; --warning-soft: #fdf0dc;
  --danger: #c4312b;  --danger-soft: #fdeceb;
  --info: #2459c7;    --info-soft: #e7eefc;

  --r-panel: 16px;
  --r-card: 12px;
  --r-control: 10px;
  --r-chip: 6px;
  --shadow-panel: 0 1px 2px rgba(22, 21, 31, 0.04);
  --shadow-float: 0 12px 32px -12px rgba(22, 21, 31, 0.18);
  --shadow-accent: 0 8px 20px -8px rgba(110, 86, 248, 0.55);

  --row-h: 46px;
  --control-h: 38px;
  --gap: 12px;
  --pad: 16px;

  --brand-mark-ink: #ffffff;
  --nav-active-bg: var(--surface);
  --nav-active-ink: var(--ink);
  --nav-active-shadow: 0 1px 2px rgba(22, 21, 31, 0.05), 0 0 0 1px var(--line);
  --stat-size: 32px;
  --stat-weight: 600;
  --bar-fill: var(--accent);
  --cta-btn-bg: var(--surface);
  --cta-btn-ink: var(--ink);
}

/* Linen — warm editorial. Generous rounding, black pill actions, big numerals, saffron only for highlights. */
[data-preset="linen"] {
  --font: "Instrument Sans", "Hanken Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-display: var(--font);
  --display-weight: 500;
  --display-tracking: -0.035em;
  --title-weight: 500;

  --canvas: #eceae4;
  --surface: #f8f7f3;
  --surface-2: #f2f0ea;
  --surface-3: #e8e5dc;
  --line: #dedbd2;
  --line-strong: #cdc9bd;
  --ink: #1c1b18;
  --ink-2: #3d3b35;
  --ink-3: #66635a;
  --ink-4: #a5a198;

  --accent: #f0a500;
  --accent-hover: #d99500;
  --accent-soft: #fbefd2;
  --accent-ink: #8a5d00;
  --on-accent: #1c1b18;
  --btn-solid: #1c1b18;
  --btn-solid-hover: #34322c;
  --on-btn-solid: #f8f7f3;
  --accent-gradient: linear-gradient(135deg, #2a2823 0%, #1c1b18 100%);

  --success: #2f6a12; --success-soft: #e4f2c9;
  --warning: #8a5d00; --warning-soft: #fbefd2;
  --danger: #b23a22;  --danger-soft: #f8e1da;
  --info: #3a5a8c;    --info-soft: #e1e8f2;

  --r-panel: 26px;
  --r-card: 20px;
  --r-control: 999px;
  --r-chip: 999px;
  --shadow-panel: none;
  --shadow-float: 0 18px 40px -18px rgba(28, 27, 24, 0.28);
  --shadow-accent: 0 10px 24px -12px rgba(28, 27, 24, 0.6);

  --row-h: 56px;
  --control-h: 42px;
  --gap: 16px;
  --pad: 22px;

  --brand-mark-ink: var(--accent);
  --nav-active-bg: var(--ink);
  --nav-active-ink: var(--surface);
  --nav-active-shadow: none;
  --stat-size: 44px;
  --stat-weight: 500;
  --bar-fill: var(--ink);
  --cta-btn-bg: var(--accent);
  --cta-btn-ink: var(--ink);
}

/* Nocturne — dark indigo marketing. Deep gradient canvas, glassy surfaces, violet actions. Pairs with Lumen product screens. */
[data-preset="nocturne"] {
  --font: "Geist", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-display: var(--font);
  --display-weight: 500;
  --display-tracking: -0.035em;
  --title-weight: 500;

  --canvas: #100e2e;
  --surface: #1b1946;
  --surface-2: #211e52;
  --surface-3: #2a2762;
  --line: rgba(236, 234, 255, 0.1);
  --line-strong: rgba(236, 234, 255, 0.18);
  --ink: #f3f2ff;
  --ink-2: #d6d4f5;
  --ink-3: #a4a1d4;
  --ink-4: #7b78ad;

  --accent: #6450f2;
  --accent-hover: #5641e6;
  --accent-soft: rgba(124, 107, 255, 0.18);
  --accent-ink: #c9c1ff;
  --on-accent: #ffffff;
  --btn-solid: var(--accent);
  --btn-solid-hover: var(--accent-hover);
  --on-btn-solid: #ffffff;
  --accent-gradient: linear-gradient(135deg, #6f5cf7 0%, #4d3bd8 100%);
  --hero-gradient: radial-gradient(90% 55% at 50% 58%, rgba(92, 82, 255, 0.55) 0%, rgba(92, 82, 255, 0) 70%), linear-gradient(180deg, #100e2e 0%, #17145a 45%, #2a26a6 72%, #100e2e 100%);

  --success: #5ee0a0; --success-soft: rgba(94, 224, 160, 0.14);
  --warning: #ffc36b; --warning-soft: rgba(255, 195, 107, 0.14);
  --danger: #ff8a80;  --danger-soft: rgba(255, 138, 128, 0.14);
  --info: #8fb6ff;    --info-soft: rgba(143, 182, 255, 0.14);

  --r-panel: 18px;
  --r-card: 14px;
  --r-control: 10px;
  --r-chip: 6px;
  --shadow-panel: 0 1px 0 rgba(255, 255, 255, 0.04) inset;
  --shadow-float: 0 30px 60px -30px rgba(0, 0, 0, 0.7);
  --shadow-accent: 0 10px 28px -10px rgba(124, 107, 255, 0.8);

  --row-h: 46px;
  --control-h: 38px;
  --gap: 12px;
  --pad: 18px;

  --brand-mark-ink: #ffffff;
  --nav-active-bg: var(--surface-3);
  --nav-active-ink: var(--ink);
  --nav-active-shadow: 0 0 0 1px var(--line-strong);
  --stat-size: 32px;
  --stat-weight: 600;
  --bar-fill: var(--accent);
  --cta-btn-bg: #ffffff;
  --site-bg: var(--hero-gradient) top / 100% 1500px no-repeat, var(--canvas);
  --cta-btn-ink: #16151f;
}
```

## 3. Icons

`i-delivery`, `i-order`, `i-basket`, `i-tag`, `i-boxes`, `i-folder`, `i-bars`, `i-award`, `i-badge`, `i-percent`, `i-store`, `i-settings`, `i-chev-down`, `i-chev-right`, `i-bell`, `i-help`, `i-search`, `i-calendar`, `i-upload`, `i-sort`, `i-plus-circle`, `i-chair`, `i-truck`, `i-checklist`, `i-cloud-download`, `i-zap`, `i-info`, `i-close`, `i-sort-arrows`, `i-arrow-up`, `i-arrow-down-right`, `i-arrow-up-right`, `i-grid`, `i-megaphone`, `i-wallet`, `i-plus`, `i-sparkle`, `i-production`, `i-sparkles`, `i-shield-check`, `i-sun`, `i-layout`, `i-clipboard`, `i-user`, `i-warehouse`, `i-card`, `i-cart`, `i-grid-2`, `i-users`, `i-lock`, `i-columns`, `i-building`, `i-package`, `i-signpost`, `i-radio`, `i-van`, `i-id-card`, `i-map-pin`, `i-trending-up`, `i-route`, `i-dots`, `i-arrow-left`, `i-arrow-right`, `i-home`, `i-mail`, `i-check`, `i-file`, `i-image`, `i-refresh`, `i-trash`, `i-message`, `i-download`, `i-eye`, `i-key`, `i-logo`, `i-x`, `i-play`

```html
<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">
  <!-- pixelproof starter sprite: 24x24, line icons, stroke from .icon (currentColor, 1.6, round caps/joins).
       Adjust stroke width in .icon to the measured reference; add/redraw icons in the same style. -->
  <symbol id="i-delivery" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M10 4v5M14 4v5M7 15h3"/></symbol>
  <symbol id="i-order" viewBox="0 0 24 24"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/></symbol>
  <symbol id="i-basket" viewBox="0 0 24 24"><path d="M4 10h16l-1.6 8.3a2 2 0 0 1-2 1.7H7.6a2 2 0 0 1-2-1.7z"/><path d="M8.5 10 11 4M15.5 10 13 4M9 14v2.5M12 14v2.5M15 14v2.5"/></symbol>
  <symbol id="i-tag" viewBox="0 0 24 24"><path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.2"/></symbol>
  <symbol id="i-boxes" viewBox="0 0 24 24"><rect x="3" y="12" width="8" height="8" rx="1"/><rect x="13" y="12" width="8" height="8" rx="1"/><rect x="8" y="3" width="8" height="9" rx="1"/><path d="M12 3v3M7 12v3M17 12v3"/></symbol>
  <symbol id="i-folder" viewBox="0 0 24 24"><path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 10h18"/></symbol>
  <symbol id="i-bars" viewBox="0 0 24 24"><rect x="3" y="13" width="4" height="7" rx="1"/><rect x="10" y="9" width="4" height="11" rx="1"/><rect x="17" y="4" width="4" height="16" rx="1"/></symbol>
  <symbol id="i-award" viewBox="0 0 24 24"><circle cx="12" cy="9" r="6"/><circle cx="12" cy="9" r="2.5"/><path d="m8.5 14-1.5 7 5-2.5 5 2.5-1.5-7"/></symbol>
  <symbol id="i-badge" viewBox="0 0 24 24"><path d="m12 3 2.3 1.7 2.8-.2.9 2.7 2.3 1.6-.9 2.7.9 2.7-2.3 1.6-.9 2.7-2.8-.2L12 21l-2.3-1.7-2.8.2-.9-2.7-2.3-1.6.9-2.7-.9-2.7 2.3-1.6.9-2.7 2.8.2z"/><circle cx="12" cy="12" r="3"/></symbol>
  <symbol id="i-percent" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m9 15 6-6"/><circle cx="9.3" cy="9.3" r=".8"/><circle cx="14.7" cy="14.7" r=".8"/></symbol>
  <symbol id="i-store" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M8 3v6M16 3v6M9.5 21v-6h5v6"/></symbol>
  <symbol id="i-settings" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></symbol>
  <symbol id="i-chev-down" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></symbol>
  <symbol id="i-chev-right" viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></symbol>
  <symbol id="i-bell" viewBox="0 0 24 24"><path d="M6 16v-5a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/></symbol>
  <symbol id="i-help" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6"/><path d="M12 17h.01"/></symbol>
  <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></symbol>
  <symbol id="i-calendar" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M7.5 14h.01M12 14h.01M16.5 14h.01M7.5 17.5h.01M12 17.5h.01M16.5 17.5h.01"/></symbol>
  <symbol id="i-upload" viewBox="0 0 24 24"><path d="M12 15V3M7 8l5-5 5 5"/><path d="M4 14v5a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/></symbol>
  <symbol id="i-sort" viewBox="0 0 24 24"><path d="M4 6h16M7 12h10M10 18h4"/></symbol>
  <symbol id="i-plus-circle" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></symbol>
  <symbol id="i-chair" viewBox="0 0 24 24"><path d="M6 11V7a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v4"/><path d="M4 11a2 2 0 0 1 2 2v2h12v-2a2 2 0 1 1 4 0v4H2v-4a2 2 0 0 1 2-2z"/><path d="M5 17v3M19 17v3"/></symbol>
  <symbol id="i-truck" viewBox="0 0 24 24"><path d="M3 6h10v9H3z"/><path d="M13 9h4l3 3v3h-7"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></symbol>
  <symbol id="i-checklist" viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="m8 8 1.2 1.2L11.5 7M13.5 8.5H16M8 13.5l1.2 1.2 2.3-2.2M13.5 14H16M8 18h8"/></symbol>
  <symbol id="i-cloud-download" viewBox="0 0 24 24"><path d="M7 18a4.5 4.5 0 0 1-.9-8.9A6 6 0 0 1 17.7 8a4.5 4.5 0 0 1-.2 9"/><path d="M12 11v9M9 17l3 3 3-3"/></symbol>
  <symbol id="i-zap" viewBox="0 0 24 24"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></symbol>
  <symbol id="i-info" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></symbol>
  <symbol id="i-sort-arrows" viewBox="0 0 24 24"><path d="M8 20V4M4 8l4-4 4 4M16 4v16M12 16l4 4 4-4"/></symbol>
  <symbol id="i-arrow-up" viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6"/></symbol>
  <symbol id="i-arrow-down-right" viewBox="0 0 24 24"><path d="M7 7l10 10M17 9v8H9"/></symbol>
  <symbol id="i-arrow-up-right" viewBox="0 0 24 24"><path d="M7 17 17 7M9 7h8v8"/></symbol>
  <symbol id="i-grid" viewBox="0 0 24 24"><rect x="4" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5"/></symbol>
  <symbol id="i-megaphone" viewBox="0 0 24 24"><path d="M4 10v4a1 1 0 0 0 1 1h2l8 4V5L7 9H5a1 1 0 0 0-1 1z"/><path d="m7 15 1 5h2l-1-4.5M18 9.5a3 3 0 0 1 0 5"/></symbol>
  <symbol id="i-wallet" viewBox="0 0 24 24"><path d="M4 7a2 2 0 0 1 2-2h11v2"/><rect x="4" y="7" width="16" height="13" rx="2"/><path d="M20 11h-4a2 2 0 0 0 0 4h4"/></symbol>
  <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-sparkle" viewBox="0 0 24 24"><path d="M12 3l2 7 7 2-7 2-2 7-2-7-7-2 7-2z"/></symbol>
  <symbol id="i-production" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V4h8v3M9 7v13M15 7v13"/></symbol>
  <symbol id="i-sparkles" viewBox="0 0 24 24"><path d="m10 4 1.6 4.4L16 10l-4.4 1.6L10 16l-1.6-4.4L4 10l4.4-1.6z"/><path d="M18 3v4M16 5h4"/><circle cx="6" cy="19" r="1.5"/></symbol>
  <symbol id="i-shield-check" viewBox="0 0 24 24"><path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z"/><path d="m9 12 2 2 4-4"/></symbol>
  <symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></symbol>
  <symbol id="i-layout" viewBox="0 0 24 24"><rect x="4" y="3" width="7" height="18" rx="1.5"/><rect x="14" y="3" width="6" height="8" rx="1.5"/><rect x="14" y="14" width="6" height="7" rx="1.5"/></symbol>
  <symbol id="i-clipboard" viewBox="0 0 24 24"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 3h6v3H9zM9 11h6M9 15h6M9 18.5h3"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></symbol>
  <symbol id="i-warehouse" viewBox="0 0 24 24"><path d="M3 10 12 3l9 7v11H3z"/><path d="M9 21v-7h6v7"/></symbol>
  <symbol id="i-card" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/></symbol>
  <symbol id="i-cart" viewBox="0 0 24 24"><path d="M3 4h2l2.4 11h10.6l2-8H6.2"/><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/></symbol>
  <symbol id="i-grid-2" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 4v16M4 12h16"/></symbol>
  <symbol id="i-users" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14a6.5 6.5 0 0 1 3 6"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></symbol>
  <symbol id="i-columns" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16M15 4v16"/></symbol>
  <symbol id="i-building" viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="1.5"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2M10 21v-3h4v3"/></symbol>
  <symbol id="i-package" viewBox="0 0 24 24"><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/></symbol>
  <symbol id="i-signpost" viewBox="0 0 24 24"><path d="M12 3v18M8 21h8"/><path d="M5 6h11l3 2.5L16 11H5z"/></symbol>
  <symbol id="i-radio" viewBox="0 0 24 24"><circle cx="12" cy="12" r="2"/><path d="M8.5 8.5a5 5 0 0 0 0 7M15.5 8.5a5 5 0 0 1 0 7M5.6 5.6a9 9 0 0 0 0 12.8M18.4 5.6a9 9 0 0 1 0 12.8"/></symbol>
  <symbol id="i-van" viewBox="0 0 24 24"><path d="M3 6h13l4 4v5H3z"/><path d="M3 10h17M8 6v4M13 6v4"/><circle cx="7" cy="17" r="2"/><circle cx="16" cy="17" r="2"/></symbol>
  <symbol id="i-id-card" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16a3 3 0 0 1 6 0M14 10h4M14 14h3"/></symbol>
  <symbol id="i-map-pin" viewBox="0 0 24 24"><path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/></symbol>
  <symbol id="i-trending-up" viewBox="0 0 24 24"><path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/></symbol>
  <symbol id="i-route" viewBox="0 0 24 24"><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 18H16a3 3 0 0 0 0-6H8a3 3 0 0 1 0-6h7.5"/></symbol>
  <symbol id="i-dots" viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.3" fill="currentColor"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/><circle cx="19" cy="12" r="1.3" fill="currentColor"/></symbol>
  <symbol id="i-arrow-left" viewBox="0 0 24 24"><path d="M19 12H5M11 6l-6 6 6 6"/></symbol>
  <symbol id="i-arrow-right" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
  <symbol id="i-home" viewBox="0 0 24 24"><path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6h-6v6H5a1 1 0 0 1-1-1z"/></symbol>
  <symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12 5 5 9-10"/></symbol>
  <symbol id="i-file" viewBox="0 0 24 24"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></symbol>
  <symbol id="i-image" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/></symbol>
  <symbol id="i-refresh" viewBox="0 0 24 24"><path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 4v4h4M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20v-4h-4"/></symbol>
  <symbol id="i-trash" viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/></symbol>
  <symbol id="i-message" viewBox="0 0 24 24"><path d="M20 15a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/></symbol>
  <symbol id="i-download" viewBox="0 0 24 24"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></symbol>
  <symbol id="i-eye" viewBox="0 0 24 24"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></symbol>
  <symbol id="i-key" viewBox="0 0 24 24"><circle cx="8" cy="15" r="4"/><path d="m11 12 9-9M16 7l3 3M14 9l2 2"/></symbol>
  <symbol id="i-logo" viewBox="0 0 24 24"><path d="M5 19V9l7-5 7 5v10"/><path d="M9 19v-6h6v6"/></symbol>
  <symbol id="i-x" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path d="M7 4v16l13-8z"/></symbol>
</svg>
```

## 4. Components

### 4.1 Sidebar
Source: `dashboard.html`
```html
<aside class="side" aria-label="Main navigation">
  <div class="side-brand">
    <span class="brand-mark"><svg class="icon"><use href="#i-logo"/></svg></span>
    <div><small>Pixelproof</small><strong>Juniper Goods</strong></div>
  </div>
  <label class="input-group">
    <svg class="icon icon-sm"><use href="#i-search"/></svg>
    <input class="input" type="search" placeholder="Search" aria-label="Search" />
    <span class="kbd">⌘K</span>
  </label>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-bell"/></svg>Notifications<span class="badge">3</span></a>

  <p class="nav-label">Store</p>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-home"/></svg>Home</a>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-cart"/></svg>Orders<span class="badge">12</span></a>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-package"/></svg>Products</a>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-users"/></svg>Customers</a>

  <p class="nav-label">Money</p>
  <a href="#" class="nav-item is-active"><svg class="icon"><use href="#i-wallet"/></svg>Payouts</a>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-trending-up"/></svg>Reports</a>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-folder"/></svg>Files</a>

  <p class="nav-label">Workspace</p>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-clipboard"/></svg>Listings</a>
  <a href="#" class="nav-item"><svg class="icon"><use href="#i-settings"/></svg>Settings</a>

  <div class="side-user">
    <span class="avatar" style="background:#8a6a55">RA</span>
    <div><strong>Rani Aditya</strong><span>rani@junipergoods.co</span></div>
  </div>
</aside>
```

### 4.2 Topbar
Source: `dashboard.html`
```html
<div class="topbar">
      <nav class="crumbs" aria-label="Breadcrumb"><svg class="icon icon-sm"><use href="#i-home"/></svg><span>Money</span><svg class="icon icon-sm"><use href="#i-chev-right"/></svg><span class="current">Payouts</span></nav>
      <div class="actions">
        <button class="btn btn-line btn-sm"><svg class="icon icon-sm"><use href="#i-download"/></svg>Export</button>
        <button class="btn btn-line btn-sm">Payout settings</button>
      </div>
    </div>
```

### 4.3 Page head
Source: `dashboard.html`
```html
<div class="page-head">
      <div>
        <h1 class="page-title">Payouts</h1>
        <p class="page-sub">Next payout lands in 3 days. You're paid every Friday.</p>
      </div>
      <div class="segmented" role="group" aria-label="Period">
        <button aria-pressed="false">Daily</button>
        <button aria-pressed="true">Weekly</button>
        <button aria-pressed="false">Monthly</button>
      </div>
    </div>
```

### 4.4 Stat cards
Source: `dashboard.html`
```html
<section class="grid grid-3">
      <article class="card">
        <div class="stat-head"><span class="tile"><svg class="icon icon-sm"><use href="#i-calendar"/></svg></span>Next payout<span class="chip chip-accent">Fri, 25 Sep</span></div>
        <p class="stat-value">$6,248</p>
        <p class="stat-foot">From 58 orders this week</p>
      </article>
      <article class="card">
        <div class="stat-head"><span class="tile"><svg class="icon icon-sm"><use href="#i-wallet"/></svg></span>Available balance</div>
        <p class="stat-value">$7,910</p>
        <p class="stat-foot">Updated hourly</p>
      </article>
      <article class="card">
        <div class="stat-head"><span class="tile"><svg class="icon icon-sm"><use href="#i-trending-up"/></svg></span>Paid out in September</div>
        <p class="stat-value">$41,320</p>
        <p class="stat-foot"><span class="chip chip-success"><svg class="icon icon-sm"><use href="#i-arrow-up"/></svg>9.4%</span>compared with August</p>
      </article>
    </section>
```

### 4.5 Table panel
Source: `dashboard.html`
```html
<section class="panel">
        <div class="panel-head">
          <div><h2 class="panel-title">Payout history</h2></div>
          <a href="#" class="link">View statements</a>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead><tr><th>Date</th><th>Payout</th><th class="end">Net amount</th><th>Account</th><th>Status</th><th></th></tr></thead>
            <tbody>
              <tr><td class="strong">25 Sep 2026</td><td class="muted">PO-3108</td><td class="end strong num">$6,248</td><td class="muted">BCA ••• 4410</td><td><span class="chip chip-warning">Scheduled</span></td><td class="end"><a class="row-link" href="#" aria-label="Open PO-3108"><svg class="icon icon-sm"><use href="#i-chev-right"/></svg></a></td></tr>
              <tr><td class="strong">18 Sep 2026</td><td class="muted">PO-3094</td><td class="end strong num">$5,730</td><td class="muted">BCA ••• 4410</td><td><span class="chip chip-info">In transit</span></td><td class="end"><a class="row-link" href="#" aria-label="Open PO-3094"><svg class="icon icon-sm"><use href="#i-chev-right"/></svg></a></td></tr>
              <tr><td class="strong">11 Sep 2026</td><td class="muted">PO-3071</td><td class="end strong num">$6,015</td><td class="muted">BCA ••• 4410</td><td><span class="chip chip-success">Paid</span></td><td class="end"><a class="row-link" href="#" aria-label="Open PO-3071"><svg class="icon icon-sm"><use href="#i-chev-right"/></svg></a></td></tr>
              <tr><td class="strong">4 Sep 2026</td><td class="muted">PO-3052</td><td class="end strong num">$4,862</td><td class="muted">BCA ••• 4410</td><td><span class="chip chip-success">Paid</span></td><td class="end"><a class="row-link" href="#" aria-label="Open PO-3052"><svg class="icon icon-sm"><use href="#i-chev-right"/></svg></a></td></tr>
              <tr><td class="strong">28 Aug 2026</td><td class="muted">PO-3036</td><td class="end strong num">$5,407</td><td class="muted">BCA ••• 4410</td><td><span class="chip chip-danger">Returned</span></td><td class="end"><a class="row-link" href="#" aria-label="Open PO-3036"><svg class="icon icon-sm"><use href="#i-chev-right"/></svg></a></td></tr>
              <tr><td class="strong">21 Aug 2026</td><td class="muted">PO-3019</td><td class="end strong num">$4,998</td><td class="muted">BCA ••• 4410</td><td><span class="chip chip-success">Paid</span></td><td class="end"><a class="row-link" href="#" aria-label="Open PO-3019"><svg class="icon icon-sm"><use href="#i-chev-right"/></svg></a></td></tr>
            </tbody>
          </table>
        </div>
        <div class="panel-foot">6 of 38 payouts</div>
      </section>
```

### 4.6 Summary card
Source: `dashboard.html`
```html
<section class="panel">
          <div class="panel-head"><h2 class="panel-title">Next payout</h2><button class="btn btn-ghost btn-sm btn-icon" aria-label="More options"><svg class="icon"><use href="#i-dots"/></svg></button></div>
          <div class="panel-body">
            <p class="big-number">$6,248</p>
            <p class="muted" style="margin-top:6px">Arrives Friday, 25 September</p>
            <div class="rows">
              <div class="row"><span>Gross sales</span><b>$6,412</b></div>
              <div class="row"><span>Platform fee (2%)</span><b class="neg">−$128</b></div>
              <div class="row"><span>Card fees (58 × $0.63)</span><b class="neg">−$36</b></div>
            </div>
            <div class="row" style="margin-bottom:16px"><span style="color:var(--ink);font-weight:600">Net payout</span><b>$6,248</b></div>
            <button class="btn btn-solid btn-block">View schedule</button>
          </div>
        </section>
```

### 4.7 Plan card
Source: `dashboard.html`
```html
<section class="plan-card">
          <div class="row" style="color:inherit"><strong>Payout account</strong><span class="chip">Default</span></div>
          <p class="big-number">•••• 4410</p>
          <div class="plan-meta"><div>Account holder<b>Juniper Goods</b></div><div style="text-align:right">Next payout<b>25 Sep</b></div></div>
        </section>
```

### 4.8 Chart card
Source: `dashboard.html`
```html
<section class="card" style="margin-top:var(--gap)">
      <div class="topbar">
        <div><h2 class="panel-title">Weekly volume</h2><p class="panel-sub">Gross sales and payouts, last 6 weeks</p></div>
        <div class="legend"><span><i class="dot" style="color:var(--surface-3)"></i>Gross</span><span><i class="dot" style="color:var(--accent)"></i>Paid out</span></div>
      </div>
      <div class="bars">
        <div class="bar"><i style="height:30%"></i><i style="height:42%"></i><span>W34</span></div>
        <div class="bar"><i style="height:22%"></i><i style="height:48%"></i><span>W35</span></div>
        <div class="bar"><i style="height:34%"></i><i style="height:38%"></i><span>W36</span></div>
        <div class="bar"><i style="height:18%"></i><i style="height:52%"></i><span>W37</span></div>
        <div class="bar"><i style="height:26%"></i><i style="height:47%"></i><span>W38</span></div>
        <div class="bar"><i style="height:24%"></i><i style="height:55%"></i><span>W39</span></div>
      </div>
    </section>
```

### 4.9 Settings dialog
Source: `settings.html`
```html
<div class="dialog" role="dialog" aria-labelledby="dlg-title">
  <aside class="dialog-side">
    <p class="nav-label" style="padding-top:0">rani@junipergoods.co</p>
    <div class="segmented" role="group" aria-label="Settings scope">
      <button aria-pressed="false">Account</button>
      <button aria-pressed="true">Workspace</button>
    </div>
    <nav>
      <a href="#" class="nav-item"><svg class="icon"><use href="#i-trending-up"/></svg>Usage</a>
      <a href="#" class="nav-item"><svg class="icon"><use href="#i-building"/></svg>Workspace details</a>
      <a href="#" class="nav-item"><svg class="icon"><use href="#i-shield-check"/></svg>Security</a>
      <a href="#" class="nav-item"><svg class="icon"><use href="#i-user"/></svg>Members</a>
      <a href="#" class="nav-item is-active"><svg class="icon"><use href="#i-users"/></svg>Teams</a>
      <a href="#" class="nav-item"><svg class="icon"><use href="#i-lock"/></svg>Roles</a>
      <a href="#" class="nav-item"><svg class="icon"><use href="#i-grid"/></svg>Integrations</a>
    </nav>
  </aside>
  <section class="dialog-main">
    <header class="dialog-head">
      <div><h2 class="page-title" id="dlg-title" style="font-size:20px">Teams</h2><p class="page-sub">Group people so you can share access in one step.</p></div>
      <button class="btn btn-ghost btn-icon" aria-label="Close settings"><svg class="icon"><use href="#i-x"/></svg></button>
    </header>
    <div class="dialog-body">
      <div class="toolbar">
        <label class="input-group"><svg class="icon icon-sm"><use href="#i-search"/></svg><input class="input" type="search" placeholder="Search teams" aria-label="Search teams" /></label>
        <select class="select" style="width:auto" aria-label="Filter by access"><option>Access: All</option><option>Owner</option><option>Editor</option><option>Viewer</option></select>
      </div>
      <div class="panel">
        <div class="table-wrap">
          <table class="table">
            <thead><tr><th>Team</th><th>Status</th><th>Access</th><th>Members</th><th></th></tr></thead>
            <tbody>
              <tr><td class="strong">Operations</td><td><span class="chip chip-success"><i class="dot"></i>Active</span></td><td><span class="chip chip-outline">Owner</span></td><td><div class="cell"><div class="avatar-stack"><span class="avatar avatar-sm" style="background:#6b5b95">DS</span><span class="avatar avatar-sm" style="background:#3f7d6e">AK</span><span class="avatar avatar-sm" style="background:#a0664b">RL</span></div><span class="muted">6 members</span></div></td><td class="end"><button class="row-link" aria-label="Team options"><svg class="icon icon-sm"><use href="#i-dots"/></svg></button></td></tr>
              <tr><td class="strong">Finance</td><td><span class="chip chip-success"><i class="dot"></i>Active</span></td><td><span class="chip chip-outline">Editor</span></td><td><div class="cell"><div class="avatar-stack"><span class="avatar avatar-sm" style="background:#2f5d8a">NW</span><span class="avatar avatar-sm" style="background:#7a6a3b">TP</span></div><span class="muted">3 members</span></div></td><td class="end"><button class="row-link" aria-label="Team options"><svg class="icon icon-sm"><use href="#i-dots"/></svg></button></td></tr>
              <tr><td class="strong">Customer care</td><td><span class="chip chip-success"><i class="dot"></i>Active</span></td><td><span class="chip chip-outline">Editor</span></td><td><div class="cell"><div class="avatar-stack"><span class="avatar avatar-sm" style="background:#8a4a6b">MY</span><span class="avatar avatar-sm" style="background:#4a6b8a">HB</span><span class="avatar avatar-sm" style="background:#4a7a3b">IS</span></div><span class="muted">14 members</span></div></td><td class="end"><button class="row-link" aria-label="Team options"><svg class="icon icon-sm"><use href="#i-dots"/></svg></button></td></tr>
              <tr><td class="strong">Warehouse</td><td><span class="chip chip-warning"><i class="dot"></i>Invite pending</span></td><td><span class="chip chip-outline">Viewer</span></td><td><div class="cell"><div class="avatar-stack"><span class="avatar avatar-sm" style="background:#6b6b6b">GF</span></div><span class="muted">1 member</span></div></td><td class="end"><button class="row-link" aria-label="Team options"><svg class="icon icon-sm"><use href="#i-dots"/></svg></button></td></tr>
              <tr><td class="strong">Contractors</td><td><span class="chip"><i class="dot"></i>Paused</span></td><td><span class="chip chip-outline">Viewer</span></td><td><div class="cell"><span class="muted">No members</span></div></td><td class="end"><button class="row-link" aria-label="Team options"><svg class="icon icon-sm"><use href="#i-dots"/></svg></button></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <footer class="dialog-foot">
      <button class="btn btn-line">Cancel</button>
      <button class="btn btn-solid"><svg class="icon icon-sm"><use href="#i-plus"/></svg>Create team</button>
    </footer>
  </section>
</div>
```

### 4.10 Form section
Source: `form.html`
```html
<section style="margin-top:26px">
      <h2 class="panel-title">Listing details</h2>
      <p class="panel-sub">Shoppers see everything on this page.</p>

      <div class="form-row" style="margin-top:14px">
        <div><h3>Product name</h3><p>Keep it short. Shoppers scan names in search results.</p></div>
        <div class="form-control">
          <input class="input" value="Linen tote, natural" aria-label="Product name" />
          <span class="hint">19 of 60 characters</span>
        </div>
      </div>

      <div class="form-row">
        <div><h3>Sold as</h3><p>Pick every format you offer.</p></div>
        <div class="form-control">
          <label class="check"><input type="checkbox" checked /> Single item</label>
          <label class="check"><input type="checkbox" checked /> Bundle of 3</label>
          <label class="check"><input type="checkbox" /> Wholesale case</label>
          <label class="check"><input type="checkbox" /> Made to order</label>
        </div>
      </div>

      <div class="form-row">
        <div><h3>Ships from</h3><p>Used to estimate delivery times at checkout.</p></div>
        <div class="form-control">
          <label class="input-group"><svg class="icon icon-sm"><use href="#i-map-pin"/></svg><input class="input" value="Bandung" aria-label="City" /></label>
          <select class="select" aria-label="Country"><option>Indonesia</option><option>Singapore</option><option>Malaysia</option></select>
        </div>
      </div>

      <div class="form-row">
        <div><h3>Collections</h3><p>Choose up to 5. Collections decide where the product appears in your store.</p></div>
        <div class="form-control">
          <div class="tags"><span class="chip chip-accent">Bags</span><span class="chip chip-accent">Everyday carry</span><span class="chip chip-accent">Natural fibres</span></div>
          <label class="input-group"><svg class="icon icon-sm"><use href="#i-search"/></svg><input class="input" placeholder="Search collections" aria-label="Search collections" /></label>
        </div>
      </div>

      <div class="form-row">
        <div><h3>Price</h3><p>Before tax. You can add discounts later.</p></div>
        <div class="form-control">
          <input class="input is-error" value="0" aria-label="Price" aria-describedby="price-error" />
          <span class="error-text" id="price-error">Enter a price above 0 to publish this listing.</span>
        </div>
      </div>
    </section>
```

### 4.11 Auth split
Source: `auth.html`
```html
<div class="auth">
  <section class="auth-form">
    <a href="#" class="logo"><span class="brand-mark"><svg class="icon"><use href="#i-logo"/></svg></span>Pixelproof</a>
    <div class="auth-inner">
      <h1 class="auth-title">Log in to your store</h1>
      <p class="muted">Pick up where you left off.</p>
      <form>
        <button type="button" class="btn btn-line btn-block"><svg class="icon icon-sm"><use href="#i-key"/></svg>Continue with single sign-on</button>
        <div class="divider">or use your email</div>
        <label class="field"><span class="label">Email</span><input class="input" type="email" placeholder="you@store.co" autocomplete="email" /></label>
        <label class="field"><span class="label">Password</span><span class="input-group"><input class="input" type="password" value="password123" autocomplete="current-password" style="padding-left:12px" /><button type="button" class="btn btn-ghost btn-sm btn-icon" style="position:absolute;right:4px;height:30px;width:30px" aria-label="Show password"><svg class="icon icon-sm"><use href="#i-eye"/></svg></button></span></label>
        <div class="auth-row"><label class="check"><input type="checkbox" checked /> Keep me signed in</label><a href="#" class="link">Forgot password?</a></div>
        <button class="btn btn-solid btn-block btn-lg">Log in</button>
      </form>
      <p class="auth-foot">New to Pixelproof? <a href="#" class="link">Create a store</a></p>
    </div>
  </section>
  <aside class="auth-aside">
    <span class="chip" style="align-self:flex-start;background:rgba(255,255,255,.16);color:inherit">Payouts every Friday</span>
    <div>
      <p class="auth-quote">Every order, payout and refund in one calm place.</p>
      <div class="mini">
        <div class="stat-head"><span class="tile tile-accent"><svg class="icon icon-sm"><use href="#i-wallet"/></svg></span>Next payout<span class="chip chip-success">On time</span></div>
        <p class="stat-value" style="font-size:28px">$6,248</p>
        <div class="progress"><i style="width:72%"></i></div>
        <p class="stat-foot" style="margin-top:8px">58 orders settled, 3 still in review</p>
      </div>
    </div>
  </aside>
</div>
```

### 4.12 Otp card
Source: `auth-states.html`
```html
<section class="card">
    <span class="tile tile-accent"><svg class="icon"><use href="#i-mail"/></svg></span>
    <h2 class="state-title">Check your email</h2>
    <p class="muted">We sent a 6-digit code to rani@junipergoods.co. It expires in 10 minutes.</p>
    <div class="otp" style="margin:20px 0">
      <input class="input" value="4" aria-label="Digit 1" /><input class="input" value="8" aria-label="Digit 2" /><input class="input" value="1" aria-label="Digit 3" /><input class="input" aria-label="Digit 4" /><input class="input" aria-label="Digit 5" /><input class="input" aria-label="Digit 6" />
    </div>
    <button class="btn btn-solid btn-block">Verify code</button>
    <p class="auth-foot" style="margin-top:14px">Didn't get it? <a href="#" class="link">Send a new code</a></p>
  </section>
```

### 4.13 Reset card
Source: `auth-states.html`
```html
<section class="card">
    <span class="tile tile-accent"><svg class="icon"><use href="#i-key"/></svg></span>
    <h2 class="state-title">Reset your password</h2>
    <p class="muted">Enter the email you log in with. We'll send a reset link.</p>
    <div class="alert alert-danger" style="margin-top:16px"><svg class="icon icon-sm"><use href="#i-info"/></svg><span>No account uses rani@junipergods.co. Check the spelling or create a store.</span></div>
    <label class="field" style="margin:14px 0"><span class="label">Email</span><input class="input is-error" value="rani@junipergods.co" /></label>
    <button class="btn btn-solid btn-block">Send reset link</button>
  </section>
```

### 4.14 Register card
Source: `auth-states.html`
```html
<section class="card">
    <span class="tile tile-accent"><svg class="icon"><use href="#i-store"/></svg></span>
    <h2 class="state-title">Create your store</h2>
    <p class="muted">Free for your first 50 orders.</p>
    <form style="display:grid;gap:12px;margin-top:16px">
      <div class="grid grid-2" style="gap:10px"><label class="field"><span class="label">First name</span><input class="input" value="Rani" /></label><label class="field"><span class="label">Last name</span><input class="input" value="Aditya" /></label></div>
      <label class="field"><span class="label">Store name</span><input class="input" placeholder="Juniper Goods" /></label>
      <label class="field"><span class="label">Password</span><input class="input" type="password" value="longpassword" /><span class="hint">At least 12 characters.</span></label>
      <div class="alert alert-success"><svg class="icon icon-sm"><use href="#i-check"/></svg><span>Store name is available.</span></div>
      <button class="btn btn-solid btn-block">Create store</button>
    </form>
  </section>
```

### 4.15 Upload panel
Source: `upload.html`
```html
<section class="panel">
        <div class="panel-head"><div><h2 class="panel-title">Upload documents</h2><p class="panel-sub">PDF, JPG, PNG, DOCX or CSV, up to 25 MB each</p></div></div>
        <div class="panel-body">
          <label class="dropzone">
            <input type="file" class="sr-only" multiple />
            <span class="tile"><svg class="icon"><use href="#i-upload"/></svg></span>
            <strong><span>Click to upload</span> or drag files here</strong>
            <span class="hint">Files upload one at a time and keep going if you leave this page.</span>
          </label>
          <div class="files">
            <div class="file">
              <span class="file-type ft-pdf">PDF</span>
              <div><p class="file-name">tax-invoice-september.pdf</p><p class="file-meta">2.4 MB · Uploaded just now</p></div>
              <span class="chip chip-success"><svg class="icon icon-sm"><use href="#i-check"/></svg>Done</span>
            </div>
            <div class="file">
              <span class="file-type ft-img">JPG</span>
              <div><p class="file-name">tote-natural-front.jpg</p><p class="file-meta">6.1 of 8.4 MB · about 20 seconds left</p><div class="progress" role="progressbar" aria-valuenow="72" aria-valuemin="0" aria-valuemax="100"><i style="width:72%"></i></div></div>
              <button class="btn btn-ghost btn-sm btn-icon" aria-label="Cancel upload"><svg class="icon icon-sm"><use href="#i-x"/></svg></button>
            </div>
            <div class="file is-error">
              <span class="file-type ft-doc">DOC</span>
              <div><p class="file-name">supplier-agreement-2026.docx</p><p class="file-meta">31 MB is over the 25 MB limit. Compress it or upload a PDF.</p></div>
              <button class="btn btn-line btn-sm"><svg class="icon icon-sm"><use href="#i-refresh"/></svg>Retry</button>
            </div>
            <div class="file">
              <span class="file-type ft-csv">CSV</span>
              <div><p class="file-name">stock-count-week-38.csv</p><p class="file-meta">Waiting to upload</p><div class="progress"><i style="width:0%"></i></div></div>
              <button class="btn btn-ghost btn-sm btn-icon" aria-label="Remove file"><svg class="icon icon-sm"><use href="#i-trash"/></svg></button>
            </div>
          </div>
        </div>
      </section>
```

### 4.16 File grid
Source: `upload.html`
```html
<section class="panel">
        <div class="panel-head"><h2 class="panel-title">Recent</h2><a href="#" class="link">See all</a></div>
        <div class="panel-body thumbs" style="grid-template-columns:repeat(2,minmax(0,1fr))">
          <figure class="thumb"><div class="thumb-art a1"><svg class="icon icon-lg"><use href="#i-image"/></svg></div><figcaption class="thumb-cap">tote-front.jpg<small>8.4 MB</small></figcaption></figure>
          <figure class="thumb"><div class="thumb-art a2"><svg class="icon icon-lg"><use href="#i-image"/></svg></div><figcaption class="thumb-cap">tote-detail.jpg<small>5.2 MB</small></figcaption></figure>
          <figure class="thumb"><div class="thumb-art"><svg class="icon icon-lg"><use href="#i-file"/></svg></div><figcaption class="thumb-cap">invoice-0913.pdf<small>1.1 MB</small></figcaption></figure>
          <figure class="thumb"><div class="thumb-art a3"><svg class="icon icon-lg"><use href="#i-image"/></svg></div><figcaption class="thumb-cap">lookbook-cover.png<small>3.7 MB</small></figcaption></figure>
        </div>
      </section>
```

### 4.17 Empty state
Source: `upload.html`
```html
<section class="card card-soft" style="margin-top:var(--gap);text-align:center;padding:40px">
      <span class="tile" style="margin:0 auto"><svg class="icon"><use href="#i-folder"/></svg></span>
      <h2 class="state-title">No shared files yet</h2>
      <p class="muted">Files you share with your accountant show up here.</p>
      <button class="btn btn-line" style="margin-top:16px">Share a file</button>
    </section>
```

### 4.18 Site nav
Source: `landing.html`
```html
<header class="site-nav">
      <a href="#" class="logo"><span class="brand-mark"><svg class="icon"><use href="#i-logo"/></svg></span>Pixelproof</a>
      <nav aria-label="Main"><a href="#">Product</a><a href="#">Payouts</a><a href="#">Pricing</a><a href="#">Help</a></nav>
      <div class="actions"><a href="#" class="btn btn-line btn-sm">Log in</a><a href="#" class="btn btn-solid btn-sm">Open a store</a></div>
    </header>
```

### 4.19 Hero
Source: `landing.html`
```html
<section class="hero">
      <span class="chip chip-accent">New: payouts every Friday</span>
      <h1>Run your shop from one quiet screen</h1>
      <p>Orders, payouts and stock for independent brands. Pixelproof does the tallying so you can get back to making things.</p>
      <div class="actions"><a href="#" class="btn btn-solid btn-lg">Open a free store</a><a href="#" class="btn btn-line btn-lg"><svg class="icon icon-sm"><use href="#i-play"/></svg>Watch the 2-minute tour</a></div>

      <div class="hero-shot" data-preset="lumen" aria-hidden="true">
        <div class="shell">
          <aside class="side">
            <div class="side-brand"><span class="brand-mark"><svg class="icon"><use href="#i-logo"/></svg></span><div><small>Pixelproof</small><strong>Juniper Goods</strong></div></div>
            <p class="nav-label">Store</p>
            <span class="nav-item"><svg class="icon"><use href="#i-home"/></svg>Home</span>
            <span class="nav-item"><svg class="icon"><use href="#i-cart"/></svg>Orders<span class="badge">12</span></span>
            <span class="nav-item is-active"><svg class="icon"><use href="#i-wallet"/></svg>Payouts</span>
            <span class="nav-item"><svg class="icon"><use href="#i-package"/></svg>Products</span>
          </aside>
          <div class="main">
            <div class="page-head" style="margin-top:4px"><div><p class="page-title">Payouts</p><p class="page-sub">Next payout lands in 3 days.</p></div></div>
            <div class="grid grid-3">
              <div class="card"><div class="stat-head"><span class="tile"><svg class="icon icon-sm"><use href="#i-calendar"/></svg></span>Next payout</div><p class="stat-value">$6,248</p><p class="stat-foot">58 orders</p></div>
              <div class="card"><div class="stat-head"><span class="tile"><svg class="icon icon-sm"><use href="#i-wallet"/></svg></span>Balance</div><p class="stat-value">$7,910</p><p class="stat-foot">Updated hourly</p></div>
              <div class="card"><div class="stat-head"><span class="tile"><svg class="icon icon-sm"><use href="#i-trending-up"/></svg></span>September</div><p class="stat-value">$41,320</p><p class="stat-foot"><span class="chip chip-success">9.4%</span></p></div>
            </div>
          </div>
        </div>
      </div>
    </section>
```

### 4.20 Logo strip
Source: `landing.html`
```html
<div class="logos" aria-label="Brands using Pixelproof"><span>Northpeak</span><span>fieldnote</span><span>OAKWELL</span><span>Brightline</span><span>Marrow&amp;Co</span></div>
```

### 4.21 Bento
Source: `landing.html`
```html
<section class="section">
      <div class="section-head"><h2>Everything a small shop does in a week</h2><p>Four jobs that used to live in four tabs.</p></div>
      <div class="bento">
        <article class="card">
          <div class="art"><div class="mini" style="width:min(100%,460px)">
            <div class="file" style="border:0;padding:0 0 10px"><span class="file-type ft-pdf">PDF</span><div><p class="file-name">tax-invoice-september.pdf</p><p class="file-meta">Matched to 58 orders</p></div><span class="chip chip-success">Done</span></div>
            <div class="file" style="border:0;padding:10px 0 0;border-top:1px solid var(--line)"><span class="file-type ft-csv">CSV</span><div><p class="file-name">stock-count-week-38.csv</p><div class="progress"><i style="width:64%"></i></div></div><span class="chip">64%</span></div>
          </div></div>
          <h3>Paperwork that files itself</h3>
          <p>Drop invoices and stock sheets in. Pixelproof matches them to orders and flags anything that doesn't add up.</p>
        </article>
        <article class="card">
          <div class="art"><div class="chat"><div class="bubble">Where's order #4471?</div><div class="bubble me">Out for delivery, arriving before 5 pm.</div></div></div>
          <h3>Answers customers get on their own</h3>
          <p>Order status replies go out automatically, in your tone.</p>
        </article>
        <article class="card">
          <div class="art"><div class="bars" style="height:120px;width:100%;margin:0"><div class="bar"><i style="height:30%"></i><i style="height:40%"></i></div><div class="bar"><i style="height:20%"></i><i style="height:55%"></i></div><div class="bar"><i style="height:26%"></i><i style="height:48%"></i></div><div class="bar"><i style="height:18%"></i><i style="height:66%"></i></div></div></div>
          <h3>Weekly numbers, no spreadsheet</h3>
          <p>Sales, fees and payouts, reconciled every Monday.</p>
        </article>
        <article class="card">
          <div class="art"><div class="flow"><span class="chip chip-accent">New wholesale order</span><div class="flow-row"><span class="chip chip-outline">Reserve stock</span><span class="chip chip-outline">Send invoice</span></div><span class="chip chip-success">Ready to pack</span></div></div>
          <h3>Rules for the busywork</h3>
          <p>Reserve stock and send invoices the moment an order lands.</p>
        </article>
        <article class="card">
          <div class="art"><div class="plan-card" style="width:min(100%,280px)"><div class="row" style="color:inherit"><strong>Payout account</strong><span class="chip">Default</span></div><p class="big-number" style="margin:18px 0 0">•••• 4410</p></div></div>
          <h3>Paid on a schedule you can plan around</h3>
          <p>Every Friday, straight to your local bank.</p>
        </article>
      </div>
    </section>
```

### 4.22 Steps
Source: `landing.html`
```html
<section class="section">
      <div class="section-head"><h2>Open your store this afternoon</h2></div>
      <div class="steps">
        <div class="step"><h3>Add your products</h3><p>Import a spreadsheet or photograph your shelf. We fill in the details.</p></div>
        <div class="step"><h3>Connect your bank</h3><p>Verify once. Payouts start the Friday after your first sale.</p></div>
        <div class="step"><h3>Share your link</h3><p>Sell from your store page, Instagram or a QR code at the counter.</p></div>
      </div>
    </section>
```

### 4.23 Testimonial
Source: `landing.html`
```html
<section class="section">
      <figure class="quote">
        <blockquote>“Friday used to be spreadsheet day. Now it's the day the money shows up and I don't think about it.”</blockquote>
        <figcaption><span class="avatar avatar-lg" style="background:#7a5a48">DP</span><span><b>Dewi Prameswari</b><small>Founder, Kain Pagi</small></span></figcaption>
      </figure>
    </section>
```

### 4.24 Pricing
Source: `landing.html`
```html
<section class="section">
      <div class="section-head"><h2>Pay when you sell</h2><p>No setup fee. Cancel whenever you like.</p></div>
      <div class="pricing">
        <article class="card price">
          <h3 class="panel-title">Starter</h3>
          <p class="price-amount">$0 <small>/ month</small></p>
          <p class="muted">For your first 50 orders.</p>
          <ul><li><svg class="icon icon-sm"><use href="#i-check"/></svg>Store page and checkout</li><li><svg class="icon icon-sm"><use href="#i-check"/></svg>Weekly payouts</li><li><svg class="icon icon-sm"><use href="#i-check"/></svg>3% per order</li></ul>
          <a href="#" class="btn btn-line btn-block">Start free</a>
        </article>
        <article class="card price is-featured">
          <div class="row" style="color:inherit"><h3 class="panel-title">Studio</h3><span class="chip chip-accent">Most shops</span></div>
          <p class="price-amount">$24 <small>/ month</small></p>
          <p class="muted">For shops with steady weekly orders.</p>
          <ul><li><svg class="icon icon-sm"><use href="#i-check"/></svg>Everything in Starter</li><li><svg class="icon icon-sm"><use href="#i-check"/></svg>Automatic paperwork matching</li><li><svg class="icon icon-sm"><use href="#i-check"/></svg>1.8% per order</li></ul>
          <a href="#" class="btn btn-line btn-block">Choose Studio</a>
        </article>
        <article class="card price">
          <h3 class="panel-title">Wholesale</h3>
          <p class="price-amount">$79 <small>/ month</small></p>
          <p class="muted">For brands selling to other shops.</p>
          <ul><li><svg class="icon icon-sm"><use href="#i-check"/></svg>Everything in Studio</li><li><svg class="icon icon-sm"><use href="#i-check"/></svg>Trade price lists</li><li><svg class="icon icon-sm"><use href="#i-check"/></svg>1.2% per order</li></ul>
          <a href="#" class="btn btn-line btn-block">Choose Wholesale</a>
        </article>
      </div>
    </section>
```

### 4.25 Faq
Source: `landing.html`
```html
<section class="section">
      <div class="section-head"><h2>Questions shop owners ask</h2></div>
      <div class="faq">
        <details open><summary>When do I get paid?<svg class="icon"><use href="#i-plus"/></svg></summary><p>Every Friday, for all orders completed by the previous Tuesday. The first payout arrives the Friday after your first sale.</p></details>
        <details><summary>Can I bring my products from another platform?<svg class="icon"><use href="#i-plus"/></svg></summary><p>Yes. Upload the export file from your current store and Pixelproof maps the fields for you.</p></details>
        <details><summary>What happens if a customer asks for a refund?<svg class="icon"><use href="#i-plus"/></svg></summary><p>Approve it from the order page. The amount comes out of your next payout, and the customer gets an email right away.</p></details>
      </div>
    </section>
```

### 4.26 Cta band
Source: `landing.html`
```html
<section class="cta">
      <h2>Your next Friday could be payout day</h2>
      <p>Open a store in about ten minutes. No card needed.</p>
      <div class="actions"><a href="#" class="btn btn-solid btn-lg">Open a free store</a><a href="#" class="btn btn-line btn-lg">Talk to us</a></div>
    </section>
```

### 4.27 Footer
Source: `landing.html`
```html
<footer class="footer">
      <div><a href="#" class="logo"><span class="brand-mark"><svg class="icon"><use href="#i-logo"/></svg></span>Pixelproof</a><p>Orders, payouts and stock for independent brands.</p></div>
      <div><h4>Product</h4><ul><li><a href="#">Store page</a></li><li><a href="#">Payouts</a></li><li><a href="#">Paperwork</a></li></ul></div>
      <div><h4>Company</h4><ul><li><a href="#">About</a></li><li><a href="#">Careers</a></li><li><a href="#">Contact</a></li></ul></div>
      <div><h4>Legal</h4><ul><li><a href="#">Terms</a></li><li><a href="#">Privacy</a></li><li><a href="#">Cookies</a></li></ul></div>
    </footer>
```


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

Values below were read from the rendered slices at 1440px (`getComputedStyle` on each component's root element). Widths, and heights of content-driven blocks, are informational; everything else must match exactly. Text properties are listed only where they differ from `body`.

- **sidebar** (`.side`, dashboard): height `980px`, padding `16px 12px`, gap `4px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `16px`, background-color `rgb(248, 248, 250)`, width `264px`
- **topbar** (`.topbar`, dashboard): height `32px`, gap `12px`, width `1104px`
- **page-head** (`.page-head`, dashboard): height `54.1875px`, margin `22px 0px 18px`, gap `16px`, width `1104px`
- **stat-cards** (`.grid.grid-3`, dashboard): height `150px`, gap `12px`, width `1104px`
- **table-panel** (`.panel`, dashboard): height `412.594px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `752px`
- **summary-card** (`.panel`, dashboard): height `374.484px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `340px`
- **plan-card** (`.plan-card`, dashboard): height `159.688px`, padding `18px`, border-radius `12px`, box-shadow `rgba(110, 86, 248, 0.55) 0px 8px 20px -8px`, color `rgb(255, 255, 255)`, width `340px`
- **chart-card** (`.card`, dashboard): height `274.594px`, padding `16px`, margin `12px 0px 0px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `1104px`
- **settings-dialog** (`.dialog`, settings): height `515.297px`, margin `40px 230px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `16px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.18) 0px 12px 32px -12px`, width `980px`
- **form-section** (`.panel-title`, form): height `680.562px`, margin `26px 0px 0px`, width `1104px`
- **auth-split** (`.auth`, auth): height `1000px`, min-height `1000px`, padding `10px`, gap `10px`, width `1440px`
- **otp-card** (`.card`, auth-states): height `518.062px`, padding `28px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `465.33px`
- **reset-card** (`.card`, auth-states): height `518.062px`, padding `28px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `465.33px`
- **register-card** (`.card`, auth-states): height `518.062px`, padding `28px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `465.34px`
- **upload-panel** (`.panel`, upload): height `600.656px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `752px`
- **file-grid** (`.panel`, upload): height `419.312px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `340px`
- **empty-state** (`.card.card-soft`, upload): height `239.297px`, padding `40px`, margin `12px 0px 0px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `12px`, background-color `rgb(248, 248, 250)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `1104px`
- **site-nav** (`.site-nav`, landing): height `62px`, padding `8px 8px 8px 16px`, margin `12px 0px 0px`, gap `16px`, border-top `1px solid rgb(231, 230, 236)`, border-right `1px solid rgb(231, 230, 236)`, border-bottom `1px solid rgb(231, 230, 236)`, border-left `1px solid rgb(231, 230, 236)`, border-radius `16px`, background-color `rgb(255, 255, 255)`, box-shadow `rgba(22, 21, 31, 0.04) 0px 1px 2px 0px`, width `1160px`
- **hero** (`.hero`, landing): height `790.531px`, padding `88px 0px 0px`, width `1160px`
- **logo-strip** (`.logos`, landing): height `93px`, padding `56px 0px 8px`, gap `18px 48px`, color `rgb(107, 106, 120)`, font-size `20px`, font-weight `600`, letter-spacing `-0.6px`, line-height `29px`, width `1160px`
- **bento** (`.section`, landing): height `952.438px`, padding `96px 0px 0px`, width `1160px`
- **steps** (`.section`, landing): height `349.859px`, padding `96px 0px 0px`, width `1160px`
- **testimonial** (`.section`, landing): height `239.594px`, padding `96px 0px 0px`, width `1160px`
- **pricing** (`.section`, landing): height `525px`, padding `96px 0px 0px`, width `1160px`
- **faq** (`.section`, landing): height `431.781px`, padding `96px 0px 0px`, width `1160px`
- **cta-band** (`.cta`, landing): height `323.016px`, padding `64px 32px`, margin `96px 0px 0px`, border-radius `22px`, color `rgb(255, 255, 255)`, width `1160px`
- **footer** (`.footer`, landing): height `203.281px`, padding `56px 0px 40px`, margin `56px 0px 0px`, gap `24px`, border-top `1px solid rgb(231, 230, 236)`, width `1160px`
