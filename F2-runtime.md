# F2 — AEE Runtime [IN PROGRESS]
## [CONF] direct read of `core/brew/mod_runtime.h` (clone, 09-14)
- .mod RVCT ROPI: `AEEStaticMod_New` computes its load address via PC-relative addressing,
  reads a pointer 4B before it, then calls the slot at 0x68 (MALLOC nSize+16=IModuleVtbl) — matches AEEModGen.c.
- Slot 0x6c = FREE (the `AEEApplet_New` cleanup path).
- Slot 0xc0 = `ISHELL_CreateInstance` via ambient context (138 call sites in the real DD);
  context+12 = IShell, +20 = IDisplay (SetClipRect slot 18), +0x2c = unknown relative-vtable object (Peggle).
- `SetShellInstance/SetDisplayInstance/SetThirdContextObject` inject the pointers.
## [CONF] `core/brew/hle_runtime.h`
- Two-way bridge: sentinel traps (guest→HLE call-outs, vtable points at sentinel,
  `Register/RegisterLabeled` for unimplemented-slot logging) + `CallArmFunction`
  (HLE→guest: AEEMod_Load, CreateInstance, HandleEvent, runs to return, AAPCS R0-R3).
- `CallArmFunctionPreservingContext` for synchronous callbacks (e.g. ISQL::Exec rows).
## [CONF] `core/brew/ishell.h` — START dispatch + timer
- `CreateInstance` is real: known singletons + factories (e.g. IDisplay); other slots stubbed.
- `SetTimer/CancelTimer` are real, one-shot: the game re-arms every frame (`SetTimer(16ms, cb)` inside
  the real DD `HandleEvent(EVT_APP_START)`) — the cooperative loop lives on the host.
- `SetAppletHandleEvent(fn)` stores the guest's real HandleEvent for event dispatch.
## [CONF] Bug confrontation (ROADMAP.md UPDATE 13/14, parked fork)
- Symptom: DD schedules ONE 16ms timer (cb=0x11c074) at START, then busy-waits on GetUpTimeMS
  with no Sleep/yield → START continuation never returns → timer never fires.
- Tried: ZEEB_UPTIME_YIELD (yields but re-enters WITHOUT the outer tick → 0 ticks),
  ZEEB_TIMER_PREEMPT=1 (save context, run due timers as the shell would, restore).
- SDK contract (brew-sim-recon, public AEEShell/AEECallback headers): cooperative + returning;
  the per-frame loop lives in the shell timer queue, re-armed each frame — identical to
  the clone contract (`ishell.h`). Diagnosis and fix direction converge. [CONF]
- State: fix pending validation on DD (AUTOPRESS still gated).
