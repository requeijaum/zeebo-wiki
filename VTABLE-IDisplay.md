# VTable IDisplay (`AEEIDisplay.h INHERIT_IDisplay`, ordem SDK) [CONF via header; base 0-1 = IBase(AddRef/Release), SetClipRect = slot 18 — consenso SDK+clone+zeemu+zeebx]

| Slot | Método | Retorno | Args |
|---|---|---|---|
| 0 | INHERIT | INHERIT_IBase(iname) |  |
| 1 | GetFontMetrics | int | po,AEEFont nFont,int * pnAscent,int * pnDescent |
| 2 | MeasureTextEx | int | po, AEEFont nFont, const AECHAR * pcText,int nChars,int nMaxWidth, int * pnFits |
| 3 | DrawText | int | po,AEEFont nFont, const AECHAR * pcText,int nChars,int x,int y,const AEERect * prcBackground,uint32 dwFlags |
| 4 | DrawRect | void | po,const AEERect * pRect,RGBVAL clrFrame, RGBVAL clrFill, uint32 dwFlags |
| 5 | BitBlt | void | po,int xDest,int yDest,int cxDest,int cyDest,const void * pbmSource,int xSrc,int ySrc,AEERasterOp dwRopCode |
| 6 | Update | void | po, boolean bDefer |
| 7 | SetAnnunciators | void | po, uint16 wVal, uint16 wMask |
| 8 | Backlight | void | po,boolean bOn |
| 9 | SetColor | RGBVAL | po, AEEClrItem clr, RGBVAL rgb |
| 10 | GetSymbol | AECHAR | po,AEESymbol sym, AEEFont nFont |
| 11 | DrawFrame | int | po, AEERect * prc,AEEFrameType ft, RGBVAL rgbFill |
| 12 | CreateDIBitmap | int | po, IDIB **ppIDIB, uint8 colorDepth, uint16 w, uint16 h |
| 13 | SetDestination | int | po, IBitmap *pDst |
| 14 | GetDestination | IBitmap * | po |
| 15 | GetDeviceBitmap | int | po, IBitmap **ppIBitmap |
| 16 | SetFont | IFont * | po, AEEFont nFont, IFont *piFont |
| 17 | SetClipRect | void | po, const AEERect * pRect |
| 18 | GetClipRect | void | po, AEERect * pRect |
| 19 | Clone | int | po, IDisplay **ppIDisplayNew |
| 20 | MakeDefault | void | po |
| 21 | IsEnabled | boolean | po |
| 22 | NotifyEnable | int | po, AEECallback *pcb |
| 23 | CreateDIBitmapEx | int | po, IDIB **ppIDIB, int nDepth, int nHeight, int nWidth, int nPaletteSize, int cbExtra |
| 24 | SetPrefs | int | po, const char *pchSettings, int cSettings |
