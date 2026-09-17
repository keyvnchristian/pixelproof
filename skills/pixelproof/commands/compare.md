# /pixelproof compare — quick drift check against a reference

Read-only. Measures how far one page is from one reference image, without the full workflow.

Usage: `/pixelproof compare <reference.png> <url | slice.html | screenshot.png> [--ref-box x0,y0,x1,y1]`

## Steps
1. **Find the app area** in the reference (exclude browser chrome) and the scale: `measure.py scale --frame …`.
2. **Get a render** of the target at the reference's CSS width (`render.py --widths <w> --full`), unless the target is already a screenshot.
3. **Compare:**
   ```bash
   python <SKILL_DIR>/scripts/compare.py <ref> <render> --ref-box <frame> --out docs/pixelproof/compare/<name>.png
   ```
4. **Measure the areas that drift** (`measure.py boxes` / `lines` on both images) and turn the differences into CSS terms, e.g. "row height 70 vs 76px → padding 14 → 17px".
5. **Report:**
   - the similarity score
   - the divider drift table
   - the top differences, each as element → reference value → current value → fix
   - the image paths

   Then offer: **Fix these** (preview first) / **Full replicate** / **Done**.
