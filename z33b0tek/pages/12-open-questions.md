# Open Questions

Each item below is unresolved and stated with the artefact that would close it.

## Container formats

- MIF full layout. Resource tables, class IDs and privilege bits are unknown.
  Closing evidence: a documented MIF with a resource table whose offsets are
  independently confirmed by a title that loads from it.
- BAR sub-table at header offset 8. Its contents are unused by anything decoded
  so far. Closing evidence: a dump where that sub-table holds plausible entries.

## Runtime

- The ambient application context exposes a third pointer beyond IShell and
  IDisplay. Which interface it represents is unknown. Closing evidence: a title
  that calls through it with a recognisable method sequence.
- Timer preemption policy. Whether the shell may run a due timer callback while
  an applet callback is still executing determines the shape of the main loop.
  Closing evidence: a title whose busy wait depends on it.
- Thumb interworking. Mixed ARM and Thumb modules need a core that switches
  state correctly. Closing evidence: a title whose entry path crosses between
  instruction sets.

## Video

- Newer IGL and IEGL ABI promotion criteria. Deciding the ABI from a live vtable
  plus an observed class ID is required; a size heuristic is not enough.
- GetProcAddress return values. Extension entry points must be read from the
  guest and registered dynamically rather than assumed.
- Surface scaling. One surface manipulation interface is only reachable after a
  QueryInterface on a live object.
- Fragment pipeline gaps: alpha test, remaining depth functions and blend
  factors, culling edge cases, scissor and texture environment.

## Audio

- Which decoder a given title actually requires. Closing evidence: a title that
  reaches playback with the media object instrumented, showing the class ID it
  requests and the bytes it feeds.

## Storage

- Firmware boot requires a full NAND and EFS2 model. Title execution does not.
  The boundary between the two is only partly mapped.
