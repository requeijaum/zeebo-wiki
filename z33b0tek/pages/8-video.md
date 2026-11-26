# Video: EGL, OpenGL ES and the IGL layer

The GPU is an Adreno 130 from the Yamato generation.
Titles reach it through OpenGL ES 1.x, with EGL underneath for display, configuration, surface and context management.

## API stack

| Layer | Role | Why it matters |
|---|---|---|
| OpenGL ES 1.0 / 1.1 | fixed-function pipeline used by every observed title | defines the call set a title can use |
| EGL | display, configuration, surface and context management | nothing renders until a context is current |
| Qualcomm IGL and IEGL | vendor layer that carries the ES entry points to the hardware | the vtable a title actually calls through |
| MDDI | display serial interface between the SoC and the panel | where a finished frame leaves the SoC |

The vendor layer is the one that surprises people.
A title does not call the standard ES entry points directly through a library: it calls through a vtable supplied by the platform.
That is why the slot layout matters as much as the call semantics, and why an implementation can have every function correct and still draw nothing.

## EGL call set observed in use

| Area | Calls |
|---|---|
| Display | GetDisplay, Initialize, QueryString, Terminate, GetError, QueryInterface |
| Configuration | ChooseConfig, GetConfigAttrib |
| Surface | CreateWindowSurface, CreatePbufferSurface, QuerySurface, DestroySurface |
| Context | CreateContext, DestroyContext, MakeCurrent |
| Presentation | SwapBuffers |
| Vendor | GetColorBufferQualcomm, GetProcAddress |

Which of these a bring-up needs first, in order:

| Stage | Calls | Why |
|---|---|---|
| 1 | GetDisplay, Initialize, GetError | nothing works before the display object exists |
| 2 | ChooseConfig, GetConfigAttrib | the title selects a pixel format before creating anything |
| 3 | CreateWindowSurface, CreateContext, MakeCurrent | rendering needs a current context |
| 4 | QueryString, GetProcAddress | titles probe for extensions and behave differently without them |
| 5 | SwapBuffers, GetColorBufferQualcomm | presentation and the vendor colour buffer path |

GetError deserves its own note.
Titles call it after most GL operations and treat GL_NO_ERROR as a signal to continue.
A runtime that leaves a stale error value set makes a title take its fallback path and produce visibly wrong output with no other symptom.

## GL call set observed in use

| Group | Calls |
|---|---|
| Clear and colour | Clear, ClearColorx, ClearColorf, ClearDepthx |
| Depth | DepthFunc, DepthMask, DepthRange |
| Raster | Viewport, CullFace, FrontFace, ShadeModel, Hint, PixelStorei |
| Blend and test | Enable, Disable, AlphaFunc, AlphaFuncx, BlendFunc, StencilFunc, StencilOp |
| Matrices | MatrixMode, LoadIdentity, LoadMatrixf, LoadMatrixx, MultMatrixf, MultMatrixx, Orthof, Orthox, Frustumf, Frustumx, Translatef, Translatex, Scalef, Scalex, Rotatef, Rotatex, PushMatrix, PopMatrix |
| Vertex arrays | VertexPointer, ColorPointer, TexCoordPointer, NormalPointer, EnableClientState, DisableClientState, DrawArrays, DrawElements |
| Textures | GenTextures, BindTexture, DeleteTextures, ActiveTexture, ClientActiveTexture, TexImage2D, TexSubImage2D, CompressedTexImage2D, TexParameterx, TexEnvx, TexEnvfv, TexEnvxv |
| Lighting and material | Materialx, Materialxv, Materialfv, Lightx, Lightxv, Lightfv, LightModelx, LightModelxv, Color4f, Color4x |
| Misc | GetString, GetIntegerv, GetError, Finish, DrawTexxOES |

## Extension gating

Titles probe the extension set before initialising 3D.
They abandon rendering when a required name is absent.
Measured across the library:

- A group of titles checks `GL_OES_draw_texture` in `GetString(GL_EXTENSIONS)` before creating their render target.
- Without it they stop at a clear error screen.
- `glDrawTex*OES` is the window-coordinate blit they use to present.
- The Z-Wheel store UI probes for `GL_ATI_texture_compression_atitc` before building its stage.
- The stage textures are ATITC-compressed `.qxt` files.
- Announcing an extension without serving its entry points makes the title call a function that does not exist.
- Omitting a served one makes it refuse to start.
- The two sides must ship together.

## Qualcomm vendor extensions

