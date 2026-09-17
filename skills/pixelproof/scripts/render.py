#!/usr/bin/env python3
"""Render pages (slice files or app URLs) at several widths and run layout checks.

Usage:
  python render.py <file-or-url> [<file-or-url> ...] --out <dir> [--widths 1440,1024,390]
                   [--height 1000] [--full] [--storage state.json] [--wait-for SELECTOR] [--json]

Writes <out>/<name>-<width>.png, where name is the file stem, or the URL path slug.
Checks per page and width:
  overflow         document wider than the viewport (horizontal page scroll)
  missing_icons    <use href="#id"> with no matching element
  undefined_classes classes used in markup but not found in any same-origin stylesheet (files only)
  console_errors   console errors and page errors (failed font loads are reported separately)
With --deep, each page also reports (informational unless --strict):
  small_tap_targets  interactive elements smaller than 44x44 (reported at widths <= 768)
  clipped            elements whose content overflows their box, or that extend past the viewport
  low_contrast       text below WCAG AA contrast against its effective background
  small_text         text rendered below 12px
  missing_alt        <img> without an alt attribute
  unlabeled          buttons/links/inputs without an accessible name
Exit code 1 if any check fails (deep findings count only with --strict).
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright missing: pip install playwright && python -m playwright install chromium")


def target_url(t):
    if re.match(r"^https?://", t):
        slug = urlparse(t).path.strip("/")
        slug = re.sub(r"\.html?$", "", slug).replace("/", "-") or "index"
        return t, slug
    p = Path(t).resolve()
    if not p.exists():
        sys.exit(f"not found: {t}")
    return p.as_uri(), p.stem


CHECK_JS = r"""
() => {
  const overflow = document.documentElement.scrollWidth > window.innerWidth + 1;
  const missing = [...document.querySelectorAll('use')]
    .map(u => u.getAttribute('href') || u.getAttribute('xlink:href'))
    .filter(h => h && h.startsWith('#') && !document.getElementById(h.slice(1)));
  const used = new Set();
  document.querySelectorAll('[class]').forEach(el => {
    const c = el.getAttribute('class');
    if (typeof c === 'string') c.split(/\s+/).filter(Boolean).forEach(x => used.add(x));
  });
  let cssText = '';
  for (const sheet of document.styleSheets) {
    try { for (const r of sheet.cssRules) cssText += r.cssText + '\n'; } catch (e) {}
  }
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const undef = [...used].filter(c => !new RegExp('\\.' + esc(CSS.escape(c)) + '(?![\\w-])').test(cssText));
  return { overflow, scrollWidth: document.documentElement.scrollWidth,
           missing_icons: [...new Set(missing)], undefined_classes: undef.sort() };
}
"""


DEEP_JS = r"""
(vw) => {
  const path = (el) => {
    const parts = [];
    while (el && el.nodeType === 1 && parts.length < 4) {
      let p = el.tagName.toLowerCase();
      if (el.id) { parts.unshift(p + '#' + el.id); break; }
      const cls = (typeof el.className === 'string' ? el.className : '').trim().split(/\s+/).filter(Boolean).slice(0, 2);
      if (cls.length) p += '.' + cls.join('.');
      parts.unshift(p); el = el.parentElement;
    }
    return parts.join(' > ');
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect(); const c = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && c.visibility !== 'hidden' && c.display !== 'none' && c.opacity !== '0';
  };
  const parse = (s) => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
  const lum = ({ r, g, b }) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const bgOf = (el) => {
    let layers = [];
    for (let n = el; n; n = n.parentElement) {
      const c = getComputedStyle(n);
      if (c.backgroundImage && c.backgroundImage !== 'none') return null; // gradient/image: can't judge
      const p = parse(c.backgroundColor); if (p && p.a > 0) { layers.push(p); if (p.a >= 1) break; }
    }
    let out = { r: 255, g: 255, b: 255 };
    for (const l of layers.reverse()) out = { r: l.r * l.a + out.r * (1 - l.a), g: l.g * l.a + out.g * (1 - l.a), b: l.b * l.a + out.b * (1 - l.a) };
    return out;
  };
  const res = { small_tap_targets: [], clipped: [], low_contrast: [], small_text: [], missing_alt: [], unlabeled: [] };
  const interactive = document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=tab], [role=menuitem]');
  const inlineInText = (el) => {
    // WCAG 2.5.8 exception: links inside a sentence
    if (getComputedStyle(el).display !== 'inline') return false;
    const p = el.parentElement;
    return p && [...p.childNodes].some((n) => n !== el && n.nodeType === 3 && n.textContent.trim().length > 0);
  };
  for (const el of interactive) {
    if (!visible(el)) continue;
    // a checkbox/radio/input wrapped in (or tied to) a label is tapped through the label
    const lab = el.closest('label') || (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`));
    const r = (lab && /^(checkbox|radio)$/.test(el.type || '') ? lab : el).getBoundingClientRect();
    const hidden = el.getBoundingClientRect().width <= 2 && el.getBoundingClientRect().height <= 2; // sr-only inputs
    if (vw <= 768 && !hidden && !inlineInText(el) && (r.width < 44 || r.height < 44)) res.small_tap_targets.push({ el: path(el), size: `${Math.round(r.width)}x${Math.round(r.height)}` });
    const name = (el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('aria-labelledby') || el.textContent || el.getAttribute('placeholder') || el.value || '').trim();
    const labelled = el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
    const hasImgAlt = el.querySelector && el.querySelector('img[alt]:not([alt=""])');
    if (!name && !labelled && !hasImgAlt && !el.closest('label')) res.unlabeled.push({ el: path(el) });
  }
  for (const img of document.querySelectorAll('img:not([alt])')) if (visible(img)) res.missing_alt.push({ el: path(img), src: (img.getAttribute('src') || '').slice(0, 80) });
  const all = document.body.querySelectorAll('*');
  let checked = 0;
  for (const el of all) {
    if (!visible(el)) continue;
    const c = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.right > vw + 1 && c.position !== 'fixed') {
      let scroller = false;
      for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
        const ox = getComputedStyle(n).overflowX; if (ox === 'auto' || ox === 'scroll' || ox === 'hidden') { scroller = true; break; }
      }
      if (!scroller) res.clipped.push({ el: path(el), why: `extends ${Math.round(r.right - vw)}px past viewport` });
    }
    if (el.scrollWidth > el.clientWidth + 2 && c.overflowX === 'visible' && el.clientWidth > 0 && !['html', 'body'].includes(el.tagName.toLowerCase())) {
      res.clipped.push({ el: path(el), why: `content ${el.scrollWidth}px in ${el.clientWidth}px box` });
    }
    const direct = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!direct) continue;
    const fs = parseFloat(c.fontSize);
    if (fs < 12) res.small_text.push({ el: path(el), size: c.fontSize, text: el.textContent.trim().slice(0, 40) });
    if (checked++ > 400) continue;
    const fg = parse(c.color); const bg = bgOf(el);
    if (!fg || !bg) continue;
    const blended = { r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a) };
    const L1 = lum(blended), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const large = fs >= 24 || (fs >= 18.66 && parseInt(c.fontWeight) >= 700);
    if (ratio < (large ? 3 : 4.5)) res.low_contrast.push({ el: path(el), ratio: Math.round(ratio * 100) / 100, text: el.textContent.trim().slice(0, 40), color: c.color });
  }
  const dedupe = (arr) => { const seen = new Set(); return arr.filter((x) => { const k = x.el + (x.why || ''); if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, 25); };
  for (const k of Object.keys(res)) res[k] = dedupe(res[k]);
  return res;
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--widths", default="1440,1024,390")
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--full", action="store_true", help="full-page screenshots")
    ap.add_argument("--storage", help="Playwright storage state (for logged-in apps)")
    ap.add_argument("--wait-for", help="selector to wait for before capturing")
    ap.add_argument("--deep", action="store_true", help="add tap-target, clipping, contrast, alt, label and small-text checks")
    ap.add_argument("--strict", action="store_true", help="deep findings make the run fail")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    widths = [int(w) for w in args.widths.split(",")]
    report, failed = [], False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx_kwargs = {"storage_state": args.storage} if args.storage else {}
        for t in args.targets:
            url, name = target_url(t)
            is_file = url.startswith("file:")
            for w in widths:
                ctx = browser.new_context(viewport={"width": w, "height": args.height}, **ctx_kwargs)
                page = ctx.new_page()
                errors, font_errors = [], []

                def on_console(msg, errors=errors, font_errors=font_errors):
                    if msg.type == "error":
                        (font_errors if "font" in msg.text.lower() or "403" in msg.text else errors).append(msg.text)

                page.on("console", on_console)
                page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
                page.on("requestfailed", lambda r, font_errors=font_errors:
                        font_errors.append(r.url) if "font" in r.url else None)
                page.goto(url, wait_until="networkidle")
                if args.wait_for:
                    page.wait_for_selector(args.wait_for)
                page.wait_for_timeout(250)
                res = page.evaluate(CHECK_JS)
                if not is_file:
                    res["undefined_classes"] = []  # app pages use many utility/framework classes
                shot = out / f"{name}-{w}.png"
                page.screenshot(path=str(shot), full_page=args.full)
                item = {"target": t, "width": w, "screenshot": str(shot), "overflow": res["overflow"],
                        "scroll_width": res["scrollWidth"], "missing_icons": res["missing_icons"],
                        "undefined_classes": res["undefined_classes"], "console_errors": errors,
                        "font_load_issues": font_errors}
                if args.deep:
                    item["deep"] = page.evaluate(DEEP_JS, w)
                bad = res["overflow"] or res["missing_icons"] or res["undefined_classes"] or errors
                if args.deep and args.strict:
                    bad = bad or any(item["deep"][k] for k in item["deep"])
                failed = failed or bool(bad)
                report.append(item)
                ctx.close()
        browser.close()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for r in report:
            flags = []
            if r["overflow"]:
                flags.append(f"OVERFLOW (scrollWidth {r['scroll_width']})")
            if r["missing_icons"]:
                flags.append(f"missing icons {r['missing_icons']}")
            if r["undefined_classes"]:
                flags.append(f"undefined classes {r['undefined_classes']}")
            if r["console_errors"]:
                flags.append(f"console errors {r['console_errors'][:3]}")
            note = " (font requests failed; screenshot uses fallback font)" if r["font_load_issues"] else ""
            print(f"{'FAIL' if flags else 'ok  '} {Path(r['screenshot']).name}: {'; '.join(flags) or 'clean'}{note}")
            if "deep" in r:
                d = r["deep"]
                summary = ", ".join(f"{k.replace('_', ' ')} {len(v)}" for k, v in d.items() if v) or "no deep findings"
                print(f"     deep: {summary}")
                for k, v in d.items():
                    for x in v[:3]:
                        extra = " ".join(f"{kk}={vv}" for kk, vv in x.items() if kk != "el")
                        print(f"       - {k}: {x['el']} {extra}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
