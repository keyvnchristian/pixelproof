#!/usr/bin/env python3
"""Static design-consistency scan of a frontend codebase.

Usage: python audit_scan.py <path> --out scan.json [--md scan.md] [--theme <dir>] [--max-files 5000]

Scans .css/.scss/.sass/.less/.ts/.tsx/.js/.jsx/.vue/.svelte/.html/.astro/.mdx files (skipping
node_modules, build output, and vendored folders) and reports, per category, the distinct values
with counts and file:line samples, plus heuristic 0-100 scores:

  color        hex/rgb/hsl literals, Tailwind palette + arbitrary colors, near-duplicate clusters
  spacing      padding/margin/gap/inset px values and Tailwind spacing classes, arbitrary values
  typography   font sizes, weights, families
  shape        radii, shadows
  icons        icon libraries imported, inline <svg> count, distinct stroke widths
  components   duplicate primitives (several Button/Card/Modal… implementations), inline styles,
               !important, z-index spread, arbitrary Tailwind values

Scores are heuristics meant to rank problems and track progress between runs, not absolute grades.
Values inside --theme (token files) are counted as "defined" and excluded from raw-value penalties.
"""
import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

EXTS = {".css", ".scss", ".sass", ".less", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue", ".svelte",
        ".html", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".next", "dist", "build", "out", ".git", "coverage", ".turbo", ".vercel",
             ".svelte-kit", ".nuxt", ".output", "vendor", "storybook-static", ".cache", "__pycache__"}
SKIP_TOP = {"public", "docs", "static", "e2e", "tests", "test", "__tests__", "fixtures"}
COMPONENT_EXTS = {".tsx", ".jsx", ".vue", ".svelte", ".astro"}
STYLE_EXTS = {".css", ".scss", ".sass", ".less"}

HEX = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
FUNC_COLOR = re.compile(r"\b(?:rgba?|hsla?)\(\s*[\d.]+[\s,%]+[\d.]+%?[\s,]+[\d.]+%?(?:[\s,/]+[\d.]+%?)?\s*\)")
TW_PALETTE = re.compile(
    r"(?<![\w-])(?:[a-z-]+:)*(?:bg|text|border|ring|fill|stroke|from|via|to|divide|outline|decoration|accent|caret|placeholder|shadow)"
    r"-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)"
    r"-(50|100|200|300|400|500|600|700|800|900|950)\b")
TW_ARBITRARY = re.compile(r"(?<![\w-])(?:[a-z-]+:)*-?[a-z]+(?:-[a-z]+)*-\[([^\]\s]+)\]")
TW_SPACING = re.compile(
    r"(?<![\w-])(?:[a-z-]+:)*-?(p|px|py|pt|pr|pb|pl|ps|pe|m|mx|my|mt|mr|mb|ml|ms|me|gap|gap-x|gap-y|space-x|space-y|inset|inset-x|inset-y|top|right|bottom|left)"
    r"-(\d+(?:\.\d+)?|px)\b")
TW_TEXT_SIZE = re.compile(r"(?<![\w-])(?:[a-z-]+:)*text-(xs|sm|base|lg|xl|[2-9]xl)\b")
TW_WEIGHT = re.compile(r"(?<![\w-])(?:[a-z-]+:)*font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)\b")
TW_ROUNDED = re.compile(r"(?<![\w-])(?:[a-z-]+:)*rounded(?:-(?:t|r|b|l|tl|tr|br|bl|s|e|ss|se|es|ee))?(?:-(none|sm|md|lg|xl|2xl|3xl|full))?(?=[\s\"'`}])")
TW_SHADOW = re.compile(r"(?<![\w-])(?:[a-z-]+:)*shadow(?:-(sm|md|lg|xl|2xl|inner|none))?(?=[\s\"'`}])")
TW_Z = re.compile(r"(?<![\w-])(?:[a-z-]+:)*z-(\d+|auto)\b")
TW_BP = re.compile(r"(?<![\w-])(sm|md|lg|xl|2xl):")
DECL = re.compile(r"(?<![\w-])(padding(?:-[a-z]+)?|margin(?:-[a-z]+)?|gap|row-gap|column-gap|top|right|bottom|left|inset|"
                  r"font-size|font-weight|font-family|border-radius|border-[a-z-]*radius|box-shadow|z-index)\s*:\s*([^;{}\n]+)")
