# F8 — frentes [EM CURSO]
## [CONF] `core/backend.h` + `frontends/` clone (15/09)
- Costura: `Backend` com `PushVideoFrame` (RGB565/XRGB8888), `PushAudioSamples` (stereo int16,
  sample_rate por push — DD real é 22050Hz, `core/audio/mixer.h` único chamador), `PollInput()->ZPadState`.
- standalone SDL2: sdl2_backend + sdl2_gl + unified, letterbox, zpad_edges.
- libretro: shim `libretro_core.cpp`. gui: session + game_library (+default_games.json).
## [CONF] controles + zeemu frontend (15/09)
- Teclado (`zeebulator_game_probe`, README upstream): setas=D-pad, Backspace/Enter=Back,
  Z/X/C/V=botões 1-4 (X = soco no DD), Q/E=shoulders. Gamepad XInput junto (A/X trocados).
- Zeemu frontend/ = só Launcher (cpp/h). Menos frentes que o clone.
## Pendente
- Portas RetroArch (shim existe, uso real?); gui default_games.json.
