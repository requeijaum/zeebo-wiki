# z33b0tek

A technical reference for the Zeebo console (Qualcomm MSM7201A, BREW 4.0.2,
Adreno 130), written for emulator developers and hardware hackers.

## Layout

| Path | Role |
|---|---|
| `pages/*.md` | source of truth for the published site |
| `tools/gen_interfaces.py` | regenerates vtable tables from public SDK headers |
| `tools/audit.py` | enforces the house standard on `pages/` |
| `gen.py` | builds `site/` and lints the output |
| `site/` | generated HTML, not committed |

## Build

```sh
python3 tools/audit.py pages        # standard check, exits 1 on violation
python3 gen.py                      # build site/, exits 1 on leaked identifier
python3 -m http.server -d site 8000
```

The GitHub Actions workflow runs both checks before deploying, so a page that
breaks the standard or leaks a private identifier never reaches the site.

## House standard

Enforced by `tools/audit.py`:

| Rule | Requirement |
|---|---|
| R1 | one H1 per page |
| R2 | an intro of at least two lines before the first section |
| R3 | every section has at least six lines (evidence lines exempt) |
| R4 | prose wraps at 100 characters (tables and code exempt) |
| R5 | generated blocks are filled, not left empty |
| R6 | no private or third-party identifiers |

## Content rules

- Describe the platform, never a particular emulator implementation.
- No compatibility lists and no title matrices.
- Good sections end with an evidence line: what the claim rests on.
- Every unknown belongs in the open questions page with the artefact that would
  close it.
