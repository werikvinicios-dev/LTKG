#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PR-09 — Âncoras: como o livro as descreve, tipo por tipo. Cada exemplo é desenhado por código (sem gerador de
imagem) a partir das descrições do manuscrito e da Bíblia Técnica: objetos físicos, sem símbolos. Os capítulos
citados ficam no rodapé de cada quadro. Saída em exportacoes/identidade_aresta/pranchas/ (+ pranchas_jpg/)."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from pranchas_aresta import panel, shot, A
from prancha_magia import placa, glow, blackbody, salva, W, H

OUT_JPG = "/home/user/LTKG/exportacoes/identidade_aresta/pranchas_jpg"
NOISE = np.random.default_rng(5)
AMBER, BRASA, COBRE, BRONZE, MUTED = (240, 150, 50), (200, 51, 47), (184, 115, 51), (176, 138, 74), (156, 138, 102)
PW, PH = 472, 304
K = max(PW / W, PH / H)                                          # escala do "cover" do painel


def base():
    return Image.fromarray(placa().astype(np.uint8))


def render(im, lay, raio=8):
    a = np.asarray(im).astype(np.float32) + NOISE.normal(0, 2.4, (H, W, 1))
    return glow(a, np.asarray(lay).astype(np.float32), raio)


def poli(d, pts, cor, larg=3, per=22, k=1.0):
    """Elo: fio reto e tenso, com franjas ao longo do caminho."""
    acc = 0.0
    for p, q in zip(pts, pts[1:]):
        L = math.dist(p, q); n = max(1, int(L / 4))
        for i in range(n):
            s0, s1 = i / n, (i + 1) / n
            f = .5 + .5 * math.cos(2 * math.pi * ((acc + s0 * L) / per))
            c = tuple(int(v * k * (.3 + .7 * f ** 2)) for v in cor)
            d.line([(p[0] + (q[0] - p[0]) * s0, p[1] + (q[1] - p[1]) * s0), (p[0] + (q[0] - p[0]) * s1, p[1] + (q[1] - p[1]) * s1)], fill=c, width=larg)
        acc += L


def bezier(p0, p1, p2, n=30):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


def tijolo(im, x0=0, x1=W, y0=0, y1=H, cor=(58, 30, 24)):
    d = ImageDraw.Draw(im); r_ = np.random.default_rng(2)
    for r, y in enumerate(range(y0, y1, 46)):
        off = 0 if r % 2 else 70
        for x in range(-140 + off, x1, 140):
            k = int(r_.integers(-7, 8)); c = (cor[0] + k, cor[1] + k // 2, cor[2] + k // 2)
            xa, xb = max(x + 3, x0), min(x + 137, x1)
            if xb > xa and y + 3 < y1: d.rectangle([xa, y + 3, xb, max(y + 3, min(y + 43, y1))], fill=c)


def bota(d, x, y, s=1.0, esp=10, cor=(30, 26, 24)):
    P = [(-30, 0), (150, 0), (162, -24), (142, -46), (74, -54), (62, -132), (-8, -132), (-12, -44), (-34, -26)]
    d.polygon([(x + px * s, y + py * s) for px, py in P], fill=cor, outline=(120, 110, 100))
    d.rectangle([x - 34 * s, y, x + 162 * s, y + esp * s], fill=(96, 90, 82), outline=(150, 140, 125))
    for rx in range(-20, 150, 34):
        d.ellipse([x + (rx - 3) * s, y + (esp / 2 - 3) * s, x + (rx + 3) * s, y + (esp / 2 + 3) * s], fill=BRONZE)


def tag(x, y, s, lado="l"):
    px = x * K - (W * K - PW) / 2; py = y * K - (H * K - PH) / 2
    est = f"left:{px:.0f}px" if lado == "l" else f"right:{PW - px:.0f}px"
    return (f'<div style="position:absolute;{est};top:{py:.0f}px;z-index:5;font-family:Cz;font-size:8.4px;letter-spacing:.9px;'
            f'color:#EADFC6;text-shadow:0 1px 3px #000;white-space:nowrap">{s}</div>')


# ------------------------------------------------------------------ os oito exemplos
def t_prego():
    im = base(); tijolo(im); d = ImageDraw.Draw(im); BR = (58, 30, 24)
    for cx in (236, 708):                                          # prego pintado da cor da parede
        d.ellipse([cx - 15, 315, cx + 15, 345], fill=(BR[0] + 4, BR[1] + 2, BR[2] + 2), outline=(44, 22, 18), width=2)
        d.arc([cx - 12, 318, cx + 12, 342], 200, 290, fill=(78, 44, 34), width=2)
    c, R = (708, 270), 205
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], fill=255)
    lente = im.copy(); dc = ImageDraw.Draw(lente)
    dc.ellipse([693, 315, 723, 345], fill=COBRE, outline=(230, 170, 110), width=2); dc.ellipse([700, 321, 706, 327], fill=(240, 196, 150))
    im.paste(lente, (0, 0), m)
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay)
    poli(dl, [(708, 313), (708, 70)], AMBER, 5, 24)
    for y in (250, 180, 110): dl.line([(696, y + 12), (708, y), (720, y + 12)], fill=(240, 170, 80), width=3)
    lay = ImageChops.multiply(lay, Image.merge("RGB", [m, m, m]))
    d = ImageDraw.Draw(im)
    d.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], outline=BRONZE, width=12)
    d.line([(c[0] + R * .72, c[1] + R * .72), (c[0] + R * 1.14, c[1] + R * 1.14)], fill=BRONZE, width=16)
    d.line([(472, 0), (472, H)], fill=(120, 100, 70), width=2)
    return render(im, lay)


