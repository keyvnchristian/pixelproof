# /pixelproof theme — global rebrand through tokens

Changes brand color, font, radius, or density across the app by editing tokens only.

Usage: `/pixelproof theme "<change>"`, e.g. `/pixelproof theme "primary #992c29"`, `/pixelproof theme "font Manrope"`, `/pixelproof theme "radius softer"`, `/pixelproof theme "compact density"`.

## Steps
1. **Locate the tokens.** Requires tokens: a pixelproof theme, or an existing CSS-variable or Tailwind theme. If colors are hard-coded, say so, and offer `/pixelproof audit` → fix batch "collapse colors into tokens" first.
2. **Derive the full set from the request.**
   - **Color:** from the primary, derive hover (about 8–10% darker), a soft tint for backgrounds and charts, and the focus ring. Check text-on-primary contrast (at least 4.5:1). If it fails, propose the nearest passing shade and explain why.
   - **Font:** pick the family and weights, the loading method, and the fallback stack. Check that sizes still fit: long labels, table columns, buttons.
   - **Radius and density:** scale the existing steps proportionally. Keep hairlines at 1px, and keep tap targets at 44px or more.
3. **Preview.** Render the slices (or key app pages) before and after, at 1440 and 390, with a side-by-side comparison.

   **GATE A:** show the token diff table (old → new), the contrast results, and the before/after images. Ask Approve / Request changes / Apply directly.
4. **Apply.** Edit the layer-1/layer-2 token files only, plus the font loading if needed. No component edits, unless a component bypassed tokens; list those as findings and ask.
5. **Verify.** Run `check_tokens.mjs`, then `render.py --deep` on the key pages, then parity against re-rendered slices (the slices use the same tokens, so re-assemble them first).

   **GATE B:** show the results. Ask Approve / Request changes. Then update `state.json` (`brand`).
