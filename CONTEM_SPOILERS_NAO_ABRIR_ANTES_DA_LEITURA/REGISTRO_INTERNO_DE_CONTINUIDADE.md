# ⚠️ INTERNO — CONTÉM SPOILERS — Registro de continuidade da revisão de linguagem (V1)

**Documento do ambiente de edição. Não mostrar ao autor antes de ele ler o livro.** Cita cenas,
falas, mortes, culpados e o desfecho do Volume 1. O relatório visível ao autor é outro
(`relatorio/RELATORIO_EDITORA_SEM_SPOILERS.md`); este registro é a auditoria técnica prevista no §12 do briefing.

Resumo: 49 entradas numeradas de pendência nas 31 notas de auditoria (mais 2 observações não
numeradas, nas notas 02 e 22). Descontadas 4 remissões cruzadas, são **45 problemas distintos**:
**9 corrigidos como correção mecânica (A)**, com 10 edições em 8 capítulos (§3); **1 encerrado**
(26-1, resolvido pela correção pré-aprovada do cap. 27, §2); **35 para decisão do autor (B)** (§4).
A conferência do §5 achou **3 itens novos (N1–N3)**, também B. O editor de continuidade não fez
commit; as 10 edições do §3 entraram no commit `135f87a` do coordenador, e este registro e as
marcações nas notas de auditoria estão no diretório de trabalho, sem commit.

---

## §1 Escopo e método da revisão

**Arquivos.** 31 arquivos em `manuscrito/V1_revisao_linguagem/` (`01.md` … `30.md` = capítulos 1–30;
`31.md` = Epílogo). O original intocado está em `manuscrito/V1_original_preservado/` (backup de
segurança no commit `520cc24`). `manuscrito/capitulos/` e o original preservado não foram tocados em
nenhuma etapa. O estado revisado antes desta etapa está no commit do coordenador `d450938`; as
10 edições do §3 entraram depois no commit `135f87a`, feito pelo coordenador.

**Natureza da revisão.** Revisão de prosa, sem reescrita de enredo (briefing §§00, 09, 13): fatos,
números, nomes, cronologia, causalidade, ordem de cenas e revelações, pistas, POV (3ª limitada),
tempo verbal (passado), títulos e quebras `---` preservados. Contradições de trama não foram
corrigidas por improviso: foram registradas na seção "Pendências" de cada nota de auditoria
(`auditoria_revisao/NN.md`) e consolidadas aqui. Únicas alterações de fato permitidas: as quatro
correções pré-aprovadas do guia §10 (§2 abaixo) e as correções mecânicas desta etapa (§3).

**Metas do guia de calibração** (`GUIA_DE_CALIBRACAO_DA_REVISAO.md`):
- voz: português brasileiro contemporâneo, próclise na narração, "lhe" só em fala formal (Ione,
  Ossan, Pimm, Anúbis), "tu/teu" soltos de Ilan harmonizados para "você/seu";
- tiques com teto por capítulo: contraste corretivo "não era X, era Y" (≤ 1); "com a X de quem…"
  (≤ 2); "quase sorriu/riu" (≤ 1); silêncios ("ficou calado", "não respondeu") e "por um
  instante/momento" cortados pela metade; "alguma coisa" trocada pelo substantivo concreto, exceto
  onde a vagueza é intencional; frases de efeito em série e fechamentos aforísticos variados;
- magia: modelo efeito → decisão → custo → explicação curta; toda técnica mantém fonte, âncora,
  elo, destino, limite e Retorno visíveis; nomes canônicos e números técnicos intocáveis;
- motivos deliberados e textos de documento citados preservados literalmente (lista em §6);
- extensão entre ~85% e ~110% do original.

**Ferramentas de conferência.**
- `build/compara_capitulo.py NN`: compara original × revisado (palavras, título, quebras de cena,
  parágrafos, algarismos, números por extenso, nomes capitalizados, trechos entre aspas).
  Rodado nos 31 capítulos antes desta etapa (linha de base), depois de cada capítulo editado e de
  novo nos 31 ao final.
- Notas de auditoria por capítulo (números, nomes e pistas conferidos; intervenções; pendências).
- `MATRIZ_CONTINUIDADE.md` (fatos fixados até o cap. 27) e `BIBLIA_INTERNA_SAGA_E_VOLUME_1.md`
  (numeração das leis, p. ex. Dissipação = lei 5).
- Leitura cruzada dos trechos em questão no revisado, no original e nos capítulos vizinhos (grep
  por âncoras de tempo: "ontem", "anteontem", "véspera", "há N dias", horários).

**Resultado da conferência final (31/31 capítulos).** Título idêntico 31/31; número de quebras
idêntico 31/31; trechos entre aspas idênticos 31/31. Extensão total 163.368 → 159.023 palavras
(−2,7%); por capítulo, de −4,0% (cap. 22) a +1,2% (cap. 27), dentro da faixa do guia. Comparada
à linha de base, a saída do script só mudou nos capítulos editados nesta etapa, e só nas contagens
de número esperadas (p. ex. cap. 20: "doze" 9→8, "onze" 4→5).

**Método desta etapa (continuidade).** (1) Leitura das pendências das 31 notas. (2) Verificação de
cada uma no texto revisado, no original e nos capítulos vizinhos, montando o calendário pelos
próprios marcadores do texto (§5.1). (3) Classificação:
- **A — correção mecânica:** erro inequívoco de referência temporal relativa, concordância, número
  que contradiz conta explícita do livro, ou troca manhã/tarde quando o texto fixa o horário em
  outro ponto; 1 a ~8 palavras; não muda quem fez o quê, a ordem ou o conteúdo de revelações nem
  pistas; **uma só correção possível**. Na prática: a expressão errada é falsa em qualquer leitura
  razoável (inclusive a convenção de quem não dormiu e conta a madrugada como o dia anterior, e
  eventuais episódios fora de cena que o texto não exclua), e uma única expressão de substituição é
  verdadeira em todas.
- **B — decisão do autor:** tudo o que é interpretável (fala imprecisa de personagem, evasiva,
  pista), geometria e blocagem, horários de clímax, números de mundo, o que exigiria acrescentar
  frase ou técnica, ou o que admite mais de uma solução razoável.
(4) Aplicação só das A, com a menor edição possível, e nova conferência por script.
(5) Conferência dos fatos de continuidade do §5.

---

## §2 Correções de conformidade canônica pré-aprovadas e aplicadas (guia §10)

Aplicadas pelo coordenador antes desta etapa; conferidas agora no texto revisado.

