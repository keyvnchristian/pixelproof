# /pixelproof enhance — improve an existing frontend's style, speed, or structure

For an existing app you want to elevate, not rebuild. It has three modes and can run one or all:

| Mode | Changes | Proof |
|---|---|---|
| `looks` | Borders, weight, radii, font-size scale, spacing/layout density, and overall visual style — from a reference if the user gave one, otherwise from a built-in preset | Before/after previews, then parity with the style source |
| `perf` | Loading and runtime speed | Before/after LCP, CLS, TBT, and transfer size per page |
| `structure` | Oversized ("god") components → hooks and subcomponents | Screenshots must be pixel-identical before and after |

Usage:
- `/pixelproof enhance`: quick triage, then recommends a mode
- `/pixelproof enhance looks [refs…] [--preset lumen|linen|nocturne] [--pages …]`
- `/pixelproof enhance perf [--url http://localhost:3000] [--pages /,/orders]`
- `/pixelproof enhance structure [path]`

All three modes keep features, content, routes, data, and behavior unchanged, and every change goes through a preview and approval.

**`enhance looks` vs `replicate`:** both can take a reference, but they answer different requests.
- `replicate` builds or clones screens to be pixel-exact to the reference, screen by screen, with a full measure → slice → spec → plan → batches workflow. Use it when the reference *is* the target UI.
- `enhance looks` takes the app's **current** pages and lifts their border style, boldness, font-size scale, radii, spacing/density, and overall look toward a reference's style — without rebuilding the pages to match its exact layout. Use it when the reference is inspiration for restyling what already exists, or when there's no reference at all (built-in presets are the fallback library, not the primary path).

## 0. Triage (no mode given)
1. **Scan** (read-only, a few seconds):
   ```bash
   python <SKILL_DIR>/scripts/audit_scan.py . --out docs/pixelproof/enhance/scan.json
   python <SKILL_DIR>/scripts/structure_scan.py . --out docs/pixelproof/enhance/structure.json
   python <SKILL_DIR>/scripts/perf_scan.py . --out docs/pixelproof/enhance/perf.json [--url <url> --pages <key pages>]
   ```
2. **Summarize** in five lines: the looks score, the flagged components, and the top perf issues.
3. **Recommend** the order: usually structure first on files you'll restyle, then looks, then perf.
4. **Ask** which mode(s) to run, using the question tool if available.

## 1. `looks`

1. **Context:** read `docs/pixelproof/context.md` (brand, users, Always/Never rules). If it's missing, offer `/pixelproof teach` first.
2. **Intake — two images ("enhance this [current], make it look like this [reference]"):**
   - The **first** image (or the one described as "this"/"current"/a screenshot of the running app) is the current state. The **second** (or the one described as "like this"/a Dribbble shot/design) is the style reference. If the wording doesn't make the roles clear, ask which is which before doing anything.
   - **If the scope is clear from the prompt** (e.g. "make the buttons bolder like this", "match this card style"), proceed with just that scope.
   - **If the scope is ambiguous** (e.g. "enhance this, make it look like this" with nothing else), ask a single question before starting: which of these should move toward the reference — **style** (colors, borders, weight, radii, shadows), **layout** (spacing, density, structure), **content** (copy, data, sections), or **all of it**? Offer the question tool if available, otherwise numbered options. Don't guess an answer that changes content or layout beyond what "looks" work implies.
3. **Pick a style source:**
   - **The user gave a reference** (screenshot, Dribbble/Behance shot, Figma export, design.md): this is the primary path. Copy it into `docs/pixelproof/refs/`, then measure it (`<SKILL_DIR>/references/measure.md`) and slice it (`<SKILL_DIR>/references/slice.md`) to get its exact border widths/styles, font-weight and size scale, radii, shadows, spacing rhythm, and layout density as tokens — same rigor as `replicate` Steps 2–3, but you only need enough of the reference to cover the style traits, not every screen. **Mind the scale check in measure.md Step 1** — a missed 2× on a retina/scaled screenshot is the usual cause of a restyle coming out looking "zoomed in" (font sizes, padding, and margin roughly double what they should be).
   - **No reference:** presets live in `<SKILL_DIR>/assets/presets/` as a library fallback. Read its `README.md`, then `SPEC.md` (tokens, components, patterns, verification values). The rendered references are `gallery/build/<page>--<preset>.html`. Choose the 1–2 presets that fit the product and users (e.g. `lumen` for dense ops tools, `linen` for lifestyle or consumer brands, `nocturne` for marketing).
   - Either way: render the user's own key page in each candidate, using the style source's classes, following `<SKILL_DIR>/references/slice.md`. Apply the user's brand color to the accent tokens, keeping AA contrast.

   **GATE A:** show the before screenshot and the candidate previews at 1440 and 390. Ask which style source to use (or "keep my current look, just clean it up"), or Request changes.
