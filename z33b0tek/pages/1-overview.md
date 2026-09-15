# Console Overview

The Zeebo is a 2009 home console built from a Qualcomm handset platform.

It has no fixed-function game hardware.
Titles are ordinary BREW applications that draw through OpenGL ES and read input through the HID interfaces, on top of a mobile operating environment.
That single fact drives every decision in this reference: emulating the console means implementing a software platform, not a register-level graphics chip.

## Hardware summary

| Block | Part | Notes |
|---|---|---|
| Applications CPU | ARM1136J-S | ARMv6, ARM and Thumb-1, no Thumb-2, 528 MHz |
| Modem CPU | ARM926EJ-S | runs AMSS on REX, 256 MHz |
| SoC | Qualcomm MSM7201A | handset platform, undocumented publicly |
| GPU | Adreno 130 | Yamato class, OpenGL ES 1.1 |
| DSP | QDSP5 | audio and voice processing |
| RAM | 160 MB | shared with the modem side |
| Storage | 1 GB NAND | firmware plus installed titles |
| Network | 3G modem | digital distribution only, servers shut down in 2011 |
| Display output | composite video | 320x240 panel-class resolution |
| Input | two USB gamepads | digital directions and buttons, two analog axes |

## Software stack

From the bottom up:

1.
OKL4 2.1.1, a microkernel built from the L4e lineage.
2.
REX, the real-time executive that hosts the modem and bootstrap tasks.
3.
BREW 4.0.2, the application environment that titles are written against.
4.
Zeebo OEM layers, which add the store UI, gamepad handling and extra classes.

A title never sees the microkernel.
It sees BREW object interfaces, so the practical emulation boundary is the BREW API surface.

## How a title runs

| Step | Action |
|---|---|
| 1 | The loader maps the title module image into memory |
| 2 | The runtime calls the module's load entry point |
| 3 | The module registers its applet factory |
| 4 | The runtime creates the applet object for the title class ID |
| 5 | The runtime delivers EVT_APP_START |
| 6 | The title schedules a timer and returns control |
| 7 | Each timer callback draws a frame and re-arms the timer |

Steps 6 and 7 are the important ones.
There is no thread inside the title and no frame loop owned by the title.
The frame loop is a timer queue owned by the runtime, and the title re-arms it from inside its own callback.

## What this reference covers

| Page | Content |
|---|---|
| Loader and container formats | how a title and its assets are packed |
| AEE runtime contract | module lifecycle, events, timers |
| IShell, IDisplay, and other interfaces | vtables with real slot numbers |
| Input, OEM layer, video, audio, storage | subsystem behaviour |
| Hardware registers and kernel syscalls | what firmware-level work needs |
| ABI reference | structures, class IDs, error codes |
| Open questions | what is still unknown, and what would close it |

Evidence: hardware figures come from the platform documentation that ships with the public SDK and from measurements taken on real dumps.
Slot numbers come from the SDK headers and are reproduced by the generator in `tools/`.
