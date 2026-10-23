"""Armorial de Aresta — feito com os símbolos do nosso sistema (build/aresta/simbolos.py,
exportacoes/identidade_aresta/simbolos/). Cada instituição e região ganha brasão, bandeira e estandarte no mesmo
desenho; as pranchas pintadas do banco de arte (facções, estandartes, selos de cera, medalhões, anéis) entram em seguida."""
import re
from motor import *

SIM = f"{ROOT}/exportacoes/identidade_aresta/simbolos"
INST = [("ordem_da_ultima_sentenca", "Ordem da Última Sentença", "A lei acima de tudo.", "#283040", OURO),
        ("os_carrascos", "Os Carrascos", "Equilíbrio pela ausência.", "#4E1216", "#D9B26A"),
        ("ilan_varek", "Ilan Varek", "Sobrevivência é princípio.", "#26272A", "#C9A15A"),
        ("aurelia", "Aurelia, Senhora dos Limiares", "Limiares, soberania, escolhas.", "#5E461A", "#F2DDA0"),
        ("os_limiares", "Os Limiares", "Portais exigem testemunhas.", "#1D4442", OURO),
        ("coroas_e_soberanias", "Coroas e Soberanias", "Entre mundos, há um trono.", "#40294F", "#E2C47E"),
        ("companhia_arrimo", "Companhia Arrimo", "A apólice cobre o que pode.", "#3A362C", "#D7C08A"),
        ("cidades_livres", "Cidades Livres", "Povos escolhem.", "#24425F", "#E2C47E"),
        ("os_dragoes", "Os Dragões", "Memória mais antiga que os deuses.", "#62241A", "#E6B07A")]
REG = [("cidade_de_limiar", "Cidade de Limiar", "Onde todos os caminhos se encontram.", "#22403F"),
       ("reinos_do_norte", "Reinos do Norte", "Ferro, tempestade e juramento.", "#36404C"),
       ("delta_e_arquivos", "Delta e Arquivos", "O que não pode ser esquecido.", "#2A4636"),
       ("ilhas_prisma", "Ilhas-Prisma", "Luz dividida sobre o mar.", "#37305A"),
       ("terras_dos_dragoes", "Terras dos Dragões", "Escama, soberania e tempo.", "#54221A"),
       ("cidades_livres", "Cidades Livres", "Ninguém manda em quem escolhe.", "#4A4524"),
       ("a_confluencia", "A Confluência", "O que liga e o que pode ruir.", "#283C58")]


def simbolo(pasta, chave, cor):
    s = open(f"{SIM}/{pasta}/{chave}_linear_marfim.svg", encoding="utf-8").read()
    corpo = re.sub(r"^.*?<svg[^>]*>", "", s, flags=re.S).rsplit("</svg>", 1)[0]
    return corpo.replace("#EFE8DA", cor)


def brasao(sim, fundo, metal):
    return f'''<svg viewBox="0 0 220 260" class="hb"><defs><linearGradient id="g{fundo[1:]}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{fundo}" stop-opacity=".85"/><stop offset="1" stop-color="{fundo}"/></linearGradient></defs>
<path d="M18 16 H202 V120 C202 190 150 230 110 248 C70 230 18 190 18 120 Z" fill="url(#g{fundo[1:]})" stroke="{metal}" stroke-width="5"/>
<path d="M30 28 H190 V120 C190 182 145 216 110 233 C75 216 30 182 30 120 Z" fill="none" stroke="{metal}" stroke-width="1.2" opacity=".7"/>
<g transform="translate(35 40) scale(.75)">{sim}</g></svg>'''


def bandeira(sim, fundo, metal):
    return f'''<svg viewBox="0 0 300 200" class="hf"><path d="M6 10 H294 L270 100 L294 190 H6 Z" fill="{fundo}" stroke="{metal}" stroke-width="3"/>
<path d="M6 10 L110 100 L6 190" fill="none" stroke="{metal}" stroke-width="1.4" opacity=".55"/>
<g transform="translate(115 30) scale(.7)">{sim}</g></svg>'''


