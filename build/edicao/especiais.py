"""Páginas especiais do mundo: as Sete Leis, as Seis Disciplinas, a gramática do selo e a arquitetura da magia.
Sem spoilers: só o que o livro ensina nos primeiros capítulos."""
from motor import *

SIM = f"{ROOT}/exportacoes/identidade_aresta/simbolos"
LEIS = [("I", "Conservação", "conservacao", "Nada se cria. Tudo muda de lugar."),
        ("II", "Vínculo", "vinculo", "Sem ligação, nada passa."),
        ("III", "Compatibilidade", "compatibilidade", "O que não combina se rompe."),
        ("IV", "Vazão", "vazao", "Toda passagem tem um limite."),
        ("V", "Dissipação", "dissipacao", "Nada fica para sempre."),
        ("VI", "Capacidade", "capacidade", "Tudo tem um tamanho."),
        ("VII", "Retorno", "retorno", "Todo tranco volta para algum lugar.")]
DISC = [("Pulso", "pulso", "movimento e impulso", "azul"), ("Brasa", "brasa", "calor e frio", "vermelho"),
        ("Trama", "trama", "ligações e estruturas", "ouro velho"), ("Clarão", "clarao", "luz", "marfim"),
        ("Eco", "eco", "vibração e som", "azul-gelo"), ("Carga", "carga", "carga e raio", "ouro elétrico")]


def leis():
    itens = "".join(f'''<div class="lei"><img src="{img(f"{SIM}/leis/{k}_decorativa.png", 500)}"><div class="ln">{r}</div>
<div class="lt">{n}</div><div class="lx">{x}</div></div>''' for r, n, k, x in LEIS)
    return pagina(f'''<div class="esp"><div class="ek">O que todo mago aprende primeiro</div><div class="et">As Sete Leis</div>{ornamento()}
<div class="lgrid">{itens}</div><div class="enota">Valem para mortais, deuses e dragões. Nenhum selo, nenhuma coroa e nenhuma prece muda uma vírgula delas.</div></div>''', "noite")


def disciplinas():
    itens = "".join(f'''<div class="dis"><img src="{img(f"{SIM}/disciplinas/{k}_decorativa.png", 500)}"><div class="dt2" style="color:{COR[n]}">{n}</div>
<div class="dx">{x}</div><div class="dc">luz {c}</div></div>''' for n, k, x, c in DISC)
    return pagina(f'''<div class="esp"><div class="ek">O que a magia move</div><div class="et">Os Seis Sinais</div>{ornamento()}
<div class="dgrid">{itens}</div><div class="enota">Fogo, gelo, raio, vento: tudo é mistura destes seis. Cada disciplina acende os selos com a sua cor.</div></div>''', "noite")


def gramatica_selo():
    vermelho = COR["Brasa"]
    svg = f'''<svg viewBox="0 0 400 330" width="128mm" height="106mm">
<defs><filter id="gl"><feGaussianBlur stdDeviation="2.2"/></filter></defs>
<g stroke="{vermelho}" fill="none" stroke-linecap="round">
 <g filter="url(#gl)" opacity=".8"><circle cx="200" cy="150" r="78" stroke-width="7"/></g>
 <circle cx="200" cy="150" r="78" stroke-width="3"/>
 <path d="M200 92 C222 120 230 140 220 168 C214 184 206 194 200 206 C194 194 186 184 180 168 C172 148 184 130 190 142 C188 118 196 106 200 92 Z" fill="{vermelho}" stroke="none"/>
 <path d="M255 95 L302 48" stroke-width="3"/><path d="M290 48 L302 48 L302 60" stroke-width="3"/>
 <path d="M150 238 L250 238" stroke-width="3"/><path d="M168 252 L232 252" stroke-width="2.4"/><path d="M186 265 L214 265" stroke-width="2"/>
 <path d="M200 228 L200 238" stroke-width="3"/>
</g>
<g stroke="{OURO}" stroke-width=".8" fill="none" opacity=".9">
 <path d="M200 150 L60 60"/><path d="M302 48 L350 20"/><path d="M122 150 L40 170"/><path d="M150 238 L60 280"/>
</g>
<g font-family="AT" font-size="11" fill="{OURO}" letter-spacing="1.5">
 <text x="4" y="52">1 · SINAL</text><text x="330" y="14">2 · CAUDA</text><text x="2" y="186">3 · TAMANHO</text><text x="4" y="298">4 · TRAÇO DE TERRA</text></g>
<g font-family="EBG" font-size="10.5" fill="#E6DCC6" font-style="italic">
 <text x="4" y="66">qual disciplina passa</text><text x="300" y="34">por onde pode passar</text>
 <text x="2" y="200">o anel diz quanto cabe</text><text x="4" y="312">para onde vai o tranco</text></g>
</svg>'''
    return pagina(f'''<div class="esp"><div class="ek">Como se lê um selo</div><div class="et">A gramática do selo</div>{ornamento()}
<div class="fig">{svg}</div>
<div class="cols2"><div><div class="ch">Selo conjurado</div><p>Sai da mão, do pé ou do olhar treinado de quem faz. Um risco fino de luz que todo mundo vê.
Dura segundos. É rápido, é fraco e cansa.</p></div>
<div><div class="ch">Selo gravado</div><p>Fixado em pedra, couro, bronze ou osso, com tempo e ferramenta. Quase invisível até ser usado.
É forte e dura anos. Pode ser raspado, rasurado ou tomado.</p></div></div>
<div class="enota">Um selo não é uma força. É um endereço. Quem paga a conta é o mundo: o degrau, a viga, a parede, o lago.
Selo sem traço de terra devolve o tranco a quem fez.</div></div>''', "noite")


