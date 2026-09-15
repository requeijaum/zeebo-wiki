# Loader and Container Formats

Zeebo titles ship as a BREW module plus asset containers.
This page describes each container as observed on real game dumps.

## Module: .mod

- Flat ARM binary. No header, no section table, no relocation table observed.
- Position independent: the image loads at any base address.
- Entry point is at file offset 0.
- The module is a relocatable BREW application image, not an ELF or PE file.
- Verification: a real commercial .mod was loaded at an arbitrary address and
  single-stepped on an ARM interpreter. 23 instructions executed, including two
  nested calls with correct prologue, epilogue and BX LR return.

## Asset archive: GGZ

Reverse-engineered layout. No public specification exists.

- Header: table of N entries, 8 bytes each, big-endian.
- Entry fields: offset (u32), decompressed_size (u32).
- The byte length of the table equals the first entry's offset value.
- Therefore N = first_entry_offset / 8.
- Each entry points to a standard RFC 1952 gzip stream elsewhere in the file.
- When present, the gzip FNAME field carries the asset's original filename.

## Resource archive: BAR

Used by titles that ship a resources.bar, for example board-game ports.
The game opens it through ISHELL_LoadResDataEx. There is no embedded parser
inside the module, so the format was derived from raw bytes only.

Header is 32 bytes, little-endian:

| Offset | Meaning |
|---|---|
| 0 | unconfirmed |
| 4 | unconfirmed |
| 8 | first sub-table start offset (observed 32) |
| 12 | first sub-table byte length |
| 16 | real offset table start (= offset 8 + length 12) |
| 20 | real offset table entry count |
| 24 | start of resource data |

- Entry records pair an offset with a size.
- Resource ID directory entries are 8 bytes: type (u16), requested_id (u16),
  unknown (u16), entry_index (u16).
- Verification: embedded RIFF, ID3 and PNG file signatures land exactly on the
  offsets this layout computes, on a real resources.bar.

## Metadata: MIF

Module Information File. The full binary layout is not understood.

- Confirmed: human-readable metadata is stored as UTF-16LE strings.
- Each string is prefixed by a 0xFFFE byte-order mark.
- A string ends at a null code unit or at the next BOM; strings may be
  back to back with no separator.
- This is enough to read app name, publisher and version for a library UI.
- Resource tables, class IDs and privilege bits remain unknown.
