# Hardware: MSM7201A Register Map

The MSM7201A has no public datasheet. Everything on this page comes from running
the bootloader under emulation and modelling each register until the boot
advanced, so the values are what the boot code expects to read back, not what a
vendor document states.

## Interrupt controller, 0xc0000000

| Offset | Access | Value | Meaning |
|---|---|---|---|
| +0x10 | write | 0 | clear or disable |
| +0x14 | write | 0 | clear or disable |
| +0xb0 | write | 0xffffffff | mask all |
| +0xb4 | write | 0xffffffff | mask all |

Initialisation only, with no polling. Plain sticky registers are sufficient. The
kernel later programs individual sources; the watchdog and timer interrupts are
the ones that matter for scheduling.

## Clock and PLL controller, 0xc0100000

| Offset | Behaviour |
|---|---|
| +0x100 | clock source configuration, programmed in stages: 0x640000, 0x640010, 0x64001f, 0x64101f, 0x64171f |
| +0x104 | handshake and status for +0x100; boot writes 2, reads 2, writes 3, reads 3 |
| +0x008 | enable latch; read 0, then write 1 |

The handshake register must reflect the written value. If it does not, the PLL
programming loop never converges and the boot hangs before any driver loads.

## Multi-channel block, 0xa9700000

Status registers use a per-channel stride of 4.

| Offset | Meaning |
|---|---|
| +0xe10 + channel*4 | status; bit 0 is READY and must read 1, bit 1 is ERROR and must read 0 |
| +0xc50 + channel*4 | secondary status |
| +0xf10 + channel*4 | configuration and acknowledge; boot writes 2 |

The correct return value is 0x1. Returning 0xffffffff trips the ERROR bit and the
boot aborts, which is a useful reminder that reads of undocumented status
registers are usually bitfield tests, not opaque values.

## Boot failure sink

Address 0xc30 contains a branch to itself. Reaching it means a boot check failed
before any driver loaded.

Two properties make it useful rather than merely annoying:

| Property | Consequence |
|---|---|
| The sink is reached by a branch, not by a fault | the failure is a failed check, not a crash |
| Each modelled register pushes the halt later | a change in the halt address proves the model change had an effect |

The halt address is therefore the primary progress metric for early boot work.
Advancing it from 0xc30 to the next stage is evidence; a run that reaches the same
address twice, with no other observable change, is not.

A second, subtler lesson: reads of undocumented status registers are usually
bitfield tests rather than opaque values. A model that returns all ones passes a
"non-zero means ready" check and trips an error bit elsewhere. Returning the
smallest plausible value, such as a single ready bit, is the safer default.

## Kernel bring-up peripherals

| Block | Base | Notes |
|---|---|---|
| VIC | 0xc0000000 | two words for enable and pending, acknowledge, round-robin delivery |
| UART1 | 0xa9a00000 | TX, IMR, RX |
| UART2 | 0xa9c00000 | kernel console on ttyMSM2, interrupt 11 |
| UART3 | 0xa9e00000 | TX, IMR, RX |
| GPT/DGT | VA 0xe0001000, PA 0xc0100000 | clock event source, tick rate 100 Hz |
| MDP | 0xaa200000 | interrupt enable, status and clear; DMA completes immediately; interrupt 19 |
| TVENC | 0xaa400000 | composite video encoder |
| USB HS EHCI | 0xa0800000 | capability registers at 0x000 and 0x100, CAPLENGTH 0x40 |

Two details that cost time if missed:

- Interrupt delivery must round-robin. Serving strictly in numeric order starves
  the MDP interrupt behind the timer, and the display stops updating while the
  kernel keeps running.
- The EHCI port status register must report a connected, enabled device, and the
  port reset must complete on read. Otherwise the host controller driver never
  binds and no input device appears.

## Storage and memory management

| Item | Value |
|---|---|
| NAND geometry | 65536 pages |
| NAND identify | FETCH_ID returns 0x5580b1ad in the model |
| NAND read | PAGE_READ matches byte for byte against a real dump |
| MMU entries | 150 real ARM11 virtual to physical mappings |

MMU layout observed: peripherals at 0xc0000000, RAM identity mapped, and coarse
entries in the 0xb0xxx range resolving into 0x100a3xxx. A translation table taken
from hardware removes the guesswork that usually dominates early boot work.

## Dual-core layout

| Core | Role | Architecture | Clock |
|---|---|---|---|
| Core 0 | applications processor | ARM1136J-S, ARMv6, ARM and Thumb-1 | 528 MHz |
| Core 1 | modem and baseband | ARM926EJ-S running AMSS on REX | 256 MHz |

Game code runs on core 0 only. Core 1 matters for firmware boot and for services
that titles call indirectly, such as network and telemetry.

## Timer behaviour

| Property | Value |
|---|---|
| Tick source | general purpose timer block |
| Kernel tick rate | 100 Hz in the Linux bring-up harness |
| Guest uptime query | monotonic, advanced by the runtime |
| Frame cadence in titles | 16 ms timer re-armed by the title |

The uptime query deserves care. If it never advances, titles that use it as a
frame clock spin forever. If it advances with wall-clock time instead of emulated
time, titles run at the wrong speed.

Evidence: register behaviour from bootloader bring-up under emulation; MMU and
NAND values from hardware dumps; peripheral map from a Linux 3.4.113 bring-up
harness.
