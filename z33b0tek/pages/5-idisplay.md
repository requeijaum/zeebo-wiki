# IDisplay Interface

IDisplay is the drawing surface. Text, rectangles, bitmaps and DIB allocation all
pass through this interface. It is not a GPU abstraction: it is the 2D surface a
title paints before any OpenGL work, and many titles use it for menus, HUD and
loading screens.

## Vtable layout

<!-- BEGIN GENERATED: IDisplay -->
_Generated from the public SDK header `AEEIDisplay.h`. Inheritance chain: IBase, IDisplay._

Base slots: **IBase → IDisplay**, so slot 0 is the first method of IBase and the first method of IDisplay starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | GetFontMetrics | int | this, AEEFont nFont,int * pnAscent,int * pnDescent |
| 3 | MeasureTextEx | int | this, AEEFont nFont, const AECHAR * pcText,int nChars,int nMaxWidth, int * pnFits |
| 4 | DrawText | int | this, AEEFont nFont, const AECHAR * pcText,int nChars,int x,int y,const AEERect * prcBackground,uint32 dwFlags |
| 5 | DrawRect | void | this, const AEERect * pRect,RGBVAL clrFrame, RGBVAL clrFill, uint32 dwFlags |
| 6 | BitBlt | void | this, int xDest,int yDest,int cxDest,int cyDest,const void * pbmSource,int xSrc,int ySrc,AEERasterOp dwRopCode |
| 7 | Update | void | this, boolean bDefer |
| 8 | SetAnnunciators | void | this, uint16 wVal, uint16 wMask |
| 9 | Backlight | void | this, boolean bOn |
| 10 | SetColor | RGBVAL | this, AEEClrItem clr, RGBVAL rgb |
| 11 | GetSymbol | AECHAR | this, AEESymbol sym, AEEFont nFont |
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

- SetClipRect is slot 18, confirmed by the header, by two independent implementations and by a real game disassembly.
<!-- END GENERATED: IDisplay -->

## Drawing model

| Concept | Detail |
|---|---|
| Text | AECHAR strings, 16-bit code units, not bytes |
| Fonts | selected by AEEFont constant or by an IFont object |
| Colours | RGBVAL with a SetColor item selector for pen, fill and text |
| Rectangles | AEERect is 8 bytes: x, y, dx, dy as int16 |
| Bitmaps | IBitmap objects, allocated as DIBs or wrapped from raw pixels |
| Raster operations | AEERasterOp controls how a blit combines with the destination |
| Clipping | a single current clip rectangle, set and restored by the title |
| Presentation | Update pushes the surface to the display, optionally deferred |

## Surface flow

1. The shell creates a display for the applet and passes it in the start event.
2. The title allocates bitmaps with CreateDIBitmap or CreateDIBitmapEx.
3. The title draws with DrawText, DrawRect and BitBlt.
4. SetDestination redirects drawing to a bitmap, for example for an offscreen
   buffer, and GetDestination reads the current target.
5. Update presents the result.

Some titles never call Update directly. They draw into a bitmap that the render
path reads, so a runtime that only presents on Update will show nothing.

## Bitmap and font interfaces

<!-- BEGIN GENERATED: IBitmap -->
_Generated from the public SDK header `AEEIBitmap.h`. Inheritance chain: IQI, IBitmap._

Base slots: **IQI → IBitmap**, so slot 0 is the first method of IQI and the first method of IBitmap starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | RGBToNative | NativeColor | this, RGBVAL rgb |
| 4 | NativeToRGB | RGBVAL | this, NativeColor clr |
| 5 | DrawPixel | int | this, unsigned x, unsigned y, NativeColor color, AEERasterOp rop |
| 6 | GetPixel | int | this, unsigned x, unsigned y, NativeColor *pColor |
| 7 | SetPixels | int | this, unsigned cnt, AEEPoint *pPoint, NativeColor color, AEERasterOp rop |
| 8 | DrawHScanline | int | this, unsigned y, unsigned xMin, unsigned xMax, NativeColor color, AEERasterOp rop |
| 9 | FillRect | int | this, const AEERect *prc, NativeColor color, AEERasterOp rop |
| 10 | GetInfo | int | this, AEEBitmapInfo *pinfo, int nSize |
| 11 | CreateCompatibleBitmap | int | this, IBitmap **ppIBitmap, uint16 w, uint16 h |
| 12 | SetTransparencyColor | int | this, NativeColor color |
| 13 | GetTransparencyColor | int | this, NativeColor *pColor |
<!-- END GENERATED: IBitmap -->

<!-- BEGIN GENERATED: IFont -->
_Generated from the public SDK header `AEEIFont.h`. Inheritance chain: IQI, IFont._

Base slots: **IQI → IFont**, so slot 0 is the first method of IQI and the first method of IFont starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | GetInfo | int | this, AEEFontInfo *pinfo, int nSize |
<!-- END GENERATED: IFont -->

## Notes for implementers

- SetClipRect is slot 18. It is the single most-called display method in some
  titles, and getting the slot wrong silently corrupts drawing rather than
  crashing.
- GetDeviceBitmap hands back a reference the caller must release, so the reference
  count of the returned bitmap matters.
- DrawText takes a background rectangle and flags. Titles use the flags to draw
  shadowed or inverted text, so ignoring them produces readable but visibly wrong
  UI.
- DIB colour depth matters. A runtime that always allocates 32-bit surfaces
  breaks titles that blit 8-bit palettised data with BitBlt.

Evidence: slots and signatures from the public SDK header. Expected sequence from
real titles and from the SDK sample sources.
