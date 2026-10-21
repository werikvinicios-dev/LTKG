#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pranchas de apresentação das três direções da identidade visual v2 (16:9).
Cada página é um HTML renderizado pelo Chromium (captura 2880×1620) e montado num único PDF.
Saída: exportacoes/identidade_v2/Identidade_visual_v2_tres_opcoes.pdf + PNGs das pranchas.
Uso: python3 pranchas.py [A B C]   (sem argumento: todas as opções disponíveis)"""
import os, sys, subprocess, html, math
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

ROOT = "/home/user/LTKG"
OUTD = f"{ROOT}/exportacoes/identidade_v2"
TMP = f"{ROOT}/build/_pranchas"
F = f"file://{ROOT}/build/fonts"
os.makedirs(TMP, exist_ok=True)
os.makedirs(f"{OUTD}/pranchas", exist_ok=True)

FONTS = {  # família CSS → arquivo
    "EBG": "EBGaramond-Regular.ttf", "EBGi": "EBGaramond-Italic.ttf", "EBGSC": "EBGaramondSC-Regular.ttf",
    "PFD": "PlayfairDisplay-Regular.ttf", "PFDi": "PlayfairDisplay-Italic.ttf", "PFDSC": "PlayfairDisplaySC-Regular.ttf",
    "PFDSCB": "PlayfairDisplaySC-Bold.ttf", "ITA": "Italiana-Regular.ttf", "JOSL": "JosefinSans-Light.ttf",
    "JOSB": "JosefinSans-SemiBold.ttf", "INS": "InstrumentSerif-Regular.ttf", "INSi": "InstrumentSerif-Italic.ttf",
    "MONO": "IBMPlexMono-Light.ttf", "MONOr": "IBMPlexMono-Regular.ttf", "MARC": "Marcellus-Regular.ttf",
}
FONTFACE = "".join(f"@font-face{{font-family:{k};src:url('{F}/{v}')}}" for k, v in FONTS.items())

LEIS = ["Conservação", "Vínculo", "Compatibilidade", "Vazão", "Dissipação", "Capacidade", "Retorno"]

# ------------------------------------------------------------------ dados de cada opção
OP = {}
OP["A"] = dict(
    letra="A", nome="Apólice", pasta="A_Apolice", suf="apolice", metal="bronze",
    lema="A lei impressa como dinheiro: impossível de falsificar.",
    conceito=("A magia do livro é contrato, tarifa e conservação. A Opção A trata o volume como um título de valor: "
              "o brasão vira a medalha de uma cédula, gravada em guilhochê de torno, com as sete leis em microtexto "
              "e o sol rachado em talho-doce. Luxo de banco central: vinho, bronze e papel apólice."),
    palavras=["gravura de segurança", "talho-doce", "microtexto", "guilhochê"],
    bg="#EEE5D0", fg="#3A1411", soft="#8B6F57", acc="#5E1B17", line="#C9B48E", dark="#2A0B09",
    paleta=[("#5E1B17", "Vinho apólice", "tecido, tinta principal"), ("#B07D45", "Bronze", "hot-stamping, foil"),
            ("#EEE5D0", "Papel apólice", "sobrecapa, miolo"), ("#1F3A32", "Verde-cédula", "princípios, acento"),
            ("#1B1714", "Tinta", "texto corrido")],
    tipos=[("PFDSCB", "Playfair Display SC Bold", "Título, numerais romanos", "MATAR DEUSES"),
           ("PFDi", "Playfair Display Italic", "Chamadas, títulos de capítulo", "Noite tropical"),
           ("EBG", "EB Garamond", "Texto corrido do miolo", "O contrato tinha onze páginas")],
    anat=[(18.3, 18.3, "Microtexto contínuo com as sete leis: num brasão de 9 cm, letras de 1,4 mm. De longe, é só um fio."),
          (83.5, 23.2, "Sete losangos interrompem o perlado de pontos: as sete leis, como no brasão da saga."),
          (12.6, 50.0, "Guilhochê de torno: duas fitas de 14 fios, 21 lóbulos (7 × 3), desenhadas por equação, não à mão."),
          (56.5, 47.0, "Sol de inverno em talho-doce: linhas de espessura variável modelam a esfera, como o retrato de uma cédula."),
          (42.5, 44.5, "A rachadura separa o disco; a metade de baixo escorrega alguns pontos."),
          (50.0, 13.4, "Espada vertical, ponta para baixo; lâmina com bisel hachurado."),
          (21.0, 54.0, "A guarda é a balança, e o prato esquerdo pesa mais.")],
    lombada=dict(bg="#5E1B17", ink="linear-gradient(100deg,#F3DDA8,#C99A57 30%,#8A5E2C 55%,#E8C88A)", fam="PFDSCB", fam2="PFDSC"),
    producao=["Tecido vinho (buckram ou linho tingido), hot-stamping bronze em dois tons",
              "Relevo seco (deboss) no anel de microtexto",
              "Corte pintado vinho com renda de torno em bronze (impressão de borda)",
              "Guarda em papel apólice marfim, 1 cor (vinho), 140 g",
              "Sobrecapa em papel de algodão, vinheta oval em duotone, numeração tipográfica"],
    ref=[("Guilhochê, talho-doce e espirógrafo (FontLab, 2026)", "https://blog.fontlab.com/2026/04/14/money-lace-guilloche-intaglio-spirograph/"),
         ("Máquina de guilhochê Kämpf, Bank of England (Science Museum Group)", "https://collection.sciencemuseumgroup.org.uk/search/object_type/turning-engine"),
         ("Guillochage (Breguet)", "https://www.breguet.com/en/guillochage")],
    motion=[(0.5, "o torno desenha o guilhochê"), (2.0, "o anel de microtexto gira e trava"), (3.0, "os sete losangos acendem"),
            (4.6, "a espada desce e o sol racha"), (5.8, "a balança pende para a esquerda"), (6.6, "o brilho do foil passa")],
    edge="apolice",
)
OP["B"] = dict(
    letra="B", nome="Limiar", pasta="B_Limiar", suf="limiar", metal="champanhe",
    lema="Cada lei é uma porta. O livro é o limiar.",
    conceito=("Art déco de 1925–1932: portas escalonadas, sunburst, simetria rigorosa. O brasão vira um portal; o sol "
              "de inverno nasce rachado atrás dele, a espada é o eixo da porta e a balança é o travessão. Meia-noite, "
              "champanhe e um toque de verdete."),
    palavras=["art déco", "portal escalonado", "sunburst", "geometria"],
    bg="#0E1626", fg="#EFE8DA", soft="#9C9479", acc="#D8C08A", line="#3B4660", dark="#070B14",
    paleta=[("#0E1626", "Meia-noite", "tecido, fundo"), ("#D8C08A", "Champanhe", "hot-stamping, foil"),
            ("#4E8C7E", "Verdete", "acento raro"), ("#EFE8DA", "Marfim", "miolo, sobrecapa"), ("#16213A", "Azul-noite", "segunda tinta")],
    tipos=[("ITA", "Italiana", "Título em versal espaçada", "MATAR DEUSES"),
           ("JOSL", "Josefin Sans Light", "Rótulos, numeração", "VOLUME I · O DEUS QUE CAIU DO CÉU"),
           ("EBG", "EB Garamond", "Texto corrido do miolo", "O contrato tinha onze páginas")],
    anat=[], producao=[], lombada=dict(bg="#0E1626", ink="linear-gradient(100deg,#F4E6C1,#C8A96A 35%,#8C6E3C 60%,#E9D39C)", fam="ITA", fam2="JOSL"), ref=[
        ("O Chrysler Building, símbolo do art déco (Dezeen, 2025)", "https://www.dezeen.com/2025/03/04/chrysler-building-art-deco-centenary/"),
        ("Art déco: chevrons, sunbursts e arcos (Smarthistory)", "https://smarthistory.org/?p=34666"),
        ("Pierre Legrain, encadernação déco (Masterworks)", "https://www.masterworks.com/academy/artists/pierre-legrain")],
    motion=[], edge="limiar",
)
OP["C"] = dict(
    letra="C", nome="Instrumento", pasta="C_Instrumento", suf="instrumento", metal="prata",
    lema="Um instrumento de precisão para aferir deuses.",
    conceito=("A magia do livro tem unidades, escalas e limites. A Opção C transforma o brasão num astrolábio: limbo "
              "graduado, rete com sete ponteiros-losango e o sol rachado como lente. Obsidiana, prata e um único ponto "
              "de iridescência."),
    palavras=["astrolábio", "escala graduada", "óptica", "diagrama técnico"],
    bg="#0B0C0E", fg="#E9ECEF", soft="#8E949C", acc="#C9CED6", line="#2A2E34", dark="#000000",
    paleta=[("#0B0C0E", "Obsidiana", "tecido, fundo"), ("#BFC4CB", "Prata", "hot-stamping, foil"),
            ("#B9975B", "Latão", "acento"), ("#29C3C9", "Iridescente", "só na lente"), ("#F2EFE8", "Papel", "miolo")],
    tipos=[("INS", "Instrument Serif", "Título, capítulos", "Matar Deuses"),
           ("MONO", "IBM Plex Mono", "Escalas, rótulos técnicos", "VOL. I · 360° · 07 LEIS"),
           ("EBG", "EB Garamond", "Texto corrido do miolo", "O contrato tinha onze páginas")],
    anat=[], producao=[], lombada=dict(bg="#0B0C0E", ink="linear-gradient(100deg,#FFFFFF,#BFC4CB 35%,#7B818A 60%,#E3E7EC)", fam="INS", fam2="MONO"), ref=[
        ("Componentes do astrolábio (Museo Galileo)", "https://catalogue.museogalileo.it/indepth/AstrolabeComponents.html"),
        ("Partes do astrolábio (History of Science Museum, Oxford)", "https://www.mhs.ox.ac.uk/students/03to04/Astrolabes/Starholder_parts.html"),
        ("Astrolábio de 1574 (British Museum)", "https://www.britishmuseum.org/collection/object/H_1855-1201-223")],
    motion=[], edge="instrumento",
)

# ------------------------------------------------------------------ cortes pintados (fore-edge) para o mockup
def edge_png(o, path, w=96, h=800):
    k = o["edge"]
    if k == "apolice":
        L = [f'<rect width="{w}" height="{h}" fill="#4F1713"/>']
        for j in range(8):
            L.append(f'<path d="{wave_band(-10, h + 10, w / 2, 26, 64, j * 2 * math.pi / 8, 2)}" transform="rotate(90 {w / 2} {w / 2})" fill="none" stroke="#C89A5C" stroke-width="0.8"/>')
        body = "".join(L)
    elif k == "limiar":
        L = [f'<rect width="{w}" height="{h}" fill="#0E1626"/>']
        for y in range(-40, h + 80, 80):
            for r in range(8, 60, 8):
                L.append(f'<path d="M{w / 2 - r},{y} A{r},{r} 0 0 1 {w / 2 + r},{y}" fill="none" stroke="#D8C08A" stroke-width="1.2"/>')
            L.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="#D8C08A" stroke-width="2"/>')
        body = "".join(L)
    else:
        L = [f'<rect width="{w}" height="{h}" fill="#101215"/>']
        for i in range(0, h, 6):
            ln = 34 if i % 60 == 0 else (22 if i % 30 == 0 else 12)
            L.append(f'<line x1="0" y1="{i}" x2="{ln}" y2="{i}" stroke="#C9CED6" stroke-width="1"/>')
        body = "".join(L)
    to_png(svg(w, h, body), path, w * 2)
    return path

# ------------------------------------------------------------------ html base
def page(o, n, total, titulo, corpo, extra_css=""):
    bg, fg, soft, acc, line = o["bg"], o["fg"], o["soft"], o["acc"], o["line"]
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
{FONTFACE}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:{bg};color:{fg};font-family:EBG}}
.top{{position:absolute;left:96px;right:96px;top:52px;display:flex;justify-content:space-between;font-family:EBGSC;
  font-size:17px;letter-spacing:4px;color:{soft};border-bottom:1px solid {line};padding-bottom:14px}}
.foot{{position:absolute;left:96px;right:96px;bottom:44px;display:flex;justify-content:space-between;font-family:EBGSC;
  font-size:15px;letter-spacing:3px;color:{soft}}}
h1{{font-family:EBGi;font-weight:400;font-size:54px;line-height:1.05;color:{fg}}}
.k{{font-family:EBGSC;font-size:17px;letter-spacing:4px;color:{acc}}}
p{{font-size:23px;line-height:1.42;color:{fg}}}
.soft{{color:{soft}}}
{extra_css}
</style></head><body>
<div class="top"><div>Leis para Matar Deuses · identidade visual · três direções</div><div>Opção {o['letra']} · {o['nome']}</div></div>
{corpo}
<div class="foot"><div>{html.escape(titulo)}</div><div>{n:02d} / {total:02d}</div></div>
</body></html>"""

