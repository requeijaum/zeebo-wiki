# AEE Runtime Contract

BREW applications are event-driven modules. They do not own a main loop.

## Module lifecycle

1. The loader places the .mod image in memory.
2. The module's first .text symbol is AEEMod_Load.
3. AEEMod_Load registers the module's CreateInstance entry point.
4. The shell calls IModule::CreateInstance(ClsId) to build the applet object.
5. The shell drives the applet through IApplet::HandleEvent.

Calls in both directions follow the ARM AAPCS:
the first four 32-bit arguments in R0-R3, further arguments on the stack,
and the return value in R0.

## Object creation

- Objects are created with ISHELL_CreateInstance(shell, ClsId, &ppobj).
- The class ID is a 32-bit value, for example the media player.
- On success the call returns 0 and writes the object pointer to ppobj.
- On an unsupported class the call returns 3 (ECLASSNOTSUPPORT).
  Value 20 means EUNSUPPORTED and is a different error.

## Events

The applet receives events through HandleEvent(app, eCode, wParam, dwParam).

| Event | Value |
|---|---|
| EVT_APP_START | 0 |
| EVT_APP_STOP | 0x1 |
| EVT_APP_SUSPEND | 0x2 |
| EVT_APP_RESUME | 0x3 |
| EVT_APP_CONFIG | 0x4 |
| EVT_APP_HIDDEN_CONFIG | 0x5 |
| EVT_APP_BROWSE_URL | 0x6 |
| EVT_APP_BROWSE_FILE | 0x7 |
| EVT_APP_MESSAGE | 0x8 |
| EVT_APP_TERMINATE | 0xa |
| EVT_APP_RESTART | 0xc |
| EVT_APP_MESSAGE_EX | 0x10 |
| EVT_APP_START_BACKGROUND | 0x11 |
| EVT_APP_WOULD_START | 0x12 |
| EVT_APP_POST_URL | 0x13 |
| EVT_APP_START_WINDOW | 0x14 |
| EVT_APP_LAST_EVENT | = EVT_APP_START_WINDOW |

Start flags passed in wParam of EVT_APP_START:

| Flag | Value | Meaning |
|---|---|---|
| AEE_START_OEM | 0x1 | launched externally by OEM software |
| AEE_START_RESTART | 0x2 | restarted after suspend failure or memory recovery |
| AEE_START_SSAVER | 0x4 | launched as screen saver |

Direct system callback types, requested through RegisterSystemCallback:

| Type | Value |
|---|---|
| AEE_SCB_AEE_INIT | 0 |
| AEE_SCB_AEE_EXIT | 1 |
| AEE_SCB_LOW_RAM | 2 |
| AEE_SCB_LOW_STORAGE | 3 |
| AEE_SCB_APP_CLOSED | 4 |
| AEE_SCB_MOD_UNLOAD | 5 |
| AEE_SCB_DEVICE_INFO_CHANGED | 6 |
| AEE_SCB_LOW_RAM_CRITICAL | 7 |
| AEE_SCB_APP_EXIT | 8 |

## Timers and the frame loop

- ISHELL_SetTimer schedules a one-shot callback after a delay in milliseconds.
- Timers are not periodic. A game that needs a frame loop re-arms the timer
  from inside its own callback.
- A typical frame delay is 16 ms.
- Consequence: the frame loop lives in the shell's timer queue, not in the game.
- The application returns control to the shell after each callback.
- There is no preemptive scheduling between the applet and its timers.

## Memory and I/O

- Allocation uses MALLOC and FREE from the AEE heap, not a host libc.
- File access goes through IFileMgr and IFile, not a host filesystem.
- There is no stdio, and C++ global constructors do not run automatically.

## Application processor ABI notes

Real .mod code compiled with ARM RVCT read-only position independence expects a
static base register convention. Observed shape in real game code:

- The module computes its own load address through PC-relative addressing.
- A pointer is read from 4 bytes before that address.
- A function pointer at offset 0x68 of the pointed structure is called with a
  byte count and returns a pointer. This matches the module allocation of
  nSize + sizeof(IModuleVtbl), where IModuleVtbl is 4 function pointers.
- Offset 0x6c holds the matching free function.
- Offset 0xc0 returns an ambient application context. The most used field of that
  context is at +12 and returns the IShell pointer used by helper macros that do
  not take a shell argument. A sibling field at +20 holds the current IDisplay.

Counts measured on one commercial title: 138 distinct call sites read the static
base and index the table; the ambient context at +0xc0 is by far the most used.
