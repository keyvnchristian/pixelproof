# /pixelproof teach — teach Pixelproof about this project

Interviews the user once and writes `docs/pixelproof/context.md`. Every other command reads this file first, so answers never have to be repeated across commands, sessions, or teammates. It edits no app code.

Usage:
- `/pixelproof teach`: first run, or a full refresh
- `/pixelproof teach "<fact>"`: add or change one fact, e.g. `/pixelproof teach "status is always two-line text, never pills"`
- `/pixelproof teach --show`: print the current context

## Steps

### 1. Learn what you can before asking
Read the repo quickly:
- `package.json` (framework, styling, component, chart, map, and icon libraries)
- router or page list
- logo and favicon files
- theme or token files and the Tailwind config
- README
- existing `docs/pixelproof/` (state, spec)
- any existing `PRODUCT.md`, `DESIGN.md`, or `CLAUDE.md` design rules

Pre-fill everything you can, and mark each pre-filled item "(detected)".

### 2. Interview in one round
Ask only what the repo can't answer. Offer defaults, and keep it to about 8 questions. Use the question tool if available.
1. **Product:** what it is, in one sentence, and the main job users do with it.
2. **Users:** who they are, on which devices, how often, and how expert they are. For example: "dispatchers on desktop all day; supervisors on phones".
3. **Brand:**
   - primary color (hex)
   - logo path
   - font
   - personality in 3 words (e.g. calm, dense, trustworthy)
4. **References:** which files are the official design references, and what each one is the source for.
5. **Always rules:** things every screen must follow. For example: "status is two-line text", "UI language is Indonesian", "tables scroll on mobile", "no shadows".
6. **Never rules:** things to avoid. For example: "purple gradients", "emoji icons", "text under 12px".
7. **Running the app:**
   - the dev command and URL
   - how to log in for screenshots (credentials come from environment variable names, never literal values)
   - which pages matter most
8. **Workflow preferences:**
   - how many screens per batch
   - which preview size to use
   - the report language
   - whether to prefer "implement directly" after the first approval

### 3. Write the context file
Write `docs/pixelproof/context.md` using this template:

```markdown
# Pixelproof context — <project>
Updated: <date> · Source: /pixelproof teach

## Product
<one sentence> · Main job: <…>

## Users
- <who, device, frequency, expertise>

## Brand
- Primary: <hex> · Logo: <path> · Font: <family>
- Personality: <3 words>

## References
| File | Source of truth for |
|---|---|

## Always
- <rule>

## Never
- <rule>

## Tech (detected + confirmed)
- Stack: <…> · Styling: <…> · Tokens: <path> · Icons: <sprite/library> · Charts/maps: <…>
- Run: `<command>` → <url> · Login: <steps, env var names only>
- Key pages: <list>

## Workflow
- Batch size: <n> · Previews: <widths> · Report language: <lang> · After first approval: <ask each time | implement directly>

## Open questions
- <anything unresolved>
```

Rules for writing it:
- Keep it under about 150 lines.
- Write facts, not essays.
- Never store secrets (passwords, tokens, API keys). Store environment variable names instead.
- For `/pixelproof teach "<fact>"`: put the fact in the right section, replacing any fact it contradicts, and show the diff.

### 4. Confirm
Show the file, or the diff, and ask **Approve / Change**. Then update `state.json`:
- `contextUpdatedAt`: the current time
- `brand`: from the context file

### 5. Suggest the next step
Suggest one of `/pixelproof extract`, `/pixelproof replicate <refs>`, or `/pixelproof audit`, based on what the project has.

## How other commands use the context
- **Every command:** reads `context.md` before starting. Values in it are treated as confirmed answers: don't ask again, and just mention them in the intake summary.
- **When context and a request conflict:** the user's current request wins. Ask whether to update the context.
- **`audit` and `roast`:** judge against the product, users, and personality. Dense tables are fine for expert desktop users; tiny tap targets are not fine if supervisors use phones.
- **Always/Never rules:** these are extra checks in `audit`, `roast`, `verify`, and `add`, and constraints for `replicate` and `theme`.
