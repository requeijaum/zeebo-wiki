# Input: IHID, IHIDDevice, ISignal

Input is not a fixed API on this platform.
Titles open HID devices and subscribe to button or axis events, then poll them from their own timer callback.
There is no global input state a title can read at any time.

## Interfaces

<!-- BEGIN GENERATED: IHID -->
_Generated from the public SDK header `AEEIHID.h`. Inheritance chain: IQI, IHID._

Base slots: **IQI → IHID**, so slot 0 is the first method of IQI and the first method of IHID starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | CreateDevice | AEEResult | this, int nDevHandle, IHIDDevice** ppiHidDevice |
| 4 | GetDeviceInfo | AEEResult | this, int nDevHandle, AEEHIDDeviceInfo* pDevInfo |
| 5 | GetNextConnectEvent | AEEResult | this, int* pnDevHandle, int* pnStatus, boolean* pbDroppedEvents |
| 6 | RegisterForConnectEvents | AEEResult | this, ISignal* piSignal |
| 7 | GetConnectedDevices | AEEResult | this, int nDeviceType, int* pnDevHandles, int pnDevHandlesLen, int* pnDevHandlesLenReq |
<!-- END GENERATED: IHID -->

<!-- BEGIN GENERATED: IHIDDevice -->
_Generated from the public SDK header `AEEIHIDDevice.h`. Inheritance chain: IQI, IHIDDevice._

Base slots: **IQI → IHIDDevice**, so slot 0 is the first method of IQI and the first method of IHIDDevice starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | GetDeviceInfo | AEEResult | this, AEEHIDDeviceInfo* pDevInfo |
| 4 | GetDeviceStatus | AEEResult | this, int* pnStatus |
| 5 | RegisterForStatusChange | AEEResult | this, ISignal* piSignal |
| 6 | GetButtonInfo | AEEResult | this, int nButtonID, AEEHIDButtonInfo* pnButtonInfo |
| 7 | GetNumberOfButtons | AEEResult | this, int* pnButtons |
| 8 | RegisterForButtonEvent | AEEResult | this, ISignal* piSignal |
| 9 | GetNextButtonEvent | AEEResult | this, AEEHIDButtonInfo* pnButtonInfo, uint32* pdwTimestamp, boolean* pbDroppedEvents |
| 10 | GetPositionState | AEEResult | this, AEEHIDPositionInfo* pPosInfo |
| 11 | GetMinPositionInfo | AEEResult | this, AEEHIDPositionInfo* pPosInfo |
| 12 | GetMaxPositionInfo | AEEResult | this, AEEHIDPositionInfo* pPosInfo |
| 13 | GetAxesInfo | AEEResult | this, AEEHIDPositionInfo* pPosInfo |
| 14 | RegisterForPositionChange | AEEResult | this, ISignal* piSignal |
| 15 | SetExclusiveLevel | AEEResult | this, int nLevel |
| 16 | GetExclusiveLevel | AEEResult | this, int* pnLevel |
| 17 | Rumble | AEEResult | this, int nLeftMotorSpeed, int nRightMotorSpeed |
| 18 | GetRumbleStatus | AEEResult | this, int* pnLeftMotorSpeed, int* pnRightMotorSpeed |
<!-- END GENERATED: IHIDDevice -->

<!-- BEGIN GENERATED: ISignal -->
_Generated from the public SDK header `AEEISignal.h`. Inheritance chain: IQI, ISignal._

Base slots: **IQI → ISignal**, so slot 0 is the first method of IQI and the first method of ISignal starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | Set | int | this |
<!-- END GENERATED: ISignal -->

Note the inheritance difference: IHID and IHIDDevice inherit IQI and therefore start at slot 3, while ISignal also inherits IQI.
Interfaces that inherit IBase, such as IShell and IDisplay, start at slot 2.
Mixing the two up shifts every slot by one and produces calls that appear to work but act on the wrong method.

## Button identifiers

Buttons are identified by 32-bit UIDs, not by a dense enum.

- Measured on five commercial titles, game code embeds only the base UID and derives the others arithmetically. 
- The observed shape is: subtract the base, compare against a small count, then index a jump table of inline branch instructions. 
- Base UID measured: 0x0106c3fe. 
- The d-pad occupies four consecutive UIDs: 0x0106c3fe, 0x0106c3ff, 0x0106c400 and 0x0106c401. 
- Consequence: there is no single d-pad button.
  A runtime that reports one composite direction value leaves titles that poll individual UIDs with no input at all.

Two jump-table encodings appear in real code and behave differently:

| Encoding | Form | Behaviour |
|---|---|---|
| PC-relative branch table | add pc, pc, rN, lsl #2 with inline branches | relative, no base ambiguity |
| Absolute pointer table | ldr pc, [pc, rN, lsl #2] | absolute addresses, needs relocation |

## Zeebo specifics

| Property | Value |
|---|---|
| Gamepads supported | two, over USB |
| Directions | four digital UIDs, not a hat value |
| Buttons | four face buttons, two shoulders, back |
| Analog | two axes per pad |
| Rumble | exposed through the device interface |
| Hot plug | connect and disconnect events are reported |

A runtime has to supply three things for input to work at all:

1.
A device table that answers enumeration, including the second pad.
Titles that expect two players read the table before they draw their menus.
2.
Button events keyed by UID rather than by index, matching the arithmetic the title performs on the base UID.
3.
Connect and disconnect events, because some titles wait for a connect event before they start accepting button input at all.

The third item is the one most often missed.
The pad is present, the buttons work, and the title still ignores input because it is waiting for a connection notification that never arrives.

## Testing approach

The SDK ships interface definition files for the HID interfaces.
They are good fixture material: a fake device can be driven from them without touching real hardware, and the same fixtures make input behaviour reproducible in CI.

| Fixture | What it exercises |
|---|---|
| Keyboard device | button events with a large UID range |
| Mouse device | relative axes and buttons |
| Joystick device | absolute axes, buttons, rumble |
| Raw device | unfiltered reports, useful for protocol work |

Two practices that keep input tests honest:

- Drive the fake device through the same event queue the real path uses.
  A test that sets a global input state proves nothing about event delivery.
- Assert on the guest-visible effect, not on the runtime's internal state.
  An input test that passes while the title ignores the input has proved the wrong thing.

