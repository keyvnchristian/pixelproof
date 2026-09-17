# Implementation plan — <project>

Mode: <new build | restyle>. Brand: primary <hex>, logo <path>, font <family>.
Status: draft, waiting for approval at GATE D.

## 1. Stack wiring
| Concern | Decision |
|---|---|
| Framework / styling | <e.g. Next.js 15 App Router, Tailwind v4> |
| Token files | `src/styles/theme/primitives.css`, `semantic.css`, `breakpoints.ts`, `tokens.ts` |
| Global CSS entry | <path>; import order: primitives → semantic → base → components |
| Component CSS | `src/styles/components/*.css` (one per spec group) |
| Font loading | <next/font / link tag> |
| Icons | `IconSprite` rendered in <root layout>; `Icon` component |
| Tailwind mapping | theme values → `var(--…)`; layout only |
| Charts / maps | <library>; colors via `readToken()` |

## 2. Files
**Create:** <list>
**Change:** <list>
**Delete after migration:** <legacy styles/components>

## 3. Component API
| Component | Props | Classes produced | Component tokens | Spec |
|---|---|---|---|---|
| Button | `variant: 'primary' \| 'outline' \| 'light'`, `size: 'md' \| 'top' \| 'row'`, `icon?` | `btn btn-primary btn-top` … | `--btn-h`, `--btn-px` | §4.x |

## 4a. Restyle — element mapping (every element type in the app)
| Existing element | Becomes | Spec | Notes |
|---|---|---|---|
| Page title + breadcrumb | `.topbar` + `.breadcrumb` | §4.x | |
| Status pill | two-line text | §4.x | |

## 4b. Restyle — per-page inventory (content unchanged)
### <Page name> (`/route`)
| Current element | Maps to | Content kept |
|---|---|---|
| Stat strip (4 counts) | status tab counts | same 4 counts |
| Table: Order Id, Customer, Drop Point, Trip Id, Status, Action | `.panel` + `.data-table` | same columns, same order |
Doesn't map cleanly → **question for user:** <…>

## 4c. New build — build sheets
### <Screen>
| Region | Component | Classes | Spacing (token → px) | Size (token → px) | Data | States |
|---|---|---|---|---|---|---|

## 5. Additions (approved at GATE C)
| Addition | Where | Derived from | Spec |
|---|---|---|---|

## 6. States
- **Loading:** skeleton blocks with the same size and radius as the element they replace, `--bg-chip`, no shimmer under reduced motion.
- **Empty:** inside the same frame, a 16px `--text-3` message and one primary action.
- **Error:** inside the same frame, a message saying what failed plus a retry button (outline).
- **Disabled:** `--opacity-disabled` and `cursor: default`.

## 7. Accessibility
Landmarks, icon-button labels, aria states, focus order, and contrast notes.

## 8. Batches
1. Theme + base + icons + shared components + shell
2. <screens>
3. <screens>

Each batch ends with verification and GATE E.

## 9. Risks
| Risk | Mitigation |
|---|---|
