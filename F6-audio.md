# F6 — Audio [IN PROGRESS]
## [CONF] `media_hle.cpp` clone (09-15)
- Media object: Allocate/CreateMediaObject, AddRef/Release, RegisterNotify/LastNotify.
- Data: ApplyMediaData, Set/GetMediaParm; transport: Play/Stop/Pause/Resume, host Tick,
  GetTotalTime/GetState; save-state: Serialize/Deserialize.
- Matches the vs-zeemu note: the trampoline stores a real MediaHle at media_source+8; the guest
  Play dereferences [+0x28]->[+8]->vtable->[6]; Release zeroes +8 (the DD NULL-wander).
## [CONF] parked fork `curupira/core/brew/imedia.cpp` + `core/audio/misturador.*` (09-15)
- Media CLSIDs mapped: MEDIA/MIDI/MP3/QCP/PMD/MIDIOUT/MPEG4/ADPCM/AAC/SAF/PCM (0x01005500+).
- 16-bit PCM via `MMD_BUFFER.pData`; mixer = `misturador`.
- Honest gap in code: "NO audio decoder in this tree" (not even WAV);
  a file in VFS without decoder = warning, no sound. The clone has a GM soundfont synth — divergence to exploit.
## Pending
- Real DD audio gate; MDDI scanout.
