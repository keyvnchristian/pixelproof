---
name: pixelproof
description: Pixel-exact UI from design references, plus design audits. Use this skill whenever the user shares a screenshot, Dribbble/Behance shot, Figma export, or design.md and wants it built, matched, cloned, restyled, or "made exactly like this"; wants to rebrand an app's colors or theme; wants to improve a frontend's looks, performance, or oversized components without a reference; wants to add a page, section, or menu in an existing style; wants to extract a design system from an existing UI; or asks to audit, roast, review, or check the consistency, spacing, icons, responsiveness, or design quality of a frontend. Commands include teach, replicate, enhance, extract, add, theme, audit, roast, compare, verify, responsive, status, and help.
argument-hint: "[teach|replicate|enhance|extract|add|theme|audit|roast|compare|verify|responsive|status|help] [target]"
---

# Pixelproof

Invocation arguments: `$ARGUMENTS`

SKILL_DIR = `${CLAUDE_SKILL_DIR}`. If that text still shows literally, as a placeholder instead of a path, SKILL_DIR is the folder that contains this SKILL.md. Every `<SKILL_DIR>` in the command files means this path.

## 1. Route the request

The first word of the arguments is the command. The rest is its target: paths, URLs, or a short brief. Match case-insensitively, including the aliases.

| Command | Aliases | Read and follow | What it does |
|---|---|---|---|
| `teach` | `setup`, `init`, `context` | `<SKILL_DIR>/commands/teach.md` | Interview once and save project context (product, users, brand, rules) to `docs/pixelproof/context.md` |
| `replicate` | `build`, `clone` | `<SKILL_DIR>/commands/replicate.md` | References → measured slice → spec → exact implementation, with approval gates |
| `enhance` | `improve`, `polish`, `refactor`, `speed` | `<SKILL_DIR>/commands/enhance.md` | No reference: improve looks (built-in presets), performance, or god components, with previews and proof |
| `extract` | `reverse`, `spec` | `<SKILL_DIR>/commands/extract.md` | Reverse-engineer the current UI into slices, tokens, and a style spec |
| `add` | `new`, `extend` | `<SKILL_DIR>/commands/add.md` | Add a page, section, menu, or feature in the established style |
| `theme` | `rebrand`, `recolor` | `<SKILL_DIR>/commands/theme.md` | Change brand color, font, radius, or density globally through tokens |
| `audit` | `check`, `lint` | `<SKILL_DIR>/commands/audit.md` | Design-consistency audit of the whole directory (read-only) |
| `roast` | — | `<SKILL_DIR>/commands/roast.md` | Brutally honest, funny, evidence-backed critique of the frontend |
| `compare` | `diff` | `<SKILL_DIR>/commands/compare.md` | Quick drift check of a page against one reference image |
| `verify` | `parity` | `<SKILL_DIR>/commands/verify.md` | Parity, token, overflow, and icon checks on implemented pages |
| `responsive` | `breakpoints`, `mobile` | `<SKILL_DIR>/commands/responsive.md` | Breakpoint torture test with fixes |
| `status` | `progress` | `<SKILL_DIR>/commands/status.md` | Where the pixelproof project stands and what's next |
| `help` | `?` | `<SKILL_DIR>/commands/help.md` | Show the commands |

Routing rules:
- **No arguments:** if the user attached or mentioned design references, run `replicate`. If they want the UI improved but have no references, run `enhance`. If they asked for a review or critique, run `audit` (or `roast` if they asked for a roast). If `docs/pixelproof/context.md` doesn't exist and the request is open-ended, suggest `teach` first. Otherwise run `help`.
- **Unknown first word:** if it looks like a file path, URL, or image, treat it as `replicate <args>`. Otherwise show `help` and ask which command they meant.
- **Loaded automatically** (the user wrote a request instead of a slash command): pick the command whose description matches the request, and state it in one line, e.g. "Running pixelproof audit on this repo."
- Read only the command file you need. Each command file says which `references/` guides to load.

## 2. Shared rules (every command)

**Project context comes first.**
- **If `docs/pixelproof/context.md` exists:** read it before anything else. Treat its values as confirmed: don't ask for them again, and list them in summaries instead. The Always/Never rules are extra constraints and checks for every command. If the current request conflicts with the context, the request wins; ask whether to update the context.
- **If it doesn't exist:** for any command other than `teach`, `help`, or `status`, offer `/pixelproof teach` first in one line ("Takes about 2 minutes, and later commands will ask far fewer questions"), then continue if the user declines.

