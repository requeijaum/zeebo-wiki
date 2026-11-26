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
## [CONF] dump em hardware real: EGL/GLES (26/11, 4 dumps do usuario)
- Fonte: dump de um console real (4 rodadas; so a 4a testa wrap e filtro). Nao e header nem codigo.
  Origem: homebrew do Pedro (Hardwarelandia), via Rafael. Rodadas 1-3 (25/11) tambem arquivadas, sem edicao,
  em sonic-adventure-zeebo/ports/zeebo/docs/zeebo-gl-extensions-dump*-hardwarelandia.txt; a 4a so existe em Downloads.
- GL_VENDOR QUALCOMM; GL_RENDERER `Q3Dimension MSM7500 01.02.37 0 4.0.0`; GL_VERSION `OpenGL ES 1.0-CM`.
- AEEIID_GLES10 NON-NULL, AEEIID_GLES11 NULL (via GLES_Init/QEGL) nesta unidade.
- GL_MAX_TEXTURE_SIZE 1024 (=> 10 niveis de mipmap, MAX_MIPMAP_LEVEL medido 10); TEXTURE_UNITS 2; MAX_VERTEX_UNITS_OES 4; depth 16 bits; stencil 0 bits.
- AEE_DEVICE_PLATFORM_ID 16000.
- EGL_VERSION `2.07.050110.34681`; EGL_EXTENSIONS: QUALCOMM_COLOR_BUFFER, get_color_buffer,
  EXT_swap_control, QUALCOMM_surface_{scale,rotate,transparency,color_key,overlay}.
- GL_EXTENSIONS (24): ARB_texture_env_{combine,crossbar,dot3}, ARB_texture_mirrored_repeat,
  ARB_vertex_buffer_object, ATI_extended_texture_coordinate_data_formats, ATI_imageon_misc,
  ATI_texture_compression_atitc, EXT_blend_{equation_separate,func_separate,minmax,subtract},
  EXT_stencil_wrap, OES_{byte_coordinates,compressed_paletted_texture,draw_texture,fixed_point,
  matrix_palette,point_size_array,point_sprite,read_format,single_precision,vertex_buffer_object},
  QUALCOMM_vertex_buffer_object.
- NAO anunciados: GL_OES_framebuffer_object, qualquer coisa ES 1.1 (GLES11 NULL).
- glTexParameterx(S/T, GL_MIRRORED_REPEAT): GL_NO_ERROR. Draw com filtro default e GL_LINEAR: sem erro.
- Stencil 0 bits com EXT_stencil_wrap anunciada. Dev Guide §7.1.1/§7.4.1: depth 16 bits e stencil de 4 bits OPCIONAL;
  0 provavelmente reflete a config escolhida pelo homebrew, nao o limite do HW. NAO verificado (dump nao mostra a config EGL).
- O dump traz a nota RENDERER_VS_GUIDE: o guia usado pelo autor do dump diz MSM7201A; GL_RENDERER e o rotulo do driver.
- Ausentes no console, apesar de declarados em glESext.h/EGLext.h do SDK (ou anunciados pelo zeebx):
  OES_framebuffer_object (=> sem glGenerateMipmapOES), OES_query_matrix, OES_texture_cube_map,
  OES_texture_mirrored_repeat (existe a ARB), OES_blend_* (existem as EXT), GL_QUALCOMM_IMAGEON,
  point parameters, EGL_QUALCOMM_get_power_level, get_color_buffer_info. Bate com Dev Guide Tabela 7-1
  (sem render p/ textura, sem mipmap automatico, sem matrix get). Fonte do cruzamento: doc do port SA1 §3b/§4.
- [CONF] wrapper SDK (GLES_1x.c / GLES_1x_support.h, SDK BREW 4.0.2): GLES_Init pede AEEIID_GLES10 e AEEIID_GLES11
  separadas; funcoes so-1.1 (macros GL11_FUNC_*: glTexParameteri, glTexEnvi, Get*) fazem `if (NULL != GPIGLES11)`
  e nao fazem NADA caso contrario (sem erro, sem fallback). Com GLES11 NULL, sao no-ops silenciosos;
  usar glTexParameterx/glTexEnvx (caminho 1.0). Achado do port SA1 (zstrip.c, commit 0deba05).
- Relato (nao e dump): o teste de render em GLES10 da rodada 3 deu WATCHDOG no console; causa nao isolada.
  Na 4a rodada os mesmos draws (filtro default e LINEAR) passaram sem erro => provavel defeito do teste antigo.
- Pendente: rodadas 2 e 3 pularam MIRRORED_REPEAT (UNKNOWN / SKIPPED SAFE MODE); so a 4a o mediu.
## Pending
- Real MDDI scanout (host presentation); DD non-uniform guest-derived frame gate.
