# zeebo-hle-wiki — regras
- Execução lê só skills/ atual. Não ler patterns/ durante execução.
- 1 mudança de skill por ciclo. Skill pode reverter; wiki nunca.
- Todo fato [CONF] exige fonte: header SDK, código clonado ou dump.
- Clean-room: olhar, não copiar código Qualcomm.
- lfm: temp 0 extração, 0.7+CoT raciocínio, max_tokens 800, nunca temp 1.0.
- JSON com exemplo literal. Resposta termina em `Resposta: <valor>`.
- FOCO ATUAL: clone zeebulator (base estável) + zeemu + SDK. curupira/dev ESTACIONADO (in-dev) — nada novo lá até estabilizar.
