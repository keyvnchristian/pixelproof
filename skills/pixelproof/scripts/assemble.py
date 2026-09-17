#!/usr/bin/env python3
"""Assemble self-contained slice pages.

Usage: python assemble.py <slices-dir> [--only name,name]

Reads <slices-dir>/manifest.json:
{
  "font_href": "https://fonts.googleapis.com/css2?...",   (optional)
  "lang": "en",                                            (optional)
  "css": ["shared.css"],                                   (optional, default ["shared.css"]; paths relative to the manifest)
  "sprite": "sprite.svg",                                  (optional)
  "presets": ["lumen", "linen"],                           (optional; one file per preset: <name>--<preset>.html
                                                            with <html data-preset="...">. A screen may set its own "presets")
  "out": ".",                                              (optional output folder, relative to the manifest)
  "screens": [{"name": "list", "title": "Orders", "body": "list.body.html"}]
}
and writes <out>/<name>.html (or <name>--<preset>.html) with the CSS inlined and the sprite embedded.

Body files may include partials:
  <!-- include: partials/sidebar.html {{active:orders}} -->
Inside a partial, {{#active=orders}}TEXT{{/active}} renders TEXT only when active == orders.
Any {{key}} is replaced with the include variable of the same name (or left empty).
"""
import argparse
import json
import re
import sys
from pathlib import Path

INCLUDE = re.compile(r"<!--\s*include:\s*([^\s]+)((?:\s+\{\{[\w-]+:[^}]*\}\})*)\s*-->")
VAR = re.compile(r"\{\{([\w-]+):([^}]*)\}\}")
COND = re.compile(r"\{\{#([\w-]+)=([^}]*)\}\}(.*?)\{\{/\1\}\}", re.S)
PLAIN = re.compile(r"\{\{([\w-]+)\}\}")


def render_partial(text, variables):
    text = COND.sub(lambda m: m.group(3) if variables.get(m.group(1)) == m.group(2) else "", text)
    return PLAIN.sub(lambda m: variables.get(m.group(1), ""), text)


def expand(text, base, depth=0):
    if depth > 8:
        sys.exit("include depth exceeded (circular include?)")

    def repl(m):
        path = base / m.group(1)
        if not path.exists():
            sys.exit(f"missing partial: {path}")
        variables = dict(VAR.findall(m.group(2) or ""))
        inner = render_partial(path.read_text(), variables)
        return expand(inner, base, depth + 1)

    return INCLUDE.sub(repl, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slices")
    ap.add_argument("--only")
    args = ap.parse_args()
    base = Path(args.slices)
    manifest = json.loads((base / "manifest.json").read_text())
    css = "\n\n".join((base / c).read_text().rstrip() for c in manifest.get("css", ["shared.css"]))
    sprite = (base / manifest.get("sprite", "sprite.svg")).read_text().strip()
    font = manifest.get("font_href")
    lang = manifest.get("lang", "en")
    out_dir = base / manifest.get("out", ".")
    out_dir.mkdir(parents=True, exist_ok=True)
    only = set(args.only.split(",")) if args.only else None
    font_tags = ""
    if font:
        font_tags = ('  <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
                     '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
                     f'  <link href="{font}" rel="stylesheet" />\n')
    for scr in manifest["screens"]:
        if only and scr["name"] not in only:
            continue
        body = expand((base / scr["body"]).read_text(), base)
        presets = scr.get("presets", manifest.get("presets")) or [None]
        for preset in presets:
            attr = f' data-preset="{preset}"' if preset else ""
            html = (f'<!DOCTYPE html>\n<html lang="{lang}"{attr}>\n<head>\n  <meta charset="UTF-8" />\n'
                    f'  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
                    f'  <title>{scr.get("title", scr["name"])}</title>\n{font_tags}'
                    f'<style>\n{css}\n</style>\n</head>\n<body class="{scr.get("body_class", "")}">\n\n{sprite}\n\n{body.strip()}\n\n</body>\n</html>\n')
            out = out_dir / (f"{scr['name']}--{preset}.html" if preset else f"{scr['name']}.html")
            out.write_text(html)
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
