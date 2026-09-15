#!/usr/bin/env python3
"""Regenerate interface vtable tables in z33b0tek pages from SDK headers.

Usage:
  python3 gen_interfaces.py <sdk-platform-dir> --update pages/*.md

Pages embed tables between markers:

  <!-- BEGIN GENERATED: IHID -->
  <!-- END GENERATED: IHID -->

The tool resolves the inheritance chain first (IBase contributes 2 slots,
IQI contributes 3) so slot numbers are real vtable indices.
"""
import pathlib, re, sys

MARK_BEGIN = "<!-- BEGIN GENERATED: %s -->"
MARK_END = "<!-- END GENERATED: %s -->"


def find_macro(sdk: pathlib.Path, macro: str):
    pat = re.compile(r"#define\s+" + macro + r"\(iname\s*\)")
    for h in sorted(sdk.rglob("*.h")):
        try:
            txt = h.read_text(errors="replace")
        except OSError:
            continue
        m = pat.search(txt)
        if m:
            return h, txt[m.start():]
    return None, None


def macro_body(txt: str):
    """Return the list of physical lines of a macro definition."""
    lines = txt.splitlines()
    body = []
    for i, ln in enumerate(lines):
        if i == 0:
            continue
        body.append(ln)
        if not ln.rstrip().endswith("\\"):
            break
    return [l.strip().rstrip("\\").strip() for l in body]


def clean_args(s):
    s = re.sub(r"/\*.*?\*/", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().strip(",").strip()


def chain(sdk: pathlib.Path, iface: str, seen=None):
    """Return [iface, parent, grandparent...] resolving INHERIT_ lines."""
    seen = seen or []
    _, txt = find_macro(sdk, "INHERIT_" + iface)
    if txt is None:
        return [iface]
    parents = []
    for ln in macro_body(txt):
        m = re.match(r"INHERIT_(\w+)\(", ln)
        if m:
            parents.append(m.group(1))
    if not parents:
        return [iface]
    p = parents[0]
    if p in seen:
        return [iface]
    return [iface] + chain(sdk, p, seen + [iface])


def methods(sdk: pathlib.Path, iface: str):
    """Own methods of iface, in declaration order."""
    _, txt = find_macro(sdk, "INHERIT_" + iface)
    if txt is None:
        return []
    out = []
    for ln in macro_body(txt):
        if re.match(r"INHERIT_\w+\(", ln):
            continue
        m = re.match(r"^(.*?)\(\s*\*?\s*(\w+)\s*\*?\s*\)\s*\((.*)\)\s*;?\s*$", ln)
        if not m:
            continue
        ret, name, args = m.group(1).strip(), m.group(2), clean_args(m.group(3))
        args = re.sub(r"^[A-Za-z_]\w*\s*\**\s*(?:[A-Za-z_]\w*)?\s*,?\s*", "", args, count=1).strip()
        args = ("this, " + args) if args else "this"
        args = re.sub(r",\s*$", "", args).strip()
        out.append((name, ret, args))
    return out


def slots(sdk: pathlib.Path, iface: str):
    """Full slot list with real indices, base first."""
    ch = list(reversed(chain(sdk, iface)))
    rows, idx = [], 0
    for name in ch:
        for mname, ret, args in methods(sdk, name):
            rows.append((idx, mname, ret, args)); idx += 1
    return rows, ch
def render(sdk: pathlib.Path, iface: str, note: str):
    rows, ch = slots(sdk, iface)
    base = ", ".join(ch)
    out = [f"_Generated from the public SDK header `AEE{iface}.h`. "
           f"Inheritance chain: {base}._",
           "",
           f"Base slots: **{ch[0]} → {ch[-1]}**, so slot 0 is the first method of "
           f"{ch[0]} and the first method of {iface} starts at the first free index.",
           "",
           "| Slot | Method | Returns | Arguments |",
           "|---|---|---|---|"]
    for i, name, ret, args in rows:
        out.append(f"| {i} | {name} | {ret} | {args} |")
    if note:
        out += ["", note]
    return "\n".join(out)


def update_page(path: pathlib.Path, sdk: pathlib.Path, notes: dict):
    txt = path.read_text()
    found = re.findall(r"<!-- BEGIN GENERATED: (\w+) -->", txt)
    changed = 0
    for iface in found:
        b, e = MARK_BEGIN % iface, MARK_END % iface
        if b in txt and e in txt:
            head, rest = txt.split(b, 1)
            _, tail = rest.split(e, 1)
            txt = head + b + "\n" + render(sdk, iface, notes.get(iface, "")) + "\n" + e + tail
            changed += 1
    if changed:
        path.write_text(txt)
    return changed


def main():
    sdk = pathlib.Path(sys.argv[1])
    args = sys.argv[2:]
    if "--update" not in args:
        print(__doc__); return
    pages = [pathlib.Path(a) for a in args[args.index("--update") + 1:]]
    notes = {
        "IBase": "- Every interface starts with AddRef and Release. "
                 "There is no QueryInterface slot here.",
        "IQI": "- IQI adds QueryInterface at slot 2, after AddRef and Release.",
        "IShell": "- IShell inherits IBase directly, so its first own method is slot 2.",
        "IDisplay": "- SetClipRect is slot 18, confirmed by the header, by two "
                    "independent implementations and by a real game disassembly.",
    }
    for p in pages:
        n = update_page(p, sdk, notes)
        print(f"{p.name}: {n} block(s) regenerated")


if __name__ == "__main__":
    main()
