# Pixelproof — maintainer guide for Claude Code

This repo *is* the Pixelproof product: an agent skill that ships in three ways from one source.

| Channel | Entry point |
|---|---|
| npm / npx installer | `package.json` → `cli/pixelproof.mjs` (copies `skills/pixelproof/` into `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`) |
| Claude Code plugin | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (plugin root = repo root, skills in `skills/`) |
| skills CLI | `npx skills add <owner>/pixelproof` reads `skills/pixelproof/SKILL.md` |

## Layout
```
cli/pixelproof.mjs            installer CLI (no dependencies, Node 18+)
skills/pixelproof/SKILL.md    router: command table + shared rules (keep under ~120 lines)
skills/pixelproof/commands/   one playbook per command (teach, replicate, enhance, extract, add, theme, audit, roast, compare, verify, responsive, status, help)
skills/pixelproof/references/ long guides loaded by commands (intake, measure, slice, spec-and-plan, implement, verify)
skills/pixelproof/scripts/    python (Pillow, numpy, Playwright) + node (.mjs) tools
skills/pixelproof/assets/     starter sprite, starter CSS, templates, presets/ (lumen, linen, nocturne + gallery + SPEC.md)
tools/smoke.mjs               pack + install + uninstall smoke test (not published)
.github/workflows/            ci.yml (tests on push/PR), publish.yml (npm publish on v* tags)
```

## Rules when editing
- **Router:** SKILL.md frontmatter may use Claude Code fields (`argument-hint`). The installer strips them for non-Claude targets; `RELEASE.md` strips them for the `.skill` upload. Don't add other non-spec keys without updating `stripClaudeOnlyFrontmatter` in the CLI.
- **Adding a command:**
  1. create `commands/<name>.md`
  2. add a row to the router table in SKILL.md
  3. update `commands/help.md`, the README command table, `argument-hint`, `.claude-plugin/plugin.json` description, and the CLI help line
  4. `npm test` checks that router links resolve
- **Paths:** command files refer to bundled files as `<SKILL_DIR>/…`. SKILL.md defines SKILL_DIR from `${CLAUDE_SKILL_DIR}`, with a fallback for other agents.
- **Scripts:** must stay dependency-light (Python: Pillow, numpy, Playwright; Node: built-ins + Playwright resolved from the user's project). Keep Python 3.9-compatible: no backslashes inside f-string expressions, no `match`.
- **Behavior:** read-only commands never edit app code. Code-changing commands always preview and ask Approve / Request changes / Apply directly.
- **Content:** never add real third-party brand names, logos, or copy to templates or examples.

## Presets
- **Editing:** change a preset's token values in `assets/presets/<name>.css`. Change component styling only in `components.css`, and only through tokens (no `[data-preset]` rules there).
- **After any preset change, rebuild and re-check** (from `assets/presets/`):
  ```bash
  python3 ../../scripts/assemble.py gallery && python3 build_gallery.py
  python3 ../../scripts/build_spec.py gallery --template ../templates/preset-spec.template.md --out SPEC.md
  python3 ../../scripts/render.py gallery/build/*--*.html --widths 1440,1024,390 --deep --strict --out /tmp/preset-check
  ```
  The render check must pass.

## Checks
```bash
npm test          # CLI help, python syntax, node syntax, router links
npm run smoke     # pack → npx install (Claude + Codex) → idempotency → uninstall
claude plugin validate .    # plugin + marketplace manifests (needs Claude Code)
```
Before a release, also run a script end to end:

```bash
python3 skills/pixelproof/scripts/audit_scan.py . --out /tmp/scan.json
```

## Versioning
`package.json` and `.claude-plugin/plugin.json` must have the same version (the publish workflow enforces this). Add a `CHANGELOG.md` entry for every release. See `RELEASE.md`.
