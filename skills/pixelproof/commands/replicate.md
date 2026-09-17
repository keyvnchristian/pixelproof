# /pixelproof replicate — build exactly from references

Default command. Aliases: `build`, `clone`, or no command with images/design docs attached.
Arguments after the command are reference paths or a short brief, e.g.
`/pixelproof replicate refs/orders.png refs/dashboard.png "primary #992c29"`.

**Core idea:** never implement straight from an image. Images are fuzzy, so models guess spacing, borders, and icons, and the result drifts into generic "slop". This skill first converts each reference into a **measured, rendered HTML+CSS slice**. That code has exact numbers and is the source of truth. The codebase is then built from the slice, and the result is verified against it.

```
references ──► 1. intake ──► 2. measure ──► 3. slice (HTML+CSS) ──► 4. additions
                  │ GATE A                        │ GATE B                  │ GATE C
                  ▼                               ▼                         ▼
             5. spec + tokens + plan ──► 6. implement in batches ──► 7. verify
                  │ GATE D                        │ GATE E (per batch)
```

Every **GATE** is a stop: show a preview, then ask the user to **Approve**, **Request changes**, or **Implement directly** (skip the remaining preview gates; verification still runs). Never pass a gate without the user's answer. After every gate, record the decision in `docs/pixelproof/state.json` (see the router's State section).

---

## Step 1 — Intake → GATE A

Read `<SKILL_DIR>/references/intake.md` and ask its questions in **one round**:
- which references (and which parts of them) to use
- new build or restyle of an existing codebase
- brand color and logo overrides
- target stack
- the screens in scope
- **any features, menu items, or sections to add in this style that the references don't show**
- whether the references' demo content should be replaced with the project's own content

Copy the references into `docs/pixelproof/refs/`. If the user gave a `design.md` or tokens file, treat its explicit values as measurements (they win over pixel estimates) and still slice it, so there is rendered proof.

**GATE A:** summarize the intake (references, scope, overrides, additions, stack) in a short list and ask Approve / Change. Don't start measuring until it's confirmed.

## Step 2 — Measure

Read `<SKILL_DIR>/references/measure.md`. For each reference:
1. **Scale:** find the scale with `measure.py scale`. Screenshots are often 2× or scaled mockups inside a browser frame.
2. **Measure:** get colors (`palette`, `sample`), borders (`lines`), and spacing (`boxes`), and convert everything to CSS px.
3. **Snap:** round to clean values (whole px; 2px grid for spacing unless the image clearly shows odd values). Keep one value per role; don't create near-duplicates like 15px and 16px for the same role.
4. **Type and icons:** identify the typeface and the icon style (stroke width, size, corner style).
5. **Log:** write every value to `measurements.md` (element, image px, scale, CSS value, confidence).

Measure; don't eyeball. If something can't be measured (blurry, cropped), say so in the log and pick the value that is consistent with the rest of the system.

## Step 3 — Slice → GATE B