**1. Cap. 27 — passagem sobre a caixa (reflexos nos caps. 28 e 29).**
- *Problema:* o V1 dizia que a passagem de Aurelia sobre o Mandato "não tinha âncora, não tinha
  extremidade preparada" — "uma soleira de dois lados no ar, uma na superfície do lago, outra sobre a
  caixa aberta, a dez passos". Portal sem âncora: viola a proibição de portais não ancorados
  (briefing §04; guia §4).
- *Solução:* o trenó encalha atravessado na margem; a caixa fica a um metro da água, pesada e presa
  à armação de ferro, impossível de virar no lago. Aurelia "fez das próprias mãos as duas
  extremidades": palma direita dentro do lago, palma esquerda sobre o Mandato — "duas âncoras de carne
  e osso, presas à Coroa dela por um elo que atravessava o próprio corpo" (âncoras somáticas de uma
  Soberania dos Limiares). A passagem é minúscula ("deixaria escorrer um fio de água") e ela a força
  "muito além da vazão"; o Retorno, que numa estação cairia na pedra dos batentes, "caiu nela".
  Resultado idêntico ao V1: a água a 0 °C racha a cerâmica de lastro, o Mandato de Calvenor se
  desfaz, Aurelia paga com o corpo (custo que sustenta o cap. 29).
- *Capítulos tocados:* 27 (a passagem); 28 (menção: "usando o corpo como as duas extremidades e
  pagando o custo inteiro com ele"); 29 (duas menções: "usando as próprias mãos como extremidades";
  "com as próprias mãos no lugar das extremidades"). Nenhuma menção restante a "sem âncora".

**2. Cap. 27 — "faísca azul" → globo de Clarão.**
- *Problema:* o V1 tirava a faísca de um "resíduo de carga que tinha sobrado da descarga do leão de
  bronze… guardado na célula velha", mas esse resíduo foi recebido pela célula 1, que estourou
  (cap. 18). A manopla não tinha carga utilizável naquele ponto.
- *Solução:* ao lado da porta da fachada da estação do Passo Cinzento há um globo antigo de vidro de
  Clarão, cheio até a borda por quarenta anos de luz sem uso (lei da Capacidade); Ilan o solta da
  argola, sai ao pátio e o esmaga contra a quina do arco: clarão branco, eco do globo do corredor do
  Sete Chaminés (cap. 1). Fala de Ulvra ajustada: "Você quebrou uma luz no meu vale. Foi recado ou
  foi tolice?" (V1: "Você acendeu uma faísca azul. Foi um recado ou foi tolice?"). Apoio no mesmo
  capítulo: na conferência das células, "Todas vivas. Todas vazias, porque ele já tinha gastado o que
  tinha" (V1: "todas vazias agora", porque a faísca acabara de gastá-las).
- *Observação:* o guia dava como premissa que as células "foram esvaziadas no cap. 26", o que o 26
  não narra (nota 26, pendência 1). A correção não depende disso: o apoio textual ficou no próprio
  27. **Pendência 26-1 encerrada.**
- *Capítulos tocados:* 27.

**3. Epílogo — último parágrafo.**
- *Problema:* o V1 situava o terreno "numa cidade do norte onde o degelo começava" e mostrava Ilan
  plantando a primeira figueira em abril, com uma campainha que "às vezes tocava". Contradiz Tarvel,
  "onde não neva nunca" (caps. 1 e 30), o sul para onde Ilan ia, e o "Não este ano" das figueiras
  (cap. 30).
- *Solução:* "nas colinas de Tarvel, onde não nevava nunca, um terreno de pedra e mato tinha dono
  desde a primavera. Ainda não tinha figueiras." Cerca e porta pequena, trinco de um lado e campainha
  do outro; Ilan em outro lugar, "não sabia de nada disso ainda, e era feliz" (preservado). "O
  terreno esperava. A porta também." Sem neve.
- *Capítulos tocados:* 31 (Epílogo).

**4. Cap. 24 — Ithren no calor.** Por instrução do guia, **nenhuma técnica foi acrescentada**. O
texto continua com Ithren atravessando a abóbada sem proteção visível e "o calor não parecia
tocá-lo". Registrado como pendência para o autor (§4, item 1). *Capítulos tocados:* nenhum.

*Ajuste de redação adicional, fora da lista e sem mudança de fato* (nota 28): "Brannoc Ister não
voltou para Hvel" → "não desceu a Hvel" — Brannoc nunca esteve em Hvel; a frase só fazia sentido
como "não desceu com os outros para a aldeia".

---

## §3 Correções mecânicas aplicadas nesta etapa (classe A)

10 edições, 8 capítulos (03, 05, 10, 12, 13, 18, 19, 20). Todas já estavam no V1 original (não
foram introduzidas pela revisão de linguagem). Cada capítulo foi conferido com
`compara_capitulo.py` depois da edição: título, quebras de cena e trechos entre aspas idênticos.
As pendências correspondentes foram marcadas "(corrigida — ver REGISTRO §3)" nas notas.

