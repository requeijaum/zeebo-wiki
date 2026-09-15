# F3 — BREW núcleo [EM CURSO]
## [CONF] `ishell.cpp` CreateInstance (clone, 15/09)
- AAPCS: cls=R1, ppobj=R2; factory → Write32(ppobj, obj), R0=0 SUCCESS;
  sem factory → R0=3 ECLASSNOTSUPPORT (AEEError.h; 20 seria EUNSUPPORTED).
- `RegisterInstance(cls, ptr)` singletons + `RegisterFactory(cls, fn)`; `DescribeClsid` p/ log.
- CLSIDs SDK (AEEClassIDs.h): SHELL=CORE+0, DISPLAY=CORE+1, DISPLAYCLONE=CORE+43, APPLETCTL=CORE+88.
## [CONF] `idisplay.cpp` (556 linhas)
- Implementados: DrawText, DrawRect, SetColor, SetClipRect(18)/GetClipRect, BitBlt,
  GetDeviceBitmap, SetDestination/GetDestination, IsEnabled, AllocateDib,
  CreateDIBitmap(Ex), Update. `Build()` monta vtable.
## [CONF] `file_hle.cpp` (26KB)
- FileMgr: OpenFile, GetInfo, Test, MkDir, GetFreeSpace, EnumInit/EnumNext.
- Handle: Read/Write/Seek, FileGetInfo(Ex). Sobre VirtualFilesystem + path gravável normalizado.
## [CONF] heap + font
- Heap: AddRef/Release, Malloc/Realloc/Free, StrDup, CheckAvail, GetMemStats(Ex) (`heap_hle.cpp`).
- Font: 5x7 bitmap autoral clean-room (`GetGlyph5x7`, maiúsculas+dígitos; resto = caixa) p/ DrawText HUD.
## Pendente
- Confronto full-rewrite (fork canônico).
- **RESOLVIDO [CONF]** (15/09): SetClipRect = slot 18. IBase nesta ABI tem 2 slots (AddRef/Release, sem QueryInterface na vtable — `AEEIBase.h`). Prova 4 vias: SDK macro, clone `Build()` (16/17/18), zeemu `add_method(18)`, zeebx `aee_slots.rs` (índice 18). Hipótese 'slot 19' assumia IBase=3 — errada aqui.
