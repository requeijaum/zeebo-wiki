# F3 — Core BREW [IN PROGRESS]
## [CONF] `ishell.cpp` CreateInstance (clone, 09-15)
- AAPCS: cls=R1, ppobj=R2; factory → Write32(ppobj, obj), R0=0 SUCCESS;
  no factory → R0=3 ECLASSNOTSUPPORT (AEEError.h; 20 would be EUNSUPPORTED).
- `RegisterInstance(cls, ptr)` singletons + `RegisterFactory(cls, fn)`; `DescribeClsid` for logs.
- SDK CLSIDs (AEEClassIDs.h): SHELL=CORE+0, DISPLAY=CORE+1, DISPLAYCLONE=CORE+43, APPLETCTL=CORE+88.
## [CONF] `idisplay.cpp` (556 lines)
- Implemented: DrawText, DrawRect, SetColor, SetClipRect(18)/GetClipRect, BitBlt,
  GetDeviceBitmap, SetDestination/GetDestination, IsEnabled, AllocateDib,
  CreateDIBitmap(Ex), Update. `Build()` assembles the vtable.
## [CONF] `file_hle.cpp` (26KB)
- FileMgr: OpenFile, GetInfo, Test, MkDir, GetFreeSpace, EnumInit/EnumNext.
- Handles: Read/Write/Seek, FileGetInfo(Ex). Over VirtualFilesystem + normalized writable path.
## [CONF] heap + font
- Heap: AddRef/Release, Malloc/Realloc/Free, StrDup, CheckAvail, GetMemStats(Ex) (`heap_hle.cpp`).
- Font: self-authored clean-room 5x7 bitmap (`GetGlyph5x7`, uppercase+digits; rest = box) for DrawText HUD.
## [CONF] RESOLVED (09-15): SetClipRect = slot 18
- IBase in this ABI has 2 slots (AddRef/Release, no QueryInterface in vtable — `AEEIBase.h`).
  4-way proof: SDK macro, clone `Build()` (16/17/18), zeemu `add_method(18)`, zeebx `aee_slots.rs` (index 18).
  The 'slot 19' hypothesis assumed IBase=3 — wrong here.
## Pending
- Confrontation with parked fork.
