# Pixelproof

**Pixel-exact UI from design references.** Give your coding agent a screenshot, a Dribbble shot, a Figma export, or a `design.md`, and get the *same* padding, borders, type, table style, and icons in your codebase, not an approximation. Then audit, roast, and verify your frontend with evidence.

```bash
npx pixelproof
```

## Why
When an agent builds straight from an image, it guesses spacing and swaps icons, and the result drifts into generic UI. Pixelproof adds a measured step in between:

```
reference image(s) → measurements → HTML+CSS slice (the contract) → style spec + tokens + plan → your code → parity checks
```

At every step it shows you a preview (PNG/HTML) and waits for your choice:
- **Approve**
- **Request changes**
- **Implement directly**

It also asks up front which menus, features, or sections you want added in the same style.

## Install

### Option 1: npx (Claude Code, Codex, other agents)
```bash
npx pixelproof                    # interactive: pick tool(s) and global/local
npx pixelproof install --global   # ~/.claude/skills/pixelproof
npx pixelproof install --local    # ./.claude/skills/pixelproof (this project only)
npx pixelproof install --global --claude --codex
npx pixelproof update             # get the latest version
npx pixelproof uninstall --global
npx pixelproof doctor             # check Python / Playwright requirements
```

### Option 2: Claude Code plugin
Inside Claude Code:
```
/plugin marketplace add keyvnchristian/pixelproof
/plugin install pixelproof@pixelproof
```
Update later with `/plugin marketplace update pixelproof`.

### Option 3: skills CLI
```bash
npx skills add keyvnchristian/pixelproof
```

### Requirements
- Node 18+ (installer and parity checks)
- Python 3.9+ with `pillow`, `numpy`, and `playwright`, plus Chromium:
  ```bash
  pip install pillow numpy playwright && python -m playwright install chromium
  ```
- For app parity checks, in your project: `npm i -D playwright`

Run `npx pixelproof doctor` to see what's missing.

## Commands
Run these inside Claude Code. The plugin install uses the prefix `/pixelproof:pixelproof`. You can also just describe what you want, and Pixelproof picks the matching command.

| Command | What it does | Edits code? |
|---|---|---|
| `/pixelproof teach` | One-time interview: product, users, brand, rules → `docs/pixelproof/context.md` (run this first) | No |
| `/pixelproof enhance [looks\|perf\|structure]` | Lift your existing app's borders, boldness, font sizes, and layout toward a reference (or a built-in preset if you have none), speed up pages, or split god components, with before/after proof | After your approval |
| `/pixelproof replicate <refs…>` | Build exactly from screenshots, Dribbble shots, or a `design.md` (the default) | After your approval |
| `/pixelproof extract [--url]` | Reverse-engineer your current UI into slices, tokens, and a style spec | No |
| `/pixelproof add "<what>"` | Add a page, section, or menu in the established style | After your approval |
| `/pixelproof theme "<change>"` | Rebrand globally: color, font, radius, density (tokens only) | After your approval |
| `/pixelproof audit [path]` | Design-consistency audit: scored tables (category scores, findings by severity, strengths), evidence, and an HTML report | No (offers fixes) |
| `/pixelproof roast [url\|path]` | Brutally honest, funny critique with slop bingo and a Slop Score (`--spicy` optional) | No (offers fixes) |
| `/pixelproof compare <ref> <url>` | Quick drift check of one page against one reference | No |
| `/pixelproof verify [page\|all]` | Parity, token, overflow, and icon checks | No |
| `/pixelproof responsive [url]` | Breakpoint torture test: overflow, clipped text, tap targets, tiny fonts | No |
| `/pixelproof status` | Progress, gates, audit trend, next step | No |
| `/pixelproof help` | Show the commands | No |

Start with `/pixelproof teach`: it takes about 2 minutes, and every other command asks fewer questions afterwards.

Examples:

> `/pixelproof replicate refs/orders.png "primary #992c29"`

> `/pixelproof roast http://localhost:3000`

> Restyle our whole admin to match these two screenshots. Keep all our pages and columns.

### What `replicate` does

| Step | What you see | Your choice |
|---|---|---|
| 1. Intake | Summary of references, scope, brand, stack, additions | Approve / change |
| 2. Measure | Measurement log (image px → CSS px) | — |
| 3. Slice | PNG previews at 1440/1024/390, the HTML file, and a side-by-side comparison with the reference | Approve / change / implement directly |
| 4. Additions | Previews of the menus/sections you asked for, built from the same style values | Approve / change / implement directly |
| 5. Spec & plan | `style-spec.md`, `tokens.json`, `plan.md` (element mapping for existing apps) | Approve / change / implement directly |
| 6. Implement | Per batch: app screenshots next to the slices, parity report, token check | Continue / change / implement the rest directly |

Everything is saved in your project under `docs/pixelproof/`, so future sessions (and teammates) reuse the same source of truth.

## What's inside
| Path | What |
|---|---|
| `skills/pixelproof/SKILL.md` | Command router and shared rules |
| `skills/pixelproof/commands/` | One playbook per command |
| `skills/pixelproof/references/` | Intake, measuring, slicing, spec/plan, implementation, and verification guides |
| `scripts/measure.py` | Scale detection, palette, pixel samples, border lines, content boxes |
| `scripts/assemble.py` | Self-contained slice pages from shared CSS, sprite, and partials |
| `scripts/render.py` | Screenshots plus overflow, missing-icon, undefined-class, and console checks; `--deep` adds tap-target, clipping, contrast, alt-text, and label checks |
| `scripts/compare.py` | Reference vs render side-by-side, overlay, and divider drift report |
| `scripts/tokens.py` | Inventory of every design value |
| `scripts/structure_scan.py` | Finds god components and suggests splits |
| `scripts/perf_scan.py` | Static perf smells plus LCP, CLS, TBT, and transfer size from a real browser |
| `scripts/audit_scan.py` | Static scan: colors, spacing, type, radii, shadows, icon libraries, duplicate components, inline styles |
| `scripts/report.py` | Shareable HTML reports for audit, roast, verify, and responsive |
| `scripts/build_spec.py` | Generates the style spec, with verification values read from rendered slices |
| `scripts/check_parity.mjs` | Computed-style diff between slice and your running app |
| `scripts/check_tokens.mjs` | Fails on raw colors or px values outside your theme |
| `assets/presets/` | Lumen, Linen, and Nocturne presets, the reference gallery, and SPEC.md |
| `assets/` | Starter icon sprite (77 icons), starter CSS, templates |

(The `scripts/` and `assets/` paths are inside `skills/pixelproof/`.)

## Built-in presets
Three original styles ship with Pixelproof, and `enhance looks` uses them:

| Preset | Feel |
|---|---|
| **Lumen** | Light floating panels, violet actions, dense data. Built for dashboards and tools. |
| **Linen** | Warm neutrals, big rounding, black pill buttons, large numerals |
| **Nocturne** | Dark indigo marketing with a glow, pairs with Lumen screenshots |

Each covers a dashboard, settings, forms, auth (login, OTP, reset, register), file upload, and a full landing page. To see them all, open `skills/pixelproof/assets/presets/gallery/build/index.html`; it has page and preset switchers. Every page passes contrast, tap-target, text-size, and overflow checks at desktop, tablet, and mobile widths.

## Third-party references
Pixelproof replicates layout and visual language. For third-party shots, it replaces brand names, logos, photos, illustrations, and copy with your own content or neutral placeholders.

## Changelog
See [CHANGELOG.md](CHANGELOG.md).

## License
MIT
