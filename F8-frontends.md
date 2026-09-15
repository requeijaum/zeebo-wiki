# F8 — Frontends [IN PROGRESS]
## [CONF] `core/backend.h` + `frontends/` clone (09-15)
- Seam: `Backend` with `PushVideoFrame` (RGB565/XRGB8888), `PushAudioSamples` (stereo int16,
  per-push sample_rate — real DD is 22050Hz, `core/audio/mixer.h` is the only caller), `PollInput()->ZPadState`.
- SDL2 standalone: sdl2_backend + sdl2_gl + unified, letterbox, zpad_edges.
- libretro: `libretro_core.cpp` shim. gui: session + game_library (+default_games.json).
## [CONF] controls + zeemu frontend (09-15)
- Keyboard (`zeebulator_game_probe`, upstream README): arrows=D-pad, Backspace/Enter=Back,
  Z/X/C/V=buttons 1-4 (X = DD punch), Q/E=shoulders. XInput gamepad alongside (A/X swapped).
- Zeemu frontend/ = Launcher only (cpp/h). Fewer frontends than the clone.
## Pending
- RetroArch ports (shim exists, real use?); gui default_games.json.
