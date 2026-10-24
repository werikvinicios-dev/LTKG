# Trailer oficial — Leis para Matar Deuses

Motion 2D/2.5D, 95,7 segundos, sem narração (decisão do autor: as frases do roteiro entram como textos na tela). Só usa artes do banco que não estão nas pastas de spoiler.

## Arquivos

| Arquivo | O que é |
|---|---|
| `LMD_trailer_oficial_96s_1080p.mp4` | Trailer principal. 1920×1080, 24 fps, H.264, áudio AAC estéreo 48 kHz, −16 LUFS |
| `LMD_trailer_96s_vertical_1080x1920.mp4` | Versão vertical 9:16 (Reels), reenquadrada cena a cena |
| `LMD_teaser_30s_1080p.mp4` | Teaser de 30 s. Os recortes não partem nenhum texto |
| `LMD_teaser_15s_1080p.mp4` | Teaser de 15 s |
| `LMD_trailer_96s_1080p_sem_textos.mp4` | Mesma imagem sem os letreiros, para remontagem ou legendagem |
| `LMD_trailer_96s_1080p_sem_musica.mp4` | Só os efeitos sonoros, para remontagem |
| `audio/LMD_trilha_original.wav` | Trilha separada, tocada com orquestra gravada (WAV 24 bits, 48 kHz) |
| `audio/LMD_efeitos_sonoros.wav` | Efeitos sonoros separados |
| `audio/LMD_mix_final.wav` | Mistura final |
| `audio/CREDITOS_SOM.md` | De onde veio cada som e a licença de cada banco |
| `LMD_trailer_linha_do_tempo.json` | Linha do tempo: planos, fontes de arte, movimentos, letreiros e cortes dos teasers |

## Projeto editável

O projeto é o código em `build/trailer/`. Cada plano é uma função com câmera, camadas e efeitos; mudar um número muda o plano.

- `base.py`: motor. Faz a câmera 2.5D por mapa de profundidade, neve em três profundidades, névoa e vento em tecido e cabelo (por máscaras de segmentação). Também faz os raios de luz, a gradação de cor, o grão, a gravura de tinta e a tipografia.
- `cenas.py`: as dez cenas do roteiro, os letreiros (`LETREIROS`) e a linha do tempo (`LINHA`).
- `audio.py`: trilha original (tema em ré menor) tocada com amostras gravadas, efeitos gravados sincronizados e mistura.
- `amostras.py`: sampler das gravações (escolhe a nota e a dinâmica, transpõe pouco, sustenta notas longas e recorta golpes).
- `banco.py`: baixa os bancos de som e escreve os créditos.
- `render.py`: render paralelo. Uso: `python3 render.py 16x9 saida.mp4 audio.wav`. Com `SEM_TEXTO=1`, sai sem letreiros.
- `primeiro_som.py`: a cena 1 (o fio e a gota).
- `remontar.sh` e `remontar2.sh`: renderizam só as cenas refeitas e emendam com os trechos que não mudaram.
- `letreiros.py`: aplica os letreiros animados sobre um vídeo sem textos.
- `versoes.py`: teasers, versão sem música, stems e linha do tempo.

## Como foi feito

