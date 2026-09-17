#!/usr/bin/env python3
"""Find oversized ("god") UI components and suggest how to split them.

Usage: python structure_scan.py <path> --out structure.json [--md structure.md] [--top 20]

Scans .tsx/.jsx/.vue/.svelte/.astro files (skipping node_modules and build output) and measures, per file:
  lines           non-blank lines
  components      components defined in the file
  state           useState/useReducer/ref() calls
  effects         useEffect/useLayoutEffect/watch/onMounted calls
  memo            useMemo/useCallback/computed calls
  data_calls      fetch/axios/supabase/trpc/graphql/useQuery/useSWR calls
  handlers        inline JSX handlers (onClick={() => …})
  conditionals    conditional renders ({x && …}, ternaries inside JSX)
  jsx_depth       deepest element nesting
  props           props destructured by the main component
  imports         import statements
  sections        top-level JSX regions (comment labels or landmark tags), used as split candidates
A weighted "god score" ranks files; files at 45 or above are flagged. Heuristic, regex-based: confirm by reading the file.
"""
import argparse
import json
import re
from pathlib import Path

EXTS = {".tsx", ".jsx", ".vue", ".svelte", ".astro"}
SKIP = {"node_modules", ".next", "dist", "build", "out", ".git", "coverage", ".turbo", ".svelte-kit", ".nuxt", "storybook-static"}

RX = {
    "components": re.compile(r"(?:export\s+(?:default\s+)?)?(?:function\s+([A-Z]\w*)\s*\(|const\s+([A-Z]\w*)\s*(?::[^=]+)?=\s*(?:React\.)?(?:memo\(|forwardRef\()?\s*(?:\([^)]*\)|\w+)\s*=>)"),
    "state": re.compile(r"\b(?:useState|useReducer|ref|reactive|writable)\s*[<(]"),
    "effects": re.compile(r"\b(?:useEffect|useLayoutEffect|watchEffect|watch|onMounted|onMount|\$effect)\s*\("),
    "memo": re.compile(r"\b(?:useMemo|useCallback|computed|\$derived)\s*\("),
    "data_calls": re.compile(r"\b(?:fetch|axios\.\w+|axios|supabase\.from|\.rpc|trpc\.\w+|useQuery|useMutation|useSWR|useInfiniteQuery|gql`)\s*[(`]?"),
    "handlers": re.compile(r"\bon[A-Z]\w*=\{\s*(?:\([^)]*\)|\w+)\s*=>"),
    "conditionals": re.compile(r"\{[^{}\n]*?(?:&&|\?[^{}\n]*:)[^{}\n]*<"),
    "imports": re.compile(r"^\s*import\s", re.M),
}
OPEN_TAG = re.compile(r"<([A-Za-z][\w.:-]*)(\s[^<>]*?)?(/?)>", re.S)
CLOSE_TAG = re.compile(r"</([A-Za-z][\w.:-]*)\s*>")
SECTION_COMMENT = re.compile(r"\{/\*\s*([^*]{3,60}?)\s*\*/\}|<!--\s*([^-]{3,60}?)\s*-->")
LANDMARK = re.compile(r"<(header|nav|aside|section|footer|form|table|dialog|Modal|Dialog|Drawer|Sheet|Tabs|Table|Form|Card)\b[^>]*?(?:aria-label=\"([^\"]+)\"|id=\"([^\"]+)\"|className=\"([\w-]+))?", re.S)
VOID = {"img", "input", "br", "hr", "meta", "link", "source", "area", "col", "wbr"}


def jsx_depth(text):
    depth = best = 0
    for m in re.finditer(r"</?[A-Za-z][\w.:-]*[^<>]*?/?>", text):
        tag = m.group(0)
        if tag.startswith("</"):
            depth = max(0, depth - 1)
            continue
        name = re.match(r"<([\w.:-]+)", tag).group(1)
        if tag.endswith("/>") or name.lower() in VOID:
            best = max(best, depth + 1)
            continue
        depth += 1
        best = max(best, depth)
    return best


def main_props(text):
    m = re.search(r"(?:function\s+[A-Z]\w*|const\s+[A-Z]\w*\s*(?::[^=]+)?=\s*(?:React\.)?(?:memo\(|forwardRef\()?)\s*\(\s*\{([^}]*)\}", text)
    if not m:
        m = re.search(r"defineProps<\{([^}]*)\}>|defineProps\(\{([^}]*)\}\)|let\s+\{([^}]*)\}\s*=\s*\$props", text)
        if not m:
            return 0
        body = next(g for g in m.groups() if g)
        return len([p for p in re.split(r"[,;\n]", body) if p.strip() and ":" in p or p.strip().isidentifier()])
    return len([p for p in m.group(1).split(",") if p.strip() and not p.strip().startswith("...")])