The vendor layer is ATI/Qualcomm imageon silicon.
Titles carry their own extension name tables, decoded from shipped modules:

- Screen blit through `GL_OES_draw_texture`.
- Matrix palette through `glMatrixIndexPointerOES` and `glWeightPointerOES`.
- Off-screen targets through `GL_OES_framebuffer_object`.
- Vertex buffers are Qualcomm-named, not ARB.
- The names are `glBindBufferQUALCOMM` and `glBufferDataQUALCOMM`.
- ATI mesh lists arrive as `glMeshListATI` and `glDrawVertexBufferObjectATI`.
- Texture compression is `GL_ATI_texture_compression_atitc`, the ATITC codec.
- The platform's own extension list announces ATITC together with `GL_ATI_imageon_misc`.
- EGL surface extras are Qualcomm-named as well.
- They are `eglSurfaceColorKeyEnableQUALCOMM`, `eglSurfaceTransparency*` and `eglCreateCompositeSurfaceQUALCOMM`.
- Two vendor interfaces are reached by IID, `EGLSurfaceManip` and `GLESImageonExt`.
- The composite surface path goes through the vendor EGL object.

An implementation that announces only what it serves avoids both failure modes.

## IGL and IEGL ABI generations

Two incompatible vtables exist.
They must not share a constant.

| Generation | IGL slots | IEGL slots | Method calling | GetProcAddress slot | SwapBuffers slot |
|---|---|---|---|---|---|
| Legacy | 80 | 28 | no this pointer | 8 | 26 |
| ES 1.1 | 148 | 31 | this pointer, pointer return | not at the same position | 25 |

Choosing the wrong generation shifts every slot.
A runtime must decide from the observed class ID or interface ID plus a live vtable, not from a size heuristic.

## State defaults and pipeline requirements

| Item | Default or requirement |
|---|---|
| Surface format | RGB565 native; normalising to RGBA8 internally is acceptable |
| Texture filter | linear at start |
| Texture wrap | repeat at start |
| Depth test | LESS, with depth writes enabled |
| Blend | SRC_ALPHA, ONE_MINUS_SRC_ALPHA |
| Texture modulation | sampled texel multiplies the current or array colour |
| Vertex arrays | gl*Pointer changes the descriptor but does not enable the array |
| Pixel storage | default pack and unpack alignment is 4, which matters for 8-bit data |

The separation between pointer setup and array enable is a common bring-up bug.
A runtime that treats glVertexPointer as an enable draws geometry the title never asked for, or draws nothing when the title enables arrays it never filled.

## Software rasterizer minimum

To turn guest draw calls into pixels:

| Step | Requirement |
|---|---|
| Clear | glClear fills with the clear colour |
| Primitives | TRIANGLES, TRIANGLE_STRIP and TRIANGLE_FAN |
| Rasterisation | bounding-box scan with an edge function and the top-left rule |
| Attribute interpolation | per-vertex colour and texture coordinates |
| Texture sampling | GL_NEAREST with clamp addressing |
| Depth | test against the depth buffer when GL_DEPTH_TEST is enabled |
| Culling | face orientation from glCullFace and glFrontFace |

The top-left rule is not optional.
Without it, neighbouring triangles either double-write shared edges or leave visible seams.

Known deviations worth declaring rather than hiding:

- Affine interpolation, not perspective corrected, so large oblique polygons show stretched texture. 
- A triangle with any vertex at w <= 0 is discarded instead of clipped against the near plane. 
- No blending, alpha test, stencil, dither, polygon offset, scissor or per-channel colour mask. 
- No lighting and no fog. 
- No mipmaps and no bilinear filtering. 
- Repeat wrap is not implemented;
  coordinates outside 0..1 are clamped.

Each of those shows up as a specific visual defect, so it is better to name them than to let a tester rediscover them one at a time.

## Compressed textures

Titles ship ATITC-compressed textures in RGB and RGBA variants, plus palette formats.
A compressed-texture decoder is required for any title-driven render path.

| Format | Bytes per block | Notes |
|---|---|---|
| ATITC RGB | fixed ratio block | no alpha; treating the block as RGBA shifts the colour channels |
| ATITC RGBA | fixed ratio block | alpha in the same block |
| Palette | index plus palette | palette lives in the payload or in a companion resource |

Skipping the decoder produces noise that looks like a memory bug: correct geometry, garbage colours, no crash.
Confirm the diagnosis by dumping the raw block and checking whether the size matches the compressed ratio or the uncompressed pixel count.
If it matches the compressed ratio, the data is compressed and the render path is not at fault.

