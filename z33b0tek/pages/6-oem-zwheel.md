# OEM Layer: Z-Wheel

The Zeebo ships an OEM application that hosts the store user interface and the
carousel of installed titles. It is a normal BREW applet with an OEM class ID.

## Identity and VFS layout

| Item | Value |
|---|---|
| App ID | 274755 |
| Class ID | 0x01070798 |
| Registered vendor string | TECTOY |
| Metadata file | fs:/mif/274755.mif |
| Module directory | fs:/mod/274755/ |
| Private applet directory | fs:/~0x01070798/ |
| License and keys | fs:/~0x01070798/tectoyli.brf |
| Shell configuration | fs:/mod/274755/tectoy.cfg and uiconfig.xml |

## Embedded SQLite databases

The OEM app stores its catalogue in standard SQLite 3 files with 1024-byte
pages. The schema is fixed and small enough to reimplement.

tt_game_info, the carousel catalogue:

```sql
CREATE TABLE GAMEINFO (
    game_id       INTEGER PRIMARY KEY,
    class_id      INTEGER,
    playcount     INTEGER,
    dt_download   INTEGER,
    dt_lastplayed INTEGER,
    boxart_path   TEXT,
    flags         INTEGER,
    size          INTEGER,
    UNIQUE(game_id, class_id)
);

CREATE TABLE TITLETEXT (
    game_id       INTEGER,
    lang_id       INTEGER,
    titletext     TEXT,
    UNIQUE(game_id, lang_id)
);

CREATE TABLE DBINFO (
    version       INTEGER DEFAULT DB_VERSION,
    subversion    INTEGER DEFAULT DB_SUBVERSION
);
```

Language identifiers are ASCII four-character codes stored in 32 bits:

| Language | Decimal | Hex | ASCII |
|---|---|---|---|
| Portuguese (Brazil) | 538997872 | 0x20205450 | "PT  " |
| English | 538996325 | 0x20204545 | "EN  " |
| Spanish | 538997605 | 0x20205345 | "ES  " |

A queue database used for downloads also carries a DBINFO table. A database
file that exists but has no DBINFO table is treated as invalid by the OEM code
and the SQLite open fails, which stalls the UI.

## OEM service objects

The OEM layer exposes four object families to titles and to its own UI:

| Object | Purpose |
|---|---|
| config | shell and device configuration |
| root_form | top-level UI form |
| mcp | media control and playback |
| telemetry | usage reporting counters |

Calls arrive through named hooks rather than a fixed numeric vtable, so a HLE
layer must dispatch by hook name.

## Roller widget

The carousel uses a "roller" widget. Two observed requirements:

- The widget vtable must expose slot 17; a real title calls it with
  (0x8000, pFont) to bind a font model. If the slot is missing, assembly of the
  roller aborts.
- The queue database must contain a valid DBINFO table.
