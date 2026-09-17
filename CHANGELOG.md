# Changelog

## 0.4.2 — 2026-09-17
- **`enhance looks`:** a user-supplied reference is now the primary style source (measured and sliced like `replicate`), not just the built-in presets — presets are a fallback library for when there's no reference. Handles two-image prompts ("enhance this, make it look like this") by asking which of style/layout/content/all is in scope when it isn't stated.
- **`measure.md` / `enhance` verify step:** hard scale-sanity gate — a body font-size or control-height outside plausible px ranges after scale detection flags the scale as off by 2x/3x before it propagates into a "zoomed in" restyle.
- **Fix:** normalized bare `scripts/...`/`assets/...` paths and a lowercase `<skill>/...` placeholder in `references/*.md` to `<SKILL_DIR>/...`, matching the convention every command file already follows.

## 0.4.1 — 2026-09-17
- **`audit`:** chat reply is now three Markdown tables (category scores, top findings, strengths) instead of prose lines. Findings sorted Critical → High → Medium → Low.

## 0.4.0 — 2026-09-17
- **New `/pixelproof enhance`** for projects without references:
  - `looks`: restyle with a built-in preset
  - `perf`: measure and fix loading and runtime speed
  - `structure`: split god components, with pixel-identical proof
- **Built-in presets:** `lumen`, `linen`, and `nocturne` share one component stylesheet, with reference pages for dashboard, settings, form, auth (login, OTP, reset, register), file upload, and landing. Every page passes `render.py --deep --strict` at 1440, 1024, and 390. `assets/presets/gallery/build/index.html` shows them all with page and preset switchers.
- **New scripts:** `structure_scan.py` (god components) and `perf_scan.py` (static perf smells plus LCP, CLS, TBT, transfer size, oversized images, render-blocking).
- **`assemble.py`:** supports multiple CSS files, a sprite path, an output folder, and preset variants.
- **`build_spec.py`:** reads those manifests.
- **`render.py --deep`:** ignores visually hidden inputs and inline text links, and measures checkboxes by their label.
- **Starter sprite:** 14 more icons (77 total).
- **`audit`:** findings now carry a Confidence rating, with an explicit verify-before-report step for high-severity findings.
- **`roast`:** now surfaces duplicate components and inline-style hotspots from the scan as bingo squares, plus a handoff-ready cleanup list.

## 0.3.0 — 2026-09-17
- **New `/pixelproof teach`:** a one-time interview that writes `docs/pixelproof/context.md` (product, users, brand, references, Always/Never rules, how to run the app, workflow preferences). `teach "<fact>"` updates one fact.
- **Every command reads the context first:** intake questions answered there are skipped, and Always/Never rules become checks in audit, roast, verify, and add.
- **Repo tooling:** `CLAUDE.md` maintainer guide, `RELEASE.md`, CI workflow, `npm run smoke`.

## 0.2.0 — 2026-09-17
- **Subcommands:** `/pixelproof <command>` with replicate, extract, add, theme, audit, roast, compare, verify, responsive, status, and help. SKILL.md is now a router, and each command has its own playbook in `commands/`.
- **New `audit_scan.py`:** static design-consistency scan with heuristic scores.
- **New `report.py`:** self-contained HTML reports, including slop bingo for roasts.
- **`render.py --deep`:** tap-target, clipping, contrast, alt-text, label, and small-text checks.
- **`state.json`:** progress tracking across commands and sessions.
- **Installer:** Claude-only frontmatter is stripped for Codex and other agents.

## 0.1.0 — 2026-09-17
- First release.
- **Skill:** a gated workflow: intake → measure → slice → additions → spec/plan → batched implementation → verify.
- **Scripts:** measure, assemble, render, compare, tokens, build_spec, check_parity, check_tokens.
- **Assets:** starter sprite (63 icons), starter CSS, spec and plan templates.
- **Installs via:** `npx pixelproof`, the Claude Code plugin marketplace, or `npx skills add`.