def shot(html_text, name):
    hp = f"{TMP}/{name}.html"; pp = f"{TMP}/{name}.png"
    open(hp, "w", encoding="utf-8").write(html_text)
    subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--hide-scrollbars",
                    "--force-device-scale-factor=1.5", "--window-size=1920,1080", f"--screenshot={pp}", "file://" + hp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pp

def A(o, f):  # caminho absoluto de um arquivo da opção
    return f"{OUTD}/{o['pasta']}/{f}"

def book3d(o, front, edge, left, top, w=520, rot=-30, depth=None, sheen=True):
    h = w * 2300 / 1600; d = depth or w * 28 / 160
    return f"""<div style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;perspective:2600px">
 <div style="position:absolute;left:{-w * .1}px;top:{h - 20}px;width:{w * 1.35}px;height:70px;
   background:radial-gradient(ellipse at 45% 40%,rgba(0,0,0,.42),rgba(0,0,0,0) 68%);filter:blur(8px)"></div>
 <div style="position:absolute;inset:0;transform-style:preserve-3d;transform:rotateY({rot}deg) rotateX(3deg)">
  <div style="position:absolute;width:{w}px;height:{h}px;background:url({front}) center/cover;transform:translateZ({d / 2}px);
     box-shadow:inset 5px 0 9px rgba(0,0,0,.35)">{'<div style="position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,0) 30%,rgba(255,250,235,.16) 46%,rgba(255,255,255,0) 60%)"></div>' if sheen else ''}</div>
  <div style="position:absolute;width:{d}px;height:{h - 10}px;top:5px;left:{w - d / 2 - 4}px;background:url({edge}) center/100% 100%;
     transform:rotateY(90deg);box-shadow:inset 0 0 6px rgba(0,0,0,.4)"></div>
  <div style="position:absolute;width:{w}px;height:{d}px;top:{-d / 2}px;background:linear-gradient(#e9e1cf,#cfc4ad);transform:rotateX(90deg)"></div>
 </div></div>"""

