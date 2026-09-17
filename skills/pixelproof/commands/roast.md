# /pixelproof roast — honest, funny, evidence-backed critique

Read-only. Roasts the frontend the way a sharp senior designer would over coffee: funny, specific, and useful. Every joke points at a real problem and comes with a fix.

Usage: `/pixelproof roast [path | url | screenshot] [--spicy] [--pages /,/pricing]`

## Tone rules
- **Target:** roast the UI, never the person or their team. No insults about skill, intelligence, or identity. No profanity unless the user passes `--spicy` (and even then, keep it light and rare).
- **Evidence:** every roast must name the element and show proof (a screenshot region, a computed value, or file:line). A joke without evidence doesn't ship.
- **Fix:** every roast ends with a concrete fix in one sentence.
- **Credit:** give real credit where it's due. A roast with zero compliments reads as spite.
- **Language:** match the user's language. Indonesian slang is fine if the user writes that way.

## Steps

### 1. Capture
- **URL, or a runnable app** (ask before starting a dev server):
  ```bash
  python <SKILL_DIR>/scripts/render.py <urls> --widths 1440,390 --deep --full --out docs/pixelproof/roast/shots --json
  ```
- **Screenshots given:** use them directly, and measure suspicious areas with `measure.py palette|boxes|lines`.
- **Code only:** run the static scan (step 2) and render any static pages you can. Say that the roast is code-based if nothing was rendered.

### 2. Scan

```bash
python <SKILL_DIR>/scripts/audit_scan.py <path> --out docs/pixelproof/roast/scan.json
```

### 3. Look at the screenshots yourself
Open the PNGs and check:
- hierarchy
- alignment
- spacing rhythm
- type scale
- color use
- icon consistency
- empty space
- density
- mobile layout

### 4. Slop bingo
If `docs/pixelproof/context.md` exists, roast against it: what fits its users and personality isn't slop, and every broken Never rule is an automatic square.

Also pull from `scan.json` (step 2): if it reports `duplicate primitives` or a high `inline styles` count, that's two more squares — name the actual files.

Mark every square you can prove:
- default gradient hero (purple → blue)
- everything in Inter at 14–16px with no scale
- cards inside cards inside cards
- icon tile above every heading
- 5+ shades of gray that nobody chose on purpose
- random border radii (4, 6, 8, 12, 16 on one screen)
- emoji as icons next to real icons
- two icon libraries in one sidebar
- centered everything
- gray text on a colored background
- shadow on everything
- buttons with three different heights
- "Lorem ipsum" or "John Doe" in production
- horizontal scroll on mobile
- tap targets under 44px
- focus outline removed
- duplicate component implementations (same button/card/modal built more than once)
- inline styles everywhere instead of the shared stylesheet/tokens

### 5. Write 7–10 roasts, ranked by impact
Format each one like this:

```
🔥 <punchline about the element>
Evidence: <screenshot path + region, computed style, or file:line>
Fix: <one sentence>
```

### 6. Score
The **Slop Score** runs 0–100, where lower is better: it's the share of bingo squares hit, weighted by severity. Also give a **Pixelproof Score** (0–100, higher is better) from the audit categories, so the two agree.

### 7. Report

```bash
python <SKILL_DIR>/scripts/report.py docs/pixelproof/roast/report.json --out docs/pixelproof/roast/roast.html
```

This uses the same JSON shape as audit, with `"kind": "roast"`, `"slop_score"`, `"bingo": [{"square": "...", "hit": true, "evidence": "..."}]`, and findings whose `title` is the punchline.

In chat, reply with:
- a one-line verdict
- Slop Score and Pixelproof Score
- the roasts
- "What actually slaps" (2–3 real strengths)
- a **cleanup list**: every duplicate component (with which copy to keep) and the inline-style hotspot files, straight from `scan.json` — handoff-ready
- the report path

### 8. Offer next steps (approval gate)
- **Fix the top 3 roasts** (with a preview first)
- **Run a full audit** (`/pixelproof audit`)
- **Restyle from a reference** (`/pixelproof replicate`)
- **Done**
