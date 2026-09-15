# F0 — fatos [CONF]
- SoC MSM7201A: ARM1136J-S AP @528MHz + ARM926EJ-S modem (fonte: pagina Copetti projects/zeebo/index.html + SDK).
- OS: OKL4 + BREW 4.0.2 + ext Zeebo (IHID/IHIDDevice/ISignal, Z-Wheel).
- App: .mod relocável, AEEMod_Load -> CreateInstance(ClassID u32) -> HandleEvent(EVT_APP_START=0).
- AEERect 8B {int16 x,y,dx,dy}; AEEAppStart 24B (fonte: docs/brew-abi.md [CONF]).
- Formatos: GGZ (ggzbrewtools, doc), BAR (bar-etapa3 medido), MIF.
- Gráfica: Adreno 130, GLES 1.0/1.1, Micro3D/Brew3D/QXGL (zeemu cobre).
