> Origem: `projects/zeebo-emulator/research/sources/2026-09-01_prior-art-experimental-emulators.md` (cópia integral 15/09; origem manda, wiki espelha).

# Prior-art: emuladores experimentais / recomp (levantamento 2026-09-01)

Reconhecimento de técnicas a partir da onda recente de emuladores experimentais
(muitos AI-assisted) e projetos de recompilação. Disparado pela pista do Rafael:
SuperPSX (frangar) — dynarec MIPS→MIPS de PS1 em PS2. Todas as afirmações têm URL.
Cross-check obrigatório de qualquer claim de README AI-assisted contra código/commits.

## SuperPSX — o caso mais próximo do DKWDRV

- Repo: https://github.com/frangarcj/superpsx — MIT, C99 (~20K linhas), WIP 2026,
  fortemente AI-assisted (Copilot). Autor: Francisco José García García ("frangar",
  dev homebrew PS2/Vita/PSP conhecido). Doc mais rica: `README.ai.md`.
- NÃO é recomp estático: é um **EMULADOR** de PS1 rodando NATIVO no EE (R5900 ~294MHz)
  com um **dynarec JIT MIPS→MIPS** (~5.5K LOC). Explora que o R5900 é superset do
  R3000A (MIPS I) → traduz instruções guest quase 1:1 para o host.
- Técnicas medidas (com commits):
  - **Register pinning**: 10 GPRs do PSX fixados em registradores físicos do EE
    (v0→T3, v1→T4, a0→T5, ... ra→S5), write-through pra shadow `cpu.regs[]`.
    Infra: S0=cpu ptr, S1=RAM base, S2=cycles_left, S3=máscara 0x1FFFFFFF. Slots
    dinâmicos T0/T1/T2 por frequência. "O maior ganho isolado do JIT."
  - **Máscara de endereço** S3=0x1FFFFFFF espelha o mirroring KUSEG/KSEG do PSX;
    fast-path com range-check + trampolines cold-path; otimização "SMRV" pula o
    range-check quando o reg sabidamente contém RAM base.
  - **Block cache + direct linking + hash dispatch**; região fixa de trampolines
    (JR RA lento, C-call cheia flushando os 10 pinned, C-call lite flushando 5) e
    blocos JIT a partir do offset 144.
  - **SMC**: page-tracking em dynarec_cache.c invalida blocos de páginas sujas.
  - **GTE (COP2)**: reimplementado — parte HLE em C (gte.c ~2K linhas), parte
    **acelerado no VU0 do EE em macro mode** (RTPS/RTPT commit cdf3a2d, MVMVA 3
    matrizes fb61e84, pipeline de luz bdb8725). 22 comandos GTE, validado contra
    ps1-tests gte-fuzz.
  - **GPU GP0/GP1 → PS2 GS**: tradução de primitivas com state tracking lazy;
    layout de VRAM da GS bem pensado (cache de textura O(1) page-mapped, CLUT
    round-robin com CLD=4 pra pular reloads redundantes).
  - **SPU**: software (spu.c), batch ADSR cortou 93.5% do tempo. [INCERTO se usa
    SPU2 do PS2 por HW — aparenta ser 100% software].
  - **DCE por liveness backward** (~5-10%), shadow VRAM upload eliminando readback
    de 1MB.
  - Perf (Crash): ~55% da velocidade; JIT = 75% do frame time (gargalo).
- Toolchain: C99 + CMake, ps2dev/PS2SDK; roda em PCSX2 e PS2 real; precisa BIOS.
- Testes: 48 testes de acurácia do JaCzekanski/ps1-tests + comparação pixel-a-pixel
  de screenshots de VRAM contra referência de hardware real.

### Por que importa pro DKWDRV (PS2 Deckard, R5900 + PPC-IOP)
SuperPSX é o prior-art PÚBLICO mais próximo de rodar código guest R3000A no R5900.
Transferível: (1) exploração ISA-superset — a maioria das ops int/branch/load-store
do R3000A traduz 1:1, só precisando de máscara de endereço e delay-slots; (2) register
pinning com write-through; (3) **GTE no VU0 em macro mode** — diretamente relevante
porque o backward-compat real do Deckard/PS2 também apoia GTE do PS1 no EE+VU0;
(4) mapeamento GP0→GS e layout de VRAM; (5) SMC page-tracking.
DIVERGÊNCIA honesta: DKWDRV faz RE do caminho OFICIAL da Sony (PPC-IOP "Deckard" +
TBIN fechado), enquanto SuperPSX é dynarec clean-room de terceiros. As mecânicas de
tradução e a estratégia GTE-no-VU0 são referência forte, mas o alvo é diferente.

## A onda de recompilação estática (MIPS/PPC/68k → C)