def spine(o, left, top, length):
    """Lombada deitada (pé à esquerda, como na estante lida de lado), proporção 230 × 28 mm."""
    sp = o["lombada"]; t = length * 28 / 230
    ink = f"background:{sp['ink']};-webkit-background-clip:text;background-clip:text;color:transparent"
    em = emblem_png(o)
    return (f'<div style="position:absolute;left:{left}px;top:{top}px;width:{length}px;height:{t:.0f}px;background:{sp["bg"]};'
            f'box-shadow:0 16px 30px rgba(0,0,0,.35),inset 0 6px 10px rgba(255,255,255,.06),inset 0 -8px 12px rgba(0,0,0,.3);'
            f'display:flex;align-items:center;justify-content:space-between;padding:0 {t * .45:.0f}px">'
            f'<div style="font-family:{sp["fam2"]};font-size:{t * .16:.0f}px;letter-spacing:{t * .04:.1f}px;white-space:nowrap;{ink}">WERIK MARTINS</div>'
            f'<div style="font-family:{sp["fam"]};font-size:{t * .27:.0f}px;letter-spacing:{t * .05:.1f}px;white-space:nowrap;{ink}">LEIS PARA MATAR DEUSES</div>'
            f'<div style="display:flex;align-items:center;gap:{t * .3:.0f}px"><div style="font-family:{sp["fam"]};font-size:{t * .34:.0f}px;{ink}">I</div>'
            f'<img src="{em}" style="height:{t * .74:.0f}px"></div></div>')

