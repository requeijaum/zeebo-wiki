# Publicação (wiki vs site)

## Divisão
- **Wiki** (`*.md` na raiz) = caderno de laboratório. Vale contexto local, nomes de
  projetos, dossiês, logs e decisões. Não é publicada.
- **Site z33b0tek** = referência técnica pública. Fonte própria: `z33b0tek/pages/`.
  Não deriva da wiki.

## Regras do site
- Descreve a **plataforma** (MSM7201A, BREW 4.0.2, Adreno 130), nunca um emulador.
- Sem listas de compatibilidade, sem matriz de títulos.
- Sem paths locais, sem nomes de autores, sem nomes de documentos internos.
- Cada afirmação é fato de SDK público, medição em binário/dump real, ou marcada
  como não verificada.

## Garantia
`z33b0tek/gen.py` roda um lint ao final do build e falha (exit 1) se algum
identificador privado ou de terceiros aparecer no HTML.

## Fluxo
1. Editar `z33b0tek/pages/*.md`.
2. `python3 z33b0tek/gen.py` (lint deve passar).
3. Commit em `main`; o GitHub Actions reconstrói e republica o Pages.
