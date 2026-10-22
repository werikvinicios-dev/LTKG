import html, re
SRC = "/home/user/LTKG/manuscrito/V1_revisao_linguagem/01.md"
OUT = "/home/user/LTKG/exportacoes/amostras"
L = open(SRC, encoding="utf-8").read().split("\n")
def troca(n, inicio, novo):
    assert L[n - 1].startswith(inicio), (n, L[n - 1][:60]); L[n - 1] = novo; MUD.add(n - 1)
def sub(n, a, b):
    assert L[n - 1].count(a) == 1, (n, a); L[n - 1] = L[n - 1].replace(a, b); MUD.add(n - 1)
MUD = set()

sub(67, "Era uma brasa de parede, uma das centenas", "Era uma brasa de parede, com o selo da Casa da Fornalha gravado no centro, uma das centenas")

troca(73, "Ele abriu os olhos e soltou do colete",
"Ele abriu os olhos e soltou do colete uma lente redonda de vidro de aferição, presa por uma corrente curta, e olhou a parede através dela. Vidro nenhum mostrava calor. Aquele mostrava o caminho do calor: os vínculos viravam franjinhas coloridas, inclinadas no sentido do fluxo, e os selos, mesmo escondidos, acendiam como um risco de brasa por baixo de papel. As franjas estavam inclinadas para cima e para a esquerda, na direção da escada. E, na quina, por baixo da cal, havia um selo do tamanho de uma moeda, com a cauda virada para o mesmo lado.")

troca(113, "Quem tinha instalado aquilo",
"Quem tinha instalado aquilo não tocara nas brasas do deus. Seria burrice. As placas de bronze traziam selos coronais gravados por dentro, ligados à Coroa de Calvenor por uma rede que nenhum mortal enxergava inteira, e qualquer mexida neles faria a Casa da Fornalha notar em minutos. O instalador tinha feito outra coisa: gravara no tijolo, a dois dedos de cada placa, um selo próprio. Pequenos, do tamanho de uma moeda, de traço limpo, cobertos com cal da cor da parede. Todos com o sinal de Brasa no meio e a cauda para cima, todos amarrados num mesmo vínculo que subia pela alvenaria até o telhado. O calor saía da brasa do deus para o tijolo, como sempre. Mas, antes de se espalhar pelo quarto, o tijolo o entregava ao selo, e o selo mandava tudo para cima.")

troca(117, "Ilan se agachou junto a um dos pregos",
"Ilan se agachou junto a um deles e raspou a cal com a unha. O selo apareceu: um desenho fino e escuro, sem brilho nenhum a olho nu, gravado fundo, com a paciência de quem tinha tempo. Pela lente, as franjas do vínculo estavam apertadas e corriam para cima. Ele calculou, sem pressa, quanto calor passava por ali. Pouco, por selo. Mas eram muitos selos, e alguém tinha passado meses gravando aquilo, um quarto de cada vez.")

troca(141, "Gorm se levantou.",
"Gorm se levantou. Era meia cabeça mais alto que Ilan e tinha o dobro da largura. Segurou o bastão com as duas mãos e firmou os pés no assoalho, e Ilan viu, debaixo do calcanhar direito do rapaz, um risco azul se acender na madeira: um selo de Pulso conjurado às pressas, torto, com um traço de terra que mais parecia um rabisco. Com ele, o golpe empurraria contra o prédio inteiro, e não só contra o peso do corpo. Pulso de escola de bairro. Funcionava.")

troca(151, "Estava meio metro para o lado",
"Estava meio metro para o lado, sem ter saltado. Na quina do degrau, onde a sola esquerda tinha tocado, um selo do tamanho de uma unha acendeu e se apagou, tão rápido que ficou mais na memória do olho do que no degrau. Por um instante, o degrau virou o ponto de onde ele empurrou o próprio corpo para longe do golpe: um deslocamento curto e seco, sem impulso de pernas, como se o mundo tivesse dado o passo por ele. Por baixo da luva, no pulso esquerdo, a velha marca da balança esquentou, como sempre esquentava quando segurava um tranco. O bastão acertou o corrimão, que gemeu. Ilan já estava dentro da guarda do rapaz. Espalmou a mão esquerda, a da manopla, no peito de Gorm e sentiu o vínculo que descia do corpo dele até o selo do calcanhar: um fio esticado até a madeira, como a corda de um arco.")

troca(153, "Cortou o fio.", "Não cortou o fio. Apagou o traço de terra.")

