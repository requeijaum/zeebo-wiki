# Confronto fork curupira/dev × clone zeebulator [EM CURSO]
## [CONF] arquitetura despacho (15/09)
- Clone: vtable sentinela por slot (`HleRuntime::Register`), AAPCS R0-R3.
- Fork (`curupira/core/brew/despacho.{h,cpp}`): guest descobre sistema via `AEEHelperFuncs`
  + vtables; ponteiros apontam p/ FAIXA DE SAÍDA; loop para com PC na faixa; despacho por ÍNDICE
  (ex: `kSlotIdSetTimer=1520`). Comportamento saiu de `tools/bateria.cpp` (~860 linhas) p/ o motor.
- CreateInstance = IShell slot 2; fork serve título + 5 classes, resto FALSE (fail-closed, não stub 0).
## Pendente
- Mapear slot→função (despacho.cpp ~1200 linhas); comparar SetTimer/HandleEvent paths; gate DD.
