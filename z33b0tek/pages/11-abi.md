# ABI Reference: structures, class IDs, error codes

## Structures

AEERect, 8 bytes:

```
offset 0: int16 x
offset 2: int16 y
offset 4: int16 dx
offset 6: int16 dy
```

AEEAppStart, 24 bytes on 32-bit ARM:

```
offset 0:  int         error
offset 4:  AEECLSID    clsApp
offset 8:  IDisplay *  pDisplay
offset 12: AEERect     rc
offset 20: const char *pszArgs
```

Character type: AECHAR is 16 bits. Strings passed to text APIs are arrays of
16-bit code units, not bytes.

## Class IDs

Class IDs are 32-bit. The core range starts from the runtime version value:

| Name | Value |
|---|---|
| AEECLSID_CORE | QVERSION + 0x1000 |
| AEECLSID_SHELL | AEECLSID_CORE |
| AEECLSID_DISPLAY | AEECLSID_CORE + 1 |
| AEECLSID_DISPLAYCLONE | AEECLSID_CORE + 43 |
| AEECLSID_APPLETCTL | AEECLSID_CORE + 88 |
| AEECLSID_APPLET | AEECLSID_APP |

A game also declares its own class ID in its metadata file. The MIF identifier
and the class ID a title actually registers at runtime can differ; the runtime
value is the one that matters.

## Return codes

| Value | Meaning |
|---|---|
| 0 | success |
| 3 | ECLASSNOTSUPPORT |
| 20 | EUNSUPPORTED |

## Calling convention recap

- ARM AAPCS: this pointer in R0 where the interface takes one, then R1 to R3,
  then stack arguments.
- Return value in R0.
- All HLE entry points must preserve the guest register file except for
  documented clobbers.
