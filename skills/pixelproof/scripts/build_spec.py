#!/usr/bin/env python3
"""Generate style-spec.md from the slices and a template.

Usage:
  python build_spec.py <pixelproof-dir> --template style-spec.template.md --out style-spec.md
                       [--no-verify] [--width 1440]

<pixelproof-dir> must contain slices/ (shared.css, sprite.svg, manifest.json, assembled <name>.html).
Template placeholders:
  {{CSS}}         full shared.css
  {{SPRITE}}      full sprite.svg
  {{ICON_TABLE}}  markdown table: icon id -> inner SVG
  {{ICON_LIST}}   comma-separated icon ids
  {{REFERENCES}}  markdown table of assembled slices (from manifest)
  {{COMPONENTS}}  every @component block (first occurrence per name), each under a heading
  {{COMPONENT:name}}  one component block
  {{VERIFY}}      computed styles of each component's root element, read from the rendered slices
  {{PROJECT}}     value of manifest "project" (or the folder name)
  {{DIR}}         the pixelproof directory path as given
Blocks written by hand in the template are kept as-is.
"""
import argparse
import json
import re
import sys
from pathlib import Path

COMP = re.compile(r"<!--\s*@component:\s*([\w-]+)\s*-->\s*\n?(.*?)\n?\s*<!--\s*@end\s*-->", re.S)
SYMBOL = re.compile(r'<symbol id="([\w-]+)"[^>]*>(.*?)</symbol>', re.S)
PROPS = ["height", "min-height", "padding", "margin", "gap", "border-top", "border-right",
         "border-bottom", "border-left", "border-radius", "background-color", "box-shadow", "color",
         "font-size", "font-weight", "letter-spacing", "line-height"]
DEFAULTS = {"box-shadow": "none", "margin": "0px", "gap": "normal", "border-radius": "0px",
            "letter-spacing": "normal", "background-color": "rgba(0, 0, 0, 0)", "padding": "0px",
            "min-height": ("auto", "0px")}
INHERITED = ["color", "font-size", "font-weight", "letter-spacing", "line-height"]


def dedent(block):
    lines = block.split("\n")
    ind = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    return "\n".join(l[ind:] for l in lines).strip()


def root_selector(markup):
    m = re.search(r'<([a-z0-9-]+)[^>]*?class="([^"]+)"', markup)
    if not m:
        return None
    classes = m.group(2).split()
    return "." + ".".join(classes)


def assembled_path(slices, manifest, scr):
    out_dir = slices / manifest.get("out", ".")
    presets = scr.get("presets", manifest.get("presets"))
    return out_dir / (f"{scr['name']}--{presets[0]}.html" if presets else f"{scr['name']}.html")


def collect_components(slices, manifest):
    comps, order = {}, []
    for scr in manifest["screens"]:
        f = assembled_path(slices, manifest, scr)
        if not f.exists():
            sys.exit(f"missing assembled slice {f}; run assemble.py first")
        for name, markup in COMP.findall(f.read_text()):
            if name not in comps:
                comps[name] = {"markup": dedent(markup), "screen": scr["name"], "file": f}
                order.append(name)
    return comps, order


