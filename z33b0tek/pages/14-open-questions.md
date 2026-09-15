# Open Questions

Each item states what is unknown and what evidence would close it.
Nothing here should be presented as settled behaviour.

## Container formats

Closed 2026-09-15:

- The BAR header offset 8 is the registry start; the fields at 0..28 are now confirmed (magic 0x0011, version fields, registry, index, data and end offsets). The same header serves the MIF.
- The full MIF layout is settled: same container as the BAR (records of 8 bytes), string payloads with 0x03 / UTF-16 BOM markers, resource IDs 6/7/8 for company/author/version, possible trailing footer. Basis: 62 shipped MIF files parsed with offsets cross-checked against payload signatures.
- Container survey of the 62-title library: PAKZ (magic PACK, LZMA_ALONE payloads), ZTEX (.tex), QX (.qxt/.qxa/.qxm), FNZ fonts, NAMCO 3D (.n3d/.nsk), BIGF/BIG4 (.big/.viv), JDLZ (.lzc), SHPM (.msh), IANN (.rwh), SWERVE/SWVARC (.m3g/.sar). The BIGF/BIG4/JDLZ/SHPM set appears only in the resource set of a single title; PAKZ is exclusive to the first-party engine family.

Still open:

| Question | Evidence that would close it |
|---|---|
| Where exactly the icon and launch parameters live for the store list | a title whose MIF resource directory is walked by the shell, with the walk traced |
| Are there further container types in unreleased or homebrew builds | any build outside the 62-title library with a new magic |
| Does any shipped title actually read the MIF directory instead of the runtime registry for its class ID | a title whose load path is traced back to a MIF payload |

## Runtime

| Question | Evidence that would close it |
|---|---|
| Which interface is the third pointer in the ambient application context? | a title that calls through it with a recognisable method sequence |
| May the runtime run a due timer while an applet callback is executing? | a title whose progress depends on the answer, plus a control run with the opposite policy |
| How does a module that mixes ARM and Thumb behave under a JIT? | a title whose entry path crosses instruction sets, traced at the transition |
| What is the exact applet teardown order on forced exit? | a title that allocates in start and frees in stop, with the calls logged |

The timer policy question is the one that most often decides whether a title reaches gameplay or stalls at its first frame.

## Video

| Question | Evidence that would close it |
|---|---|
| What promotes an object from the legacy to the ES 1.1 IGL ABI? | an observed class ID or interface ID plus a live vtable, on a title that uses ES 1.1 |
| Which extension entry points does GetProcAddress return? | the returned addresses read from guest memory on a real title, then validated |
| What does the surface manipulation interface do at slot 4? | a live object reached through QueryInterface, with the call traced |
| Which fragment states are load-bearing for real titles? | per-title runs that enumerate the states each title sets |

The extension question matters because assuming a fixed extension set produces subtle rendering differences rather than obvious failures.

## Audio

| Question | Evidence that would close it |
|---|---|
| Which decoder each title requires | a title run with media creation instrumented, showing the class ID it requests and the samplerate it sets |
| The exact completion notification order | a title traced from play to callback, with the callback parameters recorded |
| How simultaneous channels are expected to be mixed | a title that plays music and effects at once, with both captured and compared against a reference recording |
| Whether the sound bank ships with titles or with the firmware | a survey of installed applications listing which ones carry a bank and which rely on a shared one |
| What happens when a title requests a class the runtime refuses | a title run with creation forced to fail, checking whether it degrades or stalls |

The decoder question is the practical one.
A runtime can be correct in every observable way and still be judged broken because the music does not play.

## Storage

| Question | Evidence that would close it |
|---|---|
| Where exactly is the boundary between firmware boot needs and title execution needs? | a title run against a minimal VFS-only backend, with the failure modes recorded |
| How is the journal recovered after an unclean shutdown? | a dump with an open journal, plus the recovery path traced to completion |
| Which paths are writable, and by whom? | a title that writes outside its private directory, checking the error it receives |
| What does the shell do when free space is reported as zero? | a title run with the free-space query returning zero, watching whether it degrades or refuses to start |
| Are there paths that only the OEM application can read? | a direct read attempt against each documented prefix, from title context |

Keeping that boundary explicit prevents the most expensive kind of scope creep: building a full storage stack for titles that only need a directory tree.

## Method

Two habits keep this list useful rather than decorative:

- Every unknown gets a named artefact that would close it.
  An entry without one is a wish, not a question.
- Every claim elsewhere in this reference is either a public SDK fact, a measurement from a real binary or dump, or is labelled as unconfirmed.
  When a claim is refuted, it moves here as a resolved item with the refutation recorded, so the same wrong answer is not rediscovered.
