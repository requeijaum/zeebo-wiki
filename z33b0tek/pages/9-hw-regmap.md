# Hardware: MSM7201A register map

Empirical map, derived from bootloader execution traces. The MSM7201A has no
public datasheet, so every value below is what the boot code expects to read
back, not what a vendor document states.

## Interrupt controller, 0xc0000000

- +0x10, +0x14: write 0 to clear.
- +0xb0, +0xb4: write 0xffffffff to mask all.
- Initialisation only, no polling. Sticky registers are sufficient.

## Clock and PLL controller, 0xc0100000

- +0x100: clock source configuration, programmed in stages:
  0x640000, 0x640010, 0x64001f, 0x64101f, 0x64171f.
- +0x104: handshake and status for +0x100. Boot writes 2, reads 2, writes 3,
  reads 3. The register must reflect the written value or the loop never
  converges.
- +0x008: enable latch. Read 0, then write 1.

## Multi-channel block, 0xa9700000

Status registers use a per-channel stride of 4.

- +0xe10 + channel*4: status. Bit 0 is READY and must read 1. Bit 1 is ERROR and
  must read 0. The correct return value is 0x1; returning 0xffffffff trips the
  error bit.
- +0xc50 + channel*4: secondary status.
- +0xf10 + channel*4: configuration and acknowledge. Boot writes 2.

## Boot failure sink

- Address 0xc30 contains a branch to itself. Reaching it means a boot check
  failed. Each correctly modelled register pushes the halt later, which makes
  the halt address a usable progress metric.

## Kernel bring-up peripherals

From a Linux 3.4.113 boot harness:

| Block | Base | Notes |
|---|---|---|
| VIC | 0xc0000000 | two words for enable and pending, acknowledge, round-robin delivery |
| UART1 | 0xa9a00000 | TX, IMR, RX |
| UART2 | 0xa9c00000 | kernel console on ttyMSM2, IRQ 11 |
| UART3 | 0xa9e00000 | TX, IMR, RX |
| GPT/DGT | VA 0xe0001000, PA 0xc0100000 | clock event, HZ 100 |
| MDP | 0xaa200000 | interrupt enable, status and clear, DMA completes immediately, IRQ 19 |
| TVENC | 0xaa400000 | composite output |
| USB HS (EHCI) | 0xa0800000 | capability registers at 0x000 and 0x100, CAPLENGTH 0x40 |

## Storage and memory management

- NAND geometry: 65536 pages. Controller self-test passes with FETCH_ID
  0x5580b1ad and byte-exact PAGE_READ.
- MMU: 150 real ARM11 VA to PA entries recovered from a hardware dump.
  Peripherals map at 0xc0000000, RAM is identity mapped, and coarse entries
  0xb0xxx resolve to 0x100a3xxx.

## Dual-core layout

| Core | Role | Clock |
|---|---|---|
| Core 0 | applications processor, ARM1136J-S | 528 MHz |
| Core 1 | modem and baseband, ARM926EJ-S running AMSS on REX | 256 MHz |

Game code runs on core 0 only. Emulating core 1 is required for firmware boot,
not for running titles.
