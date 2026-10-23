# ⚠️ INTERNO — Guia de voz da V2 (ritmo e humor de Rick Riordan, peso adulto)

**Decisões do autor (23/10/2026):**
- 3ª pessoa, bem colada na cabeça do personagem do capítulo (como em *Os Heróis do Olimpo*). Nunca 1ª pessoa.
- Ritmo e humor do Riordan, **sem suavizar nada**: o livro continua fantasia adulta +18. Violência, dor, morte, sexo
  e escolhas morais ficam com o mesmo peso e o mesmo nível de detalhe.
- Títulos de capítulo engraçados, no estilo Riordan.
- Ilan é **alto** (ficha visual). Corrigir "altura média" e qualquer coisa que diga o contrário.
- Selos mágicos no lugar das âncoras: ver `ADENDO_SELOS.md`.
- Português brasileiro simples, de conversa. Nada rebuscado.

Referência de calibração: `manuscrito/V2/01.md`. Leia antes de começar. Fonte de cada capítulo: `manuscrito/V1_revisao_linguagem/NN.md` (fica intacta). Saída: `manuscrito/V2/NN.md`.

## 1. Como soa

- **Frases curtas e diretas.** Uma ideia por frase. Parágrafos curtos. Frase de uma linha sozinha para bater forte.
- **O narrador pensa como o personagem.** O que o Ilan acha engraçado, irritante ou absurdo aparece no texto, com o
  jeito dele: seco, cansado, observador, irônico. Mara é precisa e afiada; Nara é prática e impaciente; Sevran é
  gentil e debochado; Aurelia é antiga, divertida e perigosa. Cada um puxa a narração para o próprio humor.
- **Comentário de lado.** Pequenos apartes no meio da ação: "Isso, para constar, não era um bom sinal." "Ilan tinha
  três regras para trabalhar no frio. Estava quebrando as três."
- **Listas com virada.** "Ele tinha uma espada, uma manopla rachada e um plano. Duas dessas coisas funcionavam."
- **Exagero cômico preciso** em coisas pequenas (burocracia, comida, frio, contrato), nunca nas mortes.
- **Final de capítulo com gancho**: última linha curta, que dá vontade de virar a página.
- **Diálogo rápido**, com resposta atravessada e piada de personagem. Fala natural brasileira ("tá", "pra" só em fala, e
  com moderação; narração usa "está", "para").
- **Ação clara**: onde cada um está, o que quer, o que muda. A magia aparece em imagens bonitas e rápidas (riscos de
  luz, selos acendendo em fila, rastros que somem), sem aula de física. A explicação vem depois, numa frase, se
  precisar.

## 2. O que não fazer

- Não mudar fatos, nomes, números, ordem das cenas, pistas, revelações, mortes, quem faz o quê. Só a forma.
- Não criar cena nova, personagem novo, técnica nova, lugar novo.
- Não infantilizar, não tirar palavrão onde existe, não amaciar violência nem sensualidade.
- Não transformar todo parágrafo em piada. Cena triste fica triste: humor some, frases ficam simples e secas.
- Não usar gíria datada nem referências do nosso mundo (nada de celular, cinema, super-herói, internet).
- Não usar mais-que-perfeito simples (estivera, fizera), mesóclise, ênclise de livro antigo ("deixou-a").
- Não mudar a quantidade nem a posição das quebras `---`.
- Não explicar a mesma regra de magia duas vezes no mesmo capítulo.

## 3. Formato do arquivo

- Primeira linha: `# Capítulo N — Título novo engraçado` (Epílogo: `# Epílogo — Título`).
- Título engraçado no estilo Riordan: frase curta que conta uma verdade do capítulo com ironia, sem dar spoiler
  grande. Exemplos de tom: "Onze páginas de contrato e nenhuma de bom senso", "Eu pago pedágio para um deus" (mas
  sempre em 3ª pessoa ou impessoal, já que o narrador não é o Ilan: "Ilan paga pedágio para um deus").
- Mesmo tamanho aproximado do capítulo original (pode variar ±15%).
- Markdown simples: parágrafos separados por linha em branco, itálico com `*`, quebras de cena `---`.
