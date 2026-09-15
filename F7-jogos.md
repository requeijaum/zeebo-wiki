# F7 — gate jogos [EM CURSO]
## [CONF] `zeebo-emulator/docs/compat-list.md` (15/09, legenda Playable/In-game/Boots/Untested)
- **Double Dragon** (CLS 0x0102F789): Playable — REGREDIDO por `86463ac` (frame branco),
  contorno `ZEEB_NO_ASSET_AUTODISCOVER=1` (262 cores, pixel-idêntico baseline); fix permanente pendente.
  Áudio: tick final só em run manual (VALIDACAO-FASE1-DD-AUDIO.md).
- **Alien Breaker Deluxe** (CLS 0x0108e356 ≠ MIF 0x0103081d): In-game (ticks 0-9, 748 HLE calls,
  loop em stub 0x800b1800).
- **Tork**: PLAYABLE com `ZEEB_GENERIC_RENDER=1` (452 cores, input muda frames).
## Pendente
- Fix permanente DD; ABD stub wall; confronto curupira/dev gates.
- Checado 15/09: `zeebulator-upstream` local = 95b2d51 (12/08, sem nada novo no origin). Sem evidência de mais jogáveis no Marcelo; 'muitos' = Infuse (oráculo). [CONF]
