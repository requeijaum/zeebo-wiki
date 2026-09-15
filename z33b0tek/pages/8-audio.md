# Audio: Media, Sound and the Mixer

## Media classes

Audio playback goes through BREW media classes. Class IDs observed in the media
range 0x01005500 upward:

| Class ID | Name |
|---|---|
| 0x01005500 | MEDIA |
| 0x01005501 | MEDIAMIDI |
| 0x01005502 | MEDIAMP3 |
| 0x01005503 | MEDIAQCP |
| 0x01005504 | MEDIAPMD |
| 0x01005505 | MEDIAMIDIOUTMSG |
| 0x01005506 | MEDIAMIDIOUTQCP |
| 0x01005507 | MEDIAMPEG4 |
| 0x0100550a | MEDIAADPCM |
| 0x0100550b | MEDIAAAC |
| 0x01005510 | MEDIASAF |
| 0x01005511 | MEDIAPCM |

## Lifecycle

1. Allocate a media object with the class ID of the format.
2. Apply media data: either a buffer or a VFS file handle.
3. Set media parameters such as sample rate, channels and volume.
4. Register a notification callback.
5. Play. Stop, Pause and Resume control playback afterwards.
6. The runtime ticks the media object, which advances decoding and fires the
   notification when playback completes.

## PCM path

- Uncompressed audio arrives as 16-bit signed PCM.
- MMD_BUFFER carries the sample pointer and a byte size.
- An odd byte size for 16-bit PCM is an error condition worth logging.

## Sound channels

- ISound and ISoundPlayer model short effects and streams.
- Some titles keep their own channel objects and expect the runtime to hand back
  a working media object pointer for each channel.
- Observed failure mode in a HLE runtime: the game stores a media pointer at
  channel+0x28 and expects the object at +8 to stay valid. If the runtime clears
  that field on Release and the game then calls Play, the call walks a null
  vtable slot. Both sides of that contract must be modelled.

## What a runtime must actually decode

- MP3, ADPCM and MIDI are the formats used by real titles.
- A runtime that only mixes PCM16 will stay silent unless the title itself ships
  PCM. Declaring "no decoder" is honest but not a compatibility claim.