- **Pinturas que ganham vida.** Cada placa tem um mapa de profundidade (Depth Anything V2). A câmera faz parallax e travellings em que o primeiro plano se move mais que o fundo. Cabelo, casacos e véus têm máscaras próprias (segmentação de roupas) e se mexem com um campo de vento. A neve cai em três camadas de profundidade.
- **Magia como engenharia.** Nenhum raio sai das mãos e não há círculo mágico decorativo. O que aparece é um fio sob tensão que vibra e para no contato da gota, uma gota no aço, calor numa célula da manopla, rachaduras no gelo, uma onda de choque que levanta neve e metal vibrando. Os símbolos oficiais das sete leis aparecem gravados na matéria, cada um com um fenômeno físico curto.
- **Personagens oficiais.** Ilan (PE-001, PE-025 e as cenas do capítulo 1) aparece com a manopla no antebraço esquerdo. Nenhuma imagem foi espelhada. Mara é a do PE-003, de coque escuro e óculos redondos. Aurelia aparece nas versões douradas aprovadas (PE-012 e PE-013).
- **O primeiro som.** Plano macro: um fio de prata vibra, a gota presa nele se solta e a câmera desce com ela até uma chapa de aço escovado molhada, onde ela respinga e levanta um jato d'água.
- **As sete leis.** São os brasões pintados (SI-001). Cada lei se monta: o eixo cresce do centro para as pontas, a estrutura é traçada em volta e as pérolas descem pelo eixo e travam. A câmera acompanha de perto e no fim recua para mostrar as sete. Em "O último carrasco" o tempo para: a neve fica suspensa, a cor esfria, a geada cresce das bordas e o selo de cera da Ordem da Última Sentença (FA-001) cai e é prensado sobre a imagem congelada.
- **O livro.** A metade esquerda gira sobre a lombada e cai sobre a outra; passando do meio do giro, aparece a capa do volume 1 (CA-001). Depois do baque, a câmera enquadra o livro fechado.
- **O gelo racha.** Fissuras escuras que se ramificam a partir do impacto, com anel de fratura, borda de luz, fratura leitosa e refração do gelo em volta.
- **Letreiros.** Cada palavra entra em sequência, subindo e saindo do desfoque.
- **Título.** O emblema e o letreiro oficiais (ID-008 e ID-006) se montam peça por peça. O arco se fecha e o estandarte se desenrola. A espada desce do alto, passa pelo anel da coroa e se crava, tremendo, com faíscas e um tranco na imagem. A balança pousa na guarda da espada, oscila e para nivelada, e as sete pérolas acendem. O halo de raios fecha com uma onda de choque e as letras do título encaixam uma a uma. Cada encaixe tem o seu golpe de metal e de orquestra. As peças são recortes do desenho oficial, sem redesenho.
- **Som.** Não há mais som sintetizado. A trilha é tocada com a orquestra gravada do VSCO-2-CE (cordas, metais, flauta, harpa, tímpanos, bumbo, gongo e pratos). Os efeitos são gravações reais do BigSoundBank, do Kenney e do OpenGameArt: vento, sino, gota, cordas sob tensão, lâminas, gelo, fogo, papel, livro, relógio, corrente, tecido, passos na neve, respiração e a espada (cortando o ar, entrando como numa bainha e vibrando presa). Todos os bancos são CC0, uso comercial livre.

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
14. Título: monta de 87,5 s a 92,3 s e fica completo e legível por cerca de 2,6 s antes do escurecimento. ✔

## Limites desta versão

- **Animação dos personagens.** Eles respiram, o cabelo e a roupa se mexem com o vento e há vapor do hálito. Não há animação quadro a quadro de ações (andar, girar o corpo, sacar a espada), piscadas nem olhos mudando de direção. Em vez de deformar as pinturas, a ação vem dos cortes, da câmera e dos efeitos físicos.
- **Trilha.** É tocada com amostras gravadas de uma orquestra de câmara (VSCO-2-CE). Soa real, mas é um naipe pequeno e sem coro. Uma orquestra grande ou uma biblioteca comercial dariam mais peso no confronto, e a faixa e os stems estão separados para isso.
- **Versão do 21st Video.** O projeto no editor do 21st ainda está na montagem anterior (90 s), com as frases animadas palavra por palavra. O plano gratuito do 21st só exporta até 30 s em 720p, então os 90 s de lá precisam de um plano pago. Os arquivos desta pasta saem do motor próprio e não têm esse limite.
- **Projeto editável.** O projeto é o código Python com a linha do tempo. Não há arquivo de After Effects ou Premiere.