def emblem_png(o):
    """Emblema em metal sobre transparente, para lombada (recorta o fundo da versão foil)."""
    p = f"{TMP}/emb_{o['suf']}_metal.png"
    if not os.path.exists(p):
        im = Image.open(emblem_bg(o)).convert("RGBA").resize((400, 400), Image.LANCZOS)
        bgc = im.getpixel((4, 4))[:3]
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                d = abs(r - bgc[0]) + abs(g - bgc[1]) + abs(b - bgc[2])
                if d < 60:
                    px[x, y] = (r, g, b, int(255 * d / 60))
        im.save(p)
    return p

def flat(img, left, top, w, shadow=True, extra=""):
    sh = "box-shadow:0 30px 60px rgba(0,0,0,.35),0 6px 14px rgba(0,0,0,.25);" if shadow else ""
    return f'<img src="{img}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{sh}{extra}">'

# ------------------------------------------------------------------ páginas de uma opção
def pages_for(o, start, total):
    out = []; n = start
    edge = edge_png(o, f"{TMP}/edge_{o['suf']}.png")
    pal = "".join(f'<div style="display:flex;align-items:center;gap:18px;margin-bottom:14px"><div style="width:58px;height:58px;'
                  f'background:{h};border:1px solid {o["line"]}"></div><div><div style="font-family:EBGSC;letter-spacing:2px;font-size:19px">'
                  f'{nm}</div><div class="soft" style="font-size:17px">{h} · {u}</div></div></div>' for h, nm, u in o["paleta"])
    kw = " · ".join(o["palavras"])
    # 1. herói
    corpo = (book3d(o, A(o, f"capa_tecido_{o['metal']}.png"), edge, 980, 150, 500, -32)
             + flat(A(o, f"sobrecapa_{o['suf']}.png"), 1500, 300, 330)
             + f"""<div style="position:absolute;left:96px;top:170px;width:760px">
  <div class="k">Opção {o['letra']}</div>
  <div style="font-family:EBGi;font-size:150px;line-height:1;margin:10px 0 18px;color:{o['acc']}">{o['nome']}</div>
  <h1 style="font-size:40px;margin-bottom:30px">{o['lema']}</h1>
  <p style="margin-bottom:34px">{o['conceito']}</p>
  <div class="k" style="color:{o['soft']}">{kw}</div></div>""")
    out.append(shot(page(o, n, total, "Conceito", corpo), f"{o['letra']}_{n:02d}")); n += 1
    # 2. emblema e anatomia
    em_bg = A(o, [f for f in sorted(os.listdir(f"{OUTD}/{o['pasta']}")) if f.startswith(f"emblema_{o['suf']}_") and f.endswith(".png")][0])
    em = A(o, f"emblema_{o['suf']}.png")
    dots = "".join(f'<div style="position:absolute;left:{x}%;top:{y}%;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;'
                   f'background:{o["bg"]};border:1.5px solid {o["acc"]};color:{o["acc"]};font-family:EBGSC;font-size:19px;'
                   f'display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 4px rgba(0,0,0,.12)">{i + 1}</div>'
                   for i, (x, y, _) in enumerate(o["anat"]))
    legend = "".join(f'<div style="display:flex;gap:20px;margin-bottom:20px"><div style="font-family:EBGSC;color:{o["acc"]};font-size:24px;'
                     f'width:24px">{i + 1}</div><p style="font-size:21px;line-height:1.36">{t}</p></div>' for i, (_, _, t) in enumerate(o["anat"]))
    corpo = (f'<div style="position:absolute;left:96px;top:130px;width:860px;height:860px;background:url({em_bg}) center/cover"></div>'
             f'<div style="position:absolute;left:96px;top:130px;width:860px;height:860px">{dots}</div>'
             f'<div style="position:absolute;left:1030px;top:150px;width:790px"><div class="k">O brasão</div>'
             f'<h1 style="margin:10px 0 34px">Anatomia do emblema</h1>{legend}</div>'
             f'<div style="position:absolute;left:1030px;bottom:110px;display:flex;gap:34px;align-items:flex-end">'
             f'<img src="{em}" style="width:130px;background:{o["bg"]}"><img src="{em}" style="width:64px"><img src="{em}" style="width:34px">'
             f'<div class="soft" style="font-size:17px;max-width:330px">Teste de redução: 45 mm, 22 mm e 12 mm (lombada, selo, ex-líbris).</div></div>')
    out.append(shot(page(o, n, total, "Emblema", corpo), f"{o['letra']}_{n:02d}")); n += 1
    # 3. logotipo, tipografia, paleta
    tipos = "".join(f'<div style="margin-bottom:30px"><div class="k" style="color:{o["soft"]}">{nm} · {role}</div>'
                    f'<div style="font-family:{fam};font-size:{60 if i == 0 else 40}px;line-height:1.15;margin-top:6px">{html.escape(s)}</div></div>'
                    for i, (fam, nm, role, s) in enumerate(o["tipos"]))
    corpo = (f'<div style="position:absolute;left:96px;top:150px;width:1060px;height:360px;background:url({A(o, "logotipo_" + o["suf"] + ".png")}) left center/contain no-repeat"></div>'
             f'<div style="position:absolute;left:96px;top:570px;width:1000px"><div class="k" style="margin-bottom:22px">Tipografia</div>{tipos}</div>'
             f'<div style="position:absolute;left:1300px;top:150px;width:520px"><div class="k" style="margin-bottom:24px">Paleta</div>{pal}</div>')
    out.append(shot(page(o, n, total, "Logotipo, tipografia e cor", corpo), f"{o['letra']}_{n:02d}")); n += 1
    # 4. sinais
    corpo = (f'<div style="position:absolute;left:96px;top:130px" class="k">As sete leis</div>'
             f'<img src="{A(o, "sinais_leis_" + o["suf"] + ".png")}" style="position:absolute;left:96px;top:170px;width:1250px">'
             f'<div style="position:absolute;left:1400px;top:170px;width:420px"><h1 style="font-size:44px;margin-bottom:24px">Sinais</h1>'
             f'<p style="font-size:21px">Cada lei ganha um sinal desenhado pela própria geometria: o que a lei faz, a figura faz. '
             f'Servem como abertura de parte, marcador de página, carimbo em relevo e índice visual do sistema de magia.</p></div>'
             f'<div style="position:absolute;left:96px;top:830px" class="k">Os seis princípios</div>'
             f'<img src="{A(o, "sinais_principios_" + o["suf"] + ".png")}" style="position:absolute;left:96px;top:868px;width:1250px">')
    out.append(shot(page(o, n, total, "Sinais das leis e dos princípios", corpo), f"{o['letra']}_{n:02d}")); n += 1
    # 5. edição: guarda, lombada, produção
    prod = "".join(f'<li style="margin-bottom:12px">{t}</li>' for t in o["producao"])
    corpo = (f'<div style="position:absolute;left:96px;top:130px;width:1040px;height:590px;background:url({A(o, "guarda_" + o["suf"] + ".png")}) center/cover;'
             f'box-shadow:0 24px 50px rgba(0,0,0,.35)"></div>'
             f'<div style="position:absolute;left:96px;top:738px" class="k">Folha de guarda</div>'
             + spine(o, 96, 786, 1040) +
             f'<div style="position:absolute;left:96px;top:{786 + 1040 * 28 / 230 + 14:.0f}px" class="k">Lombada · 28 mm</div>'
             + book3d(o, A(o, f"capa_tecido_{o['metal']}.png"), edge, 1250, 175, 380, -50, sheen=False) +
             f'<div style="position:absolute;left:1220px;top:770px;width:600px"><div class="k" style="margin-bottom:14px">Especificação de produção</div>'
             f'<ul style="font-size:19px;line-height:1.35;padding-left:22px">{prod}</ul></div>')
    out.append(shot(page(o, n, total, "Edição especial", corpo), f"{o['letra']}_{n:02d}")); n += 1
    # 6. miolo e movimento
    mp4 = A(o, f"animacao_{o['suf']}.mp4")
    frames = ""
    for i, (ts, txt) in enumerate(o["motion"]):
        fp = f"{TMP}/{o['suf']}_f{i}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ts), "-i", mp4, "-frames:v", "1", "-vf", "scale=640:-1", fp], check=True)
        frames += (f'<div style="width:350px"><img src="{fp}" style="width:350px;display:block;border:1px solid {o["line"]}">'
                   f'<div style="font-family:EBGSC;letter-spacing:2px;color:{o["acc"]};font-size:16px;margin-top:10px">{ts:.1f} s</div>'
                   f'<div style="font-size:18px;line-height:1.3">{txt}</div></div>')
    corpo = (flat(A(o, "abertura_capitulo.png"), 96, 130, 560)
             + f'<div style="position:absolute;left:740px;top:150px" class="k">Movimento · 8 s · 1920 × 1080</div>'
             f'<div style="position:absolute;left:740px;top:194px;display:grid;grid-template-columns:repeat(3,350px);gap:34px 28px">{frames}</div>'
             f'<div style="position:absolute;left:740px;bottom:110px;width:1080px" class="soft"><p style="font-size:19px;color:{o["soft"]}">'
             f'Abertura de capítulo à esquerda (página 1 do capítulo 1). A animação completa acompanha esta prancha '
             f'(animacao_{o["suf"]}.mp4 e .gif): trailer, redes sociais, vinheta de leitura em voz alta.</p></div>')
    out.append(shot(page(o, n, total, "Miolo e movimento", corpo), f"{o['letra']}_{n:02d}")); n += 1
    return out

