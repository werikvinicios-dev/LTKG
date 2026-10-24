# Trailer oficial — Leis para Matar Deuses

Motion 2D/2.5D, 90 segundos, sem narração (decisão do autor: as frases do roteiro entram como textos na tela). Só usa artes do banco que não estão nas pastas de spoiler.

## Arquivos

| Arquivo | O que é |
|---|---|
| `LMD_trailer_oficial_90s_1080p.mp4` | Trailer principal. 1920×1080, 24 fps, H.264, áudio AAC estéreo 48 kHz, −16 LUFS |
| `LMD_trailer_90s_vertical_1080x1920.mp4` | Versão vertical 9:16 (Reels), reenquadrada cena a cena |
| `LMD_teaser_30s_1080p.mp4` | Teaser de 30 s. Os recortes não partem nenhum texto |
| `LMD_teaser_15s_1080p.mp4` | Teaser de 15 s |
| `LMD_trailer_90s_1080p_sem_textos.mp4` | Mesma imagem sem os letreiros, para remontagem ou legendagem |
| `LMD_trailer_90s_1080p_sem_musica.mp4` | Só os efeitos sonoros, para remontagem |
| `audio/LMD_trilha_original.wav` | Trilha separada (WAV 24 bits, 48 kHz) |
| `audio/LMD_efeitos_sonoros.wav` | Efeitos sonoros separados |
| `audio/LMD_mix_final.wav` | Mistura final |
| `LMD_trailer_linha_do_tempo.json` | Linha do tempo: planos, fontes de arte, movimentos, letreiros e cortes dos teasers |

## Projeto editável

O projeto é o código em `build/trailer/`. Cada plano é uma função com câmera, camadas e efeitos; mudar um número muda o plano.

- `base.py`: motor. Faz a câmera 2.5D por mapa de profundidade, neve em três profundidades, névoa e vento em tecido e cabelo (por máscaras de segmentação). Também faz os raios de luz, a gradação de cor, o grão, a gravura de tinta e a tipografia.
- `cenas.py`: as dez cenas do roteiro, os letreiros (`LETREIROS`) e a linha do tempo (`LINHA`).
- `audio.py`: trilha original sintetizada (tema em ré menor), efeitos sincronizados e mistura.
- `render.py`: render paralelo. Uso: `python3 render.py 16x9 saida.mp4 audio.wav`. Com `SEM_TEXTO=1`, sai sem letreiros.
- `versoes.py`: teasers, versão sem música, stems e linha do tempo.

## Como foi feito

- **Pinturas que ganham vida.** Cada placa tem um mapa de profundidade (Depth Anything V2). A câmera faz parallax e travellings em que o primeiro plano se move mais que o fundo. Cabelo, casacos e véus têm máscaras próprias (segmentação de roupas) e se mexem com um campo de vento. A neve cai em três camadas de profundidade.
- **Magia como engenharia.** Nenhum raio sai das mãos e não há círculo mágico decorativo. O que aparece é um fio sob tensão que vibra e para no contato da gota, uma gota no aço, calor numa célula da manopla, rachaduras no gelo, uma onda de choque que levanta neve e metal vibrando. Os símbolos oficiais das sete leis aparecem gravados na matéria, cada um com um fenômeno físico curto.
- **Personagens oficiais.** Ilan (PE-001, PE-025 e as cenas do capítulo 1) aparece com a manopla no antebraço esquerdo. Nenhuma imagem foi espelhada. Mara é a do PE-003, de coque escuro e óculos redondos. Aurelia aparece nas versões douradas aprovadas (PE-012 e PE-013).
- **Título.** Usa o emblema e o letreiro oficiais (ID-008 e ID-006) com reflexo metálico.

## Auditoria

1. Rosto de Ilan: o mesmo retrato oficial em todos os closes. ✔
2. Manopla no antebraço esquerdo: conferida em PE-001, PE-025, PE-021 e C01-a. ✔
3. Aurelia na aparência aprovada (PE-012 e PE-013). ✔
4. Mara na referência atual (coque escuro, óculos redondos). ✔
5. Símbolos e brasões tirados dos assets oficiais (leis, Ordem da Última Sentença, emblema, letreiro). ✔
6. Magia mostrada só como causa e efeito físico. ✔
7. Sem spoilers: nenhuma imagem das pastas de spoiler e nenhuma cena que mostre a queda do deus ou um confronto resolvido. ✔
8. Sem deformações: não há geração de vídeo por IA, então não há mãos ou rostos derretidos. O movimento é de câmera e de camadas. ✔
11. Narração: substituída por letreiros a pedido do autor. ✔
13. A gradação de cor é a mesma em todas as cenas: negro mineral, azul glacial, âmbar e ouro velho. ✔
14. Título final legível por cerca de 5 s. ✔

## Limites desta versão

- **Animação dos personagens.** Eles respiram, o cabelo e a roupa se mexem com o vento e há vapor do hálito. Não há animação quadro a quadro de ações (andar, girar o corpo, sacar a espada), piscadas nem olhos mudando de direção. Em vez de deformar as pinturas, a ação vem dos cortes, da câmera e dos efeitos físicos.
- **Trilha sintetizada.** A trilha foi sintetizada em código, sem bibliotecas de instrumentos gravados. A estrutura segue o roteiro (mistério, tensão, fascínio, confronto, silêncio e assinatura) e tem um tema próprio. Uma orquestra ou bibliotecas reais vão soar melhor, e a faixa e os stems estão separados para isso.
- **Projeto editável.** O projeto é o código Python com a linha do tempo. Não há arquivo de After Effects ou Premiere.
