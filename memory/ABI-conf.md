# ABI [CONF] — fonte primária SDK (BrewMPSDK-7.12.5, `.../1.0.4.601 Pro/platform/`)
- EVT_APP_START=0, STOP=1, SUSPEND=2, RESUME=3, START_BACKGROUND=0x11, START_WINDOW=0x14=LAST (AEEEvent.h `system/inc/`). [CONF]
- AEEAppStart 24B ARM32: int error + AEECLSID + IDisplay* + AEERect + char* (AEEAppStart.h). [CONF]
- AEERect 8B: {int16 x,y,dx,dy} (AEERect.h `ui/inc/`). [CONF]
- Clone zeebulator local tem core/{brew,loader,cpu,memory,graphics,input,audio} (ls direto). [CONF]
