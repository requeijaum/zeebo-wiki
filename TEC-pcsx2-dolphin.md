> Origem: `/home/rafaelfrequiao/zeebo-lle-pcsx2-dolphin-mem-mmio-boot.md` (cópia integral 15/09; origem manda, wiki espelha).

# PCSX2 e Dolphin — mecanismos de MEMÓRIA / MMIO / BOOT / DEPURAÇÃO aplicáveis ao zeebo-lle

> **LICENÇA**: PCSX2 é GPL-3.0+, Dolphin é GPL-2.0+. Nada aqui deve ser copiado como código.
> Todos os mecanismos abaixo devem ser **REIMPLEMENTADOS do zero** a partir da descrição da
> arquitetura. Os nomes de arquivo/função/campo servem apenas como REFERÊNCIA de leitura humana.

---

## AS 3 RECOMENDAÇÕES DE MAIOR IMPACTO PARA O NOSSO BUG

O nosso bug foi: **duas fontes de verdade de memória divergiram silenciosamente** (Unicorn manteve
buffer antigo, VTLB pegou ponteiro novo após um remap que falhou), e só apareceu 181306 instruções
depois num LDRH de 16 bits que não tinha vigia.

1. **UMA fonte de verdade única para o mapa de memória, consumida pelos DOIS backends.**
   É exatamente o que o PCSX2 faz. O `vtlb` (`pcsx2/vtlb.cpp` + `vtlb.h`) tem UM array `vmap`
   (`VTLBVirtual* vmap`, um slot por página de 4 KB do espaço virtual). Tanto o interpretador
   (`vtlb_memRead<DataType>` / `vtlb_memWrite<DataType>` em vtlb.cpp) quanto o recompilador
   (recVTLB / `vtlb_DynGenReadNonQuad` etc.) leem do **mesmo** `vmap`. Não existe uma tabela
   "do JIT" e outra "do interpretador". No nosso projeto, o Unicorn NÃO deve ter memória própria:
   ele deve ser forçado a ler/escrever pela mesma VTLB/LUT do Dynarmic (via hooks de MMIO do
   Unicorn ou mapeando o Unicorn sobre os mesmos buffers de host). Enquanto houver duas fontes,
   o bug volta.

2. **Remapeamento deve ser atômico e transacional: OU atualiza tudo OU não atualiza nada.**
   O nosso bug foi um remap que "falhou pela metade" — a VTLB avançou, o Unicorn não. O padrão do
   PCSX2 (`vtlb_VMap` / `vtlb_VMapUnmap` / `mmap_ClearCpuBlock`) e do Dolphin
   (`MemoryManager::UpdateDBATMappings`, antes `UpdateLogicalMemory`) é: quando o mapeamento muda,
   **primeiro** desfaz todo o mapeamento antigo, **depois** monta o novo, e **em seguida** invalida
   o JIT afetado. Se o `MapInMemoryRegion` retorna ponteiro diferente do pedido, o Dolphin trata
   como falha explícita (`PanicAlertFmt` + `continue`/`exit`) — nunca segue com estado meio-atualizado.
   Aplicação: envolver o remap num único ponto que, em caso de erro do backend nativo (Unicorn
   `uc_mem_map`/`uc_mem_unmap` retornando != UC_ERR_OK), **aborta a transação inteira** e deixa a
   VTLB inalterada, em vez de aplicar só um dos lados.

3. **Watchpoint de dados por RANGE e por LARGURA, com callback que reporta PC/valor/tamanho.**
   O `TMemCheck` do Dolphin (`Source/Core/Core/PowerPC/BreakPoints.h`, método
   `TMemCheck::Action(system, value, addr, write, size, pc)`) resolve os dois pontos fracos que nos
   pegaram: (a) é **ranged** (`start_address`/`end_address`, `is_ranged`), então cobre um endereço
   independentemente da largura — 8/16/32/64 caem todos no mesmo range; (b) o callback recebe `size`,
   `write`, `value` e `pc`, ou seja, ele **te diz QUEM escreveu** e com que largura. Precisamos de um
   watchpoint desses cobrindo o endereço do LDRH, disparando em qualquer largura, e imprimindo o PC
   do escritor. O nosso bug "só o de 32 bits tinha vigia" é precisamente o anti-padrão que o
   `TMemCheck` ranged elimina.

---

## 1. VTLB / fastmem / lookup table de memória

