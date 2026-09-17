# /pixelproof extract — reverse-engineer the current UI into a spec

Turns an existing app into the same artifacts `replicate` produces: slices, tokens, and `style-spec.md`. Use it when there are no references, before `add` or `theme`, or to put a design system under an app that grew organically.

Usage: `/pixelproof extract [--url http://localhost:3000] [--pages /,/orders] [path]`

## Steps
1. **Inventory.** Run `audit_scan.py` on the source, and read the shared components (layout, sidebar, header, buttons, inputs, tables, cards, modals). List which pages represent each pattern.
2. **Capture.** If the app can run (ask before starting it), take screenshots with `render.py --widths 1440,1024,390 --full`, and read computed styles of key elements with Playwright. Computed values are more precise than pixel measurement. Otherwise, use the CSS/Tailwind config and components as the source.
3. **Decide the canonical system.** When the app uses several values for one role (e.g. 3 button heights), propose the most common or most intentional one as canonical and list the others as drift.

   **GATE 1:** show the proposed token table (colors, spacing, type, radii, shadows, icon set) and the drift list. Ask Approve / Change.
4. **Slice.** Build slices of 1–3 representative pages from the canonical values (`<SKILL_DIR>/references/slice.md`), with `@component` markers. Use the app's real content in the slices; it's the user's own.
5. **Spec.** Run `tokens.py` and `build_spec.py`, and fill in the hand-written sections (`<SKILL_DIR>/references/spec-and-plan.md`).

   **GATE 2:** show the slice previews and a spec summary. Ask Approve / Change.
6. **Finish.** Update `state.json` (`mode: "extracted"`), and suggest the next step:
   - `/pixelproof audit` to measure drift against the new spec
   - `/pixelproof add` to extend it
   - `/pixelproof theme` to rebrand it

   Extraction never changes app code.
