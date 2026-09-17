# Slice (Step 3)

A slice is a self-contained HTML page that renders one reference screen from `shared.css` + `sprite.svg`. It is the contract the codebase is built and verified against.

## Contents
1. File layout and assembly
2. CSS rules
3. Markup and component markers
4. Icons
5. Content, brand, and IP rules
6. Responsive rules
7. The measure → fix loop
8. GATE B preview

## 1. File layout and assembly

```
slices/
  shared.css            # tokens on :root, then components; one file for all screens
  sprite.svg            # <svg width="0" height="0" style="position:absolute">…<symbol id="i-…">…</svg>
  partials/sidebar.html # reusable markup
  list.body.html        # the page body (everything inside <body>, except the sprite)
  manifest.json
```

`manifest.json`:
```json
{
  "font_href": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
  "lang": "en",
  "screens": [
    { "name": "list", "title": "Orders", "body": "list.body.html" },
    { "name": "dashboard", "title": "Dashboard", "body": "dashboard.body.html" },
    { "name": "additions", "title": "Additions", "body": "additions.body.html" }
  ]
}
```

- **Partials:** inside a body file, `<!-- include: partials/sidebar.html -->` inserts a partial. `{{active:orders}}` in the include line sets a variable the partial can use: in the partial, write `{{#active=orders}} is-active{{/active}}` to add a class only on the matching screen.
- **Assemble:** `python scripts/assemble.py docs/pixelproof/slices` writes `<name>.html` for each screen, with the CSS inlined and the sprite embedded.

## 2. CSS rules
- **Starting point:** `assets/templates/shared.starter.css`: reset, `.icon`, focus ring, and a token block to fill in.
- **Tokens:** all colors and repeated values on `:root`, with semantic names (`--primary`, `--text-2`, `--border`, `--bg-subtle`…). Components reference tokens for colors. Sizes and spacing can be literal px inside the slice; Step 5 turns them into tokens.
- **Selectors:** one class per component and part, BEM-light (`.order`, `.order-head`, `.order-row`). Variants are modifier classes (`.btn-primary`, `.is-active`). No IDs, no deep descendant chains, no `!important`.
- **Surfaces:** no shadows or gradients unless measured in the reference. If they exist, make them tokens and list exactly where they're allowed.
- **Group by component**, with a comment header per group (`/* ===== Order table ===== */`). `build_spec.py` uses these headers.
- **Alignment:** make grids explicit (`grid-template-columns` in `fr`) when the header and rows must line up. Compensate for card borders (e.g. header padding +1px).
- **Long text:** give text containers `min-width: 0` and a wrap or nowrap strategy, so long values don't break the layout.
- **Overlays:** check that decorative art never overlaps text. Reserve space with margins; don't rely on z-index.

## 3. Markup and component markers
Wrap each reusable component's **first** occurrence:

```html
<!-- @component: status-tabs -->
<div class="tabs" role="tablist" aria-label="Order status">…</div>
<!-- @end -->
```

- **Naming:** kebab-case names. Use the same name for the same component across screens; `build_spec.py` takes the first occurrence it finds.
- **Semantics:** `nav`, `header`, `main`, `section`, `table` where appropriate.
- **States:** state goes in attributes and classes: `aria-selected`, `aria-pressed`, `aria-expanded`, `aria-current`, `.is-active`, `.is-disabled`.
- **Labels:** icon-only buttons get an `aria-label`.

## 4. Icons
- **Source:** every icon comes from `sprite.svg`: `<svg class="icon"><use href="#i-name"/></svg>`.
- **Style:** `.icon` sets size, stroke, caps, and joins. Size variants are classes (`.icon-sm`, `.icon-md`), and color comes from `currentColor`.
- **Drawing new icons:** use the measured style. Keep shapes simple and readable at 16–20px, reuse starter icons where the meaning fits, and name them by meaning (`i-truck`, not `i-icon7`).
- **Checks:** `render.py` reports missing `<use>` targets.

## 5. Content, brand, and IP rules
- **User's own brand:** use it (logo, name, color).
- **Third-party references** (Dribbble, other products): replicate layout, spacing, type scale, component styling, and icon *style*. **Replace:**
  - brand names and logos → the user's brand, or a neutral placeholder name and a simple CSS mark
  - photos → tinted placeholder tiles with a relevant sprite icon, and people → initials avatars
  - illustrations → a simple abstract shape or icon
  - marketing copy → the user's copy or neutral copy in the same length and tone
  - the references' exact data → realistic data in the user's domain and language
- **Restyles:** the slice may use demo content to show the style. Label it clearly in the spec as demo content that must not be copied.

## 6. Responsive rules
References are usually one width. Derive breakpoints conservatively (e.g. 1180 / 900 / 520):
- **Wide multi-column areas:** grids go 4 → 2 → 1, and side-by-side panels stack.
- **Sidebar:** becomes a top bar at tablet width; hide the nav or move it into a menu, whichever the app already does.
- **Tables:** scroll inside their own wrapper; the page never scrolls sideways.
- **Filter rows:** wrap; buttons stack on small phones.

Label derived rules "derived" in the spec. `render.py` must report no page-level overflow at 1024 and 390.

## 7. The measure → fix loop
Repeat until the differences are only intentional ones (placeholders, brand swaps):
1. `python scripts/assemble.py <slices>`
2. `python scripts/render.py <slices>/<screen>.html --widths 1440,1024,390 --out <previews>`: fix every reported issue.
3. `python scripts/compare.py refs/<ref>.png previews/<screen>-1440.png --ref-box <app area> --out previews/<screen>-compare.png`
4. Look at the compare image. Check element positions, row heights, paddings, border presence, icon size and weight, text size and weight, and column alignment.
5. Re-measure anything that looks off (`measure.py boxes` / `lines`), fix the CSS, and repeat.

Do at least two passes. Many issues only show up in the side-by-side view (e.g. a 4px row height difference, or a missing header border).

## 8. GATE B preview
Present per screen:
- `previews/<screen>-1440.png`, `-1024.png`, `-390.png`, and the path to `slices/<screen>.html` (open it in a browser).
- `previews/<screen>-compare.png`.
- Intentional differences, e.g.:
  - "logo replaced with Cedea"
  - "photos → placeholders"
  - "font is Plus Jakarta Sans (closest match)"
  - "responsive rules derived"

Then ask: **Approve** / **Request changes** / **Implement directly**. If the environment can publish or open HTML for the user, do that too.
