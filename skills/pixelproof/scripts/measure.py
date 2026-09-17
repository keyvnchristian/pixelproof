#!/usr/bin/env python3
"""Measure UI reference images (screenshots, Dribbble shots, exports).

Subcommands
  scale    <img> [--frame x0,y0,x1,y1]                 candidate CSS scales
  palette  <img> [--box ...] [--top N] [--merge D]     dominant colors in a region
  sample   <img> x,y [x,y ...]                          exact pixel colors
  lines    <img> [--box ...] [--min-len N] [--scale S]  long horizontal/vertical lines (borders, dividers)
  boxes    <img> [--box ...] [--scale S] [--bg auto|#hex] [--tol N] [--min-gap N]
                                                        content bands (rows) and blocks (columns)

All coordinates are image pixels. With --scale, sizes are also printed in CSS px (image px / scale).
Add --json to any subcommand for machine-readable output.
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image

COMMON_WIDTHS = [1280, 1366, 1440, 1536, 1600, 1920]


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.int16)


def parse_box(img, box):
    h, w = img.shape[:2]
    if not box:
        return 0, 0, w, h
    x0, y0, x1, y1 = [int(float(v)) for v in box.split(",")]
    x0, x1 = max(0, min(x0, x1)), min(w, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(h, max(y0, y1))
    if x1 - x0 < 1 or y1 - y0 < 1:
        sys.exit(f"empty box {box} for image {w}x{h}")
    return x0, y0, x1, y1


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(int(v) for v in rgb)


def parse_hex(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.int16)


def out(args, data, text):
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(text)


# ---------------------------------------------------------------- scale
def cmd_scale(args):
    img = load(args.image)
    h, w = img.shape[:2]
    x0, y0, x1, y1 = parse_box(img, args.frame)
    fw = x1 - x0
    rows = []
    for cw in COMMON_WIDTHS:
        rows.append({"basis": f"viewport {cw}px", "scale": round(fw / cw, 4), "css_frame_width": cw})
    for s in (1, 2, 3):
        rows.append({"basis": f"{s}x export", "scale": s, "css_frame_width": round(fw / s, 1)})
    lines = [f"image {w}x{h}, frame {fw}x{y1 - y0} (x{x0}..{x1}, y{y0}..{y1})",
             "Candidates (verify by measuring text cap height and control heights with `boxes --scale`):"]
    for r in rows:
        lines.append(f"  scale {r['scale']:<7} ← {r['basis']:<16} (frame = {r['css_frame_width']} css px)")
    lines.append("Tip: cap height ≈ 0.71 × font-size; 1px borders should measure ≈ 1×scale image px.")
    out(args, {"image": [w, h], "frame": [x0, y0, x1, y1], "candidates": rows}, "\n".join(lines))


# ---------------------------------------------------------------- palette
def quantize_counts(px, merge):
    """Group colors whose channels differ by <= merge; return [(rgb, count)] sorted."""
    q = (px // max(1, merge)).astype(np.int32)
    keys = q[:, 0] * 65536 + q[:, 1] * 256 + q[:, 2]
    uniq, inv, counts = np.unique(keys, return_inverse=True, return_counts=True)
    order = np.argsort(-counts)
    res = []
    for idx in order:
        members = px[inv == idx]
        # representative = most common exact color within the bucket
        mk = members[:, 0].astype(np.int64) * 65536 + members[:, 1] * 256 + members[:, 2]
        u, c = np.unique(mk, return_counts=True)
        top = u[np.argmax(c)]
        rep = np.array([top // 65536, (top // 256) % 256, top % 256])
        res.append((rep, int(counts[idx])))
    return res


def cmd_palette(args):
    img = load(args.image)
    x0, y0, x1, y1 = parse_box(img, args.box)
    px = img[y0:y1, x0:x1].reshape(-1, 3)
    total = len(px)
    res = quantize_counts(px, args.merge)[: args.top]
    data = [{"hex": hexc(c), "count": n, "share": round(n / total, 4)} for c, n in res]
    text = "\n".join(f"{d['hex']}  {d['share'] * 100:5.1f}%  ({d['count']} px)" for d in data)
    out(args, {"box": [x0, y0, x1, y1], "colors": data}, text)


# ---------------------------------------------------------------- sample
def cmd_sample(args):
    img = load(args.image)
    h, w = img.shape[:2]
    data = []
    for p in args.points:
        x, y = [int(float(v)) for v in p.split(",")]
        if not (0 <= x < w and 0 <= y < h):
            data.append({"x": x, "y": y, "hex": None})
            continue
        data.append({"x": x, "y": y, "hex": hexc(img[y, x])})
    out(args, data, "\n".join(f"({d['x']},{d['y']}) {d['hex']}" for d in data))


# ---------------------------------------------------------------- lines
def runs(mask):
    """Return (start, end) of True runs in a 1-D bool array (end exclusive)."""
    m = np.concatenate([[False], mask, [False]])
    d = np.diff(m.astype(np.int8))
    starts = np.where(d == 1)[0]
    ends = np.where(d == -1)[0]
    return list(zip(starts, ends))


def find_lines(region, min_len, tol, contrast, k=3):
    """Horizontal lines (borders/dividers).

    A row belongs to a line where it differs from the surrounding background, taken from the
    rows k above and k below (which must agree with each other). Adjacent rows with overlapping
    spans are merged, so anti-aliased 1px borders spread over 2-3 image rows count once.
    """
    h, w = region.shape[:2]
    rows = []
    for y in range(h):
        a = region[max(0, y - k)]
        b = region[min(h - 1, y + k)]
        stable = np.abs(a - b).max(axis=1) <= tol
        ref = (a + b) // 2
        dev = np.abs(region[y] - ref).max(axis=1)
        mask = stable & (dev > contrast)
        for s, e in runs(mask):
            if e - s >= min_len:
                seg = region[y, s:e]
                strength = float(dev[s:e].mean())
                color = np.median(seg, axis=0)
                rows.append((y, int(s), int(e), strength, color))
    merged = []
    for y, s, e, strength, color in rows:
        last = merged[-1] if merged else None
        if last and y - last["end_y"] <= 1 and s < last["x1"] and e > last["x0"]:
            last["end_y"] = y
            last["x0"], last["x1"] = min(last["x0"], s), max(last["x1"], e)
            last["rows"].append((strength, color))
        else:
            merged.append({"y": y, "end_y": y, "x0": s, "x1": e, "rows": [(strength, color)]})
    result = []
    for m in merged:
        strengths = [r[0] for r in m["rows"]]
        peak = max(strengths)
        core = [r for r in m["rows"] if r[0] >= peak * 0.5]
        best = max(m["rows"], key=lambda r: r[0])
        result.append({"y": m["y"], "x0": m["x0"], "x1": m["x1"],
                       "thickness": len(core), "rows": len(m["rows"]), "color": hexc(best[1])})
    return result


def cmd_lines(args):
    img = load(args.image)
    x0, y0, x1, y1 = parse_box(img, args.box)
    region = img[y0:y1, x0:x1]
    horiz = find_lines(region, args.min_len, args.tol, args.contrast)
    vert = find_lines(region.transpose(1, 0, 2), args.min_len, args.tol, args.contrast)
    data = {"box": [x0, y0, x1, y1], "horizontal": [], "vertical": []}
    lines = []
    for h in horiz:
        item = {"y": y0 + h["y"], "x0": x0 + h["x0"], "x1": x0 + h["x1"], "thickness": h["thickness"], "color": h["color"]}
        if args.scale:
            item["thickness_css"] = round(h["thickness"] / args.scale, 2)
        data["horizontal"].append(item)
    for v in vert:
        item = {"x": x0 + v["y"], "y0": y0 + v["x0"], "y1": y0 + v["x1"], "thickness": v["thickness"], "color": v["color"]}
        if args.scale:
            item["thickness_css"] = round(v["thickness"] / args.scale, 2)
        data["vertical"].append(item)
    lines.append(f"Horizontal lines ({len(data['horizontal'])}):")
    prev = None
    for it in data["horizontal"]:
        gap = ""
        if prev is not None:
            g = it["y"] - prev
            gap = f"  Δy {g}px" + (f" = {g / args.scale:.1f} css" if args.scale else "")
        lines.append(f"  y={it['y']:<5} x {it['x0']}–{it['x1']}  t={it['thickness']}  {it['color']}{gap}")
        prev = it["y"]
    lines.append(f"Vertical lines ({len(data['vertical'])}):")
    prev = None
    for it in data["vertical"]:
        gap = ""
        if prev is not None:
            g = it["x"] - prev
            gap = f"  Δx {g}px" + (f" = {g / args.scale:.1f} css" if args.scale else "")
        lines.append(f"  x={it['x']:<5} y {it['y0']}–{it['y1']}  t={it['thickness']}  {it['color']}{gap}")
        prev = it["x"]
    out(args, data, "\n".join(lines))


# ---------------------------------------------------------------- boxes
def segments(profile, min_gap):
    """Split a boolean profile into segments separated by gaps >= min_gap."""
    segs = []
    for s, e in runs(profile):
        if segs and s - segs[-1][1] < min_gap:
            segs[-1] = (segs[-1][0], e)
        else:
            segs.append((s, e))
    return segs


def cmd_boxes(args):
    img = load(args.image)
    x0, y0, x1, y1 = parse_box(img, args.box)
    region = img[y0:y1, x0:x1]
    if args.bg == "auto":
        border = np.concatenate([region[0], region[-1], region[:, 0], region[:, -1]])
        bg = quantize_counts(border, 2)[0][0].astype(np.int16)
    else:
        bg = parse_hex(args.bg)
    mask = np.abs(region - bg).max(axis=2) > args.tol
    s = args.scale
    fmt = (lambda v: f"{v}px" + (f" ({v / s:.1f})" if s else ""))
    data = {"box": [x0, y0, x1, y1], "background": hexc(bg), "scale": s, "bands": []}
    lines = [f"background {hexc(bg)}; values: image px" + (" (css px)" if s else "")]
    bands = segments(mask.any(axis=1), args.min_gap)
    prev_end = None
    for bi, (by0, by1) in enumerate(bands):
        band = mask[by0:by1]
        blocks = segments(band.any(axis=0), args.min_gap)
        bdata = {"y0": y0 + by0, "y1": y0 + by1, "height": by1 - by0,
                 "gap_above": (by0 - prev_end) if prev_end is not None else by0, "blocks": []}
        lines.append(f"band {bi}: y {y0 + by0}–{y0 + by1}  h {fmt(by1 - by0)}  gap above {fmt(bdata['gap_above'])}")
        prev_x = None
        for (bx0, bx1) in blocks:
            sub = band[:, bx0:bx1]
            rows = np.where(sub.any(axis=1))[0]
            ty0, ty1 = by0 + rows[0], by0 + rows[-1] + 1
            blk = {"x0": x0 + bx0, "x1": x0 + bx1, "width": bx1 - bx0, "y0": y0 + ty0, "y1": y0 + ty1,
                   "height": ty1 - ty0, "gap_left": (bx0 - prev_x) if prev_x is not None else bx0}
            bdata["blocks"].append(blk)
            lines.append(f"   block x {blk['x0']}–{blk['x1']}  w {fmt(blk['width'])}  h {fmt(blk['height'])}"
                         f"  gap left {fmt(blk['gap_left'])}")
            prev_x = bx1
        data["bands"].append(bdata)
        prev_end = by1
    if s:
        for b in data["bands"]:
            b["height_css"] = round(b["height"] / s, 2)
            b["gap_above_css"] = round(b["gap_above"] / s, 2)
            for k in b["blocks"]:
                k["width_css"] = round(k["width"] / s, 2)
                k["height_css"] = round(k["height"] / s, 2)
                k["gap_left_css"] = round(k["gap_left"] / s, 2)
    out(args, data, "\n".join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("scale"); a.add_argument("image"); a.add_argument("--frame")
    a.set_defaults(fn=cmd_scale)

    a = sub.add_parser("palette"); a.add_argument("image"); a.add_argument("--box")
    a.add_argument("--top", type=int, default=6); a.add_argument("--merge", type=int, default=4)
    a.set_defaults(fn=cmd_palette)

    a = sub.add_parser("sample"); a.add_argument("image"); a.add_argument("points", nargs="+")
    a.set_defaults(fn=cmd_sample)

    a = sub.add_parser("lines"); a.add_argument("image"); a.add_argument("--box")
    a.add_argument("--min-len", type=int, default=120); a.add_argument("--tol", type=int, default=10)
    a.add_argument("--contrast", type=int, default=8); a.add_argument("--scale", type=float)
    a.set_defaults(fn=cmd_lines)

    a = sub.add_parser("boxes"); a.add_argument("image"); a.add_argument("--box")
    a.add_argument("--scale", type=float); a.add_argument("--bg", default="auto")
    a.add_argument("--tol", type=int, default=18); a.add_argument("--min-gap", type=int, default=8)
    a.set_defaults(fn=cmd_boxes)

    for sp in sub.choices.values():
        sp.add_argument("--json", action="store_true")
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