NEUTRO = dict(letra="", nome="", bg="#15120F", fg="#EFE8DA", soft="#9A8F7E", acc="#C9A46A", line="#3A332B")

def page_neutral(n, total, titulo, corpo, extra_css=""):
    o = dict(NEUTRO)
    h = page(o, n, total, titulo, corpo, extra_css)
    return h.replace("<div>Opção  · </div>", "<div>Volume I</div>")

def emblem_bg(o):
    d = f"{OUTD}/{o['pasta']}"
    return f"{d}/" + [f for f in sorted(os.listdir(d)) if f.startswith(f"emblema_{o['suf']}_") and f.endswith(".png")][0]

def intro(keys, total):
    cards = ""
    for k in keys:
        o = OP[k]
        cards += (f'<div style="width:520px"><div style="width:520px;height:520px;background:url({emblem_bg(o)}) center/cover"></div>'
                  f'<div class="k" style="margin-top:26px">Opção {o["letra"]}</div>'
                  f'<div style="font-family:EBGi;font-size:64px;line-height:1.05;margin:4px 0 10px">{o["nome"]}</div>'
                  f'<p style="font-size:21px;color:{NEUTRO["soft"]}">{o["lema"]}</p></div>')
    corpo = (f'<div style="position:absolute;left:96px;top:120px"><div class="k">Identidade visual · versão 2</div>'
             f'<h1 style="font-size:64px;margin-top:8px">Três direções para o mesmo brasão</h1></div>'
             f'<div style="position:absolute;left:96px;right:96px;top:300px;display:flex;justify-content:space-between">{cards}</div>')
    return shot(page_neutral(1, total, "Apresentação", corpo), "00_intro")

