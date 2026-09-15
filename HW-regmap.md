# HW MSM7201A — Empirical Map (LLE) [CONF via zeebo-lle]
Source: `zeebo-lle/docs/register-map.md` (APPSBL boot under Unicorn; values = what the bootloader EXPECTS).
- **0xc0000000** VIC-like: +0x10/+0x14 W0 clear, +0xb0/+0xb4 mask all. Init only.
- **0xc0100000** clock/PLL: +0x100 staged config, +0x104 handshake (sticky), +0x008 enable latch.
- **0xa9700000** multi-channel block: status +0xe10+ch*4 (bit0 READY=1, bit1 ERROR=0 → 0x1),
  +0xc50 secondary, +0xf10 config/ack. Channel 1 stalls boot (halt 0xc30).
- **Halt 0xc30** = `b 0xc30`, the bootloader's error/abort sink.
- Real MMU: 150 ARM11 VA→PA entries (`tools/arm11_mmu.py`); NAND 65536 pages (`tools/nand_controller.py`).
## Linux 3.4.113 harness (`docs/linux-boot.md`) [CONF via LLE]
- VIC 0xc0000000 (2-word enable/pending, round-robin irq19 MDP vs irq7 timer).
- UART1/2/3: 0xa9a00000/0xa9c00000/0xa9e00000; `ttyMSM2` = console (irq 11), host keyboard into RX.
- GPT/DGT: VA 0xe0001000 (PA 0xc0100000), HZ=100. MDP 0xaa200000 (irq 19, instant DMA).
- TVENC 0xaa400000 (composite). EHCI 0xa0800000 (CAPLENGTH 0x40, PORTSC HS attached).
- State: BusyBox shell + /proc, 1x2 SDL2 (UART|framebuffer); HID (keyboard) pending.
