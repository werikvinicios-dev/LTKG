#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pranchas da identidade Aresta, no layout das referências do autor (4:3), montadas com as artes do banco
(exportacoes/banco_de_arte) e textos editáveis por cima (Cinzel + EB Garamond). Captura em 2896 × 2172."""
import os, subprocess, html
ROOT = "/home/user/LTKG"
BA = f"{ROOT}/exportacoes/banco_de_arte"
OUT = f"{ROOT}/exportacoes/identidade_aresta/pranchas"
TMP = f"{ROOT}/build/_pranchas_aresta"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
F = f"file://{ROOT}/build/fonts"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)

def A(p): return f"file://{BA}/{p}"

CSS = f"""
@font-face{{font-family:Cz;src:url('{F}/Cinzel-SemiBold.ttf')}}
@font-face{{font-family:CzB;src:url('{F}/Cinzel-Bold.ttf')}}
@font-face{{font-family:Gi;src:url('{F}/EBGaramond-Italic.ttf')}}
@font-face{{font-family:G;src:url('{F}/EBGaramond-Regular.ttf')}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1448px;height:1086px;overflow:hidden;background:#090807;color:#E9E0CC;font-family:G}}
body{{background:linear-gradient(rgba(8,7,6,.86),rgba(8,7,6,.9)),url({A('08_editorial/ED-003_texturas_e_materiais.png')}) 0 0/360px auto}}
.p{{position:absolute;border:1px solid #6B5532;background:rgba(10,9,8,.72);overflow:hidden}}
.p:before{{content:"";position:absolute;inset:3px;border:1px solid rgba(201,161,90,.18);pointer-events:none;z-index:3}}
.t{{position:absolute;left:0;right:0;top:0;padding:7px 12px 16px;background:linear-gradient(rgba(6,5,4,.94),rgba(6,5,4,.6) 60%,rgba(6,5,4,0));z-index:4;font-family:Cz;font-size:12.5px;letter-spacing:3.2px;color:#D9BC7C;text-transform:uppercase;
   text-shadow:0 1px 3px #000}}
.t small{{font-size:8.5px;letter-spacing:2.4px;color:#9C8A66;margin-left:14px}}
.img{{position:absolute;inset:0;background-size:cover;background-position:center}}
.lab{{position:absolute;display:flex;z-index:4;align-items:flex-end;padding-bottom:3px}}
.lab:before{{content:"";position:absolute;left:-12px;right:-12px;top:-14px;bottom:-6px;background:linear-gradient(rgba(6,5,4,0),rgba(6,5,4,.88) 45%);z-index:-1}}
.lab div{{flex:1;text-align:center;font-family:Cz;font-size:10px;letter-spacing:1.4px;color:#EADFC6;line-height:1.25;text-shadow:0 1px 3px #000}}
.lab i{{display:block;font-family:Gi;font-style:normal;font-size:10.5px;letter-spacing:0;color:#B8A887}}
.q{{font-family:Gi;color:#D7CBB2;line-height:1.35;text-shadow:0 1px 4px #000}}
.h1{{font-family:CzB;color:#E2C47E;letter-spacing:4px;text-shadow:0 2px 8px #000}}
.sc{{font-family:Cz;letter-spacing:2.6px;color:#C9A15A;text-transform:uppercase}}
.fade-r{{background:linear-gradient(90deg,rgba(9,8,7,.92) 0%,rgba(9,8,7,.6) 38%,rgba(9,8,7,0) 70%)}}
.fade-l{{background:linear-gradient(270deg,rgba(9,8,7,.92) 0%,rgba(9,8,7,.55) 40%,rgba(9,8,7,0) 70%)}}
.fade-b{{background:linear-gradient(0deg,rgba(9,8,7,.95) 0%,rgba(9,8,7,.5) 35%,rgba(9,8,7,0) 60%)}}
ul.b{{list-style:none}} ul.b li{{font-family:Cz;font-size:9.5px;letter-spacing:1.6px;color:#D9CDB4;margin:3px 0}} ul.b li:before{{content:"◆ ";color:#C9A15A;font-size:7px}}
"""

def panel(x, y, w, h, title="", img=None, pos="center", sub="", extra="", fit="cover"):
    t = f'<div class="t">{title}<small>{sub}</small></div>' if title else ""
    im = f'<div class="img" style="background-image:url({img});background-position:{pos};background-size:{fit}"></div>' if img else ""
    return f'<div class="p" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{im}{t}{extra}</div>'

def labels(x, y, w, items, h=40):
    cells = "".join(f'<div>{a}<i>{b}</i></div>' for a, b in items)
    return f'<div class="lab" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{cells}</div>'

def page(body):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'

def shot(name, body):
    hp = f"{TMP}/{name}.html"; pp = f"{OUT}/{name}.png"
    open(hp, "w", encoding="utf-8").write(page(body))
    subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--hide-scrollbars",
                    "--force-device-scale-factor=2", "--window-size=1448,1086", f"--screenshot={pp}", "file://" + hp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pp

LEIS = [("I · Conservação", "Tudo persiste."), ("II · Vínculo", "Tudo se conecta."), ("III · Compatibilidade", "Tudo se ajusta."),
        ("IV · Vazão", "Tudo flui."), ("V · Dissipação", "Tudo se desfaz."), ("VI · Capacidade", "Tudo tem limite."), ("VII · Retorno", "Tudo volta.")]
LEIS_LONG = [("I · Conservação", "Nada é criado. Tudo se transforma."), ("II · Vínculo", "Toda magia requer uma ligação."),
             ("III · Compatibilidade", "O que não ressoa se rompe."), ("IV · Vazão", "Toda passagem tem um limite."),
             ("V · Dissipação", "Nada permanece para sempre."), ("VI · Capacidade", "Todo ser, objeto ou lugar tem um limite."),
             ("VII · Retorno", "Toda ação retorna.")]
DISC = [("Pulso", "Movimento."), ("Brasa", "Transformação."), ("Trama", "Estrutura."), ("Clarão", "Revelação."), ("Eco", "Ressonância."), ("Carga", "Acúmulo.")]
FAC = [("Ordem da Última Sentença", "A lei acima de tudo."), ("O Carrasco", "Cortar para que permaneça."), ("Coroa dos Limiares", "Entre mundos, há um trono."),
       ("Convergência de Limiar", "Portais exigem testemunhas."), ("Cidades Livres", "Povos escolhem. Aresta resiste."), ("Os Dragões", "Memória mais antiga que os deuses.")]
CASAS = [("Aurelia", "Limiares, soberania, escolhas."), ("Ilan Varek", "Sobrevivência é princípio."), ("Arquivistas", "Tudo deixa registro."),
         ("Círculo do Vazio Profundo", "O que caiu ainda canta."), ("Senhorios de Aresta", "Poder é negociação.")]
EST = ["Ordem da Última Sentença", "Carrasco", "Coroa dos Limiares", "Convergência de Limiar", "Cidades Livres", "Os Dragões", "Aurelia", "Ilan Varek", "Arquivistas", "Círculo do Vazio Profundo"]

def logo_center(x, y, w, h):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:url({A("01_identidade/ID-007_logo_vertical_transparente.png")}) center/contain no-repeat;filter:drop-shadow(0 0 18px #000) drop-shadow(0 0 30px #000)"></div>'

# ------------------------------------------------------------------ 1. emblemas, símbolos, selos, heráldica
def prancha_1():
    b = []
    b.append(panel(0, 0, 1448, 128, img=A("05_mundo/MU-001_cidade_de_limiar.png"), pos="center 40%",
                   extra='<div class="img fade-r"></div><div class="img fade-l"></div>'
                         '<div style="position:absolute;left:210px;top:24px;z-index:4" class="h1"><span style="font-size:23px">EMBLEMAS ◆ SÍMBOLOS ◆ SELOS ◆ HERÁLDICA</span>'
                         '<div class="sc" style="font-size:12px;margin-top:6px;letter-spacing:3px">Leis, disciplinas, facções e marcas do mundo</div></div>'
                         '<div class="q" style="position:absolute;left:196px;top:86px;font-size:13px;z-index:4">Em Aresta, tudo deixa um sinal.</div>'
                         '<div class="q" style="position:absolute;right:120px;top:30px;font-size:13.5px;z-index:4;text-align:left">Leis são mais que palavras.<br>São armas, fronteiras e memórias.<br>São os vestígios de um mundo que se recusa a morrer.</div>'))
    b.append(panel(8, 136, 576, 262, "Sete leis", A("02_simbolos/SI-001_sete_leis.png"), "center 40%", "Princípios que sustentam o mundo",
                   labels(10, 214, 556, [(a.replace(" · ", "<br>"), b) for a, b in LEIS], 46).replace("font-size:10px", "font-size:8.6px")))
    b.append(panel(864, 136, 576, 262, "Seis disciplinas", A("02_simbolos/SI-002_seis_disciplinas.png"), "center 8%", "Artes que tornam a lei ação", fit="100% auto", extra=
                   labels(10, 220, 556, DISC)))
    b.append(logo_center(592, 120, 264, 282))
    b.append(panel(8, 408, 930, 286, "Facções e instituições", A("03_faccoes/FA-001_seis_faccoes.png"), "center 6%", "", labels(8, 240, 914, FAC, 44), fit="100% auto"))
    b.append(panel(946, 408, 494, 286, "Outras casas, cultos e ordens", A("03_faccoes/FA-002_outras_casas.png"), "center 20%", "", labels(6, 240, 482, CASAS, 44), fit="100% auto"))
    b.append(panel(8, 702, 436, 150, "Selos de cera", A("04_objetos/OB-001_selos_de_cera.png"), "center 55%"))
    b.append(panel(452, 702, 456, 150, "Medalhões e insígnias", A("04_objetos/OB-002_medalhoes.png"), "center 60%"))
    b.append(panel(916, 702, 524, 150, "Anéis de autoridade", A("04_objetos/OB-003_aneis_de_autoridade.png"), "center 58%"))
    b.append(panel(8, 860, 720, 218, "Estandartes", A("04_objetos/OB-004_estandartes.png"), "center 45%", "",
                   labels(6, 188, 708, [(e, "") for e in EST], 24).replace("font-size:10px", "font-size:7.4px")))
    b.append(panel(736, 860, 362, 218, "Marcas em manuscritos", A("04_objetos/OB-006_marcas_em_manuscritos.png")))
    b.append(panel(1106, 860, 334, 218, "Aplicações", A("04_objetos/OB-007_artefatos_de_colecao.png"), "center 55%"))
    return shot("PR-01_emblemas_simbolos_selos_heraldica", "".join(b))

# ------------------------------------------------------------------ 2. aplicações do título da saga
def prancha_2():
    b = []
    b.append(panel(0, 0, 560, 300, img=A("10_promocional/PR-001_poster_cinematografico.png"), pos="center 55%",
                   extra='<div class="img fade-r"></div><div style="position:absolute;left:22px;top:22px;width:250px;height:140px;'
                         f'background:url({A("01_identidade/ID-006_lettering_transparente.png")}) center/contain no-repeat"></div>'
                         '<ul class="b" style="position:absolute;left:28px;top:178px;z-index:4"><li>Mundos em colisão.</li><li>Leis em ruínas.</li>'
                         '<li>Deuses em queda.</li><li>Homens no julgamento.</li></ul>'))
    b.append(panel(568, 8, 872, 160, "Aplicações do título da saga", None, extra=
                   f'<div style="position:absolute;left:12px;top:30px;width:300px;height:124px;background:url({A("01_identidade/ID-003_logo_horizontal.png")}) center/cover"></div>'
                   f'<div style="position:absolute;left:322px;top:30px;width:280px;height:124px;background:url({A("01_identidade/ID-006_lettering_transparente.png")}) center/contain no-repeat"></div>'
                   f'<div style="position:absolute;left:612px;top:30px;width:120px;height:124px;background:url({A("01_identidade/ID-004_monograma_LMD.png")}) center/contain no-repeat"></div>'
                   f'<div style="position:absolute;left:740px;top:30px;width:120px;height:124px;background:url({A("01_identidade/ID-002_emblema_isolado.png")}) center/contain no-repeat"></div>'))
    b.append(panel(568, 176, 872, 124, "", None, extra='<ul class="b" style="position:absolute;left:24px;top:22px;columns:3;column-gap:30px">'
                   + "".join(f"<li>{t}</li>" for t in ["Poder.", "Aresta.", "Consequência.", "Liberdade.", "O fim dos deuses.", "Uma saga sobre poder,",
                                                         "consequências e o preço", "de desafiar o divino."]) + "</ul>"))
    capas = [("07_capas/CA-001_capa_vol1_o_deus_que_caiu_do_ceu.png"), ("07_capas/CA-002_capa_vol2_o_preco_da_imortalidade.png"),
             ("07_capas/CA-003_capa_vol3_a_guerra_das_coroas.png"), ("07_capas/CA-004_capa_vol4_a_ultima_sentenca.png")]
    cv = "".join(f'<div style="position:absolute;left:{14 + k * 172}px;top:30px;width:160px;height:240px;background:url({A(c)}) center/cover;'
                 f'box-shadow:0 10px 22px #000,0 0 0 1px #4a3c24"></div>' for k, c in enumerate(capas))
    b.append(panel(8, 308, 708, 282, "Capas da saga", None, extra=cv))
    b.append(panel(724, 308, 282, 282, "Lombadas e conjunto", A("07_capas/CA-005_lombadas_conjunto.png"), "56% center"))
    b.append(panel(1014, 308, 426, 282, "Edição de colecionador", A("07_capas/CA-006_caixa_colecionador.png"), "40% center",
                   extra='<div class="img fade-l"></div><ul class="b" style="position:absolute;right:14px;top:40px;z-index:4;text-align:left">'
                         + "".join(f"<li>{t}</li>" for t in ["Caixa rígida com arte exclusiva", "Quatro volumes", "Arte nas laterais", "Fitas marcadoras",
                                                               "Mapa exclusivo", "Medalhão de coleção", "Selo em cera", "Marcadores de facção", "Pôster"]) + "</ul>"))
    b.append(panel(8, 598, 560, 250, "Páginas internas", A("08_editorial/ED-001_livro_aberto_capitulo1.png"), "center 50%"))
    b.append(panel(576, 598, 470, 250, "Elementos editoriais", A("08_editorial/ED-002_elementos_editoriais.png")))
    b.append(panel(1054, 598, 386, 250, "Marcadores de capítulo", A("04_objetos/OB-005_marcadores_de_capitulo.png"), "center 55%"))
    b.append(panel(8, 856, 400, 222, "Estandartes das facções", A("04_objetos/OB-004_estandartes.png"), "12% 40%"))
    b.append(panel(416, 856, 350, 222, "Artefatos de coleção", A("04_objetos/OB-007_artefatos_de_colecao.png"), "center 60%",
                   labels(6, 196, 338, [("Medalhão da saga", ""), ("Selo em cera", ""), ("Anel da Aresta", "")], 20)))
    b.append(panel(774, 856, 300, 222, "Fragmento de mapa", A("05_mundo/MU-010_mapa_de_aresta_conceitual.png"), "35% 40%"))
    b.append(panel(1082, 856, 358, 222, "Apresentação completa", A("07_capas/CA-007_apresentacao_completa.png")))
    return shot("PR-02_aplicacoes_do_titulo", "".join(b))

# ------------------------------------------------------------------ 3. engenharia arcana
def prancha_3():
    b = []
    b.append(panel(0, 0, 1448, 140, img=A("05_mundo/MU-008_a_confluencia.png"), pos="center 45%",
                   extra='<div class="img" style="background:rgba(9,8,7,.55)"></div>'
                         f'<div style="position:absolute;left:574px;top:4px;width:300px;height:86px;background:url({A("01_identidade/ID-006_lettering_transparente.png")}) center/contain no-repeat;z-index:4"></div>'
                         '<div class="h1" style="position:absolute;left:0;right:0;top:92px;text-align:center;font-size:22px;letter-spacing:9px;z-index:4">ENGENHARIA ARCANA</div>'
                         '<div class="sc" style="position:absolute;left:0;right:0;top:120px;text-align:center;font-size:9.5px;letter-spacing:4px;z-index:4">Disciplina. Estrutura. Limite. Consequência.</div>'
                         '<div class="q" style="position:absolute;right:40px;top:40px;font-size:13.5px;z-index:4">A magia não é milagre.<br>É arquitetura.<br>E toda arquitetura obedece a leis.</div>'))
    b.append(panel(8, 148, 1150, 268, "As sete leis", A("02_simbolos/SI-001_sete_leis.png"), "center 45%", "Fundamentos imutáveis da realidade arcana",
                   labels(8, 216, 1134, LEIS_LONG, 46)))
    b.append(panel(1166, 148, 274, 268, "Registro das leis", A("09_engenharia_arcana/EA-001_registro_das_leis.png"), "center 40%"))
    b.append(panel(8, 424, 600, 288, "As seis disciplinas", A("02_simbolos/SI-002_seis_disciplinas.png"), "center 50%", "Formas de aplicação das leis",
                   labels(6, 250, 588, DISC, 34)))
    etapas = [("Fonte", "Origem da energia arcana."), ("Âncora", "Ponto de fixação e estabilidade."), ("Elo", "Conexão e transmissão."),
              ("Destino", "Onde a lei se aplica."), ("Controle", "Regula, limita e mantém."), ("Retorno", "Dissipação ou recirculação.")]
    b.append(panel(616, 424, 512, 288, "Estrutura de um feitiço", A("02_simbolos/SI-003_etapas_da_transposicao.png"), "center 48%", "Sequência universal",
                   labels(6, 214, 500, etapas, 60)))
    b.append(panel(1136, 424, 304, 288, "Fluxograma arcano", A("09_engenharia_arcana/EA-002_fluxograma_arcano.png"), "center 50%",
                   extra='<div style="position:absolute;left:10px;top:34px;bottom:12px;display:flex;flex-direction:column;justify-content:space-around;z-index:4">'
                         + "".join(f'<div class="sc" style="font-size:8.5px;background:rgba(0,0,0,.6);padding:2px 5px">{e}</div>' for e, _ in etapas) + "</div>"))
    b.append(panel(8, 720, 348, 190, "Materiais de âncora", A("09_engenharia_arcana/EA-005_materiais_de_ancora.png"), "", "Propriedades e aplicações"))
    b.append(panel(364, 720, 474, 190, "Instrumentos arcano-técnicos", A("09_engenharia_arcana/EA-004_instrumentos_arcano_tecnicos.png"), "", "Extensões da vontade",
                   labels(6, 170, 462, [("Bastão", ""), ("Círculo", ""), ("Orbe", ""), ("Selo", ""), ("Códice", ""), ("Matriz", "")], 16)))
    b.append(panel(846, 720, 594, 190, "Diagramas de circuitos", A("09_engenharia_arcana/EA-003_diagramas_de_circuitos.png"), "center 40%", "Exemplos de aplicação",
                   labels(6, 24, 582, [("Círculo de contenção", ""), ("Canal de transposição", ""), ("Feitiço de estrutura", "")], 16)))
    b.append(panel(8, 918, 330, 160, "Transposição", A("09_engenharia_arcana/EA-006_transposicao_portal.png"), "center 45%", "Deslocamento através das leis"))
    b.append(panel(346, 918, 400, 160, "Lógica de portais e limiar", A("05_mundo/MU-008_a_confluencia.png"), "center 30%", "",
                   '<div class="img fade-b"></div><div class="q" style="position:absolute;left:12px;right:12px;bottom:10px;font-size:11px;z-index:4">'
                   'O Limiar é a camada de transição entre realidades. Quanto maior a distância, maior a complexidade da âncora.</div>'))
    b.append(panel(754, 918, 230, 160, "Compatibilidade e dissipação", None, extra=
                   '<div style="position:absolute;left:12px;top:34px;right:12px">' + "".join(
                       f'<div style="display:flex;align-items:center;gap:8px;margin:7px 0"><span style="width:10px;height:10px;border-radius:50%;background:{c};box-shadow:0 0 8px {c}"></span>'
                       f'<span class="sc" style="font-size:8.5px;letter-spacing:1.4px;flex:1">{t}</span><span class="q" style="font-size:10px">{s}</span></div>'
                       for c, t, s in [("#4F8BD6", "Ressonância plena", "estável"), ("#C9A15A", "Ressonância parcial", "degradação"),
                                       ("#C8332F", "Ressonância conflitante", "distorção"), ("#7A1218", "Incompatível", "colapso")]) + "</div>"))
    b.append(panel(992, 918, 220, 160, "Interdição", A("09_engenharia_arcana/EA-007_interdicao_carrascos.png"), "center 40%", "Os Carrascos",
                   '<div class="img fade-b"></div><div class="q" style="position:absolute;left:10px;bottom:8px;font-size:10.5px;z-index:4">Onde os carrascos passam, a magia se cala.</div>'))
    b.append(panel(1220, 918, 220, 160, "Redes divinas e dracônicas", A("09_engenharia_arcana/EA-008_redes_divinas_draconicas.png"), "center 40%", "",
                   '<div class="img fade-b"></div><div class="q" style="position:absolute;left:10px;bottom:8px;font-size:10.5px;z-index:4">As mesmas leis. Outra escala.</div>'))
    return shot("PR-03_engenharia_arcana", "".join(b))

# ------------------------------------------------------------------ 4. Aresta — o mundo
def regiao(x, y, w, h, nome, sub, txt, img, pos="center"):
    return panel(x, y, w, h, "", A(img), pos, extra='<div class="img fade-b"></div><div class="img fade-r" style="opacity:.8"></div>'
                 f'<div style="position:absolute;left:16px;top:12px;z-index:4"><div class="h1" style="font-size:19px;letter-spacing:3px">{nome}</div>'
                 f'<div class="sc" style="font-size:8.5px;margin-top:3px">{sub}</div><div class="q" style="font-size:11.5px;margin-top:7px;max-width:{w * .5:.0f}px">{txt}</div></div>')

def prancha_4():
    b = []
    b.append(panel(0, 0, 1448, 96, img=A("05_mundo/MU-008_a_confluencia.png"), pos="center 55%",
                   extra='<div class="img fade-r"></div>'
                         f'<div style="position:absolute;left:14px;top:4px;width:250px;height:88px;background:url({A("01_identidade/ID-006_lettering_transparente.png")}) center/contain no-repeat;z-index:4"></div>'
                         '<ul class="b" style="position:absolute;left:300px;top:20px;z-index:4"><li>Um mundo ligado por portais,</li><li>marcado por deuses,</li><li>sustentado por escolhas.</li></ul>'
                         '<div class="sc" style="position:absolute;right:30px;top:62px;font-size:9px;z-index:4">Portais · Povos · Territórios · Memória · Consequências</div>'))
    b.append(regiao(8, 104, 462, 328, "Cidade de Limiar", "Capital · Portais · Lei", "Onde todos os caminhos se encontram. Limiar é a sede das Leis, dos portais e do equilíbrio precário entre deuses e povos.", "05_mundo/MU-001_cidade_de_limiar.png"))
    b.append(panel(478, 104, 492, 328, "", A("05_mundo/MU-010_mapa_de_aresta_conceitual.png"), "center", fit="cover",
                   extra='<div class="sc" style="position:absolute;left:0;right:0;bottom:6px;text-align:center;font-size:7.5px;z-index:4;color:#9C8A66">Cartografia conceitual · não canônica</div>'))
    b.append(regiao(978, 104, 462, 328, "Reinos do Norte", "Ferro · Tempestades · Resistência", "Terras de gelo e juramento. Povos que não se curvam, forjados na tempestade.", "05_mundo/MU-002_reinos_do_norte.png"))
    b.append(regiao(8, 440, 470, 230, "Delta e Arquivos", "Memória · Preservação · Saber", "Onde os rios guardam histórias. Água, registros e vozes que se recusam a se perder.", "05_mundo/MU-003_delta_e_arquivos.png"))
    b.append(regiao(486, 440, 470, 230, "Ilhas-Prisma", "Isolamento · Experimentação · Luz", "Arquipélago de luz e refração, onde ciência, arte e heresia se encontram.", "05_mundo/MU-004_ilhas_prisma.png"))
    b.append(regiao(964, 440, 476, 230, "Terras dos Dragões", "Escama · Soberania · Tempo", "Montanhas onde os antigos ainda falam. Ruínas vivas e leis mais velhas que os deuses.", "05_mundo/MU-005_terras_dos_dragoes.png"))
    b.append(regiao(8, 678, 470, 224, "Cidades Livres", "Independência · Comércio · Pluralidade", "Cidades que escolhem a si mesmas. Mercados, ideias e povos unidos pela recusa ao domínio.", "05_mundo/MU-006_cidades_livres.png"))
    b.append(regiao(486, 678, 470, 224, "Interiores Sagrados", "Poder · Rito · Consequência", "Templos, arquivos e salões onde o divino e o humano se encontram.", "05_mundo/MU-007_interiores_sagrados.png"))
    b.append(regiao(964, 678, 476, 224, "Vhalessa", "Volume I · a cidade gelada", "Fornalha Velha, vinte e dois graus abaixo de zero. Das sete chaminés, só duas soltam fumaça.", "05_mundo/MU-009_vhalessa_fornalha_velha_noite.png"))
    b.append(regiao(8, 910, 880, 168, "A Confluência", "O mundo em movimento", "No centro de Aresta, as rotas se encontram. Portal, corrente, equilíbrio e risco: é o que liga e o que pode fazer tudo ruir.", "05_mundo/MU-008_a_confluencia.png", "center 40%"))
    b.append(panel(896, 910, 544, 168, "Atmosfera de Aresta", A("09_engenharia_arcana/EA-008_redes_divinas_draconicas.png"), "center 40%",
                   extra='<div class="img fade-b"></div><div class="q" style="position:absolute;left:12px;bottom:8px;font-size:11px;z-index:4">Mundos diversos. Um mesmo céu. Leis que atravessam. Deuses que ainda sangram.</div>'))
    return shot("PR-04_aresta_o_mundo", "".join(b))

# ------------------------------------------------------------------ 5. personagens principais
PERS = {
    "ilan": ("Ilan Varek", "O último carrasco", "Humano · 34 anos<br>Mercenário · Veterano<br>Execução · Consequência",
             "Último Carrasco conhecido. Especialista em transformar leis em consequências. Pragmático, afiado, perigoso. Humor seco.",
             "Deuses também sangram. A diferença é que alguém precisa lembrar das consequências.", ["#2B2D31", "#4A4B4F", "#C8B79A", "#6B5A47", "#8E1B22"]),
    "aurelia": ("Aurelia", "A original dos limiares", "Deusa · Atemporal<br>Soberana dos Limiares<br>Inteligência · Autonomia",
                "Uma das deusas originais. Senhora dos Limiares, portais e transições. Elegante, poderosa e implacável quando necessário.",
                "Entre um mundo e outro, eu decido o que passa.", ["#E3C27A", "#EFE8DA", "#C9A15A", "#B07A3E", "#1E2C4A"]),
    "mara": ("Mara Quen", "Auditora dos pactos", "Humana · 32 anos · Jurista · Auditora",
             "Analisa pactos, coleta provas e mantém a memória do que foi acordado. Rígida, perspicaz e implacável com contradições.",
             "Sem prova, não há lei. Sem memória, tudo se repete.", ["#3A3A3A", "#EFE8DA", "#5E1B17", "#C9A15A", "#8E1B22"]),
    "nara": ("Nara Voss", "Engenheira de âncoras", "Humana · 29 anos · Construtora · Arquiteta",
             "Projeta, constrói e mantém as âncoras que sustentam portais. Prática, brilhante e teimosa. Acredita em soluções, não em milagres.",
             "Alguém precisa construir o que outros apenas invocam.", ["#6E6E6E", "#3B2F26", "#2E5DA8", "#B4532A", "#8E1B22"]),
    "sevran": ("Sevran", "O ex-sacerdote", "Humano · 45 anos · Memória institucional",
               "Carrega a memória das instituições e de tudo que já caiu. Irônico, compassivo e perigosamente esperançoso.",
               "Até deuses caem. E alguém precisa cuidar dos que ficam.", ["#3B2F26", "#6B3B2A", "#EFE8DA", "#C9C2B3", "#2F4A3A"]),
}
def ficha(x, y, w, h, key, img, big=False, flip=False, vpos="22%", fit="cover"):
    n, r, dados, txt, quote, pal = PERS[key]
    chips = "".join(f'<span style="display:inline-block;width:20px;height:14px;background:{c};margin-right:3px;border:1px solid #5a4a2e"></span>' for c in pal)
    side = "right" if not flip else "left"
    ipos = "left" if not flip else "right"
    fade = "fade-l" if not flip else "fade-r"
    tw = w * (0.46 if big else 0.5)
    return panel(x, y, w, h, "", A(img), f"{ipos} {vpos}", fit=fit, extra=
                 f'<div class="img {fade}"></div><div style="position:absolute;{side}:16px;top:14px;width:{tw:.0f}px;z-index:4">'
                 f'<div class="h1" style="font-size:{30 if big else 21}px;letter-spacing:3px">{n.upper()}</div>'
                 f'<div class="sc" style="font-size:{11 if big else 9}px;margin:3px 0 9px">{r}</div>'
                 f'<div class="sc" style="font-size:8.5px;color:#D9CDB4;line-height:1.6">{dados}</div>'
                 f'<div class="q" style="font-size:{12.5 if big else 11}px;margin-top:9px">{txt}</div>'
                 f'<div class="q" style="font-size:{12.5 if big else 11}px;margin-top:9px;color:#E2C47E">“{quote}”</div>'
                 f'<div class="sc" style="font-size:8px;margin-top:10px">Paleta</div><div style="margin-top:4px">{chips}</div></div>')

def prancha_5():
    b = []
    b.append(ficha(8, 8, 572, 470, "ilan", "06_personagens/PE-001_ilan_varek_retrato.png", True))
    b.append(panel(588, 8, 272, 470, "", None, extra=
                   '<div class="sc" style="position:absolute;left:0;right:0;top:12px;text-align:center;font-size:10px;z-index:4">Personagens principais</div>'
                   f'<div style="position:absolute;left:14px;right:14px;top:34px;bottom:70px;background:url({A("01_identidade/ID-007_logo_vertical_transparente.png")}) center/contain no-repeat"></div>'
                   '<div class="sc" style="position:absolute;left:0;right:0;bottom:16px;text-align:center;font-size:8.5px;line-height:1.7">Portais · Leis · Povos<br>Deuses · Consequências</div>'))
    b.append(ficha(868, 8, 572, 470, "aurelia", "06_personagens/PE-012_aurelia_dourada_retrato.png", True, flip=True))
    b.append(ficha(8, 486, 472, 340, "mara", "06_personagens/PE-003_mara_quen_retrato.png"))
    b.append(ficha(488, 486, 472, 340, "nara", "06_personagens/PE-028_nara_voss_ponte_da_cidade.png", vpos="4%", fit="auto 140%;background-repeat:no-repeat"))
    b.append(ficha(968, 486, 472, 340, "sevran", "06_personagens/PE-005_sevran_retrato.png"))
    b.append(panel(8, 834, 470, 244, "Silhuetas e posturas", A("06_personagens/PE-007_silhuetas_elenco.png"), "center 60%", "",
                   labels(4, 220, 462, [("Ilan", ""), ("Aurelia", ""), ("Mara", ""), ("Nara", ""), ("Sevran", "")], 18)))
    b.append(panel(486, 834, 586, 244, "Dinâmica do grupo", A("06_personagens/PE-006_dinamica_do_grupo.png"), "center 45%", "",
                   labels(6, 214, 574, [("A memória", ""), ("A estrutura", ""), ("A lei que executa", ""), ("A força que abre caminhos", ""), ("A prova", "")], 24)))
    b.append(panel(1080, 834, 360, 244, "Objetos simbólicos", A("04_objetos/OB-007_artefatos_de_colecao.png"), "center 55%", "Em conjunto"))
    return shot("PR-05_personagens_principais", "".join(b))

# ------------------------------------------------------------------ 6. identidade da saga
PALETA = [("#0B0B0C", "Obsidiana"), ("#7A1218", "Sangue"), ("#E6DCC6", "Osso"), ("#A8823E", "Ouro antigo"), ("#5C6168", "Aresta"),
          ("#1E3A5C", "Céu de Limiar"), ("#1F3A32", "Floresta sombria")]
def prancha_6():
    b = []
    b.append(panel(0, 0, 600, 300, img=A("05_mundo/MU-001_cidade_de_limiar.png"), pos="center 40%",
                   extra='<div class="img fade-r"></div>'
                         f'<div style="position:absolute;left:18px;top:14px;width:250px;height:120px;background:url({A("01_identidade/ID-006_lettering_transparente.png")}) center/contain no-repeat;z-index:4"></div>'
                         '<div class="q" style="position:absolute;left:24px;top:150px;font-size:14px;z-index:4">Em Aresta,<br>lei não é proteção.<br>É limite. É consequência.<br>'
                         'E é o que mantém o mundo de pé,<br>mesmo quando os deuses caem.</div>'))
    b.append(logo_center(600, 0, 300, 470))
    b.append(panel(908, 8, 532, 286, "Variações do logo", None, extra="".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:url({A(f)}) {p}/{s} no-repeat"></div>'
        f'<div class="sc" style="position:absolute;left:{x}px;top:{y + h + 2}px;width:{w}px;text-align:center;font-size:7.5px">{lab}</div>'
        for x, y, w, h, f, p, s, lab in [(14, 30, 170, 100, "01_identidade/ID-001_logo_principal_vertical.png", "center 86%", "170px auto", "Logo principal"),
                                         (192, 30, 200, 100, "01_identidade/ID-003_logo_horizontal.png", "center", "cover", "Logo horizontal"),
                                         (400, 30, 118, 100, "01_identidade/ID-004_monograma_LMD.png", "center", "contain", "Monograma"),
                                         (14, 158, 150, 108, "01_identidade/ID-002_emblema_isolado.png", "center", "contain", "Emblema"),
                                         (172, 158, 220, 108, "01_identidade/ID-003_logo_horizontal.png", "70% center", "cover", "Logo tipográfico"),
                                         (400, 158, 118, 108, "01_identidade/ID-005_selo_de_serie.png", "center", "contain", "Selo de série")])))
    b.append(panel(8, 308, 600, 200, "As sete leis da Transposição", A("02_simbolos/SI-001_sete_leis.png"), "center 38%", "", labels(6, 150, 588, [(a.replace(" · ", "<br>"), b) for a, b in LEIS], 46)))
    b.append(panel(908, 302, 532, 200, "As seis disciplinas da Transposição", A("02_simbolos/SI-002_seis_disciplinas.png"), "center 30%", "", labels(6, 166, 520, DISC, 30)))
    b.append(regiao(8, 516, 880, 170, "Aresta", "Um mundo entre limiares", "Cidades livres. Portais. Dragões. Coroas. Leis. Povos. Deuses. Consequências.", "05_mundo/MU-008_a_confluencia.png", "center 45%"))
    b.append(panel(896, 510, 260, 176, "Jurisprudência também é poder", A("05_mundo/MU-007_interiores_sagrados.png"), "center 45%"))
    b.append(panel(1164, 510, 276, 176, "A promessa da saga", None, extra='<ul class="b" style="position:absolute;left:12px;top:34px">' + "".join(
        f"<li>{t}</li>" for t in ["Fantasia épica com identidade original", "Leis como base da magia", "Política, guerras e consequências reais",
                                  "Personagens em conflito com deuses e com a lei", "Um mundo vivo, entre portais e dragões", "Moralidade ambígua, escolhas com peso"]) + "</ul>"))
    locs = [("Cidade de Limiar", "05_mundo/MU-001_cidade_de_limiar.png"), ("Reinos do Norte", "05_mundo/MU-002_reinos_do_norte.png"),
            ("Delta e Arquivos", "05_mundo/MU-003_delta_e_arquivos.png"), ("Ilhas-Prisma", "05_mundo/MU-004_ilhas_prisma.png"),
            ("Cidades Livres", "05_mundo/MU-006_cidades_livres.png"), ("Terras dos Dragões", "05_mundo/MU-005_terras_dos_dragoes.png")]
    b.append(panel(8, 694, 880, 150, "Locais e atmosfera", None, extra="".join(
        f'<div style="position:absolute;left:{10 + k * 145}px;top:28px;width:139px;height:96px;background:url({A(f)}) center/cover;border:1px solid #4a3c24"></div>'
        f'<div class="sc" style="position:absolute;left:{10 + k * 145}px;top:128px;width:139px;text-align:center;font-size:7.5px">{n}</div>' for k, (n, f) in enumerate(locs))))
    b.append(panel(896, 694, 544, 150, "Personagens centrais", None, extra=
                   f'<div style="position:absolute;left:10px;top:28px;width:258px;height:114px;background:url({A("06_personagens/PE-001_ilan_varek_retrato.png")}) center 18%/cover"></div>'
                   f'<div style="position:absolute;left:276px;top:28px;width:258px;height:114px;background:url({A("06_personagens/PE-012_aurelia_dourada_retrato.png")}) center 18%/cover"></div>'
                   '<div class="h1" style="position:absolute;left:18px;top:118px;font-size:12px;z-index:4">ILAN VAREK</div>'
                   '<div class="h1" style="position:absolute;left:284px;top:118px;font-size:12px;z-index:4">AURELIA</div>'))
    b.append(panel(8, 852, 300, 226, "Facções e símbolos", A("03_faccoes/FA-001_seis_faccoes.png"), "0% 30%", fit="auto 230%"))
    b.append(panel(316, 852, 220, 226, "Os dragões", A("05_mundo/MU-005_terras_dos_dragoes.png"), "18% 30%",
                   extra='<div class="img fade-b"></div><div class="q" style="position:absolute;left:10px;bottom:8px;font-size:10.5px;z-index:4">Onde há poder, há dragões. E onde há dragões, a lei hesita.</div>'))
    b.append(panel(544, 852, 344, 106, "Paleta de cores", None, extra="".join(
        f'<div style="position:absolute;left:{10 + k * 47}px;top:30px;width:42px;height:44px;background:{c};border:1px solid #5a4a2e"></div>'
        f'<div class="sc" style="position:absolute;left:{6 + k * 47}px;top:78px;width:50px;text-align:center;font-size:6.2px;letter-spacing:.6px">{n}</div>' for k, (c, n) in enumerate(PALETA))))
    b.append(panel(544, 966, 344, 112, "Texturas e materiais", A("08_editorial/ED-003_texturas_e_materiais.png")))
    b.append(panel(896, 852, 270, 226, "Elementos gráficos", A("08_editorial/ED-002_elementos_editoriais.png"), "center 70%"))
    b.append(panel(1174, 852, 266, 108, "Aplicações", A("07_capas/CA-007_apresentacao_completa.png")))
    b.append(panel(1174, 968, 266, 110, "Mapa (detalhe)", A("05_mundo/MU-010_mapa_de_aresta_conceitual.png"), "20% 30%", fit="200%"))
    return shot("PR-06_identidade_da_saga", "".join(b))

# ------------------------------------------------------------------ 7. extra: kit de lançamento
def prancha_7():
    b = []
    b.append(panel(8, 8, 420, 620, "Pôster cinematográfico", A("10_promocional/PR-001_poster_cinematografico.png"), fit="cover"))
    b.append(panel(436, 8, 400, 400, "Post de lançamento", A("10_promocional/PR-002_post_lancamento_quadrado.png")))
    b.append(panel(844, 8, 596, 400, "Capa do Volume I", None, extra=
                   f'<div style="position:absolute;left:20px;top:34px;width:240px;height:356px;background:url({A("07_capas/CA-001_capa_vol1_o_deus_que_caiu_do_ceu.png")}) center/cover;box-shadow:0 12px 30px #000"></div>'
                   f'<div style="position:absolute;left:280px;top:34px;width:300px;height:356px;background:url({A("07_capas/CA-006_caixa_colecionador.png")}) 30% center/cover"></div>'))
    b.append(panel(436, 416, 1004, 212, "Marcadores e brindes", A("04_objetos/OB-005_marcadores_de_capitulo.png"), "center 50%"))
    b.append(panel(8, 636, 716, 442, "Banner de site · capa de redes", A("05_mundo/MU-001_cidade_de_limiar.png"), "center 40%", extra=
                   '<div class="img fade-r"></div>'
                   f'<div style="position:absolute;left:28px;top:60px;width:320px;height:200px;background:url({A("01_identidade/ID-006_lettering_transparente.png")}) center/contain no-repeat;z-index:4"></div>'
                   '<div class="q" style="position:absolute;left:34px;top:280px;font-size:18px;z-index:4">Volume I · O Deus que Caiu do Céu</div>'
                   '<div class="sc" style="position:absolute;left:34px;top:318px;font-size:11px;z-index:4">Werik Martins</div>'))
    b.append(panel(732, 636, 708, 442, "Selos, lacres e medalhões", A("04_objetos/OB-001_selos_de_cera.png"), "center 50%"))
    return shot("PR-07_extra_kit_de_lancamento", "".join(b))

if __name__ == "__main__":
    import sys
    fns = [prancha_1, prancha_2, prancha_3, prancha_4, prancha_5, prancha_6, prancha_7]
    sel = [int(a) for a in sys.argv[1:]] or range(1, 8)
    for i in sel:
        print(fns[i - 1]())