def t_corpo():
    im = base(); tijolo(im, 640, W, 0, 470, (52, 30, 24)); d = ImageDraw.Draw(im)
    d.rectangle([0, 470, W, H], fill=(26, 24, 22)); d.line([(0, 470), (W, 470)], fill=(120, 110, 100), width=2)
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay)
    bota(d, 200, 470); bota(d, 420, 470)
    pts = [(210, 494), (330, 494), (430, 494), (550, 494)]
    d.ellipse([750, 290, 770, 310], fill=COBRE, outline=(230, 170, 110), width=2)
    for k, p in enumerate(pts):
        d.ellipse([p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8], fill=COBRE, outline=(230, 170, 110), width=2)
        poli(dl, [p, (p[0], 520 + 8 * k), (760, 520 + 8 * k), (760, 300)], AMBER, 3, 22, .9)
    return render(im, lay)


def t_lastro():
    im = base(); d = ImageDraw.Draw(im)
    for y in range(380, H):
        u = (y - 380) / (H - 380); d.line([(0, y), (W, y)], fill=(int(24 + 22 * u), int(34 + 26 * u), int(44 + 30 * u)))
    d.line([(0, 380), (W, 380)], fill=(130, 160, 185), width=2)
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay); rnd = random.Random(5); cx = 470
    for k in range(18):
        ang = 2 * math.pi * k / 18 + rnd.uniform(-.15, .15); L = rnd.uniform(220, 440); x, y = cx, 388; pts = [(x, y)]
        for s in range(14):
            ang += rnd.uniform(-.3, .3); x += math.cos(ang) * L / 14; y += abs(math.sin(ang)) * L / 14 * .5; pts.append((x, y))
        dl.line(pts, fill=(70, 92, 120), width=2)
    bota(d, 380, 380, 1.4, 14)
    for dx in (-130, 0, 130):
        dl.line([(cx + dx - 14, 430), (cx + dx, 452), (cx + dx + 14, 430)], fill=(150, 170, 200), width=3)
    return render(im, lay)


def t_pivo():
    im = base(); d = ImageDraw.Draw(im)
    for y in range(470, H):
        u = min(1, (y - 470) / 90); d.line([(0, y), (W, y)], fill=(int(150 - 92 * u), int(160 - 94 * u), int(172 - 96 * u)))
    d.rectangle([458, 470, 482, 570], fill=(84, 52, 30), outline=(120, 80, 50))
    d.rectangle([458, 160, 482, 470], fill=COBRE); d.rectangle([462, 160, 467, 470], fill=(226, 160, 104)); d.rectangle([476, 160, 482, 470], fill=(120, 70, 32))
    d.polygon([(405, 474), (535, 474), (508, 424), (432, 424)], fill=(224, 216, 200), outline=(150, 142, 128))
    d.rectangle([432, 424, 508, 432], fill=(204, 196, 180))
    d.ellipse([450, 120, 490, 160], outline=BRONZE, width=7)
    cabo = bezier((488, 134), (700, 170), (W, 70)); d.line(cabo, fill=COBRE, width=7); d.line([(x, y - 2) for x, y in cabo], fill=(226, 160, 104), width=2)
    d.line([(380, 160), (380, 470)], fill=MUTED, width=2)
    for y in (160, 470): d.line([(368, y), (392, y)], fill=MUTED, width=2)
    lay = Image.new("RGB", (W, H))
    return render(im, lay)