troca(155, "Não foi difícil.",
"Não foi difícil. O selo era torto, conjurado com pressa, sem redundância nenhuma. Bastou passar o polegar da manopla por cima do risco, como quem borra uma letra ainda molhada. Sem terra, o tranco que o rapaz tinha posto no golpe não tinha para onde ir, e voltou para ele. Gorm tinha jogado todo o peso para a frente, confiando que o piso o seguraria, e de repente o piso não segurava mais. Ele perdeu o equilíbrio. Ilan deu um empurrãozinho, quase gentil, no lugar certo, e o rapaz sentou de volta no caixote com tanta força que o caixote se desmanchou debaixo dele.")

troca(183, "O barbudo assentiu",
"O barbudo assentiu, como se aquilo fosse uma informação técnica relevante. Também tinha selos nos pés, como Gorm, mas com mais capricho: dois em cada sola, gravados no couro e reavivados com um toque, e um terceiro, conjurado na parede à direita, na altura do quadril, um anel azul que ele mantinha aceso só com o canto do olho. Um apoio lateral. Ilan reparou nele, e reparou que o homem tinha parado a um palmo da parede justamente para poder usá-lo. O besteiro tinha um selo só, gravado no próprio arco da arma, que dava ao virote um empurrão extra no disparo. Selo gravado aguenta muito, mas esvazia a cada tiro e leva um instante para encher de novo.")

sub(201, "No mesmo instante, o barbudo avançou, usando a âncora da parede para ganhar um arranque lateral que o jogou direto na linha de Ilan.",
"No mesmo instante, o barbudo avançou. O anel da parede acendeu forte e o jogou de lado, direto na linha de Ilan, deixando no ar um rastro azul que se desfez atrás dele.")

troca(205, "O impacto foi brutal.",
"O impacto foi brutal. Não pela força do braço do homem, mas pelo que vinha atrás dele: o corpo inteiro, mais o empurrão do piso e da parede, concentrados num arco de ferro do tamanho de uma mão. No osso, teria partido o osso. Na manopla, o golpe entrou no couro e no aço e não parou ali. No instante em que levantou o braço, Ilan tinha conjurado o caminho: três selos em sequência, rápidos como três batidas de dedo na mesa. Um no dorso da manopla, um na placa de ferro da bota esquerda, um no assoalho, com o traço de terra apontado para a viga mestra que sustentava aquele lado do corredor. O golpe correu por eles como água por uma calha, da manopla para a bota, da bota para o assoalho, do assoalho para a viga, e os três riscos acenderam em fila, do braço ao chão, e se apagaram juntos. A viga recebeu o golpe inteiro. A madeira estalou, uma nuvem de pó caiu do teto, a lâmpada de Clarão balançou. Ilan sentiu o tranco nos dentes e nos joelhos, mas continuou de pé.")

troca(209, "Não brigou com as âncoras das solas.",
"Não brigou com os selos das solas. Brigou com o da parede. Era o mais longe do corpo, o mais exposto, e o barbudo o tinha usado para avançar; por isso ainda estava aceso, carregado com o impulso que não tinha sido gasto. Ilan encostou dois dedos da manopla no anel azul e escreveu por cima dele, num gesto curto, a própria marca: uma cauda virada para o outro lado. O anel tremeu e mudou de letra, como uma assinatura rasurada. Por meio segundo, o impulso que o barbudo tinha deixado guardado na parede foi dele. E ele o devolveu inteiro, no sentido contrário.")

sub(227, "Você usou a minha âncora.", "Você usou o meu selo.")
sub(229, "— Você deixou ela carregada.", "— Você deixou ele aceso.")

sub(255, "os elos que vinham dos pregos de todos os quartos lá embaixo.", "os vínculos que vinham dos selos de todos os quartos lá embaixo.")

troca(291, "Ilan não estava perto o bastante",
"Ilan não estava perto o bastante para segurar a mão dele. Mas estava perto o bastante para segurar o cabo. Havia três metros entre ele e o painel; a uns dois, o cabo da alavanca vermelha passava rente a uma viga do telhado, preso por uma braçadeira de bronze. Ilan ergueu a mão esquerda, apontou dois dedos da manopla para a braçadeira e conjurou. No bronze acendeu um risco âmbar do tamanho de uma unha, que durou uma piscada e sumiu para os olhos, mas não para o fio que agora ligava a braçadeira à manopla.")

sub(295, "Deixou-a entrar pela marca, pela manopla,", "Deixou-a entrar pelo selo, pela manopla,")

sub(305, "vindos de dezenas de pregos, em dezenas de paredes geladas.", "vindos de dezenas de selos, em dezenas de paredes geladas.")
sub(305, "Os pregos continuavam cravados ao lado das brasas do deus.", "Os selos continuavam gravados ao lado das brasas do deus.")