def verify_values(comps, order, width):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "_Playwright not installed; run with Playwright to fill verification values._"
    js = """(args) => {
      const [name, props, inherited] = args;
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_COMMENT);
      let el = null;
      while (walker.nextNode()) {
        const t = walker.currentNode.nodeValue.trim();
        if (t === '@component: ' + name || t.replace(/\\s+/g, ' ') === '@component: ' + name) {
          let n = walker.currentNode.nextSibling;
          while (n && n.nodeType !== 1) n = n.nextSibling;
          el = n; break;
        }
      }
      if (!el) return null;
      const c = getComputedStyle(el), body = getComputedStyle(document.body);
      const o = {};
      for (const p of props) {
        const v = c.getPropertyValue(p);
        if (inherited.includes(p) && v === body.getPropertyValue(p)) continue;
        o[p] = v;
      }
      o['width'] = Math.round(el.getBoundingClientRect().width * 100) / 100 + 'px';
      return o; }"""
    out = ["Values below were read from the rendered slices at "
           f"{width}px (`getComputedStyle` on each component's root element). Widths, and heights of "
           "content-driven blocks, are informational; everything else must match exactly. Text properties "
           "are listed only where they differ from `body`.", ""]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 1000})
        loaded = None
        for name in order:
            c = comps[name]
            sel = root_selector(c["markup"])
            if not sel:
                continue
            if loaded != c["file"]:
                page.goto(c["file"].resolve().as_uri())
                page.wait_for_timeout(150)
                loaded = c["file"]
            vals = page.evaluate(js, [name, PROPS, INHERITED])
            if not vals:
                continue
            parts = []
            for k in PROPS + ["width"]:
                v = vals.get(k, "")
                d = DEFAULTS.get(k)
                if not v or v == d or (isinstance(d, tuple) and v in d) or \
                        (k.startswith("border-") and k != "border-radius" and v.startswith("0px")):
                    continue
                parts.append(f"{k} `{v}`")
            out.append(f"- **{name}** (`{sel}`, {c['screen']}): " + ", ".join(parts))
        browser.close()
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--width", type=int, default=1440)
    args = ap.parse_args()
    root = Path(args.dir)
    slices = root / "slices" if (root / "slices" / "manifest.json").exists() else root
    manifest = json.loads((slices / "manifest.json").read_text())
    css = "\n\n".join((slices / c).read_text().rstrip() for c in manifest.get("css", ["shared.css"]))
    sprite = (slices / manifest.get("sprite", "sprite.svg")).read_text().strip()
    symbols = SYMBOL.findall(sprite)
    comps, order = collect_components(slices, manifest)

    def squash(text):
        return re.sub(r"\s+", " ", text.strip())

    icon_table = "| id | inner SVG |\n|---|---|\n" + "\n".join(
        f"| `{i}` | `{squash(body)}` |" for i, body in symbols)
    refs = "| Slice | Title | Shows |\n|---|---|---|\n" + "\n".join(
        f"| `{assembled_path(slices, manifest, s).as_posix()}` | {s.get('title', '')} | {s.get('shows', '')} |"
        for s in manifest["screens"])
    comp_md = []
    for i, name in enumerate(order, 1):
        c = comps[name]
        comp_md.append(f"### 4.{i} {name.replace('-', ' ').capitalize()}\n"
                       f"Source: `{c['screen']}.html`\n```html\n{c['markup']}\n```\n")
    tpl = Path(args.template).read_text()
    rep = {
        "{{CSS}}": css, "{{SPRITE}}": sprite, "{{ICON_TABLE}}": icon_table,
        "{{ICON_LIST}}": ", ".join(f"`{i}`" for i, _ in symbols),
        "{{REFERENCES}}": refs, "{{COMPONENTS}}": "\n".join(comp_md),
        "{{PROJECT}}": manifest.get("project", root.resolve().parent.name),
        "{{DIR}}": args.dir.rstrip("/"),
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    tpl = re.sub(r"\{\{COMPONENT:([\w-]+)\}\}",
                 lambda m: f"```html\n{comps[m.group(1)]['markup']}\n```" if m.group(1) in comps
                 else f"<!-- unknown component {m.group(1)} -->", tpl)
    if "{{VERIFY}}" in tpl:
        tpl = tpl.replace("{{VERIFY}}", "_Skipped (--no-verify)._" if args.no_verify
                          else verify_values(comps, order, args.width))
    left = re.findall(r"\{\{[A-Z_:a-z-]+\}\}", tpl)
    Path(args.out).write_text(tpl)
    print(f"wrote {args.out}: {len(order)} components, {len(symbols)} icons"
          + (f"; unreplaced placeholders: {left}" if left else ""))
    todo = len(re.findall(r"<!--\s*WRITE:", tpl))
    if todo:
        print(f"{todo} '<!-- WRITE: … -->' sections still need hand-written content")


if __name__ == "__main__":
    main()
