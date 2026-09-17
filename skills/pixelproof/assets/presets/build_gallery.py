#!/usr/bin/env python3
"""Build gallery/build/index.html: one self-contained page with a page switcher and a preset switcher.

Usage: python build_gallery.py   (run from anywhere; paths are relative to this file)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAL = HERE / "gallery"
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from assemble import expand  # noqa: E402

m = json.loads((GAL / "manifest.json").read_text())
css = "\n\n".join((GAL / c).read_text() for c in m["css"])
sprite = (GAL / m["sprite"]).read_text().strip()
pages = []
for s in m["screens"]:
    body = expand((GAL / s["body"]).read_text(), GAL)
    body = re.sub(r"<!--\s*@(component:[^>]*|end)\s*-->\n?", "", body)
    pages.append((s["name"], s["title"], body))

tabs = "".join(f'<button type="button" data-page="{n}">{t}</button>' for n, t, _ in pages)
sections = "".join(f'<section class="gx-page" data-name="{n}" hidden>{b}</section>' for n, _, b in pages)
presets = "".join(f'<button type="button" data-preset-btn="{p}">{p.title()}</button>' for p in m["presets"])
html = f"""<!DOCTYPE html>
<html lang="en" data-preset="{m['presets'][0]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Pixelproof presets</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="{m['font_href']}" rel="stylesheet" />
<style>
{css}
/* gallery chrome (not part of the presets) */
.gx-bar {{ position: fixed; left: 0; right: 0; bottom: 14px; width: fit-content; margin: 0 auto; z-index: 50; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;
  max-width: calc(100vw - 20px); padding: 8px; border-radius: 16px; background: rgba(20, 19, 28, 0.88); color: #fff; font: 13px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  box-shadow: 0 16px 40px -12px rgba(0, 0, 0, 0.5); backdrop-filter: blur(8px); }}
.gx-group {{ display: flex; gap: 2px; padding: 2px; border-radius: 11px; background: rgba(255, 255, 255, 0.08); overflow-x: auto; }}
.gx-group button {{ height: 34px; padding: 0 11px; border-radius: 9px; color: rgba(255, 255, 255, 0.78); white-space: nowrap; }}
.gx-group button[aria-pressed="true"] {{ background: #fff; color: #14131c; }}
body {{ padding-bottom: 70px; }}
</style>
</head>
<body>
{sprite}
{sections}
<nav class="gx-bar" aria-label="Gallery controls">
  <div class="gx-group" role="group" aria-label="Page">{tabs}</div>
  <div class="gx-group" role="group" aria-label="Preset">{presets}</div>
</nav>
<script>
(() => {{
  const pages = [...document.querySelectorAll('.gx-page')];
  const state = {{ page: '{pages[0][0]}', preset: document.documentElement.dataset.preset }};
  const fromHash = () => {{
    const [p, s] = location.hash.slice(1).split('/');
    if (p && pages.some((x) => x.dataset.name === p)) state.page = p;
    if (s && document.querySelector(`[data-preset-btn="${{s}}"]`)) state.preset = s;
  }};
  const render = () => {{
    document.documentElement.dataset.preset = state.preset;
    pages.forEach((x) => (x.hidden = x.dataset.name !== state.page));
    document.querySelectorAll('[data-page]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.page === state.page)));
    document.querySelectorAll('[data-preset-btn]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.presetBtn === state.preset)));
    history.replaceState(null, '', `#${{state.page}}/${{state.preset}}`);
  }};
  document.addEventListener('click', (e) => {{
    const b = e.target.closest('[data-page],[data-preset-btn]');
    if (!b) return;
    if (b.dataset.page) {{ state.page = b.dataset.page; window.scrollTo(0, 0); }}
    if (b.dataset.presetBtn) state.preset = b.dataset.presetBtn;
    render();
  }});
  window.addEventListener('hashchange', () => {{ fromHash(); render(); }});
  fromHash(); render();
}})();
</script>
</body>
</html>
"""
out = GAL / "build" / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html)
print(f"wrote {out} ({len(html) // 1024} KB)")
