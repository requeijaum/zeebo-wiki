# Online Services and Score Servers

Several Zeebo titles ship a score table that lives on a server, and the console reaches it over the 3G modem with the plain HTTP stack of the platform.
This page records which first-party titles do that, what each one sends, and what a runtime has to implement before any of those screens can work again.

The distinction that matters most is between a **local** score table and an **online** one.
A local table is a file the title writes itself, and it keeps working with the network switched off.
An online table is a request to a host that no longer exists, and it stays empty until something answers.

## Local score tables

This group is not online, and confusing it with the other one costs a lot of work.
The evidence is the resource or file name that each title carries for its own table:

- FIFA 09 keeps its table in `udata/rankings.f08`.  
- Cannonball keeps `udata/highscore.dat` and the artwork `menu/gfx/highscore.png`.  
- Bejeweled keeps `udata/gof_highscores_`.  
- Quake keeps `gfx/ranking.lmp`.  
- Alpine Racer EX carries the text `world ranking data.` and the directory `/res/2d/ranking/`.  
- Zenonia carries the string `!CRanking`.  

None of these names is a host, a path on a server or a query, and none of the six requests a network class at run time.
A runtime that implements no networking at all still shows these tables, so they are the wrong target for a "restore the scoreboard" effort.

Evidence: six modules under `brew/mod/<folder>/`, string offsets listed in the table at the end of this page.

## Titles with an online score

Each entry below has both the endpoint and the request string in the shipped module, which is what separates an online score from a local one.
The table at the end of the page lists every offset, so the claim can be re-checked in the file.

| Title | Endpoint in the module | Method and headers |
|---|---|---|
| Zeeboids | `www.zeeboids.com/zeeboidsService/PHP/Client/import.php`, `export.php`, `synchronize.php` | `POST`, `X-Method: POST`, `Content-Type: application/octet-stream` |
| Zeebo Tennis | `www.boomerangsports.com.br/tennisService/OnlineRanking/Client/client.php` | `GET`, header `X-Method: GET` |
| Zeebo Volley | `www.boomerangsports.com.br/volleyService/OnlineRanking/Client/client.php` | `GET`, header `X-Method: GET` |
| Dodgeball | `www.boomerangsports.com.br/dodgeballService/OnlineRanking/Client/client.php` | `GET`, header `X-Method: GET` |
| Zeebo Peteca | `www.boomerangsports.com.br/petecaService/OnlineRanking/Client/checkgames.php` and `client.php` | `GET`, header `X-Method: GET` |
| All Star Cards | `www.derekboyle.com/back/gateway/` | HTTP through the platform web interface |
| Reckless Racing | `www.polarbit.com/Fuse/Score/PolarbitScoreSystem.php` and `PolarbitUserSystem.php` | `GET` and `POST` over a raw socket |
| Reckless Racing 2 | `polarbit.com/scripts/update_lobby2.php` | `GET` over a raw socket |
| Chessbots | `swervenet.superscape.com/superscape/` plus `join.php`, `lobby.php`, `message.php` | `POST` with `multipart/form-data` |

The Zeebo Tennis, Volley, Dodgeball and Peteca titles come from one studio and share one engine.
All four carry a 3D engine whose type names start with `TTD`, and all four name the same three ranking operations in their binaries.
An implementer writing one server for that studio gets four titles at once.

Evidence: the endpoints are ASCII strings inside the `.mod` files;
offsets in the closing table.

## The Zeeboids service

Zeeboids is the only first-party title whose content depends on a server, so it is the one whose protocol can be written down in full.
It speaks plain HTTP with three fixed routes, and the body of the request is a binary POST:

| Route | Direction | Body |
|---|---|---|
| `import.php` | server to client | binary, and the client inflates it with its own unzip stream |
| `export.php` | client to server | binary, built from the rows the client marked as changed |
| `synchronize.php` | both | empty body is a valid answer and means "nothing to sync" |

The serialised form is text separated by semicolons, with one record per row of the query that feeds it.
The client builds each record with a format string that sits immediately after that query in the binary.
That pairing is the measurement: the row query for `zeeboids` is followed by `%d;%d;%s;%s;%s;%d;%s;%s;%d;`.
The score query for one player is followed by `%d;%d;`, which is a score identifier and a value.
The answer uses the same shape, and one field order is load-bearing.
The reply to `import` must carry `lid;id;zid` first, because the client reads the IMEI as the local id when they are missing.

