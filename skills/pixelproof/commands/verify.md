# /pixelproof verify — parity and system checks

Read-only. Proves that implemented pages still match the slices and the token rules.

Usage: `/pixelproof verify [page-name | all] [--url http://localhost:3000]`

## Steps
1. **Setup.** Needs `docs/pixelproof/parity.config.json` (see `<SKILL_DIR>/references/verify.md`). If it's missing, build it from `state.json` batches and the spec's component selectors, and show it to the user before running.
2. **Run the checks.** Confirm the app is running first (ask before starting it).
   - `node <SKILL_DIR>/scripts/check_parity.mjs docs/pixelproof/parity.config.json --out docs/pixelproof/previews/parity [--only <name>]`
   - `node <SKILL_DIR>/scripts/check_tokens.mjs <src> --theme <theme-dir>`
   - `python <SKILL_DIR>/scripts/render.py <urls> --widths 1440,1024,390 --deep --out docs/pixelproof/previews/app`
   - Search the source for icon-library imports.
3. **Report** using the table format in `<SKILL_DIR>/references/verify.md`, and build the HTML report with `report.py` (`"kind": "verify"`).
4. **If anything failed,** list the exact diffs (selector, property, expected, actual) and offer **Fix these** (preview first) / **Done**. Update `state.json`.
