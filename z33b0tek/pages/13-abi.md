# ABI Reference: Structures, Class IDs and Codes

Everything on this page is fixed layout information that a runtime must match exactly.
A single wrong field offset shifts every subsequent read.

## Structures

AEERect, 8 bytes.
Not four 32-bit integers, which is the intuitive but wrong assumption:

```
offset 0: int16 x
offset 2: int16 y
offset 4: int16 dx
offset 6: int16 dy
```

AEEAppStart, 24 bytes on 32-bit ARM.
Passed by pointer in the start event:

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

Character type: AECHAR is 16 bits.
Text APIs take arrays of 16-bit code units, so treating a text buffer as bytes produces garbled output rather than a crash.

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

Media classes live in their own range, starting at 0x01005500.
OEM classes for this platform sit outside both ranges;
the store application, for example, uses 0x01070798.

A title declares a class ID in its metadata, but the value it registers at runtime can differ from the one in its module information file.
The runtime value is the one that matters when creating instances.

## Return codes

Most BREW calls return an int status, and titles branch on the exact value.
The set that shows up in real code is small.

| Value | Name | Meaning | Typical cause |
|---|---|---|---|
| 0 | SUCCESS | completed | normal path |
| 1 | EFAILED | general failure | unspecified, worth logging |
| 2 | ENOMEMORY | out of memory | heap exhausted or a size computed wrong |
| 3 | ECLASSNOTSUPPORT | class unsupported | the runtime does not implement that class ID |
| 10 | EBADCLASS | null class object | a null interface pointer was passed |
| 13 | EBADSTATE | invalid state | a call in the wrong lifecycle phase |
| 14 | EBADPARM | invalid parameter | wrong argument, often a null pointer |
| 16 | EBADITEM | invalid item | an index or resource ID that does not exist |
| 20 | EUNSUPPORTED | API unsupported | the operation exists but is not implemented here |
| 26 | EALREADY | already in progress | a second start without a stop |
| 32 | EITEMBUSY | busy | a device or context held by someone else |
| 43 | ENOTALLOWED | not allowed | a privilege or policy check failed |

Two of these carry disproportionate weight during bring-up:

- Returning 0 while writing a null pointer is worse than returning 2 or 20.
  The title proceeds and faults somewhere unrelated, and the real cause is lost.
- Confusing 3 with 20 changes control flow in titles that test for the exact value.
  Value 3 means the runtime does not have that class;
  value 20 means the operation is not implemented at all.

## Calling convention

| Rule | Detail |
|---|---|
| Argument registers | R0 to R3, then the stack |
| Return value | R0 |
| This pointer | the first argument for interface methods |
| Preserved | callee-saved registers must survive an HLE call |
| CPSR | must be restored unless the method documents a flag change |

Two additional rules matter for a runtime that traps calls:

- A trapped call must not clobber guest registers other than the documented return value and the caller-saved set. 
- If a trampoline needs to call back into guest code, the guest register file must be saved and restored around that call, unless the method is documented to be reentrant. 

## Endianness

The CPU is little-endian in practice for all title data, but the container formats are not uniform.

| Structure | Byte order | Note |
|---|---|---|
| Guest data, structs, integers | little | the CPU is little-endian |
| AECHAR strings | UTF-16, little | two bytes per character |
| GGZ archive table | big | entries are big-endian u32 pairs |
| GGZ payload | gzip stream | gzip itself is little-endian internally |
| BAR header and tables | little | 32-bit little-endian fields |
| MIF strings | UTF-16LE | with a 0xFFFE byte-order mark |

The GGZ table is the one that catches people out.
A loader that applies one endianness everywhere reads a plausible-looking entry count.
It then walks off into the file, producing assets that are the wrong size rather than an error.

