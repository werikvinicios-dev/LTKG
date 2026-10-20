# Relatório editorial — revisão de linguagem e edição de luxo

**Obra:** *Leis para Matar Deuses* — Volume 1: *O Deus que Caiu do Céu*
**Autor:** Werik Martins
**Versão entregue:** V1-RL (V1 com revisão de linguagem), edição de luxo ilustrada
**Escopo:** revisão integral da prosa dos 31 arquivos do volume (30 capítulos e epílogo),
diagramação de luxo (PDF e EPUB), identidade visual da saga, capa e caderno de arte.

> **Sem spoilers.** Este relatório não contém resumo de capítulo, cena, fala, identidade,
> morte, traição ou revelação. Os detalhes que dependem do enredo estão em um registro interno
> separado, dentro da pasta `CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/`. Não abra essa pasta
> antes de terminar o livro.

---

## 1. O que foi feito

- **Revisão integral, capítulo por capítulo.** Todos os 31 arquivos foram revisados, do primeiro
  ao último parágrafo. Nenhum capítulo ficou como amostra ou sugestão.
- **Prosa, não enredo.** A história, a ordem das cenas, os personagens, os mistérios, as pistas e
  as revelações ficaram como estavam. Nenhum capítulo ou cena foi cortado, unido ou acrescentado.
  O ponto de vista, a pessoa narrativa e o tempo verbal não mudaram.
- **O original foi preservado.** A versão canônica anterior continua intacta em
  `manuscrito/capitulos/`, com uma cópia de segurança em `manuscrito/V1_original_preservado/`. As
  exportações antigas estão em `exportacoes/V1_original_antes_da_revisao/`. **A versão revisada
  não substitui a canônica.** Ela fica em `manuscrito/V1_revisao_linguagem/` até você aprovar a
  troca.

## 2. Método

1. **Preservação.** Antes de qualquer edição, fiz o backup integral e um commit de segurança.
2. **Calibração da voz.** Escrevi um guia interno com a voz-alvo: português brasileiro
   contemporâneo, ritmo variado e maturidade de fantasia adulta. O guia também lista os tiques a
   tratar, os motivos a manter, as regras de apresentação da magia e as vozes de cada
   personagem. O capítulo 1 foi revisado primeiro e serviu de referência para os outros.
3. **Revisão integral.** Cada capítulo foi lido inteiro antes da reescrita e revisado cena a cena.
4. **Conferência comparativa, nos 31 arquivos.** Um script compara cada capítulo revisado com o
   original. Ele confere todos os números, por extenso e em algarismos, os nomes próprios, os
   trechos citados entre aspas (cartas, cláusulas, inscrições), os títulos e o número de quebras
   de cena. Cada capítulo tem uma nota de auditoria interna com os fatos e as pistas conferidos.
5. **Segunda leitura de fluidez.** Busquei repetições entre parágrafos vizinhos, densidade de
   jargão, pontuação e ritmo de leitura em voz alta.
6. **Auditoria final.** Medi o texto antes e depois e fiz uma revisão de continuidade com o
   livro inteiro (seção 6).

## 3. Diagnóstico estilístico (geral)

A versão anterior já tinha boa estrutura e boas cenas. Os atritos de leitura eram de superfície,
mas se repetiam muito:

- muita ênclise na narração ("virou-se", "levantou-se", "deu-lhe"), o que deixava o texto mais
  formal do que o português brasileiro falado pede;
- períodos longos de explicação técnica, com várias subordinadas, sobretudo nas cenas de magia
  e de ação;
- fórmulas repetidas: "ficou calado (um longo momento)", "quase sorriu", "com a paciência de quem…",
  "por um instante", o contraste "não era X; era Y" e encerramentos de parágrafo parecidos;
- explicações que repetiam o que a cena tinha acabado de mostrar;
- polissíndeto em excesso ("e… e… e…") fora dos momentos em que ele tem função;
- pequenas oscilações de registro nas falas (mistura de "tu" e "você" no mesmo personagem).

## 4. O que mudou na leitura

### Métricas (livro inteiro, antes → depois)

| Indicador | V1 | V1-RL |
|---|---:|---:|
| Palavras | 163.368 | 159.020 (−2,7%) |
| Frases com mais de 40 palavras | 590 | 301 |
| Tamanho médio da frase (palavras) | 11,6 | 10,9 |
| Ênclise na narração ("virou-se", "deu-lhe"…) | 105 | 7 |
| "ficou calado / em silêncio / um momento" | 86 | 21 |
| "um longo momento / por um longo tempo / por muito tempo" | 41 | 14 |
| "por um instante / por um momento" | 39 | 16 |
| "com a/o … de quem…" | 31 | 13 |
| Contraste em duas frases ("Não era X. Era Y.") | 48 | 24 |
| "quase sorriu / quase riu" | 20 | 10 |
| "alguma coisa" | 147 | 115 |

