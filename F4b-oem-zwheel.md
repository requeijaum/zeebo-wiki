# F4b — OEM Z-Wheel [EM CURSO]
## [CONF] zeemu `BrewZWheelOem.h` (15/09)
- Serviço OEM com 4 objetos + vtables: config, root_form, mcp, telemetry (+send_count, config_lines).
- `handle_hook(name, cpu)` — intercepta por nome de hook.
## [CONF parcial]
- zeebx: branches `fix-zwheel-roller`, `fix-otimizacoes-pos-zwheel` (conteúdo por diff).
## [CONF] diff zwheel zeebx já mergeado (15/09, commits 11/09)
- `d7a73d3` (Kaio): despacho de eventos + superfície do roller (`src/machine.rs`).
- `c109a54`: fonte usada pelo roller.
- `39de79a`: roller inferior destravado; causas: (1) Widget vtable só até Slot 16, roller
  (`tectoy.mod` 0x23860/0x23d0c) chama `Slot17(0x8000, pFont)` → UnimplementedCall abortava;
  fix = Slot17 retorna SUCCESS; (2) `tt_dlqueue.db` vazio → falta tabela DBINFO p/ SQLite.
## Pendente
- Quem chama Z-Wheel no boot (AppMgr gate?); confronto fork.
## [CONF] Z-Wheel IDs + dados (LLE `notes/ZWHEEL_SQLITE_SCHEMAS.md`, 15/09)
- App ID 274755, CLSID 0x01070798 ("TECTOY"); VFS `fs:/mif/274755.mif`, `fs:/mod/274755/`, `fs:/~0x01070798/`.
- SQLite 3 (págs 1024B): GAMEINFO(game_id,class_id,playcount,dt_*,boxart,flags,size),
  TITLETEXT(game_id,lang_id,titletext), DBINFO(version,subversion) — DBINFO é a tabela que
  faltava no `tt_dlqueue.db` vazio do fix zeebx.
- lang FourCC: PT 0x20205450, EN 0x20204545, ES 0x20205345.
