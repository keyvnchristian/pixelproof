# Implement (Step 6)

## Order inside the first batch
1. **Theme:** primitives, semantic tokens, breakpoints constant, JS token helpers, and the Tailwind mapping (if used).
2. **Base styles:** reset, body defaults, `.icon`, focus ring, reduced motion, font loading (`next/font` or `<link>`).
3. **Icons:** an `IconSprite` component rendered once in the root layout (the sprite as-is) and an `Icon` component that renders `<svg class="icon …"><use href="#i-{name}"/></svg>`.
4. **Component CSS:** port `shared.css` group by group into component stylesheets.
   - Keep the **same selectors and rule order**, and replace literals with tokens.
   - Declare layer-3 tokens at the top of each block.
   - Computed values must stay identical to the slice.
5. **Components:** one per spec component, outputting the spec markup. Variants are props, never page-specific classes.
6. **Shell:** sidebar, topbar, and page container.
7. **Screens:** the batch's screens.
8. **Cleanup:** delete the replaced legacy styles and components. No duplicate implementations.

Later batches repeat steps 6–8, adding new components only when a screen needs them.

## Restyle rules (existing app)
- **Keep:** data fetching, routes, permissions, feature flags, text and language, column order, filters, actions, keyboard shortcuts, and analytics events.
- **Mapping:** use `plan.md`. If an element doesn't map cleanly, ask the user; don't invent a style.
- **Status pills, stat strips, and similar elements:** convert them the way the spec's pattern table says (e.g. status becomes two-line text, per-status counts move onto status tabs).
- **Content:** don't add columns, widgets, or sections, and don't remove any. Additions happen only if the user approved them at GATE C.
- **Reference content:** don't copy the references' demo content.

## Framework notes
- **React/Next.js:** components render the same class names via `className`. Keep server/client component boundaries as they are. Charts and maps read colors with `readToken()` at runtime.
- **Tailwind:** fine for page layout (`grid`, `gap-[var(--space-24)]`), but component visuals come from the spec classes. Never recreate a spec component with utilities.
- **Vue/Svelte/others:** the same rules. The CSS is global or imported once, and components output spec markup.
- **Component libraries (shadcn, MUI, …):** keep behavior primitives (dialogs, popovers, menus) if the app uses them, but style their visible parts with spec classes and tokens. Remove conflicting default styles.

## Charts and maps
- **Charts:** use the colors, grid style, axes, height, and tooltip style defined in the spec's chart section. Configure the library to match; don't restyle the reference to fit the library's defaults.
- **Maps:** use the map box container from the spec. Base map, route, marker, and popup styling come from the spec; colors are read via `readToken()`.

## GATE E (after every batch)
Run Step 7, then present:
- app screenshots at 1440 / 1024 / 390 next to the slice previews, for each screen in the batch
- the parity report summary (checked / failed / fixed)
- the token check result
- the files changed and the legacy code removed
- open questions

Ask: **Approve & continue** / **Request changes** / **Implement the remaining batches directly** (still verify each batch, and report at the end).