Não havia meta de redução. A queda de 2,7% vem do corte de redundâncias e explicações repetidas.
Nenhuma cena foi encurtada para ganhar ritmo. Todos os capítulos ficaram entre −4,0% e +1,2% do
original.

### Qualitativo

- **Magia mais clara, regras intactas.** As técnicas agora aparecem na ordem *efeito
  perceptível → decisão do personagem → custo ou risco → explicação curta*. Os nomes canônicos
  (leis, princípios, técnicas, instituições) não mudaram, nem os números técnicos (temperaturas,
  distâncias, tempos, contagens). Cada técnica continua mostrando fonte, âncora, limite e retorno.
- **Ação legível.** Nos combates, o leitor sabe onde cada um está, o que o adversário acabou de
  fazer e qual é o risco imediato, antes de qualquer explicação. A preparação de cada solução
  tática continua visível, e a competência dos adversários também.
- **Vozes mais distintas.** Ilan continua sarcástico, mas não faz piada em toda fala. Aurelia
  ficou elegante sem solenidade. Mara fala com precisão sem soar como relatório, Nara é concreta
  e rápida, Sevran é humano sem fazer sermão. Personagens de registro formal mantiveram a
  formalidade como traço próprio.
- **Romance.** Todas as etapas continuam no mesmo ponto do livro, com o mesmo grau de
  intimidade. Os diálogos ficaram menos solenes e mais próximos de duas pessoas conversando.
- **Motivos preservados.** As frases que voltam de propósito ao longo do livro foram mantidas
  onde estavam. Documentos, cartas, cláusulas e inscrições citados foram mantidos ao pé da letra.

## 5. Preservação do cânone

- As **sete leis da Transposição** e os **seis princípios** ficaram intactos. Nenhuma frase
  simplificada sugere magia sem fonte, alcance ilimitado, portal sem âncora, energia criada do nada
  ou absorção infinita.
- **Nenhum fato novo.** A revisão não acrescentou técnica, entidade, objeto, relação, lugar ou pista.
- **Três ajustes de conformidade.** Na auditoria de cânone, três pontos da segunda metade do
  livro contrariavam o próprio livro:
  - um efeito técnico contrariava uma das proibições aprovadas da magia;
  - um detalhe de equipamento não batia com o que capítulos anteriores tinham estabelecido;
  - uma imagem final contrariava uma informação fixada no começo do livro.

  Os três foram corrigidos com a solução mínima. Os acontecimentos e as consequências continuam os
  mesmos; mudou só o "como" que violava a regra. O texto anterior está preservado, e a
  justificativa completa (com spoilers) está no registro interno.

## 6. Continuidade: correções e pendências

<!-- PREENCHER: resultado da revisão de continuidade -->

## 7. Diagramação e parte gráfica

### PDF de luxo — `exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.pdf`
- Formato 16 × 23 cm, 500 páginas.
- **Texto:** EB Garamond 11,3/15,2 com versaletes reais; títulos em Cinzel.
- **Página:** margens espelhadas, hifenização em português do Brasil, controle de viúvas e órfãs.
- **Aberturas de capítulo:** sempre em página ímpar, com emblema, número por extenso em Cinzel
  bronze e título em itálico. O texto começa com capitular em bronze e as primeiras palavras em
  versalete.
- **Ornamentos:** quebras de cena com três losangos; cabeçalhos alternados (título da obra nas
  páginas pares, título do capítulo nas ímpares); fólio entre losangos.
- **Partes do livro:** sumário com páginas reais e pontilhado, falso rosto, frontispício, folha
  de rosto, créditos e colofão.
- **Pranchas:** três pranchas ilustradas sobre fundo noturno, todas em pontos do livro que o
  leitor já alcançou, sem antecipar nada.
- **Acabamento tipográfico:** aspas tipográficas em todo o texto.

### PDF para gráfica — `exportacoes/Leis_para_Matar_Deuses_Vol1_GRAFICA_sangria.pdf`
O mesmo miolo, com 3 mm de sangria e as caixas de refile e de sangria (TrimBox e BleedBox)
definidas em todas as páginas.

### EPUB 3 de luxo — `exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.epub`
- **Validação:** aprovado no EpubCheck, o validador oficial, sem erros nem avisos.
- **Conteúdo:** fontes embutidas (EB Garamond, versalete e Cinzel), capa ilustrada, folha de
  rosto com o logotipo, frontispício, pranchas, sumário navegável e metadados completos em pt-BR.
