# HW L4e/OKL4 Syscall ABI [CONF via LLE `docs/l4e-syscall-abi.md`]
- Kernel: L4e/OKL4 2.1.1 (Pistachio-embedded) + REX (AMSS/APPS strings). [CONF]
- Real ABI (RefMan N1 rev2 C.2): syscall = **`bl` to a KIP link** (~0xFE00..), NOT `svc #imm`.
  MR0-5 = r3-r8; UTCB at 0xFF000FF0; r8-r12 clobbered.
- Numbers (syscalls_asm.h): ipc 0x0, thread_switch 0x4, thread_control 0x8, exch_regs 0xc,
  schedule 0x10, map 0x14, space 0x18, cache 0x20, security 0x24, lipc 0x28, platform 0x2c,
  space_switch 0x30, mutex 0x34, mutex_control 0x38, interrupt 0x3c, cap 0x40, memcopy 0x44.
- The firmware `mvn sp; svc #0x14` thunk is likely a shim (SP/SW bases mismatch: SYSBASE 0xffffff00, SWIBASE 0x1400).
  Audit correction 09-06 — the old "imm=syscall" reading is REFUTED.
