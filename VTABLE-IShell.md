# VTable IShell (`AEEIShell.h`, ordem SDK) [CONF via header]

| Slot | Método | Retorno | Args |
|---|---|---|---|
| 0 | CreateInstance | int | AEECLSID ClsId, void ** ppobj |
| 1 | QueryClass | boolean | AEECLSID cls, AEEAppInfo * pai |
| 2 | GetDeviceInfo | void | AEEDeviceInfo * pi |
| 3 | StartApplet | int | AEECLSID cls,uint16 wFlags, const char * pszArgs |
| 4 | CloseApplet | int | boolean bReturnToIdle |
| 5 | CanStartApplet | boolean | AEECLSID cls |
| 6 | ActiveApplet | AEECLSID |  |
| 7 | EnumAppletInit | void |  |
| 8 | EnumNextApplet | AEECLSID | AEEAppInfo * pai |
| 9 | SetTimer | int | int32 dwMsecs, void (*pfn)(void *), void * pUser |
| 10 | CancelTimer | int | void (*pfn)(void *), void * pUser |
| 11 | GetTimerExpiration | uint32 | void (*pfn)(void *), void * pUser |
| 12 | CreateDialog | int | const char * pszRes, uint16 wID, DialogInfo * pInfo |
| 13 | GetActiveDialog | IDialog * |  |
| 14 | EndDialog | int |  |
| 15 | LoadResString | int | const char * pszBaseFile, uint16 nResID, AECHAR * pBuff, int nSize |
| 16 | LoadResData | void * | const char * pszResFile, uint16 nResID, ResType nType |
| 17 | LoadResObject | IBase * | const char * pszResFile, uint16 nResID, AEECLSID cls |
| 18 | FreeResData | void | void * pData |
| 19 | SendEvent | boolean | uint16 wFlags, AEECLSID clsApp,AEEEvent evt, uint16 wParam, uint32 dwParam |
| 20 | Beep | boolean | BeepType nBeepType, boolean bLoud |
| 21 | GetPrefs | int | AEECLSID id,uint16 wVer, void * pCfg, uint16 nSize |
| 22 | SetPrefs | int | AEECLSID id,uint16 wVer, void * pCfg, uint16 nSize |
| 23 | GetItemStyle | void | AEEItemType t, AEEItemStyle * pNormal, AEEItemStyle * pSel |
| 24 | Prompt | boolean | AEEPromptInfo * pi |
| 25 | MessageBox | boolean | const char * pszRes, uint16 wTitle, uint16 wText |
| 26 | MessageBoxText | boolean | const AECHAR * pTitle, const AECHAR * pText |
| 27 | SetAlarm | int | AEECLSID cls, uint16 nUserCode, uint32 nMins |
| 28 | CancelAlarm | int | AEECLSID cls, uint16 nUserCode |
| 29 | AlarmsActive | boolean |  |
| 30 | GetHandler | AEECLSID | AEECLSID cls, const char * pszIn |
| 31 | RegisterHandler | int | AEECLSID clsBase, const char * pszIn, AEECLSID clsHandler |
| 32 | RegisterNotify | int | AEECLSID clsNotify, AEECLSID clsType, uint32 dwMask |
| 33 | Notify | int | AEECLSID clsType, uint32 dwMask, void * pData |
| 34 | Resume | void | AEECallback * pcb |
| 35 | ForceExit | boolean |  |
| 36 | GetPosition | int | AEEPosAccuracy nPres, PFNPOSITIONCB pfn, void * pUser |
| 37 | CheckPrivLevel | boolean | AEECLSID clsIDWant, boolean bQueryOnly |
| 38 | IsValidResource | boolean | const char * pszRes, uint16 wID,ResType t, AEECLSID cls |
| 39 | LoadResDataEx | void* | const char * pszResFile, uint16 nResID, ResType nType, void *pBuf, uint32 *pnLen |
| 40 | RegisterSystemCallback | void | AEECallback * pcb, int nSCBType |
| 41 | DetectType | int | const void * cpBuf, uint32 * pdwSize, const char * cpszName, const char ** pcpszMIME |
| 42 | GetDeviceInfoEx | int | AEEDeviceItem nItem, void *pBuff, int *nSize |
| 43 | GetClassItemID | uint32 | AEECLSID cls |
| 44 | Obsolete | int |  |
| 45 | GetProperty | int | AEECLSID cls,uint16 wID, void * pDest, uint16 * pwSize |
| 46 | SetProperty | int | AEECLSID cls,uint16 wID, void * pSrc, uint16 wSize |
| 47 | RegisterEvent | AEEEvent | const char * psz, int * pnCount |
| 48 | Reset | int | AEEResetType resettype |