**Workspace.** Every artifact goes under `docs/pixelproof/` in the user's project, unless the user picks another folder:

```
docs/pixelproof/
  context.md                                   ← from /pixelproof teach
  refs/  slices/  previews/  audit/  roast/
  measurements.md  style-spec.md  tokens.json  plan.md  state.json
```

**State.** `state.json` records progress, so any command, and any future session, can pick up where the work stopped:

```json
{ "version": 1, "mode": "restyle", "brand": {"primary": "#992c29"},
  "gates": {"A": "approved", "B": "approved", "C": "skipped", "D": "pending"},
  "batches": [{"name": "Orders + Control Tower", "status": "verified"}],
  "lastCommand": "verify", "updatedAt": "2026-09-17T10:00:00Z", "contextUpdatedAt": "2026-09-17T09:00:00Z", "openQuestions": [] }
```

Read it at the start of every command, if it exists, and update it at the end.

**Approval.** Any command that changes code shows a preview first and asks **Approve / Request changes / Apply directly**. Read-only commands (`audit`, `roast`, `compare`, `verify`, `responsive`, `status`) never edit code, and `teach` edits only `context.md`; they end by offering fixes, which go through the same approval. When asking, use the question tool if the environment has one (e.g. `AskUserQuestion`); otherwise use numbered options, and wait for the answer.

**Evidence.** Every finding cites something real: file:line, a measured value, a computed style, or a screenshot path. No generic advice.

**One source of truth.**
- Styles come from one token set, icons from one sprite, and markup from the spec components.
- Never introduce new colors, radii, shadows, or font sizes outside the tokens.
- Never mix icon libraries.

**Third-party references.** Replicate layout and visual language, but replace names, logos, photos, illustrations, and copy with the user's own content or neutral placeholders.

**Tooling.** The scripts need Python 3 with Pillow, numpy, and Playwright (Chromium), and Node for the `.mjs` checks. If a script fails with a missing dependency, tell the user to run `npx pixelproof doctor`, and give the fix command:

```
pip install pillow numpy playwright && python -m playwright install chromium
```

## 3. Built-in presets
`<SKILL_DIR>/assets/presets/` holds three original styles (`lumen`, `linen`, `nocturne`) that share one component stylesheet, with reference pages for dashboard, settings, forms, auth, file upload, and landing pages. `enhance looks` uses them; see the README and SPEC.md there.

## 4. Scripts (`<SKILL_DIR>/scripts/`)

| Script | Used by | Purpose |
|---|---|---|
| `measure.py` | replicate, compare, extract | Scale candidates, palette, pixel samples, border lines, content boxes (image px → CSS px) |
| `assemble.py` | replicate, extract, add, theme | Build self-contained slice pages from shared CSS, sprite, partials, and bodies |
| `render.py` | all visual commands | Screenshots at chosen widths. `--deep` adds tap-target, clipped-text, contrast, alt-text, and small-font checks |
| `compare.py` | replicate, compare | Reference vs render: side-by-side, overlay, divider drift report |
| `tokens.py` | replicate, extract, theme | Inventory of every design value in a stylesheet |
| `build_spec.py` | replicate, extract | Generate `style-spec.md` with verification values from rendered slices |
| `structure_scan.py` | enhance structure, audit | Find god components (size, state, effects, data calls, nesting, props) and suggest splits |
| `perf_scan.py` | enhance perf, audit | Static perf smells plus runtime LCP, CLS, TBT, transfer size, oversized images, render-blocking |
| `audit_scan.py` | audit, roast, extract | Static scan of a codebase: colors, spacing, type, radii, shadows, z-index, icon libraries, inline styles, `!important`, arbitrary Tailwind values, duplicate components → JSON + scores |
| `report.py` | audit, roast, verify, responsive | Build a shareable HTML report (scores, findings, screenshots) from JSON |
| `check_parity.mjs` | replicate, verify, add, theme | Computed-style diff between a slice and the running app |
| `check_tokens.mjs` | replicate, verify, audit | Fail on raw colors or px values outside the theme |
