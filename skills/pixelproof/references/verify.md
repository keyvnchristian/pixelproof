# Verify (Step 7)

## 1. Computed-style parity

Create `docs/pixelproof/parity.config.json` once and extend it per batch:

```json
{
  "widths": [1440, 1024, 390],
  "pairs": [
    {
      "name": "orders",
      "reference": "docs/pixelproof/slices/list.html",
      "app": "http://localhost:3000/orders",
      "selectors": [".sidebar", ".nav-item", ".nav-item.is-active", ".topbar", ".page-title",
                    ".breadcrumb .current", ".tabs", ".tab.is-active", ".search", ".filters-right .btn",
                    ".subbar", ".seg", ".table-head", ".order", ".order-head", ".order-row", ".btn-primary"]
    }
  ],
  "properties": ["height", "min-height", "padding-top", "padding-right", "padding-bottom", "padding-left",
                 "margin-top", "margin-bottom", "row-gap", "column-gap",
                 "border-top-width", "border-top-style", "border-top-color",
                 "border-bottom-width", "border-bottom-color", "border-left-width", "border-right-width",
                 "border-top-left-radius", "background-color", "box-shadow",
                 "color", "font-family", "font-size", "font-weight", "letter-spacing", "line-height"],
  "ignore": { "height": [".order", ".order-row"] },
  "login": null
}
```

```bash
node <SKILL_DIR>/scripts/check_parity.mjs docs/pixelproof/parity.config.json --out docs/pixelproof/previews/parity
```

- **What it does:** opens both pages, compares the first element matching each selector, prints a diff table, and saves screenshots of both pages. It exits with code 1 if there are differences.
- **Selectors:** use the spec's component root selectors. A selector missing on either page counts as a failure, unless it's listed under `optional`.
- **Content-dependent values** (heights of cards with variable text, widths) go in `ignore`.
- **Authenticated apps:** set `login` to `{ "url": "...", "steps": [{"fill": ["#email", "..."]}, {"fill": ["#password", "..."]}, {"click": "button[type=submit]"}], "waitFor": ".sidebar" }`, or pass `--storage state.json` from a saved Playwright session. Never hard-code real credentials in committed files; read them from environment variables (`"$ENV:APP_PASSWORD"`).
- **Fonts:** the font must load in both pages. If the check environment blocks Google Fonts, compare with `font-family` excluded and say so.

## 2. Token lint

```bash
node <SKILL_DIR>/scripts/check_tokens.mjs src --theme src/styles/theme --allow "*.svg"
```

- **What it flags:** hex, `rgb()`/`rgba()`, and `px` literals in `.css/.scss/.ts/.tsx/.js/.jsx/.vue/.svelte` outside the theme folder.
- **Allowed:** `0`, `0px`, `1px` inside `var(--border-width, 1px)` fallbacks, percentages, `fr`, `em`, and unitless numbers.
- **Inline suppression:** a comment containing `pixelproof-allow` on the same line allows it (e.g. third-party config).

## 3. Other checks (run as part of `render.py` against the app URL)

```bash
python <SKILL_DIR>/scripts/render.py http://localhost:3000/orders --widths 1440,1024,390 --out docs/pixelproof/previews/app
```

- no horizontal page overflow at 1024 and 390
- every `<use href="#…">` resolves
- no console errors
- **icons:** search the source for icon library imports (e.g. `lucide-react`, `@heroicons`) and remove any found, unless the spec says otherwise
- **columns:** for grouped tables, the header label's left edge equals the row content's left edge (documented offsets allowed)

## 4. Report format

```
Batch <n> verification
| Check | Result | Notes |
|---|---|---|
| Parity (orders, 1440/1024/390) | 0 diffs | fixed: .order-head padding 10→9px, .tab radius 8→6px |
| Token lint | pass | |
| Overflow | pass | |
| Icons | pass | removed lucide-react from 3 files |
| Column alignment | pass | |
Screenshots: previews/app/orders-1440.png … vs previews/list-1440.png
Changed files: …
Removed: …
```
