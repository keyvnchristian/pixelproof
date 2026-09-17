# Intake (Step 1)

Ask everything in **one round**. Offer sensible defaults so the user can answer quickly. If `docs/pixelproof/context.md` or the conversation already answers a question, don't ask it again; list the answer in the GATE A summary instead, marked "(from context)".

## Questions

1. **References:** which images, screenshots, or design docs, and which parts of each?
   - Several references can be combined, e.g. "sidebar from A, tables from B, dashboard widgets from C".
   - If they conflict, ask which one wins for each area (layout, color, type, components).
2. **Mode:**
   - **New build:** create screens from scratch.
   - **Restyle:** apply the style to an existing codebase. Content and behavior stay; only visuals change.
3. **Brand overrides:**
   - Primary color (hex). If the user points at their current app, sample it from a screenshot with `measure.py palette`.
   - Logo file.
   - Font override (default: the font measured from the reference).
   - Anything else that must differ from the reference (e.g. "keep our badge color").
4. **Target stack:**
   - framework and version
   - styling (Tailwind version, CSS modules, plain CSS)
   - component library, if any
   - chart and map libraries

   Detect these from the repo when possible and only confirm with the user.
5. **Scope:** which screens, in which order. For a restyle, list the app's existing pages from the router and let the user confirm.
6. **Additions:** "Are there any features, menu items, or sections you want to add in this style that the references don't show?" Examples:
   - a new sidebar menu structure
   - a settings page
   - a map panel
   - pagination
   - a form
   - empty states
   - a notifications drawer

   Record each addition with a one-line description.
7. **Content policy:**
   - **Restyle:** keep the app's own content; never copy the reference's demo content.
   - **New build:** use realistic placeholder content in the user's domain and language.
8. **Output location:** default `docs/pixelproof/`.

## GATE A summary format

```
Intake summary
- References: <file> → <what it's used for> (…)
- Mode: new build | restyle of <repo/app>
- Brand: primary <hex>, logo <path>, font <name>
- Stack: <framework>, <styling>, <libraries>
- Screens (in order): 1. … 2. …
- Additions: <name> — <description> (…)
- Content: <policy>
- Output: <folder>
Approve, or tell me what to change?
```

## Notes
- **Low-resolution or partial references:** ask for a larger export before measuring. Low-resolution images lead to guessed values.
- **Mobile references:** treat mobile as the primary width and derive desktop, instead of the other way around.
- **Figma exports:** ask for the frame width and whether the export is 1× or 2×. It removes the scale guesswork.
