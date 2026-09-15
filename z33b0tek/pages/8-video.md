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

## Scanout

The display controller path is MDDI.
The display list carries a priority pointer to a list in guest memory.
Frame output must originate from guest-written surfaces;
a host-owned buffer will produce a frame that the title did not draw.

Evidence: call sets observed in real titles and in the SDK.
IGL and IEGL slot counts measured on shipped objects and confirmed against live vtables.
Pipeline defaults from the OpenGL ES 1.x specification and from observed behaviour.
