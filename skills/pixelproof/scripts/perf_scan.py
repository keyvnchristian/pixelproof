#!/usr/bin/env python3
"""Measure frontend performance problems, statically and (optionally) in a real browser.

Usage:
  python perf_scan.py <project-path> --out perf.json [--md perf.md]
                      [--url http://localhost:3000 --pages /,/orders] [--throttle] [--storage state.json]

Static checks (no server needed):
  heavy_deps         known heavy packages in package.json (moment, full lodash, chart/editor/map libs)
  wide_imports       `import * as X` / default lodash / whole-icon-library imports
  client_pages       Next.js app/ pages and layouts marked "use client"
  effect_fetching    client components that fetch data inside useEffect
  raw_img            <img> tags (no next/image or width/height)
  big_assets         files over 300 KB in public/ (or static/)
  font_files         self-hosted font files and Google Fonts links
Runtime checks (with --url; Chromium via Playwright):
  lcp_ms, cls, tbt_ms (sum of long-task time over 50 ms), fcp_ms, ttfb_ms, dom_nodes
  requests and transfer bytes by type, the 10 largest resources
  oversized_images   images whose natural size is over 2× their rendered size
  render_blocking    stylesheets and synchronous scripts in <head>
--throttle applies 4× CPU slowdown and a fast-3G-like network so problems show up on fast machines.
"""
import argparse
import json
import re
from pathlib import Path

SKIP = {"node_modules", ".next", "dist", "build", "out", ".git", "coverage", ".turbo", ".svelte-kit", ".nuxt"}
HEAVY = {
    "moment": "Use date-fns or dayjs (moment is ~300 KB and not tree-shakable).",
    "lodash": "Import per-method (lodash/debounce) or use lodash-es; the default import pulls everything.",
    "chart.js": "Load charts lazily (dynamic import) on pages that show them.",
    "echarts": "Load lazily and register only the chart types you use.",
    "highcharts": "Load lazily on chart pages only.",
    "mapbox-gl": "Load the map lazily when it scrolls into view.",
    "leaflet": "Load the map lazily when it scrolls into view.",
    "@fullcalendar/core": "Load the calendar lazily.",
    "draft-js": "Load the editor lazily.",
    "quill": "Load the editor lazily.",
    "@tiptap/react": "Load the editor lazily.",
    "monaco-editor": "Load the editor lazily; it is several MB.",
    "xlsx": "Import only where exporting, via dynamic import.",
    "jspdf": "Import only where exporting, via dynamic import.",
    "framer-motion": "Use LazyMotion + domAnimation to cut the bundle, or CSS for simple transitions.",
    "@mui/icons-material": "Import icons by path (@mui/icons-material/Search) to avoid pulling the whole set.",
    "react-icons": "Fine if imported per pack; avoid mixing many packs.",
}
EXTS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte", ".astro", ".html"}

RUNTIME_JS = r"""
async () => {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  await wait(1500);
  const nav = performance.getEntriesByType('navigation')[0] || {};
  const paint = performance.getEntriesByType('paint');
  const fcp = (paint.find((p) => p.name === 'first-contentful-paint') || {}).startTime || null;
  const lcpEntries = window.__pp_lcp || [];
  const lcp = lcpEntries.length ? lcpEntries[lcpEntries.length - 1] : null;
  const cls = (window.__pp_cls || 0);
  const tbt = (window.__pp_long || []).reduce((s, d) => s + Math.max(0, d - 50), 0);
  const res = performance.getEntriesByType('resource').map((r) => ({
    name: r.name, type: r.initiatorType, bytes: r.transferSize || r.encodedBodySize || 0, ms: Math.round(r.duration) }));
  const imgs = [...document.images].filter((i) => i.naturalWidth && i.getBoundingClientRect().width)
    .map((i) => ({ src: (i.currentSrc || i.src).slice(0, 140), natural: `${i.naturalWidth}x${i.naturalHeight}`,
      shown: `${Math.round(i.getBoundingClientRect().width)}x${Math.round(i.getBoundingClientRect().height)}`,
      ratio: i.naturalWidth / (i.getBoundingClientRect().width * devicePixelRatio), lazy: i.loading === 'lazy' }))
    .filter((x) => x.ratio > 2);
  const blocking = [...document.head.querySelectorAll('link[rel=stylesheet], script[src]:not([async]):not([defer]):not([type=module])')]
    .map((e) => (e.href || e.src || '').slice(0, 140));
  return { ttfb_ms: Math.round(nav.responseStart || 0), fcp_ms: fcp && Math.round(fcp),
    lcp_ms: lcp && Math.round(lcp.time), lcp_element: lcp && lcp.el, cls: Math.round(cls * 1000) / 1000, tbt_ms: Math.round(tbt),
    dom_nodes: document.getElementsByTagName('*').length, resources: res, oversized_images: imgs.slice(0, 15), render_blocking: blocking };
}
"""
INIT_JS = r"""
window.__pp_lcp = []; window.__pp_cls = 0; window.__pp_long = [];
try {
  new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__pp_lcp.push({ time: e.startTime,
    el: e.element ? (e.element.tagName.toLowerCase() + (e.element.className && typeof e.element.className === 'string' ? '.' + e.element.className.trim().split(/\s+/).slice(0, 2).join('.') : '')) : null }); })
    .observe({ type: 'largest-contentful-paint', buffered: true });
  new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__pp_cls += e.value; })
    .observe({ type: 'layout-shift', buffered: true });
  new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__pp_long.push(e.duration); })
    .observe({ type: 'longtask', buffered: true });
} catch (e) {}
"""


