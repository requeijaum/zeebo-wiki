# The Card Interface: Commands the Terminal Obeys

The console's modem implements the terminal side of the SIM Application Toolkit.
A card can therefore ask the console to display, prompt and report, and the console parses bytes that the card supplies.
This page records what that path looks like in the 1.1.2 images, and why it sits closer to the port assignment than the application-side routes.

## The terminal side exists, command by command

The modem image contains the toolkit service with one source file per command, named in its own strings.
Proactive command handling, the expected-response check and the terminal profile all appear as separate units.
Envelope responses, polling and the local information command appear in the same way.
The profile is announced with the slot and the application in the message itself, which means the terminal declares its capabilities at start-up rather than on request.
A bearer-independent path is present as well: an allocation failure and a channel request failure are both logged as their own messages.
The units, and the message each one logs, are named in the strings of the modem image.

| Evidence | Address |
|---|---|
| `gstk_proactive_cmd.c` | `0x16E51518` |
| expected-response message | `0x16E51598` |
| `Received Proactive cmd` | `0x16EE2488` |
| terminal profile message | `0x16FC4789` |
| envelope handling unit | `0x00C4A8BC` |
| polling unit | `0x00C4BB0C` |
| local information unit | `0x00C4C0B0` |
| channel allocation message | `0x16FC70CB` |

Each address above is a string location in the 1.1.2 modem image, not a function entry point.

## The card supplies the structure, not only the content

A proactive command is a template of tagged fields: a command type and qualifier, the device identities, and then the text, the items and the lengths, all supplied by the card.
Two delivery mechanisms exist and the terminal may use either: a pending status byte followed by a fetch, or a pending status followed by a read of the response object.
Both were implemented in the reference instrument, because which one this terminal uses is not yet measured.
The important property is structural: item counts, text lengths and tag order are all card-controlled, and the terminal parses them in order to display a menu or a prompt.
Evidence: the command templates and the pending-command status are defined by the toolkit specification.
The encoding used by the reference instrument was reproduced against captured exchanges from commercial cards.

## Two parsers face the card, one at a time

Before any command is issued, the card is initialised: files are selected and read, and the terminal parses file control parameters and record lengths that come from the card.
That is a first parser surface, and it faces the same party.
The proactive command is the second, and it only becomes reachable once initialisation completes.
Both live in the modem image, and neither is federated: the card answers, and the terminal parses the answer.
Evidence: the card driver strings for file selection and status words, together with the toolkit units above.

## Why this route is structurally different

The device map that assigns ports lives in the same image as the toolkit service.
Its name table, its getter and its pair validation are all in the modem image, while the caller that requests an assignment sits in the applications image.
An application-side route therefore has to cross a processor boundary to reach the port map, and a fault on the modem side does not.
That is the argument for looking at the card interface at all, and it is an argument about address spaces rather than about exploitability.
Evidence: the port map table, its getter and its validation, compared with the location of the caller.

## What a card can ask for, and what this research does not

A card can ask the terminal to show text, offer a menu, read a key, return local information such as the device identity, and manage timers.
It can also ask for messages, calls, data channels and browser launches, which is why a research card has to restrict itself in code rather than in a document.
The reference instrument refuses any command outside a small display-and-read set, keeps a refusal counter, and does not build the transmitting commands into the firmware at all.
The restriction is tested rather than trusted: a mutation that turns an allowed command into a forbidden one is rejected before anything is armed.
Evidence: the allowlist in the instrument's core and the tests that exercise it, including the mutation case.

## What is not established

Whether this release enables the toolkit path is untested.
Whether card initialisation completes without a step derived from the network is untested.
Whether any card-facing parser has a length fault is untested.
Each one is answered by a bench check whose failure closes the route cheaply, and none is currently supported by anything stronger than the presence of the code.
Evidence: the questions listed on the open questions page, and the absence of bench data.