def score(r):
    s = 0
    s += min(30, max(0, r["lines"] - 150) / 10)
    s += min(15, max(0, r["state"] - 4) * 2.5)
    s += min(12, max(0, r["effects"] - 2) * 3)
    s += min(10, max(0, r["data_calls"] - 1) * 3)
    s += min(10, max(0, r["jsx_depth"] - 8) * 1.5)
    s += min(8, max(0, r["props"] - 8))
    s += min(8, max(0, r["handlers"] - 6) * 0.8)
    s += min(7, max(0, r["conditionals"] - 6) * 0.7)
    if r["data_calls"] and r["state"] > 3 and r["lines"] > 200:
        s += 10  # fetching + state + big view in one place
    return round(min(100, s))


def advice(r):
    out = []
    if r["data_calls"] and (r["state"] > 2 or r["effects"] > 1):
        out.append("Move data loading and its state into a hook (use<Name>Data) or a server component/loader; keep the view presentational.")
    if r["effects"] > 3:
        out.append("Several effects usually hide derived state; compute it during render or with useMemo, and keep effects for real side effects.")
    if r["state"] > 8:
        out.append("Group related state with useReducer or a small store; pass setters down as named callbacks.")
    if len(r["sections"]) >= 3:
        out.append("Extract each section into its own component: " + ", ".join(r["sections"][:6]) + ".")
    if r["jsx_depth"] > 12:
        out.append("Deep nesting: extract repeated row/card markup into components and flatten wrapper divs.")
    if r["handlers"] > 8:
        out.append("Many inline handlers: name them (handleX) or move them into the hook so the JSX reads as layout.")
    if r["props"] > 10:
        out.append("Wide props: pass a single object per concern, or split into smaller components with focused props.")
    if not out and r["lines"] > 300:
        out.append("Long file: split by section and move helpers/constants to their own modules.")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    root = Path(args.path).resolve()
    rows = []
    for p in root.rglob("*"):
        if p.suffix not in EXTS or p.is_dir():
            continue
        if any(part in SKIP or part.startswith(".") for part in p.relative_to(root).parts[:-1]):
            continue
        if re.search(r"\.(test|spec|stories)\.", p.name):
            continue
        text = p.read_text(errors="ignore")
        lines = sum(1 for l in text.split("\n") if l.strip())
        comps = {a or b for a, b in RX["components"].findall(text)}
        sections = []
        for a, b in SECTION_COMMENT.findall(text):
            label = (a or b).strip()
            if label and not label.lower().startswith(("eslint", "todo", "@", "prettier")) and label not in sections:
                sections.append(label)
        if len(sections) < 3:
            for tag, aria, idv, cls in LANDMARK.findall(text):
                label = aria or idv or (f"{tag}.{cls}" if cls else tag)
                if label not in sections:
                    sections.append(label)
        r = {
            "file": str(p.relative_to(root)), "lines": lines, "components": sorted(c for c in comps if c),
            "state": len(RX["state"].findall(text)), "effects": len(RX["effects"].findall(text)),
            "memo": len(RX["memo"].findall(text)), "data_calls": len(RX["data_calls"].findall(text)),
            "handlers": len(RX["handlers"].findall(text)), "conditionals": len(RX["conditionals"].findall(text)),
            "jsx_depth": jsx_depth(text), "props": main_props(text), "imports": len(RX["imports"].findall(text)),
            "use_client": text.lstrip().startswith(("'use client'", '"use client"')), "sections": sections[:12],
        }
        r["god_score"] = score(r)
        r["advice"] = advice(r) if r["god_score"] >= 30 else []
        rows.append(r)
    rows.sort(key=lambda r: (-r["god_score"], -r["lines"]))
    flagged = [r for r in rows if r["god_score"] >= 45]
    data = {"root": str(root), "files": len(rows), "flagged": len(flagged), "components": rows}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"scanned {len(rows)} component files; {len(flagged)} flagged (god score ≥ 45)")
    for r in rows[: args.top]:
        if r["god_score"] < 30:
            break
        print(f"  {r['god_score']:>3}  {r['file']}  ({r['lines']} lines, state {r['state']}, effects {r['effects']}, "
              f"data {r['data_calls']}, depth {r['jsx_depth']}, props {r['props']})")
    print(f"wrote {out}")
    if args.md:
        md = [f"# Component structure — {root.name}", "", f"{len(rows)} files scanned, {len(flagged)} flagged.", "",
              "| Score | File | Lines | State | Effects | Data | Depth | Props | Handlers |", "|---|---|---|---|---|---|---|---|---|"]
        for r in rows[: args.top]:
            md.append(f"| {r['god_score']} | `{r['file']}` | {r['lines']} | {r['state']} | {r['effects']} | {r['data_calls']} | {r['jsx_depth']} | {r['props']} | {r['handlers']} |")
        md.append("")
        for r in rows[: args.top]:
            if r["advice"]:
                md += [f"## `{r['file']}` — score {r['god_score']}", ""] + [f"- {a}" for a in r["advice"]] + [""]
        Path(args.md).write_text("\n".join(md))
        print(f"wrote {args.md}")


if __name__ == "__main__":
    main()