Read `<SKILL_DIR>/references/slice.md`. Build one slice per reference screen:
- **Shared files:** one `shared.css` and one `sprite.svg`. Start from `<SKILL_DIR>/assets/templates/shared.starter.css` and `<SKILL_DIR>/assets/icons/starter-sprite.svg`.
- **Markup:** body markup per screen, with shared partials (sidebar, topbar). Wrap each reusable component in `<!-- @component: name -->` … `<!-- @end -->` so the spec can extract it.
- **Content:** apply the intake overrides (brand color, logo, the project's own content). Replace third-party brand names, logos, photos, and illustrations with neutral placeholders or the user's own.
- **Build and check:** assemble with `assemble.py`, then render with `render.py` (1440 / 1024 / 390).
- **Compare and fix:** compare with `compare.py` against the reference and fix differences. Do **at least two** measure → fix passes before showing anything.
- **Responsive:** references are usually desktop-only. Derive responsive rules conservatively and label them "derived" in the spec.

**GATE B:** show the user, per screen:
- the PNG preview paths (and the self-contained HTML path to open in a browser)
- the side-by-side comparison image
- a short list of deliberate differences (placeholders, brand swaps, derived responsive behavior)

Ask: **Approve** / **Request changes** (list them; repeat Step 3) / **Implement directly** (skip Gates C and D previews).

## Step 4 — Additions → GATE C

If the user asked for additions in Step 1 (menus, sections, features the references don't show), or the target app has elements the references lack (pagination, dropdowns, forms, maps, modals, empty states):
1. **Design:** build them **only from existing tokens and component patterns**. Same heights, borders, radii, type scale, and icon style. No new colors, shadows, or radii unless the user approves them.
2. **Slice:** put them in `slices/additions.body.html` (or into the relevant screen when they belong there, e.g. a new sidebar menu), with `@component` markers.
3. **Check:** render and check them as in Step 3.

**GATE C:** show the additions preview and list each addition with the existing pattern it was derived from. Ask Approve / Request changes / Implement directly. Skip this gate if there are no additions.

## Step 5 — Spec, tokens, and plan → GATE D

Read `<SKILL_DIR>/references/spec-and-plan.md`.
1. **Tokens:** run `tokens.py` → `tokens.json`. Design the three token layers (primitives → semantic → component) from it.
2. **Spec:** run `build_spec.py` → `style-spec.md`. It contains:
   - the CSS
   - the icons, with a usage table
   - the component markup
   - which pattern to use when
   - measurement tables
   - responsive rules
   - verification values (read from the rendered slices, not typed by hand)
3. **Plan:** write `plan.md` from `<SKILL_DIR>/assets/templates/plan.template.md`:
   - stack wiring and the file structure
   - the component API
   - **for existing apps:** an element-mapping table (current element → spec component), a per-page inventory, and a statement that content and behavior stay unchanged
   - **for new builds:** a per-screen build sheet
   - states (loading/empty/error), accessibility, and batches

**GATE D:** summarize the spec (tokens, component list, patterns) and the plan (files, mapping, batches, anything that doesn't map cleanly), then ask Approve / Request changes / Implement directly.

## Step 6 — Implement in batches → GATE E (per batch)

Read `<SKILL_DIR>/references/implement.md`.
1. **Theme first:** token files, global styles, font loading, icon sprite and `Icon` component, then shared components, then the shell (sidebar/topbar).
2. **Port the CSS rule by rule.** Keep the same selectors and rule order, and replace literals with tokens so that **computed values stay identical**.
3. **Restyles:** keep every page's data, columns, fields, actions, routes, permissions, text, and logic. Don't add or remove content unless the user approved an addition. Don't copy reference demo content.
4. **Batches:** 1–3 screens per batch, in the order from the plan.
5. **After each batch:** run Step 7, then **GATE E:** show app screenshots next to the slice previews, the parity report, and fixed mismatches. Ask **Approve & continue** / **Request changes** / **Implement the remaining batches directly** (keep verifying each batch, and report at the end).

## Step 7 — Verify

Read `<SKILL_DIR>/references/verify.md`. For every batch:
- **Parity:** `check_parity.mjs` compares the slice with the app page for the spec's selector list at 1440 / 1024 / 390. Differences must be zero except content-dependent widths.
- **Tokens:** `check_tokens.mjs` must report zero raw values outside the theme files.
- **Checks:** no horizontal page scroll, icons come only from the sprite, and table columns line up.
- **Report:** a table of what was checked, what failed, what was fixed, the changed files, and the screenshot paths.

## After the last batch
- Tell the user which files hold the design system (`style-spec.md`, slices, tokens).
- Suggest a one-line `CLAUDE.md` rule so future UI work follows the spec:
  `For any UI work, follow docs/pixelproof/style-spec.md exactly and use the theme tokens.`
- Offer to add new screens later by repeating Steps 3–7 for just those screens.
