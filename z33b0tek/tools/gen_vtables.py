#!/usr/bin/env python3
"""Generate vtable reference pages for z33b0tek from public BREW SDK headers.

Usage:
  python3 gen_vtables.py <path-to-sdk>/platform <out-dir>

Parses INHERIT_<Iface>(iname) macro blocks (the C vtable layout) and emits
markdown tables with the real slot index. IBase contributes 2 slots
(AddRef, Release); there is no QueryInterface in this ABI's vtable.
"""
import pathlib, re, sys

def macro_rows(header, macro):
    lines = header.read_text(errors="replace").splitlines()
    buf, on = [], False
    for ln in lines:
        if not on:
            if re.match(r"#define\s+" + macro + r"\(iname\s*\)", ln):
                on = True
            continue
        if ln.rstrip().endswith("\\"):
            buf.append(ln)
        else:
            if ln.strip():
                buf.append(ln)
            break
    rows = []
    for ln in buf:
        ln = ln.strip().rstrip("\\").strip()
        if ln.startswith("INHERIT_"):
            rows.append(("__ibase__", ln.strip(";"), ""))
            continue
        m = re.search(r"^(.*?)\(\*(\w+)\)\(iname\s*\*\s*p\w*(.*?)\)\s*;?\s*$", ln)
        if m:
            rows.append((m.group(2), m.group(1).strip(), ("this" + m.group(3)).strip()))
    return rows

def tbl(rows, ibase=2):
    out = ["| Slot | Method | Returns | Arguments |", "|---|---|---|---|"]
    i = 0
    for name, ret, args in rows:
        if name == "__ibase__":
            for nm in ("AddRef", "Release"):
                out.append(f"| {i} | {nm} | uint32 | this |")
                i += 1
            continue
        out.append(f"| {i} | {name} | {ret} | {args} |")
        i += 1
    return "\n".join(out)

def main():
    sdk = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    ishell = next(sdk.glob("**/AEEIShell.h"))
    idisp = next(sdk.glob("**/AEEIDisplay.h"))
    r1 = macro_rows(ishell, "INHERIT_IShell")
    idisp_rows = macro_rows(idisp, "INHERIT_IDisplay")
    if not any(x[0] == "__ibase__" for x in r1):
        r1 = [("__ibase__", "", "")] + r1
    if not any(x[0] == "__ibase__" for x in idisp_rows):
        idisp_rows = [("__ibase__", "", "")] + idisp_rows
    txt = """# IShell Interface

IShell is the shell object. It is the entry point for object creation,
applet control, timers, resources, dialogs and system notification.

Vtable layout: slot N lives at vtable + N*4. Slots 0 and 1 are AddRef and
Release, inherited from IBase.

""" + tbl(r1) + """

Notes:

- Slot 0 is AddRef, slot 1 is Release. There is no QueryInterface slot.
- On ARM, arguments follow AAPCS: this in R0, then R1-R3, then the stack.
- ISHELL_CreateInstance returns 0 on success and 3 (ECLASSNOTSUPPORT) when the
  requested class is not supported by the runtime.
"""
    (out / "3-ishell.md").write_text(txt)
    txt2 = """# IDisplay Interface

IDisplay is the drawing surface for an applet. Text, rectangles, bitmaps and
DIB allocation all pass through this interface.

Vtable layout: slot N lives at vtable + N*4. Slots 0 and 1 are AddRef and
Release, inherited from IBase.

""" + tbl(idisp_rows) + """

Notes:

- SetClipRect is slot 18. This value is confirmed by the SDK macro layout, by
  two independent emulator implementations and by a real game disassembly that
  calls slot 18 while setting a clip rectangle.
- DrawText takes an AECHAR string; AECHAR is a 16-bit character type, so game
  text is not plain ASCII.
- BitBlt takes an AEERasterOp raster operation code.
- Update pushes the surface to the physical display. The boolean argument
  requests deferred update when set.
"""
    (out / "4-idisplay.md").write_text(txt2)
    print("wrote", out / "3-ishell.md", out / "4-idisplay.md")

if __name__ == "__main__":
    main()
