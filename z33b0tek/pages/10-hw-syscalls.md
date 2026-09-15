# Hardware: L4e kernel syscall ABI

The Zeebo firmware runs OKL4 2.1.1 (Pistachio-embedded) with REX on top.

## Calling convention

The authoritative L4-embedded reference manual defines the entry mechanism:

- A system call is invoked by a branch to a link address inside the kernel
  interface page, in the address range around 0xfe000000.
- The call is not invoked by an SVC immediate.
- Message registers MR0 to MR5 map to r3 to r8.
- The link register holds the return address.
- UTCB and local ID are read from a 32-bit load at 0xff000ff0.
- r8 to r12 are clobbered by most calls.

## Syscall numbers

| Number | Name |
|---|---|
| 0x00 | ipc |
| 0x04 | thread_switch |
| 0x08 | thread_control |
| 0x0c | exchange_registers |
| 0x10 | schedule |
| 0x14 | map_control |
| 0x18 | space_control |
| 0x20 | cache_control |
| 0x24 | security_control |
| 0x28 | lipc |
| 0x2c | platform_control |
| 0x30 | space_switch |
| 0x34 | mutex |
| 0x38 | mutex_control |
| 0x3c | interrupt_control |
| 0x40 | cap_control |
| 0x44 | memory_copy |

## The SVC thunk

Some firmware paths use a compact thunk:

```
mov  ip, sp
mvn  sp, #imm        ; sp becomes 0xffffffxx
svc  #imm
```

The kernel dispatches on the SVC immediate, and the SP value carries a magic
check. In the user-side L4 library the pattern is instead:

```
mov  sp, #SYSNUM(name)   ; 0xffffff00 + number
swi  SWINUM(name)        ; SVC immediate 0x1400 + number
```

Bases differ between the two forms: the library uses SYSBASE 0xffffff00 and
SWIBASE 0x1400, while firmware thunks observed in the dump do not match either
base value. Treat the observed thunk as a shim over the real KIP-link calls.

## Practical rule

To recover the real syscall set from a firmware image, read the kernel interface
page and follow the branch targets the kernel actually exposes. Do not infer the
syscall table from SVC immediates.
