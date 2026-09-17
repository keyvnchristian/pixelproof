#!/usr/bin/env node
// Smoke test: pack the package, install it with npx into a temp HOME/project, and check the result.
// Usage: npm run smoke
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const run = (cmd, opts = {}) => execSync(cmd, { stdio: 'pipe', encoding: 'utf8', ...opts });
const fail = (msg) => { console.error(`✗ ${msg}`); process.exit(1); };

const tgz = run('npm pack --silent', { cwd: root }).trim().split('\n').pop();
const tarball = path.join(root, tgz);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pixelproof-smoke-'));
const env = { ...process.env, HOME: tmp, CLAUDE_CONFIG_DIR: path.join(tmp, '.claude'), CODEX_HOME: path.join(tmp, '.codex') };
const npx = (args) => run(`npx --yes --package=${tarball} pixelproof ${args}`, { cwd: tmp, env, input: '' });

try {
  const v = npx('--version').trim();
  if (v !== pkg.version) fail(`--version printed ${v}, expected ${pkg.version}`);

  npx('install --global --claude --codex --yes');
  const claude = path.join(tmp, '.claude', 'skills', 'pixelproof');
  const codex = path.join(tmp, '.codex', 'skills', 'pixelproof');
  for (const dir of [claude, codex]) {
    if (!fs.existsSync(path.join(dir, 'SKILL.md'))) fail(`missing SKILL.md in ${dir}`);
    for (const f of ['commands/teach.md', 'commands/enhance.md', 'assets/presets/SPEC.md', 'assets/presets/gallery/build/index.html', 'scripts/perf_scan.py', 'scripts/structure_scan.py']) {
      if (!fs.existsSync(path.join(dir, f))) fail(`missing ${f} in ${dir}`);
    }
    if (fs.readFileSync(path.join(dir, '.pixelproof-version'), 'utf8').trim() !== pkg.version) fail(`wrong version marker in ${dir}`);
  }
  if (!fs.readFileSync(path.join(claude, 'SKILL.md'), 'utf8').includes('argument-hint:')) fail('Claude install lost argument-hint');
  if (fs.readFileSync(path.join(codex, 'SKILL.md'), 'utf8').includes('argument-hint:')) fail('Codex install kept argument-hint');

  const again = npx('install --global --claude --yes');
  if (!again.includes('already has')) fail('second install was not idempotent');

  npx('uninstall --global --claude --codex --yes');
  if (fs.existsSync(claude) || fs.existsSync(codex)) fail('uninstall left files behind');

  const s = fs.readFileSync(path.join(root, 'skills', 'pixelproof', 'SKILL.md'), 'utf8');
  for (const m of s.matchAll(/commands\/([a-z]+)\.md/g)) {
    if (!fs.existsSync(path.join(root, 'skills', 'pixelproof', 'commands', `${m[1]}.md`))) fail(`router points to missing commands/${m[1]}.md`);
  }
  console.log(`✓ smoke test passed for pixelproof ${pkg.version}`);
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
  fs.rmSync(tarball, { force: true });
}
