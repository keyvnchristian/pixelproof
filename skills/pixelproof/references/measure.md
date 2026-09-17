# Measure (Step 2)

Goal: every value in the slice comes from a measurement or from an explicit value in a design doc, never from a guess.

## Contents
1. Find the scale
2. Colors
3. Borders and dividers
4. Spacing and sizes
5. Typography
6. Icons
7. Snapping rules
8. measurements.md format

All commands take `--box x0,y0,x1,y1` (image px) to limit the region. Get coordinates by opening the image and reading positions. `boxes` output is a good way to find them.

## 1. Find the scale
Screenshots are rarely 1:1 with CSS pixels:
- **Retina screenshots:** 2×.
- **Dribbble shots:** often a scaled mockup inside a fake browser window.
- **Figma exports:** 1×, 2×, or 3×.

```bash
python scripts/measure.py scale refs/list.png --frame 102,207,1945,1536
```
- `--frame` is the app area: inside the browser chrome, or the full image if there is none.
- The script prints candidate scales for common viewport widths (1280, 1366, 1440, 1536, 1600, 1920) and for 1×/2×/3×.

**Pick the scale that makes known elements plausible:**
- Body text cap height ≈ 0.70–0.73 × font size.
- Common UI font sizes are 12–18px.
- Common control heights are 32–44px.
- A 1px hairline border should come out at 1–1.5 image px × scale.

Measure 2–3 elements at each candidate scale:

```bash
python scripts/measure.py boxes refs/list.png --box 530,500,1900,560 --scale 1.28
```

Record the chosen scale and the reasoning in `measurements.md`. For a `design.md` or Figma file with explicit values, scale = 1 and those values win.

## 2. Colors

```bash
python scripts/measure.py palette refs/list.png --box 2025,152,2230,195 --top 4
python scripts/measure.py sample refs/list.png 1480,1150 560,90
```

- **Background regions:** use the dominant color.
- **Text:** sample the darkest cluster within a word, not the anti-aliased edge. Use `palette` on a tight box around the text and take the most saturated or darkest entry that is not the background.
- **Color management:** screenshots may shift colors slightly. Snap near-identical grays into one token, and keep the number of distinct neutrals small (roughly 4 text shades, 3–5 surfaces, 2 borders).
- **Brand override:** the user's primary color replaces every place the reference uses its accent. Derive tints the same way the reference derives them (e.g. a soft tint for chart backgrounds).

## 3. Borders and dividers

```bash
python scripts/measure.py lines refs/list.png --box 530,800,1900,1400 --min-len 200
```

This finds long 1px (or thicker) horizontal and vertical lines and their colors. Use it to:
- find row dividers and card edges, and measure row heights (the distance between dividers ÷ scale)
- tell a border (a line) from an elevation (a soft gradient, which isn't a line)
- confirm which sides have borders (e.g. a table header with top + bottom borders only)

## 4. Spacing and sizes

```bash
python scripts/measure.py boxes refs/list.png --box 530,490,1900,560 --scale 1.28 --bg auto
```

- **How it works:** it segments the region into content bands (rows) and, inside each band, content blocks (columns). It prints image px and CSS px.
- **Padding:** the distance from a container edge (found with `lines`, or the box edge) to its first content block.
- **Gap:** the distance between consecutive blocks.
- **Control height:** measure the filled or bordered shape, not the text inside it.
- **Grid columns:** measure the left edge of each header label and of the matching cell content, then express the widths as `fr` ratios of the container.
- **Row alignment:** the headers of a table and its rows must share the same grid. Note any offset (e.g. rows inside bordered cards shift by the border width).

## 5. Typography
- **Size:** font size ≈ cap height ÷ 0.71 (for most sans fonts). Cross-check with line spacing in multi-line text.
- **Weight:** compare stroke thickness between headings and body. Typical pairs are 400/500 and 600/700.
- **Tracking:** tight geometric UIs often use -0.01 to -0.025em.
- **Family:** match letterforms (single- or double-storey `a`/`g`, `t` terminal, `R` leg, numeral shapes). Pick the closest freely available font (e.g. Inter, Plus Jakarta Sans, DM Sans, Manrope, Geist, Figtree, Outfit, Urbanist). Tell the user it is an estimate and ask whether they know the original.
- **Scale:** list every distinct size, then collapse sizes that are within 0.5px into one.

## 6. Icons
Measure:
- the box size (typically 16/18/20/24)
- the stroke width relative to size (1.5–2 for most line sets)
- line caps and joins (round or square)
- corner radius
- whether icons are filled or outlined

Default: draw every icon into `sprite.svg` in one consistent style (24×24 viewBox, `fill: none`, `stroke: currentColor`, measured stroke width, round caps and joins). Start from `assets/icons/starter-sprite.svg` and add what's missing. Only use an icon library if the reference clearly *is* that library (same shapes) and the user agrees. Never mix sets.

## 7. Snapping rules
- **Spacing:** round to whole px. Prefer even numbers unless several elements consistently measure odd (e.g. 9px nav spacing).
- **Font sizes:** whole px, or .5 for small labels when the image clearly shows it.
- **Radii:** snap to a small scale (e.g. 3/4/5/6/8/10/12, full).
- **One value per role:** if two measurements for the same role differ by 1px, pick one and use it everywhere.
- **Cleanest-system rule:** when measurements are ambiguous, choose the value that keeps the system cleanest (reuses an existing token), and note it.

## 8. measurements.md format

```markdown
# Measurements — <reference file>
Scale: 1.28 (frame 1843px wide → 1440px viewport). Reason: body cap height 11.4px → 16px font; hairlines 1.3px.

| Element | What | Image px | CSS px (raw) | Final | Confidence | Notes |
|---|---|---|---|---|---|---|
| Status tabs | container height | 61 | 47.7 | 48 | high | 5px padding + 36px tab + border |
| Status tabs | tab padding-x | 18 | 14.1 | 14 | high | |
| Order row | padding-y | 19 | 14.8 | 14 | medium | thumb 42px centered, row 70px |
| Primary | color | #3b8bf5 | — | #3a8cf6 | high | palette of button fill |
```
