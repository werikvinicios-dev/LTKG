#!/usr/bin/env python3
"""Tipografia própria da Edição Imersiva.

1. ARESTA TITULAR — fonte de títulos derivada da Cinzel (OFL): cada letra leva o corte de uma lâmina,
   uma fenda fina na mesma diagonal em todos os sinais ("a aresta"). Nome novo, como pede a licença.
2. SELAR — a escrita dos selos de Aresta: 26 letras e 10 algarismos montados só com a gramática dos selos
   (anel, eixo, cauda, traço de terra e pérola). Serve para inscrições, bordas e medalhões; não é para ler texto.

Saída: build/fonts/ArestaTitular-{Regular,Bold}.ttf, build/fonts/Selar-Regular.ttf e
exportacoes/edicao_imersiva/tipografia/ (fontes + amostra)."""
import math, os, shutil
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.fontBuilder import FontBuilder

ROOT = "/home/user/LTKG"
FON = f"{ROOT}/build/fonts"
OUT = f"{ROOT}/exportacoes/edicao_imersiva/tipografia"
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------ 1. Aresta Titular
def fenda(xmin, ymin, xmax, ymax, upm):
    """Faixa diagonal fina que atravessa o sinal (sobe da esquerda para a direita)."""
    h = ymax - ymin
    esp = upm * 0.024                     # espessura do corte
    ang = math.radians(17)
    cy = ymin + h * 0.56
    x0, x1 = xmin - 200, xmax + 200
    cx = (xmin + xmax) / 2
    y0 = cy + (x0 - cx) * math.tan(ang)
    y1 = cy + (x1 - cx) * math.tan(ang)
    p = pathops.Path()
    p.moveTo(x0, y0 - esp / 2); p.lineTo(x1, y1 - esp / 2); p.lineTo(x1, y1 + esp / 2); p.lineTo(x0, y0 + esp / 2); p.close()
    return p


def aresta(src, dst, familia, estilo):
    f = TTFont(src)
    gs = f.getGlyphSet()
    glyf = f["glyf"]
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    alvo = set()
    for cp, g in cmap.items():
        ch = chr(cp)
        if ch.isalnum() or ch in "&?!":
            alvo.add(g)
    feitos = 0
    for g in sorted(alvo):
        gl = glyf[g]
        if gl.isComposite() or gl.numberOfContours <= 0:
            continue
        p = pathops.Path()
        gs[g].draw(pathops.PathPen(p, glyphSet=gs))
        b = p.bounds
        if not b or b[3] - b[1] < 50:
            continue
        cortado = pathops.op(p, fenda(*b, upm), pathops.PathOp.DIFFERENCE)
        pen = TTGlyphPen(gs)
        cortado.draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
        novo = pen.glyph()
        novo.recalcBounds(glyf)
        glyf[g] = novo
        feitos += 1
    nome = f["name"]
    for rec in list(nome.names):
        if rec.nameID in (1, 3, 4, 6, 16, 17):
            txt = {1: familia, 3: f"{familia} {estilo}; derivada da Cinzel (OFL)", 4: f"{familia} {estilo}",
                   6: f"{familia.replace(' ', '')}-{estilo}", 16: familia, 17: estilo}[rec.nameID]
            rec.string = txt
    nome.setName("Derivada de Cinzel (c) The Cinzel Project Authors, SIL Open Font License 1.1. "
                 "Corte de lâmina criado para Leis para Matar Deuses.", 0, 3, 1, 0x409)
    f.save(dst)
    return feitos


# ------------------------------------------------------------------ 2. Selar (escrita dos selos)
UPM = 1000
TOPO, BASE = 720, 0
R = 250                               # raio do anel
CX, CY = 360, 360
TRACO = 46                            # espessura do traço


def arco(p, cx, cy, r, a0, a1, n=40):
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        (p.moveTo if i == 0 else p.lineTo)(x, y)


def linha(p, x0, y0, x1, y1):
    p.moveTo(x0, y0); p.lineTo(x1, y1)


def perola(cx, cy, r):
    q = pathops.Path()
    k = 0.5523 * r
    q.moveTo(cx + r, cy)
    q.cubicTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
    q.cubicTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
    q.cubicTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
    q.cubicTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
    q.close()
    return q


# Cada sinal: (anel, eixo, cauda, terra, pérola)
# anel: None | (a0, a1) graus;  eixo: None | 'cheio' | 'alto' | 'baixo'
# cauda: None | ângulo em graus (sai do anel para fora);  terra: None | 'base' | 'topo' | 'dupla'
# pérola: None | 'centro' | 'alto' | 'baixo' | 'cauda'
ANEIS = [(0, 360), (60, 420), (-120, 180), (30, 330), (210, 510), (120, 420)]
EIXOS = [None, "cheio", "alto", "baixo"]
CAUDAS = [None, 45, 135, -45, -135, 90]
TERRAS = [None, "base", "dupla"]
PEROLAS = ["centro", None, "alto", "baixo", "cauda"]