JS_STYLE = re.compile(r"\b(padding\w*|margin\w*|gap|rowGap|columnGap|fontSize|fontWeight|borderRadius|boxShadow|zIndex|fontFamily)\s*:\s*(['\"][^'\"]+['\"]|\d+(?:\.\d+)?)")
PX = re.compile(r"(-?\d*\.?\d+)px")
MEDIA = re.compile(r"@media[^{]*\((?:max|min)-width:\s*(\d+)px")
IMPORTANT = re.compile(r"!important")
INLINE_STYLE = re.compile(r"style=\{\{|\sstyle=\"")
SVG_TAG = re.compile(r"<svg\b")
STROKE_W = re.compile(r"stroke-?[wW]idth[=:]\s*[\"'{]?\s*([\d.]+)")
ICON_LIBS = {
    "lucide": re.compile(r"from\s+['\"](lucide-react|lucide-vue-next|lucide-svelte|lucide)['\"]"),
    "heroicons": re.compile(r"from\s+['\"]@heroicons/"),
    "react-icons": re.compile(r"from\s+['\"]react-icons/"),
    "tabler": re.compile(r"from\s+['\"]@tabler/icons"),
    "phosphor": re.compile(r"from\s+['\"](@phosphor-icons/|phosphor-react)"),
    "radix-icons": re.compile(r"from\s+['\"]@radix-ui/react-icons['\"]"),
    "mui-icons": re.compile(r"from\s+['\"]@mui/icons-material"),
    "feather": re.compile(r"from\s+['\"](react-feather|feather-icons)['\"]"),
    "fontawesome": re.compile(r"from\s+['\"]@fortawesome/"),
    "iconoir": re.compile(r"from\s+['\"]iconoir-react['\"]"),
    "iconify": re.compile(r"from\s+['\"]@iconify/"),
    "remix": re.compile(r"from\s+['\"]@remixicon/"),
}
PRIMITIVES = ["button", "card", "modal", "dialog", "table", "input", "select", "badge", "tag", "avatar",
              "tabs", "dropdown", "tooltip", "sidebar", "navbar", "header", "pagination", "checkbox", "toggle", "switch"]


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def norm_hex(h):
    r, g, b = hex_to_rgb(h)
    return "#%02x%02x%02x" % (r, g, b)


def srgb_to_lab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return math.dist(srgb_to_lab(a), srgb_to_lab(b))


def clusters(colors, threshold):
    items = sorted(colors)
    rgbs = {c: hex_to_rgb(c) for c in items}
    seen, out = set(), []
    for c in items:
        if c in seen:
            continue
        group = [c]
        for d in items:
            if d != c and d not in seen and delta_e(rgbs[c], rgbs[d]) < threshold:
                group.append(d)
        if len(group) > 1:
            seen.update(group)
            out.append(group)
    return out


class Bag:
    def __init__(self):
        self.data = defaultdict(lambda: {"count": 0, "samples": []})

    def add(self, key, where):
        d = self.data[key]
        d["count"] += 1
        if len(d["samples"]) < 4:
            d["samples"].append(where)

    def as_list(self, sort_numeric=False):
        def k(item):
            m = re.match(r"-?\d*\.?\d+", item[0])
            return (0, float(m.group(0))) if sort_numeric and m else (1, -item[1]["count"], item[0])
        return [{"value": v, "count": d["count"], "samples": d["samples"]}
                for v, d in sorted(self.data.items(), key=k)]

    def __len__(self):
        return len(self.data)