The client keeps a full mirror of the service schema in a local SQLite database under `fs:/zeeboiddata/zeeboid.db`.
The shipped database contains 38 named queries and 27 tables, and those tables are the contract the server has to satisfy:

| Table | Role |
|---|---|
| `zeeboids` | one row per avatar: local id, account id, nickname, password, creator IMEI, gender, birthday, status |
| `scores` | the player score per score type, with an `updated` flag that means "not sent yet" |
| `score_types` | the catalogue of scores per game, with decimal places and unit text |
| `scores_top10` | the global top ten, downloaded from the server and deleted when the client refreshes |
| `scores_zeeboid_neighbours` | the ranking neighbourhood around the player, also downloaded |
| `game_achievement`, `zeeboid_achievement` | achievements with required and completed task counts |
| `attributes`, `attribute_types`, `attributes_string` | accumulated counters, such as goals and wins |
| `zeeboid_body`, `zeeboid_head`, ... | eleven tables that hold the editable avatar |

Two details change a server implementation.
The upload body is **encrypted** before it leaves the client, and the client creates a hash object alongside the cipher, so a server that wants the clear text has to know the key.
The body of `import` is **compressed**, and the client inflates it itself, so the server sends the compressed form and nothing else.
The client also limits synchronisation and export to one civil day, using the timestamps in its own database.
That limit makes repeated testing slow unless the stored date is moved back.

The screens the client drives are observable.
They name the queries `getGameTOP10`, `getRanking` and `getRankingNeighbours`, each with an integer variant.
They also name the connection states `Connecting`, `ReceivingData`, `Complete`, `Unauthorized` and `Connection_Failed`.

Evidence: strings and format pairings inside `zeeboids.mod`, and the shipped `zeeboiddata/zeeboid.db` read with SQLite.

## The Boomerang Sports ranking

The four sports titles share one ranking interface with three named operations, and the request carries a header whose value repeats the method:

```
X-Method: GET
```

That line is a **header**, not the request line, and the platform web interface takes both from the title: the method as an option and the header as a name-value list.
No query template appears anywhere in the four modules, so the field names the service expects are still unknown.
What would close that is a title run to its ranking screen, with the request recorded.
Two of the four also create a hash object next to the web object, which suggests a digest of the score.
`Dodgeball` and `Zeebo Peteca` add countdown artwork, which shows their ranking screen sits behind a menu.

Evidence: `X-Method: GET` and the endpoint on adjacent lines of each module;
hash class constants in two of them.

## The Polarbit score and lobby service

The Polarbit titles do not use the platform web interface.
They open a raw socket through the network manager and write HTTP/1.1 by hand, and their own error texts say so.
The socket open error names a null network manager, and another message is a connect timeout.
The score protocol is form-encoded and its parameters are literal strings:

| Purpose | Parameter list |
|---|---|
| Account and login | `pid=%d&action=%d&uhash=%d&sid=%d` |
| Read scores | `pid=%d&action=%d&uhash=%d&gid=%d&filtermask=%u&start=%d&max=%d` |
| Submit a score | `pid=%d&action=%d&uhash=%d&gid=%d&lid=%d&score=%s&type=%d&descid=%d&scoredesc=%s&logic=%d&blen=%d&btype=%d&did=%s&duid=%s&uagent=%s&bdata=` |
| List game rooms | `action=3&game_id=%d&protocol_version=%d&name_filter=%s&desc_filter=%s&protocol_filter=%d&near_me_filter=%d&sorting_key=%s&max_results=%d&return_mask=%d` |

The score and account routes are two separate PHP files under one host directory, so a server can serve both from a single endpoint.
The lobby answer is parsed into three named fields, `Name`, `PlayerCount` and `GameRooms`.
The `uhash` field is a user digest, and what it covers is not known from the module.
The lobby route also tells the player that an account is needed before global scores appear, which means the account screen is a prerequisite for the score screen.

Evidence: parameter strings and socket error text inside the two Polarbit modules, and inside the third title that shares the same socket layer.

## The SwerveNet lobby in Chessbots

Chessbots does not speak HTTP directly.
It loads a third-party networking framework, and its own message says so when the private class cannot be created: the framework instance is named in the error text.
The lobby is served by three PHP routes under one host, one for joining, one for the lobby list and one for player messages.
The join and message bodies are built from templates that name their fields.
The names are `uid`, `aid`, `lid`, `tout`, `msg`, `tck` and `sid`, with a session marker written to the shared store.
The requests are multipart forms with a fixed boundary string.
The module also lists the source files of the lobby screens, which shows the split between joining, lobby, message and transport.
A separate observation says the title also **downloads** content.
Sixty-six resource files in its folder exist only with a `.net` suffix and no plain copy, and their payload is an archive of a shipped format.

