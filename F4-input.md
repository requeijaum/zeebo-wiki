# F4 — Input [IN PROGRESS]
## [CONF] parked-fork `testkit/shadow_inc/` (09-15)
- IHID shadows for tests: AEEIHID.(IDL/H), AEEIHIDDevice.(IDL/H), RawDevice, Keyboard/Mouse/Joystick.
- SDK origin; fixtures only, not runtime.
## [CONF] `hid_hle.cpp` clone (09-15)
- Buttons: RegisterForButtonEvent, GetNextButtonEvent. Devices: CreateDevice, GetDeviceInfo.
- Connection: GetNextConnectEvent, GetConnectedDevices. Host injects via `UpdateState(ZPadState)`.
## Pending
- Fork runtime HID; Z-Wheel (F4b); d-pad UIDs.
