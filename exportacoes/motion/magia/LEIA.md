# Animações canônicas da magia

São animações curtas, com som, em 1920×1080 a 30 fps. Cada uma mostra uma técnica do livro funcionando como o
cânone descreve. Abre com uma pintura do banco de arte e segue para uma demonstração em estilo de manual técnico:
- fonte, âncora, elo, destino e retorno aparecem em sequência, com legendas;
- no fim, a lei da Transposição que a cena ilustra.

A linguagem visual segue `exportacoes/identidade_aresta/GUIA_VISUAL_DA_MAGIA.md`: efeito físico real, âncoras
físicas, elo como fio tenso com franjas na cor da disciplina, custo à vista (células da manopla, vapor, trincas).

| Arquivo | Técnica | Capítulo |
|---|---|---|
| `MG-01_afericao.mp4` | Aferição: leitura com a lente (Igneo) | 1 |
| `MG-02_reversao_do_sifao.mp4` | Reversão do sifão: Saldo Final (Igneo) | 1 |

As outras seis animações mostram técnicas de capítulos posteriores. Elas ficam na pasta de spoilers, junto com o
rolo completo.

**Como refazer:** `python3 build/motion/magia_canonica.py [cena ...]`. O motor de desenho e de som fica em
`build/motion/magia_motor.py`.
