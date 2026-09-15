# Audio: Media, Sound and the Mixer

Audio is where a superficially working emulator is most often silent.
Titles do not play a fixed set of resources: they create a media object for the format they need, feed it data, and expect a callback when playback finishes.

## Media classes

Class IDs in the media range, from the SDK class table:

| Class ID | Name | Notes |
|---|---|---|
| 0x01005500 | MEDIA | base class |
| 0x01005501 | MEDIAMIDI | sequenced music |
| 0x01005502 | MEDIAMP3 | compressed audio |
| 0x01005503 | MEDIAQCP | Qualcomm codec format |
| 0x01005504 | MEDIAPMD | mobile audio format |
| 0x01005505 | MEDIAMIDIOUTMSG | MIDI output |
| 0x01005506 | MEDIAMIDIOUTQCP | MIDI to QCP output |
| 0x01005507 | MEDIAMPEG4 | video and audio container |
| 0x0100550a | MEDIAADPCM | adaptive PCM |
| 0x0100550b | MEDIAAAC | advanced audio coding |
| 0x01005510 | MEDIASAF | service audio format |
| 0x01005511 | MEDIAPCM | raw PCM |

Titles query these by class ID through ISHELL_CreateInstance.
A runtime that implements only PCM will fail the creation for every other class;
a runtime that implements creation but not playback produces a title that runs and stays silent.

## Interfaces

<!-- BEGIN GENERATED: IMedia -->
_Generated from the public SDK header `AEEIMedia.h`. Inheritance chain: IQI, IMedia._

Base slots: **IQI → IMedia**, so slot 0 is the first method of IQI and the first method of IMedia starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | QueryInterface | int | this, AEEIID, void ** |
| 3 | RegisterNotify | int | this, PFNMEDIANOTIFY pfnNotify, void * pUser |
| 4 | SetMediaParm | int | this, int nParamID, int32 p1, int32 p2 |
| 5 | GetMediaParm | int | this, int nParamID, int32 * pP1, int32 * pP2 |
| 6 | Play | int | this |
| 7 | Record | int | this |
| 8 | Stop | int | this |
| 9 | Seek | int | this, AEEMediaSeek eSeek, int32 lSeekValue |
| 10 | Pause | int | this |
| 11 | Resume | int | this |
| 12 | GetTotalTime | int | this |
| 13 | GetState | int | this, boolean * pbStateChanging |
<!-- END GENERATED: IMedia -->

<!-- BEGIN GENERATED: ISound -->
_Generated from the public SDK header `AEEISound.h`. Inheritance chain: IBase, ISound._

Base slots: **IBase → ISound**, so slot 0 is the first method of IBase and the first method of ISound starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | RegisterNotify | void | this, PFNSOUNDSTATUS pfn, const void* pUser |
| 3 | Set | int | this, const AEESoundInfo* pSoundInfo |
| 4 | Get | void | this, AEESoundInfo* pSoundInfo |
| 5 | SetDevice | void | this |
| 6 | PlayTone | void | this, AEESoundToneData toneData |
| 7 | PlayToneList | void | this, AEESoundToneData* pToneData, uint16 wDataLen |
| 8 | PlayFreqTone | void | this, uint16 wHiFreq, uint16 wLoFreq, uint16 wDuration |
| 9 | StopTone | void | this |
| 10 | Vibrate | void | this, uint16 wDuration |
| 11 | StopVibrate | void | this |
| 12 | SetVolume | void | this, uint16 wVolume |
| 13 | GetVolume | void | this |
| 14 | GetResourceCtl | int | this, IResourceCtl ** ppo |
<!-- END GENERATED: ISound -->

## Lifecycle

| Step | Action |
|---|---|
| 1 | Create the media object with the format class ID |
| 2 | Supply data, either a memory buffer or a VFS file |
| 3 | Set parameters: sample rate, channels, volume, loop behaviour |
| 4 | Register a notification callback |
| 5 | Play |
| 6 | Stop, Pause and Resume as the title requires |
| 7 | The runtime ticks the object and fires the callback at completion |

The notification is not optional bookkeeping.
Many titles wait for it before raising a load barrier or starting the next track, so a runtime that never fires it leaves the title on a menu that looks frozen.

## PCM path

- Uncompressed audio arrives as 16-bit signed PCM. 
- MMD_BUFFER carries the sample pointer and a byte size. 
- An odd byte size for 16-bit PCM is an error worth logging;
  it usually means the title used the wrong parameter.

| Field | Meaning | Common mistake |
|---|---|---|
| sample pointer | guest address of the buffer | reading it as a host pointer |
| byte size | length in bytes, not samples | halving or doubling the length |
| format | PCM or compressed variant | assuming PCM for every buffer |

Two checks worth making early, because both produce silence rather than an error:

- Whether the buffer lives in guest memory that the title later overwrites.
  A runtime that copies lazily will read stale samples.
- Whether the title expects the callback before or after the buffer is released.
  Releasing too early yields truncated audio at the end of every effect.

## Sound channels

| Concept | Detail |
|---|---|
| ISound | a decoded sound resource |
| ISoundPlayer | the output channel that plays an ISound |
| Channel count | titles use several concurrent channels; a single-channel mixer drops effects |
| Rate | assets are not uniformly one rate, so the mixer must resample per voice |
| Level | volume and pan are per channel and set by the title |

Observed failure mode: a title keeps its own channel objects and stores a media pointer at channel+0x28, expecting the object at +8 to remain valid.
If the runtime clears that field on release and the title then calls play, the call walks a null vtable slot.
Both sides of that contract must be modelled, and the release path is the one that is usually wrong.

## What a runtime must actually decode

| Format | Used by | Consequence of skipping |
|---|---|---|
| MP3 | music tracks | silence in menus and levels |
| ADPCM | effects and voice | missing sound effects |
| MIDI | sequenced music with a sound bank | silence, or noise if a raw dump is played |
| PCM | short effects and streams | minimal, this is the easy case |

Declaring that a runtime has no decoder is honest, but it is not a compatibility claim.
Titles that reach gameplay with no audio at all are a common intermediate state, and the reason is almost always a missing decoder rather than a broken mixer.

## Mixing and output

- The mixer receives a format, a rate and a buffer of interleaved stereo samples. 
- Sample rate travels with each push, because nothing guarantees that all assets of a title share one rate. 
- The host backend converts to the device rate, not the other way round. 
- A soundfont synthesizer is required for MIDI titles, and the bank must ship with the runtime. 

Evidence: class IDs and interface layouts from the public SDK headers.
Channel object behaviour and the completion notification from real title traces.
