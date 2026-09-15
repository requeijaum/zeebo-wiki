# logs

## loader-zeebulator (61s)

Zeebulator loads GGZ/BAR/MIF files by emulating the BREW API surface within its high‑level HLE layer rather than loading any copyrighted firmware or BIOS.
This approach follows the design principle of cleanly reimplementing the BREW OS APIs, as described in the source document.  

Resposta: Carrega GGZ/BAR/MIF via emulação da API do BREW | FONTE (/home/rafaelfrequiao/projects/zeebulator/research/sources/zeebulator.md) | <fato>

## brew-zeebulator (39s)

Resposta: Zeebulator reimplements the entire BREW API surface in high‑level emulation rather than emulating the SoC at the hardware level — which also means no copyrighted firmware/BIOS is required | `FontE (/home/rafaelfrequiao/projects/zeebo-emulator/research/sources/zeebulator.md, trechos relevantes): ...`

## brew-zeemu (60s)

**Zeemu covers the following BREW interface modules (10):**  
1. BrewMediaPCM  
2. BrewAudio  
3. BrewSound(Player)  
4. Brew3D  
5. Brew3DModel  
6. BrewMicro3D  
7. BrewGL  
8. BrewEGL  
9. BrewQXGL (+Dispatch/Draw)  
10. BrewNet  

*Source: research/sources/2026-08-31_zeebulator-vs-zeemu-hle-coverage.md*  

Resposta: Zeemu covers the following BREW interface modules (10): BrewMediaPCM, BrewAudio, BrewSound(Player), Brew3D, Brew3DModel, BrewMicro3D, BrewGL, BrewEGL, BrewQXGL (+Dispatch/Draw), BrewNet | Fonte: research/sources/2026-08-31_zeebulator-vs-zeemu-hle-coverage.md

## infuse-status (44s)

**Resposta:** Os jogos que o Infuse executa na tela principal (boot‑to‑menu) são:

- Double Dragon  
- Crash Nitro Kart 3D  
- Zeebo Family Pack (– jogos comerciais)  
- Asphalt Urban GT 2/3/3D (+Multiplayer)  
- Kingdom Hearts V‑Cast  
- NFS Carbon: Own the City  
- Turma da Mônica  

e, além disso, cerca de 20 títulos do Zeebo que iniciam a inicialização mas ainda não entram no menu (por exemplo, *Tekken 2*, *Quake*, *Rally Master Pro*, *Zuma's Revenge*, *Ultimate Chess 3D*, *RE4: Zeebo Edition*, *Pac‑Mania*, *Toy Raid*, *Zenonia* – quase completos; *Quake II* funciona com som intermitente; e o jogo *Reckless Racing / Raging Thunder II / Armageddon Squadron* sofre corrupção de texturas e ausência de som (problema de memória em investigação).  

| Fonte |
|-------|
| tuxality.net project page (última modificação 2026‑01‑29), Emulation General Wiki/Infuse page, crashynews dev logs |

## oem-zwheel (37s)

Zeebulator models the guest's own sound‑channel object graph, causing the HLE trampoline to store a real MediaHle object that is dereferenced at PLAY, but Release zeroes +8 so vtable[6] becomes NULL.
This specific media playback lifecycle defect was identified in Phase 1 of the research and is documented in the source comparison between Zeebulator and Zeemu HLE coverage (2026-08-31).  
Resposta: Zeebulator models the guest's own sound‑channel object graph, causing the HLE trampoline to store a real MediaHle object that is dereferenced at PLAY, but Release zeroes +8 so vtable[6] becomes NULL | The source comparison between Zeebulator and Zeemu HLE coverage (2026-08-31).

## ggz-formato (43s)

ggzbrewtools is a full clone of Tuxality’s GGZ packer/unpacker for the BREW and Zeebo platforms (supporting DMC Dante x Vergil, Sonic BREW, and Double Dragon). It is implemented in C++17 with Boost libraries.
| research/sources/ggzbrewtools

## zeeno-status (30s)

O estado atual do Zeeno é monitor, sem URL de repositório disponível até 31/08/2026. Ele foi anunciado como projeto aberto e planejado para ser publicado no GitHub quando em melhor condição (FONTE).  
Resposta: O estado atual do Zeeno é monitor, sem URL de repositório disponível até 31/08/2026. Ele foi anunciado como projeto aberto e planejado para ser publicado no GitHub quando em melhor condição | Fonte: FONTE.

## runtime-brew (50s)

The BREW platform loads its modules via the AEE’s AEEMod_Load function, which registers a module’s creation callback; objects are instantiated through the COM‑like interface using ISHELL_CreateInstance with a 32‑bit ClassID declared in the project’s .bid file; and BREW runs as an event‑driven loop that continuously re‑schedules timers and callbacks (e.g., via ISHELL_SetTimer or AEECallback), returning control to the AEE after each frame.  
Resposta: O ciclo de vida do BREW envolve carregamento do módulo, criação de objetos e loop de eventos com temporizadores; | Fonte (/home/rafaelfrequiao/projects/zeebx-emu/docs/02-plataforma-brew.md, trechos relevantes)

## abi-eventos (43s)

**Valores exatos dos eventos e tamanho estrutural**

- `EVT_APP_START` = **0**  
- `EVT_APP_STOP` = **0x01** (valor de 1)  

- Estrutura **`AEERect`** ocupa **8 bytes** (4 offsets de 2 bytes cada: x, y, dx, dy).  

*Fontes:* valores extraídos do cabeçalho `AEEEvent.h` da plataforma BREW 1.0.4.601 (`platform/system/inc/AEEEvent.h`) e confirmados contra o SDK oficial (documentação do Zeebo‑MPSDK‑7.12.5).  

Resposta: `EVT_APP_START = 0; EVT_APP_STOP = 0x01; tamanho de AEERect = 8 bytes | fonte: documento AEEEvent.h da plataforma BREW 1.0.4.601, extraído via reverse‑engineering do Zeebo |

## sdk-headers (69s)

AEEShell.h — research/docs/sdk-extract/BrewMPSDK-7.12.5/.../platform/system/inc/  
AEEStdLib.h — mesma diretório  
AEEISysTimer.h — mesma diretório  
AEE.h — mesma diretório  

Resposta: Os cabeçalhos AEE são AEEShell.h, AEEStdLib.h, AEEISysTimer.h e AEE.h — CONTRATO de API, texto público; repositório research/docs/sdk-extract/BrewMPSDK-7.12.5/.../platform/system/inc/ | Extração do README da brew-sim-recon
