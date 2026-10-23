"""Armorial e Codex de Aresta: só pranchas pintadas do nosso acervo (GitHub) e artes da coleção, em molduras de galeria."""
from motor import *

BA = "exportacoes/banco_de_arte"
DR = "exportacoes/acervo_drive"
B4 = "exportacoes/banco_de_arte_4x"
SIM = "exportacoes/identidade_aresta/simbolos"

CANTO = (f'<svg viewBox="0 0 40 40" class="ct"><path d="M2 38 V2 H38" fill="none" stroke="{OURO}" stroke-width="1.6"/>'
         f'<path d="M7 38 V7 H38" fill="none" stroke="{OURO}" stroke-width=".6"/><circle cx="7" cy="7" r="2.4" fill="{OURO}"/></svg>')


def moldura_img(path, w=None, h=None, pos="center", maxw=2000):
    st = f"width:{w}mm;" if w else ""
    st += f"height:{h}mm;" if h else ""
    return (f'<div class="mol" style="{st}"><div class="moli" style="background-image:url({img(path, maxw)});background-position:{pos}"></div>'
            f'{CANTO}{CANTO.replace("class=\"ct\"", "class=\"ct c2\"")}{CANTO.replace("class=\"ct\"", "class=\"ct c3\"")}{CANTO.replace("class=\"ct\"", "class=\"ct c4\"")}</div>')


def placa(path, titulo, legenda, rotulo="Armorial de Aresta"):
    """Prancha de página inteira em paisagem, com moldura, título e legenda; a moldura segue a proporção da arte."""
    from PIL import Image
    w, h = Image.open(path if path.startswith("/") else f"{ROOT}/{path}").size
    mw, mh = 200, 116
    if w / h > mw / mh:
        mh = round(mw * h / w)
    else:
        mw = round(mh * w / h)
    return pagina(f'''<div class="pl"><div class="ek">{esc(rotulo)}</div><div class="plt">{esc(titulo)}</div>
{moldura_img(path, mw + 5, mh + 5)}<div class="pll">{esc(legenda)}</div></div>''', "noite", nome="paisagem")


def galeria(titulo, itens, cols=2, alt=82, rotulo="Codex de Aresta", pos="center 22%"):
    cards = "".join(f'<div class="gc">{moldura_img(p, None, alt, pos, 1300)}<div class="gt">{esc(t)}</div>'
                    f'<div class="gx">{esc(x)}</div></div>' for p, t, x in itens)
    return pagina(f'''<div class="gal"><div class="ek">{esc(rotulo)}</div><div class="plt">{esc(titulo)}</div>{ornamento()}
<div class="gg2" style="grid-template-columns:repeat({cols},1fr)">{cards}</div></div>''', "noite")


def heroi(path, titulo, sub, pos="center 20%"):
    return pagina(f'''<div class="bg" style="background-image:url({img(path, 2000)});background-position:{pos}"></div><div class="veu baixo"></div>
<div class="her"><div class="ek">Codex de Aresta</div><div class="ptit">{esc(titulo)}</div>{ornamento()}<div class="pepi"><p>{esc(sub)}</p></div></div>''', "img")


def divisor(titulo, sub, selar="CODEX DE ARESTA"):
    return pagina(f'''<div class="parte">{anel_svg(44)}<div class="ptit" style="margin-top:8mm">{esc(titulo)}</div>{ornamento()}
<div class="pepi"><p>{esc(sub)}</p></div><div class="selar">{esc(selar)}</div></div>''', "noite")


INSIGNIAS = [("ordem_da_ultima_sentenca", "Ordem da Última Sentença"), ("os_carrascos", "Os Carrascos"), ("ilan_varek", "Ilan Varek"),
             ("aurelia", "Aurelia"), ("os_limiares", "Os Limiares"), ("coroas_e_soberanias", "Coroas e Soberanias"),
             ("companhia_arrimo", "Companhia Arrimo"), ("cidades_livres", "Cidades Livres"), ("os_dragoes", "Os Dragões")]