def arquitetura():
    etapas = [("Fonte", "fonte", "de onde sai"), ("Selo", "ancora", "onde se prende"), ("Vínculo", "elo", "por onde passa"),
              ("Destino", "destino", "para onde vai"), ("Controle", "controle", "quem segura"), ("Retorno", "retorno", "o que volta")]
    itens = "".join(f'''<div class="eta"><img src="{img(f"{SIM}/etapas_transposicao/{k}_decorativa.png", 400)}"><div class="lt">{n}</div><div class="lx">{x}</div></div>'''
                    + ('<div class="seta">→</div>' if i < 5 else "") for i, (n, k, x) in enumerate(etapas))
    return pagina(f'''<div class="esp"><div class="ek">A Transposição</div><div class="et">Toda magia, em seis passos</div>{ornamento()}
<div class="egrid">{itens}</div>
<div class="enota">A magia não cria nada. Ela muda de lugar o que já existe: calor, movimento, luz, som, carga, tensão.
Quem esquece o Retorno descobre, do pior jeito, para onde o tranco foi.</div></div>''', "noite")


CSS_ESP = f"""
.esp{{position:absolute;inset:0;padding:16mm 14mm;color:{MARFIM};text-align:center;display:flex;flex-direction:column;justify-content:center}}
.esp img{{mix-blend-mode:lighten}}
.ek{{font:400 8.5pt AT;letter-spacing:2mm;color:{OURO};text-transform:uppercase}}
.et{{font:700 24pt/1.15 AT;color:#E2C47E;margin:3mm 0 1mm}}
.enota{{font:italic 10.5pt/1.45 EBG;color:#D9CFB8;margin:5mm auto 0;max-width:118mm}}
.lgrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8mm 3mm;margin-top:8mm}}
.lgrid .lei:nth-child(5){{grid-column:1 / span 1;margin-left:16mm}}
.lei img,.dis img{{width:29mm;height:29mm;object-fit:contain}}
.ln{{font:400 8pt AT;color:{OURO};letter-spacing:1.2mm;margin-top:1mm}} .lt{{font:700 10.5pt AT;color:{MARFIM};margin-top:.6mm}}
.lx{{font:italic 9pt/1.3 EBG;color:#CFC4AC;margin-top:1mm}}
.dgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:7mm 4mm;margin-top:7mm}}
.dis img{{width:34mm;height:34mm}} .dt2{{font:700 13pt AT;margin-top:2mm}} .dx{{font:italic 10pt EBG;color:#E2D8C2}}
.dc{{font:400 7pt AT;letter-spacing:1mm;color:#9A8A6A;text-transform:uppercase;margin-top:1mm}}
.fig{{margin:2mm auto 0}}
.cols2{{display:grid;grid-template-columns:1fr 1fr;gap:7mm;text-align:left;margin-top:2mm}}
.cols2 p{{font:10pt/1.42 EBG;color:#E2D8C2;margin:1.5mm 0 0}} .ch{{font:700 10.5pt AT;color:#E2C47E;letter-spacing:.5mm}}
.egrid{{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:2mm 1mm;margin-top:10mm}}
.eta{{width:36mm}} .eta img{{width:30mm;height:30mm;object-fit:contain}} .seta{{font:16pt EBG;color:{OURO};width:6mm}}
"""
