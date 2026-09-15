# skill-impact
- SKILL F0-extrair: max_tokens 800 -> 2000 (content vazio, revertido p/ 2000). Wiki mantém lição.
- F0 célula loader-zeebulator lfm: genérica + path FONTE errado → [INCERTO], superada por ls direto (ggz/bar/mif/mod.cpp) [CONF]. Lição: lfm sem grep-contexto alucina path; manter keyword-chunks.
- F0 célula brew-zeebulator lfm: genérica nível README → [INCERTO], superada por ls (20 módulos) [CONF]. Padrão: lfm resume dossier, não enumera; enumeração fica com trilha direta.
- F0 célula brew-zeemu lfm: lista 10 módulos bate com ls (51 .cpp) → [CONF corrobora]. Refinamento: lfm enumera bem com keyword-chunks; resume mal sem eles.
- F0 final lfm (10 células): CONF corroboram = brew-zeemu, infuse-status, zeeno-status, abi-eventos, sdk-headers.
INCERTO = loader-zeebulator, brew-zeebulator (genéricas), oem-zwheel + ggz-formato (fora do tópico), runtime-brew (vaga). Regra: lfm fiel a lista/valor literal no chunk; síntese livre = conferir ou descartar.
- Job enum F3-F6 v2 travou na célula 1 de novo (request sem retorno; LM saudável no probe). Regra: trilha direta primeiro; lfm só p/ lotes pequenos com deadline, nunca caminho crítico.
- CORREÇÃO: fork canônico = projects/curupira branch dev (core/+tools/+tests); zeebo-emulator/full-rewrite guarda docs/testkit/research. Confrontos passam a mirar curupira/dev.
- Direção: confronto curupira PARKED (in-dev, pedido 15/09). Foco volta ao clone + dossiers; CONFRONTO-fork.md congela como está.
- Slot SetClipRect: divergência 18v19 resolvida p/ 18 (IBase=2 slots). Lição: nunca assumir QueryInterface na vtable; contar a partir do INHERIT_IBase real.
- Site separado da wiki: z33b0tek passou a ter fonte própria (pages/) + lint que quebra o build. Motivo: scrub frágil vazava nomes de projetos; wiki é lab, site é referência.
