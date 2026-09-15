# Lacunas declaradas do clone [CONF] (cada uma com endereço)
- MIF: só strings UTF-16LE; tabelas resource/ClassID/privilégios NÃO entendidas (`mif.h`).
- BAR: sub-tabela do off8 (32B header) NÃO usada/conteúdo diferido (`bar.h`).
- Contexto +0x2c: objeto relativo-vtable não-nulo, interface desconhecida (Peggle) (`mod_runtime.h`).
- Fork (estacionado): sem decoder áudio; START busy-wait (TIMER_PREEMPT pendente).
- Zeemu: 51 módulos, profundidade não medida (só largura).
- Infuse: fonte fechada; Z-Wheel pulado por custo.
