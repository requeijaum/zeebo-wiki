# F6 — áudio [EM CURSO]
## [CONF] `media_hle.cpp` clone (15/09)
- Objeto mídia: Allocate/CreateMediaObject, AddRef/Release, RegisterNotify/LastNotify.
- Dados: ApplyMediaData, Set/GetMediaParm; transporte: Play/Stop/Pause/Resume, Tick (host),
  GetTotalTime/GetState; save-state: Serialize/Deserialize.
- Casa com note vs-zeemu: trampoline grava MediaHle real em media_source+8; Play do guest
  dereferencia [+0x28]->[+8]->vtable->[6]; Release zera +8 (NULL-wander do DD).
## [CONF] fork `curupira/core/brew/imedia.cpp` + `core/audio/misturador.*` (15/09)
- CLSIDs mídia mapeados: MEDIA/MIDI/MP3/QCP/PMD/MIDIOUT/MPEG4/ADPCM/AAC/SAF/PCM (0x01005500+).
- PCM16 via `MMD_BUFFER.pData`; mixer = `misturador`.
- Lacuna honesta no código: "NÃO há descodificador de áudio nesta árvore" (nem WAV);
  arquivo no VFS sem decoder = aviso, não som. Clone tem synth GM soundfont — divergência a explorar.
## Pendente
- Gate DD áudio real; scanout MDDI.
