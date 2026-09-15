# z33b0tek

A technical reference for the Zeebo console (Qualcomm MSM7201A, BREW 4.0.2,
Adreno 130), written for emulator developers and hardware hackers.

## Layout

- `pages/*.md` — source of truth for the published site. Plain markdown.
- `tools/gen_vtables.py` — regenerates the IShell and IDisplay vtable pages from
  public BREW SDK headers.
- `gen.py` — builds `site/` from `pages/`, then runs a lint that fails the build
  if any private or third-party identifier leaks into the output.
- `site/` — generated HTML. Not committed.

## Build

```sh
python3 gen.py
# site/ contains the reference, index.html is the entry point
```

## Rules

- Describe the platform, never a particular emulator implementation.
- No compatibility lists, no title matrices.
- No local paths, no author names, no internal document names.
- Every claim is either a public SDK fact, a measurement from a real binary or
  firmware dump, or is marked as unverified.
