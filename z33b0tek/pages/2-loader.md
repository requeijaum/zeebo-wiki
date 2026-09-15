# Loader and Container Formats

A Zeebo title is a BREW module plus one or more asset containers.
This page describes each container as observed on real commercial dumps.

## Container types

| Extension | Role | Where the runtime gets it |
|---|---|---|
| .mod | the title's ARM code image | the module loader |
| .ggz | compressed asset archive | the game, then ISHELL_LoadResData |
| .bar | resource archive with a resource ID directory | ISHELL_LoadResDataEx |
| .pakz | first-party asset archive, PACK plus LZMA payloads | the VFS, under the title's directory |
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

Header, 30 bytes, little-endian:

| Offset | Size | Meaning |
|---|---|---|
| 0 | 2 | container magic 0x0011 (u16); the same header serves BAR and MIF |
| 2 | 2 | version field (observed 1) |
| 4 | 2 | second version field (observed 1) |
| 6 | 2 | registry record count |
| 8 | 4 | registry start offset (observed 32) |
| 12 | 4 | registry byte length |
| 16 | 4 | index table start, equal to offset 8 plus length 12 |
| 20 | 4 | index table entry count |
| 24 | 4 | start of resource data, equal to the first index offset |
| 28 | 2 | end offset (u16), may be followed by a footer |

Entry and directory records:

- Offset table entries pair a 32-bit offset with a 32-bit size. 
- Resource ID records are 8 bytes: type (u16), requested_id (u16), unknown (u16), entry_index (u16). 
- The type field selects the loader used on the payload, so the same archive can carry raw images, audio streams and RLE bitmaps side by side. 

Verification: on a real resources.bar, embedded RIFF, ID3 and PNG file signatures land exactly on the offsets this layout computes.

## Metadata: MIF

The MIF is the same container as the BAR, with the resource directory naming the module fields.
Verified on 62 shipped titles, cross-checked against BAR payloads and the public SDK:

- Header: 30 bytes, little-endian, as the table above.
- The header holds magic 0x0011, two version fields, registry, index, data and end offsets.
- Registry records are 8 bytes, read as four u16 fields.
- The fields are type, requested id, unknown and entry index.
- String payloads carry an encoding marker byte before the text.
- The marker 0x03 selects 8-bit text.
- The markers 0xFF 0xFE and 0xFE 0xFF select UTF-16 with a BOM.
- A reader scans for markers rather than splitting on nulls.
- Resource IDs 6, 7 and 8 are the company, copyright and version fields (AEEShell IDS_MIF_COMPANY / IDS_MIF_COPYRIGHT / IDS_MIF_VERSION).
- ISHELL_GetAppAuthor / GetAppCopyright / GetAppVersion select them with a null file name.
- Some files carry trailing bytes after the last index offset.
- They are a footer, not resources, and a strict reader must validate the end offset.
- The MIF directory also carries the applet record with the class ID, read by walking the offset table.
- The module and the runtime class registry are alternative sources.

## Asset archive: PAKZ

The first-party packer writes PACK followed by LZMA_ALONE streams.
Observed on ten resource packages across the first-party library, 7 487 index entries total.

- The file opens with the magic PACK.
- An index of 64-byte records follows.
- Each record names an entry and carries its offset and size.
- The name field is 56 bytes, not 40.
- On 354 of the 7 487 observed entries the NUL terminator falls in bytes 41-43.
- The tail of the name lives in bytes 40-55.
- A reader that stops at 40 bytes truncates those names.
- Each entry payload is an LZMA_ALONE stream that decompresses cleanly.
- Index names may carry the leading directory or omit it.
- The runtime matches both, for example ani/touxiang1 and resources/ani/touxiang1.

## What the loader must do

| Step | Requirement |
|---|---|
| Map the image | writable memory, at any base address |
| Resolve the entry | call the load entry point with the runtime's helper table |
| Register the factory | the module hands back its instance creation callback |
| Expose archives | mount GGZ, BAR and PAKZ so resource calls resolve by name or ID |
| Parse metadata | read MIF strings for the shell and for user-visible naming |

Evidence: container layouts from real commercial dumps;
module behaviour from single-stepping a real image;
MIF string encoding from real SDK samples and a commercial module.
