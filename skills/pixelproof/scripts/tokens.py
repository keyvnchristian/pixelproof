#!/usr/bin/env python3
"""Inventory every design value in a stylesheet.

Usage: python tokens.py shared.css --out tokens.json [--md]

Groups: spacing, sizes, font_sizes, font_weights, line_heights, letter_spacing, radii,
        colors, shadows, breakpoints, custom_properties.
Each value lists how often it appears and the selectors that use it, so near-duplicates
(15px vs 16px for the same role) are easy to spot before building the theme.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

SPACING = {"padding", "padding-top", "padding-right", "padding-bottom", "padding-left", "padding-inline",
           "padding-block", "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
           "margin-inline", "margin-block", "gap", "row-gap", "column-gap", "top", "right", "bottom",
           "left", "inset"}
SIZES = {"width", "height", "min-width", "min-height", "max-width", "max-height", "flex", "flex-basis",
         "background-size", "grid-template-columns"}
COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)")
PX_RE = re.compile(r"(-?\d*\.?\d+)px")


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def iter_rules(css):
    """Yield (selector, declarations, media) including rules nested in @media."""
    css = strip_comments(css)
    token = re.compile(r"([^{}]*)\{|\}")
    buf_sel = []
    pos = 0
    while True:
        m = token.search(css, pos)
        if not m:
            break
        if m.group(0) == "}":
            if buf_sel:
                buf_sel.pop()
            pos = m.end()
            continue
        head = m.group(1).strip()
        body_start = m.end()
        if head.startswith(("@media", "@supports", "@keyframes", "@layer", "@container")):
            buf_sel.append(("@", head))
            pos = body_start
            continue
        end = css.find("}", body_start)
        body = css[body_start:end]
        media = " ".join(h for kind, h in buf_sel if kind == "@")
        yield head, body, media
        pos = end + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("css")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", action="store_true", help="also write a markdown table next to --out")
    args = ap.parse_args()
    css = Path(args.css).read_text()
    groups = defaultdict(lambda: defaultdict(lambda: {"count": 0, "selectors": set()}))

    def add(group, value, sel):
        g = groups[group][value]
        g["count"] += 1
        if len(g["selectors"]) < 12:
            g["selectors"].add(sel)

    for m in re.finditer(r"@media[^{]*\((?:max|min)-width:\s*(\d+)px\)", strip_comments(css)):
        add("breakpoints", f"{m.group(1)}px", "@media")

    for sel, body, media in iter_rules(css):
        sel_label = (sel if not media else f"{sel} @ {media}")[:90]
        for decl in body.split(";"):
            if ":" not in decl:
                continue
            prop, val = [x.strip() for x in decl.split(":", 1)]
            prop_l = prop.lower()
            if prop_l.startswith("--"):
                add("custom_properties", f"{prop_l}: {val}", sel_label)
            clean_val = re.sub(r"url\([^)]*\)", "", val)
            for c in COLOR_RE.findall(clean_val):
                add("colors", c.lower(), sel_label)
            if prop_l in ("box-shadow", "text-shadow") and val not in ("none", "0"):
                add("shadows", val, sel_label)
            if prop_l == "font-size":
                add("font_sizes", val, sel_label)
            elif prop_l == "font-weight":
                add("font_weights", val, sel_label)
            elif prop_l == "line-height":
                add("line_heights", val, sel_label)
            elif prop_l == "letter-spacing":
                add("letter_spacing", val, sel_label)
            elif "radius" in prop_l:
                px_vals = PX_RE.findall(val)
                if px_vals:
                    for n in px_vals:
                        add("radii", f"{abs(float(n)):g}px", sel_label)
                else:
                    add("radii", val, sel_label)
            elif prop_l in SPACING:
                for n in PX_RE.findall(clean_val):
                    add("spacing", f"{abs(float(n)):g}px", sel_label)
            elif prop_l in SIZES or prop_l.startswith("--") and PX_RE.search(val):
                for n in PX_RE.findall(clean_val):
                    add("sizes", f"{abs(float(n)):g}px", sel_label)

    def sort_key(v):
        m = re.match(r"-?\d*\.?\d+", v)
        return (0, float(m.group(0))) if m else (1, v)

    data = {}
    for g, vals in groups.items():
        data[g] = [{"value": v, "count": d["count"], "selectors": sorted(d["selectors"])}
                   for v, d in sorted(vals.items(), key=lambda kv: sort_key(kv[0]))]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"wrote {out}")
    for g in ["spacing", "sizes", "font_sizes", "font_weights", "radii", "colors", "shadows", "breakpoints"]:
        vals = [d["value"] for d in data.get(g, [])]
        print(f"{g:14} ({len(vals)}): {', '.join(vals)}")
    if args.md:
        md = ["# Token inventory", ""]
        for g, items in data.items():
            if g == "custom_properties":
                continue
            md += [f"## {g.replace('_', ' ').title()}", "", "| Value | Uses | Example selectors |", "|---|---|---|"]
            for d in items:
                md.append(f"| `{d['value']}` | {d['count']} | {', '.join('`' + s + '`' for s in d['selectors'][:4])} |")
            md.append("")
        mdp = out.with_suffix(".md")
        mdp.write_text("\n".join(md))
        print(f"wrote {mdp}")


if __name__ == "__main__":
    main()