- **N64Recomp** https://github.com/N64Recomp/N64Recomp (8k★) — recomp estático
  MIPS→C: cada função MIPS vira função C sobre um struct `ctx` de registradores
  (`addiu $r4,$r4,0x20` → `ctx->r4 = ADD32(ctx->r4,0x20)`); `jal`→chamada C real;
  delay-slot por duplicação de instrução. Precisa de metadata de símbolos (de um
  decomp/disasm ELF) + um **TOML** que faz stub/skip/patch de funções. Sem
  interpretador nem JIT em runtime.
- **Zelda64Recomp** https://github.com/Zelda64Recomp/Zelda64Recomp — pipeline
  completo shippável; `us.rev1.toml` é o exemplo canônico de overlay/stub/patch.
- **RT64** https://github.com/rt64/rt64 — renderer HLE de N64 separado da CPU:
  prova que projetos recomp separam CPU recompilada de uma camada gráfica HLE
  escrita à mão (mesmo split que BREW precisaria).
- **UnleashedRecomp** https://github.com/hedge-dev/UnleashedRecomp +
  **MarathonRecomp** — provam o padrão N64Recomp transferindo pra **PowerPC**
  (Xbox 360) via XenonRecomp: endianness + tradução da unidade vetorial VMX128.
  Datapoint same-family em outro RISC big-endian.
- **ido-static-recomp** https://github.com/decompals/ido-static-recomp — recompila
  o compilador IRIX IDO; prova que recomp funciona pra código MIPS user-mode
  genérico, não só jogos.
- **jamulator** https://github.com/andrewrk/jamulator — recomp estático NES→LLVM IR;
  o write-up documenta honestamente o problema de SMC/indirect-jump que força
  fallback híbrido estático+interpretador. [INCERTO] sem manutenção.
- **m2c** https://github.com/matt-kempster/m2c — decompilador MIPS/PPC asm→C que
  alimenta a metadata dos projetos de decomp.

## Interpreters GERADOS por código — SNESticle (a 3ª via)

- **SNESticle / SNESticleRevive** https://github.com/ReyFxck/SNESticleRevive —
  o SNES emu do Icer Addis (iaddis), famoso por ter ido ESCONDIDO dentro do
  Fight Night Round 2 (GameCube, 2005) rodando Super Punch-Out!!; extraído por
  RE da comunidade em 2022, fonte liberada MIT. Alvos: PS2 (MIPS), Dreamcast,
  Win32. Multi-plataforma via framework de abstração de hardware `Gep` (core
  separado do backend).
- **Técnica-núcleo — ISA declarativa → codegen por plataforma.** Os 256 opcodes
  do 65816 e do SPC700 NÃO são escritos à mão. O ISA vive em XML
  (`pd65816.xml`/`pdspc700.xml`); XSL (`pd65816.xsl`) + geradores JS emitem:
  - `asm_c.js` → C (Win32/genérico)
  - `asm_mips.js` → **assembly MIPS otimizado pro EE do PS2**, mapeando os
    registradores do 65816 direto em registradores físicos MIPS (register
    allocation no gerador, não no programador)
  - Uma ÚNICA fonte de verdade: corrigir o ADC no XML conserta as 8 variantes
    (immediate/absolute/indexed/etc.) de uma vez.
  É uma **3ª via** entre interpretador-à-mão e JIT: um *interpretador gerado*
  onde a spec é a fonte da verdade e o código otimizado por host é emitido.
  Relevância pro Zeebo: dynarmic já cobre "emitir código de host"; o que
  SNESticle adiciona é a **disciplina de spec-única** (mesma lição do vibe-GB:
  LLM vai bem em ISA table-driven porque o decode é data). Se algum dia for
  preciso um fallback ARM11→ARM64 same-family "gerado" (em vez de dynarec
  cross-ISA), o padrão XML/XSL→asm é o template. Também documentado: memória
  bancada `SNCpuBankT` (256 bancos × 64KB).
- **Método "catch-up" (CPU/PPU)**: rodar a CPU à frente e só "alcançar" a PPU
  quando um evento exige (elimina o overhead de trocar CPU↔PPU a cada ciclo).
  Clássico (citado na thread psx-place de full-speed SNES no PS2); o tick-loop
  do Zeebo já faz algo parecido implicitamente.
- **Wii**: Wii64/WiiSX (N64/PS1 no Wii, PPC Broadway) usam **dynarec MIPS→PPC**
  tradicional — confirma o padrão, nada novo vs dynarmic. SNES9x GX / FCE Ultra
  GX / Genesis Plus GX são ports C via libogc, sem técnica inédita.
- **N64Recomp "single file output mode"**: recompilar o binário UMA vez e iterar
  os patches (TOML) sem re-rodar o recompilador — mesmo espírito da camada de
  quirks por-título (core/brew/compat/) com patch-por-dado em vez de
  re-recompilar.

## HLE moderno — prior-art direto pro Zeebo/BREW

