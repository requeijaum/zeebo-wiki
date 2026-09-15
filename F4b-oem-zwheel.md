# F4b — OEM Z-Wheel [IN PROGRESS]
## [CONF] zeemu `BrewZWheelOem.h` (09-15)
- OEM service with 4 objects + vtables: config, root_form, mcp, telemetry (+send_count, config_lines).
- `handle_hook(name, cpu)` — dispatches by hook name.
## [CONF] zeebx zwheel diff, already merged (09-15, commits 09-11)
- `d7a73d3` (Kaio): event dispatch + roller surface (`src/machine.rs`).
- `c109a54`: font used by the roller.
- `39de79a`: lower roller unlocked; root causes: (1) Widget vtable stopped at Slot 16 while the roller
  (`tectoy.mod` 0x23860/0x23d0c) calls `Slot17(0x8000, pFont)` → UnimplementedCall aborted assembly;
  fix = Slot17 returns SUCCESS; (2) `tt_dlqueue.db` empty → missing DBINFO table for SQLite.
## [CONF] Z-Wheel IDs + data (LLE `notes/ZWHEEL_SQLITE_SCHEMAS.md`, 09-15)
- App ID 274755, CLSID 0x01070798 ("TECTOY"); VFS `fs:/mif/274755.mif`, `fs:/mod/274755/`, `fs:/~0x01070798/`.
- SQLite 3 (1024B pages): GAMEINFO(game_id,class_id,playcount,dt_*,boxart,flags,size),
  TITLETEXT(game_id,lang_id,titletext), DBINFO(version,subversion) — DBINFO is the table
  missing from the empty `tt_dlqueue.db` in the zeebx fix.
- Language FourCC: PT 0x20205450, EN 0x20204545, ES 0x20205345.
## Pending
- Who calls Z-Wheel at boot (AppMgr gate?); parked-fork confrontation.