| Cap. | Trecho antes | Trecho depois | Motivo |
|---|---|---|---|
| 03 | "…que tinha chegado pela porta de Vhalessa **uma hora antes** e que ninguém tinha lido." | "…**pouco antes**…" | A folha da agência noticia a detenção de Ilan, que acontece às 21h10 (cap. 4: "Vieram buscá-lo às nove e dez da noite"), e é lida logo depois do ofício das 21h30. "Uma hora antes" (≈ 20h30) seria anterior ao fato noticiado. As 21h10 são fato fixado (matriz); só a referência relativa podia mudar. (P03-1 = P04-1) |
| 05 | "**Hoje de manhã** pedi a um homem que vende bolinhos de grão-de-bico que não se ajoelhasse." | "**Ontem à noite** pedi…" | O episódio dos bolinhos é na noite do Dia 0 (cap. 3: "hoje é a noite do solstício"). Aurelia passou essa noite num banco do saguão da estação de Vhalessa e às 6h do Dia 1 estava no São Brúlio (cap. 5). A frase seguinte, "Ontem pedi a um mestre de guilda", continua verdadeira e não foi tocada. (P05-1) |
| 10 | "…a que o doutor Orsk tinha aberto para o Carrasco **duas noites antes**, e olhou." | "…**quatro noites antes**…" | O serviço do Sete Chaminés é na noite do Dia −1 (cap. 1, por volta das 22h30); a cena é às 7h do Dia 3 (noites −1, 0, 1 e 2). Ilan não voltou ao sótão nesse intervalo (cap. 9: o favo continua lá e "ninguém mandou buscar"). (P10-1) |
| 10 | "— Ele disse **ontem**, na tenda — falou a Soberania —, que Calvenor lutou até o fim." | "— Ele disse **anteontem**, na tenda —…" | A fala de Oriel ("Ele lutou até o fim") é do cap. 6 (Dia 1). No mesmo capítulo, "ontem, na oficina da senhora Voss" fixa o Dia 2 (cap. 9), em que não há visita à tenda (cap. 9: "Na noite anterior, da tenda até a escadaria"). (P10-2) |
| 12 | "…porque um homem que eu derrotei **há quatro dias** anda contando a história…" | "…**há cinco dias**…" | O barbudo foi derrotado na noite do Dia −1 (cap. 1); a fala é na noite do Dia 4 (continuação das 19h do cap. 11; o cap. 11 fixa o Dia 4: "Ontem à noite, jogando Muralhas" = cap. 10). (P12-1) |
| 13 | "— **Anteontem**, no alto da torre, alguém pôs no piso uma trilha de âncoras…" | "— **Há três dias**, no alto da torre…" | A armadilha da plataforma é do cap. 8 (Dia 2); o cap. 13 é o Dia 5 (no próprio capítulo, "ontem à tarde" = canal e São Brúlio, Dia 4). (P13-1, fala de Ilan) |
| 13 | "Eu andei mil cento e quarenta degraus atrás de uma armadilha **anteontem**." | "…atrás de uma armadilha **há três dias**." | Idem. (P13-1, fala de Aurelia) |
| 18 | "Ilan a tinha tocado **quatro dias antes**, subindo a escada…" | "…**seis dias antes**…" | A única subida de Ilan pela escada de serviço é a do cap. 8 (Dia 2); "escada de serviço" só aparece nos caps. 4, 8, 18, 21 e 23. O cap. 18 é o Dia 8 (o "dois dias antes" do Mercado do Sal, Dia 6, confirma). (P18-1) |
| 19 | "…tinha passado a **tarde** inteira segurando a porta de Neska aberta para o cobre." | "…a **manhã** inteira…" | O próprio cap. 19 fixa o horário: o cobre passou das 9h ao meio-dia ("Aurelia passou a manhã inteira de pé junto ao arco de Neska… Ao meio-dia, Ingeborg mandou dizer… que Neska não tinha mais cobre"); à tarde ela estava na oficina, e às 16h na Cozinha. (P19-1) |
| 20 | "…onde tinha guardado, **doze dias antes**, um fragmento de cerâmica com uma balança torta." | "…**onze dias antes**…" | O fragmento foi recolhido no Dia −1 (cap. 1); a cena é no Dia 10. A parte da pendência sobre o bolso foi mantida (§6). (P20-1) |

---

## §4 Pendências para decisão do autor (classe B)

Nada desta seção foi alterado no texto. Id: `Pnn-k` = nota do capítulo nn, pendência k;
`N1–N3` = itens novos achados na conferência do §5. Ordem por relevância: **alta** (clímax,
regra de magia, pista ou dedução, objeto que o leitor acompanha), **média** (blocagem, objeto ou
pessoa no lugar errado, números de fundo), **baixa** (referência relativa com mais de uma forma
possível, imprecisão provavelmente deliberada). Quando a nota sugere manter, a recomendação vem
explícita.

