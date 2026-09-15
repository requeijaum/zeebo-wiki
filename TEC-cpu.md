> Origem: `projects/zeebo-emulator/docs/cpu-techniques.md` (cópia integral 15/09; origem manda, wiki espelha).

# CPU / Implementation Techniques — Zeebo Emulator (Phase 5)

Grounded synthesis of the CPU-execution and dynamic-recompilation
techniques relevant to a Zeebo (ARM1136J-S / ARMv6) HLE emulator.

Sources & trust:
- [CONF] = verified against local clones (zeebulator, zeemu) or primary
  docs (ARM ARMv6, official SDK) in this repo.
- [PRIOR-ART] = well-established public projects (QEMU, dynarmic, Citra
  family, melonDS, FEX) — widely documented, treated as reliable.
- [ATENÇÃO] = claim originates from Rafael's Qwen research chat
  (`research/sources/chat-arm11-emulation.md`, AI-generated) and is NOT
  independently verified here; flagged so it is not trusted blindly
  (ROADMAP open-Q8 discipline).

---

## 1. The guest: what we must execute

- Guest CPU = **ARM1136J-S**, architecture **ARMv6** (ARM + Thumb-1;
  NO Thumb-2). [CONF — DevGuide / MSM7200A datasheet, docs/hardware-map.md]
- Both real open emus prove an **interpreter is sufficient** for BREW
  applets:
  - **zeebulator** = pure interpreter (`core/cpu/arm_interpreter.cpp`,
    no JIT/dynarec anywhere in core/). Runs Double Dragon through the
    full BREW lifecycle. [CONF]
  - **zeemu** = higan-derived ARMv4T core extended to ARMv6 + VFP for
    the ARM11 guest (`cpu/`). [CONF]
- Why interpreter-first is the right default here: BREW games are HLE'd
  at the AEE API boundary, so the emulator only runs the game's own
  applet code (tens–hundreds of KB), not a full OS. Games lock
  **20–35 FPS** on real hardware, so raw CPU throughput is not the
  bottleneck. [CONF — observed in oracle captures, ROADMAP Phase 1]

Decision (Phase 6 input): **interpreter-first; add a JIT only if a
specific title is CPU-bound.** This matches zeebulator and avoids the
single largest engineering cost (a correct ARMv6→host dynarec).

---

## 2. Interpreter design notes (the proven path)

Key ARMv6 correctness points a Zeebo interpreter MUST get right — each
already a live concern in our RE:

1. **ARM/Thumb interworking.** `BX`/`BLX` toggle the `T` bit in CPSR;
   the decoder must switch 32-bit ARM ↔ 16-bit Thumb-1 per the low bit
   of the target address. Real .mods mix both: the module entry veneers
   are ARM, much applet body is Thumb. [CONF — capstone RE of ddragonz.mod,
   nand-dump-analysis.md]
2. **MRS/MSR (status-register moves).** ARMv6 "misc instruction space";
   zeebulator originally trapped on these. Now implemented with
   field-mask byte enables (CPSR/SPSR, register+immediate). [CONF —
   ROADMAP Phase 1, commit 9461854]
3. **Memory alignment.** ARM faults on unaligned word/halfword access;
   a naive host pointer pass-through hides the bug. For HLE of userland
   applets this is low-risk (compiler-generated aligned access), but the
   memory layer must not silently mis-handle it. [PRIOR-ART]
4. **CP15 / MMU.** For HLE we do NOT emulate the MMU — BREW applets run
   in a flat virtual view the loader sets up. LLE of CP15 is only needed
   for firmware/AMSS bring-up (out of scope for the game emulator).
   [CONF — HLE strategy, research/KNOWLEDGE.md]
5. **Lazy flags.** Even in an interpreter, deferring NZCV computation
   until a flag is read is a cheap, well-known speedup if profiling ever
   shows the flag path hot. [PRIOR-ART]

---

## 3. If/when a JIT is needed — dynarec landscape

Host targets that matter to Rafael: **x86_64** (desktop) and **ARM64**
(handhelds / Apple Silicon / Snapdragon).

| Project | Guest | Technique | Lesson for us |
|---|---|---|---|
| **dynarmic** | ARM (v5–v8, incl. ARMv6) | mature ARM→x86_64/ARM64 JIT library | drop-in option; **Infuse uses it** [CONF dossier]. Fastest route to a JIT without writing one |
| **Citra/Lime3DS/PabloMK7** | ARM11 (ARMv6!) | ARMv6→x86_64/ARM64 dynarec + OS HLE | closest guest match (also ARM11); their ARMv6 unaligned-access + CP15 handling is the reference [PRIOR-ART] |
| **melonDS** | ARM9/ARM7 (v4/v5) | threaded JIT, per-thread block cache | shows the threading model; simpler guest than ours |
| **QEMU TCG** | many | portable IR (TCG) + full MMU | the LLE/firmware tool, not the game path |
| **FEX** | x86→ARM64 | aggressive block translation, direct register mapping, lazy flags | technique reference for ARM64 hosts (register pressure, EFLAGS≈NZCV) [ATENÇÃO source, but FEX is public] |

