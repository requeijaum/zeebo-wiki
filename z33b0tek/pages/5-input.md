# Input: IHID, IHIDDevice, ISignal

Gamepad input in BREW is not a fixed API. Games open HID devices and subscribe
to button or axis events.

## Interfaces

- IHID: device enumeration and event subscription.
  - RegisterForButtonEvent / GetNextButtonEvent: subscribe and poll button events.
  - CreateDevice / GetDeviceInfo: open a device and read its capabilities.
  - GetNextConnectEvent / GetConnectedDevices: hot-plug tracking.
- IHIDDevice: a single device handle. The SDK ships concrete class IDs for
  keyboard, mouse and joystick devices, plus a raw device variant.
- ISignal: blocking wait on an event, used when a title wants to sleep on input.

## Button identifiers

Buttons are identified by 32-bit UIDs, not by a dense enum.

- Measured on five commercial titles: game code embeds only the base UID and
  derives the rest arithmetically.
- Observed shape: subtract the base, compare against a small count, then index a
  jump table of inline branch instructions.
- Base UID measured: 0x0106c3fe.
- The d-pad occupies four consecutive UIDs: 0x0106c3fe, 0x0106c3ff,
  0x0106c400, 0x0106c401.
- Consequence: there is no single "d-pad button". Up, down, left and right are
  four separate UIDs, and a title may query them individually or in a group.

## Zeebo specifics

- Two gamepads are supported, connected over USB.
- Each pad reports digital directions and buttons and two analog axes.
- Rumble and exclusive access are part of the device interface.

## Test approach

The SDK ships interface description files for the HID interfaces. They are
useful as fixture definitions when building a test harness, because a fake
device can be driven from them without touching real hardware.
