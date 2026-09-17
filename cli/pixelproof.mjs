#!/usr/bin/env node
// pixelproof installer — copies the pixelproof skill into your AI coding tool's skills folder.
//
//   npx pixelproof                      interactive (asks for tool + location)
//   npx pixelproof install --global     ~/.claude/skills/pixelproof
//   npx pixelproof install --local      ./.claude/skills/pixelproof
//   npx pixelproof install --local --claude --codex --agents
//   npx pixelproof update [--global|--local]     reinstall the latest version over the old one
//   npx pixelproof uninstall [--global|--local] [--claude --codex --agents]
//   npx pixelproof doctor               check Python/Playwright requirements
//   npx pixelproof --version | --help
//
// Options: --dir <path> (install into a custom skills folder), --yes (no prompts), --force (overwrite).
// Env: CLAUDE_CONFIG_DIR overrides ~/.claude for global Claude Code installs.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import readline from 'node:readline';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKILL = 'pixelproof';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE = path.join(ROOT, 'skills', SKILL);
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
const MARKER = '.pixelproof-version';

const c = process.stdout.isTTY
  ? { b: (s) => `\x1b[1m${s}\x1b[0m`, d: (s) => `\x1b[2m${s}\x1b[0m`, g: (s) => `\x1b[32m${s}\x1b[0m`, r: (s) => `\x1b[31m${s}\x1b[0m`, y: (s) => `\x1b[33m${s}\x1b[0m` }
  : { b: (s) => s, d: (s) => s, g: (s) => s, r: (s) => s, y: (s) => s };

const TARGETS = {
  claude: {
    label: 'Claude Code',
    global: () => path.join(process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude'), 'skills'),
    local: (cwd) => path.join(cwd, '.claude', 'skills'),
    after: 'Restart Claude Code (or start a new session), then check with /skills.',
  },
  codex: {
    label: 'Codex CLI',
    global: () => path.join(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'), 'skills'),
    local: (cwd) => path.join(cwd, '.codex', 'skills'),
    after: 'Restart Codex to pick up the skill.',
  },
  agents: {
    label: 'Other agents (.agents/skills)',
    global: () => path.join(os.homedir(), '.agents', 'skills'),
    local: (cwd) => path.join(cwd, '.agents', 'skills'),
    after: 'Point your agent at the .agents/skills folder if it does not read it automatically.',
  },
};

function parse(argv) {
  const opts = { cmd: null, scope: null, targets: [], dir: null, yes: false, force: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (['install', 'update', 'uninstall', 'doctor', 'help'].includes(a) && !opts.cmd) opts.cmd = a;
    else if (a === '--global' || a === '-g') opts.scope = 'global';
    else if (a === '--local' || a === '-l') opts.scope = 'local';
    else if (a === '--claude') opts.targets.push('claude');
    else if (a === '--codex') opts.targets.push('codex');
    else if (a === '--agents') opts.targets.push('agents');
    else if (a === '--all') opts.targets.push('claude', 'codex', 'agents');
    else if (a === '--dir') opts.dir = argv[++i];
    else if (a === '--yes' || a === '-y') opts.yes = true;
    else if (a === '--force' || a === '-f') opts.force = true;
    else if (a === '--version' || a === '-v') opts.cmd = 'version';
    else if (a === '--help' || a === '-h') opts.cmd = 'help';
    else { console.error(c.r(`Unknown argument: ${a}`)); opts.cmd = 'help'; opts.bad = true; }
  }
  opts.targets = [...new Set(opts.targets)];
  return opts;
}

function help() {
  console.log(`${c.b('pixelproof')} ${PKG.version} — pixel-exact UI from design references

${c.b('Usage')}
  npx pixelproof                         interactive install
  npx pixelproof install [--global|--local] [--claude] [--codex] [--agents] [--all]
  npx pixelproof update  [--global|--local] [targets]
  npx pixelproof uninstall [--global|--local] [targets]
  npx pixelproof doctor                  check Python, Pillow, numpy, Playwright

${c.b('Options')}
  --global, -g   install for every project (~/.claude/skills, ~/.codex/skills, ~/.agents/skills)
  --local,  -l   install into the current project (./.claude/skills, …)
  --dir <path>   install into a custom skills folder
  --yes, -y      no prompts (defaults: Claude Code, global)
  --force, -f    overwrite an existing install

Inside your agent (after install):
  /pixelproof teach | replicate | enhance | extract | add | theme | audit | roast | compare | verify | responsive | status | help

Other ways to install:
  Claude Code plugin:  /plugin marketplace add ${repoSlug()}   then   /plugin install ${SKILL}@${SKILL}
  skills CLI:          npx skills add ${repoSlug()}`);
}

function repoSlug() {
  const url = typeof PKG.repository === 'string' ? PKG.repository : PKG.repository?.url || '';
  const m = url.match(/github\.com[/:]([^/]+\/[^/.]+)/);
  return m ? m[1] : '<owner>/pixelproof';
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    if (e.name === '__pycache__' || e.name === '.DS_Store') continue;
    const s = path.join(src, e.name);
    const d = path.join(dest, e.name);
    if (e.isDirectory()) copyDir(s, d);
    else {
      fs.copyFileSync(s, d);
      if (s.includes(`${path.sep}scripts${path.sep}`)) fs.chmodSync(d, 0o755);
    }
  }
}

// Claude Code understands extra frontmatter (argument-hint); other agents follow the portable
// Agent Skills spec, so drop Claude-only keys for them.
function stripClaudeOnlyFrontmatter(file) {
  const text = fs.readFileSync(file, 'utf8');
  const m = text.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return;
  const kept = m[1].split('\n').filter((l) => !/^(argument-hint|arguments|disable-model-invocation|user-invocable|context|agent|model|effort|when_to_use|paths|hooks|shell):/.test(l));
  fs.writeFileSync(file, `---\n${kept.join('\n')}\n---\n${text.slice(m[0].length)}`);
}

function installedVersion(dest) {
  try { return fs.readFileSync(path.join(dest, MARKER), 'utf8').trim(); } catch { return null; }
}

// Line-queue prompt: answers typed ahead are kept, and closed input falls back to defaults.
function createPrompter() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: false });
  const lines = [];
  const waiters = [];
  let closed = false;
  rl.on('line', (l) => (waiters.length ? waiters.shift()(l) : lines.push(l)));
  rl.on('close', () => { closed = true; while (waiters.length) waiters.shift()(null); });
  const next = () => (lines.length ? Promise.resolve(lines.shift()) : closed ? Promise.resolve(null) : new Promise((r) => waiters.push(r)));
  return {
    async ask(question, choices, def) {
      const list = choices.map((ch, i) => `  ${i + 1}) ${ch.label}${[].concat(def).includes(ch.value) ? c.d(' (default)') : ''}`).join('\n');
      process.stdout.write(`${question}\n${list}\n> `);
      const answer = ((await next()) ?? '').trim();
      if (answer === '') process.stdout.write('\n');
      if (!answer) return def;
      const picks = answer.split(/[ ,]+/).map((x) => choices[Number(x) - 1]?.value).filter(Boolean);
      return picks.length ? picks : def;
    },
    close: () => rl.close(),
  };
}

