# IShell Interface

IShell is the shell object. It is the entry point for object creation,
applet control, timers, resources, dialogs and system notification.

Vtable layout: slot N lives at vtable + N*4. Slots 0 and 1 are AddRef and
Release, inherited from IBase.

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
| 19 | LoadResObject | IBase * | this,const char * pszResFile, uint16 nResID, AEECLSID cls |
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
| 35 | Notify | int | this,AEECLSID clsType, uint32 dwMask, void * pData |
| 36 | Resume | void | this, AEECallback * pcb |
| 37 | ForceExit | boolean | this |
| 38 | GetPosition | int | this, AEEPosAccuracy nPres, PFNPOSITIONCB pfn, void * pUser |
| 39 | CheckPrivLevel | boolean | this, AEECLSID clsIDWant, boolean bQueryOnly |
| 40 | IsValidResource | boolean | this, const char * pszRes, uint16 wID,ResType t, AEECLSID cls |
| 41 | LoadResDataEx | void* | this, const char * pszResFile, uint16 nResID, ResType nType, void *pBuf, uint32 *pnLen |
| 42 | RegisterSystemCallback | void | this, AEECallback * pcb, int nSCBType |
| 43 | DetectType | int | this, const void * cpBuf, uint32 * pdwSize, const char * cpszName, const char ** pcpszMIME |
| 44 | GetDeviceInfoEx | int | this, AEEDeviceItem nItem, void *pBuff, int *nSize |
| 45 | GetClassItemID | uint32 | this,AEECLSID cls |
| 46 | Obsolete | int | this |
| 47 | GetProperty | int | this,AEECLSID cls,uint16 wID, void * pDest, uint16 * pwSize |
| 48 | SetProperty | int | this,AEECLSID cls,uint16 wID, void * pSrc, uint16 wSize |
| 49 | RegisterEvent | AEEEvent | this, const char * psz, int * pnCount |
| 50 | Reset | int | this,AEEResetType resettype |
| 51 | AppIsInGroup | int | this, AEECLSID idApp, AEECLSID idGroup |

Notes:

- Slot 0 is AddRef, slot 1 is Release. There is no QueryInterface slot.
- On ARM, arguments follow AAPCS: this in R0, then R1-R3, then the stack.
- ISHELL_CreateInstance returns 0 on success and 3 (ECLASSNOTSUPPORT) when the
  requested class is not supported by the runtime.
