# F4 — input [EM CURSO]
## [CONF] fork `testkit/shadow_inc/` (15/09)
- Sombras IHID p/ testes: AEEIHID.(IDL/H), AEEIHIDDevice.(IDL/H), RawDevice, Keyboard/Mouse/Joystick.
- Origem SDK; uso: fixtures de teste, não runtime.
## [CONF] `hid_hle.cpp` clone (15/09)
- Botão: RegisterForButtonEvent, GetNextButtonEvent. Device: CreateDevice, GetDeviceInfo.
- Conexão: GetNextConnectEvent, GetConnectedDevices. Host injeta via `UpdateState(ZPadState)`.
## Pendente
- Runtime HID fork; Z-Wheel (F4b); UIDs d-pad (4 UIDs, etapa 8).