PERFIL = {
    "A": dict(forte=["O brasão atual ganha profundidade sem mudar de desenho", "Guilhochê e microtexto são assinatura única: gerados por equação",
                     "Casa com o tema do livro: contratos, tarifas, apólices"],
              cuidado=["Linhas finas exigem foil de boa qualidade e clichê preciso", "Vinho e bronze leem como “clássico”: menos óbvio como fantasia"],
              custo=3, melhor="edição de colecionador numerada; tom de “documento oficial”"),
    "B": dict(forte=["Leitura imediata a distância: geometria forte, alto contraste", "Muito versátil em movimento, redes sociais e sinalização",
                     "Sunburst e portal dão escala épica"],
              cuidado=["Art déco é popular em capas de fantasia: precisa de execução impecável para não parecer genérico",
                       "Pede tipografia de título muito controlada"],
              custo=2, melhor="lançamento amplo; capa que funciona em miniatura de loja online"),
    "C": dict(forte=["A mais “inteligente”: o sistema de magia vira instrumento, escalas e diagramas",
                     "Prata e iridescência dão luxo contemporâneo, fora do clichê dourado", "Sinais técnicos rendem material didático (guias, mapas, apêndices)"],
              cuidado=["Foil iridescente encarece e varia entre gráficas", "Excesso de detalhe técnico pode esfriar o tom; exige contenção"],
              custo=3, melhor="saga longa com apêndices, mapas e materiais extras"),
}