def clamp(v):
    return max(0, min(100, round(v)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--theme", help="token/theme folder; values there are not penalized")
    ap.add_argument("--max-files", type=int, default=5000)
    args = ap.parse_args()
    root = Path(args.path).resolve()
    theme = Path(args.theme).resolve() if args.theme else None

    colors, tw_palette, spacing, tw_spacing, sizes, tw_sizes = Bag(), Bag(), Bag(), Bag(), Bag(), Bag()
    weights, families, radii, tw_radii, shadows, tw_shadows = Bag(), Bag(), Bag(), Bag(), Bag(), Bag()
    zidx, bps, arbitrary, icon_libs, strokes = Bag(), Bag(), Bag(), Bag(), Bag()
    counts = defaultdict(int)
    primitive_files = defaultdict(list)
    raw_colors_outside_theme = 0
    files = []

    for p in root.rglob("*"):
        if len(files) >= args.max_files:
            break
        if p.is_dir() or p.suffix.lower() not in EXTS:
            continue
        rel_parts = p.relative_to(root).parts
        if any(part in SKIP_DIRS or (part.startswith(".") and part != ".storybook") for part in rel_parts[:-1]):
            continue
        if len(rel_parts) > 1 and rel_parts[0] in SKIP_TOP:
            continue
        if p.name.endswith((".min.css", ".min.js", ".d.ts", ".test.tsx", ".test.ts", ".spec.ts", ".spec.tsx", ".stories.tsx")):
            continue
        files.append(p)

    tailwind = any((root / n).exists() for n in ("tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs", "tailwind.config.mjs"))
    for p in files:
        rel = str(p.relative_to(root))
        in_theme = bool(theme and (p == theme or theme in p.parents))
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        if "@tailwind" in text or '@import "tailwindcss"' in text or "@import 'tailwindcss'" in text:
            tailwind = True
        stem = p.stem.lower().replace("-", "").replace("_", "")
        if p.suffix in COMPONENT_EXTS and stem not in ("index", "page", "layout"):
            for prim in PRIMITIVES:
                if stem == prim or (stem.endswith(prim) and len(stem) <= len(prim) + 10):
                    primitive_files[prim].append(rel)
                    break
        counts["files"] += 1
        counts["svg_inline"] += len(SVG_TAG.findall(text))
        counts["important"] += len(IMPORTANT.findall(text))
        counts["inline_style"] += len(INLINE_STYLE.findall(text))
        for name, rx in ICON_LIBS.items():
            if rx.search(text):
                icon_libs.add(name, rel)
        for i, line in enumerate(text.split("\n"), 1):
            where = f"{rel}:{i}"
            clean = re.sub(r"url\([^)]*\)", "", line)
            if re.search(r"^\s*(//|\*|/\*)", clean):
                continue
            for h in HEX.findall(clean):
                if len(h) in (4, 5, 7, 9):
                    colors.add(norm_hex(h), where)
                    raw_colors_outside_theme += 0 if in_theme else 1
            for f in FUNC_COLOR.findall(clean):
                colors.add(re.sub(r"\s+", "", f.lower()), where)
                raw_colors_outside_theme += 0 if in_theme else 1
            for m in TW_PALETTE.finditer(clean):
                tw_palette.add(f"{m.group(1)}-{m.group(2)}", where)
            for m in TW_ARBITRARY.finditer(clean):
                arbitrary.add(m.group(0).split(":")[-1], where)
                val = m.group(1)  # colors inside [..] are already counted by the HEX pass
                for n in PX.findall(val):
                    kind = m.group(0).split(":")[-1].split("-[")[0].lstrip("-")
                    if kind in ("text",):
                        sizes.add(f"{float(n):g}px", where)
                    elif kind.startswith("rounded"):
                        radii.add(f"{float(n):g}px", where)
                    elif re.match(r"^(p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml|gap|space|inset|top|left|right|bottom)", kind):
                        spacing.add(f"{abs(float(n)):g}px", where)
            for m in TW_SPACING.finditer(clean):
                tw_spacing.add(m.group(2), where)
            for m in TW_TEXT_SIZE.finditer(clean):
                tw_sizes.add(m.group(1), where)
            for m in TW_WEIGHT.finditer(clean):
                weights.add(m.group(1), where)
            for m in TW_ROUNDED.finditer(clean):
                tw_radii.add(m.group(1) or "DEFAULT", where)
            for m in TW_SHADOW.finditer(clean):
                tw_shadows.add(m.group(1) or "DEFAULT", where)
            for m in TW_Z.finditer(clean):
                zidx.add(m.group(1), where)
            for m in TW_BP.finditer(clean):
                bps.add(m.group(1), where)
            for m in MEDIA.finditer(clean):
                bps.add(f"{m.group(1)}px", where)
            for m in STROKE_W.finditer(clean):
                strokes.add(m.group(1), where)
            decls = list(DECL.finditer(clean)) + list(JS_STYLE.finditer(clean))
            for m in decls:
                prop, val = m.group(1).lower(), m.group(2).strip().strip("'\"")
                if in_theme or "var(" in val:
                    continue
                if prop.startswith(("padding", "margin")) or prop in ("gap", "rowgap", "columngap", "row-gap", "column-gap", "top", "right", "bottom", "left", "inset"):
                    nums = PX.findall(val) or ([val] if re.fullmatch(r"\d+(\.\d+)?", val) else [])
                    for n in nums:
                        if float(n) != 0:
                            spacing.add(f"{abs(float(n)):g}px", where)
                elif prop in ("font-size", "fontsize"):
                    sizes.add(val if not re.fullmatch(r"\d+(\.\d+)?", val) else f"{val}px", where)
                elif prop in ("font-weight", "fontweight"):
                    weights.add(val, where)
                elif prop in ("font-family", "fontfamily"):
                    families.add(val.split(",")[0].strip().strip("'\""), where)
                elif "radius" in prop:
                    radii.add(val if not re.fullmatch(r"\d+(\.\d+)?", val) else f"{val}px", where)
                elif prop in ("box-shadow", "boxshadow") and val not in ("none", "0"):
                    shadows.add(val, where)
                elif prop in ("z-index", "zindex"):
                    zidx.add(val, where)
        for m in re.finditer(r"next/font/google['\"]", text):
            for fam in re.findall(r"import\s*\{([^}]+)\}\s*from\s*['\"]next/font/google", text):
                for f in fam.split(","):
                    if f.strip():
                        families.add(f.strip().replace("_", " "), rel)
            break

    color_list = [c["value"] for c in colors.as_list() if c["value"].startswith("#")]
    near = clusters(color_list, 2.2)  # ΔE76 < 2.2 ≈ not distinguishable at a glance
    dup_primitives = {k: sorted(set(v)) for k, v in primitive_files.items() if len(set(v)) > 1}

    distinct_colors = len(colors) + len(tw_palette)
    palette_families = {v["value"].split("-")[0] for v in tw_palette.as_list()}
    neutral_families = palette_families & {"slate", "gray", "zinc", "neutral", "stone"}
    distinct_spacing = len(spacing) + len(tw_spacing)
    distinct_sizes = len(sizes) + len(tw_sizes)
    scores = {
        "color": clamp(100 - max(0, distinct_colors - 14) * 2.5 - len(near) * 4
                       - max(0, len(neutral_families) - 1) * 8 - min(20, raw_colors_outside_theme * 0.1)),
        "spacing": clamp(100 - max(0, distinct_spacing - 16) * 2.5 - min(25, len([a for a in arbitrary.as_list() if "px" in a["value"]]) * 0.8)),
        "typography": clamp(100 - max(0, distinct_sizes - 8) * 5 - max(0, len(weights) - 4) * 6 - max(0, len(families) - 2) * 12),
        "shape": clamp(100 - max(0, len(radii) + len(tw_radii) - 4) * 7 - max(0, len(shadows) + len(tw_shadows) - 3) * 7),
        "icons": clamp(100 - max(0, len(icon_libs) - 1) * 30 - max(0, len(strokes) - 2) * 8),
        "components": clamp(100 - len(dup_primitives) * 10 - min(25, counts["inline_style"] * 0.5)
                            - min(20, counts["important"] * 2) - max(0, len(zidx) - 6) * 3),
    }
    weights_map = {"color": 15, "spacing": 15, "typography": 15, "shape": 10, "icons": 10, "components": 15}
    overall = round(sum(scores[k] * w for k, w in weights_map.items()) / sum(weights_map.values()))

    data = {
        "root": str(root), "files_scanned": counts["files"], "tailwind": tailwind,
        "scores": scores, "static_overall": overall,
        "summary": {
            "distinct_colors": distinct_colors, "near_duplicate_color_clusters": len(near),
            "raw_colors_outside_theme": raw_colors_outside_theme,
            "tailwind_neutral_families": sorted(neutral_families),
            "distinct_spacing": distinct_spacing, "distinct_font_sizes": distinct_sizes,
            "font_weights": len(weights), "font_families": len(families),
            "radii": len(radii) + len(tw_radii), "shadows": len(shadows) + len(tw_shadows),
            "z_index_values": len(zidx), "icon_libraries": [i["value"] for i in icon_libs.as_list()],
            "inline_svg": counts["svg_inline"], "svg_stroke_widths": [s["value"] for s in strokes.as_list(True)],
            "inline_styles": counts["inline_style"], "important": counts["important"],
            "arbitrary_tailwind_values": sum(a["count"] for a in arbitrary.as_list()),
            "duplicate_primitives": dup_primitives,
        },
        "colors": colors.as_list(), "near_duplicate_colors": near, "tailwind_palette": tw_palette.as_list(),
        "spacing": spacing.as_list(True), "tailwind_spacing": tw_spacing.as_list(True),
        "font_sizes": sizes.as_list(True), "tailwind_font_sizes": tw_sizes.as_list(),
        "font_weights": weights.as_list(), "font_families": families.as_list(),
        "radii": radii.as_list(True), "tailwind_radii": tw_radii.as_list(),
        "shadows": shadows.as_list(), "tailwind_shadows": tw_shadows.as_list(),
        "z_index": zidx.as_list(True), "breakpoints": bps.as_list(True),
        "arbitrary_values": arbitrary.as_list()[:60], "icon_libraries": icon_libs.as_list(),
        "svg_stroke_widths": strokes.as_list(True),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))

    s = data["summary"]
    lines = [f"Scanned {counts['files']} files under {root} (tailwind: {'yes' if tailwind else 'no'})",
             f"Static score: {overall}/100  " + "  ".join(f"{k} {v}" for k, v in scores.items()),
             f"colors {s['distinct_colors']} (near-duplicate clusters {s['near_duplicate_color_clusters']}, raw outside theme {s['raw_colors_outside_theme']})"
             + (f", neutral families {', '.join(s['tailwind_neutral_families'])}" if s['tailwind_neutral_families'] else ""),
             f"spacing values {s['distinct_spacing']} · font sizes {s['distinct_font_sizes']} · weights {s['font_weights']} · families {s['font_families']}",
             f"radii {s['radii']} · shadows {s['shadows']} · z-index values {s['z_index_values']}",
             f"icon libraries {s['icon_libraries'] or 'none'} · inline svg {s['inline_svg']} · stroke widths {s['svg_stroke_widths']}",
             f"inline styles {s['inline_styles']} · !important {s['important']} · arbitrary tailwind values {s['arbitrary_tailwind_values']}",
             f"duplicate primitives: {', '.join(f'{k} ({len(v)})' for k, v in dup_primitives.items()) or 'none'}"]
    if near:
        lines.append("near-duplicate colors: " + "; ".join(" ≈ ".join(g) for g in near[:8]))
    print("\n".join(lines))
    print(f"wrote {out}")

    if args.md:
        md = [f"# Static scan — {root.name}", "", f"Files: {counts['files']} · Tailwind: {'yes' if tailwind else 'no'} · Static score: **{overall}/100**", "",
              "| Category | Score |", "|---|---|"] + [f"| {k} | {v} |" for k, v in scores.items()] + [""]

        def table(title, items, n=25):
            if not items:
                return []
            rows = [f"## {title}", "", "| Value | Uses | Samples |", "|---|---|---|"]
            for it in items[:n]:
                rows.append(f"| `{it['value']}` | {it['count']} | {', '.join('`' + x + '`' for x in it['samples'][:2])} |")
            return rows + [""]
        md += table("Colors", data["colors"]) + table("Tailwind palette", data["tailwind_palette"])
        if near:
            md += ["## Near-duplicate colors", ""] + [f"- {' ≈ '.join(g)}" for g in near] + [""]
        md += table("Spacing (px)", data["spacing"]) + table("Tailwind spacing", data["tailwind_spacing"])
        md += table("Font sizes", data["font_sizes"]) + table("Tailwind font sizes", data["tailwind_font_sizes"])
        md += table("Font weights", data["font_weights"]) + table("Font families", data["font_families"])
        md += table("Radii", data["radii"]) + table("Tailwind radii", data["tailwind_radii"])
        md += table("Shadows", data["shadows"]) + table("Tailwind shadows", data["tailwind_shadows"])
        md += table("z-index", data["z_index"]) + table("Breakpoints", data["breakpoints"])
        md += table("Icon libraries", data["icon_libraries"]) + table("Arbitrary Tailwind values", data["arbitrary_values"])
        if dup_primitives:
            md += ["## Duplicate primitives", ""] + [f"- **{k}**: {', '.join('`' + f + '`' for f in v)}" for k, v in dup_primitives.items()] + [""]
        Path(args.md).write_text("\n".join(md))
        print(f"wrote {args.md}")


if __name__ == "__main__":
    main()
