# Hardware: L4e Kernel Syscall ABI

The firmware runs OKL4 2.1.1, from the L4e lineage, with REX on top. Titles never
call the kernel directly, but firmware bring-up does, and the calling convention
is unusual enough that guessing wastes days.

## Calling convention

From the authoritative L4-embedded reference manual:

| Item | Detail |
|---|---|
| Trigger | a branch to a link address inside the kernel interface page |
| Address range | around 0xfe000000 |
| Not the trigger | an SVC immediate, in the reference ABI |
| Message registers | MR0 to MR5 map to r3 to r8 |
| Return address | held in the link register |
| Thread control block | pointer read from 0xff000ff0 |
| Clobbered | r8 to r12 after most calls |

The manual is explicit that any instruction which branches to the right target
works, as long as the return address is in r14. That is why the convention is
described as a call into the kernel interface page, not as a trapped instruction.

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

Numbers are not contiguous: 0x1c is missing from the table, so an implementation
that enumerates by index rather than by value will be off by one from that point
on.

## IPC and LIPC

| Call | Use |
|---|---|
| ipc | synchronous message send and receive between threads |
| lipc | long IPC, for messages that do not fit in the message registers |
| thread_switch | explicit yield |
| schedule | create or configure a thread |
| exchange_registers | inspect or modify another thread's registers |

Inter-processor communication on this SoC uses these calls between the two cores
and the DSP, which is why firmware boot depends on them while title execution
does not.

## The SVC thunk observed in firmware

```
mov  ip, sp
mvn  sp, #imm
svc  #imm
```

| Component | Library form | Firmware form |
|---|---|---|
| syscall number in SP | 0xffffff00 + number | 0xffffffxx from mvn |
| syscall number in immediate | 0x1400 + number | immediate as written |
| Dispatch | on the immediate | on the immediate |

The bases do not match the library form, so the thunk seen in firmware is best
treated as a shim over the real kernel interface page calls rather than as the
documented ABI. Trap it, log it, and confirm against the kernel interface page
before building behaviour on it.

## Practical rule

To recover the real syscall set from a firmware image, find the kernel interface
page and follow the branch targets the kernel actually exposes. Do not infer the
table from SVC immediates: the immediates in the image are the least reliable
source available.

Evidence: calling convention and syscall numbers from the L4-embedded reference
manual and from the kernel's own headers. Thunk shape from disassembly of the
firmware image.