### 1a. Como o PCSX2 distingue RAM direta de página que exige handler de MMIO

Referência: `pcsx2/vtlb.h` (struct `VTLBVirtual`, `MapData`) e `pcsx2/vtlb.cpp`.

O truque central é **codificar RAM-vs-handler no bit de sinal do ponteiro**, sem branch extra de
lookup de tipo:

- `MapData::vmap` é um array com um slot `VTLBVirtual` por página virtual de 4 KB
  (`VTLB_PAGE_BITS = 12`, `VTLB_VMAP_ITEMS = 4GB / 4096`).
- Cada slot guarda um único `uptr value`. Para páginas de RAM direta, `value` é
  `ponteiro_do_host_da_página - vaddr_base_da_página`; para páginas de MMIO, o `value` tem o
  `POINTER_SIGN_BIT` (bit mais alto) setado, e os bits baixos carregam o ID do handler.
- O teste é `isHandler(vaddr)` = `(sptr)(value + vaddr) < 0`. Ou seja: soma o endereço, e se o
  resultado ficar **negativo** (bit alto), é MMIO; se positivo, é RAM e o próprio resultado
  `value + vaddr` **já é o ponteiro de host** (`assumePtr(vaddr)`). Uma soma e um teste de sinal
  resolvem "é RAM ou MMIO?" e, se for RAM, já dão o ponteiro. Não há segunda tabela.
- Para MMIO, `assumeHandlerGetPAddr(vaddr)` recupera o endereço físico e
  `assumeHandler<Width,Write>()` indexa `RWFT[5][2][128]` — 5 larguras (8/16/32/64/128) × 2
  (read/write) × 128 handlers — para achar o ponteiro de função do handler daquela largura.

Aplicação ao zeebo-lle: adotar exatamente esta representação unificada (ponteiro-com-bit-de-sinal)
para o MSM7201A. Uma LUT por página, um slot, discriminação RAM/MMIO no bit alto. Fazer o Unicorn
consumir essa mesma LUT (via callback de leitura/escrita) elimina a segunda fonte de verdade.

### 1b. Handlers por largura (8/16/32/64/128) — o cerne do nosso bug do LDRH

Referência: `vtlb.h` — `typedef mem16_t vtlbMemR16FP(u32 addr);` e a família R8/R16/R32/R64/R128,
W8..W128; a tabela de despacho `vtlbMemFP<Width,Write>` mapeia cada largura para um `Index` (0..4).
`vtlb_RegisterHandler(...)` e `vtlb_ReassignHandler(...)` (vtlb.cpp, ~linha 685) recebem **um
ponteiro de função por largura**: `r8,r16,r32,r64,r128,w8,w16,w32,w64,w128`. Se algum for NULL, cai
no handler default que dispara `pxFail`/BusError.

Lição direta para nós: **cada região de MMIO deve ter handler para TODAS as larguras**, não só 32.
O nosso LDRH de 16 bits caiu num caminho sem vigia porque o registro só cobria 32 bits. No modelo do
PCSX2 é impossível registrar "só o de 32" e deixar os outros num limbo silencioso — os slots não
preenchidos apontam para o handler default que **falha ruidosamente** (`vtlbDefaultPhyRead16`,
vtlb.cpp ~624, chama `pxFail`). Recomendação: qualquer largura não tratada numa região deve chamar
um handler default que **aborta/loga**, nunca ler silenciosamente RAM crua.

### 1c. Acessos que cruzam fronteira de página

Referência: `vtlb_memSafeReadBytes` / `vtlb_memSafeWriteBytes` / `vtlb_memSafeCmpBytes` (vtlb.cpp).
Eles fazem `std::memcpy` **só até o fim da página** (`remaining_in_page = min(VTLB_PAGE_SIZE -
(mem & VTLB_PAGE_MASK), restante)`) e então re-consultam `vmap[mem >> VTLB_PAGE_BITS]` para a próxima
página, num laço. Isto é, tratam cada página independentemente e nunca assumem contiguidade de host
através de fronteira. O caminho quente (`vtlb_memRead<DataType>`) NÃO trata cross-page — assume que
um acesso alinhado de N bytes cabe numa página; cross-page só aparece nas variantes "Safe" usadas por
ferramentas. Aplicação: para nós, acessos de 16/32 bits desalinhados que cruzam página precisam do
padrão "fatiar por página e re-consultar a LUT a cada fatia".