Evidence: framework error text, the three routes, the field templates and the file survey of the title folder.

## The card gateway in All Star Cards

All Star Cards is a card game with tables and rooms rather than a single score list.
Its gateway address appears in all three of its string tables, which is where the title keeps its own resource strings.
The protocol is visible in its screen code.
It prints a room number, a table number and a table identifier, it reports a join response and it reports leaving a table.
It also reacts to a game start delivered by an update poll, so the client polls the gateway for state instead of holding a connection.
The interface it uses is the platform web interface, and that use is measured rather than assumed.
Of the whole first-party library, this is the only title observed asking the runtime for the web class, and it asks once, during start.

Evidence: address string in the three string tables, the screen texts in the module, and the recorded class request.

## Titles that embed the Zeeboids client

Zeebo FunSoccer and FootParty show a Zeeboid ranking without speaking to a server themselves.
Their binaries carry the same query names as Zeeboids, including the ranking neighbour query and the score insertion.
Their own text keys also separate a local high score from an online one.
Neither module contains a host, a route or a web class.
Both read the same shared database path that Zeeboids writes, so their online screen is a **view** of data another title fetched.
This is why a server alone does not fix them: the Zeeboids application has to synchronise first, and the shared database is the handover between the two titles.

Evidence: query-name strings and text keys in both modules, absent host and web class in both, and the shared path named in the runtime that reads it.

## The OEM services: store, credits and telemetry

The OEM application carries its own HTTP wrapper and its own configuration file, and that file is a better source than any inference.
It holds the service address, the asset catalogue identifier, the browser item identifier and a telemetry switch.

| Item | Value in the shipped configuration |
|---|---|
| Credit service | `https://aquila.tectoy.com.br:8443/WSM/wsm?wsdl` |
| Telemetry server | `http://66.179.182.77`, used with the path suffix `/cgi-bin/upload.cgi` |
| First-run credit grant | 35, which matches the `Points` row of the preferences database |
| Asset catalogue | identifier 80500, with the certificate check described below |

The credit service is SOAP over TLS, and the module carries six operations: read the available credit, register account data, and recharge from four different payment sources.
The telemetry path uploads a log file as a multipart form, and it disables itself when the server name is invalid.
The store itself is not a protocol of its own.
It drives the platform download subsystem, which the module names in its own failure texts, and the item list arrives from the download catalogue.
Two facts about that catalogue belong here.
The asset catalogue XML is verified against an X.509 certificate before assets are downloaded.
The download server address is not in the configuration file, it is a platform configuration item read by the download subsystem.

Evidence: the shipped `.cfg` with its offsets, the SOAP envelope and operation strings in the module, and the preference rows read from the console database.

## Titles with network code and no reachable endpoint

Some modules contain networking code but no address, and the difference matters when planning work.

- Need for Speed carries a network menu, a list of online options and form-encoded POST support, and no host, route or query anywhere in the module or its resources.  
- Ten arcade titles from one publisher create the platform network manager and say so in an error text. 
- That error text sits in the same relative position in all ten files, and none of the ten carries a host or a web route. 
- Prey 3D reports a failure to initialise the web interface and keeps its server address outside the module, in a text file next to the resource folder.  
- Iron Sight writes HTTP/1.1 by hand over a raw socket, like the Polarbit titles, and carries no address at all.  

For these the honest answer is that the endpoint is unknown.
The artefact that would close it is named: the network menu is reached, the request is recorded, and the missing host appears in it.

Evidence: menu and option strings in Need for Speed;
the shared error text in the ten arcade modules;
the server address file of Prey 3D;
the socket strings of Iron Sight.

## What a runtime needs to serve these titles

The titles above exercise four different mechanisms, and a runtime that has only one of them can serve only part of the library.

| Mechanism | What the title does | What the runtime must provide |
|---|---|---|
| Web interface | opens a URL, sets a method and headers, reads a response object | the request call, header options, and a response object the title can read and release |
| Source utility | wraps a buffer or a file as a source, and wraps the POST body as a buffer | source creation from memory and from file, which the Zeeboids body path needs |
| Raw socket | opens a connection through the network manager, writes and reads bytes | socket object, network manager object, connect with timeout, send and receive |
| Cryptography | prepares a digest and, for one title, encrypts the payload | hash object with reset, update and digest, and a cipher object with key, mode and padding |

