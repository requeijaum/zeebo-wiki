> Origem: `projects/zeebo-emulator/research/lessons/other-emulators.md` (cópia integral 15/09; origem manda, wiki espelha).

# Lessons learned from other emulators

Applied to the Zeebo problem. Sources: Infuse (Tuxality) dev logs,
Zeebulator (PHASE8_LOG/ARCHITECTURE/TASKS), plus well-known emulator
project history (dynarmic lineage: Citra/yuzu/Ryujinx; libretro;
BREW emulator landscape: the dead "Brew Emulator" for Windows Mobile,
Xe emulators, etc.).

## 1. HLE beats LLE when the "hardware" is a closed runtime
BREW 4.0.2 is a giant Qualcomm codebase; games talk to it through AEE
C++ interfaces. Two independent projects (Infuse, Zeebulator) both chose
to reimplement the API surface. LLE would mean emulating the whole
MSM7201A (ARM9 baseband + AMSS + Rex/L4 + BREW) for zero benefit — the
ARM9 never runs game code. Lesson: **identify the real ABI boundary and
intercept there.** Bonus: no firmware/BIOS needed → legally distributable.

## 2. Interpreter first, JIT later (and dynarmic when you get there)
Zeebulator principle #4: "get it correct before it's fast." A JIT
optimizing the wrong model is wasted work. When the time comes, Infuse
proves dynarmic works for this workload (it's the same JIT the
Citra/yuzu/Ryujinx family uses for ARM). BUT: see lesson 4.

## 3. Core/frontend separation from day one
Libretro's oldest lesson, restated by Zeebulator: the same core behind
standalone + libretro frontends, with I/O through abstract backends.
Retrofitting it later is "far more expensive" (their words).

## 4. Thumb interworking + dynarmic = real pain
EmuGenWiki/Infuse: compiling with Thumb interworking caused boot issues
with dynarmic; the dev considered switching JITs or writing his own.
Lesson: for BREW modules that mix ARM/Thumb, test the JIT's
interworking support early; keep the interpreter as fallback.

## 5. The zero-memory false-positive trap (subtle and nasty)
Zeebulator's ARM interpreter decoded never-written (zero-filled) memory
as harmless `ANDEQ r0,r0,r0` no-ops. Result: a *plausible-looking but
meaningless* "success" — 262,237 no-op steps walking PC back to the
module base, silently re-entering AEEMod_Load and returning a bogus
module pointer. Caught only by `CallArmFunctionChecked`: a wrapper that
warns loudly if PC leaves the loaded module's address range. Lesson:
**never trust R0/return values alone; validate the execution path.**

## 6. Disassemble with real tools, not hex-by-hand
Zeebulator: "manual hex decoding of this same function produced real
mistakes before switching to the real tool" (`arm-none-eabi-objdump -D
-b binary -m arm`). Lesson: tool up early; document the exact command.

## 7. The SDK installer is a spec goldmine (clean-room-safe)
Zeebulator NSIS-extracted the BREW MP SDK installer to read reference
headers (AEEEvent.h → EVT_APP_START=0; AEEModGen.c → AEEStaticMod_New
flow). Reading published spec/header *structure* is clean-room-safe;
copying Qualcomm *implementation code* is not. Keep extracts outside the
repo (git-ignored) — that's also the legal hygiene that makes the
project distributable.

## 8. Compatibility is per-title reverse engineering
Every working title is a small RE project (Zeebulator's 8,883-line
PHASE8_LOG for ONE game; Infuse's per-game notes). Architecture must
make per-game quirks cheap (Zeebulator `core/brew/compat/`), and the
compat list must be honest and public (EmuGenWiki pages).

## 9. Audio: HLE mixer with resampling; MIDI via soundfonts
Infuse: multiple streams, host-rate/channel-independent resampling;
backends per-OS; ALSA "written but not working" — cross-platform audio
is its own project. Zeebulator: GM MIDI via soundfonts + mixer. Both
reimplemented audio at the AEE boundary (IMedia/ISound) rather than
emulating QDSP5.

## 10. Save states need host-side state too
Zeebulator: save states capture CPU regs + full guest memory, and
**replay real GL texture uploads** on cold load (host textures don't
survive). Host-side audio/timer state still not captured — expect no
music right after cold load. Lesson: in an HLE emulator, "state" spans
the guest AND your HLE objects — design serialization for both.

## 11. Scope discipline: skip the Z-Wheel
Infuse: Z-Wheel needs "too many dependencies and effort for not that
much of a gain." The Z-Wheel is the console's UI/game carousel (BREW
UI + asset manager). Lesson: skip UI reimplementation; boot games
directly.

## 12. Performance targets are modest
Zeebo games lock at 20–35 FPS by design; Infuse runs >full speed on an
M1 with a debug build and is playable on Haswell/N4200. An interpreter
may honestly be enough for most titles; JIT is a late-stage optimization.

## 13. Formats: write the spec as you go
Zeebulator's loader headers ARE the format docs (each with "confirmed
against real sample X"). The nocash-style docs in this project should
absorb them incrementally (docs/file-formats.md) — with CONFIRMED
markers and the exact sample each fact was verified against.

## 14. There is prior art in "BREW emulator" land
EmuGenWiki's cellphone emulators section: BREW emulation attempts
predate Zeebo (e.g. the old BREW emulator / Qualcomm's own BREW
Simulator for dev, Windows-only). Infuse's Windows Mobile compatibility
layer was itself BREW-on-BREW. Lesson: the BREW ABI has been
reverse-engineered in multiple eras — cross-check our ABI doc against
any surviving BREW emulator docs, not just Zeebo sources.