### 1d. Fastmem (mapeamento direto explorando faults do host) — PCSX2 e Dolphin

**PCSX2** (`vtlb.cpp`): reserva uma arena de 4 GB (`FASTMEM_AREA_SIZE = 0x100000000`,
`s_fastmem_area` = `SharedMemoryMappingArea`) e mapeia RAM guest diretamente nela, de modo que um
load/store recompilado vira um acesso nativo sem checagem. Quando o acesso cai numa página de MMIO
(não mapeada na arena), o host gera fault → `PageFaultHandler::HandlePageFault(exception_pc,
fault_address, is_write)` (vtlb.cpp): se o fault é numa página de código protegida
(`ProtMode_Write`), chama `mmap_ClearCpuBlock` (invalida o bloco JIT); senão chama
`vtlb_BackpatchLoadStore(exception_pc, fault_address)` que **reescreve o código JIT** daquele
load/store para passar a chamar o caminho lento (handler de MMIO). Os metadados para isso ficam em
`LoadstoreBackpatchInfo` (guest_pc, gpr_bitmask, fpr_bitmask, code_size, address_register,
data_register, size_in_bits, is_signed, is_load, is_fpr) — repare que **size_in_bits está gravado
por load/store**, então o backpatch sabe reconstruir o acesso na largura certa.

**Dolphin** (`Source/Core/Core/PowerPC/JitCommon/JitBackpatch.cpp`,
`Jitx86Base::HandleFault` / `BackPatch`; e `JitArm64/JitArm64_BackPatch.cpp`,
`JitArm64::HandleFastmemFault`): idêntico em espírito. Mapeia todo o espaço GC/Wii em host
(`Memory::base`, janela de `0x100010000`), acessos a RAM "just work" nativamente, acessos a MMIO
faltam → fault → `HandleFault` verifica se `access_address` está na janela de fastmem, e se sim
`BackPatch` desmonta o MOV, descobre registradores em uso (`registersInUseAtLoc`) e emite um
trampolim para o caminho lento (`GetReadTrampoline`/`GetWriteTrampoline`).

Nuance de ARM64 relevante para nós (temos backend ARM): o commit
`JitArm64_BackPatch: Correct usage of an invalidated iterator after ... erase()` mostra que ao
consumir `m_fault_to_handler` eles precisaram **copiar `fault_location`/`fastmem_area_length` para
temporários ANTES do `erase()`**, porque o `erase` invalida o iterador do `std::map` e o código
seguia usando `slow_handler_iter->first`. É exatamente a classe do nosso bug: **estado meio-mutado
usado depois da mutação**. Se formos fazer backpatch em ARM64, cuidado com iteradores/ponteiros
capturados antes de mutar o mapa de mapeamentos.

Observação honesta: fastmem/backpatch é uma otimização de performance, não pré-requisito de
correção. Para o zeebo-lle no estágio atual (boot/MMIO/correção), a LUT explícita (1a) já basta e é
mais fácil de manter consistente entre os dois backends. Fastmem pode vir depois.

---

## 2. Invalidação do JIT em remapeamento de memória / mudança de MMU

Este é o ponto mais diretamente ligado ao nosso bug (ponteiros de host obsoletos em blocos já
compilados).

### 2a. PCSX2 — proteção de página + discard de bloco

Referências: `vtlb.cpp` (`mmap_MarkCountedRamPage`, `mmap_ClearCpuBlock`, `m_PageProtectInfo`,
`vtlb_ProtectionMode`); Wiki "PCSX2 EE Recompiler".

- O recompilador mapeia a RAM guest em três arrays `BASEBLOCK` (`recRAM`, `recROM`, `recROM1`); cada
  `BASEBLOCK` é essencialmente um ponteiro de função (para o bloco compilado ou para um dispatcher
  `JITCompile`).
- Cada página de RAM tem um `vtlb_PageProtectionInfo` com um `Mode`
  (`ProtMode_None/Write/Manual/NotRequired`) e um `ReverseRamMap` (offset físico de origem).
- Ao compilar código de uma página, `mmap_MarkCountedRamPage` marca a página como
  `PageAccess_ReadOnly` (via `HostSys::MemProtect` **e** `vtlb_UpdateFastmemProtection`). Uma escrita
  nessa página gera SIGSEGV → o handler chama `mmap_ClearCpuBlock(offset)`, que: remonta a página
  R/W, marca `ProtMode_Manual`, e chama `Cpu->Clear(ReverseRamMap, pagesize)` para **descartar os
  blocos compilados** daquela página. Blocos "manual" recompilam com uma checagem de integridade no
  início (compara os bytes atuais com os de quando compilou; se diferem, `dyna_block_discard`).
