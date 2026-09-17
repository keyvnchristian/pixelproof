# /pixelproof help

Reply with this list, adapted to the user's language:

```
Pixelproof — pixel-exact UI from design references

Setup
  /pixelproof teach               interview once → docs/pixelproof/context.md

Build
  /pixelproof replicate <refs…>   build exactly from screenshots / design.md (default)
  /pixelproof enhance [looks|perf|structure]   no reference? improve looks, speed, or god components
  /pixelproof extract [--url]     turn the current UI into a spec + tokens
  /pixelproof add "<what>"        add a page/section/menu in the same style
  /pixelproof theme "<change>"    rebrand: color, font, radius, density

Check (read-only)
  /pixelproof audit [path]        design-consistency audit with scores
  /pixelproof roast [url|path]    brutally honest, funny critique (--spicy)
  /pixelproof compare <ref> <url> drift check against one reference
  /pixelproof verify [page|all]   parity + token + overflow checks
  /pixelproof responsive [url]    breakpoint torture test

Utility
  /pixelproof status              progress, gates, next step
  /pixelproof help                this list

Everything is saved in docs/pixelproof/. Commands that change code always show a preview and ask first.
Setup check: npx pixelproof doctor
```
