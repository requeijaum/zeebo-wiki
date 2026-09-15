# F7 — Title Gate [IN PROGRESS]
## [CONF] `zeebo-emulator/docs/compat-list.md` (09-15; Playable/In-game/Boots/Untested)
- **Double Dragon** (CLS 0x0102F789): Playable — REGRESSED by `86463ac` (white frame),
  workaround `ZEEB_NO_ASSET_AUTODISCOVER=1` (262 colors, pixel-identical baseline); permanent fix pending.
  Audio: final tick is a manual-run check only (VALIDACAO-FASE1-DD-AUDIO.md).
- **Alien Breaker Deluxe** (CLS 0x0108e356, not MIF 0x0103081d): In-game (ticks 0-9, 748 HLE calls,
  runaway loop on stub 0x800b1800).
- **Tork**: PLAYABLE with `ZEEB_GENERIC_RENDER=1` (452 colors, input changes frames).
- Checked 09-15: local `zeebulator-upstream` = 95b2d51 (08-12, nothing new on origin).
  No evidence of more Marcelo playables; 'many' = Infuse (oracle). [CONF]
## Pending
- Permanent DD fix; ABD stub wall; parked-fork gate confrontation.
