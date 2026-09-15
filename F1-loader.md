# F1 — loader [EM CURSO]
## [CONF] leitura direta do clone (14/09)
- **.mod**: binário ARM flat, sem header, position-independent (`LoadMod(core, data, base)`).
  Prova citada no código: DD real, 23 instruções, calls aninhados OK (`core/loader/mod.h`).
- **GGZ**: tabela N entradas BE 8B (offset, decompressed_size); len tabela = offset[0]; N = offset[0]/8;
  cada entrada -> gzip RFC1952, FNAME = nome original. `GgzArchive::Parse/Extract` (`core/loader/ggz.h`).
- **BAR**: header 32B LE (off8=sub-table, off16=real offset table, off20=count, off24=data start);
  aberto via `ISHELL_LoadResDataEx`, não parser embutido; derivado do `resources.bar` real do Peggle
  (RIFF/ID3/PNG batem nos offsets). (`core/loader/bar.h`). [CONF]
- **MIF**: estrutura binária total NÃO entendida; confirmado: strings UTF-16LE com BOM 0xFFFE,
  terminadas em null ou próximo BOM (nome/publisher/versão p/ UI). (`core/loader/mif.h`). [CONF]
- Pendente: AEEMod_Load offset no .mod (F2).
