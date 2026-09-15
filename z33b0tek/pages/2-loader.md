# Loader and Container Formats

A Zeebo title is a BREW module plus one or more asset containers.
This page describes each container as observed on real commercial dumps.

## Container types

| Extension | Role | Where the runtime gets it |
|---|---|---|
| .mod | the title's ARM code image | the module loader |
| .ggz | compressed asset archive | the game, then ISHELL_LoadResData |
| .bar | resource archive with a resource ID directory | ISHELL_LoadResDataEx |
| .mif | module information: name, publisher, version | the shell and the store UI |
| .bid | interface definition, used by tools | build tooling only |
| .sig | signature blob shipped beside some titles | installation and validation |

A title does not have to use every container.
Observed combinations include a module with two archives, and a module with one archive plus a signature file.

## Module image: .mod

- Flat ARM binary.
  No header, no section table, no relocation table observed.
- Position independent: the image can be placed at any base address. 
- The entry point is at file offset 0. 
- It is not an ELF, not a PE, and not a container of either. 
- Nothing in the image names the runtime entry symbol;
  the runtime knows where to call because the convention is fixed.

Verification: a real commercial module was loaded at an arbitrary address and single-stepped on an ARM interpreter.
Twenty-three instructions executed, including two nested calls with correct prologue, epilogue and BX LR return, with no header parsing of any kind.

## Asset archive: GGZ

No public specification exists.
The layout below was derived from real archives.

- The file opens with a table of N entries, 8 bytes each, big-endian. 
- Each entry holds an offset (u32) and a decompressed size (u32). 
- The byte length of the table equals the offset value of the first entry. 
- Therefore N = first_entry_offset / 8. 
- Each entry points to an RFC 1952 gzip stream elsewhere in the file. 
- When present, the gzip FNAME field carries the asset's original filename, which is why archive contents can be listed without extra metadata. 

| Field | Size | Endianness | Meaning |
|---|---|---|---|
| offset | 4 | big | start of the gzip stream for this entry |
| decompressed_size | 4 | big | expected size after decompression |

## Resource archive: BAR

Used by titles that ship a resources.bar.
The title opens it through ISHELL_LoadResDataEx, so there is no parser inside the module to trace.
The layout below was derived from raw bytes and cross-checked against embedded file signatures.

Header, 32 bytes, little-endian:

| Offset | Size | Meaning |
|---|---|---|
| 0 | 4 | unconfirmed |
| 4 | 4 | unconfirmed |
| 8 | 4 | first sub-table start offset (observed value 32) |
| 12 | 4 | first sub-table byte length |
| 16 | 4 | real offset table start, equal to offset 8 plus length 12 |
| 20 | 4 | real offset table entry count |
| 24 | 4 | start of resource data, equal to the first offset entry |
| 28 | 4 | unconfirmed |

Entry and directory records:

- Offset table entries pair a 32-bit offset with a 32-bit size. 
- Resource ID records are 8 bytes: type (u16), requested_id (u16), unknown (u16), entry_index (u16). 
- The type field selects the loader used on the payload, so the same archive can carry raw images, audio streams and RLE bitmaps side by side. 

Verification: on a real resources.bar, embedded RIFF, ID3 and PNG file signatures land exactly on the offsets this layout computes.

## Metadata: MIF

The full binary layout is not understood.
What is confirmed:

- Human-readable metadata is stored as UTF-16LE strings. 
- Each string is prefixed by a 0xFFFE byte-order mark. 
- A string ends at a null code unit or at the next BOM. 
- Strings can sit back to back with no separator, so a reader must scan for BOMs rather than split on nulls. 
- This is enough to read app name, publisher and version for a library UI. 

Still unknown: resource tables, class IDs and privilege bits.
A loader that needs those must read them from the module or from the runtime class registry instead.

## What the loader must do

| Step | Requirement |
|---|---|
| Map the image | writable memory, at any base address |
| Resolve the entry | call the load entry point with the runtime's helper table |
| Register the factory | the module hands back its instance creation callback |
| Expose archives | mount GGZ and BAR so resource calls resolve by name or ID |
| Parse metadata | read MIF strings for the shell and for user-visible naming |

Evidence: container layouts from real commercial dumps;
module behaviour from single-stepping a real image;
MIF string encoding from real SDK samples and a commercial module.
