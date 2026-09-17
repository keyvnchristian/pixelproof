# Spec, tokens, and plan (Step 5)

## Contents
1. Token inventory
2. Token architecture
3. Generating style-spec.md
4. Writing plan.md
5. GATE D summary

## 1. Token inventory

```bash
python <SKILL_DIR>/scripts/tokens.py docs/pixelproof/slices/shared.css --out docs/pixelproof/tokens.json --md
```

The output lists every distinct value, with its count and the rules that use it:
- spacing values (padding, margin, gap, inset)
- size values (width, height, min/max)
- font sizes, weights, line heights, letter spacing
- radii
- colors
- shadows

Use it to spot near-duplicates. If you find any, fix them in `shared.css` before building tokens.

## 2. Token architecture
Three layers. Components use only layers 2 and 3.

**Layer 1 — primitives:** raw values, named by value. One variable per distinct value in the inventory.
- Spacing: `--space-14: 14px`
- Sizes: `--size-42: 42px`
- Font sizes: `--font-size-16: 16px`
- Radii: `--radius-6: 6px`, plus named aliases if the slice already uses them
- Palette: `--crimson-600: #992c29`, `--gray-200: #ebedf0`, etc.
- Hairlines: `--border-width: 1px`

**Layer 2 — semantic:** meaning, not value. Keep the slice's own names so the CSS ports 1:1.
- Colors: `--primary`, `--text-2`, `--border`, `--bg-subtle`, …
- Control heights: `--control-h-md: var(--size-42)`, …
- Icon sizes and stroke width.
- Layout: sidebar width, page padding, vertical rhythm (`--stack-md`).
- Typography roles: page title, panel title, body, caption, label (size/weight/tracking).
- Effects: `--shadow-active`, `--focus-ring`, `--opacity-disabled`.

**Layer 3 — component:** declared at the top of each component block (`.tab { --tab-h: var(--control-h-tab); }`), so a variant changes one variable.

Other rules:
- **Breakpoints** can't be CSS variables in media queries. Define them once in a TS/JS constant, mirror them in the Tailwind `screens` config, and use only those values.
- **Theming:** a `[data-theme="x"]` block overrides only layer-2 color tokens.
- **JS access:** a `cssVar(name)` helper returns `var(--name)`, and `readToken(name)` resolves the value at runtime for canvas charts and map styles. Never copy hex values into JS.
- **Tailwind (if used):** map `theme` values to the variables (`primary: 'var(--primary)'`). Use utilities for page layout only; components use the spec classes.

## 3. Generating style-spec.md

```bash
python <SKILL_DIR>/scripts/build_spec.py docs/pixelproof \
  --template <SKILL_DIR>/assets/templates/style-spec.template.md \
  --out docs/pixelproof/style-spec.md
```

- **What the script fills in** (placeholders in the template):
  - `{{CSS}}`: the full `shared.css`
  - `{{SPRITE}}`: the full sprite
  - `{{ICON_TABLE}}`: id → path data
  - `{{COMPONENTS}}`: every `@component` block, each with a heading
  - `{{REFERENCES}}`: a table of the slices from the manifest
  - `{{VERIFY}}`: computed styles of each component's root element at 1440px, read from the rendered slices, so verification values are never typed by hand
- **What you write by hand**, before or after running the script. Replace the template's `<!-- WRITE: … -->` blocks:
  - Brand and color rules (which colors are allowed where), and the only allowed shadows and gradients.
  - Icon usage table: place → icon → size → color.
  - Notes per component: variants, when to use it, content rules (two-line cells, status as text or pills, etc.).
  - "Which pattern to use" table and the page layout order.
  - Measurement cheat sheet: borders (which sides, which elements have none) and height/padding/radius/font per element. Take these from `measurements.md` and the CSS.
  - Responsive rules (mark derived ones).
  - Additions (from Step 4), each labeled with the pattern it was derived from.
  - For restyles: "reference content is demo content; never copy it".

Keep the spec self-sufficient. Someone with only `style-spec.md` + the slices should be able to rebuild the UI exactly.

## 4. Writing plan.md
Start from `<SKILL_DIR>/assets/templates/plan.template.md`. Required sections:
1. **Stack wiring:** where tokens and global CSS live, font loading, the sprite/`Icon` component, and the Tailwind mapping.
2. **File structure:** every file to create or change, and the legacy files to delete.
3. **Component API:** name, props (variants/sizes), the classes each prop produces, the component tokens, and the spec section.
4. **Mapping** (restyle) or **build sheets** (new build):
   - **Restyle:** a table of current element → spec component that covers every element type in the app, plus a per-page inventory listing each page's actual elements and their mapped components. Flag anything that doesn't map cleanly as a question for the user.
   - **New build:** per screen, a table with columns Region | Component | Classes | Spacing | Size | Data | States.
5. **States:** loading skeletons (same size and radius as the element they replace, `--bg-chip`), empty state (inside the same frame, message + one action), error state (message + retry), and disabled state. All from tokens.
6. **Accessibility:** landmarks, labels, aria states, focus order, and contrast notes.
7. **Batches:** 1–3 screens each, shell first.
8. **Risks:** anything that could break behavior, and how to avoid it.

## 5. GATE D summary format

```
Spec & plan ready
- Tokens: N spacing, N sizes, N font sizes, N colors (primary <hex>) → 3-layer theme in <paths>
- Components: <list>
- Patterns: <status tabs, grouped table, data table, summary cards, …>
- Additions: <list, each with its source pattern>
- Mapping highlights: <old element → new component> (…)
- Needs your decision: <items that don't map cleanly>
- Batches: 1) … 2) … 3) …
Files: docs/pixelproof/style-spec.md, plan.md, tokens.json
Approve / Request changes / Implement directly?
```