def insignias():
    h = "".join(f'<div class="ins"><img src="{img(f"{SIM}/instituicoes/{k}_decorativa.png", 500)}"><div class="gt">{esc(t)}</div></div>' for k, t in INSIGNIAS)
    return pagina(f'''<div class="gal"><div class="ek">Armorial de Aresta</div><div class="plt">Insígnias</div>{ornamento()}
<div class="insg">{h}</div><div class="pll" style="margin-top:6mm">As marcas gravadas em sinetes, portas e lacres de cada ordem, casa e companhia.</div></div>''', "noite")


def armorial():
    F, O = f"{BA}/03_faccoes", f"{BA}/04_objetos"
    return [divisor("Armorial de Aresta", "Estandartes, brasões, sinetes e bandeiras das ordens, das casas, das companhias, dos deuses e das terras.", "ARMORIAL"),
            placa(f"{F}/FA-001_seis_faccoes.png", "As seis facções", "Ordem da Última Sentença · Carrascos · Coroa dos Limiares · Convergência de Limiar · Cidades Livres · Dragões"),
            placa(f"{F}/FA-002_outras_casas.png", "Outras casas", "Aurelia · Ilan Varek · Arquivistas · Círculo do Vazio Profundo · Senhorios de Aresta"),
            placa(f"{F}/FA-003_vhalessa.png", "Vhalessa", "Casa da Fornalha · Coroa do Sol de Inverno · Câmara dos Pactos · Conselho da cidade"),
            placa(f"{F}/FA-004_companhias_e_guildas.png", "Companhias e guildas", "Companhia Arrimo · Kaltz e Filhas · Guilda dos Graneleiros · Liga dos Peritos de Selos"),
            placa(f"{F}/FA-005_deuses_vizinhos.png", "Soberanias vizinhas", "Reinos da Tempestade · Necrópole do Poente · Soberania dos Limiares · A Velha das Cristas"),
            placa(f"{F}/FA-006_terras_de_aresta.png", "As terras de Aresta", "Reinos do Norte · Delta e Arquivos · Ilhas-Prisma · Terras dos Dragões · Cidade de Limiar · Cidades Livres · A Confluência"),
            placa(f"{O}/OB-004_estandartes.png", "Estandartes das facções", "Os dez estandartes, como desfilam nas cortes de Aresta"),
            insignias(),
            placa(f"{O}/OB-001_selos_de_cera.png", "Sinetes e lacres", "Cera vermelha, azul, verde e marfim: cada cor, uma casa"),
            placa(f"{O}/OB-002_medalhoes.png", "Medalhões", "As medalhas que se usam no peito e se escondem debaixo da gola"),
            placa(f"{O}/OB-003_aneis_de_autoridade.png", "Anéis de autoridade", "Quem carimba com o anel responde pelo que carimbou"),
            placa(f"{O}/OB-006_marcas_em_manuscritos.png", "Marcas em manuscritos", "Sigilos em tinta, nas margens dos livros que valem a pena roubar")]


AURELIA = [("PE-012_aurelia_dourada_retrato", "A Senhora dos Limiares", "o rosto que a cidade inteira aprendeu a reconhecer"),
           ("PE-008_aurelia_dourada_portal", "No portal", "toda porta é uma pergunta"),
           ("PE-010_aurelia_dourada_escadaria", "A escadaria", "descer também é um jeito de chegar"),
           ("PE-011_aurelia_dourada_trono", "O trono", "mil anos de audiências"),
           ("PE-013_aurelia_veu_dourado_vento", "Véu ao vento", "nas varandas do Átrio"),
           ("PE-014_aurelia_regalia_de_batalha", "Regalia de batalha", "quando a deusa decide lutar"),
           ("PE-016_aurelia_luar_sacada", "Luar na sacada", "uma deusa também perde o sono"),
           ("PE-017_aurelia_chiffon_grego", "Chiffon e ouro", "o luxo de não pedir desculpas"),
           ("PE-018_aurelia_lago_de_luz", "O lago de luz", "a água lembra de tudo"),
           ("PE-015_aurelia_reclinada_templo", "No templo", "o descanso depois da conta"),
           ("PE-009_aurelia_dourada_costas", "De costas", "e mesmo assim olhando"),
           ("PE-002_aurelia_retrato", "O primeiro estudo", "a deusa antes da direção dourada")]


