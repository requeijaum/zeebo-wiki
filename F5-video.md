# F5 — vídeo [EM CURSO]
## [CONF] `gl_hle.cpp` clone (15/09)
- EGL toyosan: QueryInterface/GetError(Success)/GetDisplay/Initialize/QueryString/Terminate/
  ChooseConfig/CreateWindowSurface/CreatePbufferSurface/DestroySurface/GetConfigAttrib/
  QuerySurface/CreateContext/DestroyContext/MakeCurrent/GetColorBufferQualcomm/GetProcAddress/SwapBuffers.
- GL: Clear, ClearColorx, DepthRange, Viewport, Enable (+ resto abaixo da linha 842 — continuar).
- GL (resto): GetIntegerv, Delete/Bind/ActiveTexture(+Client), CullFace/FrontFace, ShadeModel, Hint,
  Finish, GetError, PixelStorei, Material/Light(x/fv/xv), LightModel, StencilFunc/Op,
  TexParameterx, TexImage2D/SubImage2D, CompressedTexImage2D.
- Builders: `BuildGl/BuildEgl/BuildSurfaceManip/BuildGles11` montam vtables.
- Backend: `soft_gl_backend` + `gl_backend.h`; `SyncSurfaceColorBuffer` guest via callback.
## [CONF] draw path (linhas 842-1468)
- Estado: Enable/Disable, Alpha/Blend/DepthFunc, ClearDepthx, DepthMask.
- Matrizes f/x: MatrixMode, LoadIdentity, Load/MultMatrix, Ortho/Frustum, Translate/Scale/Rotate,
  Push/PopMatrix, Color4, TexEnv.
- Draw: DrawTexxOES, Vertex/Color/TexCoord/NormalPointer, Enable/DisableClientState,
  `ExtractArrays`, DrawArrays/DrawElements, GenTextures, GetString.
## [CONF] fork `curupira/core/video/rasterizador.h` + `core/brew/tela.h` (15/09)
- Rasterizador software escreve DIRETO na `tela` (não buffer próprio); bateria mede PIXELS nela.
  Antes: 0 px em 62/62; IGL recusava DrawArrays/Elements (124 pedidos).
- TRIANGLES/STRIP/FAN, edge-func + top-left, interp afim cor/texcoord, NEAREST+clamp, depth, cull.
- Fora (declarado): perspectiva, frustum clip (w<=0 descarta), blend/alpha/stencil/dither,
  luz/nevoa, mipmap/bilinear, REPEAT (clamp + registra). Caps pedidas vão p/ traço.
## Pendente
- scanout MDDI real (apresentação host); gate DD frame não-uniforme guest-derivado.
## [CONF] 2ª fonte: `ZEEBX_GL_CLEANROOM_DIFF.md` (LLE, 15/09)
- ABI legada: IGL 80 slots (sem `this`), IEGL 28 slots (GetProcAddress=8, SwapBuffers=26).
- ABI nova: IGLES11 148 / IEGL11 31 (com `this`, SwapBuffers=25) — NÃO colapsar; promoção exige ClassID/IID + vtable viva.
- RGB565 nativo; filtro inicial linear, wrap repeat; `gl*Pointer` ≠ enable; textura modula cor.
- Gaps: ATITC/paletizados, GetString em mem guest, ProcAddress VAs, SurfaceManip slot 4, near-plane, blending/stencil restantes, present contínuo.
