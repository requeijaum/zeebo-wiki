# ABI Reference: Structures, Class IDs and Codes

Everything on this page is fixed layout information that a runtime must match
exactly. A single wrong field offset shifts every subsequent read.

## Structures

AEERect, 8 bytes. Not four 32-bit integers, which is the intuitive but wrong
assumption:

```
offset 0: int16 x
offset 2: int16 y
offset 4: int16 dx
offset 6: int16 dy
```

AEEAppStart, 24 bytes on 32-bit ARM. Passed by pointer in the start event:

```
offset 0:  int         error
offset 4:  AEECLSID    clsApp
offset 8:  IDisplay *  pDisplay
offset 12: AEERect     rc
offset 20: const char *pszArgs
```

| Field | Direction | Use |
|---|---|---|
| error | app writes | non-zero aborts the start |
| clsApp | runtime writes | the class ID being launched |
| pDisplay | runtime writes | the drawing surface for this applet |
| rc | runtime writes | the applet rectangle on screen |
| pszArgs | runtime writes | optional arguments passed at launch |

Character type: AECHAR is 16 bits. Text APIs take arrays of 16-bit code units, so
treating a text buffer as bytes produces garbled output rather than a crash.

## Class IDs

Class IDs are 32-bit and the core range starts from a version-dependent base.

| Name | Value |
|---|---|
| AEECLSID_CORE | QVERSION + 0x1000 |
| AEECLSID_SHELL | AEECLSID_CORE |
| AEECLSID_DISPLAY | AEECLSID_CORE + 1 |
| AEECLSID_DISPLAYCLONE | AEECLSID_CORE + 43 |
| AEECLSID_APPLETCTL | AEECLSID_CORE + 88 |
| AEECLSID_APPLET | AEECLSID_APP |

Media classes live in their own range, starting at 0x01005500. OEM classes for
this platform sit outside both ranges; the store application, for example, uses
0x01070798.

A title declares a class ID in its metadata, but the value it registers at runtime
can differ from the one in its module information file. The runtime value is the
one that matters when creating instances.

## Return codes

| Value | Meaning | Typical cause |
|---|---|---|
| 0 | success | normal completion |
| 3 | ECLASSNOTSUPPORT | the requested class is not implemented |
| 20 | EUNSUPPORTED | the operation is not supported on this build |

Confusing 3 with 20 changes control flow in titles that branch on the exact
value, and both differ from a generic negative error.

## Calling convention

| Rule | Detail |
|---|---|
| Argument registers | R0 to R3, then the stack |
| Return value | R0 |
| This pointer | the first argument for interface methods |
| Preserved | callee-saved registers must survive an HLE call |
| CPSR | must be restored unless the method documents a flag change |

Two additional rules matter for a runtime that traps calls:

- A trapped call must not clobber guest registers other than the documented return
  value and the caller-saved set.
- If the HLE implementation needs to call back into guest code, the guest register
  file must be saved and restored around that call unless the method is documented
  to be reentrant.

## Endianness

The CPU is little-endian in practice for all title data. One exception is worth
noting because it is easy to miss: the GGZ archive table is big-endian, so a
loader that assumes one endianness everywhere will read plausible but wrong
offsets.

Evidence: structure layouts, class ID table and return codes from the public SDK
headers. Endianness note from real archive files.