Three practical points follow from the measurements on this page.
The client refuses to work when an object it asked for is missing.
One title creates its web, hash and cipher objects in a row without checking each result, so refusing them stops the title before its first screen.
The request body of one title arrives encrypted and its answer arrives compressed.
A runtime that wants to record the exchange in clear text has to record the payload before the cipher and inflate the answer before handing it over.
The answers must also be handed to the title at a safe moment, outside the dispatch of the call that started the request.
Calling back into the title from inside that dispatch re-enters its memory manager.

Evidence: class requests recorded at run time, and the sequence of object creations read from the module of one title.

## Method

Every claim on this page rests on one of four instruments, and each claim can be re-checked with it:

- A byte scan of the shipped modules and resources, which yields a file name and an offset for each string.  
- A class-table scan that maps a four-byte constant to a name taken from the public SDK headers.  
- A run of the full first-party library with the dispatch recorded, which shows which classes the titles asked for and which were refused.  
- A read-only SQLite open of the console databases and of the databases the titles ship.  

Two cautions come from using them together.
A class constant inside a module does not prove a call, because constants from linked frameworks travel with the title even when the code path is dead.
The run-time record is therefore the proof, and the scan is only a lead.
A title that never reaches its online screen leaves no run-time trace at all, which is the case for every title whose ranking sits behind a menu.
Those entries rest on the string evidence, and a missing field name is marked unknown.

Evidence: the recorded library run, the byte scans and the database reads described above.

## Title table

| Title | Folder | Online | Endpoint or file | Evidence offset |
|---|---|---|---|---|
| Zeeboids | 279382 | yes, score and avatar | `www.zeeboids.com/zeeboidsService/PHP/Client/` | module 0x61ab0, 0xb197c, 0xb1b2c |
| Zeebo Tennis | 277534 | yes, score | `www.boomerangsports.com.br/tennisService/OnlineRanking/Client/client.php` | module 0x452bc, 0x452cc |
| Zeebo Volley | 278212 | yes, score | `www.boomerangsports.com.br/volleyService/OnlineRanking/Client/client.php` | module 0x4ab44, 0x4ab54 |
| Dodgeball | 278738 | yes, score | `www.boomerangsports.com.br/dodgeballService/OnlineRanking/Client/client.php` | module 0x52538, 0x52548 |
| Zeebo Peteca | 279159 | yes, score | `www.boomerangsports.com.br/petecaService/OnlineRanking/Client/client.php` | module 0x4acf8, 0x4ad08, 0x4adc8 |
| All Star Cards | 280173 | yes, rooms and tables | `www.derekboyle.com/back/gateway/` | string table 0x3cd and 0xaf4 |
| Reckless Racing | 280394 | yes, score and lobby | `www.polarbit.com/Fuse/Score/PolarbitScoreSystem.php` | module 0x1cfbb8, 0x1cfbd8, 0x1cfbf0, 0x1cfc8c |
| Reckless Racing 2 | 280602 | yes, lobby and account | `polarbit.com/scripts/update_lobby2.php` | module 0x174f78, 0x175010 |
| Iron Sight | 280221 | unknown | raw socket HTTP/1.1, no address | module 0xc0ea8, 0xc2a80 |
| Chessbots | 263019 | yes, lobby and matches | `swervenet.superscape.com/superscape/join.php` | module 0xa6ebe, 0xacf68, 0xad1b8 |
| FunSoccer | 280647 | indirectly, Zeeboid ranking | shared avatar database | module 0x4f73c |
| FootParty | 279380 | indirectly, Zeeboid ranking | shared avatar database | module 0x50e50, 0xe78fc |
| Z-Wheel | 274755 | yes, store, credits, telemetry | `aquila.tectoy.com.br:8443/WSM/wsm?wsdl` | configuration 0x12 and 0xb54 |
| Need for Speed | 276121 | unknown, no address | network menu only | module 0xdf228, 0x1a9e0, 0x1a8858 |
| Prey 3D | 276154 | unknown, content server | `www.arcajun.com/prey3d/` | server address file offset 0 |
| Ten arcade titles | 278986, 278987, 278988, 279125, 279126, 279173, 279200, 279233, 279888, 279889 | network manager only, no address | none | module error text, for example 0x187d28 |
| FIFA 09, Quake, Bejeweled, Zenonia, Alpine Racer EX, Cannonball | 274803, 274802, 277083, 277455, 276151, 277229 | no, local score only | local file per title | 0x56478, 0x48f54, 0x31fc8, 0x9ef08, 0x688b1, 0xa1bd0 |
