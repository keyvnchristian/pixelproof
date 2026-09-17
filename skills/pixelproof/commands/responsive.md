# /pixelproof responsive — breakpoint torture test

Read-only by default. Finds layouts that break between the widths that were designed.

Usage: `/pixelproof responsive <url | slice.html> [--pages /,/orders] [--widths 1920,1440,1280,1024,768,390,360]`

## Steps
1. **Render every page at every width, with deep checks:**
   ```bash
   python <SKILL_DIR>/scripts/render.py <targets> --widths <list> --deep --full --out docs/pixelproof/responsive --json
   ```
   The default widths are 1920, 1440, 1280, 1024, 768, 390, and 360.
2. **Collect** from the JSON:
   - page overflow
   - elements wider than their container (clipped or overflowing text)
   - tap targets under 44×44 at widths of 768 and below
   - fonts under 12px
   - images overflowing their container
3. **Inspect the screenshots** for things scripts can't catch: awkward wrapping, orphaned buttons, stacked filters that push content off screen, tables that should scroll but squash, and sidebars that don't collapse.
4. **For each issue, report:**
   - the width range where it happens
   - the element (selector or file:line)
   - a screenshot path
   - a fix that uses the spec's breakpoints (from `state.json`/spec, or a derived set if none exist)
5. **Report** with `report.py` (`"kind": "responsive"`), then offer **Fix these** (preview first) / **Done**.
