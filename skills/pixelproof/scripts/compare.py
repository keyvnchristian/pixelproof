#!/usr/bin/env python3
"""Compare a reference image with a rendered slice.

Usage:
  python compare.py <reference.png> <render.png> --out <compare.png>
                    [--ref-box x0,y0,x1,y1] [--render-box x0,y0,x1,y1] [--min-len 200] [--json]

The reference crop (usually the app area inside a browser mockup) is scaled to the render's width.
Outputs:
  - compare.png: reference | render | difference heatmap, side by side
  - compare-overlay.png: 50% blend (misalignments show as double edges)
  - a divider report: horizontal lines found in both images (in render px) and their offsets,
    which catches row-height and padding drift quickly
  - a rough similarity score (content differences like placeholder photos lower it; use it to
    track progress between passes, not as an absolute target)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from measure import find_lines  # noqa: E402


def crop(img, box):
    if not box:
        return img
    x0, y0, x1, y1 = [int(float(v)) for v in box.split(",")]
    return img.crop((x0, y0, x1, y1))


def divider_ys(arr, min_len):
    return [l["y"] for l in find_lines(arr.astype(np.int16), min_len, 10, 8)]


def align_dividers(ra, rb, tol):
    """Match reference dividers to render dividers in order, tracking drift.

    The starting offset is the most common shift between the two lists; after each match the
    expected offset follows the last matched pair, so gradual drift (rows a few px too short)
    stays matched and shows up as a growing offset instead of wrong pairs.
    """
    shifts = [yb - ya for ya in ra for yb in rb if abs(yb - ya) <= 80]
    if shifts:
        bins = {}
        for d in shifts:
            bins[d // 2] = bins.get(d // 2, 0) + 1
        off = max(bins, key=bins.get) * 2
    else:
        off = 0
    pairs, used, j0 = [], set(), 0
    for ya in ra:
        expected = ya + off
        best = None
        for j in range(j0, len(rb)):
            yb = rb[j]
            if yb in used:
                continue
            d = abs(yb - expected)
            if d <= tol and (best is None or d < best[0]):
                best = (d, j, yb)
            if yb > expected + tol:
                break
        if best:
            _, j, yb = best
            used.add(yb)
            j0 = j + 1
            off = yb - ya
            pairs.append({"reference_y": ya, "render_y": yb, "offset": yb - ya})
        else:
            pairs.append({"reference_y": ya, "render_y": None, "offset": None})
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("render")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref-box")
    ap.add_argument("--render-box")
    ap.add_argument("--min-len", type=int, default=200, help="min divider length in render px")
    ap.add_argument("--tol", type=int, default=10, help="max px between expected and found divider")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ref = crop(Image.open(args.reference).convert("RGB"), args.ref_box)
    ren = crop(Image.open(args.render).convert("RGB"), args.render_box)
    scale = ref.width / ren.width
    ref_s = ref.resize((ren.width, max(1, round(ref.height / scale))), Image.LANCZOS)
    h = min(ref_s.height, ren.height)
    a = np.asarray(ref_s.crop((0, 0, ren.width, h))).astype(np.int16)
    b = np.asarray(ren.crop((0, 0, ren.width, h))).astype(np.int16)

    diff = np.abs(a - b).max(axis=2)
    score = float(1 - (diff > 40).mean())
    # faint grayscale render as context, differences painted red
    gray = (b.mean(axis=2) * 0.25 + 190).astype(np.int16)
    strength = np.clip(diff * 4, 0, 255)
    heat = np.stack([np.clip(gray + strength, 0, 255),
                     np.clip(gray - strength, 0, 255),
                     np.clip(gray - strength, 0, 255)], axis=2).astype(np.uint8)

    gap = 16
    W = ren.width * 3 + gap * 2
    canvas = Image.new("RGB", (W, h + 28), "white")
    draw = ImageDraw.Draw(canvas)
    for i, (im, label) in enumerate([(Image.fromarray(a.astype(np.uint8)), "reference (scaled)"),
                                     (Image.fromarray(b.astype(np.uint8)), "render"),
                                     (Image.fromarray(heat), "difference")]):
        x = i * (ren.width + gap)
        canvas.paste(im, (x, 28))
        draw.text((x + 4, 8), label, fill=(20, 20, 20))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    overlay = Image.blend(Image.fromarray(a.astype(np.uint8)), Image.fromarray(b.astype(np.uint8)), 0.5)
    overlay_path = out.with_name(out.stem + "-overlay.png")
    overlay.save(overlay_path)

    ra, rb = divider_ys(a, args.min_len), divider_ys(b, args.min_len)
    pairs = align_dividers(ra, rb, args.tol)
    used = {p_["render_y"] for p_ in pairs if p_["render_y"] is not None}
    extra = [yb for yb in rb if yb not in used]

    data = {"reference_scale_to_render": round(scale, 4), "compared_height": h, "similarity": round(score, 4),
            "compare_image": str(out), "overlay_image": str(overlay_path), "dividers": pairs,
            "render_only_dividers": extra}
    if args.json:
        print(json.dumps(data, indent=2))
        return
    print(f"reference scaled by 1/{scale:.3f}; compared {ren.width}x{h}px; similarity {score:.3f}")
    print(f"images: {out}  {overlay_path}")
    print("dividers (render px): reference → render  offset   [growing offsets = a row/padding is off]")
    prev = None
    for p_ in pairs:
        if p_["render_y"] is None:
            print(f"  {p_['reference_y']:>5} → (missing in render)")
            continue
        step = "" if prev is None else f"   Δoffset {p_['offset'] - prev:+d}"
        print(f"  {p_['reference_y']:>5} → {p_['render_y']:<5} {p_['offset']:+d}{step}")
        prev = p_["offset"]
    if extra:
        print(f"  render-only dividers at {extra} (a border the reference doesn't have?)")


if __name__ == "__main__":
    main()
