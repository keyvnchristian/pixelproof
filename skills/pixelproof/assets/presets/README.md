# Pixelproof presets

Original visual systems used by `/pixelproof enhance looks`. They're for projects that have no design reference.

| Preset | For | Feel |
|---|---|---|
| `lumen` | Dashboards, settings, forms, files, auth | Light floating panels, violet actions, dense data |
| `linen` | Warm product UI or editorial marketing | Warm neutrals, big rounding, black pills, big numerals |
| `nocturne` | Landing pages, dark product UI | Indigo glow, glassy surfaces, violet actions |

## Files
| File | What |
|---|---|
| `components.css` | Every component; values come only from tokens |
| `lumen.css`, `linen.css`, `nocturne.css` | Token sets on `[data-preset="…"]` |
| `SPEC.md` | Generated design spec: tokens, CSS, icons, component markup, patterns, verification values |
| `gallery/*.body.html` | Reference pages: dashboard, settings, form, auth, auth states, upload, landing |
| `gallery/build/<page>--<preset>.html` | Rendered references, the source of truth for parity checks |
| `gallery/build/index.html` | Every page with page and preset switchers |
| `build_gallery.py` | Rebuilds `index.html` |

## Rebuild after editing
```bash
python3 ../../scripts/assemble.py gallery
python3 build_gallery.py
python3 ../../scripts/build_spec.py gallery --template ../templates/preset-spec.template.md --out SPEC.md
python3 ../../scripts/render.py gallery/build/*--*.html --widths 1440,1024,390 --deep --strict --out /tmp/preset-check
```
The last command must report no failures: contrast AA, no text under 12px, 44px tap targets on mobile, no overflow.

## Adding a preset
1. **Tokens:** copy `lumen.css` to `<name>.css` and change only token values. Every token name must stay.
2. **Register it:** add the file to `gallery/manifest.json` → `css` and `presets`, then rebuild.
3. **Check it:** run the deep check. Fix contrast by adjusting `--ink-3`, `--accent`, or `--btn-solid`, never by adding component rules.

## Origin
The presets are original designs. They draw on general patterns common in modern product UI (floating panels, soft status chips, bento sections, split auth screens), not on copies of any specific product. All names, brands, and copy in the gallery are invented.
