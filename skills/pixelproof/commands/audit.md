# /pixelproof audit — design-consistency audit

Read-only. Scans the current directory (or the path given) and reports how consistent, and how "on-system", the frontend is, with evidence and a prioritized fix list. It never edits code without approval.

Usage: `/pixelproof audit [path] [--url http://localhost:3000] [--pages /,/orders,/settings]`

## Steps

### 1. Scope
- Default path: the repo root.
- Skip `node_modules`, build output, vendored code, generated files, and test fixtures.
- Detect the stack (framework, styling approach, component library, icon libraries) from `package.json` and the config files.
- If `docs/pixelproof/context.md` exists, add its Always/Never rules as checks, and weigh findings against its users and devices.
- If `docs/pixelproof/style-spec.md` exists, audit **against the spec**. Otherwise audit against internal consistency, and mention `/pixelproof extract` at the end.

### 2. Static scan

```bash
python <SKILL_DIR>/scripts/audit_scan.py <path> --out docs/pixelproof/audit/scan.json --md docs/pixelproof/audit/scan.md
```

The output gives, per category, the distinct values, counts, near-duplicate clusters, the top files, and a 0–100 score.

### 3. Token check (if a theme folder exists)

```bash
node <SKILL_DIR>/scripts/check_tokens.mjs <src> --theme <theme-dir> --json
```

### 4. Live checks (only if the app is running or the user gave `--url`)
Ask before starting a dev server. Then run:

```bash
python <SKILL_DIR>/scripts/render.py <url>/<page> ... --widths 1440,1024,390 --deep --out docs/pixelproof/audit/shots --json
```

### 5. Read the code where the scan points
Check each suspicious cluster by opening the files. Don't report what you haven't confirmed. In particular, look for:
- **Duplicate components:** several button, card, modal, or table implementations. Look at their props and styles, not just the names.
- **Mixed icon libraries**, or inline SVGs with inconsistent stroke widths.
- **One-off styles:** inline `style={{…}}`, arbitrary Tailwind values (`p-[13px]`), and `!important`.
- **States:** missing hover, focus, disabled, loading, empty, and error states in shared components.
- **Accessibility basics:** icon buttons without labels, images without alt text, focus outlines removed, contrast problems (from `--deep`), tap targets under 44px.

Rate each finding's **Confidence** (High = opened the file and confirmed it / Medium = strong scan signal, not opened / Low = plausible but unverified). Before reporting a `high`-severity finding, actively try to disprove it (check if it's already handled by a shared base component, a theme override, or a convention) — downgrade confidence or drop it if you can't substantiate it.

### 6. Score
Use the scan scores and adjust them with confirmed findings. Categories:

| Category | What drags it down |
|---|---|
| Color | Many distinct colors, near-duplicate grays, raw hex outside the theme |
| Spacing | Too many distinct values, off-scale values, arbitrary values |
| Typography | Too many font sizes/weights, mixed families |
| Shape | Radius zoo, shadow zoo |
| Icons | Several libraries, mixed stroke widths or sizes |
| Components | Duplicated primitives, one-off styling |
| Responsive | Page overflow, clipped text, tiny tap targets |
| Accessibility | Missing labels/alt text, low contrast, removed focus |

The overall score is the weighted average (Color 15, Spacing 15, Typography 15, Shape 10, Icons 10, Components 15, Responsive 10, Accessibility 10). Skip categories that couldn't be measured and say so.

### 7. Report
Write `docs/pixelproof/audit/report.md`, and build the HTML version:

```bash
python <SKILL_DIR>/scripts/report.py docs/pixelproof/audit/report.json --out docs/pixelproof/audit/report.html
```

`report.json` shape:

```json
{"title": "Pixelproof audit — <project>", "kind": "audit", "score": 62,
 "summary": "One paragraph.",
 "categories": [{"name": "Color", "score": 48, "note": "31 distinct colors; 9 grays within 3% of each other"}],
 "findings": [{"severity": "high", "category": "Color", "title": "Nine near-identical grays",
   "evidence": ["src/components/Card.tsx:14 #f7f7f7", "src/app/page.tsx:88 #f8f8f8"],
   "fix": "Collapse into --bg-subtle", "effort": "S", "confidence": "high", "screenshot": null}],
 "strengths": ["Consistent 8px radius on cards"],
 "next": ["/pixelproof extract", "/pixelproof theme"]}
```

In chat, reply with Markdown tables:
- **Category scores** table: `Category | Score` (mark any skipped category as "skipped" with the reason instead of a number)
- **Top findings** table: `# | Severity | Finding | Evidence` (put the fix in the finding text or a `Fix` column if there's room), sorted Critical → High → Medium → Low
- **Strengths** table: `Item | Note`
- report paths, as a plain list below the tables

### 8. Offer fixes (approval gate)
Group the fixes into batches, e.g.:
1. collapse colors into tokens
2. one icon set
3. spacing scale
4. merge duplicate buttons
5. a11y fixes

Ask the user to pick one: **Fix batch 1** / **Pick batches** / **Create a spec first** (`/pixelproof extract`) / **Done**. Fixes follow the replicate implementation rules: tokens only, no content changes, and verification after each batch.

Update `state.json` (`lastCommand: "audit"`, with the score and date) so later audits can show the trend ("62 → 81 since 2026-09-01").
