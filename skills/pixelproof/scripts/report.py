#!/usr/bin/env python3
"""Build a self-contained HTML report from a pixelproof JSON result.

Usage: python report.py <report.json> --out <report.html> [--no-images]

JSON shape (fields are optional unless noted):
{
  "title": "Pixelproof audit — Acme",            (required)
  "kind": "audit" | "roast" | "verify" | "responsive",
  "score": 62,                                    overall 0-100 (higher is better)
  "slop_score": 41,                               roast only (lower is better)
  "verdict": "One-line verdict",                  roast
  "summary": "Paragraph",
  "categories": [{"name": "Color", "score": 48, "note": "…"}],
  "findings": [{"severity": "high|medium|low", "category": "Color", "title": "…",
                "evidence": ["file:line …"], "fix": "…", "effort": "S|M|L",
                "screenshot": "relative/or/absolute.png"}],
  "bingo": [{"square": "Default gradient hero", "hit": true, "evidence": "…"}],
  "strengths": ["…"],
  "next": ["/pixelproof extract"],
  "screenshots": [{"label": "Orders @ 390", "path": "shots/orders-390.png"}],
  "meta": {"date": "2026-09-17", "path": "/repo"}
}
Screenshot paths are resolved relative to the JSON file and embedded (downscaled) unless --no-images.
"""
import argparse
import base64
import html
import io
import json
import sys
from datetime import date
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

SEV = {"high": ("High", "#b42318", "#fef3f2"), "medium": ("Medium", "#b54708", "#fffaeb"),
       "low": ("Low", "#475467", "#f2f4f7")}


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def embed(path, base, max_w=1100):
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = (base / p).resolve()
    if not p.exists():
        return None
    if Image is None:
        return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
    im = Image.open(p).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)))
    if im.height > 2400:
        im = im.crop((0, 0, im.width, 2400))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def score_color(s, invert=False):
    if s is None:
        return "#667085"
    v = 100 - s if invert else s
    return "#067647" if v >= 80 else "#b54708" if v >= 60 else "#b42318"


def ring(value, label, invert=False):
    if value is None:
        return ""
    pct = max(0, min(100, value))
    col = score_color(value, invert)
    return (f'<div class="ring" style="--p:{pct};--c:{col}"><div><strong>{pct}</strong>'
            f'<span>{esc(label)}</span></div></div>')