def estandarte(sim, fundo, metal):
    franja = "".join(f'<line x1="{x}" y1="352" x2="{x}" y2="366" stroke="{metal}" stroke-width="2"/>' for x in range(34, 170, 9))
    return f'''<svg viewBox="0 0 200 400" class="he"><line x1="10" y1="14" x2="190" y2="14" stroke="{metal}" stroke-width="5" stroke-linecap="round"/>
<circle cx="10" cy="14" r="7" fill="{metal}"/><circle cx="190" cy="14" r="7" fill="{metal}"/>
<path d="M30 20 H170 V340 L100 372 L30 340 Z" fill="{fundo}" stroke="{metal}" stroke-width="3"/>
<path d="M40 30 H160 V334 L100 362 L40 334 Z" fill="none" stroke="{metal}" stroke-width="1" opacity=".6"/>
<g transform="translate(40 90) scale(.6)">{sim}</g><circle cx="100" cy="290" r="8" fill="{metal}"/>{franja}</svg>'''


def pagina_armas(titulo, lema, sim, fundo, metal, rotulo):
    return pagina(f'''<div class="arm"><div class="ek">{esc(rotulo)}</div><div class="et" style="font-size:19pt">{esc(titulo)}</div>{ornamento()}
<div class="armg"><div class="ac">{estandarte(sim, fundo, metal)}<div class="al">Estandarte</div></div>
<div class="ad"><div class="ac">{brasao(sim, fundo, metal)}<div class="al">Brasão</div></div>
<div class="ac">{bandeira(sim, fundo, metal)}<div class="al">Bandeira</div></div></div></div>
<div class="lema">“{esc(lema)}”</div><div class="selar" style="bottom:9mm">{esc(re.sub(r"[^A-Za-z ]", "", titulo).upper())}</div></div>''', "noite")


def armorial():
    pg = [pagina(f'''<div class="parte">{anel_svg(44)}<div class="ptit" style="margin-top:8mm">Armorial de Aresta</div>{ornamento()}
<div class="pepi"><p>Brasões, bandeiras e estandartes das ordens, das casas, das companhias e das terras de Aresta.</p></div>
<div class="selar">ARMORIAL</div></div>''', "noite")]
    for k, t, lema, fundo, metal in INST:
        pg.append(pagina_armas(t, lema, simbolo("instituicoes", k, metal), fundo, metal, "Ordens, casas e companhias"))
    for k, t, lema, fundo in REG:
        pg.append(pagina_armas(t, lema, simbolo("regioes_conceituais", k, OURO), fundo, OURO, "As terras de Aresta"))
    BA = "exportacoes/banco_de_arte"
    for p, leg in ((f"{BA}/03_faccoes/FA-001_seis_faccoes.png", "As seis facções"), (f"{BA}/03_faccoes/FA-002_outras_casas.png", "Outras casas"),
                   (f"{BA}/04_objetos/OB-004_estandartes.png", "Estandartes das facções"), (f"{BA}/04_objetos/OB-001_selos_de_cera.png", "Sinetes e lacres"),
                   (f"{BA}/04_objetos/OB-002_medalhoes.png", "Medalhões"), (f"{BA}/04_objetos/OB-003_aneis_de_autoridade.png", "Anéis de autoridade")):
        pg.append(pagina(f'<div class="bg" style="background-image:url({img(p, 2200)})"></div><div class="veu"></div><div class="leg" style="font:700 10pt AT;letter-spacing:1.4mm">{esc(leg.upper())}</div>',
                         "img", nome="paisagem"))
    return pg


CSS_ARM = f"""
.arm{{position:absolute;inset:0;padding:16mm 12mm 14mm;color:{MARFIM};text-align:center;display:flex;flex-direction:column}}
.armg{{display:grid;grid-template-columns:52mm 1fr;gap:5mm;align-items:center;margin-top:5mm;flex:1}}
.ad{{display:flex;flex-direction:column;gap:7mm;align-items:center}}
.he{{width:50mm;height:100mm}} .hb{{width:56mm;height:66mm}} .hf{{width:66mm;height:44mm}}
.al{{font:400 7.5pt AT;letter-spacing:1.6mm;color:#9A8A6A;text-transform:uppercase;margin-top:1.4mm}}
.lema{{font:italic 12pt EBG;color:#E6DCC6;margin:3mm 0 10mm}}
"""
