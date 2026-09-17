#!/usr/bin/env node
// Compare computed styles between a reference slice and the running app.
//
// Usage: node check_parity.mjs <parity.config.json> [--out dir] [--storage state.json] [--only name]
//
// Config (paths are relative to the current working directory):
// {
//   "widths": [1440, 1024, 390],
//   "pairs": [{ "name": "orders", "reference": "docs/pixelproof/slices/list.html",
//               "app": "http://localhost:3000/orders", "selectors": [".tabs", ".order-row"],
//               "optional": [".nav-badge"], "appSelectors": { ".tabs": "[data-ui=tabs]" } }],
//   "properties": ["height", "padding-top", ...],
//   "ignore": { "height": [".order"] },
//   "login": { "url": "http://localhost:3000/login",
//              "steps": [{ "fill": ["#email", "$ENV:APP_EMAIL"] }, { "fill": ["#password", "$ENV:APP_PASSWORD"] },
//                        { "click": "button[type=submit]" }],
//              "waitFor": ".sidebar" }
// }
// "appSelectors" maps a reference selector to a different selector in the app (optional).
// Exit code 1 when any difference or missing selector is found.
//
// Requires Playwright: `npm i -D playwright && npx playwright install chromium` (or use an existing install).

import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

// Resolve Playwright from the project (cwd) first, then from the script location.
import { createRequire } from 'node:module';
let chromium;
{
  const fromCwd = createRequire(path.join(process.cwd(), 'package.json'));
  const tries = [
    async () => (await import(pathToFileURL(fromCwd.resolve('playwright')).href)).default ?? (await import(pathToFileURL(fromCwd.resolve('playwright')).href)),
    async () => (await import(pathToFileURL(fromCwd.resolve('@playwright/test')).href)),
    async () => (await import('playwright')),
    async () => (await import('@playwright/test')),
  ];
  for (const t of tries) {
    try { const m = await t(); if (m?.chromium) { chromium = m.chromium; break; } } catch { /* try next */ }
  }
  if (!chromium) {
    console.error('Playwright not found. In the project run: npm i -D playwright && npx playwright install chromium');
    process.exit(2);
  }
}

const args = process.argv.slice(2);
const cfgPath = args.find(a => !a.startsWith('--'));
if (!cfgPath) { console.error('usage: node check_parity.mjs <config.json> [--out dir] [--storage file] [--only name]'); process.exit(2); }
const flag = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const outDir = flag('--out');
const storage = flag('--storage');
const only = flag('--only');
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));

const DEFAULT_PROPS = ['height', 'min-height', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'margin-top', 'margin-bottom', 'row-gap', 'column-gap', 'border-top-width', 'border-top-style', 'border-top-color',
  'border-right-width', 'border-bottom-width', 'border-bottom-color', 'border-left-width', 'border-top-left-radius',
  'background-color', 'box-shadow', 'color', 'font-family', 'font-size', 'font-weight', 'letter-spacing', 'line-height'];
const props = cfg.properties?.length ? cfg.properties : DEFAULT_PROPS;
const widths = cfg.widths?.length ? cfg.widths : [1440, 1024, 390];
const ignore = cfg.ignore || {};
const env = (v) => (typeof v === 'string' && v.startsWith('$ENV:') ? process.env[v.slice(5)] ?? '' : v);
const toUrl = (p) => (/^https?:\/\//.test(p) || p.startsWith('file:') ? p : pathToFileURL(path.resolve(p)).href);
const norm = (prop, v) => {
  if (v == null) return v;
  let s = String(v).trim();
  if (prop === 'font-family') s = s.split(',')[0].replace(/["']/g, '').trim().toLowerCase();
  return s.replace(/\s+/g, ' ');
};

const read = async (page, selector) => page.evaluate(([sel, ps]) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const c = getComputedStyle(el);
  const o = {};
  for (const p of ps) o[p] = c.getPropertyValue(p);
  return o;
}, [selector, props]);

const browser = await chromium.launch();
const ctxOpts = storage ? { storageState: storage } : {};
let failures = 0;
const rows = [];

async function login(context) {
  if (!cfg.login) return;
  const page = await context.newPage();
  await page.goto(cfg.login.url, { waitUntil: 'networkidle' });
  for (const step of cfg.login.steps || []) {
    if (step.fill) await page.fill(step.fill[0], env(step.fill[1]));
    if (step.click) await page.click(step.click);
    if (step.press) await page.press(step.press[0], step.press[1]);
  }
  if (cfg.login.waitFor) await page.waitForSelector(cfg.login.waitFor, { timeout: 20000 });
  await page.close();
}

for (const pair of cfg.pairs) {
  if (only && pair.name !== only) continue;
  for (const width of widths) {
    const refCtx = await browser.newContext({ viewport: { width, height: 1000 } });
    const appCtx = await browser.newContext({ viewport: { width, height: 1000 }, ...ctxOpts });
    await login(appCtx);
    const ref = await refCtx.newPage();
    const app = await appCtx.newPage();
    await ref.goto(toUrl(pair.reference), { waitUntil: 'networkidle' });
    await app.goto(toUrl(pair.app), { waitUntil: 'networkidle' });
    if (pair.waitFor) await app.waitForSelector(pair.waitFor, { timeout: 20000 });
    await ref.waitForTimeout(200); await app.waitForTimeout(200);
    if (outDir) {
      fs.mkdirSync(outDir, { recursive: true });
      await ref.screenshot({ path: path.join(outDir, `${pair.name}-${width}-reference.png`) });
      await app.screenshot({ path: path.join(outDir, `${pair.name}-${width}-app.png`) });
    }
    for (const sel of pair.selectors) {
      const appSel = pair.appSelectors?.[sel] || sel;
      const a = await read(ref, sel);
      const b = await read(app, appSel);
      const optional = (pair.optional || []).includes(sel);
      if (!a || !b) {
        if (optional) continue;
        failures++;
        rows.push({ pair: pair.name, width, selector: sel, property: '(element)', reference: a ? 'found' : 'MISSING', app: b ? 'found' : 'MISSING' });
        continue;
      }
      for (const p of props) {
        if ((ignore[p] || []).includes(sel)) continue;
        const va = norm(p, a[p]); const vb = norm(p, b[p]);
        if (va !== vb) {
          failures++;
          rows.push({ pair: pair.name, width, selector: sel, property: p, reference: va, app: vb });
        }
      }
    }
    await refCtx.close(); await appCtx.close();
  }
}
await browser.close();

if (!rows.length) {
  console.log('parity: 0 differences');
} else {
  console.log('| Page | Width | Selector | Property | Reference | App |');
  console.log('|---|---|---|---|---|---|');
  for (const r of rows) console.log(`| ${r.pair} | ${r.width} | \`${r.selector}\` | ${r.property} | \`${r.reference}\` | \`${r.app}\` |`);
  console.log(`\nparity: ${failures} difference(s)`);
}
if (outDir) {
  fs.writeFileSync(path.join(outDir, 'parity-report.json'), JSON.stringify(rows, null, 2));
  console.log(`screenshots + report: ${outDir}`);
}
process.exit(failures ? 1 : 0);
