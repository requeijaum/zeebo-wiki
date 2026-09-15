# Infuse Target (oracle, A1 05-18-2024, closed source) [CONF via dossier]
## Playable
Double Dragon, Crash Nitro Kart 3D, Zeebo Family Pack; BREW: Asphalt GT 3D/2/3D(+MP), Kingdom Hearts V-Cast.
## To menu (~20)
Zeebo Extreme series, Sports series, F.C. series, NFS Carbon: Own the City, Turma da Monica, etc.
## In-game with defects
Reckless Racing, Raging Thunder II, Armageddon Squadron (textures + no sound, leak under investigation).
## Almost/broken
Zenonia (almost boots); Quake II (playable, sound cuts); Tekken 2, Quake, Rally Master Pro,
Zuma, Ultimate Chess 3D, RE4, Pac-Mania, Toy Raid (broken).
## Techniques worth stealing (idea, not code)
- BREW HLE (AEEHelperFuncs, IShell, IDisplay first; rest stubbed to boot).
- dynarmic ARM JIT; OpenGL backend; audio MIDI+PCM/ADPCM+MP3, independent resampling;
  HID 2 pads digital+analog; BAR/MIF loader + autodetect with icons; Win/macOS/Linux/Haiku/Deck ports + native ARM32 (RG353v).
## Scope note
- Infuse: Z-Wheel "explicitly not worth it". Our F4b exists for boot fidelity, not games.
