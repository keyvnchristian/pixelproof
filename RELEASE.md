# Release checklist

Claude Code can run this top to bottom. Stop and ask the human at every **[ASK]**.

## 0. One-time setup (first release only)
1. **[ASK]** Confirm the GitHub owner and repo name (default `keyvnchristian/pixelproof`).
   - If they're different, replace `keyvnchristian/pixelproof` everywhere: `package.json` (repository, homepage, bugs), `.claude-plugin/*.json`, `README.md`, `CLAUDE.md`, and `cli/pixelproof.mjs` help text (it reads `package.json`, so usually nothing to change there).
   - Also update the author names if needed.
2. **Check tools:**
   ```bash
   node -v && npm -v && git --version && gh --version && python3 --version
   gh auth status          # if not logged in: gh auth login   [ASK the human to complete the browser flow]
   npm whoami              # if not logged in: npm login       [ASK the human to complete it]
   ```
3. **Check the npm name:** `npm view pixelproof name`. An E404 means it's still free. If it's taken, **[ASK]** for a new name (or a scope like `@keyvnchristian/pixelproof`) and update `package.json`. For a scoped name, keep `bin` as `pixelproof` and publish with `--access public`.
4. **Create the GitHub repo and push:**
   ```bash
   git init -b main
   git add .
   git commit -m "pixelproof v$(node -p "require('./package.json').version")"
   gh repo create keyvnchristian/pixelproof --public --source=. --remote=origin --push \
     --description "Pixel-exact UI from design references, plus design audits and roasts. An agent skill for Claude Code, Codex and more."
   gh repo edit --add-topic claude-code,claude-skill,agent-skills,design-system,pixel-perfect,design-audit
   ```
5. **Automated publishing (optional, recommended):**
   1. **[ASK]** the human to create an npm **granular access token**: npmjs.com → avatar → Access Tokens → Generate New Token → Granular, with read and write access to this package (or all packages for the first publish).
   2. Store it in the repo: `gh secret set NPM_TOKEN` (paste the token when prompted; never echo it or write it to a file).

## 1. Every release
1. **Bump the version** in `package.json` **and** `.claude-plugin/plugin.json` (same value), and add a `CHANGELOG.md` entry.
2. **Run the checks:**
   ```bash
   npm test
   npm run smoke
   claude plugin validate .      # if the claude CLI is available
   npm pack --dry-run            # review: only cli/, skills/, .claude-plugin/, README, LICENSE, CHANGELOG
   ```
3. **[ASK]** Show the human the version, the changelog entry, and the `npm pack --dry-run` file list, and get approval.
4. **Publish.**
   - **With the workflow:**
     ```bash
     V=$(node -p "require('./package.json').version")
     git add -A && git commit -m "v$V" && git tag "v$V" && git push && git push --tags
     gh run watch   # wait for "Publish to npm"
     ```
   - **Manually:** `npm publish --access public`. npm may ask for a one-time password; **[ASK]** the human for it.
5. **Create a GitHub release with the portable skill file attached:**
   ```bash
   V=$(node -p "require('./package.json').version")
   rm -rf /tmp/pp-skill && mkdir -p /tmp/pp-skill && cp -r skills/pixelproof /tmp/pp-skill/
   sed -i.bak '/^argument-hint:/d' /tmp/pp-skill/pixelproof/SKILL.md && rm /tmp/pp-skill/pixelproof/SKILL.md.bak
   (cd /tmp/pp-skill && zip -rq "pixelproof-$V.skill" pixelproof -x "*/__pycache__/*")
   gh release create "v$V" "/tmp/pp-skill/pixelproof-$V.skill" --title "v$V" --notes-from-tag || \
   gh release create "v$V" "/tmp/pp-skill/pixelproof-$V.skill" --title "v$V" --notes "See CHANGELOG.md"
   ```
6. **Verify from a clean folder:**
   ```bash
   cd "$(mktemp -d)"
   npx pixelproof@latest --version
   npx pixelproof@latest install --local --yes && ls .claude/skills/pixelproof
   ```
   Then, in Claude Code: `/plugin marketplace add keyvnchristian/pixelproof` → `/plugin install pixelproof@pixelproof` → `/pixelproof:pixelproof help`.
7. **Report** to the human: the npm URL, the GitHub release URL, and the three install commands.

## Rollback
- **Bad npm release:** `npm deprecate pixelproof@<version> "reason"`, then publish a fixed patch version. Avoid `npm unpublish`; it's limited and breaks users.
- **Bad plugin release:** push a fix. Users get it after `/plugin marketplace update pixelproof`.