| # | Id | Cap(s). | Problema | Proposta de solução | Impacto |
|---|---|---|---|---|---|
| 1 | P24-1 (guia §10.4) | 24 (e vols. seguintes) | Ithren atravessa a abóbada a ~108 °C (a antecâmara já passa de 40 °C) sem manto nem lã molhada, e "o calor não parecia tocá-lo". Não há fonte nem custo visíveis: pode ser lido como imunidade sem técnica. | Decidir se haverá explicação canônica (com fonte e custo) mais adiante. Até lá, o "não parecia" segura a leitura como aparência. Não acrescentar técnica no V1 sem essa decisão. | Alta. Cânone da magia; o antagonista volta no epílogo. |
| 2 | P24-4 + P25-1 (+P26-4) | 24, 25, 26 | Cronologia do clímax. A 7ª marca é às 5h14 ("faltava uma hora e cinco minutos" para as 6h20); depois disso Ilan ouve pelo anel "Estamos chegando à válvula", que no cap. 24 acontece antes das 5h10 (e lá Aurelia diz "Ilan está no nível de serviço"); no pátio, Eron diz "Faltam quarenta minutos" (≈ 5h40) com a pele ainda de pé, mas a pele cai às 5h32; no 26, "o amanhecer estava a trinta minutos" (≈ 5h50) já depois da pele e do fiel. | Proposta da nota 25: 7ª marca às 4h54 ("Faltava uma hora e vinte e cinco minutos") e Eron "Faltam cinquenta minutos" (≈ 5h30), mantendo 5h32 (24) e "trinta minutos" (26). Se preciso, no 24, "Ilan está quase pronto" em vez de "Ilan está no nível de serviço". | Alta. Sincronia das duas frentes do clímax. |
| 3 | P24-5 (= P25-2) | 24, 25 | Halsey em dois lugares: por volta das 4h está na Estação das Portas de Vhalessa com os homens dos Reinos ("Vocês vão voltar") e continua lá depois da passagem; às 4h10 desce às Cisternas com a Comissária, socorre o guarda queimado e joga água em Nara. | No 25, trocar Halsey por outro oficial da Câmara (p. ex. um sargento), ou mostrá-la saindo da estação para a Casa da Fornalha. | Alta. Personagem com nome em duas cenas simultâneas. |
| 4 | P26-2 (= P25-3) | 25, 26 | Orientação da manobra 3ª/9ª. Ilan entra na 3ª "para o norte" e sai da 9ª "para o leste, para o meio do saguão, para o espaço entre a terceira e a nona". Com as portas na parede norte e a contagem "a contar da esquerda" (cap. 25) feita por quem olha a parede, a 9ª fica a leste da 3ª, e seguir para leste a partir dela o afasta do meio. Além disso, a 9ª está "virada para a terceira", embora as duas estejam na mesma parede. | No 25, "a terceira, contando da ponta leste"; no 26, trocar "virada para a terceira" por "na mesma parede". Ou tirar o ponto cardeal ("de volta para o meio do saguão"). | Alta. Geometria do lance central (Vetor Passante), preparado no treino do cap. 19. |
| 5 | P26-3 | 26 | "A dez metros da terceira porta e a quarenta da nona", com as duas a 30 m uma da outra na mesma parede: só é possível com Ilan alinhado à parede, além da 3ª, mas ele vem recuando do vestíbulo da fachada. | "a uns trinta e poucos metros da nona". | Alta. Mesmo lance. |
| 6 | P12-2 | 12 | Fio de prata até o pilar: Ilan solta a ponta do carretel e "acoplou a ponta ao pilar da ponte", a 15 m, sem que o texto mostre como a ponta física chega à pedra. Pode ser lido como âncora à distância sem elo (regra dura do guia §4). | O autor decide meia frase que mostre a ponta chegando ao pilar (p. ex. lançada junto com a marca efêmera). | Alta. Regra de magia (elo visível). |
| 7 | P18-3 | 18 | O intervalo de "um pouco mais de um segundo" entre as ondas da crista não comporta o que acontece entre a 2ª e a 3ª (Ilan grita a Nara, ela corre dezenas de metros contornando a escadaria, crava o Pivô e o prende ao tronco), nem a cena paralela na estação (homens dos Reinos levando gente da praça até a estação entre o virote e o raio). | Tornar o intervalo de vários segundos ("um pouco mais de dez segundos" / "Dez segundos e um pouco"), ou dizer que, depois das duas primeiras ondas, a dragoa segura a carga um tempo antes da terceira. | Alta. Plausibilidade do grande lance do meio do livro. |
| 8 | P24-2 | 24 | Mara: "Tudo o que conduz alguma coisa esquenta. Primeira lei." O princípio é o da Dissipação (lei 5, bíblia interna). No cap. 5, "Primeira lei" está correta (Conservação: o calor tem de ir para algum lugar). | "Quinta lei." (ou "Dissipação."), salvo se a intenção for a contabilidade da Conservação. | Alta. Cânone das sete leis, na boca da personagem mais precisa do livro. |
| 9 | N2 (novo) | 30 (cf. 15, 18, 19) | Nara, sobre a célula cinza-escura: "Você passou um raio de dragão por ela. E um empurrão de um deus. E uma descarga de Retorno. E ela está inteira." Mas essa célula só foi feita e encaixada no Dia 9 (cap. 19), depois do empurrão de Thor (Dia 6, cap. 15, sofrido pela 2ª provisória de porcelana) e do raio da dragoa (Dia 8, cap. 18, que estourou a célula 1 antiga). Já está assim no V1 ("Você conduziu um raio de dragão por ela"). | Fazer a lista se referir à manopla e não à célula (p. ex. "Você passou um raio de dragão por essa manopla. E um empurrão de um deus. E a minha ainda está inteira, depois de uma descarga de Retorno"), ou reduzi-la ao que a célula viveu (o Fechamento e o Retorno do Dia 13). Decisão de fala. | Alta. Objeto que o leitor acompanha (§5.4), numa cena emocional. |
| 10 | P17-1 | 17 | Visão pelo anel antes de Aurelia vesti-lo: ela despeja os dois anéis na palma, ergue um, e Ilan vê pelo furo "um pedaço de teto branco, de pedra, iluminado por uma lamparina"; logo depois ela diz que o outro lado "era o meu quarto, no Átrio. Eu o trouxe comigo". Com o anel par na palma dela, no telhado, a imagem do teto não tem de onde vir. | Trocar a imagem por algo visível a partir do anel par na palma (p. ex. "um pedaço de céu visto de outro ângulo e a borda do casaco dela"). O resto da cena já está coerente. | Alta. Regra do par de soleiras (as extremidades estão nos dois anéis). |
| 11 | P19-2 | 19 (cf. 12) | Prazo de Eron: "no mínimo dez dias" contados do canal (noite do Dia 4) dão o Dia 14; Ilan diz que "dez dias depois do canal é daqui a quatro dias" (Dia 13, o da operação). | "Dez dias depois do canal cobre o dia em que vamos estar no Passo Cinzento" (sem fixar a data). | Alta. Dedução de Ilan sobre quem contratou Eron (pista). |
| 12 | P24-6 (+P26-4) | 24, 26 | Fim do 24: "Sevran tinha dado o último passo e estava de pé ao lado do amigo"; o 26 abre com Oriel mandando-o parar e Sevran dando mais passos ("deu um passo… outro… o último passo"). | No 24: "Sevran tinha dado mais alguns passos e estava a pouca distância do amigo ajoelhado". | Média. Blocagem na virada de capítulo. |
| 13 | P24-3 | 24 | Geometria da abóbada: arco no centro de uma abóbada de ~60 m; círculo de discos a ~10 m do arco (≈ 20 m da entrada, coerente com "a vinte metros"), mas o disco mais perto fica "a uns quatro metros da entrada"; na travessia, Sevran está "no meio da abóbada" e "a quarenta metros" de Mara (o raio é de ≈ 30 m). | "a uns quinze metros da entrada" e "a uns vinte metros dela", ou descrever o círculo como irregular e alongado. | Média. Blocagem. |
| 14 | P19-3 | 19 | Primeiro arremesso do Contrapasso: Ilan para "diante da porta doze, de costas, a um metro do arco", e a bola, lançada "na direção das costas" dele, "entra na porta doze um metro antes das costas". As portas da estação são nichos com parede de fundo (caps. 19 e 26), então não fica claro como a doze fica entre Tibo e Ilan. | Uma oração que situe Ilan de costas para o meio do saguão, com a doze entre ele e Tibo; ou indicar que as portas do saguão de Vhalessa são arcos isolados. | Média. Preparação do Contrapasso, pago no cap. 26. |
| 15 | P18-2 | 18 | "A mulher com o bebê" está ao lado de Ilan, sob o leão, durante a 3ª onda e, depois da descarga, sentada nas lajes olhando para ele; na cena de Aurelia, "a mulher com o bebê" é a primeira pessoa a entrar na estação (a ~400 m) antes do raio. | Na cena da estação, "uma mulher com um bebê" (outra pessoa). | Média. Identidade de figurante em duas cenas simultâneas. |
| 16 | N1 (novo) | 19, 24, 27 | Cisternas depois do fechamento: projeção de 111 °C para o Dia 13 (cap. 19); sal da abóbada externa norte a 108 °C pela sonda (cap. 24, ~4h30); dreno acelerado para 12–15 °C/dia desde a 1h. Mesmo assim, "dois dias depois" a Politécnica mede 118 °C, "caindo agora só o décimo de grau por dia" (cap. 27): uma subida de ~7 a 10 °C sem fonte narrada (o Retorno foi para o cano, o Cobre, os abrigos e os troncos da torre). Já está assim no V1. | (a) Aceitar como reequilíbrio entre abóbadas (a Politécnica mede outra abóbada e outra profundidade, e Nara já corrige leituras "de profundidade e de abóbada" no cap. 13), com meia frase opcional no 27; ou (b) trocar 118 por um valor ≤ 110 ("cento e oito", "cento e dez"). Número técnico: não mudar sem o autor. | Média. Número técnico com efeito emocional ("a maior parte tinha ficado nas Cisternas"). |
| 17 | P11-1 | 11 (cf. 13) | Último parágrafo: Mara guarda a recusa "ao lado do disco do Consórcio", mas às 19h o disco já está com a Comissária (ela o examina no saguão; no 13, "A Comissária está com ele", e Halsey o entrega a Aurelia). | "ao lado da placa de vidro trincada" (que o capítulo põe na maleta). | Média. Objeto-pista no lugar errado. |
| 18 | P11-3 | 11 | "Chegaram lá às quatro e meia — as três, a tenente Halsey e os dois guardas": "as três" sugere que Liesl Kaltz foi ao armazém, mas ela não é mencionada lá. | Decidir se Liesl vai (e citá-la uma vez) ou trocar por "as duas". | Média. Quem estava presente numa cena de descoberta. |
| 19 | P16-1 | 16 (cf. 14) | "O espaço vazio na mesa onde a moldura de madeira tinha estado durante trinta anos": a miniatura mostra Lys aos dezesseis, ela morreu em março de 1178, e em 1178 Brannoc era regente em Tollsund. O retrato não pode estar naquela mesa de Vhalessa há trinta anos ("trinta anos" é o tempo de serviço de Brannoc). | "durante anos" ou "desde que ele chegara a Vhalessa". | Média. Detalhe ligado ao motivo do antagonista. |
| 20 | P21-1 | 1, 21 | Brasas de parede: "uma das centenas de milhares" (cap. 1) × "as quarenta e tantas mil brasas de parede" (inventário do Plano, cap. 21). | O autor fixa o número. Para 600 mil habitantes, "centenas de milhares" parece o mais coerente (trocar no 21); ou o cap. 1 passa a "dezenas de milhares". | Média. Número de mundo. |
| 21 | P09-1 | 9 (cf. 2, 11) | Cronologia de Hanne: marido morto "faz quinze anos" (≈ 1172), Nara descobre "dez anos depois" (≈ 1182), e "uma semana depois" a companhia registra o favo; mas a patente é 1181-07 (cap. 11) e o favo foi desenhado "faz seis anos" (≈ 1181, cap. 2). Diferença de cerca de um ano. | "faz dezesseis anos" ou "nove anos depois"; ou aceitar como aproximação na fala de Hanne. | Média. Datas de fundo. |
| 22 | P14-1 | 14 (cf. 16) | Brannoc diz que o Consórcio instalou as válvulas dos prédios da rua de trás "no ano passado"; no 16, os registros das válvulas 1–3 são "da primavera de 1187" ("como Brannoc tinha dito"). | Se não for imprecisão deliberada de Brannoc (ele está encobrindo a válvula 4), "na primavera". | Média. Fala de antagonista; pode ser deliberada. |
| 23 | P07-2 | 7 (cf. 3, 5) | Aurelia: "A senhora mesma disse ao Conselho que é para isso que existem inquéritos." Cassia disse isso a Aurelia no saguão da estação (cap. 3) e não o repete no Conselho (cap. 5). | "A senhora mesma me disse, na estação, que é para isso que existem inquéritos." Ou manter como retórica de Aurelia. | Média. Atribuição de fala. |
| 24 | P15-1 | 15 | Ilan sobre Thor: "Conheço a reputação. Nunca o vi. […] Ele não estava lá. Estava em outro vale." Depois Thor conta que carregou as âncoras de dissipação, deu as luvas ao menino e o viu no dia seguinte, e Ilan reconhece as luvas. | **Recomendação: manter.** Leitura coerente: Ilan nunca soube que o gigante das luvas era Thor. Se não for intencional: "Nunca soube que era ele", ou dar a Ilan, no jantar, um gesto que mostre que ali ele liga uma coisa à outra. | Média. Beat emocional (as luvas). |
| 25 | P21-2 | 21 (cf. 18) | "— A Velha das Cristas — disse Aurelia, devagar. — Ontem. No gelo." A cena é por volta da 1h do Dia 11; o tratado no gelo foi no Dia 8. | "Anteontem. No gelo." (para quem não dormiu, a madrugada ainda é o Dia 10) ou "Três dias atrás. No gelo." Duas formas corretas conforme a convenção, por isso não entrou em A. | Baixa. |
| 26 | P23-2 | 23 (cf. 20) | Sevran a Oriel, por volta de 0h20 do Dia 13: "Ontem eu entreguei" (a carta de Calvenor foi entregue no Dia 10). | "Anteontem eu entreguei" (noite contada como Dia 12) ou "Faz três dias, eu entreguei." Mesma razão do item 25. | Baixa. |
| 27 | P23-1 | 23 (cf. 21) | "A Comissária tinha dito no gabinete, na véspera": a reunião da vigilância é na manhã do Dia 11 (cap. 21); a cena é às 0h10 do Dia 13. | **Correto** se a madrugada conta como Dia 12 (véspera = Dia 11). Manter, ou "dois dias antes" se o autor preferir a conta pelo calendário. | Baixa. |
| 28 | P23-3 | 23, 24 | Hora em que Oriel desce às galerias: Sevran estima "meia-noite e cinquenta, mais ou menos" (e Mara calcula "uma hora e quinze" até as 2h05); no 24, um guarda informa "Desceu às uma e cinco". | **Recomendação: manter** (estimativa de Sevran, trancado e levando 40 min para sair). Se quiser harmonizar: "por volta da uma" no 24, ou "Meia-noite e cinquenta. Uma hora. Mais ou menos." no 23. | Baixa. |
| 29 | P11-2 | 11 (cf. 7) | Mara conhece o desenho da chave "de uma conversa no saguão gelado de uma estação, dois dias antes" (Dia 4). A única cena assim com Mara presente é a do Dia 1 (cap. 7), o que daria três dias; mas não dá para excluir uma conversa fora de cena na manhã do Dia 2. | "três dias antes" ou "na primeira noite". | Baixa. |
| 30 | P13-2 | 13 | Mara, no Dia 5: "Eu li os manômetros ontem." No Dia 4 ela esteve na Kaltz de manhã até as 16h30, depois no armazém, e às 19h na delegação. A visita à galeria só caberia de madrugada ou à noite. | Manter (há brechas), ou "anteontem"/"no outro dia". Verificação inconclusiva. | Baixa. |
| 31 | P08-1 | 8 (cf. 7) | "Tinha prometido a Aurelia, na véspera, numa escadaria, que a poria na conta": o "Agora a senhora está na conta" é dito sob a lanterna de uma barraca fechada, na volta pela Feira do Gelo, antes da escadaria da praça. | "na véspera, na volta pela Feira do Gelo", ou só "na véspera". Ou manter como memória comprimida de Ilan. | Baixa. |
| 32 | P07-1 | 7 | Física do arco: o ar quente do Delta "queria subir e sair pelo alto do arco", e o frio de Vhalessa, "escorrer pela base"; logo depois, "pela base do arco, a primeira lufada" é um sopro morno do Delta que entra no saguão. | "E então, pelo alto do arco, a primeira lufada." | Baixa. Detalhe físico. |
| 33 | P10-3 | 10 (cf. 1) | "à terceira carta, a que ele tinha escrito à própria seguradora": no cap. 1 Sevran escreveu três vezes ao Conselho e duas à Casa antes da Arrimo. "Terceira" só fecha se lida como terceiro destinatário. | "à última carta" ou "à carta seguinte"; ou manter (terceiro destinatário). | Baixa. |
| 34 | P03-2 | 3 (cf. 4) | Cassia, à noite: "O suspeito está sendo interrogado." No cap. 4 Ilan passa a noite na cela e só é interrogado às 8h. | **Recomendação: manter** (evasiva de Cassia para adiar a visita da Soberania). Se o autor quiser coerência literal: "O suspeito está detido e será interrogado pela manhã." | Baixa. Fala de personagem. |
| 35 | P24-7 | 24 (cf. 25) | Pelo anel, Mara ouve "um lugar grande e frio", mas a estação do Passo Cinzento está quente e úmida. | **Recomendação: manter** (impressão de Mara); se incomodar, "um lugar grande e alto". | Baixa. |
| 36 | N3 (novo) | 17, 19 | A 3ª provisória de porcelana, "branca e lisa" quando é posta no Dia 7 (cap. 17), aparece "rendada de rachaduras" no Dia 9 (cap. 19), sem causa narrada: no cap. 18 o resíduo vai para a célula 1, que estoura. Já está assim no V1. | **Recomendação: manter** (leitura possível: o lance do cap. 18 castigou a manopla inteira). Alternativa: meia frase no 18, ou "a de porcelana de Hanne, ainda inteira" no 19. | Baixa. |
| 37 | P04-2 | 4 | "Na segunda noite desses três dias o deus da cidade morre": contando a partir da conclusão do serviço (noite do Dia −1), a Vigília é a segunda noite se a própria noite do serviço conta como a primeira. | **Recomendação: manter** (ver §6). Se o autor quiser precisão: "na noite seguinte ao serviço". | Baixa. |