def comparativo(keys, n, total):
    cols = ""
    for k in keys:
        o, pf = OP[k], PERFIL[k]
        chips = "".join(f'<div style="width:42px;height:42px;background:{h};border:1px solid #3A332B"></div>' for h, _, _ in o["paleta"])
        li = lambda xs: "".join(f'<li style="margin-bottom:6px">{x}</li>' for x in xs)
        custo = "●" * pf["custo"] + '<span style="opacity:.25">' + "●" * (4 - pf["custo"]) + "</span>"
        cols += (f'<div style="width:530px">'
                 f'<div style="display:flex;gap:14px;align-items:flex-end"><div style="flex:none;width:160px;height:160px;background:url({emblem_bg(o)}) center/cover"></div>'
                 f'<img src="{A(o, "capa_tecido_" + o["metal"] + ".png")}" style="flex:none;height:250px;box-shadow:0 14px 30px rgba(0,0,0,.45)">'
                 f'<img src="{A(o, "sobrecapa_" + o["suf"] + ".png")}" style="flex:none;height:250px;box-shadow:0 14px 30px rgba(0,0,0,.45)"></div>'
                 f'<div class="k" style="margin-top:22px">Opção {o["letra"]}</div>'
                 f'<div style="font-family:EBGi;font-size:50px;line-height:1.05">{o["nome"]}</div>'
                 f'<div style="display:flex;gap:6px;margin:12px 0 16px">{chips}</div>'
                 f'<div class="k" style="font-size:15px;color:{NEUTRO["soft"]}">Pontos fortes</div><ul style="font-size:18px;line-height:1.3;padding-left:20px;margin:6px 0 12px">{li(pf["forte"])}</ul>'
                 f'<div class="k" style="font-size:15px;color:{NEUTRO["soft"]}">Atenção</div><ul style="font-size:18px;line-height:1.3;padding-left:20px;margin:6px 0 12px">{li(pf["cuidado"])}</ul>'
                 f'<div style="font-size:18px"><span class="k" style="font-size:15px;color:{NEUTRO["soft"]}">Custo relativo</span> '
                 f'<span style="color:{NEUTRO["acc"]};letter-spacing:3px">{custo}</span></div>'
                 f'<div style="font-size:18px;margin-top:8px"><span class="k" style="font-size:15px;color:{NEUTRO["soft"]}">Melhor para</span> {pf["melhor"]}</div></div>')
    corpo = (f'<div style="position:absolute;left:96px;top:118px"><div class="k">Comparativo</div>'
             f'<h1 style="font-size:46px;margin-top:6px">Lado a lado</h1></div>'
             f'<div style="position:absolute;left:96px;right:96px;top:250px;display:flex;justify-content:space-between">{cols}</div>')
    return shot(page_neutral(n, total, "Comparativo", corpo), "90_comparativo")

