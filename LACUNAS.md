# Declared Gaps of the Clone [CONF] (each with an address)
- MIF: UTF-16LE strings only; resource/ClassID/privilege tables NOT understood (`mif.h`).
- BAR: off8 sub-table (32B header) NOT consumed/deferred (`bar.h`).
- Context +0x2c: non-null relative-vtable object, unknown interface (Peggle) (`mod_runtime.h`).
- Parked fork: no audio decoder; START busy-wait (TIMER_PREEMPT pending).
- Zeemu: 51 modules, depth unmeasured (breadth only).
- Infuse: closed source; Z-Wheel skipped on cost.
- SoC/GPU: dump real reporta GL_RENDERER `Q3Dimension MSM7500 01.02.37` (EGL 2.07.050110.34681,
  platform id 16000); wiki/site dizem MSM7201A + Adreno 130 (F0-fatos, z33b0tek 1-overview, 8-video).
  O proprio dump ressalva: GL_RENDERER e rotulo do driver (pode ser BSP antigo); nao prova o silicio.
  Nao tratar como refutacao. Fecha com: ID de chip lido de registrador/HW_REVISION, ou dump de outra
  unidade/firmware. Ate la, [CONF] so o rotulo do driver; SoC segue como informado por SDK/Copetti.
- GL_OES_framebuffer_object: modulos de titulos o referenciam (z33b0tek 8-video), mas a lista
  GL_EXTENSIONS da unidade medida nao o anuncia. Coerente com Dev Guide Tabela 7-1 ("render para textura: Nao").
  Quem o usa nos titulos e com qual fallback: nao medido.
- Dump: teste de render MIRRORED_REPEAT+GL_LINEAR em textura retangular deu watchdog (rodada 3, relato);
  a 4a rodada so testou glTexParameterx+glGetError (PASS). Render com wrap espelhado em textura retangular: nao medido.
- Dump: GL_LIGHTS max e config EGL (stencil 0 vs 4 opcional do guia) nao foram lidos.