CSS = """
:root{--text:#101828;--text-2:#475467;--text-3:#667085;--border:#eaecf0;--bg:#fff;--subtle:#f9fafb;
--font:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;color-scheme:light}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 var(--font);color:var(--text);background:var(--subtle)}
.wrap{max-width:1040px;margin:0 auto;padding:40px 24px 64px}
header{display:flex;gap:28px;align-items:center;flex-wrap:wrap;margin-bottom:28px}
h1{font-size:26px;line-height:1.2;margin:0 0 6px;letter-spacing:-.02em}
.meta{color:var(--text-3);font-size:13px}.verdict{font-size:18px;margin:10px 0 0;color:var(--text-2)}
.rings{display:flex;gap:16px;margin-left:auto}
.ring{width:104px;height:104px;border-radius:50%;display:grid;place-items:center;
background:conic-gradient(var(--c) calc(var(--p)*1%),var(--border) 0)}
.ring>div{width:84px;height:84px;border-radius:50%;background:var(--bg);display:grid;place-items:center;text-align:center;align-content:center}
.ring strong{font-size:26px;line-height:1}.ring span{font-size:11px;color:var(--text-3);margin-top:2px}
section{background:var(--bg);border:1px solid var(--border);border-radius:12px;padding:20px 22px;margin-top:16px}
h2{font-size:16px;margin:0 0 14px}p{margin:0}
.cats{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.cat{border:1px solid var(--border);border-radius:10px;padding:12px 14px}
.cat-head{display:flex;justify-content:space-between;font-weight:600}.bar{height:6px;border-radius:3px;background:var(--border);margin:8px 0}
.bar i{display:block;height:100%;border-radius:3px}.cat p{font-size:13px;color:var(--text-2)}
.finding{border-top:1px solid var(--border);padding:16px 0;display:grid;gap:8px}.finding:first-of-type{border-top:0;padding-top:0}
.f-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.f-title{font-weight:600;font-size:15px}
.badge{font-size:12px;font-weight:600;padding:2px 8px;border-radius:6px}
.tag{font-size:12px;color:var(--text-3);border:1px solid var(--border);padding:1px 7px;border-radius:6px}
code{font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--subtle);border:1px solid var(--border);border-radius:5px;padding:1px 5px}
ul{margin:0;padding-left:18px}.ev li{color:var(--text-2);font-size:13px}
.fix{font-size:14px}.fix b{color:#067647}
img{max-width:100%;border:1px solid var(--border);border-radius:8px;display:block}.finding img{max-width:min(100%,420px)}
.bingo{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}
.sq{border:1px dashed var(--border);border-radius:10px;padding:10px;font-size:13px;color:var(--text-3);min-height:64px}
.sq.hit{border:1px solid #fda29b;background:#fef3f2;color:#912018}.sq small{display:block;margin-top:4px;color:inherit;opacity:.8}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}.shots figure{margin:0}
figcaption{font-size:12px;color:var(--text-3);margin-top:6px}
@media (max-width:640px){.rings{margin-left:0}.wrap{padding:24px 14px 48px}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-images", action="store_true")
    args = ap.parse_args()
    src = Path(args.json)
    data = json.loads(src.read_text())
    if "title" not in data:
        sys.exit("report JSON needs a 'title'")
    base = src.parent
    kind = data.get("kind", "audit")
    meta = data.get("meta", {})
    parts = [f"<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
             f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
             f"<title>{esc(data['title'])}</title><style>{CSS}</style></head><body><div class=\"wrap\">"]
    rings = ring(data.get("score"), "Pixelproof score")
    if kind == "roast" and data.get("slop_score") is not None:
        rings = ring(data["slop_score"], "Slop score", invert=True) + rings
    parts.append(f"<header><div><h1>{esc(data['title'])}</h1>"
                 f"<div class=\"meta\">{esc(kind.title())} · {esc(meta.get('date', date.today().isoformat()))}"
                 f"{' · ' + esc(meta['path']) if meta.get('path') else ''}</div>"
                 f"{'<p class=verdict>' + esc(data['verdict']) + '</p>' if data.get('verdict') else ''}</div>"
                 f"<div class=\"rings\">{rings}</div></header>")
    if data.get("summary"):
        parts.append(f"<section><h2>Summary</h2><p>{esc(data['summary'])}</p></section>")
    if data.get("categories"):
        cats = []
        for c in data["categories"]:
            s = c.get("score")
            w = 0 if s is None else max(0, min(100, s))
            cats.append(f"<div class=\"cat\"><div class=\"cat-head\"><span>{esc(c.get('name'))}</span>"
                        f"<span style=\"color:{score_color(s)}\">{'—' if s is None else s}</span></div>"
                        f"<div class=\"bar\"><i style=\"width:{w}%;background:{score_color(s)}\"></i></div>"
                        f"<p>{esc(c.get('note', ''))}</p></div>")
        parts.append(f"<section><h2>Scores</h2><div class=\"cats\">{''.join(cats)}</div></section>")
    if data.get("bingo"):
        sq = "".join(f"<div class=\"sq{' hit' if b.get('hit') else ''}\">{'🔥 ' if b.get('hit') else ''}{esc(b.get('square'))}"
                     f"{'<small>' + esc(b['evidence']) + '</small>' if b.get('evidence') else ''}</div>" for b in data["bingo"])
        hits = sum(1 for b in data["bingo"] if b.get("hit"))
        parts.append(f"<section><h2>Slop bingo — {hits}/{len(data['bingo'])}</h2><div class=\"bingo\">{sq}</div></section>")
    if data.get("findings"):
        order = {"high": 0, "medium": 1, "low": 2}
        items = []
        for f in sorted(data["findings"], key=lambda f: order.get(f.get("severity", "low"), 3)):
            label, fg, bg = SEV.get(f.get("severity", "low"), SEV["low"])
            ev = "".join(f"<li><code>{esc(e)}</code></li>" for e in f.get("evidence", []))
            img = "" if args.no_images else embed(f.get("screenshot"), base)
            img_tag = f'<img alt="{esc(f.get("title"))}" src="{img}">' if img else ""
            items.append(
                f"<div class=\"finding\"><div class=\"f-head\"><span class=\"badge\" style=\"color:{fg};background:{bg}\">{label}</span>"
                f"<span class=\"f-title\">{('🔥 ' if kind == 'roast' else '') + esc(f.get('title'))}</span>"
                f"{'<span class=tag>' + esc(f['category']) + '</span>' if f.get('category') else ''}"
                f"{'<span class=tag>effort ' + esc(f['effort']) + '</span>' if f.get('effort') else ''}</div>"
                f"{'<ul class=ev>' + ev + '</ul>' if ev else ''}"
                f"{'<p class=fix><b>Fix:</b> ' + esc(f['fix']) + '</p>' if f.get('fix') else ''}"
                f"{img_tag}</div>")
        title = "Roasts" if kind == "roast" else "Findings"
        parts.append(f"<section><h2>{title} ({len(items)})</h2>{''.join(items)}</section>")
    if data.get("strengths"):
        title = "What actually slaps" if kind == "roast" else "Strengths"
        parts.append(f"<section><h2>{title}</h2><ul>{''.join('<li>' + esc(s) + '</li>' for s in data['strengths'])}</ul></section>")
    if data.get("screenshots") and not args.no_images:
        figs = []
        for s in data["screenshots"]:
            img = embed(s.get("path"), base, 700)
            if img:
                figs.append(f"<figure><img alt=\"{esc(s.get('label'))}\" src=\"{img}\"><figcaption>{esc(s.get('label'))}</figcaption></figure>")
        if figs:
            parts.append(f"<section><h2>Screenshots</h2><div class=\"shots\">{''.join(figs)}</div></section>")
    if data.get("next"):
        parts.append(f"<section><h2>Next steps</h2><ul>{''.join('<li><code>' + esc(n) + '</code></li>' for n in data['next'])}</ul></section>")
    parts.append("<p class=\"meta\" style=\"margin-top:24px\">Generated by pixelproof</p></div></body></html>")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(parts))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
