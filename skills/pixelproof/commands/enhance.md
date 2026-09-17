# /pixelproof enhance — improve a frontend without a reference

For projects without design references. It has three modes and can run one or all:

| Mode | Changes | Proof |
|---|---|---|
| `looks` | Visual style, using a built-in preset (or the project's own spec) | Before/after previews, then parity with the preset references |
| `perf` | Loading and runtime speed | Before/after LCP, CLS, TBT, and transfer size per page |
| `structure` | Oversized ("god") components → hooks and subcomponents | Screenshots must be pixel-identical before and after |

Usage:
- `/pixelproof enhance`: quick triage, then recommends a mode
- `/pixelproof enhance looks [--preset lumen|linen|nocturne] [--pages …]`
- `/pixelproof enhance perf [--url http://localhost:3000] [--pages /,/orders]`
- `/pixelproof enhance structure [path]`

All three modes keep features, content, routes, data, and behavior unchanged, and every change goes through a preview and approval.

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
Presets live in `<SKILL_DIR>/assets/presets/`. Read its `README.md`, then `SPEC.md` (tokens, components, patterns, verification values). The rendered references are `gallery/build/<page>--<preset>.html`.

1. **Context:** read `docs/pixelproof/context.md` (brand, users, Always/Never rules). If it's missing, offer `/pixelproof teach` first.
2. **Pick a preset:**
   - Choose the 1–2 presets that fit the product and users (e.g. `lumen` for dense ops tools, `linen` for lifestyle or consumer brands, `nocturne` for marketing).
   - Render the user's own key page in each candidate: build a slice of that page with its real content using the preset classes, following `<SKILL_DIR>/references/slice.md`.
   - Apply the user's brand color to the accent tokens, keeping AA contrast.

   **GATE A:** show the before screenshot and the candidate previews at 1440 and 390. Ask which preset (or "keep my current look, just clean it up"), or Request changes.
3. **Map:**
   - For every page in scope, write an element mapping (current element → preset component) into `docs/pixelproof/plan.md`.
   - Elements with no preset component get a derived component from the same tokens. Show it in an additions preview (see `replicate` Step 4).

   **GATE B:** show the mapping and the additions. Ask Approve / Request changes / Implement directly.
4. **Implement:**
   - Follow `<SKILL_DIR>/references/implement.md`: copy the preset tokens and `components.css` into the project's three-layer theme (primitives → semantic → component) and port the CSS rule by rule.
   - Keep the preset's class names, or map them 1:1 in the component API.
   - Work in batches of 1–3 pages.
5. **Verify** each batch:
   - parity against the preset references for shared components (`check_parity.mjs`)
   - `render.py --deep --strict` at 1440, 1024, and 390
   - `check_tokens.mjs`

   **GATE C:** show before/after for the batch and the results. Ask Continue / Change / Implement the rest directly.
6. **Save the system:** write `docs/pixelproof/style-spec.md` for the project with `build_spec.py`, and update `state.json` (`preset`, `brand`). Later commands then treat it as the project's own spec.

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