async function resolveChoices(opts, verb) {
  if (opts.dir) return { scope: 'custom', targets: ['custom'] };
  let { scope, targets } = opts;
  const interactive = process.stdin.isTTY && process.stdout.isTTY && !opts.yes;
  if ((!scope || !targets.length) && interactive) {
    const prompt = createPrompter();
    try {
      if (!targets.length) {
        const t = await prompt.ask(`Which tool(s) should ${verb} pixelproof? (e.g. 1 or 1,2)`,
          Object.entries(TARGETS).map(([value, v]) => ({ value, label: v.label })), ['claude']);
        targets = [].concat(t);
      }
      if (!scope) {
        const s = await prompt.ask('Where?', [
          { value: 'global', label: 'Global — available in every project' },
          { value: 'local', label: `Local — only this project (${process.cwd()})` },
        ], 'global');
        scope = [].concat(s)[0];
      }
    } finally { prompt.close(); }
  }
  return { scope: scope || 'global', targets: targets.length ? targets : ['claude'] };
}

function destFor(target, scope, opts) {
  if (opts.dir) return path.resolve(opts.dir, SKILL);
  const t = TARGETS[target];
  return path.join(scope === 'local' ? t.local(process.cwd()) : t.global(), SKILL);
}

async function install(opts, { update = false } = {}) {
  if (!fs.existsSync(path.join(SOURCE, 'SKILL.md'))) {
    console.error(c.r(`Skill files missing in package (${SOURCE}).`));
    process.exit(1);
  }
  const { scope, targets } = await resolveChoices(opts, update ? 'update' : 'install');
  for (const target of targets) {
    const dest = destFor(target, scope, opts);
    const prev = installedVersion(dest);
    const exists = fs.existsSync(dest);
    if (exists && !update && !opts.force) {
      if (prev === PKG.version) {
        console.log(`${c.g('✓')} ${label(target)} already has pixelproof ${PKG.version} at ${dest}`);
        continue;
      }
      if (!prev) {
        console.log(c.y(`! ${dest} exists but was not installed by this tool. Re-run with --force to overwrite.`));
        continue;
      }
    }
    if (exists) fs.rmSync(dest, { recursive: true, force: true });
    copyDir(SOURCE, dest);
    if (target !== 'claude' && target !== 'custom') stripClaudeOnlyFrontmatter(path.join(dest, 'SKILL.md'));
    fs.writeFileSync(path.join(dest, MARKER), `${PKG.version}\n`);
    const action = prev ? `updated ${prev} → ${PKG.version}` : `installed ${PKG.version}`;
    console.log(`${c.g('✓')} ${label(target)}: ${action}\n  ${c.d(dest)}`);
    if (TARGETS[target]) console.log(`  ${TARGETS[target].after}`);
  }
  console.log(`\nNext: run ${c.b('npx pixelproof doctor')} to check the Python/Playwright tools the skill uses.`);
  console.log(`Then, in your agent, start with ${c.b('/pixelproof teach')} (or just describe what you want).`);
}