def t_discos():
    im = base(); d = ImageDraw.Draw(im); SUP = 250; rnd = random.Random(4)
    for y in range(SUP, H):
        u = (y - SUP) / (H - SUP); d.line([(0, y), (W, y)], fill=(int(92 + 40 * u), int(66 + 10 * u), int(58 - 8 * u)))
    for _ in range(320):
        x, y = rnd.uniform(0, W), rnd.uniform(SUP + 10, H); a = rnd.uniform(0, math.pi); l = rnd.uniform(4, 14)
        d.line([(x, y), (x + math.cos(a) * l, y + math.sin(a) * l)], fill=(130, 104, 92), width=1)
    d.line([(0, SUP), (W, SUP)], fill=(190, 170, 150), width=3)
    for i in range(6):
        x = 130 + 130 * i
        d.ellipse([x - 48, SUP - 20, x + 48, SUP + 8], fill=(112, 86, 40), outline=BRONZE, width=3)
        d.arc([x - 38, SUP - 16, x + 38, SUP + 2], 200, 330, fill=(220, 180, 110), width=2)
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay)
    for i, x in enumerate((195, 455, 715)):
        d.rounded_rectangle([x - 20, 388, x + 20, 452], 10, fill=(230, 224, 210), outline=(150, 142, 128), width=2)
        dl.rounded_rectangle([x - 18, 390, x + 18, 450], 10, fill=tuple(int(v * .8) for v in blackbody(.62)))
        poli(dl, [(x, 452), (x, 500 + 22 * i), (W, 500 + 22 * i)], AMBER, 4, 24)
    return render(im, lay)


def t_anel():
    im = base(); d = ImageDraw.Draw(im)
    for y in range(300, H):
        u = (y - 300) / (H - 300); d.line([(0, y), (W, y)], fill=(int(34 - 14 * u), int(34 - 14 * u), int(38 - 14 * u)))
    cx, cy, rx, ry = 472, 400, 360, 120
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(74, 70, 66), width=26)
    d.ellipse([cx - rx - 12, cy - ry - 12, cx + rx + 12, cy + ry + 12], outline=(112, 106, 98), width=2)
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay); N = 28; grandes = {1, 5, 9, 14, 18, 22, 26}; pos = []
    for k in range(N):
        t = 2 * math.pi * k / N; x, y = cx + rx * math.cos(t), cy + ry * math.sin(t); pos.append((x, y, math.sin(t)))
        if k in grandes:
            r = 17; d.ellipse([x - r, y - r, x + r, y + r], fill=(38, 34, 32), outline=(120, 110, 100), width=2)
            dl.ellipse([x - r + 4, y - r + 4, x + r - 4, y + r - 4], fill=tuple(int(v * .3) for v in blackbody(.45)))
        else:
            r = 9 + 3 * (math.sin(t) + 1) / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=(232, 226, 214), outline=(150, 142, 128))
            dl.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], fill=tuple(int(v * .85) for v in blackbody(.6)))
    rnd = random.Random(8); costas = [p for p in pos if p[2] < 0.2]
    for k in range(12):
        x0 = 60 + k * 76 + rnd.uniform(-20, 20); a = costas[rnd.randrange(len(costas))]
        poli(dl, bezier((x0, -10), ((x0 + a[0]) / 2 + rnd.uniform(-40, 40), a[1] * .35), (a[0], a[1])), BRASA if k % 2 else AMBER, 3, 24, .9)
    return render(im, lay)