- **Ponto-chave para nós**: note que `mmap_MarkCountedRamPage` **reatualiza `ReverseRamMap` toda vez**,
  com o comentário explícito "*Update the ReverseRamMap here because TLB changes could alter the paddr
  mapping*". Ou seja, o PCSX2 assume que remaps de TLB invalidam correspondências velhas e força
  re-derivação. O nosso bug é o caso oposto: guardamos um ponteiro velho e nunca re-derivamos.

### 2b. Dolphin — `tlbie`, page-table tracking e `PageTableUpdatedFromJit`

Referências: commit `page-table-fastmem-2` (`c4b913d`), `MemoryManager::UpdateDBATMappings`,
`MMU::PageTableUpdated` / `PageTableUpdatedFromJit`, `JitBase::WantsPageTableMappings`.

- O insight do Dolphin (relatado no progress report 2603): a arquitetura PowerPC **obriga** o jogo a
  executar `tlbie` após modificar a page table. Dolphin passou a **observar `tlbie`** como sinal de
  "o mapeamento mudou". No JIT, `MSRUpdated` emite código que, se DR (data translation) está ligado e
  há `pagetable_update_pending`, chama `PowerPC::MMU::PageTableUpdatedFromJit`.
- Quando a page table muda, `UpdateDBATMappings` **desmapeia tudo** (`UnmapFromMemoryRegion` sobre
  `m_dbat_mapped_entries`), limpa (`m_logical_page_mappings.fill(nullptr)`,
  `RemoveAllPageTableMappings`), e remonta. Fazem *diff incremental* em blocos de 64 bytes para achar
  o que adicionar/remover — mas o ponto conceitual é: **há um evento explícito e único ("o mapeamento
  mudou") que dispara a reconstrução completa e consistente de todos os ponteiros derivados.**

Aplicação ao zeebo-lle: precisamos de um equivalente. O ARM/OKL4 usa `MCR` para escrever no TTBR/nas
tabelas de página e instruções de TLB (`MCR p15, ... c8` = TLB invalidate). **Interceptar essas
escritas de CP15 (TTBR0/TTBR1/TLBIALL/TLBIMVA) é o nosso "tlbie".** Em cada uma:
(1) recomputar a VTLB inteira das regiões afetadas de forma atômica;
(2) invalidar/limpar os blocos JIT do Dynarmic cujas páginas mudaram (Dynarmic:
`InvalidateCacheRange` / `ClearCache`);
(3) garantir que o Unicorn veja o mesmo mapa.
Se qualquer passo do remap falhar, **não aplicar nenhum** (transação — ver recomendação 2).

### 2c. Ponteiros de host obsoletos em blocos compilados

Consequência combinada: quando o mapeamento muda, os blocos JIT que fizeram *inline* de um ponteiro
de host (fastmem) ficam obsoletos. As duas defesas usadas:
- **PCSX2**: blocos não fazem inline de ponteiro de RAM arbitrário — usam a arena fastmem fixa +
  backpatch; e código auto-modificável/relink é pego por proteção de página.
- **Dolphin**: recarrega `MEM_REG`/base a cada `MSRUpdated` e invalida blocos via `JitInterface`
  (`InvalidateICache` / `EraseSingleBlock`, `blocks.EraseSingleBlock` em JitArm64/Jit.cpp) quando a
  região correspondente muda.
Para nós, a regra segura: **nenhum bloco Dynarmic deve conter um ponteiro de host de memória guest
que sobreviva a um remap sem invalidação.** Se usarmos LUT (não fastmem inline), o bloco carrega o
ponteiro da LUT em runtime a cada acesso e o problema desaparece — ao custo de uma indireção.

---

## 3. Ferramentas de depuração de DIVERGÊNCIA (interpretador vs. recompilador)

Aqui a resposta honesta é matizada:

- **PCSX2**: NÃO encontrei um modo automático "roda interpretador e recompilador em paralelo e
  reporta a primeira divergência" no código atual. O que existe: (a) o próprio interpretador
  (`intCpu`, caminho `vtlb_memRead`/`Write`) pode ser selecionado no lugar do recompilador, servindo
  de referência; (b) `PauseOnTLBMiss` (vtlb.cpp `vtlb_Miss`/`vtlb_BusError`, linhas ~538/558) —
  pausa a VM e abre no debugger na primeira falha de tradução, com mensagem
  `"TLB Miss, pc=0x.. addr=0x.. [store/load]"`; (c) logging por-instrução no debugger integrado.
  O padrão prático da comunidade é rodar o mesmo trecho nos dois cores e comparar dumps de estado.
- **Dolphin**: também não tem um comparador lockstep embutido no master atual. O mecanismo real é o
  JIT **cair no interpretador por instrução** (`Interpreter::GetInterpreterOp(inst)` + `ABI_Call...`
  em `Jit64/Jit.cpp` e `JitArm64/Jit.cpp`): qualquer instrução pode ser executada pela mesma função
  do interpretador dentro do bloco JIT, o que garante que interpretador e JIT compartilham a
  **mesma** implementação semântica para instruções não-recompiladas. Isso reduz divergência por
  construção (uma fonte de verdade para a semântica), em vez de detectá-la a posteriori.
  Para depuração há a UI de debug (View→Code, breakpoints em endereços PPC, step, dump de registrador
  e memória) — ver `dolphin-emu` docs "Debugging Tools & Techniques".

**Recomendação para nós** (já temos paridade, mas para o futuro): o nosso comparador lockstep
Unicorn-vs-Dynarmic (que já achou o bug) é MELHOR do que o que qualquer um dos dois tem embutido.
O gap que ele NÃO cobriu foi **memória**, não CPU. Estender o lockstep para comparar, a cada passo,
não só registradores mas também o **resultado de cada load** (o valor que cada backend leu para o
mesmo endereço/largura) teria pego o bug do LDRH na hora do primeiro acesso divergente, não 181306
instruções depois. Ou seja: **incluir loads/stores no diff do lockstep** é o item acionável nº 1
desta seção.

---

## 4. Acessos NÃO ALINHADOS e largura variável na mesma região MMIO

- **PCSX2**: como visto em 1b/1d, o handler é **selecionado por largura via tabela**
  (`RWFT[Index][Write][handler]`, `Index` de `vtlbMemFP<Width,Write>`), e o backpatch grava
  `size_in_bits` por load/store. Não existe "handler genérico" que adivinha a largura — cada largura
  tem sua função. Para desalinhamento dentro da RAM, o caminho quente usa acesso de host que tolera
  desalinhamento (`r128_store_unaligned`), e os utilitários "Safe" fatiam por página. Para MMIO,
  desalinhamento tipicamente não deveria ocorrer (registradores são acessados alinhados); se ocorrer,
  cai no handler da largura pedida.
- **Dolphin**: MMIO é roteado por `MMIO::Mapping` com handlers registrados **por largura** (8/16/32);
  o `MMU`/`ReadFromHardware`/`WriteToHardware` despacham conforme o tamanho do acesso. Acesso que
  cruza fronteira de página no caminho MMU é decomposto.

**Lição para o nosso bug de 16 bits**: a arquitetura correta é **tabela de handlers indexada por
largura**, com TODAS as larguras preenchidas (mesmo que seja para um handler que loga/aborta). Assim
um LDRH nunca pode "escapar" para um caminho não vigiado — ele é obrigado a passar pelo slot de 16
bits daquela região. Se aquele slot deveria espelhar o de 32 bits, ele espelha explicitamente; nunca
por omissão silenciosa.

---

## 5. Memory watchpoint / breakpoint de dado — "quem escreveu este endereço?"

Referência: `Source/Core/Core/PowerPC/BreakPoints.h` — struct `TMemCheck` e classe `BreakPoints`.

`TMemCheck`:
- `start_address`, `end_address`, `is_ranged` — **cobre um intervalo**, portanto pega o mesmo
  endereço em qualquer largura de acesso (resolve nosso "só o de 32 tinha vigia").
- `is_break_on_read`, `is_break_on_write` — separa leitura de escrita.
- `log_on_hit`, `break_on_hit`, `num_hits`, `condition` (`std::optional<Expression>` — condição
  avaliada em runtime).
- `bool Action(System&, u64 value, u32 addr, bool write, size_t size, u32 pc)` — o callback recebe
  **`pc` (quem acessou), `value`, `addr`, `write`, `size`**. É literalmente "quem escreveu, o quê, de
  que largura, em que endereço".

Como se conecta ao motor: quando há qualquer memcheck/watchpoint ativo, Dolphin liga `jo.memcheck`
(`JitBase::RefreshConfig`: `jo.memcheck = IsMMUMode() || IsPauseOnPanicMode() || any_watchpoints`) e
**o JIT emite a checagem de memória inline em cada load/store** (macros `MEMCHECK_START`/`MEMCHECK_END`
em `JitCommon`), e/ou desativa fastmem para aquela região, de modo que os acessos passem pelo caminho
lento que chama `TMemCheck::Action`. `BreakPoints` mantém a lista, `DelayedMemCheckUpdate` cuida de
atualizar sem corromper o JIT em execução.

**Aplicação imediata ao zeebo-lle**: implementar um `MemCheck` ranged próprio (não copiar; reimplementar
a partir desta descrição). Para caçar o bug de forma reprodutível: colocar um watchpoint no endereço
do LDRH cobrindo 1 byte de range (que por ser ranged pega leituras de 8/16/32/64), com callback que
loga `pc`, `size`, `write` e `value` em CADA acesso dos DOIS backends. A primeira vez que o `value`
lido pelo Unicorn diferir do lido pela VTLB para o mesmo `addr`/`size` é o ponto exato da divergência
de mapeamento — muito antes das 181306 instruções.

---

## Resumo dos arquivos/símbolos de referência (para leitura humana, não cópia)

PCSX2 (github.com/PCSX2/pcsx2):
- `pcsx2/vtlb.h` — `VTLBVirtual` (bit de sinal RAM/handler), `MapData::vmap`/`pmap`/`RWFT`,
  `vtlbMemFP<Width,Write>`, `vtlb_ProtectionMode`, `LoadstoreBackpatchInfo` (via vtlb.cpp).
- `pcsx2/vtlb.cpp` — `vtlb_memRead/Write<DataType>`, `vtlb_memSafe*Bytes` (cross-page),
  `vtlb_VMap`/`vtlb_VMapUnmap`, `mmap_MarkCountedRamPage`, `mmap_ClearCpuBlock`,
  `PageFaultHandler::HandlePageFault`, `vtlb_BackpatchLoadStore`, `vtlb_ReassignHandler`,
  `vtlb_Miss`/`vtlb_BusError` (+ `PauseOnTLBMiss`).
- Wiki: "PCSX2 Documentation/PCSX2 EE Recompiler" (BASEBLOCK, Write Interception, Manual Protection).

Dolphin (github.com/dolphin-emu/dolphin):
- `Source/Core/Core/PowerPC/BreakPoints.h` — `TMemCheck` (ranged, `Action(...,size,pc)`), `BreakPoints`.
- `Source/Core/Core/HW/Memmap.{h,cpp}` — `MemoryManager::UpdateDBATMappings`/`InitFastmemArena`,
  `m_dbat_mapped_entries`, `MapInMemoryRegion`/`UnmapFromMemoryRegion`, `m_physical_base`/`m_logical_base`.
- `Source/Core/Core/PowerPC/MMU.{h,cpp}` — `PageTableUpdated`/`PageTableUpdatedFromJit`, `ReloadPageTable`.
- `Source/Core/Core/PowerPC/JitCommon/JitBackpatch.cpp` — `HandleFault`/`BackPatch`, trampolins.
- `Source/Core/Core/PowerPC/JitArm64/JitArm64_BackPatch.cpp` — `HandleFastmemFault` (cuidado com
  iterador invalidado após `erase`).
- `Source/Core/Core/PowerPC/Jit64/Jit.cpp` e `JitArm64/Jit.cpp` — fallback por-instrução ao
  interpretador (`GetInterpreterOp`), `EraseSingleBlock`, `MSRUpdated`.
- `JitBase::RefreshConfig`/`WantsPageTableMappings` — `jo.memcheck`/`jo.fastmem` gating.

### O que NÃO encontrei (honestidade)
- Nenhum comparador lockstep interpretador-vs-JIT automático embutido, nem no PCSX2 nem no Dolphin
  master atual. Ambos usam "mesma semântica compartilhada" + debugger manual, não diff automático.
- Não inspecionei os arquivos `recVTLB.cpp` (dynarec do vtlb) nem `MMIO.cpp`/`MMIOHandlers.cpp` do
  Dolphin linha a linha — as descrições de MMIO por largura vêm da assinatura das tabelas e do
  comportamento documentado, não de leitura completa desses arquivos.
