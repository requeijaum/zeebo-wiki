# AEE Runtime Contract

BREW applications are event-driven modules. They do not own a main loop, do not
create threads for normal work, and do not talk to a host operating system. Every
interaction with the outside world goes through an object interface.

Get this contract right and titles boot. Get it wrong and they hang in ways that
look like graphics bugs.

## Module lifecycle

| Step | Call | Notes |
|---|---|---|
| 1 | image mapped | the runtime chooses the base address |
| 2 | AEEMod_Load | the module's first .text symbol, called by the runtime |
| 3 | module registers factory | the module hands back its instance creation entry |
| 4 | IModule::CreateInstance | the runtime asks for the applet object |
| 5 | IApplet::HandleEvent | the runtime drives the title from here on |
| 6 | EVT_APP_STOP | the runtime retires the applet |

Calls in both directions follow the ARM AAPCS: the first four 32-bit arguments
travel in R0 to R3, further arguments go on the stack, and the return value comes
back in R0.

## Interfaces involved in the lifecycle

<!-- BEGIN GENERATED: IModule -->
_Generated from the public SDK header `AEEIModule.h`. Inheritance chain: IBase, IModule._

Base slots: **IBase → IModule**, so slot 0 is the first method of IBase and the first method of IModule starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | CreateInstance | int | this, IShell * pIShell,AEECLSID ClsId,void ** ppObj |
| 3 | FreeResources | void | this, IHeap * ph, IFileMgr * pfm |
<!-- END GENERATED: IModule -->

<!-- BEGIN GENERATED: IApplet -->
_Generated from the public SDK header `AEEIApplet.h`. Inheritance chain: IBase, IApplet._

Base slots: **IBase → IApplet**, so slot 0 is the first method of IBase and the first method of IApplet starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | HandleEvent | boolean | this, AEEEvent evt, uint16 wp, uint32 dwp |
<!-- END GENERATED: IApplet -->

<!-- BEGIN GENERATED: IAppletCtl -->
_Generated from the public SDK header `AEEIAppletCtl.h`. Inheritance chain: IQI, IAppletCtl._

Base slots: **IQI → IAppletCtl**, so slot 0 is the first method of IQI and the first method of IAppletCtl starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | GetRunningList | int | this, void *pBuff, int *pnSize |
| 4 | GetRunningInfo | int | this, AEECLSID cls, AEEAppItem nItem, void *pBuff, int *pnSize |
| 5 | Control | int | this, AEECLSID cls, int op, void *pBuff, int *pnSize |
<!-- END GENERATED: IAppletCtl -->

## Object creation

Objects are created with ISHELL_CreateInstance(shell, ClsId, &ppobj).

| Result | Meaning |
|---|---|
| 0 | success, the object pointer is written to ppobj |
| 3 | ECLASSNOTSUPPORT, the runtime does not implement that class |
| 20 | EUNSUPPORTED, a different and rarer failure |

The distinction matters. A runtime that returns 0 while writing a null pointer
produces a crash deep inside the title, far from the real cause. Returning 3 is
both honest and survivable: titles branch on it.

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

Note that EVT_APP_START is 0, not 1. Fixtures that assume 1 break the first
dispatch and produce a title that paints nothing.

Start flags arrive in wParam of EVT_APP_START:

| Flag | Value | Meaning |
|---|---|---|
| AEE_START_OEM | 0x1 | launched externally by OEM software |
| AEE_START_RESTART | 0x2 | restarted after a suspend failure or for memory recovery |
| AEE_START_SSAVER | 0x4 | launched as screen saver |

Suspend and resume are part of normal operation, not an error path. A title may
be suspended while a timer is pending, and it must not assume that wall-clock
time advanced while it was stopped.

## System notifications

Components can register a one-shot callback for system-level events through
ISHELL_RegisterSystemCallback.

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

The callback is one-shot. If a component wants to keep receiving the event, it
re-registers from inside the callback.

## Timers and the frame loop

- ISHELL_SetTimer schedules a one-shot callback after a delay in milliseconds.
- Timers are not periodic. The registered callback fires once and is removed.
- A game that needs a frame loop re-arms the timer from inside its own callback.
- A typical frame delay is 16 ms, which is about 60 frames per second.
- Consequence: the frame loop lives in the shell's timer queue, not in the game.
- Consequence: if the runtime never services the timer queue, the title renders
  nothing, no matter how correct its drawing code is.

A common failure pattern: the title starts, schedules exactly one timer, then
busy-waits on a time query instead of returning. If the runtime waits for the
callback to return before running due timers, the timer never fires and the
session stalls with a live but idle title. Servicing due timers independently of
the current callback is what keeps such a title alive.

## Memory and I/O

| Need | Interface | Note |
|---|---|---|
| Allocation | AEE heap, MALLOC and FREE | not a host libc |
| Files | IFileMgr and IFile | guest path namespace |
| Text output | IDisplay | no stdio at all |
| Time | ISysTimer and the shell uptime query | no host clock exposure |

There is no stdio, and C++ global constructors do not run automatically. A module
that relies on a static constructor to initialise state will find that state
zeroed.

## Application processor ABI notes

Real module code compiled with ARM RVCT read-only position independence expects a
static base convention. The observed shape in real game code:

- The module computes its own load address through PC-relative addressing.
- A pointer is read from four bytes before that address.
- A function pointer at offset 0x68 of the pointed structure is called with a
  byte count and returns a pointer. This matches the module allocation of
  nSize + sizeof(IModuleVtbl), where IModuleVtbl is four function pointers.
- Offset 0x6c holds the matching free function, used on the cleanup path.
- Offset 0xc0 returns an ambient application context. The most used field of that
  context sits at +12 and yields the IShell pointer that helper macros use when
  they do not take a shell argument. A sibling field at +20 holds the current
  IDisplay.

Counts measured on one commercial title: 138 distinct call sites read the static
base and index the table. The ambient context at +0xc0 is by far the most used.

Practical consequence: a runtime must supply these context slots before the first
draw call, or the title dereferences a null through a path that is hard to trace.

Evidence: event values, flags, notification types and method order from the
public SDK headers. Static base behaviour from disassembly of a real commercial
module.