- **Panda3DS** https://github.com/wheremyfoodat/Panda3DS — **mesmo guest ARM11
  (ARMv6) do Zeebo**. HLE do OS do 3DS: handlers de SVC e objetos de "service"
  como classes C++ despachadas por nome/command-header, com log gracioso de
  "service não implementado" pra o boot prosseguir. Irmão arquitetural mais
  próximo de um core HLE de BREW — estudar a integração dynarmic e a tabela de
  dispatch direto.
- **dynarmic** https://github.com/lioncash/dynarmic — o JIT de ARM que já estava na
  mesa pro Zeebo. IR próprio, register allocator, backend xbyak x64; interface de
  callbacks (mem read/write, hooks de SVC/syscall) = **exatamente a costura pra
  HLE de BREW**. Forkado por Vita3K/Panda3DS/Ryujinx = testado em batalha.
- **Vita3K** https://github.com/Vita3K/Vita3K — HLE por **NID**: cada função de
  SDK/OS é um hash NID; o loader resolve a import stub table do jogo e redireciona
  cada NID pra um handler nativo C++ (ou stub logger). Analogia direta às
  entradas numeradas de IShell/interfaces do BREW → construir uma "tabela NID"
  de ordinais BREW→handlers nativos.
- **Ryujinx** https://github.com/Ryujinx/Ryujinx — arquitetura madura de HLE de
  serviços IPC: base `IpcService`, dispatch por command-id, crescimento
  incremental "stub then implement" (commits literalmente "More stubs"). A
  metodologia pragmática pra superfície grande de API do BREW.
- **vixl** https://github.com/Linaro/vixl / **xbyak** https://github.com/herumi/xbyak
  — emitters. vixl dá caminho **ARM11→ARM64 same-family** (muita op guest mapeia
  ~1:1 no host ARM), meio-termo entre interpretador e dynarec cross-ISA — relevante
  se algum dia o Zeebo rodar em handheld ARM64.
- **unicorn / QEMU TCG** — cores CPU multi-ISA de fallback/referência de design.

### "Vibecoded" (AI-assisted) — o que dá pra concluir
- vibe-gameboy-emulator https://github.com/djkf/vibe-gameboy-emulator — interpretador
  de Game Boy feito majoritariamente via LLM. Lição: LLMs vão bem em ISAs
  table-driven (decode/dispatch de opcode), mas o valor/risco está na VERIFICAÇÃO
  contra test-ROMs conhecidas. [INCERTO] correção/completude.
- SuperPSX é o exemplo sério do gênero: AI-assisted mas com histórico de commits de
  otimização concreto e suíte de testes de hardware — mostra que AI-assisted +
  verificação rigorosa produz coisa real.

## Síntese acionável (o que "roubar")

Para o **Zeebo (HLE-first)** — nada disso muda a decisão interpreter-first, mas:
1. Adotar o modelo **NID/ordinal→handler** do Vita3K pra formalizar a HLE de BREW
   (hoje o game_probe tem dispatch, mas uma tabela explícita ordinal→handler com
   stub-logger tornaria o "stub-then-implement" do Ryujinx sistemático — encaixa
   direto na nossa camada core/brew/compat/ nova).
2. **Panda3DS é leitura obrigatória**: mesmo ARM11 guest. Se um dia trocarmos o
   interpretador por JIT, dynarmic + o padrão de service-dispatch dele é o caminho
   com menos atrito.
3. A parede do ABD (loop de stub que nunca termina) é exatamente o caso "stub
   retorna default plausível e o app roda em círculo" — o padrão Ryujinx de LOGAR
   todo unimplemented hit e implementar sob demanda é a disciplina certa (e evita o
   risco de inventar semântica: você implementa quando VÊ o app exigir).

Para o **DKWDRV (R5900 + PPC-IOP)**:
1. SuperPSX é o dossiê técnico de referência pra qualquer tradução R3000A→R5900:
   register pinning, máscara de endereço, GTE no VU0. Vale clonar o repo e ler
   dynarec_insn.c / gte.c antes de qualquer tentativa de dynarec.
2. Se algum dia o alvo virar tradução estática do TBIN/IOP em vez de RE do caminho
   oficial, N64Recomp (MIPS→C literal + TOML de stub) e o XenonRecomp (PPC, o
   IOP/PPC do Deckard!) são os dois templates. XenonRecomp especificamente prova o
   padrão em PowerPC, que é a ISA do PPC-IOP do Deckard.

## Fontes (verbatim)
SuperPSX: github.com/frangarcj/superpsx (+ README.ai.md, docs/jit_optimization_roadmap.md);
ps1-tests: github.com/JaCzekanski/ps1-tests.
N64Recomp, Zelda64Recomp, RT64, ido-static-recomp, jamulator, UnleashedRecomp,
MarathonRecomp, m2c, dynarmic, Vita3K, Panda3DS, Ryujinx, unicorn, qemu, xbyak,
vixl, rabbitizer — URLs completas nos dossiês dos subagentes
(~/.hermes/cache/delegation/subagent-summary-{0,1}-20260901_094428_*.txt).