def t_coronal():
    im = base(); d = ImageDraw.Draw(im)
    for y in range(0, 430):
        u = y / 430; d.line([(0, y), (W, y)], fill=(int(10 + 18 * u), int(12 + 16 * u), int(22 + 18 * u)))
    d.polygon([(0, 430), (0, 310), (150, 240), (300, 330), (480, 210), (700, 310), (W, 230), (W, 430)], fill=(18, 20, 26))
    d.polygon([(500, H), (W, 340), (W, H)], fill=(22, 24, 30)); d.rectangle([0, 430, W, H], fill=(16, 17, 22))
    for k in range(18):                                              # cidade ao longe
        x = 20 + k * 52; h = 30 + (k * 37) % 50; d.rectangle([x, 430 - h, x + 30, 430], fill=(26, 24, 26))
        if k % 3 == 0: d.rectangle([x + 10, 430 - h + 10, x + 16, 430 - h + 18], fill=(150, 110, 50))
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay)
    mir = []
    for i in range(12):
        t = i / 11; x, y = 570 + t * 350, 528 - t * 168; mir.append((x, y))
        d.polygon([(x - 12, y - 8), (x + 12, y - 12), (x + 12, y + 6), (x - 12, y + 10)], fill=(120, 134, 160), outline=(190, 200, 220))
        dl.line([(x - 8, y - 3), (x + 6, y - 7)], fill=(150, 160, 175), width=2)
    sol = (330, 190)
    d.rectangle([320, 220, 340, 440], fill=(46, 40, 32), outline=BRONZE)
    d.ellipse([sol[0] - 36, sol[1] - 36, sol[0] + 36, sol[1] + 36], fill=(112, 80, 40), outline=BRONZE, width=4)
    for k in range(12):
        a = 2 * math.pi * k / 12; d.line([(sol[0] + math.cos(a) * 40, sol[1] + math.sin(a) * 40), (sol[0] + math.cos(a) * 58, sol[1] + math.sin(a) * 58)], fill=BRONZE, width=4)
    cis = (150, 500); d.ellipse([cis[0] - 80, cis[1] - 38, cis[0] + 80, cis[1] + 38], fill=(24, 44, 60), outline=(140, 175, 205), width=3)
    poco = (470, 500); d.rectangle([poco[0] - 12, poco[1] - 70, poco[0] + 12, poco[1] + 20], fill=(70, 62, 54), outline=(150, 140, 125))
    for k in range(7): dl.ellipse([poco[0] - 12 + k * 3, poco[1] - 100 - k * 22, poco[0] + 14 + k * 5, poco[1] - 74 - k * 22 + 10], fill=(40 - k * 4,) * 3)
    for a, b in [(sol, cis), (sol, poco), (cis, poco), (poco, mir[0]), (mir[0], mir[4]), (mir[4], mir[8]), (mir[8], mir[11]), (sol, mir[4])]:
        poli(dl, [a, b], AMBER, 3, 26, .8)
    return render(im, lay, 10)


def t_limiar():
    im = base(); d = ImageDraw.Draw(im)
    for x0 in (60, 560):
        d.rectangle([x0, 410, x0 + 330, 440], fill=(74, 50, 32), outline=(120, 86, 54))
        for lx in (x0 + 26, x0 + 292): d.rectangle([lx, 440, lx + 14, 600], fill=(58, 40, 26))
    lay = Image.new("RGB", (W, H)); dl = ImageDraw.Draw(lay)
    for cx in (225, 725):
        d.ellipse([cx - 62, 372, cx + 62, 414], outline=BRONZE, width=10)
        dl.ellipse([cx - 55, 376, cx + 55, 410], outline=(255, 226, 150), width=3)
    d.polygon([(168, 312), (218, 300), (232, 356), (184, 366)], fill=(236, 228, 210), outline=(190, 180, 160))
    d.polygon([(700, 318), (748, 308), (762, 364), (714, 374)], fill=(236, 228, 210), outline=(190, 180, 160))
    d.polygon([(700, 380), (748, 372), (754, 392), (706, 400)], fill=(236, 228, 210))
    rnd = random.Random(2)
    for k in range(22):
        x, y = 725 + rnd.uniform(-70, 90), 380 - rnd.uniform(0, 150); d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(236, 242, 250))
    for x in range(330, 620, 16): d.ellipse([x - 2, 392, x + 2, 396], fill=MUTED)
    return render(im, lay, 6)