4. **Map:**
   - For every page in scope, write an element mapping (current element → style source's component) into `docs/pixelproof/plan.md`. Only map the traits in scope from Step 2 (e.g. style-only means colors/borders/weight/radii/shadows, not spacing or structure).
   - Elements with no matching component get a derived component from the same tokens. Show it in an additions preview (see `replicate` Step 4).

   **GATE B:** show the mapping and the additions. Ask Approve / Request changes / Implement directly.
5. **Implement:**
   - Follow `<SKILL_DIR>/references/implement.md`: copy the style source's tokens and component CSS into the project's three-layer theme (primitives → semantic → component) and port the CSS rule by rule. Keep the current pages' routes, data, content, and behavior unchanged — this restyles them, it doesn't rebuild them.
   - Keep the style source's class names, or map them 1:1 in the component API.
   - Work in batches of 1–3 pages.
6. **Verify** each batch:
   - parity against the style source's references for shared components (`check_parity.mjs`)
   - `render.py --deep --strict` at 1440, 1024, and 390
   - `check_tokens.mjs`
   - **sanity check:** computed font sizes, padding, and margins land in believable UI ranges (body text 11–20px, control height 28–52px). Anything outside that, front-load-investigate before showing the batch — it's almost always a stale scale from Step 2, not a real design choice.

   **GATE C:** show before/after for the batch and the results. Ask Continue / Change / Implement the rest directly.
7. **Save the system:** write `docs/pixelproof/style-spec.md` for the project with `build_spec.py`, and update `state.json` (`styleSource`: reference path or preset name, `brand`). Later commands then treat it as the project's own spec.

## 2. `perf`
1. **Baseline:**
   - Run `perf_scan.py` with `--url` and the key pages (ask before starting a dev server; use a production build if you can, e.g. `next build && next start`). Add `--throttle` for a mid-range phone profile.
   - Save it as `docs/pixelproof/enhance/perf-before.json`.
2. **Plan** fixes ranked by impact and risk. Typical fixes:
   - **Heavy dependencies:** replace them (moment → date-fns/dayjs), import per method, or load them lazily with dynamic `import()` on the pages that use them (charts, maps, editors, exporters).
   - **Server rendering:** move data fetching out of `useEffect` into server components or loaders. Remove `"use client"` from pages and layouts that don't need it, and push client boundaries down to the interactive leaves.
   - **Images:**
     - use `next/image` (or `width`, `height`, `loading="lazy"`, `decoding="async"`)
     - use correct `sizes`
     - compress oversized assets in `public/`, and serve AVIF/WebP
   - **Fonts:** self-host or use `next/font`, subset them, set `display: swap`, and use no more than 2 families and 4 weights.
   - **Render-blocking resources:** defer non-critical scripts and inline critical CSS when the framework supports it.
   - **Lists and tables:** paginate or virtualize long lists; memoize expensive row renders only where profiling shows a cost.
   - **Layout shift:** reserve space for late content (skeletons with fixed size, `aspect-ratio`).

   **GATE A:** show the baseline table and the ranked plan (fix, expected gain, risk, files). Ask Approve / Pick items / Implement directly.
3. **Implement** in small commits, one fix type at a time, with no behavior changes. Run the project's tests and type check after each.
4. **Re-measure** with the same flags (`perf-after.json`) and a screenshot parity check, so the look didn't change.

   **GATE B:** show a before/after table per page (LCP, CLS, TBT, requests, KB, JS KB). Revert any fix that didn't help. Then update `state.json`.

## 3. `structure`
1. **Scan:**
   ```bash
   python <SKILL_DIR>/scripts/structure_scan.py <path> --out docs/pixelproof/enhance/structure.json --md docs/pixelproof/enhance/structure.md
   ```
   Open the flagged files (god score ≥ 45) and confirm them by reading them.
2. **Propose splits** for each file:
   - a data hook (`useOrdersData`) that owns fetching, loading/error state, and mutations
   - presentational subcomponents per section (the scan lists section candidates)
   - named handlers instead of inline arrow functions
   - reducers for related state
   - derived values computed during render instead of synced through effects
   - server/client boundaries where the framework supports them

   Show a file tree (before → after) and each new component's props.

   **GATE A:** show the proposal. Ask Approve / Change / Implement directly.
3. **Safety net first:**
   1. Capture screenshots of the affected pages at 1440 and 390 (`render.py --full`).
   2. Note the existing tests. If there are none for the file, add a minimal render test when the project has a test runner.
4. **Refactor** one file at a time:
   - move code without changing markup, class names, or behavior
   - keep exports stable, or update every import
   - run the type check, lint, and tests after each file
5. **Prove nothing changed:**
   1. Re-render and compare with `compare.py` (the screenshots must be identical apart from dynamic content).
   2. Re-run `structure_scan.py` and show the score change per file.

   **GATE B:** show the results. Ask Continue with the next file / Stop. Then update `state.json`.