troca(307, "Tinham sido feitos para levar calor",
"Tinham sido feitos para levar calor das paredes para o reservatório. A cauda de cada selo apontava para cima, mas a cauda de um selo de Brasa só diz por onde o calor pode passar. Quem decide para que lado ele vai é a diferença entre o quente e o frio. Durante semanas, o lado quente tinha sido a parede, junto às brasas do deus, e o lado frio, o reservatório. Agora o reservatório estava quase rachando de tanto calor. E as paredes, graças ao próprio Orsk, estavam cobertas de gelo.")

sub(311, "mantinham os vínculos dos pregos abertos num só sentido", "mantinham os vínculos dos selos abertos num só sentido")

sub(317, "e os pregos, feitos para um fio de calor e não para uma enxurrada, derreteriam dentro das paredes.",
"e os selos, gravados para um fio de calor e não para uma enxurrada, estourariam dentro das paredes, e o estouro voltaria por cada vínculo até a mão de quem os segurava.")

sub(351, "vem arrancar os pregos,", "vem raspar os selos,")
sub(423, "viria alguém tirar uns pregos das paredes,", "viria alguém raspar uns selos das paredes,")
full = "\n".join(L)
ruins = [l[:90] for l in L if re.search(r"\bâncoras?\b|\bpregos?\b", l.lower())]
assert not ruins, ruins
open(f"{OUT}/CAP01_COM_SELOS.md", "w", encoding="utf-8").write(full)

def md(p):
    p = html.escape(p)
    p = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", p)
    return p
corpo = []
for i, l in enumerate(L):
    if not l.strip(): continue
    if l.startswith("#"): corpo.append(f"<h2>{md(l.lstrip('# '))}</h2>"); continue
    if l.strip() == "---": corpo.append("<div class='sep'>◆</div>"); continue
    cls = " class='novo'" if i in MUD else ""
    corpo.append(f"<p{cls}>{md(l)}</p>")
regras = """<div class='regras'><h3>Regras usadas nesta amostra (rascunho do adendo)</h3><ul>
<li><b>Selo</b> é o ponto onde o vínculo se prende. A palavra "âncora" sai do livro.</li>
<li><b>Selo conjurado</b>: sai do próprio operador, aparece como um risco fino de luz na cor da disciplina, todo mundo vê, dura segundos. É rápido, fraco e cansa.</li>
<li><b>Selo gravado</b>: fixado num material (tijolo, couro, bronze). Leva tempo, é mais forte e dura. Os selos de Orsk e o da besta são gravados.</li>
<li><b>Gramática</b>: sinal da disciplina, cauda (por onde o fluxo pode passar), tamanho (quanto passa) e traço de terra (para onde vai o tranco). Sem traço de terra, o tranco volta para quem fez.</li>
<li>Selo é endereço, não força: quem paga a conta é o mundo (o degrau, a viga, a parede). As sete leis ficam iguais.</li>
<li>A balança no pulso de Ilan é o selo gravado da Ordem: segura trancos. Aqui só aparece como uma marca que esquenta; a explicação fica para depois.</li>
<li>Dá para escrever por cima do selo de outra pessoa (a Marca de Cobrança vira isso) e apagar o traço de terra dele.</li>
</ul><p class='leg'>Os parágrafos com fundo dourado são os que mudaram. O resto do capítulo está igual.</p></div>"""
page = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capítulo 1 com selos</title><style>
:root{{--bg:#F6F1E7;--fg:#2A2621;--mut:#7A6E5C;--ouro:#9C7A3C;--hl:#F1E3BE}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14120F;--fg:#E6DDCC;--mut:#A39478;--ouro:#C9A15A;--hl:#3A3020}}}}
body{{background:var(--bg);color:var(--fg);font-family:Georgia,'EB Garamond',serif;margin:0;padding:24px 16px;line-height:1.6}}
main{{max-width:720px;margin:0 auto}} h1{{font-weight:normal;letter-spacing:.06em;color:var(--ouro);font-size:1.6em}}
p{{margin:0 0 1em;text-align:justify}} p.novo{{background:var(--hl);border-left:3px solid var(--ouro);padding:8px 12px;border-radius:2px}}
.sep{{text-align:center;color:var(--ouro);margin:1.5em 0}} .regras{{border:1px solid var(--ouro);padding:12px 16px;margin:0 0 2em;border-radius:4px;font-size:.95em}}
.regras h3{{margin:.2em 0 .5em;color:var(--ouro);font-weight:normal}} .leg{{color:var(--mut);font-style:italic;margin-top:.6em}} li{{margin:.25em 0}}
</style></head><body><main><h1>Capítulo 1, com selos (amostra)</h1>{regras}{''.join(corpo)}</main></body></html>"""
open(f"{OUT}/CAP01_COM_SELOS.html", "w", encoding="utf-8").write(page)
print(len(MUD), "parágrafos alterados")