TILES = [
    ("Improvisada: prego de cobre", "cap. 1", t_prego,
     "“Pregos pequenos de cobre, de cabeça chata, pintados da cor da parede.” Só a lente mostra o elo.",
     [tag(60, 100, "A OLHO NU"), tag(560, 78, "PELA LENTE")]),
    ("No corpo: solas e parede", "caps. 1 e 12", t_corpo,
     "“Dois pontos em cada sola e uma terceira âncora, mais discreta, num prego da parede.”",
     [tag(180, 370, "SOLAS"), tag(675, 250, "PREGO")]),
    ("Inercial: chapas de lastro", "cap. 15", t_lastro,
     "Chapas de ferro nas botas: o contragolpe desce por elas e trinca o gelo.", []),
    ("Portátil: Pivô de Cobre", "cap. 18", t_pivo,
     "“Estaca de cobre do comprimento de um antebraço, grossa como dois dedos, com uma base larga de cerâmica e uma argola no alto.”",
     [tag(180, 300, "≈ UM ANTEBRAÇO"), tag(500, 360, "BASE DE CERÂMICA", "l")]),
    ("Trilha de contato", "caps. 8 e 24", t_discos,
     "Pontos de apoio cravados no piso a intervalos regulares. Em cima, discos de bronze; embaixo, no sal, cerâmica enterrada.",
     [tag(420, 210, "DISCOS DE BRONZE"), tag(250, 460, "CERÂMICA ENTERRADA")]),
    ("Carregada: o anel de ferro", "cap. 25", t_anel,
     "“Âncoras de cerâmica branca cravadas a intervalos regulares, todas brilhando num laranja sujo.” Sete, maiores e escuras, seguram as outras.",
     []),
    ("Coronal: a infraestrutura", "caps. 3 e 6", t_coronal,
     "“Igneos de parede, Campos de Espelho nas encostas, poços geotérmicos.” Não se pinta em separado: é a arquitetura.",
     [tag(600, 190, "SOL DE BRONZE"), tag(520, 410, "CAMPO DE ESPELHOS")]),
    ("De limiar: anéis de bronze", "cap. 17", t_limiar,
     "Dois anéis de bronze, as pontas de um limiar mínimo. Passam voz, papel dobrado e ar. A borda interna acende num filete de ouro.",
     [tag(380, 330, "LONGE DALI")]),
]


def prancha_9():
    b = []
    b.append(panel(0, 0, 1448, 128, img=A("09_engenharia_arcana/EA-005_materiais_de_ancora.png"), pos="center 42%",
                   extra='<div class="img fade-r"></div>'
                         '<div style="position:absolute;left:30px;top:22px;z-index:4" class="h1"><span style="font-size:23px">ÂNCORAS ◆ O QUE SE VÊ</span>'
                         '<div class="sc" style="font-size:11.5px;margin-top:6px;letter-spacing:3px">Fonte · Âncora · Elo · Destino · Controle · Retorno</div></div>'
                         '<div class="q" style="position:absolute;left:30px;top:84px;font-size:14px;z-index:4">Uma âncora é uma coisa de verdade, prendida em algum lugar. O que a revela é o que passa por ela.</div>'
                         '<div class="sc" style="position:absolute;left:30px;top:108px;font-size:8.5px;z-index:4;color:#9C8A66">Proposta · aguardando aprovação do autor</div>'))
    for i, (nome, cap, fn, txt, tags) in enumerate(TILES):
        x, y = 8 + (i % 3) * 480, 136 + (i // 3) * 310
        leg = (f'<div style="position:absolute;left:0;right:0;bottom:0;padding:26px 14px 9px;z-index:4;'
               f'background:linear-gradient(rgba(6,5,4,0),rgba(6,5,4,.93) 38%)" class="q"><span style="font-size:11.6px">{txt}</span></div>')
        b.append(panel(x, y, PW, PH, nome, salva(f"anc{i}", fn()), sub=cap, extra="".join(tags) + leg))
    L = lambda a, c: f'<div style="margin:0 0 9px"><span class="sc" style="font-size:9.6px;letter-spacing:1.4px">{a}</span> <span style="color:#D7CBB2">{c}</span></div>'
    lista = ("".join([L("Temperatura", "esquenta ou esfria (caps. 3 e 24)."), L("Som", "zumbe numa nota (cap. 24)."),
                      L("Lente e placas", "o elo vira franjas coloridas (caps. 1, 6 e 24)."),
                      L("Fuso", "a cerâmica brilha do vermelho sujo ao laranja (cap. 25)."),
                      L("Marca de cobrança", "quase invisível e efêmera, com a assinatura de Ilan (caps. 4, 18 e 25)."),
                      L("Lacre", "as âncoras oficiais têm selo (cap. 13).")]))
    b.append(panel(968, 756, PW, PH, "Como se denuncia", extra=
                   '<div class="q" style="position:absolute;left:16px;right:14px;top:46px;font-size:12.6px;line-height:1.42">' + lista +
                   '<div class="sc" style="font-size:9px;color:#9C8A66;margin-top:12px;letter-spacing:1.2px;line-height:1.6">Estados: improvisada (rápida, arriscada) · calibrada (estável) · integrada (ligada a uma Malha)</div></div>'))
    return shot("PR-09_ancoras", "".join(b))


if __name__ == "__main__":
    p = prancha_9(); print(p)
    Image.open(p).convert("RGB").save(f"{OUT_JPG}/PR-09_ancoras.jpg", quality=90)
