# HW MSM7201A — mapa empírico (LLE) [CONF via zeebo-lle]
Fonte: `zeebo-lle/docs/register-map.md` (boot APPSBL sob Unicorn; valores = o que o bootloader ESPERA).
- **0xc0000000** VIC-like: +0x10/+0x14 W0 clear, +0xb0/+0xb4 mask all. Init only.
- **0xc0100000** clock/PLL: +0x100 stage-config, +0x104 handshake (sticky), +0x008 enable latch.
- **0xa9700000** bloco multi-canal: status +0xe10+ch*4 (bit0 READY=1, bit1 ERROR=0 → 0x1),
  +0xc50 secundário, +0xf10 config/ack. Canal 1 trava boot (halt 0xc30).
- **Halt 0xc30** = `b 0xc30`, sink de erro do bootloader.
- MMU real: 150 entradas ARM11 VA→PA (`tools/arm11_mmu.py`); NAND 65536 págs (`tools/nand_controller.py`).
- Ver `docs/linux-boot.md` (VIC/UART/GPT/MDP/TVENC/EHCI no harness Linux 3.4.113).
## Harness Linux 3.4.113 (`docs/linux-boot.md`) [CONF via LLE]
- VIC 0xc0000000 (2 palavras enable/pending, round-robin irq19 MDP vs irq7 timer).
- UART1/2/3: 0xa9a00000/0xa9c00000/0xa9e00000; `ttyMSM2` = console (irq 11), RX injeta teclado host.
- GPT/DGT: VA 0xe0001000 (PA 0xc0100000), HZ=100. MDP 0xaa200000 (irq 19, DMA imediato).
- TVENC 0xaa400000 (composto). EHCI 0xa0800000 (CAPLENGTH 0x40, PORTSC HS conectado).
- Estado: shell BusyBox + /proc, SDL2 1x2 (UART|framebuffer); HID (teclado) pendente.
