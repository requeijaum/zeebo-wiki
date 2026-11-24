# The USB Host Stack and the Device-Controlled Descriptor

A console that can act as a USB host parses whatever the attached device declares, before any authentication and with bytes the device chooses.
This page records the host-side stack found in the 1.1.2 images, what it parses, and which parts are measured rather than assumed.

## The host controller and its client API

The applications image carries an EHCI driver, a hub driver and a host-side class layer.
The controller's register block is mapped at `0xA0800000`.
The client-facing API is named by its own assertions: a client id pool that can run out at `0x10425DA4`, and a per-device-type table of ioctl functions checked at `0x10425E3C`.
A hub driver is present, with its self-powered decision logged at `0x102F8F20`, and the controller logs pipe state at `0x103C73B8`.
A host abstraction layer and an OEM bridge appear as source paths: `hsu_host_al_hid.c` at `0x108E90C8` and `OEMHID.c` at `0x1071DC44`.
Evidence: strings and their cross-references in the 1.1.2 applications image.

## A generic HID driver parses the report descriptor

The class driver announces itself in its own log: it fetches a report descriptor, and then counts the reports it found in it.
Those two messages sit at `0x104F87B1` and `0x104F8C20`.
Neither is reached by a direct call: the only references come from a table of log records, which is what a logging framework looks like from the instruction level.
The routine that loads the record at `0x10C4FE28` is `fn~0x10771B08`, whose literal pool holds the reference at `0x10771DEE`.
That routine allocates a context through two imported helpers and copies the fields the device reported.
The descriptor message is logged from inside it, so both the fetch and the parse it reports on are reached from this routine.
The role of each individual helper call is not established.
Evidence: the literal-pool reference to the log record, plus disassembly of the attach routine.

## The device chooses the bytes, and the host must trust them

A report descriptor is a sequence of items whose lengths and counts are declared by the device, and the host walks it using those declarations.
The same applies to the descriptor length requested during enumeration, and to the interface and endpoint descriptors that precede it.
Nothing in that path is signed, and nothing in it depends on the console's own data.
A fault hunter cares about that combination for three reasons.
The input is controlled by the device, it arrives before authentication, and it is parsed by code running on the applications processor.
Evidence: the descriptor fetch and the report count in the class driver, and the absence of any verification step along that path.

## What is not established

Three questions decide whether the surface is reachable at all.
Whether the console's port is wired as a host, with supply on the connector, is untested.
Whether the release enables the host stack, rather than carrying it as a platform default, is untested.
Whether the report descriptor parser has a fault that a malformed descriptor can reach is untested, and no candidate has been examined yet.
A negative on either of the first two closes the route as cheaply as a positive opens it, which is why they are the first bench checks.
Evidence: absence of measurements, recorded as absence rather than filled with inference.

## Observation is the hard part

The console has no accessible debug output while the port is closed, so a fault has to be seen from outside: through the link itself, the screen, and the power behaviour.
The device side sees the exchange that the console initiates, which is enough to tell a stall from a completed parse, but not enough to name a faulting address.
That is why a run on this route records descriptors before and after every attempt, and treats the screen as a second channel rather than as the only one.
Evidence: the security model page records that the port is off by default, and the observation channels are defined in the research plan for this route.
