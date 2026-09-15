# IShell Interface

IShell is the shell object and the root of the object graph.
A title receives a shell pointer at start and rarely talks to anything else directly.
Object creation, applet control, timers, resources, dialogs and system notification all go through this interface.

## Vtable layout

<!-- BEGIN GENERATED: IShell -->
_Generated from the public SDK header `AEEIShell.h`. Inheritance chain: IBase, IShell._

Base slots: **IBase → IShell**, so slot 0 is the first method of IBase and the first method of IShell starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | CreateInstance | int | this, AEECLSID ClsId, void ** ppobj |
| 3 | QueryClass | boolean | this, AEECLSID cls, AEEAppInfo * pai |
| 4 | GetDeviceInfo | void | this, AEEDeviceInfo * pi |
| 5 | StartApplet | int | this, AEECLSID cls,uint16 wFlags, const char * pszArgs |
| 6 | CloseApplet | int | this, boolean bReturnToIdle |
| 7 | CanStartApplet | boolean | this, AEECLSID cls |
| 8 | ActiveApplet | AEECLSID | this |
| 9 | EnumAppletInit | void | this |
| 10 | EnumNextApplet | AEECLSID | this, AEEAppInfo * pai |
| 11 | SetTimer | int | this, int32 dwMsecs, void (*pfn)(void *), void * pUser |
| 12 | CancelTimer | int | this, void (*pfn)(void *), void * pUser |
| 13 | GetTimerExpiration | uint32 | this, void (*pfn)(void *), void * pUser |
| 14 | CreateDialog | int | this, const char * pszRes, uint16 wID, DialogInfo * pInfo |
| 15 | GetActiveDialog | IDialog * | this |
| 16 | EndDialog | int | this |
| 17 | LoadResString | int | this, const char * pszBaseFile, uint16 nResID, AECHAR * pBuff, int nSize |
| 18 | LoadResData | void * | this, const char * pszResFile, uint16 nResID, ResType nType |
| 19 | LoadResObject | IBase * | this, const char * pszResFile, uint16 nResID, AEECLSID cls |
| 20 | FreeResData | void | this, void * pData |
| 21 | SendEvent | boolean | this, uint16 wFlags, AEECLSID clsApp,AEEEvent evt, uint16 wParam, uint32 dwParam |
| 22 | Beep | boolean | this, BeepType nBeepType, boolean bLoud |
| 23 | GetPrefs | int | this, AEECLSID id,uint16 wVer, void * pCfg, uint16 nSize |
| 24 | SetPrefs | int | this, AEECLSID id,uint16 wVer, void * pCfg, uint16 nSize |
| 25 | GetItemStyle | void | this, AEEItemType t, AEEItemStyle * pNormal, AEEItemStyle * pSel |
| 26 | Prompt | boolean | this, AEEPromptInfo * pi |
| 27 | MessageBox | boolean | this, const char * pszRes, uint16 wTitle, uint16 wText |
| 28 | MessageBoxText | boolean | this, const AECHAR * pTitle, const AECHAR * pText |
| 29 | SetAlarm | int | this, AEECLSID cls, uint16 nUserCode, uint32 nMins |
| 30 | CancelAlarm | int | this, AEECLSID cls, uint16 nUserCode |
| 31 | AlarmsActive | boolean | this |
| 32 | GetHandler | AEECLSID | this, AEECLSID cls, const char * pszIn |
| 33 | RegisterHandler | int | this, AEECLSID clsBase, const char * pszIn, AEECLSID clsHandler |
| 34 | RegisterNotify | int | this, AEECLSID clsNotify, AEECLSID clsType, uint32 dwMask |
| 35 | Notify | int | this, AEECLSID clsType, uint32 dwMask, void * pData |
| 36 | Resume | void | this, AEECallback * pcb |
| 37 | ForceExit | boolean | this |
| 38 | GetPosition | int | this, AEEPosAccuracy nPres, PFNPOSITIONCB pfn, void * pUser |
| 39 | CheckPrivLevel | boolean | this, AEECLSID clsIDWant, boolean bQueryOnly |
| 40 | IsValidResource | boolean | this, const char * pszRes, uint16 wID,ResType t, AEECLSID cls |
| 41 | LoadResDataEx | void* | this, const char * pszResFile, uint16 nResID, ResType nType, void *pBuf, uint32 *pnLen |
| 42 | RegisterSystemCallback | void | this, AEECallback * pcb, int nSCBType |
| 43 | DetectType | int | this, const void * cpBuf, uint32 * pdwSize, const char * cpszName, const char ** pcpszMIME |
| 44 | GetDeviceInfoEx | int | this, AEEDeviceItem nItem, void *pBuff, int *nSize |
| 45 | GetClassItemID | uint32 | this, AEECLSID cls |
| 46 | Obsolete | int | this |
| 47 | GetProperty | int | this, AEECLSID cls,uint16 wID, void * pDest, uint16 * pwSize |
| 48 | SetProperty | int | this, AEECLSID cls,uint16 wID, void * pSrc, uint16 wSize |
| 49 | RegisterEvent | AEEEvent | this, const char * psz, int * pnCount |
| 50 | Reset | int | this, AEEResetType resettype |
| 51 | AppIsInGroup | int | this, AEECLSID idApp, AEECLSID idGroup |

