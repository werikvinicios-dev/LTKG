# Banco de arte ampliado 4×

Versões em alta resolução das artes que vão para a loja, para a divulgação e para o livro digital. Foram ampliadas
na máquina com Real-ESRGAN x4plus (licença BSD-3) pelo script `build/aresta/ampliar.py`, que leva cerca de
2 minutos por imagem na CPU. Os originais continuam em `../banco_de_arte/`, e a numeração é a mesma.

| Pasta | Arquivos | Tamanho |
|---|---|---|
| `07_capas/` | capas dos volumes I a IV | 4096 × 6144 |
| `10_promocional/` | pôster e post de lançamento | 4096 × 6144 e 4096 × 4096 |
| `05_mundo/` | Fornalha Velha (prancha do livro) | 5504 × 3072 |
| `06_personagens/` | retratos de Ilan, Aurelia, Mara, Nara e Sevran | 4096 × 6144 |

- **Retratos.** Os retratos são uma mistura de 60% do Real-ESRGAN com 40% de ampliação Lanczos do original
  (`--mistura=0.6`). O modelo puro deixa a pele lisa demais, e a mistura devolve a textura sem perder a nitidez
  do cabelo e dos olhos. Capas, divulgação e cenários usam o resultado puro.
- **Retoque da capa do Vol. I.** A arte original tinha três borrões claros sob "MATAR D". Eles foram removidos na
  versão 4× por `build/aresta/retoque_capa.py`, que roda depois da ampliação.
- **Onde são usadas.** A capa do e-book (`../capa_v2/capa_ebook.jpg`, 1781 × 2560), a frente em alta
  (`../capa_v2/capa_frente_alta_resolucao.jpg`) e a prancha da Fornalha Velha no PDF de luxo saem daqui.
- **Para ampliar outra arte:** `python3 build/aresta/ampliar.py [--mistura=0.6] exportacoes/banco_de_arte/<pasta>/<arquivo>.png`
  (use `--mistura=0.6` quando houver rosto em primeiro plano).