---

## §5 Fatos de continuidade conferidos que continuam válidos

Conferidos nos textos revisados, já com as correções do §3.

### 5.1 Calendário (ancorado nos marcadores do próprio texto)

| Dia | Capítulos | Âncora textual usada |
|---|---|---|
| −1 (véspera da Vigília) | 1 | serviço no Sete Chaminés à noite; "às dez e meia da noite, véspera de feriado" |
| 0 (Vigília, solstício) | 2, 3; início do 4 | sinos às 19h; Ilan detido às 21h10; ofício da Câmara às 21h30 |
| 1 | 4 (manhã), 5, 6, 7 | sino dos mortos desde as 6h; custódia às 14h; Anúbis à noite, volta "depois da uma da manhã" |
| 2 | 8, 9 | cap. 9: "Na noite anterior, da tenda até a escadaria" |
| 3 | 10 | "ontem, na oficina da senhora Voss" (= cap. 9) |
| 4 | 11, 12 | cap. 11: "Ontem à noite, jogando Muralhas" (= cap. 10); 19h na delegação → canal à noite |
| 5 | 13, 14 | cap. 13: "ontem à tarde… o senhor Varek estava no Hospital de São Brúlio" (= cap. 12) |
| 6 | 15 | Thor chega; Mercado do Sal |
| 7 | 16, 17 | Brannoc parte às 5h; anéis à noite |
| 8 | 18 | "o formigamento do Mercado do Sal, dois dias antes"; Cisternas a 141 °C às 7h |
| 9 | 19 | "Ontem, na praça, quando você cortou o raio do leão" |
| 10 | 20; 21 até a meia-noite | Dorn acorda; carta de Calvenor |
| 11 | 21 (0h30–2h30 e manhã) | cilindro aberto "à meia-noite e meia"; Cisternas a 123 °C |
| 12 | 22 | operação marcada para o meio-dia do Dia 13 |
| 13 | 23 (0h10–2h05), 24 (~3h–5h32), 25–27 (~4h–6h20) | horários explícitos |
| depois | 28–30, Epílogo | 2 semanas (29); abril (30) |