- IShell inherits IBase directly, so its first own method is slot 2. 
<!-- END GENERATED: IShell -->

## Slots by purpose

| Purpose | Slots | Notes |
|---|---|---|
| Object creation | CreateInstance | returns 0 on success, 3 if the class is unsupported |
| Class and device queries | QueryClass, GetDeviceInfo, GetDeviceInfoEx, GetClassItemID | used for capability checks before creating objects |
| Applet control | StartApplet, CloseApplet, CanStartApplet, ActiveApplet, EnumAppletInit, EnumNextApplet | the shell owns applet lifetime |
| Timers | SetTimer, CancelTimer, GetTimerExpiration | one-shot timers, not periodic |
| Dialogs | CreateDialog, GetActiveDialog, EndDialog | modal prompts, rarely used by games |
| Resources | LoadResString, LoadResData, LoadResObject, LoadResDataEx, FreeResData, IsValidResource | the path by which archives are read |
| Events and notification | SendEvent, RegisterNotify, Notify, RegisterEvent, RegisterSystemCallback | cross-applet messaging |
| Preferences and properties | GetPrefs, SetPrefs, GetProperty, SetProperty | configuration storage |
| Handlers | GetHandler, RegisterHandler | media and URL handlers chosen by input type |
| Alarms | SetAlarm, CancelAlarm, AlarmsActive | wake-up scheduling, unused by normal titles |
| Position | GetPosition | location provider, absent on this hardware |
| Process | Resume, ForceExit, Reset, CheckPrivLevel | lifecycle and privilege checks |
| Misc | Beep, Prompt, MessageBox, MessageBoxText, GetItemStyle, DetectType, Obsolete, AppIsInGroup | UI helpers and compatibility leftovers |

## Resource loading

Resource calls are the boundary between the runtime and the game's archives.
Two shapes exist:

- LoadResData and LoadResString take a resource file name and a resource ID. 
- LoadResDataEx adds a caller-provided buffer and a length out-parameter, so a title can read a resource without the runtime allocating. 

The archive the name refers to is the container the loader mounted.
A title does not see file paths for resources inside an archive;
it sees IDs.

## Timer semantics

- SetTimer is one-shot.
  The callback is removed after it fires.
- The callback receives the user pointer supplied at registration. 
- GetTimerExpiration lets a title read the remaining time, which some titles use as a frame clock. 
- CancelTimer matches on callback pointer plus user pointer, not on an ID. 

| Property | Consequence for a runtime |
|---|---|
| One-shot | the title must re-arm for every frame; the runtime must not re-arm it |
| No identifier | duplicate registrations of the same pair are indistinguishable |
| Millisecond delay | the delay is a request, not a guarantee of that exact spacing |
| No preemption guarantee | due timers may not run while a callback is still executing |

That last row is the one that decides whether a title reaches gameplay.
If the runtime waits for the current callback to return before servicing due timers, a title that busy-waits inside its own callback never sees its frame timer fire.

## What breaks first

Three failures account for most bring-up stalls at this interface:

1.
CreateInstance returns success but writes a null pointer.
The title later dereferences it and the fault appears somewhere unrelated.
2.
Timers are scheduled but never serviced.
The title renders once and freezes.
3.
LoadResData returns a buffer whose length field is wrong.
The title reads past the end or truncates an image silently.

## Evidence

Slot numbers and method signatures come from the public SDK header.
The classification by purpose is a reading aid, not part of the ABI.
