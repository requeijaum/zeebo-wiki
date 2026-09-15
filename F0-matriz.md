# F0 — matriz cobertura (célula = fato + fonte)
## [CONF] via ls direto (14/09)
- **Zeebulator loader** (`sources/zeebulator/core/loader/`): ggz, bar, mif, mod + assets (bmp/png/gif/tga, wav/mp3/midi, aez/atitc/fufs/obm1/pakz/pkg/sar). [CONF]
- **Zeebulator brew** (`sources/zeebulator/core/brew/`): ishell, idisplay, file_hle, hid_hle, gl_hle(+soft_gl_backend), media_hle, heap/hash/sql/thread_hle, mod_runtime, hle_runtime, brew_platform, virtual_filesystem, font5x7, bitmap_hle, mem_astream/unzip_stream, nid_table, compat/, extension_module, brew_resource_file. ~20 módulos (nota antiga dizia 13 — clone mais novo). [CONF]
- **Zeemu** (`sources/zeemu/`): brew/ com 51 .cpp (nota dizia ~50 — confirmado); inclui ZWheelOem, HID, Sound(Player), Net, ThreadScheduler, GL/EGL/QXGL(Dispatch/Draw), Micro3D, 3D. [CONF]
## lfm extração (julgada 15/09: 5 CONF corroboram, 5 INCERTO descartadas — ver skill-impact)
| Área | Zeebulator | Zeemu | Infuse | zeebx | SDK |
|---|---|---|---|---|---|
| loader | ggz/bar/mif/mod.cpp [CONF] | ELF/PELoader + AEEHelperTable/AppRunner [CONF] | fechado, só comportamento | src/loader (Rust) | ggzbrewtools [CONF] |
| BREW | ~20 módulos [CONF] | 51 .cpp [CONF] | fechado | src/brew (aee, slots, heap, vfs, sql, crypto) Rust [CONF] | headers AEE [CONF] |
| input IHID | hid_hle [CONF] | BrewHID [CONF] | fechado | src/input + fix-zwheel* [CONF parcial] | IHID ext Zeebo |
| OEM Z-Wheel | — | BrewZWheelOem.cpp [CONF] | fechado | fix-zwheel* branches [CONF parcial] | ext Zeebo |
| vídeo | gl_hle+soft_gl | BrewGL/EGL/QXGL/3D (nota) | ... | ... | ... |
| áudio | media_hle | ... | ... | ... | ... |
- **Infuse** (dossier `infuse.md`, A1 18/05/2024, fonte fechada): jogáveis DD, CNK 3D, Family Pack
  (+ BREW Asphalt/KH V-Cast); ~20 títulos até menu; dynarmic JIT. [CONF via dossier]
- **Zeeno** (dossier `zeeno.md`, 31/08/2026): Qt + debugger funcional, teclado 100%, renderer 3D;
  fechado, open-source planejado; motivado pelo Infuse fechado. Monitorar. [CONF via dossier]
- **ggzbrewtools** (MANIFEST): pack/unpack GGZ C++17+Boost, doc de formato (DMC/Sonic/DD). [CONF]