As correções do §3 seguem este calendário; as referências relativas restantes que dependem da
virada da meia-noite ficaram em B (§4, itens 25–27).

### 5.2 Temperaturas das Cisternas (tubo da Politécnica, abóbada externa, salvo indicação)

| Momento | Valor | Fonte |
|---|---|---|
| Normal (aula de Nara, fev. 1179) | 184 °C ("entre cento e oitenta e cento e noventa"); novembro: "duzentos e poucos" | cap. 13 |
| Dia 5, 10h | 161 °C; Mercado do Sal 158; Praça (pata do leão) 155; "corrigidos, os três dizem a mesma coisa"; estimativa 159,5 à tarde | cap. 13 |
| Dia 5, 17h40 | 159 °C; queda ≈ 6 °C/dia; limite útil ~90 °C → "onze dias. Talvez doze" | cap. 13 |
| Dia 8, 7h | 141 °C; "Seis graus por dia, certinho"; 90 °C em "oito dias, nove no máximo" | cap. 18 |
| Dia 9 (projeção) | 111 °C no Dia 13 ("Daqui a quatro dias") | cap. 19 |
| Dia 11, manhã | 123 °C (curva na parede do gabinete, linha até *90°*) | cap. 21 |
| Dia 13, a partir da 1h | válvula aberta; dreno de "Doze. Talvez quinze" por dia | cap. 24 |
| Dia 13, ~4h–5h | antecâmara > 40 °C; paredes da abóbada externa norte "cento e poucos graus"; sonda no sal e no disco: 108; jorro de ar a 200 °C; pele cai às 5h32 | cap. 24 |
| Dia 15 | 118 °C, caindo 0,1 °C/dia | cap. 27 (ver N1) |

Coerência interna: 161 (D5) → 141 (D8) ≈ 6,7 °C/dia; 141 (D8) → 123 (D11) = 6 °C/dia; 123 (D11)
→ 111 (D13) = 6 °C/dia. Única tensão: o valor pós-fechamento (N1).

### 5.3 Contagem de mortos (sino da Alta Mesa)

- Manhã do Dia 1: **9** ("Está tocando desde as seis da manhã… Até agora, foram nove", cap. 4;
  inclui as duas irmãs de três e cinco anos e os quatro velhos da Fornalha Velha).
