# IDisplay Interface

IDisplay is the drawing surface for an applet. Text, rectangles, bitmaps and
DIB allocation all pass through this interface.

Vtable layout: slot N lives at vtable + N*4. Slots 0 and 1 are AddRef and
Release, inherited from IBase.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | GetFontMetrics | int | this,AEEFont nFont,int * pnAscent,int * pnDescent |
| 3 | MeasureTextEx | int | this, AEEFont nFont, const AECHAR * pcText,int nChars,int nMaxWidth, int * pnFits |
| 4 | DrawText | int | this,AEEFont nFont, const AECHAR * pcText,int nChars,int x,int y,const AEERect * prcBackground,uint32 dwFlags |
| 5 | DrawRect | void | this,const AEERect * pRect,RGBVAL clrFrame, RGBVAL clrFill, uint32 dwFlags |
| 6 | BitBlt | void | this,int xDest,int yDest,int cxDest,int cyDest,const void * pbmSource,int xSrc,int ySrc,AEERasterOp dwRopCode |
| 7 | Update | void | this, boolean bDefer |
| 8 | SetAnnunciators | void | this, uint16 wVal, uint16 wMask |
| 9 | Backlight | void | this,boolean bOn |
| 10 | SetColor | RGBVAL | this, AEEClrItem clr, RGBVAL rgb |
| 11 | GetSymbol | AECHAR | this,AEESymbol sym, AEEFont nFont |
| 12 | DrawFrame | int | this, AEERect * prc,AEEFrameType ft, RGBVAL rgbFill |
| 13 | CreateDIBitmap | int | this, IDIB **ppIDIB, uint8 colorDepth, uint16 w, uint16 h |
| 14 | SetDestination | int | this, IBitmap *pDst |
| 15 | GetDestination | IBitmap * | this |
| 16 | GetDeviceBitmap | int | this, IBitmap **ppIBitmap |
| 17 | SetFont | IFont * | this, AEEFont nFont, IFont *piFont |
| 18 | SetClipRect | void | this, const AEERect * pRect |
| 19 | GetClipRect | void | this, AEERect * pRect |
| 20 | Clone | int | this, IDisplay **ppIDisplayNew |
| 21 | MakeDefault | void | this |
| 22 | IsEnabled | boolean | this |
| 23 | NotifyEnable | int | this, AEECallback *pcb |
| 24 | CreateDIBitmapEx | int | this, IDIB **ppIDIB, int nDepth, int nHeight, int nWidth, int nPaletteSize, int cbExtra |
| 25 | SetPrefs | int | this, const char *pchSettings, int cSettings |

Notes:

- SetClipRect is slot 18. This value is confirmed by the SDK macro layout, by
  two independent emulator implementations and by a real game disassembly that
  calls slot 18 while setting a clip rectangle.
- DrawText takes an AECHAR string; AECHAR is a 16-bit character type, so game
  text is not plain ASCII.
- BitBlt takes an AEERasterOp raster operation code.
- Update pushes the surface to the physical display. The boolean argument
  requests deferred update when set.
