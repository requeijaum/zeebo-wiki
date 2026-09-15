# Video: EGL, OpenGL ES and the IGL/EGL Oberon layer

Zeebo renders through OpenGL ES 1.x. The GPU is an Adreno 130 (Yamato class).
Titles reach it through two stacked API layers.

## API stack

1. OpenGL ES 1.0 / 1.1 entry points, called by the game.
2. EGL for display, configuration, surface and context management.
3. A Qualcomm layer that the SDK headers call IGL and IEGL, exposed as two
   different ABIs depending on generation.

## EGL call set seen in use

QueryInterface, GetError, GetDisplay, Initialize, QueryString, Terminate,
ChooseConfig, GetConfigAttrib, CreateWindowSurface, CreatePbufferSurface,
QuerySurface, DestroySurface, CreateContext, DestroyContext, MakeCurrent,
GetColorBufferQualcomm, GetProcAddress, SwapBuffers.

## GL call set seen in use

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

## IGL and IEGL ABI generations

Two incompatible vtables exist. They must not share a constant.

| Generation | IGL slots | IEGL slots | Method calling | GetProcAddress slot | SwapBuffers slot |
|---|---|---|---|---|---|
| Legacy | 80 | 28 | no this pointer | 8 | 26 |
| Newer (ES 1.1) | 148 | 31 | this pointer, pointer return | not at the same position | 25 |

- In the legacy ABI the gl* methods do not receive a this pointer.
- A runtime must decide the ABI from the observed class ID or interface ID and a
  live vtable, not from a vtable size heuristic.

## State defaults and pipeline requirements

- Native surface format is RGB565. A software rasterizer may normalise to RGBA8.
- Initial texture filter is linear. Initial wrap mode is repeat.
- Depth test uses LESS, with depth writes enabled.
- Blend is SRC_ALPHA and ONE_MINUS_SRC_ALPHA.
- Texture sampling multiplies the bound texture by the current or array colour.
- gl*Pointer changes the array descriptor but does not enable the array;
  glEnableClientState is a separate call.

## Software rasterizer minimum

To produce non-uniform frames from guest draw calls:

- glClear with the clear colour.
- TRIANGLES, TRIANGLE_STRIP and TRIANGLE_FAN, by bounding-box scan with an edge
  function and the top-left rule so neighbouring triangles neither double-write
  nor leave a seam.
- Per-vertex colour and texture coordinate interpolation.
- Texture sampling with GL_NEAREST and clamp.
- Depth test when GL_DEPTH_TEST is enabled.
- Face culling from glCullFace and glFrontFace.

Known deviations to declare rather than hide:

- Affine interpolation, not perspective corrected. Large oblique polygons show
  stretched texture.
- A triangle with any vertex at w <= 0 is discarded instead of clipped against
  the near plane.
- No blending, alpha test, stencil, dither, polygon offset, scissor or per-
  channel colour mask.
- No lighting and no fog.
- No mipmaps and no bilinear filtering.
- Repeat wrap is not implemented; coordinates outside 0..1 are clamped.

## Compressed textures

Titles ship ATITC-compressed textures in RGB and RGBA variants, plus palette
formats. A decoder is required for a title-driven render path.

## Scanout

The display controller path is MDDI. The display list carries a priority pointer
to a list in guest memory. Frame output must come from guest-written surfaces,
not from a host-owned buffer.