- Dia 2, à noite: **23** desde a manhã do Dia 1 ("eram vinte e três desde a manhã de ontem", cap. 9,
  citando a Comissária).
- Total contado por Oriel: **208** (cap. 23: "Duzentos e oito, Sev"; cap. 24: Mara a Ithren,
  "Duzentas e oito pessoas"; cap. 26: Sevran; cap. 30: "duzentas e oito pessoas morreram").
- Descarga da dragoa (cap. 18): sem mortos ("Ninguém na praça tinha morrido."); toca o sino de fim
  de perigo, que não tocava "havia cento e doze anos".
- Fora da contagem da cidade: Marenna, 40.312 mortos até maio de 1178 (cap. 17), "quarenta mil"
  nas falas (16, 17).

### 5.4 Células da manopla, capítulo a capítulo

| Momento | Célula 1 | Célula 2 | Célula 3 |
|---|---|---|---|
| Cap. 1 (D−1) | antiga | antiga | antiga; racha de ponta a ponta no 19º regulador; as três esvaziadas de uma vez na caixa-d'água |
| Cap. 2 (D0) | antiga | antiga | **provisória nº 1**: porcelana condutora da Cooperativa, branca, "como um dente postiço", 2/3 da carga das antigas; 20 dobras |
| Cap. 4 (D0, noite) | — | — | "provisória, recém-calibrada"; manopla entregue a Halsey |
| Cap. 8 (D2) | as três enchem na armadilha | | nº 1 inteira, fosca, com rede de rachaduras capilares ("uma célula de vinte dobras durou dois dias") |
| Cap. 15 (D6) | antiga | antiga | **provisória nº 2**, posta naquela manhã ("a última porcelana da minha mãe"); satura no empurrão de Thor; fica com rede de trincas, inteira |
| Cap. 17 (D7) | antiga | antiga | Nara troca pela **provisória nº 3**, "branca e lisa": "Esta é a última. Eu já disse isso da outra, mas desta vez é verdade"; a próxima seria do favo |
| Cap. 18 (D8) | **a mais antiga ("a de seis anos") recebe o resíduo do tentáculo e estoura**; queimadura de 2º grau no dorso da mão esquerda | antiga | nº 3, "a última porcelana de Hanne Voss" |
| Cap. 19 (D9) | **nova**: hexagonal, cinza-escura, irregular, feita por Nara com a cerâmica das 2 células mortas do favo de Orsk, mais caulim e pó de ferro; calibrada durante uma hora | "a segunda, a última das antigas" | "a de porcelana de Hanne, rendada de rachaduras" (ver N3) |
| Caps. 25–26 (D13) | cinza-escura | velha | porcelana de Hanne; manopla acoplada às sete marcas do Fechamento; nenhuma descarga ou esvaziamento narrado |
| Cap. 27 (D13) | "Todas vivas. Todas vazias, porque ele já tinha gastado o que tinha" | | o clarão vem do globo de Clarão (§2, item 2) |
| Cap. 30 | cinza-escura: "Trincada… Mas inteira" ("Traz ela de volta… Quando trincar de vez") | velha | "a de porcelana da mãe dela" |

Retificação de registro: a nota 26 diz que a célula 3 dos caps. 25–30 é "a provisória de porcelana
de Hanne, rendada de trincas desde o cap. 15". Pelo texto, é a **nº 3**, posta no cap. 17; a do cap.
15 (nº 2) foi trocada. Isso não muda nada no manuscrito. Ver também N2 (cap. 30) e N3.

### 5.5 Idades e datas

- **Ilan:** nascido em Ardósia em 1153, entregue à Ordem aos nove (cap. 4); 19 anos em Hrímvald,
  1172 (cap. 15); 22 no outono de 1175 (caps. 4 e 17); 34 anos (caps. 1, 22 e 29). Coerente com o
  ano corrente de 1187.
- **Aurelia:** 1.187 anos (caps. 3, 16, 17 e 29). Construiu o arco de Vhalessa no ano 708 (cap. 3),
  mandou fazer a estação do Passo Cinzento em 1098 (cap. 25); a mina fechou em 1147 e a porta 61
  está adormecida há quarenta anos (caps. 14 e 25). Coerente.
- **Brannoc:** 61 anos, trinta de serviço (cap. 5); Lys, 16 anos, morta em março de 1178:
  "nove anos" (caps. 5 e 16). Coerente.
- **Sevran:** entrou na Casa aos 23, em 1158; acorda às 4h30 há 29 anos; 26 anos na Casa, saiu há
  três, em 1184 (cap. 10). **Oriel:** noviço no mesmo ano, com 19 anos (cap. 26), ou seja, ~48 em 1187
  ("uns cinquenta", cap. 6). Coerente.
- **Mara:** 29 anos em fevereiro de 1178, em Marenna (cap. 16).
- **Nara:** 14 anos quando o pai morreu, "faz quinze anos"; favo desenhado "faz seis anos"; ver
  P09-1 (diferença de ~1 ano com a patente 1181-07).
- **Documentos:** encomenda 1187-44 em 14 de setembro → disco do Consórcio gravado 87-09-22, "oito
  dias depois da encomenda" (cap. 11) → válvula 4 registrada em 22 de setembro de 1187 (cap. 16);
  renovação da delegação em 9 de setembro de 1187 (caps. 14 e 16); carta à Arrimo recebida em 29 de
  outubro de 1187 (cap. 20). Coerente.
- **Calvenor:** acende o Sol "havia quase trezentos anos" (cap. 1); as brasas da Casa "em quase três
  séculos" nunca conheceram o inverno (cap. 8). Coerente.

### 5.6 Anel par de soleiras

- Cap. 17: dois anéis de bronze escuro feitos "há trezentos anos" para falar com Ione, que nunca
  usou o dela. Cada anel é uma extremidade, "ancoradas uma na outra, e em mim"; a passagem tem o
  tamanho do furo, dois dedos (ar, som de perto, um papel dobrado pequeno). Aurelia pode fechar do
  lado dela. Ilan o usa no **dedo médio da mão direita**, folgado (em Ardósia, o médio da esquerda
  quer dizer dívida não paga). Aurelia usa o par no **dedo médio da mão esquerda, por baixo da luva**.