## Measured on one unit

A dump taken from a real console (platform id 16000) gives the platform's own answers.

| Item | Value |
|---|---|
| GL_VENDOR | QUALCOMM, Inc. |
| GL_RENDERER | Q3Dimension MSM7500 01.02.37 0 4.0.0 |
| GL_VERSION | OpenGL ES 1.0-CM |
| ES 1.0 interface | obtained |
| ES 1.1 interface | NULL on this unit |
| Maximum texture size | 1024 (10 mipmap levels) |
| Texture units | 2 |
| Vertex units (matrix palette) | 4 |
| Depth bits | 16 |
| Stencil bits | 0 |
| EGL version string | 2.07.050110.34681 |

EGL extensions announced: `EGL_QUALCOMM_COLOR_BUFFER`, `EGL_QUALCOMM_get_color_buffer`, `EGL_EXT_swap_control`, and the surface extras scale, rotate, transparency, color_key and overlay.

GL extensions announced:

- `GL_ARB_texture_env_combine`, `_crossbar`, `_dot3`, `GL_ARB_texture_mirrored_repeat`, `GL_ARB_vertex_buffer_object`.
- `GL_ATI_extended_texture_coordinate_data_formats`, `GL_ATI_imageon_misc`, `GL_ATI_texture_compression_atitc`.
- `GL_EXT_blend_equation_separate`, `_func_separate`, `_minmax`, `_subtract`, `GL_EXT_stencil_wrap`.
- `GL_OES_byte_coordinates`, `_compressed_paletted_texture`, `_draw_texture`, `_fixed_point`, `_matrix_palette`, `_point_size_array`, `_point_sprite`, `_read_format`, `_single_precision`, `_vertex_buffer_object`.
- `GL_QUALCOMM_vertex_buffer_object`.

Declared in the SDK headers or named by shipped modules, but absent from the list:

- `GL_OES_framebuffer_object` and therefore `glGenerateMipmapOES`.
- `GL_OES_query_matrix`, `GL_OES_texture_cube_map`, `GL_QUALCOMM_IMAGEON`.
- `GL_OES_texture_mirrored_repeat` and the `GL_OES_blend_*` names; the ARB and EXT forms are the ones present.
- Point parameters, `EGL_QUALCOMM_get_power_level` and `get_color_buffer_info`.

This agrees with the developer guide, which lists no render-to-texture, no automatic mipmaps and no matrix get.

Interface consequence, read from the SDK wrapper source:

- The wrapper asks the vendor object for the ES 1.0 and ES 1.1 interfaces separately.
- Entry points that exist only in 1.1 (`glTexParameteri` and `glTexEnvi` among them) check the 1.1 pointer and do nothing when it is NULL.
- There is no error and no fallback to the 1.0 interface.
- On a unit like this one, use the fixed-point forms `glTexParameterx` and `glTexEnvx`, which have a 1.0 path.

Behaviour checks on the same unit:

- `glTexParameterx` with `GL_MIRRORED_REPEAT` on S and T leaves `GL_NO_ERROR`.
- Drawing with the default filter and with `GL_LINEAR` raises no error.
- A render test using mirrored repeat with `GL_LINEAR` on a rectangular texture, run in an earlier round, was reported to trip the console watchdog.
  The cause was not isolated, and the parameter-only test above passed.
- The stencil plane reports 0 bits while `GL_EXT_stencil_wrap` is announced.
  The developer guide describes depth as 16 bits and stencil as an optional 4 bits, so 0 most likely reflects the configuration chosen, not a hardware limit.
  The dump does not record that configuration.

Two cautions:

- `GL_RENDERER` is the active driver label.
  It names an MSM7500 part, while this reference names the SoC as MSM7201A.
  A driver string can describe a board family or an older support package, so GL alone does not settle the silicon.
  Both names are kept until a register read decides it.
- One unit and one firmware were measured.
  The ES 1.1 interface being NULL does not rule it out on other releases.

## Scanout

The display controller path is MDDI.
The display list carries a priority pointer to a list in guest memory.
Frame output must originate from guest-written surfaces;
a host-owned buffer will produce a frame that the title did not draw.

Evidence: call sets observed in real titles and in the SDK.
IGL and IEGL slot counts measured on shipped objects and confirmed against live vtables.
Pipeline defaults from the OpenGL ES 1.x specification and from observed behaviour.