def static_scan(root):
    out = {"heavy_deps": [], "wide_imports": [], "client_pages": [], "effect_fetching": [], "raw_img": [], "big_assets": [], "font_files": []}
    pkg = root / "package.json"
    if pkg.exists():
        try:
            deps = {**json.loads(pkg.read_text()).get("dependencies", {})}
            for d, tip in HEAVY.items():
                if d in deps:
                    out["heavy_deps"].append({"package": d, "version": deps[d], "tip": tip})
        except json.JSONDecodeError:
            pass
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        parts = p.relative_to(root).parts
        if any(x in SKIP or x.startswith(".") for x in parts[:-1]):
            continue
        rel = str(p.relative_to(root))
        if parts and parts[0] in ("public", "static") and p.stat().st_size > 300_000:
            out["big_assets"].append({"file": rel, "kb": p.stat().st_size // 1024})
        if p.suffix.lower() in (".woff", ".woff2", ".ttf", ".otf"):
            out["font_files"].append(rel)
        if p.suffix not in EXTS:
            continue
        text = p.read_text(errors="ignore")
        for i, line in enumerate(text.split("\n"), 1):
            if re.search(r"import\s+\*\s+as\s+\w+\s+from\s+['\"](?!\.)", line) or re.search(r"import\s+_\s+from\s+['\"]lodash['\"]", line) \
                    or re.search(r"from\s+['\"]@mui/icons-material['\"]", line):
                out["wide_imports"].append(f"{rel}:{i} {line.strip()[:100]}")
            if re.search(r"<img\b", line) and "next/image" not in text:
                out["raw_img"].append(f"{rel}:{i}")
            if "fonts.googleapis.com" in line:
                out["font_files"].append(f"{rel}:{i} Google Fonts link")
        is_client = text.lstrip().startswith(("'use client'", '"use client"'))
        if is_client and re.search(r"(^|/)app/.*(page|layout)\.(t|j)sx?$", rel):
            out["client_pages"].append(rel)
        if is_client or p.suffix in (".vue", ".svelte"):
            if re.search(r"useEffect\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*?\b(fetch|axios|supabase)\b", text, re.S) or \
               re.search(r"onMounted\s*\([^)]*?\b(fetch|axios|supabase)\b", text, re.S):
                out["effect_fetching"].append(rel)
    out["raw_img"] = out["raw_img"][:40]
    return out


def runtime_scan(url, pages, throttle, storage):
    from playwright.sync_api import sync_playwright
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1366, "height": 900}, **({"storage_state": storage} if storage else {}))
        for path in pages:
            page = ctx.new_page()
            page.add_init_script(INIT_JS)
            if throttle:
                cdp = ctx.new_cdp_session(page)
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                cdp.send("Network.enable")
                cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150,
                         "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
            target = url.rstrip("/") + ("/" + path.lstrip("/") if path != "/" else "/")
            page.goto(target, wait_until="load", timeout=90_000)
            page.mouse.wheel(0, 1500)
            data = page.evaluate(RUNTIME_JS)
            by_type = {}
            for r in data["resources"]:
                t = by_type.setdefault(r["type"], {"requests": 0, "kb": 0})
                t["requests"] += 1
                t["kb"] += r["bytes"] // 1024
            largest = sorted(data["resources"], key=lambda r: -r["bytes"])[:10]
            data.update({"page": path, "url": target, "requests": len(data["resources"]), "by_type": by_type,
                         "total_kb": sum(r["bytes"] for r in data["resources"]) // 1024,
                         "largest": [{"name": r["name"][:140], "kb": r["bytes"] // 1024, "type": r["type"]} for r in largest]})
            del data["resources"]
            results.append(data)
            page.close()
        browser.close()
    return results


def rate(v, good, poor):
    if v is None:
        return "n/a"
    return "good" if v <= good else "needs work" if v <= poor else "poor"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--url")
    ap.add_argument("--pages", default="/")
    ap.add_argument("--throttle", action="store_true")
    ap.add_argument("--storage")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    data = {"root": str(root), "static": static_scan(root), "runtime": []}
    if args.url:
        data["runtime"] = runtime_scan(args.url, [p.strip() for p in args.pages.split(",") if p.strip()], args.throttle, args.storage)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    s = data["static"]
    print("static: " + ", ".join(f"{k} {len(v)}" for k, v in s.items()))
    for r in data["runtime"]:
        print(f"{r['page']}: LCP {r['lcp_ms']} ms ({rate(r['lcp_ms'], 2500, 4000)}), CLS {r['cls']} ({rate(r['cls'], 0.1, 0.25)}), "
              f"TBT {r['tbt_ms']} ms ({rate(r['tbt_ms'], 200, 600)}), {r['requests']} requests, {r['total_kb']} KB, "
              f"{len(r['oversized_images'])} oversized images, {len(r['render_blocking'])} render-blocking")
    print(f"wrote {out}")
    if args.md:
        md = [f"# Performance scan — {root.name}", ""]
        if data["runtime"]:
            md += ["| Page | LCP | CLS | TBT | FCP | Requests | Transfer |", "|---|---|---|---|---|---|---|"]
            for r in data["runtime"]:
                md.append(f"| `{r['page']}` | {r['lcp_ms']} ms ({rate(r['lcp_ms'], 2500, 4000)}) | {r['cls']} ({rate(r['cls'], 0.1, 0.25)}) | "
                          f"{r['tbt_ms']} ms ({rate(r['tbt_ms'], 200, 600)}) | {r['fcp_ms']} ms | {r['requests']} | {r['total_kb']} KB |")
            md.append("")
        for k, v in s.items():
            if v:
                md += [f"## {k.replace('_', ' ')} ({len(v)})", ""] + [f"- {json.dumps(x) if isinstance(x, dict) else x}" for x in v[:25]] + [""]
        Path(args.md).write_text("\n".join(md))
        print(f"wrote {args.md}")


if __name__ == "__main__":
    main()
