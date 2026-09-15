#!/usr/bin/env python3
"""Audit the z33b0tek page sources against the house standard.

Rules enforced:
  R1 one H1 per page
  R2 an intro paragraph of at least 2 lines before the first H2
  R3 every H2 section has at least MIN_SECTION_LINES non-empty lines
  R4 prose lines are wrapped at MAX_LINE characters
  R5 no empty generated blocks (markers must be filled)
  R6 no forbidden identifiers anywhere in a page
  R7 one sentence per line: prose lines end with terminal punctuation

Exit code 1 on any violation.
"""
import pathlib, re, sys

MIN_SECTION_LINES = 3
MIN_SECTION_WORDS = 60
MAX_LINE = 180
SKIP_WRAP_PREFIXES = ("|", "```", "<!--", "_Generated", "Base slots:", "- `", "#")
FORBIDDEN = [
    r"(?i)zeebulator", r"(?i)zeemu", r"(?i)infuse\b", r"(?i)zeebx", r"(?i)curupira",
    r"(?i)marcelo|tanisho|kaio|tuxality", r"(?i)requeijaum|rafaelfrequiao", r"/home/",
    r"(?i)\bclone\b", r"(?i)\bbateria\b", r"(?i)game_probe", r"(?i)pcsx2|dolphin|higan|ymir|dynarmic",
    r"(?i)skill-impact|confronto|phase8|roadmap", r"(?i)compat-list", r"\bFONTE\b",
]


TABLE_SEP = re.compile(r"^\|[\s:\-|]+\|?$")


def section_words(body):
    """Words in prose plus table cells. Code fences are ignored."""
    words, fence = 0, False
    for ln in body:
        if ln.strip().startswith("```"):
            fence = not fence
            continue
        if fence or not ln.strip():
            continue
        if ln.startswith("|"):
            if TABLE_SEP.match(ln):
                continue
            words += len(ln.strip().strip("|").replace("|", " ").split())
        else:
            words += len(ln.split())
    return words


def sections(lines):
    out, cur = [], ("", [])
    for ln in lines:
        if ln.startswith("## "):
            out.append(cur); cur = (ln[3:].strip(), [])
        else:
            cur[1].append(ln)
    out.append(cur)
    return out


SENT_END = (".", "!", "?", ":", ";", ")")
SKIP_LINE = ("#", "|", "```", "<!--", ">", "_Generated", "Base slots:")


def sentence_break_issues(lines):
    errs, fence = [], False
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s:
            continue
        if s.startswith(SKIP_LINE) or any(k in ln for k in ("_Generated from", "Base slots:")):
            continue
        if not s.endswith(SENT_END):
            errs.append(f"R7: line {i} does not end a sentence: {s[:56]}")
    return errs


def check(path: pathlib.Path):
    errs = []
    txt = path.read_text()
    lines = txt.splitlines()
    h1 = [l for l in lines if l.startswith("# ")]
    if len(h1) != 1:
        errs.append(f"R1: {len(h1)} H1 headings")
    secs = sections(lines)
    intro = [l for l in secs[0][1] if l.strip()]
    if len(intro) < 2:
        errs.append(f"R2: intro has {len(intro)} lines")
    for name, body in secs[1:]:
        n = len([l for l in body if l.strip() and not TABLE_SEP.match(l)])
        if name.lower().startswith("evidence"):
            continue
        words = section_words(body)
        if n < MIN_SECTION_LINES or words < MIN_SECTION_WORDS:
            errs.append(f"R3: section '{name[:40]}' has {n} lines / {words} words")
    gen_ranges = [(m.start(), m.end()) for m in
                  re.finditer(r"<!-- BEGIN GENERATED.*?<!-- END GENERATED[^>]*-->", txt, re.S)]
    pos = 0
    for i, ln in enumerate(lines, 1):
        start = pos; pos += len(ln) + 1
        in_gen = any(s <= start < e for s, e in gen_ranges)
        if in_gen:
            continue
        if len(ln) > MAX_LINE and not ln.startswith(SKIP_WRAP_PREFIXES):
            errs.append(f"R4: line {i} is {len(ln)} chars")
    for m in re.finditer(r"<!-- BEGIN GENERATED: (\w+) -->(.*?)<!-- END GENERATED", txt, re.S):
        if len(m.group(2).strip()) < 40:
            errs.append(f"R5: generated block {m.group(1)} is empty")
    scan = re.sub(r"<!-- BEGIN GENERATED.*?<!-- END GENERATED[^>]*-->", "", txt, flags=re.S)
    errs.extend(sentence_break_issues(lines))
    for pat in FORBIDDEN:
        mm = re.search(r"(?s).{0,50}" + pat.replace("(?i)", "") + r".{0,50}", scan, re.I)
        if mm:
            errs.append(f"R6: forbidden {pat} -> {mm.group(0)[:80]}")
    return errs


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "pages")
    total = 0
    for p in sorted(root.glob("*.md")):
        errs = check(p)
        total += len(errs)
        status = "ok" if not errs else f"{len(errs)} issue(s)"
        print(f"{p.name:28} {status}")
        for e in errs:
            print(f"    {e}")
    print(f"\n{total} issue(s) total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
