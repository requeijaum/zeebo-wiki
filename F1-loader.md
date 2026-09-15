# F1 — Loader [IN PROGRESS]
## [CONF] direct read of the clone (09-15)
- **.mod**: flat ARM binary, headerless, position-independent (`LoadMod(core, data, base)`).
  Proof quoted in code: real DD, 23 instructions, nested calls OK (`core/loader/mod.h`).
- **GGZ**: table of N BE 8B entries (offset, decompressed_size); table len = offset[0]; N = offset[0]/8;
  each entry -> RFC1952 gzip stream, FNAME = original name. `GgzArchive::Parse/Extract` (`core/loader/ggz.h`).
- **BAR**: 32B LE header (off8=sub-table, off16=real offset table, off20=count, off24=data start);
  opened via `ISHELL_LoadResDataEx`, not an embedded parser; derived from Peggle's real `resources.bar`
  (RIFF/ID3/PNG land exactly on computed offsets). (`core/loader/bar.h`). [CONF]
- **MIF**: full binary layout NOT understood; confirmed: UTF-16LE strings with 0xFFFE BOM,
  ending at null or next BOM (name/publisher/version for UI). (`core/loader/mif.h`). [CONF]
- Pending: AEEMod_Load offset inside .mod (F2).