GERAIS = [("Special editions e cortes pintados (Pan Macmillan)", "https://www.panmacmillan.com/blogs/fiction/hot-special-editions"),
          ("“The spredges effect” (The Bookseller)", "https://thebookseller.com/news/spredges-effect-why-books-are-becoming-more-beautiful"),
          ("Special editions take a special touch (Publishers Weekly, 2024)", "https://www2.publishersweekly.com/pw/print/20241007/96085-special-editions-of-books-take-a-special-touch.html"),
          ("Edições limitadas da Folio Society 2021–2025 (LibraryThing)", "https://www.librarything.it/topic/330009")]

def referencias(keys, n, total):
    blocos = ""
    for titulo, refs in [("Mercado de edições especiais", GERAIS)] + [(f"Opção {OP[k]['letra']} · {OP[k]['nome']}", OP[k]["ref"]) for k in keys]:
        items = "".join(f'<div style="margin-bottom:12px"><div style="font-size:21px">{html.escape(t)}</div>'
                        f'<div style="font-family:MONO;font-size:14px;color:{NEUTRO["soft"]};word-break:break-all">{html.escape(u)}</div></div>' for t, u in refs)
        blocos += f'<div style="width:800px;margin-bottom:34px"><div class="k" style="margin-bottom:12px">{titulo}</div>{items}</div>'
    nota = ("Todo o desenho foi gerado por código vetorial próprio (curvas de torno, microtexto, hachuras), sem banco de imagens: "
            "nenhuma licença de terceiros embutida. As ilustrações de sobrecapa são as artes já criadas para o livro. "
            "Fontes: famílias de licença aberta (SIL OFL), livres para impressão comercial.")
    corpo = (f'<div style="position:absolute;left:96px;top:118px"><div class="k">Pesquisa</div>'
             f'<h1 style="font-size:46px;margin-top:6px">Referências consultadas</h1></div>'
             f'<div style="position:absolute;left:96px;right:96px;top:240px;display:flex;flex-wrap:wrap;justify-content:space-between">{blocos}</div>'
             f'<div style="position:absolute;left:96px;width:1700px;bottom:100px"><p style="font-size:19px;color:{NEUTRO["soft"]}">{nota}</p></div>')
    return shot(page_neutral(n, total, "Referências", corpo), "91_referencias")

def build(keys):
    total = 1 + 6 * len(keys) + 2
    pngs = [intro(keys, total)]
    for i, k in enumerate(keys):
        pngs += pages_for(OP[k], 2 + 6 * i, total)
    pngs.append(comparativo(keys, total - 1, total))
    pngs.append(referencias(keys, total, total))
    return pngs

def to_pdf(pngs, out):
    ims = [Image.open(p).convert("RGB") for p in pngs]
    ims[0].save(out, save_all=True, append_images=ims[1:], resolution=144, quality=88)

if __name__ == "__main__":
    keys = sys.argv[1:] or [k for k in "ABC" if os.path.exists(f"{OUTD}/{OP[k]['pasta']}/animacao_{OP[k]['suf']}.mp4")]
    pngs = build(keys)
    for p in pngs:
        Image.open(p).convert("RGB").save(f"{OUTD}/pranchas/{os.path.basename(p)[:-4]}.jpg", quality=90)
    if len(keys) == 3:
        to_pdf(pngs, f"{OUTD}/Identidade_visual_v2_tres_opcoes.pdf")
    print("\n".join(pngs))
