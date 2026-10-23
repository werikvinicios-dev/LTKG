#!/usr/bin/env python3
"""Edição Digital Imersiva — Leis para Matar Deuses, Volume 1 (V2).
Monta o livro inteiro (capa, atlas, páginas do mundo, seis partes, 31 capítulos ilustrados, Codex) em PDF digital.
Duas passagens: a primeira acha as páginas de cada capítulo; a segunda escreve o sumário com os números.
Uso: python3 build/edicao/montar_edicao.py"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from motor import *
from especiais import leis, disciplinas, gramatica_selo, arquitetura, CSS_ESP
from armorial import armorial, CSS_ARM
from mapas import planta_vhalessa, mapa_norte, mapa_aresta, pagina_mapa, legenda_vhalessa, CSS_MAPA

V2 = f"{ROOT}/manuscrito/V2"
E = "exportacoes/banco_de_arte/11_edicao"
DR = "exportacoes/acervo_drive"
BA = "exportacoes/banco_de_arte"
B4 = "exportacoes/banco_de_arte_4x/06_personagens"
SAIDA = f"{ROOT}/exportacoes/edicao_imersiva/Leis_para_Matar_Deuses_Vol1_Edicao_Imersiva.pdf"
PLANO = {c["cap"]: c for c in json.load(open(f"{B}/plano.json", encoding="utf-8"))}

PARTES = [("I", "A Noite Mais Longa", 1, 5, "Nada se cria. Tudo muda de lugar.", "Primeira Lei · Conservação", f"{DR}/cenarios/S01_Vhalessa_Inverno.png", "center"),
          ("II", "Custódia dos Mortos", 6, 10, "Sem ligação, nada passa.", "Segunda Lei · Vínculo", f"{DR}/producao_v2/P01_01.png", "center 30%"),
          ("III", "Livros-razão", 11, 17, "Tudo tem um tamanho.", "Sexta Lei · Capacidade", f"{DR}/producao_v2/S09_01.png", "center"),
          ("IV", "A Velha das Cristas", 18, 23, "Toda passagem tem um limite.", "Quarta Lei · Vazão", f"{DR}/producao_v2/D01_v2.png", "center"),
          ("V", "Fechamento de Contas", 24, 28, "Todo tranco volta para algum lugar.", "Sétima Lei · Retorno", f"{DR}/cenarios/S05_Passo_Cinzento.png", "center"),
          ("VI", "O Que Fica", 29, 31, "Nada fica para sempre.", "Quinta Lei · Dissipação", f"{DR}/producao_v2/CV01.png", "center")]

# por capítulo: abertura (retrato), bandas (no meio do texto, paisagem), finais (depois do capítulo)
ARTE = {
    1: (f"{BA}/05_mundo/MU-009_vhalessa_fornalha_velha_noite.png", [f"{DR}/cenarios/S04_Cozinha_do_Lento.png"], ["C01-a", "C01-c", "C01-b"]),
    2: ("C02-0", [], ["C02-2", "C02-3"]), 3: ("C03-0", ["C03-1"], ["C03-3"]), 4: ("C04-0", [], ["C04-1"]),
    5: ("C05-0", [], ["C05-2"]), 6: ("C06-0", [], ["C06-2"]), 7: (f"{DR}/producao_v2/S03.png", [], ["C07-1"]),
    8: ("C08-0", [], ["C08-3"]), 9: ("C09-0", [f"{DR}/producao_v2/S09_01.png"], ["C09-2"]), 10: ("C10-0", [], ["C10-1"]),
    11: ("C11-0", [], ["C11-2"]), 12: ("C12-0", ["C12-1"], ["C12-2"]), 13: ("C13-0", [], ["C13-1"]),
    14: ("C14-0", [], ["C14-2"]), 15: (f"{DR}/artefatos/A03_Martelo_de_Thor.png", ["C15-1"], ["C15-2"]),
    16: ("C16-0", [], ["C16-3"]), 17: ("C17-0", [], ["C17-2"]), 18: (f"{DR}/cenarios/D01_Velha_das_Cristas.png", ["C18-1"], ["C18-3"]),
    19: ("C19-0", [], ["C19-2"]), 20: ("C20-0", [], ["C20-2"]), 21: ("C21-1", [], ["C21-2"]), 22: ("C22-0", [], ["C22-4"]),
    23: ("C23-0", ["C23-2"], ["C23-1"]), 24: (f"{DR}/artefatos/A05_Maleta_de_Placas_Mara.png", ["C24-2"], ["C24-4"]),
    25: ("C25-0", ["C25-2"], ["C25-4"]), 26: ("C26-0", [], ["C26-1"]), 27: ("C27-0", ["C27-2"], ["C27-3"]),
    28: ("C28-0", [], ["C28-4"]), 29: ("C29-0", [], ["C29-1"]), 30: ("C30-0", [], ["C30-3"]), 31: ("C31-0", [], ["C31-1"]),
}
RESPIROS = [f"{DR}/cenarios/S01_Vhalessa_Inverno.png", f"{B4}/../06_personagens/PE-025_ilan_ponte_nevasca_4x.jpg", f"{BA}/05_mundo/MU-002_reinos_do_norte.png",
            f"{DR}/producao_v2/CV01.png", f"{DR}/producao_v2/D01.png", f"{BA}/05_mundo/MU-009_vhalessa_fornalha_velha_noite.png",
            f"{DR}/cenarios/S02_Atrio_da_Soleira.png", f"{DR}/producao_v2/P01_01.png", f"{BA}/05_mundo/MU-005_terras_dos_dragoes.png",
            f"{DR}/cenarios/S05_Passo_Cinzento.png", f"{BA}/06_personagens/PE-020_ilan_sete_chamines.png"]


def arq(k):
    return f"{E}/{k}.png" if re.match(r"^C\d\d-", k) else k


def dims(p):
    from PIL import Image
    return Image.open(p if os.path.isabs(p) else f"{ROOT}/{p}").size


def pagina_final(p):
    w, h = dims(p)
    if w > h:
        return pagina(f'<div class="bg" style="background-image:url({img(p, 2200)})"></div>', "img", nome="paisagem")
    return imagem_cheia(p)


# ------------------------------------------------------------------ texto: casar trechos do plano (V1) com parágrafos da V2
def palavras(t):
    return set(w for w in re.findall(r"[a-zà-ú]{4,}", t.lower()))


def achar_paragrafo(blocos, trecho, frac=None):
    alvo = palavras(trecho)
    melhor, idx = 0, None
    for i, b in enumerate(blocos):
        if b == "---":
            continue
        pb = palavras(b)
        if not pb:
            continue
        sc = len(alvo & pb) / (len(alvo) ** .5 * len(pb) ** .5 + 1e-9)
        if sc > melhor:
            melhor, idx = sc, i
    if idx is None or melhor < .12:
        idx = int(len(blocos) * (frac or .5))
    # entra depois do parágrafo, nunca colado numa quebra de cena
    return min(idx, len(blocos) - 2)


def doc_html(d):
    tipo = d.get("tipo", "carta")
    txt = re.sub(r"(?i)âncoras?", "selo", d.get("conteudo", "")).strip()
    linhas = [l.strip() for l in re.split(r"\n+|(?<=\.) (?=[A-ZÁÉÍÓÚ][a-zà-ú]+:)", txt) if l.strip()]
    titulo = {"contrato": "Contrato", "carta": "", "aviso": "Aviso", "livro-razão": "Livro-razão", "relatório": "Relatório",
              "recibo": "Recibo", "bilhete": "", "cartaz": "", "mapa": ""}.get(tipo, "")
    corpo = "".join(f"<p>{inline(l)}</p>" for l in linhas)
    dt = f'<div class="dt">{esc(titulo)}</div>' if titulo else ""
    car = f'<div class="carimbo">{anel_svg(22, cor=CARMIM)}</div>' if tipo in ("contrato", "aviso", "relatório", "recibo", "carta") else ""
    classe = {"aviso": "aviso", "cartaz": "aviso", "livro-razão": "livro"}.get(tipo, tipo)
    return documento(dt + corpo + car, classe)


def titulo_curto(t, n=40):
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0] + "…"


def ler_capitulo(n):
    md = open(f"{V2}/{n:02d}.md", encoding="utf-8").read().strip()
    cab, corpo = md.split("\n", 1)
    m = re.match(r"#\s*(Capítulo\s+(\d+)|Epílogo)\s*—\s*(.+)", cab)
    rot = "Epílogo" if cab.startswith("# Epílogo") else "Capítulo"
    return rot, m.group(3).strip(), corpo


def capitulo(n):
    rot, titulo, corpo = ler_capitulo(n)
    pl = PLANO.get(n, {})
    abertura, bandas, finais = ARTE[n]
    blocos = [b.strip() for b in corpo.strip().split("\n\n") if b.strip()]
    ins = {}
    # bandas: no trecho do plano marcado como dupla/spot, ou espalhadas
    alvos = [i for i in pl.get("ilustracoes", []) if i["tipo"] in ("dupla", "spot")]
    for k, b in enumerate(bandas):
        tr = alvos[k]["trecho_ancora"] if k < len(alvos) else ""
        i = achar_paragrafo(blocos, tr, .45 + .2 * k)
        ins.setdefault(i, "")
        ins[i] += banda(arq(b), "center", 74)
    for d in pl.get("documentos_do_mundo", [])[:2]:
        i = achar_paragrafo(blocos, d.get("onde_entra", ""), .3)
        ins.setdefault(i, "")
        ins[i] += doc_html(d)
    epi = pl.get("epigrafe_sugerida") or None
    pecas = [abertura_capitulo(n if rot == "Capítulo" else None, titulo, arq(abertura), "center", None, epi, rot)]
    pecas.append(capitulo_texto(n, titulo_curto(titulo), corpo, ins))
    pecas += [pagina_final(arq(f)) for f in finais]
    q = pl.get("citacao_respiro")
    if q:
        pecas.append(respiro(RESPIROS[(n - 1) % len(RESPIROS)], q, autor=f"{rot} {n}" if rot == "Capítulo" else "Epílogo"))
    return pecas, (n, titulo_curto(titulo).replace('"', "'"))


# ------------------------------------------------------------------ páginas de abertura e de fecho
def folha_rosto():
    return pagina(f'''<div class="rosto">{anel_svg(30)}<div class="r1">Leis para<br>Matar Deuses</div>{ornamento()}
<div class="r2">Volume I</div><div class="r3">O Deus que Caiu do Céu</div><div class="r4">Werik Martins</div>
<div class="selar">LEIS PARA MATAR DEUSES</div></div>''', "noite")


def falsa_rosto():
    return pagina(f'<div class="rosto"><div class="r1" style="font-size:20pt">Leis para Matar Deuses</div>{ornamento()}</div>', "noite")


def creditos():
    return pagina('''<div class="cred"><p><b>Leis para Matar Deuses</b><br>Volume I · O Deus que Caiu do Céu</p>
<p>© Werik Martins. Todos os direitos reservados.</p>
<p>Edição Digital Imersiva, outubro de 2026.<br>Texto da segunda versão (V2).</p>
<p>Tipografia: Aresta Titular e Selar, criadas para esta edição (Aresta Titular deriva da Cinzel, SIL Open Font License);
EB Garamond e IM Fell, SIL Open Font License.</p>
<p>Ilustrações, mapas, brasões e símbolos: acervo visual de <i>Leis para Matar Deuses</i>.</p>
<p class="aviso18">Fantasia para adultos. Contém violência, morte, linguagem forte e cenas de sexo.</p></div>''', "claro")


def epigrafe_livro():
    return pagina('''<div class="epi"><p>Poder é saber controlar transferências.<br>Sabedoria é saber quando, por que<br>e a serviço de quem fazê-lo.</p>
<div class="quem">Máxima dos Carrascos</div></div>''', "noite")


def sumario(paginas):
    linhas = []
    for num, tit, c0, c1, *_ in PARTES:
        linhas.append(f'<div class="sp">Parte {num} · {esc(tit)}</div>')
        for n in range(c0, c1 + 1):
            rot, t, _ = ler_capitulo(n)
            pg = paginas.get(n, "")
            lab = f"{n}" if rot == "Capítulo" else "Ep."
            linhas.append(f'<div class="sl"><span class="sn">{lab}</span><span class="st">{esc(t)}</span><span class="sd"></span><span class="sg">{pg}</span></div>')
    meio = len(linhas) // 2 + 2
    return (pagina(f'<div class="sum"><div class="et">Sumário</div>{ornamento()}{"".join(linhas[:meio])}</div>', "claro") +
            pagina(f'<div class="sum">{"".join(linhas[meio:])}</div>', "claro"))


ELENCO = [("Ilan Varek", f"{B4}/PE-001_ilan_varek_retrato_4x.jpg", "Trinta e quatro anos, alto, cansado e bom de conta. Desliga reservatórios, conserta problemas e não ganha por cabeça. Usa uma manopla de três células no braço esquerdo."),
          ("Aurelia", f"{B4}/PE-012_aurelia_dourada_retrato_4x.jpg", "Senhora dos Limiares. Deusa das portas, das passagens e das tarifas. Tem mais de mil anos e um senso de humor que não pediu licença a ninguém."),
          ("Mara Quen", f"{B4}/PE-003_mara_quen_retrato_4x.jpg", "Auditora da Câmara dos Pactos. Óculos redondos, colete cor de vinho e uma maleta de placas de vidro que medem o que ninguém quer medir."),
          ("Nara Voss", f"{BA}/06_personagens/PE-028_nara_voss_ponte_da_cidade.png", "Engenheira de selos do Cobre. Trança cor de cobre, óculos de latão na testa, mãos sempre ocupadas e paciência curta."),
          ("Sevran", f"{B4}/PE-005_sevran_retrato_4x.jpg", "Cozinheiro da Cozinha do Lento. Ex-sacerdote, alto e curvado, que escreve cartas para quem ninguém ouve.")]


def elenco():
    itens = "".join(f'<div class="el"><div class="eli" style="background-image:url({img(p, 900)})"></div><div><div class="eln">{esc(n)}</div>'
                    f'<div class="elt">{esc(t)}</div></div></div>' for n, p, t in ELENCO)
    return pagina(f'<div class="esp" style="justify-content:flex-start;padding-top:16mm"><div class="ek">Quem você vai conhecer</div><div class="et">O elenco</div>{ornamento()}'
                  f'<div class="elg">{itens}</div></div>', "noite")


def divisor(titulo, sub):
    return pagina(f'<div class="parte">{anel_svg(40)}<div class="ptit" style="margin-top:8mm">{esc(titulo)}</div>{ornamento()}'
                  f'<div class="pepi"><p>{esc(sub)}</p></div><div class="selar">CODEX DE ARESTA</div></div>', "noite")


def grade(titulo, itens, cols=2, alt=56):
    h = "".join(f'<div class="gi"><div class="gim" style="height:{alt}mm;background-image:url({img(p, 1100)})"></div>'
                f'<div class="gt">{esc(t)}</div><div class="gx">{esc(x)}</div></div>' for p, t, x in itens)
    return pagina(f'<div class="esp" style="justify-content:flex-start;padding-top:14mm"><div class="et" style="font-size:18pt">{esc(titulo)}</div>{ornamento()}'
                  f'<div class="gg" style="grid-template-columns:repeat({cols},1fr)">{h}</div></div>', "noite")


GLOSSARIO = [("Selo", "o ponto onde o vínculo se prende ao mundo. Conjurado (luz, segundos) ou gravado (forte, anos)."),
             ("Vínculo", "a ligação por onde algo passa: calor, movimento, luz, som, carga ou tensão."),
             ("Traço de terra", "a parte do selo que diz para onde vai o tranco. Sem ele, o tranco volta para quem fez."),
             ("Coroa", "a rede com que um deus segura o que governa: selos, mandato, sustento e identidade."),
             ("Brasa de parede", "placa de bronze com o selo da Casa da Fornalha; aquece as casas de Vhalessa de novembro a março."),
             ("Carrasco", "quem aprendeu a desmontar Coroas. A Ordem que os formava caiu há doze anos."),
             ("Dobra", "a moeda que paga contratos, sopas e células de cerâmica."),
             ("Manopla", "luva de couro e aço com células de cerâmica que guardam carga por pouco tempo."),
             ("Pulso, Brasa, Trama, Clarão, Eco, Carga", "as seis disciplinas: movimento, calor, estrutura, luz, vibração e eletricidade."),
             ("Jurisdição", "rede de selos gravados preparada num território. Ajuda muito; não acerta sozinha."),
             ("Átrio de Soleira", "o grande salão das portas de Aurelia, no outro extremo do continente."),
             ("Feira do Gelo", "a cidade de lonas que nasce todo inverno sobre o rio Lento, diante da Praça do Meio-Dia.")]


def glossario():
    h = "".join(f'<p><b>{esc(t)}.</b> {esc(x)}</p>' for t, x in GLOSSARIO)
    return pagina(f'<div class="glo"><div class="et">Glossário</div>{ornamento()}{h}</div>', "claro")


def colofao():
    return pagina(f'''<div class="rosto">{anel_svg(22)}<div class="cred" style="position:static;color:#D9CFB8;text-align:center;max-width:110mm">
<p>Esta edição foi composta em Aresta Titular, Selar e EB Garamond.</p><p>Os selos que você viu acender nestas páginas não criaram energia nenhuma.<br>Quem pagou a conta foi você, que leu até aqui.</p>
<p style="margin-top:8mm"><i>Leis para Matar Deuses continua em</i><br><b>O Preço da Imortalidade</b>.</p></div></div>''', "noite")


def contracapa():
    return pagina(f'''<div class="bg" style="background-image:url({img(f"{DR}/capas_e_marca/C02_Contracapa_Arte_Sem_Texto.png", 2000)})"></div><div class="veu"></div>
<div class="cc"><p>Ilan Varek, o último Carrasco conhecido de uma ordem extinta, chega a Vhalessa para um trabalho qualquer na véspera do inverno.
Na noite mais longa do ano, o deus que aquece a cidade cai da própria torre. Morto de um jeito que não deveria ser possível.</p>
<p>E o único jeito de fazer aquilo é o que Ilan sabe fazer.</p>{ornamento()}<div class="quem">Leis para Matar Deuses · Volume I</div></div>''', "img")


CSS_LIVRO = f"""
@page paisagem{{size:{H}mm {W}mm;margin:0}}
.pg[style*="page:paisagem"]{{width:{H}mm;height:{W}mm}}
.rosto{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:{MARFIM}}}
.r1{{font:700 30pt/1.05 AT;color:#E2C47E;letter-spacing:1.2mm;margin-top:6mm}} .r2{{font:400 10pt AT;letter-spacing:2.6mm;color:{OURO};text-transform:uppercase;margin-top:6mm}}
.r3{{font:italic 15pt EBG;color:#E6DCC6;margin-top:2mm}} .r4{{font:400 12pt AT;letter-spacing:2mm;margin-top:22mm;color:{MARFIM}}}
.cred{{position:absolute;left:22mm;right:22mm;bottom:26mm;font:9.2pt/1.5 EBG;color:#3A3128}} .cred p{{margin:0 0 3mm}}
.aviso18{{border-top:.3mm solid #9A8A6A;padding-top:3mm;font-style:italic}}
.epi{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 22mm}}
.epi p{{font:italic 15pt/1.5 EBG;color:#E6DCC6;margin:0}}
.sum{{position:absolute;inset:0;padding:20mm 18mm 18mm;color:#2A2420}} .sum .et{{text-align:center}}
.sp{{font:700 9pt AT;letter-spacing:1.4mm;color:{CARMIM};text-transform:uppercase;margin:5mm 0 1.6mm}}
.sl{{display:flex;align-items:baseline;font:10pt/1.5 EBG;margin:.4mm 0}} .sn{{font:700 8.5pt AT;color:#8A6E3A;width:9mm}}
.st{{flex:0 1 auto}} .sd{{flex:1;border-bottom:.25mm dotted #9A8A6A;margin:0 1.6mm;transform:translateY(-1mm)}} .sg{{font:9pt EBG;color:#6A5A3A}}
.elg{{display:flex;flex-direction:column;gap:4mm;margin-top:4mm;text-align:left}}
.el{{display:grid;grid-template-columns:30mm 1fr;gap:4mm;align-items:center}}
.eli{{height:30mm;background-size:cover;background-position:center 18%;border:.3mm solid #6B5532;border-radius:50%}}
.eln{{font:700 11pt AT;color:#E2C47E;letter-spacing:.5mm}} .elt{{font:9.6pt/1.38 EBG;color:#DCD2BC}}
.gg{{display:grid;gap:5mm 5mm;margin-top:4mm;text-align:left}} .gim{{background-size:cover;background-position:center 25%;border:.3mm solid #6B5532;border-radius:.6mm}}
.gt{{font:700 9.5pt AT;color:#E2C47E;margin-top:1.4mm}} .gx{{font:italic 8.6pt/1.3 EBG;color:#CFC4AC}}
.glo{{position:absolute;inset:0;padding:20mm 18mm;color:#2A2420}} .glo .et{{text-align:center}} .glo p{{font:10pt/1.45 EBG;margin:0 0 2.4mm}}
.cc{{position:absolute;left:18mm;right:18mm;bottom:22mm;text-align:center;color:#F1E8D4}} .cc p{{font:11.5pt/1.5 EBG;margin:0 0 3mm;text-shadow:0 0 3mm #000}}
.texto p{{hanging-punctuation:first}}
.capitular{{width:22mm;height:22mm}}
"""


def livro(paginas_caps):
    pecas, caps = [], []
    pecas.append(imagem_cheia("exportacoes/capa_v2/capa_ebook.jpg"))
    pecas.append(pagina_mapa(mapa_aresta()))
    pecas.append(falsa_rosto())
    pecas.append(imagem_cheia(f"{B4}/PE-019_ilan_e_aurelia_vhalessa_v2_4x.jpg", "center 30%"))
    pecas.append(folha_rosto()); pecas.append(creditos()); pecas.append(epigrafe_livro())
    pecas.append(sumario(paginas_caps))
    pecas.append(divisor("Atlas", "Aresta, o Norte e a cidade de Vhalessa."))
    pecas.append(pagina_mapa(mapa_norte())); pecas.append(pagina_mapa(planta_vhalessa()))
    ims = {1: f"{E}/C02-2.png", 2: f"{E}/C22-0.png", 3: f"{E}/C09-0.png", 4: f"{E}/C03-3.png", 5: f"{E}/C08-0.png", 6: f"{E}/C04-0.png",
           7: f"{E}/C15-2.png", 8: f"{E}/C15-1.png", 9: f"{E}/C02-0.png", 10: f"{BA}/05_mundo/MU-009_vhalessa_fornalha_velha_noite.png",
           11: f"{E}/C05-0.png", 12: f"{E}/C12-1.png", 13: f"{E}/C13-1.png", 14: f"{E}/C12-0.png"}
    pecas.append(legenda_vhalessa(ims))
    pecas.append(divisor("Antes de começar", "O que todo mundo em Aresta aprende criança, e quase todo mundo esquece."))
    pecas += [leis(), disciplinas(), gramatica_selo(), arquitetura(), elenco()]
    for num, tit, c0, c1, epi, fonte, im, pos in PARTES:
        pecas.append(abertura_parte(num, tit, epi, im, pos, fonte))
        for n in range(c0, c1 + 1):
            p, cab = capitulo(n)
            pecas += p; caps.append(cab)
    # Codex
    pecas.append(divisor("Codex de Aresta", "Galeria, arsenal, armorial e glossário. Leia depois do livro: aqui não há segredos guardados."))
    pecas.append(pagina_final(f"{DR}/producao_v2/F01.png")); pecas.append(pagina_final(f"{DR}/producao_v2/F02.png"))
    pecas.append(pagina_final(f"{DR}/producao_v2/F03.png")); pecas.append(pagina_final(f"{DR}/producao_v2/F04.png"))
    pecas.append(pagina_final(f"{DR}/producao_v2/F05.png"))
    pecas.append(grade("Em Vhalessa e além", [(f"{DR}/personagens/P07_Thor_Master.png", "Thor", "senhor do trovão dos Reinos da Tempestade"),
                                              (f"{DR}/personagens/P08_Anubis_Master.png", "Anúbis", "guardião da Necrópole do Poente"),
                                              (f"{DR}/personagens/P06_Cassia_Vale_Master.png", "Cassia Vale", "comissária da Câmara dos Pactos"),
                                              (f"{DR}/personagens/P09_Eron_Tahl_Master.png", "Eron Tahl", "a Linha Seca"),
                                              (f"{DR}/personagens/P11_Ithren_Master.png", "Mestre Ithren", "o homem de muitos rostos"),
                                              (f"{DR}/personagens/P10_Iolanthe_Ness_Master.png", "A velha mestra", "uma sala sobre um armazém, no oeste")], 3, 50))
    pecas.append(grade("Arsenal e artefatos", [(f"{DR}/artefatos/A01_Manopla_Esquerda_Tres_Celulas.png", "A manopla de Ilan", "couro, aço e três células de cerâmica"),
                                               (f"{DR}/artefatos/A02_Espada_de_Ilan.png", "A espada de Ilan", "ferro simples, guarda simples, bainha remendada"),
                                               (f"{DR}/artefatos/A03_Martelo_de_Thor.png", "O martelo de Thor", "cabo curto demais para o tamanho do dono"),
                                               (f"{DR}/artefatos/A04_Chave_e_Circlet_de_Aurelia.png", "A chave de bronze", "e o diadema da Senhora dos Limiares"),
                                               (f"{DR}/artefatos/A05_Maleta_de_Placas_Mara.png", "As placas de Mara", "vidro fino que mede o que passa"),
                                               (f"{DR}/artefatos/A06_Favo_Termico.png", "O favo térmico", "células de seis lados, cintas de bronze"),
                                               (f"{DR}/artefatos/A07_Fiel_Agulha_de_Bronze.png", "O fiel", "uma agulha de bronze, longa e fina"),
                                               (f"{BA}/01_identidade/ID-009_emblema_medalhao.png", "O emblema da saga", "a lâmina, a balança e o arco")], 2, 40))
    pecas += armorial()
    pecas.append(glossario()); pecas.append(colofao()); pecas.append(contracapa())
    return pecas, caps


def paginas_dos_capitulos(pdf):
    from pypdf import PdfReader
    r = PdfReader(pdf)
    achados = {}
    for i, p in enumerate(r.pages):
        t = p.extract_text() or ""
        m = re.search(r"Cap[íi]tulo\s*\n?\s*(\d+)\s*\n", t)
        if m and "Sumário" not in t:
            n = int(m.group(1))
            achados.setdefault(n, i + 1)
        if "Epílogo" in t and 31 not in achados and "Sumário" not in t and len(t) < 600:
            achados[31] = i + 1
    return achados


if __name__ == "__main__":
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    pecas, caps = livro({})
    css_extra = CSS_ESP + CSS_MAPA + CSS_LIVRO + CSS_ARM
    compor(pecas, caps, SAIDA, extra_css=css_extra)
    pg = paginas_dos_capitulos(SAIDA)
    pecas, caps = livro(pg)
    compor(pecas, caps, SAIDA, extra_css=css_extra)
    from pypdf import PdfReader
    print(SAIDA, len(PdfReader(SAIDA).pages), "páginas;", round(os.path.getsize(SAIDA) / 1e6, 1), "MB; capítulos em", pg)