def aurelia():
    P = f"{BA}/06_personagens"
    lista = [(f"{P}/{k}.png", t, x) for k, t, x in AURELIA]
    pg = [heroi(f"{B4}/06_personagens/PE-012_aurelia_dourada_retrato_4x.jpg", "A Senhora dos Limiares", "Aurelia, deusa das portas, das passagens e das tarifas.")]
    for i in range(1, len(lista), 4):
        pg.append(galeria("A Senhora dos Limiares", lista[i:i + 4], 2, 88))
    pg.append(placa(f"{BA}/06_personagens/PE-015_aurelia_reclinada_templo.png", "No templo", "Aurelia em repouso", "A Senhora dos Limiares"))
    return pg


def galeria_acervo():
    P = f"{DR}/personagens"; V = f"{DR}/producao_v2"
    a = [(f"{P}/P01_Ilan_Varek_Master.png", "Ilan Varek", "estudo de figurino"), (f"{P}/P03V2_Mara_Quen_Master_v2.png", "Mara Quen", "a auditora"),
         (f"{P}/P04_Nara_Voss_Master.png", "Nara Voss", "a oficina"), (f"{P}/P05_Sevran_Master.png", "Sevran", "a cozinha"),
         (f"{V}/P04_01.png", "Nara na bancada", "cobre e cerâmica"), (f"{V}/P05_01.png", "A sopa da Cozinha do Lento", "ninguém trabalha bem com fome")]
    b = [(f"{P}/P07_Thor_Master.png", "Thor", "senhor do trovão dos Reinos da Tempestade"), (f"{P}/P08_Anubis_Master.png", "Anúbis", "guardião da Necrópole do Poente"),
         (f"{P}/P06_Cassia_Vale_Master.png", "Cassia Vale", "comissária da Câmara dos Pactos"), (f"{P}/P09_Eron_Tahl_Master.png", "Eron Tahl", "a Linha Seca"),
         (f"{P}/P11_Ithren_Master.png", "Mestre Ithren", "o homem de muitos rostos"), (f"{P}/P10_Iolanthe_Ness_Master.png", "A velha mestra", "uma sala sobre um armazém, no oeste")]
    c = [(f"{V}/P02_01.png", "Aurelia à porta dourada", "inverno no Átrio"), (f"{V}/P01_01.png", "Ilan na escadaria", "a noite de Vhalessa"),
         (f"{P}/P12_Estudo_Reservado_v1.png", "Estudo reservado", "o leito de gelo"), (f"{DR}/cenarios/S03_Oficina_Voss.png", "A Oficina Voss", "o primeiro estudo"),
         (f"{DR}/cenarios/S04_Cozinha_do_Lento.png", "A Cozinha do Lento", "o primeiro estudo"), (f"{DR}/cenarios/S02_Atrio_da_Soleira.png", "O Átrio de Soleira", "o salão das portas")]
    return [galeria("Os nossos", a, 3, 62), galeria("Em Vhalessa e além", b, 3, 62), galeria("Estudos e cenários", c, 3, 62)]


def expressoes():
    V = f"{DR}/producao_v2"
    return [placa(f"{V}/F0{i}.png", t, "folha de expressões", "Galeria de personagens") for i, t in
            ((1, "Ilan Varek"), (2, "Aurelia"), (3, "Mara Quen"), (4, "Nara Voss"), (5, "Sevran"))]