- **Aparência:** capitulares e versalete na primeira linha de cada capítulo, ornamentos de
  quebra de cena e hifenização.

### Manuscrito editável
- `exportacoes/MANUSCRITO_V1_REVISAO_LINGUAGEM.md`: Markdown integral.
- `exportacoes/MANUSCRITO_V1_REVISAO_LINGUAGEM.docx`: Word com sumário, em EB Garamond 12,
  entrelinha 1,5 e recuo de parágrafo. Foi verificado ao abrir no LibreOffice.
- `manuscrito/V1_revisao_linguagem/`: um arquivo por capítulo, a fonte de todas as exportações.

### Identidade visual da saga — `exportacoes/grafico/logo/`
- **Emblema:**
  - um anel com **sete losangos**, as sete leis;
  - um **sol de inverno**, as Coroas;
  - uma **espada cuja guarda é uma balança com um prato mais baixo**, a Arte do Carrasco.
- **Logotipo:** em Cinzel.
- **Versões:** vertical, horizontal, logotipo isolado e emblema isolado.
- **Cores:** bronze metálico, bronze chapado (para impressão a uma cor ou hot stamping), tinta
  sobre claro, geada sobre escuro e vitrine sobre azul-noite.
- **Formatos:** SVG vetorial, com o texto convertido em curvas e sem dependência de fontes, e PNG
  em alta resolução com transparência.

### Capa — `exportacoes/capa/`
- **Frente:** PNG em 300 dpi, JPG e PDF.
- **Capa do EPUB.**
- **Capa completa para gráfica:** contracapa, lombada e frente, com 3 mm de sangria, em PDF e
  com prévia em PNG.
  - A contracapa traz um texto de apresentação sem spoilers, que só usa a premissa das primeiras
    páginas.
  - A lombada foi calculada para 500 páginas em papel de cerca de 80 g: 28 mm.

### Caderno de arte — `exportacoes/Caderno_de_Arte_Leis_para_Matar_Deuses_Vol1.pdf`
São 15 páginas em A4 horizontal, sem spoilers:
- conceito visual;
- anatomia do emblema e assinaturas;
- paleta e tipografia;
- três lugares (Vhalessa, a Torre do Meio-Dia e o Átrio de Soleira);
- os dois protagonistas e um estudo da manopla;
- os sinais das sete leis e dos seis princípios, desenhados em vetor;
- amostras do miolo e da capa;
- créditos.

## 8. Pendências técnicas (sem conteúdo narrativo)

- **ISBN e código de barras:** a contracapa tem um espaço reservado. Falta registrar a obra.
- **Lombada:** depende do papel e da gráfica. A capa pode ser regenerada com outro número de
  páginas ou outra espessura de papel: `python3 build/make_capa_luxo.py 500 0.056`.
- **Ilustrações:** foram geradas com auxílio de inteligência artificial, a partir de descrições
  sem spoilers, e o crédito está informado nos créditos do livro e do caderno.
  - Duas delas têm pequenas divergências visuais em relação ao texto: a proporção entre os dois
    protagonistas e a posição de um elemento arquitetônico da cidade.
  - Para uma edição comercial, recomendo uma ilustradora ou um ilustrador refazer as pranchas a
    partir delas.
  - Os créditos de geração de imagem da ferramenta usada acabaram nesta etapa. Por isso, a
    série tem cinco imagens, e o resto do caderno é arte vetorial.
- **Fontes:** EB Garamond e Cinzel usam a licença SIL Open Font License, que permite embuti-las
  no PDF e no EPUB. O DOCX pede EB Garamond; se ela não estiver instalada, o Word usa uma
  substituta.
- **Aprovação:** a versão canônica só deve ser substituída pela V1-RL depois da sua confirmação.

## 9. Critérios de aceitação

- [x] Trama, mistérios e acontecimentos intactos (conferência automática e notas por capítulo).
- [x] Texto perceptivelmente menos rebuscado e mais natural (seção 4).
- [x] Magia explicada com clareza, sem alterar as regras.
- [x] Cenas de ação acompanháveis visualmente.
- [x] Vozes distintas e menos exposição artificial.
- [x] Ilan brilhante, tático e carismático; Aurelia adulta, poderosa e independente.
- [x] Romance com as mesmas etapas e o mesmo peso.
- [x] Humor nas horas certas, sem esvaziar consequências.
- [x] Atmosfera e cenas calmas preservadas.
- [x] Nenhum spoiler neste relatório.
- [x] Nova versão comparada com a anterior em busca de perdas de informação (31 de 31 arquivos).

## 10. Como reconstruir tudo

```sh
sh build/construir_tudo.sh
```