def receita(i):
    return (ANEIS[i % 6], EIXOS[(i // 2) % 4], CAUDAS[(i * 5 + 1) % 6], TERRAS[(i * 7) % 3], PEROLAS[(i * 3) % 5])


def sinal(i, digito=False):
    anel, eixo, cauda, terra, per = receita(i if not digito else 26 + i * 3)
    r = R if not digito else R * 0.78
    linhas = pathops.Path()
    if digito:                                     # algarismos: anel fechado + i entalhes
        arco(linhas, CX, CY, r, 0, 360)
        for k in range(i):
            a = math.radians(90 - k * 36)
            linha(linhas, CX + (r - 70) * math.cos(a), CY + (r - 70) * math.sin(a), CX + (r + 60) * math.cos(a), CY + (r + 60) * math.sin(a))
    else:
        arco(linhas, CX, CY, r, *anel)
        if eixo == "cheio":
            linha(linhas, CX, BASE + 10, CX, TOPO - 10)
        elif eixo == "alto":
            linha(linhas, CX, CY, CX, TOPO - 10)
        elif eixo == "baixo":
            linha(linhas, CX, BASE + 10, CX, CY)
        if cauda is not None:
            a = math.radians(cauda)
            x0, y0 = CX + r * math.cos(a), CY + r * math.sin(a)
            linha(linhas, x0, y0, x0 + 140 * math.cos(a), y0 + 140 * math.sin(a))
        if terra in ("base", "dupla"):
            linha(linhas, CX - 120, BASE + 20, CX + 120, BASE + 20)
        if terra == "dupla":
            linha(linhas, CX - 70, BASE + 80, CX + 70, BASE + 80)
    contorno = pathops.Path()
    linhas.stroke(TRACO, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    linhas.convertConicsToQuads(0.25)
    linhas.simplify()
    contorno = linhas
    if per and not digito:
        pos = {"centro": (CX, CY), "alto": (CX, CY + r * 0.55), "baixo": (CX, CY - r * 0.55)}
        if per == "cauda" and cauda is not None:
            a = math.radians(cauda)
            pos["cauda"] = (CX + (r + 175) * math.cos(a), CY + (r + 175) * math.sin(a))
        if per in pos:
            contorno = pathops.op(contorno, perola(*pos[per], 52), pathops.PathOp.UNION)
    elif digito:
        contorno = pathops.op(contorno, perola(CX, CY, 46), pathops.PathOp.UNION)
    contorno.simplify()
    return contorno


def selar(dst):
    letras = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    nomes = [".notdef", "space"] + letras + [f"d{d}" for d in range(10)]
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(nomes)
    cmap = {32: "space"}
    for c in letras:
        cmap[ord(c)] = c
        cmap[ord(c.lower())] = c
    for d in range(10):
        cmap[ord(str(d))] = f"d{d}"
    fb.setupCharacterMap(cmap)
    glifos, larg = {}, {}
    vazio = TTGlyphPen(None).glyph()
    glifos[".notdef"], glifos["space"] = vazio, vazio
    larg[".notdef"], larg["space"] = (600, 0), (360, 0)
    for k, c in enumerate(letras):
        pen = TTGlyphPen(None)
        sinal(k).draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
        glifos[c] = pen.glyph(); larg[c] = (760, 0)
    for d in range(10):
        pen = TTGlyphPen(None)
        sinal(d, digito=True).draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
        glifos[f"d{d}"] = pen.glyph(); larg[f"d{d}"] = (760, 0)
    fb.setupGlyf(glifos)
    fb.setupHorizontalMetrics(larg)
    fb.setupHorizontalHeader(ascent=900, descent=-200)
    fb.setupNameTable({"familyName": "Selar", "styleName": "Regular",
                       "uniqueFontIdentifier": "Selar-Regular; Leis para Matar Deuses",
                       "fullName": "Selar Regular", "psName": "Selar-Regular",
                       "copyright": "Escrita dos selos de Aresta, criada para Leis para Matar Deuses."})
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-200, usWinAscent=1000, usWinDescent=250)
    fb.setupPost()
    fb.save(dst)


if __name__ == "__main__":
    n1 = aresta(f"{FON}/Cinzel-Regular.ttf", f"{FON}/ArestaTitular-Regular.ttf", "Aresta Titular", "Regular")
    n2 = aresta(f"{FON}/Cinzel-Bold.ttf", f"{FON}/ArestaTitular-Bold.ttf", "Aresta Titular", "Bold")
    selar(f"{FON}/Selar-Regular.ttf")
    for f in ("ArestaTitular-Regular.ttf", "ArestaTitular-Bold.ttf", "Selar-Regular.ttf"):
        shutil.copy(f"{FON}/{f}", f"{OUT}/{f}")
    print("Aresta Titular:", n1, "e", n2, "sinais cortados; Selar: 36 sinais")