- Caps. 19, 21 e 22: comando "agora" pelo anel no treino ("O som leva tempo para atravessar o
  anel"); conversas de Ilan com Aurelia. Mão do anel sempre a direita.
- Cap. 24: Ilan dá o anel a Mara, que o põe no **dedo médio da mão esquerda**, folgado ("No Delta,
  anel é só anel"). Caps. 24–26: Mara ↔ Aurelia pelo anel; no Passo Cinzento, Aurelia fala com Ilan
  "pela pedra", sem anel (cap. 26). Coerente. Pendência ligada: P17-1 (imagem vista antes de o par
  ser vestido).

### 5.7 Outros números-âncora conferidos

112 dobras (caps. 1, 5 e 30); 60 dobras do contrato Arrimo; Tarvel "onde não neva nunca" (caps. 1,
30 e 31); Torre do Meio-Dia com 220 m e 1.140 degraus na escada de serviço (caps. 1, 8 e 13);
Passo Cinzento a 140 km (várias menções); estação do Passo com onze portas, a 61 = "a terceira, a
contar da esquerda", a 7ª = antiga porta de carga (cap. 25); Átrio com 341 portas, mais "duas mil e
tantas" pelas estações de Aresta (caps. 3 e 30); 6.140 pessoas evacuadas para o Átrio (caps. 18 e
19).

---

## §6 Itens observados e mantidos de propósito

**Imprecisões que são fala ou percepção de personagem (texto mantido):**
- Cap. 2 (nota 02, sem número): Nara diz que o último forno de cerâmica de lastro fechou "faz uns
  dez anos"; a Casa do Fiel caiu há doze. Aproximação dela.
- Cap. 4 (P04-2): "na segunda noite desses três dias": a noite do serviço conta como a primeira.
- Cap. 3 (P03-2), Cassia, "O suspeito está sendo interrogado": evasiva para adiar a visita.
- Cap. 14 (ligado a P16-1), Brannoc, "Em trinta anos, isso aconteceu duas vezes. Uma foi quando a
  minha mulher teve a menina": funciona se "o meu escritório" for o escritório de regente onde ele
  estivesse.
- Cap. 14 (P14-1), Brannoc, "no ano passado": pode ser imprecisão de quem está encobrindo a válvula 4.
- Cap. 15 (P15-1), Ilan, "Nunca o vi": ele não sabia que o gigante das luvas era Thor. O eco "Estava
  em outro vale" (Ilan) / "Estava no outro vale, com as âncoras de dissipação" (Thor) é deliberado.
- Cap. 20 (P20-1, parte 2), "o bolso de dentro, junto ao peito" × "bolso do colete" (cap. 1): sem
  conflito. O colete de couro tem "bolsos demais" (cap. 1), e no mesmo parágrafo Ilan tira a carta
  "do bolso do colete" e a guarda "de volta no bolso de dentro" (é o mesmo bolso). Que Cassia tenha
  ficado com o fragmento desde o cap. 5 também não conflita: a frase diz só onde ele o tinha guardado
  onze dias antes.
- Cap. 22 (nota 22, sem número): a frase de Mara em itálico na lembrança de Aurelia não é idêntica à
  fala do cap. 21; é lembrança, mantida literal.
- Cap. 23 (P23-1, P23-3): "na véspera" (correto na convenção de quem não dormiu) e "meia-noite e
  cinquenta, mais ou menos" (estimativa de Sevran).
- Cap. 24 (P24-7): "um lugar grande e frio", impressão de Mara pelo anel.
- Cap. 10, "O Carrasco me deve uma partida desde ontem" (Mara, Dia 3): o lembrete foi dado depois da
  uma da manhã do Dia 2 (cap. 7). Coerente, nada a fazer.
- Cap. 17, "Esta é a última. Eu já disse isso da outra, mas desta vez é verdade": a "última
  porcelana" dita duas vezes (caps. 15 e 17) é deliberada, e o próprio texto a assume.
- Cap. 5 (§3), "Ontem à noite pedi… Ontem pedi a um mestre de guilda": a anáfora "Ontem… Ontem…"
  ficou como resultado da correção mínima. Um eventual polimento ("Ontem à tarde, a um mestre de
  guilda") é estilístico e não foi feito.

**Pendência encerrada sem edição:** 26-1 (células "esvaziadas no cap. 26", que o 26 não narra). O
apoio para a manopla sem carga está no próprio cap. 27 ("Todas vazias, porque ele já tinha gastado o
que tinha"), §2, item 2.

**Motivos repetidos deliberados (guia §3), preservados onde aparecem:** "Hoje, não."; "Eu leio
coisas." (Ilan no cap. 5, devolvido por Aurelia no mesmo capítulo); "Me dizem isso."; "Não precisa
agradecer." / "É por isso que agradeço." (caps. 21 e 24); "lido em voz alta"; "depois" / "depois
depois"; "Ainda não sei." (Calvenor/Ilan, cap. 20); "o preço" / "a única de vocês que ainda não
sabia o preço" (caps. 18, 21, 29); "Toda coroa é uma dívida…" (tratado de Oriel, carta de Brannoc,
Ithren); "o menino mede bem" (folha do Plano, caps. 21 e 29; "O homem que media bem" no epílogo); o
bolo de mel e a porta dos fundos aberta até a metade "para não ranger" (caps. 21, 23 e 26); o clarão
branco de um globo de Clarão quebrado (caps. 1 e 27). Textos de documento citados (contrato Arrimo,
ofício da Câmara, folha da agência, encomenda 1187-44, caderno de Dorn, carta à Arrimo, carta de
Calvenor, Plano, carta de Brannoc, tratado no gelo, nota a lápis de Pimm) permanecem literais
(conferidos nas notas por capítulo); o script confirma que os trechos entre aspas são idênticos em
31/31 capítulos. Contagem dos motivos no livro inteiro, original → revisado: "Hoje, não." 4 → 4
(a 5ª ocorrência da sequência no original, no cap. 21, é "hoje, não tem para onde", sem relação
com o motivo); "Eu leio coisas" 3 → 3; "Me dizem isso" 3 → 3; "É por isso que agradeço" 4 → 4;
"lido em voz alta" 3 → 3; "depois depois" 3 → 3; "Ainda não sei" 9 → 9; "Toda coroa é uma dívida"
9 → 9; "mede bem"/"media bem" 4/4 → 4/4; "para não ranger" 2 → 2; "ainda não sabia o preço" 3 → 3.


## 7. Decisões do autor posteriores à revisão

- **Aparência de Aurelia (out. 2026).** O autor aprovou uma nova direção visual: cabelo loiro dourado, olhos âmbar,
  diadema de raios, colar de filigrana e braceletes de ouro. No texto, a única menção que contradizia a nova direção
  era "o cabelo negro solto" (cap. 27), trocada por "o cabelo dourado solto" em `V1_revisao_linguagem/` e em
  `capitulos/`. `V1_original_preservado/` fica intacto como registro histórico. A ficha da Bíblia interna foi
  atualizada. Nenhuma outra passagem descreve cor de cabelo, olhos ou pele dela. O coque com a chave de bronze
  (cap. 3) foi mantido e incorporado à ficha visual.