**ARM64-host shortcut** [PRIOR-ART / ATENÇÃO detail]: guest ARMv6 and
host ARMv8 share the ARM family, so a dynarec can map guest GPRs almost
1:1 to host GPRs and translate most data-processing ops near-natively —
much lower overhead than x86 hosts. dynarmic already exploits this.

**Recommendation:** if a JIT is ever required, adopt **dynarmic**
(proven, ARMv6-capable, already validated by Infuse) rather than writing
a bespoke JIT/AOT — unless the goal becomes a research JIT for its own
sake, in which case study Citra's ARMv6 backend first (same guest ISA).

---

## 4. AOT vs JIT for .mod applets [ATENÇÃO — Qwen blueprint, unverified]

The Qwen chat proposed a hybrid: **AOT-compile static .mod applets**
(the code is a flat, position-independent ARM image known at load) +
**JIT for anything dynamic**. This is plausible because a .mod is a
headerless ROPI blob [CONF — brew-abi.md] whose code range is fixed at
load, so ahead-of-time translation of hot functions is feasible. NOT
pursued yet; recorded as a design option, not a decided path.

Pipeline sketch (Qwen, unverified): decoder ARMv6→IR → optimizer
(constant propagation, DCE, peephole) → host codegen; lazy flags;
register allocation; Thumb-1 + CP15 handled later. Standard dynarec
shape — no Zeebo-specific insight, so treat as generic guidance.

---

## 5. GPU path (for completeness — Adreno 130 / GLES 1.1)

Not a CPU technique, but the same HLE philosophy applies and the Xemu
NV2A case is the instructive prior art:

- Real games call **GLES 1.1** through the AEE IGL/IEGL surface [CONF —
  DevGuide §7.2, docs/hardware-map.md]. HLE = translate those GL calls
  to host GL/Vulkan; do NOT emulate Adreno at register level.
- Xemu's NV2A approach [ATENÇÃO source; Xemu itself is public] = HLE the
  render pipeline (translate pushbuffer commands + JIT-translate the
  proprietary vertex-shader microcode to GLSL/MSL) while keeping the
  state machine register-accurate. For Zeebo this is simpler: fixed-
  function GLES 1.1 has no custom shader ISA, so a straight GL-call
  translation suffices — no shader-microcode JIT needed.

---

## 6. C++ toolkit (Qwen suggestions) [ATENÇÃO — all unverified taste]

std::span/mdspan (framebuffers, pushbuffers), std::flat_map (soft-TLB /
MMIO tables), std::expected (MMU faults without exceptions), std::jthread
(threaded execution); Dear ImGui for API-call visualization;
Capstone/Keystone/Zydis for disasm/asm tooling. Reasonable modern-C++
choices; none Zeebo-specific. We already use **capstone** for RE
(research/tools/*.py). [CONF for capstone]

---

## 7. Prior-art reading list (papers) [ATENÇÃO source — titles real]

- Dynamo (PLDI 2000) — trace caching / fragment linking.
- FX!32 (IEEE Micro 1998) — profile-directed x86→Alpha translation.
- "QEMU, a Fast and Portable Dynamic Translator" (USENIX 2005) — TCG IR.
- "Efficient Memory Virtualization for Cross-ISA System Mode Emulation"
  (ACM VEE 2014) — softMMU/TLB design.
- Plus DynamoRIO, Unicorn (reference, not a dependency), Zink (GL→Vulkan).

These are standard dynarec/DBT literature; relevant only if the project
ever commits to a bespoke JIT (see §3 recommendation against that).

---

## Decisions feeding Phase 6 (the engineering gate)

1. **CPU = interpreter-first.** Proven by zeebulator; games are not
   CPU-bound. [CONF]
2. **If JIT ever needed → dynarmic** (ARMv6-capable, Infuse-validated),
   not a bespoke JIT — unless a research-JIT is an explicit goal, then
   mirror Citra's ARMv6 backend. [CONF + PRIOR-ART]
3. **GPU = HLE GLES 1.1 → host GL/Vulkan**, no Adreno LLE, no shader
   JIT (fixed-function). [CONF]
4. **MMU/CP15 = not emulated** for the game path (HLE at AEE boundary).
   [CONF]
5. AOT-for-.mod and a custom IR are recorded design options, explicitly
   UNVERIFIED, deferred. [ATENÇÃO]
