# /pixelproof status — where things stand

Read-only. Summarizes `docs/pixelproof/state.json` and the workspace.

## Reply format

```
Pixelproof — <project> (<mode>)
Brand: <primary> · Font: <family> · Context: <updated date | missing → /pixelproof teach>
Gates: A ✓  B ✓  C –  D ⏳  E(batch 1) ✓
Batches: 1 Orders + Control Tower — verified · 2 Trips + Drop Points — in progress
Last audit: 62 (2026-09-01) → 81 (2026-09-17)
Open questions: …
Next step: <the single most useful next command>
```

If there's no `state.json`, say that pixelproof hasn't been run here yet, and suggest one of:
- `/pixelproof teach` (recommended first)
- `/pixelproof replicate <refs>`
- `/pixelproof extract`
- `/pixelproof audit`
