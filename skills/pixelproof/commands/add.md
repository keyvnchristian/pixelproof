# /pixelproof add — extend the established style

Adds a page, section, menu item, or feature using only the existing tokens and components.

Usage: `/pixelproof add "<what>"`, e.g. `/pixelproof add "settings page with profile and notification forms"` or `/pixelproof add "Reports menu under Insights"`.

## Steps
1. **Check for a spec.** Requires `docs/pixelproof/style-spec.md`. If it's missing, offer `/pixelproof extract` (existing app) or `/pixelproof replicate` (references) first.
2. **Clarify in one round:**
   - where it lives (route, sidebar section)
   - the data and actions it needs
   - its states (empty, loading, error)
   - permissions
   - whether it follows an existing page pattern
3. **Compose.** Build it from the spec components. If something new is truly needed, derive it from existing tokens and patterns: same heights, borders, radii, type, and icon style. Name the pattern it came from. Draw any new icons in the sprite style.
4. **Slice and preview.** Add it to `slices/additions.body.html` (or a new screen in `manifest.json`), then assemble and render at 1440 / 1024 / 390.

   **GATE A:** show the previews and a list of "new element → derived from". Ask Approve / Request changes / Implement directly.
5. **Spec.** Add the new components to the spec with `build_spec.py`, and write their notes.
6. **Implement** following `<SKILL_DIR>/references/implement.md`, then verify following `<SKILL_DIR>/references/verify.md`: add a parity pair for the new page.

   **GATE B:** show app screenshots next to the slice, plus the parity result. Ask Approve / Request changes.
7. **Finish.** Update `state.json`.
