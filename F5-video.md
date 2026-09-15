# F5 — Video [IN PROGRESS]
## [CONF] `gl_hle.cpp` clone (09-15)
- Full EGL: QueryInterface/GetError(Success)/GetDisplay/Initialize/QueryString/Terminate/
  ChooseConfig/CreateWindowSurface/CreatePbufferSurface/DestroySurface/GetConfigAttrib/
  QuerySurface/CreateContext/DestroyContext/MakeCurrent/GetColorBufferQualcomm/GetProcAddress/SwapBuffers.
- GL state: Clear, ClearColorx/f, DepthRange/Func/Mask, Viewport, Enable/Disable,
  AlphaFunc(x), BlendFunc, ClearDepthx.
- Matrix f/x: MatrixMode, LoadIdentity, Load/MultMatrix, Ortho/Frustum, Translate/Scale/Rotate,
  Push/PopMatrix, Color4, TexEnv(fv/x/xv).
- Textures/light/stencil: GetIntegerv, Delete/Bind/ActiveTexture(+Client), CullFace/FrontFace,
  ShadeModel, Hint, Finish, GetError, PixelStorei, Material/Light(x/fv/xv), LightModel,
  StencilFunc/Op, TexParameterx, TexImage2D/SubImage2D, CompressedTexImage2D.
- Builders: `BuildGl/BuildEgl/BuildSurfaceManip/BuildGles11` assemble vtables.
- Backend: `soft_gl_backend` + `gl_backend.h`; `SyncSurfaceColorBuffer` via guest callback.
## [CONF] draw path
- DrawTexxOES, Vertex/Color/TexCoord/NormalPointer, Enable/DisableClientState,
  `ExtractArrays`, DrawArrays/DrawElements, GenTextures, GetString.
## [CONF] parked-fork `curupira/core/video/rasterizador.h` + `core/brew/tela.h` (09-15)
- Software rasterizer writes DIRECTLY into `tela` (no private buffer); the bateria tool measures
  PIXELS there. Before: 0 px on 62/62; IGL refused DrawArrays/Elements (124 requests).
- TRIANGLES/STRIP/FAN, edge functions + top-left rule, affine color/texcoord interp, NEAREST+clamp,
  depth test, face culling.
- Declared OUT (not silently missing): perspective, frustum clip (w<=0 discarded), blend/alpha/stencil/dither,
  lighting/fog, mipmaps/bilinear, REPEAT (clamped + logged). Requested caps go to the trace.
## [CONF] 2nd source: `ZEEBX_GL_CLEANROOM_DIFF.md` (LLE, 09-15)
- Legacy ABI: IGL 80 slots (no `this`), IEGL 28 slots (GetProcAddress=8, SwapBuffers=26).
- New ABI: IGLES11 148 / IEGL11 31 (with `this`, SwapBuffers=25) — NEVER collapse; promotion
  requires observed ClassID/IID + live vtable.
- RGB565 native; initial filter linear, wrap repeat; `gl*Pointer` != enable; texture modulates color.
- Gaps: ATITC/palettized, GetString in guest memory, ProcAddress VAs, SurfaceManip slot 4,
  near-plane, remaining blend/stencil, continuous present.
## Pending
- Real MDDI scanout (host presentation); DD non-uniform guest-derived frame gate.
