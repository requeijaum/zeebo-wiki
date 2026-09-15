# F2 — runtime AEE [EM CURSO]
## [CONF] leitura direta `core/brew/mod_runtime.h` (clone, 14/09)
- .mod RVCT ROPI: `AEEStaticMod_New` calcula load addr via PC-relativo, lê ptr 4B antes,
  chama slot 0x68 (MALLOC nSize+16=IModuleVtbl) — bate com AEEModGen.c.
- Slot 0x6c = FREE (path cleanup `AEEApplet_New`).
- Slot 0xc0 = `ISHELL_CreateInstance` via contexto ambient (138 call sites no DD real);
  contexto+12 = IShell, +20 = IDisplay (SetClipRect slot 18), +0x2c = objeto relativo-vtable desconhecido (Peggle).
- `SetShellInstance/SetDisplayInstance/SetThirdContextObject` injetam os ptrs.
## [CONF] `core/brew/hle_runtime.h`
- Ponte bidirecional: trap sentinela (call-out guest->HLE, vtable aponta p/ sentinela,
  `Register/ RegisterLabeled` p/ log de slot não implementado) + `CallArmFunction`
  (HLE->guest: AEEMod_Load, CreateInstance, HandleEvent, roda até retorno, AAPCS R0-R3).
- `CallArmFunctionPreservingContext` p/ callbacks síncronos (ex: ISQL::Exec row).
## [CONF] `core/brew/ishell.h` — dispatch START + timer
- `CreateInstance` real: singletons conhecidos + factories (ex: IDisplay); demais slots stub.
- `SetTimer/CancelTimer` reais, one-shot: jogo re-arma a cada frame (`SetTimer(16ms, cb)` no
  `HandleEvent(EVT_APP_START)` real do DD) — loop cooperativo fica no host.
- `SetAppletHandleEvent(fn)` guarda HandleEvent real do guest p/ despacho de eventos.
## [CONF] Confronto bug full-rewrite (ROADMAP.md UPDATE 13/14, fork canônico)
- Sintoma: DD agenda UM timer 16ms (cb=0x11c074) no START, depois busy-wait em GetUpTimeMS
  sem Sleep/yield → continuação START nunca retorna → timer nunca dispara.
- Tentado: ZEEB_UPTIME_YIELD (cede mas re-entra SEM passar no tick externo → 0 ticks),
  ZEEB_TIMER_PREEMPT=1 (salva contexto, roda timer devido como shell faria, restaura).
- Contrato SDK (brew-sim-recon, headers públicos AEEShell/AEECallback): cooperativo + retorno;
  loop per-frame vive na fila de timers do shell, re-armado a cada frame — idêntico ao
  contrato do clone (`ishell.h`). Diagnóstico e direção do fix convergem. [CONF]
- Estado: fix pendente de validação (AUTOPRESS ainda gated). Próximo: validar PREEMPT no DD.
