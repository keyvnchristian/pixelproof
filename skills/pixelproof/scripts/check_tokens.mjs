#!/usr/bin/env node
// Fail when raw design values appear outside the theme files.
//
// Usage: node check_tokens.mjs <src-dir> [<src-dir> ...] --theme <theme-dir> [--allow <glob-ish>]... [--json]
//
// Flags hex colors, rgb()/rgba()/hsl() values and px lengths in .css .scss .less .ts .tsx .js .jsx .vue .svelte
// files that are not inside --theme. Allowed: 0 / 0px, values inside var(--x, fallback), SVG path data,
// percentages, fr, em/rem, unitless numbers, and any line containing "pixelproof-allow".
// --allow takes simple patterns matched against the relative path (* = any chars), e.g. --allow "*.svg" --allow "*/vendor/*".

import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
const dirs = []; const allow = []; let theme = null; let asJson = false;
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--theme') theme = path.resolve(argv[++i]);
  else if (a === '--allow') allow.push(argv[++i]);
  else if (a === '--json') asJson = true;
  else dirs.push(path.resolve(a));
}
if (!dirs.length || !theme) {
  console.error('usage: node check_tokens.mjs <src-dir> [...] --theme <theme-dir> [--allow pattern] [--json]');
  process.exit(2);
}

const EXT = new Set(['.css', '.scss', '.less', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.vue', '.svelte']);
const SKIP_DIRS = new Set(['node_modules', '.next', 'dist', 'build', '.git', 'coverage', '.turbo', 'out']);
const toRe = (p) => new RegExp('^' + p.split('*').map(s => s.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$');
const allowRes = allow.map(toRe);

const HEX = /#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/g;
const FUNC = /\b(?:rgba?|hsla?)\(\s*[\d.]/g;
const PX = /(?<![\w-])-?\d*\.?\d+px\b/g;

function stripAllowed(line) {
  // remove var() fallbacks, SVG path data, url(), and string literals that look like ids/selectors
  return line
    .replace(/var\(\s*--[\w-]+\s*,[^)]*\)/g, 'var()')
    .replace(/\sd=["'][^"']*["']/g, ' d=""')
    .replace(/url\([^)]*\)/g, 'url()')
    // '#i-search' sprite refs / anchors, but keep quoted hex colors like '#ff0000'
    .replace(/(['"])(#[\w-]+)\1/g, (m, q, id) => (/^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(id) ? m : '""'));
}

const violations = [];
function scan(file, root) {
  const rel = path.relative(root, file);
  if (allowRes.some(r => r.test(rel) || r.test(path.basename(file)))) return;
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  let inBlockComment = false;
  lines.forEach((raw, idx) => {
    let line = raw;
    if (inBlockComment) { const e = line.indexOf('*/'); if (e < 0) return; line = line.slice(e + 2); inBlockComment = false; }
    line = line.replace(/\/\*.*?\*\//g, '');
    const s = line.indexOf('/*'); if (s >= 0) { inBlockComment = true; line = line.slice(0, s); }
    if (/^\s*\/\//.test(line) || raw.includes('pixelproof-allow')) return;
    const clean = stripAllowed(line);
    const found = [];
    for (const m of clean.matchAll(HEX)) found.push(m[0]);
    for (const m of clean.matchAll(FUNC)) found.push(m[0] + '…)');
    for (const m of clean.matchAll(PX)) if (!/^-?0*\.?0+px$/.test(m[0])) found.push(m[0]);
    for (const v of found) violations.push({ file: path.relative(process.cwd(), file), line: idx + 1, value: v, text: raw.trim().slice(0, 120) });
  });
}

function walk(dir, root) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name) || full === theme || full.startsWith(theme + path.sep)) continue;
      walk(full, root);
    } else if (EXT.has(path.extname(entry.name)) && !full.startsWith(theme + path.sep)) {
      scan(full, root);
    }
  }
}
for (const d of dirs) walk(d, d);

if (asJson) console.log(JSON.stringify(violations, null, 2));
else if (!violations.length) console.log('token check: 0 raw values outside the theme');
else {
  for (const v of violations) console.log(`${v.file}:${v.line}  ${v.value}    ${v.text}`);
  console.log(`\ntoken check: ${violations.length} raw value(s) outside ${path.relative(process.cwd(), theme) || theme}`);
}
process.exit(violations.length ? 1 : 0);