function label(target) { return TARGETS[target]?.label || 'Custom folder'; }

async function uninstall(opts) {
  const { scope, targets } = await resolveChoices(opts, 'uninstall');
  for (const target of targets) {
    const dest = destFor(target, scope, opts);
    if (!fs.existsSync(dest)) { console.log(`${c.d('-')} ${label(target)}: nothing at ${dest}`); continue; }
    if (!installedVersion(dest) && !opts.force) {
      console.log(c.y(`! ${dest} was not installed by this tool. Re-run with --force to remove it.`));
      continue;
    }
    fs.rmSync(dest, { recursive: true, force: true });
    console.log(`${c.g('✓')} ${label(target)}: removed ${dest}`);
  }
}

function run(cmd, args) {
  const r = spawnSync(cmd, args, { encoding: 'utf8' });
  return { ok: r.status === 0, out: `${r.stdout || ''}${r.stderr || ''}`.trim() };
}

function doctor() {
  const py = ['python3', 'python'].find((p) => run(p, ['--version']).ok);
  const rows = [];
  rows.push(['Node.js', true, process.version]);
  rows.push(['Python 3', !!py, py ? run(py, ['--version']).out : 'not found']);
  if (py) {
    for (const [name, mod] of [['Pillow', 'PIL'], ['numpy', 'numpy'], ['Playwright (Python)', 'playwright']]) {
      const r = run(py, ['-c', `import ${mod}; print(getattr(${mod}, '__version__', 'ok'))`]);
      rows.push([name, r.ok, r.ok ? r.out : 'missing']);
    }
    const chrome = run(py, ['-c', 'from playwright.sync_api import sync_playwright\nwith sync_playwright() as p:\n  b=p.chromium.launch(); print("ok"); b.close()']);
    rows.push(['Chromium for Playwright', chrome.ok, chrome.ok ? 'ok' : 'not installed']);
  }
  let nodePw = false;
  try { nodePw = !!fs.realpathSync(path.join(process.cwd(), 'node_modules', 'playwright')); } catch { /* not installed */ }
  rows.push(['Playwright (Node, this project)', nodePw, nodePw ? 'ok' : 'missing — only needed for parity checks']);

  for (const [name, ok, info] of rows) console.log(`${ok ? c.g('✓') : c.r('✗')} ${name.padEnd(32)} ${c.d(info)}`);
  const fixes = [];
  if (!py) fixes.push('Install Python 3.9+ (https://www.python.org/downloads/)');
  if (py && rows.some(([n, ok]) => ['Pillow', 'numpy', 'Playwright (Python)'].includes(n) && !ok)) {
    fixes.push(`${py} -m pip install pillow numpy playwright`);
  }
  if (py && rows.some(([n, ok]) => n === 'Chromium for Playwright' && !ok)) fixes.push(`${py} -m playwright install chromium`);
  if (!nodePw) fixes.push('npm i -D playwright   (in the project where you run parity checks)');
  if (fixes.length) {
    console.log(`\n${c.b('To fix:')}`);
    for (const f of fixes) console.log(`  ${f}`);
  } else {
    console.log(`\n${c.g('All set.')}`);
  }
}

const opts = parse(process.argv.slice(2));
switch (opts.cmd) {
  case 'version': console.log(PKG.version); break;
  case 'help': help(); process.exit(opts.bad ? 1 : 0); break;
  case 'doctor': doctor(); break;
  case 'uninstall': await uninstall(opts); break;
  case 'update': await install(opts, { update: true }); break;
  case 'install':
  default:
    console.log(`${c.b('pixelproof')} ${PKG.version}\n`);
    await install(opts);
}