def arsenal():
    A = f"{DR}/artefatos"
    itens = [(f"{A}/A01_Manopla_Esquerda_Tres_Celulas.png", "A manopla de Ilan", "couro, aço e três células de cerâmica"),
             (f"{A}/A02_Espada_de_Ilan.png", "A espada de Ilan", "ferro simples, guarda simples"),
             (f"{A}/A03_Martelo_de_Thor.png", "O martelo de Thor", "cabo curto demais para o dono"),
             (f"{A}/A04_Chave_e_Circlet_de_Aurelia.png", "A chave de bronze", "e o diadema da Senhora dos Limiares"),
             (f"{A}/A05_Maleta_de_Placas_Mara.png", "As placas de Mara", "vidro fino que mede o que passa"),
             (f"{A}/A06_Favo_Termico.png", "O favo térmico", "células de seis lados, cintas de bronze")]
    return [galeria("Arsenal e artefatos", itens, 2, 52),
            galeria("Arsenal e artefatos", [(f"{A}/A07_Fiel_Agulha_de_Bronze.png", "O fiel", "uma agulha de bronze, longa e fina"),
                                            (f"{DR}/producao_v2/W01_v2.png", "A manopla, aberta", "estudo de engenharia"),
                                            (f"{BA}/04_objetos/OB-007_artefatos_de_colecao.png", "Peças de coleção", "medalhão, sinete e anel"),
                                            (f"{BA}/01_identidade/ID-009_emblema_medalhao.png", "O emblema da saga", "a lâmina, a balança e o arco")], 2, 52)]


def engenharia():
    R = f"{B4}/12_referencias"
    return [placa(f"{R}/RF-004_registro_das_leis_4x.jpg", "Registro das Leis", "“Os deuses também as obedecem. A diferença é que eles têm tempo demais para disfarçar.”", "Engenharia arcana"),
            placa(f"{R}/RF-005_instrumentos_4x.jpg", "Instrumentos arcano-técnicos", "bastão · círculo · orbe · selo · códice · matriz", "Engenharia arcana"),
            placa(f"{R}/RF-006_diagramas_de_circuitos_4x.jpg", "Diagramas de circuitos", "círculo de contenção · canal de transposição · feitiço de estrutura", "Engenharia arcana")]


CSS_ARM = f"""
.pl,.gal,.her{{position:absolute;inset:0;color:{MARFIM};text-align:center;display:flex;flex-direction:column;align-items:center}}
.pl{{padding:9mm 14mm 8mm;justify-content:center}} .gal{{padding:15mm 12mm 10mm}} .her{{justify-content:flex-end;padding:0 16mm 24mm}}
.plt{{font:700 17pt/1.15 AT;color:#E2C47E;letter-spacing:.8mm;margin:1.5mm 0 3mm}}
.pll{{font:italic 10pt/1.4 EBG;color:#D9CFB8;margin-top:3.5mm;max-width:190mm}}
.mol{{position:relative;width:100%;padding:2.4mm;background:linear-gradient(145deg,#2A241B,#0F0D0B);box-shadow:0 1mm 4mm rgba(0,0,0,.6),inset 0 0 0 .35mm #8A6E3A}}
.moli{{width:100%;height:100%;background-size:cover;background-repeat:no-repeat;box-shadow:inset 0 0 0 .3mm #C9A15A}}
.ct{{position:absolute;width:7mm;height:7mm;left:-1.2mm;top:-1.2mm}} .c2{{left:auto;right:-1.2mm;transform:scaleX(-1)}}
.c3{{top:auto;bottom:-1.2mm;transform:scaleY(-1)}} .c4{{left:auto;top:auto;right:-1.2mm;bottom:-1.2mm;transform:scale(-1,-1)}}
.gg2{{display:grid;gap:6mm 5mm;width:100%;margin-top:3mm;text-align:center}}
.gt{{font:700 8.8pt AT;color:#E2C47E;margin-top:2mm;letter-spacing:.4mm}} .gx{{font:italic 8.2pt/1.25 EBG;color:#CFC4AC}}
.insg{{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm 4mm;width:100%;margin-top:5mm}}
.ins img{{width:32mm;height:32mm;object-fit:contain;mix-blend-mode:lighten}}
"""
