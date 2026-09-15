#!/usr/bin/env python3
"""Reflow page sources to the semantic line break style.

One sentence per line. Paragraphs are first joined, then split at sentence
boundaries, so no sentence is broken mid-way. Headings, tables, code fences,
list markers and indentation are preserved.

Usage:
  python3 reflow.py pages/*.md          # rewrite in place
  python3 reflow.py --check pages/*.md  # report violations, do not write
"""
import pathlib, re, sys

SKIP_START = ("#", "|", "```", "<!--", ">")
SKIP_CONTAINS = ("_Generated from", "Base slots:")
SENT_END = (".", "!", "?", ":", ";", ")")
MAX_LINE = 180
ABBREV = ("e.g.", "i.e.", "etc.", "vs.")


SEMI = re.compile(r"(?<=;) +")
TOKEN = re.compile(r"(?<=[.!?]) +(?=[A-Z(`\d\"'])")


def split_sentences(s):
    for ab in ABBREV:
        s = s.replace(ab, ab[:-1] + "\x00")
    out = []
    for chunk in SEMI.split(s):
        out.extend(TOKEN.split(chunk))
    return [p.replace("\x00", ".") for p in out]


def structural(ln):
    if not ln.strip():
        return True
    if ln.lstrip().startswith(SKIP_START):
        return True
    return any(k in ln for k in SKIP_CONTAINS)


MARKER = re.compile(r"^(\s*)([-*])\s+(.*)$")


def reflow_file(path, check=False):
    src = path.read_text().splitlines()
    out, buf, in_code, changed, bad = [], [], False, 0, []

    def flush():
        nonlocal buf, changed
        if not buf:
            return
        m = MARKER.match(buf[0])
        indent = buf[0][:len(buf[0]) - len(buf[0].lstrip())]
        if m:
            indent = m.group(1)
            joined = m.group(3) + " " + " ".join(x.strip() for x in buf[1:])
            first_prefix = f"{indent}{m.group(2)} "
            cont_prefix = indent + "  "
        else:
            joined = " ".join(x.strip() for x in buf)
            first_prefix = cont_prefix = indent
        parts = split_sentences(joined)
        out.append(first_prefix + parts[0])
        for extra in parts[1:]:
            out.append(cont_prefix + extra)
        if len(buf) != len(parts):
            changed += 1
        buf = []

    for idx, ln in enumerate(src, 1):
        if ln.strip().startswith("```"):
            flush(); in_code = not in_code; out.append(ln); continue
        if in_code:
            out.append(ln); continue
        if structural(ln):
            flush(); out.append(ln); continue
        if MARKER.match(ln) and buf:
            flush()
        buf.append(ln)
    flush()

    if check:
        if changed:
            bad.append((0, f"{changed} paragraph(s) are not in one-sentence-per-line form"))
        fence = False
        for i, ln in enumerate(out, 1):
            s = ln.strip()
            if s.startswith("```"):
                fence = not fence
                continue
            if fence or not s or structural(ln):
                continue
            if not s.endswith(SENT_END):
                bad.append((i, "no sentence end: " + s[:60]))
            elif len(s) > MAX_LINE:
                bad.append((i, f"{len(s)} chars: " + s[:60]))
    else:
        path.write_text("\n".join(out) + "\n")
    return changed, bad


def main():
    check = "--check" in sys.argv
    files = [pathlib.Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    total, issues = 0, 0
    for f in files:
        c, bad = reflow_file(f, check)
        total += c
        if check and bad:
            print(f"{f.name}: {len(bad)} line(s)")
            for idx, txt in bad[:5]:
                print(f"    {idx}: {txt}")
            issues += len(bad)
        elif not check:
            print(f"{f.name}: {c} paragraph(s) reflowed")
    if check:
        print(f"\n{issues} line(s) violate the one-sentence-per-line rule")
        return 1 if issues else 0
    print(f"\n{total} paragraph(s) reflowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
