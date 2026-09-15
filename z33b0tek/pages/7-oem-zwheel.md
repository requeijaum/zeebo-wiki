# OEM Layer: Z-Wheel

The Zeebo ships an OEM application that hosts the store interface and the carousel of installed titles.
It is a normal BREW applet with an OEM class ID, but titles interact with it, so a runtime that only implements stock BREW will stall before the first game.

## Identity and VFS layout

| Item | Value |
|---|---|
| App ID | 274755 |
| Class ID | 0x01070798 |
| Registered vendor string | TECTOY |
| Module information | fs:/mif/274755.mif |
| Module directory | fs:/mod/274755/ |
| Private applet directory | fs:/~0x01070798/ |
| Licence and keys | fs:/~0x01070798/tectoyli.brf |
| Shell configuration | fs:/mod/274755/tectoy.cfg |
| UI configuration | fs:/mod/274755/uiconfig.xml |

The private directory naming rule is worth noting: a tilde followed by the class ID in hexadecimal.
Implementations that use only the app ID will not find the licence file and the shell will fall back to a restricted mode.

## Embedded SQLite databases

The OEM application stores its catalogue in standard SQLite 3 files with 1024-byte pages.
The schema is small enough to reimplement by hand.

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

Column meanings that matter for behaviour:

| Column | Use |
|---|---|
| class_id | the class ID the shell passes to CreateInstance when launching |
| playcount, dt_lastplayed | drive the "most played" ordering in the carousel |
| boxart_path | path to the artwork, resolved through the VFS |
| flags | install and availability state |
| lang_id | selects a row of TITLETEXT for the current locale |

Language identifiers are ASCII four-character codes stored in 32 bits:

| Language | Decimal | Hex | ASCII |
|---|---|---|---|
| Portuguese (Brazil) | 538997872 | 0x20205450 | "PT  " |
| English | 538996325 | 0x20204545 | "EN  " |
| Spanish | 538997605 | 0x20205345 | "ES  " |

A download queue database also carries a DBINFO table.
A database file that exists but has no DBINFO table is rejected: the SQLite open fails and the UI stalls with no visible error.
Creating the file empty is therefore worse than not creating it at all.

## OEM service objects

The OEM layer exposes four object families to titles and to its own UI:

| Object | Purpose |
|---|---|
| config | shell and device configuration |
| root_form | top-level UI form |
| mcp | media control and playback |
| telemetry | usage reporting counters, with a send counter |

Calls arrive through named hooks rather than a fixed numeric vtable, so a runtime must dispatch by hook name.
Telemetry increments are observable and useful as a liveness signal: a title that reaches the carousel increases the counter.

## Roller widget

The carousel is a "roller" widget with two observed requirements:

- The widget vtable must expose slot 17.
  A real title calls it with (0x8000, pFont) to bind a font model.
  If the slot is missing, the call lands on an unimplemented handler and the assembly of the roller aborts.
- The queue database must contain a valid DBINFO table, as described above. 

Both failures present the same way: the carousel renders nothing, and the shell looks frozen with no error path.

## Configuration files

tectoy.cfg and uiconfig.xml are read at startup.
Both matter to behaviour:

| File | Content | Effect if missing |
|---|---|---|
| tectoy.cfg | shell configuration: locale, button mapping, service endpoints | default mapping, some UI paths unreachable |
| uiconfig.xml | UI layout and element list for the store front end | default layout, or the front end fails to build |

A loader that mounts the OEM files but does not expose these exact paths gets the default configuration.
That is a silent difference: the UI still draws, but the buttons respond differently from the documented layout, which is easy to misattribute to input handling.

Also worth checking on a new dump: whether the private directory holds a licence file.
Without it the shell falls back to a restricted mode and refuses to launch installed titles, again with no visible error message.

