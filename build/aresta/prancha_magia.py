#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PR-08 — Linguagem visual da magia (Transposição). Cada disciplina é desenhada pelo fenômeno físico que ela
produz (o que se vê a olho nu) e por um detalhe da lente de aferição com as franjas na cor de leitura da
disciplina. Os padrões são gerados por código (numpy), sem gerador de imagem. Saída em
exportacoes/identidade_aresta/pranchas/ (mesmo layout e captura das outras pranchas)."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pranchas_aresta import panel, labels, shot, A

ROOT = "/home/user/LTKG"
TMP = f"{ROOT}/build/_magia"
os.makedirs(TMP, exist_ok=True)
W, H = 944, 600
RNG = np.random.default_rng(7)


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)


def placa():
    """Fundo de grafite com grão e vinheta."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.55 * (((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2) * 2.2
    base = np.stack([16 * v, 15 * v, 13 * v], -1)
    return np.clip(base + RNG.normal(0, 2.2, (H, W, 1)), 0, 255)


def blackbody(t):
    pts = [(0, (0, 0, 0)), (.3, (105, 22, 12)), (.5, (196, 52, 22)), (.68, (238, 126, 40)),
           (.84, (255, 196, 108)), (1, (255, 246, 222))]
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,), np.float32)
    for (a, ca), (b, cb) in zip(pts, pts[1:]):
        m = (t >= a) & (t <= b); f = ((t - a) / (b - a))[..., None]
        out[m] = (np.array(ca) * (1 - f) + np.array(cb) * f)[m]
    return out


def glow(img, layer, raio):
    """Soma aditiva de uma camada com brilho difuso."""
    L = Image.fromarray(np.clip(layer, 0, 255).astype(np.uint8))
    g = np.asarray(L.filter(ImageFilter.GaussianBlur(raio))).astype(np.float32)
    return np.clip(img + layer + g * 1.4, 0, 255)


def lente(img, cor, ang, cx=812, cy=128, r=92):
    """Detalhe da lente de aferição: franjas na cor de leitura, inclinadas no sentido do fluxo."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = x - cx, y - cy; d = np.hypot(dx, dy)
    dentro = d < r
    u = dx * math.cos(ang) + dy * math.sin(ang)
    w = dx * -math.sin(ang) + dy * math.cos(ang)
    fr = 0.5 + 0.5 * np.cos(2 * math.pi * (u + 0.0016 * w ** 2) / 15)
    irid = 0.5 + 0.5 * np.cos(2 * math.pi * u / 47 + np.stack([0, 2.1, 4.2])[:, None, None]).transpose(1, 2, 0)
    c = hexrgb(cor)
    vidro = (img * 0.3 + (fr[..., None] ** 2.2) * (c * 1.05 + irid * 16)) * (1 - 0.35 * (d / r) ** 4)[..., None]
    img = np.where(dentro[..., None], vidro, img)
    aro = (d >= r) & (d < r + 7)
    luz = 0.55 + 0.45 * np.cos(np.arctan2(dy, dx) + 2.3)
    img = np.where(aro[..., None], (np.array([176, 138, 74]) * luz[..., None]), img)
    return img


def pulso():
    img = placa(); lay = np.zeros_like(img)
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    cx, cy = 400, 290
    for _ in range(2600):
        px, py = RNG.uniform(0, W), RNG.uniform(40, 470)
        vx, vy = px - cx, py - cy; r = math.hypot(vx, vy) + 1
        m = min(90, 5200 / r)
        if r < 40: continue
        a = int(min(255, 40 + 9000 / r))
        d.line([(px, py), (px + vx / r * m, py + vy / r * m)], fill=(a // 2, a // 2 + 10, a // 2 + 25), width=1)
    for rr, al in [(70, 120), (128, 80), (196, 50)]:
        for k in range(9):
            a0 = k * 40 + RNG.uniform(0, 14)
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a0 + 28, fill=(al, al + 20, al + 60), width=2)
    ax, ay = 74, 300                                          # âncora: chapa de ferro na parede, que recebe o contragolpe
    d.rectangle([0, 150, 40, 450], fill=(38, 35, 31))
    d.rectangle([ax - 34, ay - 32, ax - 22, ay + 32], fill=(86, 80, 72))
    for k in range(8):
        a = math.radians(k * 26); L = RNG.uniform(40, 90); x0, y0 = ax - 28, ay
        for s in range(5):
            x1 = x0 - abs(math.cos(a)) * L / 9 + RNG.uniform(-3, 3); y1 = y0 + math.sin(a) * L / 5 + RNG.uniform(-4, 4)
            d.line([(x0, y0), (x1, y1)], fill=(4, 4, 4), width=2); x0, y0 = x1, y1
    for t in np.linspace(0, 1, 60):                            # elo: fio reto e tenso, com franjas
        x0, y0 = ax + (cx - ax) * t, ay + (cy - ay) * t
        c = (79, 139, 214) if int(t * 60) % 2 else (150, 190, 240)
        d.line([(x0, y0), (x0 + (cx - ax) / 60, y0 + (cy - ay) / 60)], fill=c, width=2)
    lay = np.asarray(im).astype(np.float32)
    return lente(glow(img, lay, 3), "#4F8BD6", 0.6)


def brasa():
    img = placa(); y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    fx, fy, tx, ty = 170, 300, 640, 300
    T = np.exp(-((x - tx) ** 2 + (y - ty) ** 2) / (2 * 62 ** 2))
    haze = np.exp(-((x - tx) ** 2) / (2 * 70 ** 2)) * np.clip((ty - y) / 260, 0, 1) * (y < ty)
    xs = x + 6 * np.sin(y / 9 + x / 31) * haze
    T2 = np.exp(-((xs - tx) ** 2 + (y - ty + 40) ** 2) / (2 * 80 ** 2)) * 0.35 * haze
    img = img * (1 - T[..., None]) + blackbody(T * 1.05)[...] * T[..., None] ** 0.6 + blackbody(T2 + 0.2) * T2[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for _ in range(170):                                       # fonte: o calor sai daqui, e fica geada
        a = RNG.uniform(0, 2 * math.pi); L = RNG.uniform(8, 60) * RNG.uniform(.3, 1)
        x0, y0 = fx + RNG.normal(0, 20), fy + RNG.normal(0, 20)
        c = int(RNG.uniform(150, 235)); d.line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L)], fill=(c - 20, c, 255), width=1)
    d.ellipse([fx - 16, fy - 16, fx + 16, fy + 16], outline=(170, 200, 230), width=2)
    for t in np.linspace(0, 1, 48):
        x0 = fx + 18 + (tx - 40 - fx - 18) * t
        c = blackbody(np.array(0.45 + 0.4 * t))
        if int(t * 48) % 2: c = c * 0.55
        d.line([(x0, fy), (x0 + (tx - 40 - fx) / 48, fy)], fill=tuple(int(v) for v in c), width=3)
    img = np.asarray(im).astype(np.float32)
    return lente(img, "#C8332F", 0.0)


def trama():
    img = placa(); y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    x0, x1, y0, y1 = 90, 854, 230, 480
    viga = (x > x0) & (x < x1) & (y > y0) & (y < y1)
    pedra = 48 + RNG.normal(0, 7, (H, W)) + 10 * np.sin(x / 37 + np.sin(y / 23) * 2)
    img = np.where(viga[..., None], np.stack([pedra, pedra * .96, pedra * .9], -1), img)
    px, py = 472, y0
    dx, dy = x - px, y - py; r = np.hypot(dx, dy) + 1e-3
    N = 2600 * (dy / r) / r                                    # Flamant: diferença das tensões principais ~ cosθ/r
    I = np.sin(math.pi * N) ** 2 * np.exp(-r / 420)
    ouro = hexrgb("#C9A15A")
    img = np.where((viga & (dy > 0))[..., None], img * (1 - .85 * I[..., None]) + ouro * 1.25 * I[..., None], img)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.polygon([(px - 22, y0 - 52), (px + 22, y0 - 52), (px, y0 - 2)], fill=(92, 86, 78))
    d.rectangle([x0 + 10, y1, x0 + 70, y1 + 26], fill=(60, 56, 50)); d.rectangle([x1 - 70, y1, x1 - 10, y1 + 26], fill=(60, 56, 50))
    cx, cy = 472, y1                                           # fissura que nasce embaixo, onde a tração é maior
    for k in range(5):
        xx, yy = cx + RNG.uniform(-6, 6), cy
        for s in range(9):
            nx, ny = xx + RNG.uniform(-9, 9), yy - RNG.uniform(6, 14)
            d.line([(xx, yy), (nx, ny)], fill=(10, 9, 8), width=2); xx, yy = nx, ny
    return lente(np.asarray(im).astype(np.float32), "#C9A15A", 1.2)


def clarao():
    img = placa(); y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    chao = np.clip((y - 330) / 270, 0, 1)
    c = np.zeros((H, W), np.float32)
    for k in range(5):
        a = RNG.uniform(0, math.pi); f = RNG.uniform(.035, .06)
        c += np.sin((x * math.cos(a) + y * 2.2 * math.sin(a)) * f + RNG.uniform(0, 6))
    caus = (1 - np.abs(c) / 5) ** 10
    mancha = np.exp(-(((x - 600) / 230) ** 2 + ((y - 470) / 95) ** 2))
    luz = caus * mancha * chao * 2.2 + mancha * chao * 0.25
    marfim = hexrgb("#F2E6C2")
    img = img * (1 - 0.45 * np.exp(-(((x - 230) / 160) ** 2 + ((y - 470) / 80) ** 2)) * chao)[..., None]   # onde a luz foi tirada
    img = img + marfim * luz[..., None]
    for (a0, b0), (a1, b1), w in [((0, 40), (330, 200), 46), ((330, 200), (600, 470), 70)]:
        n = np.array([b1 - b0, -(a1 - a0)], np.float32); n /= np.linalg.norm(n)
        t = np.clip(((x - a0) * (a1 - a0) + (y - b0) * (b1 - b0)) / ((a1 - a0) ** 2 + (b1 - b0) ** 2), 0, 1)
        dist = np.abs((x - a0) * n[0] + (y - b0) * n[1])
        feixe = np.exp(-(dist / w) ** 2) * (t > 0) * (t < 1) * 0.5
        borda = np.exp(-((dist - w * 1.05) / 2.2) ** 2) * (t > 0.02) * (t < .98)
        img = img + marfim * feixe[..., None] * 0.55
        fase = (dist - w * 1.05) / 2.2
        espectro = np.stack([np.clip(fase + .8, 0, 1), np.exp(-fase ** 2 * 2), np.clip(.8 - fase, 0, 1)], -1)
        img = img + espectro * 70 * borda[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.ellipse([306, 176, 354, 224], outline=(205, 190, 150), width=3)    # âncora óptica: lente de vidro
    return lente(np.asarray(im).astype(np.float32), "#F2E6C2", 2.0)


def eco():
    img = placa(); y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    s, ox, oy = 470, 240, 86
    pl = (x > ox) & (x < ox + s) & (y > oy) & (y < oy + s)
    met = 30 + 6 * np.sin(x / 3.1) * 0.2 + RNG.normal(0, 2, (H, W))
    img = np.where(pl[..., None], np.stack([met * .9, met * .95, met * 1.08], -1), img)
    n_, m_ = 3, 5
    pts = RNG.uniform(0, 1, (60000, 2))
    f = np.cos(n_ * np.pi * pts[:, 0]) * np.cos(m_ * np.pi * pts[:, 1]) - np.cos(m_ * np.pi * pts[:, 0]) * np.cos(n_ * np.pi * pts[:, 1])
    ok = RNG.uniform(0, 1, len(pts)) < np.exp(-(f / 0.07) ** 2)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for px, py in pts[ok]:
        X, Y = ox + px * s, oy + py * s; c = int(RNG.uniform(150, 225))
        d.point((X, Y), fill=(c - 25, c - 10, c + 20))
    d.rectangle([ox, oy, ox + s, oy + s], outline=(120, 118, 112), width=2)
    d.ellipse([ox + s / 2 - 7, oy + s / 2 - 7, ox + s / 2 + 7, oy + s / 2 + 7], fill=(150, 140, 120))   # haste que faz vibrar
    return lente(np.asarray(im).astype(np.float32), "#9FB7D6", 0.9)


def raio(d, a, b, larg, prof, cor):
    """Descarga com caminho: zigue-zague por deslocamento de ponto médio, com ramos."""
    pts = [a, b]
    for k in range(7):
        novo = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            L = math.hypot(q[0] - p[0], q[1] - p[1]) * 0.22
            novo += [(mx + RNG.normal(0, L), my + RNG.normal(0, L * .3)), q]
        pts = novo
    d.line(pts, fill=cor, width=larg)
    if prof > 0:
        for i in RNG.choice(len(pts) - 1, 4, replace=False):
            p = pts[i]; ang = RNG.uniform(-1.2, 1.2) + math.pi / 2
            L = RNG.uniform(40, 120) * (prof / 2)
            raio(d, p, (p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L), max(1, larg - 2), prof - 1, cor)


def carga():
    img = placa()
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    raio(d, (300, 70), (470, 410), 4, 2, (200, 215, 255))
    lay = np.asarray(im).astype(np.float32)
    core = Image.new("RGB", (W, H)); dc = ImageDraw.Draw(core)
    out = glow(img, lay * np.array([0.75, 0.85, 1.0]), 10)
    queim = Image.new("L", (W, H)); dq = ImageDraw.Draw(queim)
    for k in range(9):                                        # figura de Lichtenberg queimada no chão, em volta da terra
        a = math.radians(-180 + k * 22 + RNG.uniform(-8, 8))
        raio(dq, (470, 418), (470 + math.cos(a) * 200, 418 + abs(math.sin(a)) * 46 - 8), 2, 1, 255)
    q = np.asarray(queim.filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32)[..., None] / 255
    out = out * (1 - 0.6 * q) + np.array([70, 40, 20]) * q * 0.6
    im2 = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)); d2 = ImageDraw.Draw(im2)
    d2.rectangle([292, 30, 308, 74], fill=(150, 98, 54)); d2.rectangle([462, 410, 478, 440], fill=(150, 98, 54))   # origem e terra (cobre)
    return lente(np.asarray(im2).astype(np.float32), "#D7B46A", 2.5)


def escala():
    Wd, Hd = 940, 652
    im = Image.new("RGB", (Wd, Hd), (14, 13, 11)); d = ImageDraw.Draw(im)
    ouro = (201, 161, 90)
    cols = [(95, "Traço"), (280, "Par"), (465, "Nó"), (650, "Malha"), (840, "Campo")]
    def anc(x, y): d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=ouro, width=3)
    anc(60, 300); anc(130, 300); d.line([(67, 300), (123, 300)], fill=ouro, width=2)
    for yy in (250, 350): anc(245, yy); anc(315, yy); d.line([(252, yy), (308, yy)], fill=ouro, width=2)
    ch = [(420, 360), (455, 260), (490, 340), (520, 240)]
    for p, q in zip(ch, ch[1:]): d.line([p, q], fill=ouro, width=2)
    for p in ch: anc(*p)
    nos = [(590 + 45 * (i % 3) + (22 if (i // 3) % 2 else 0), 220 + 55 * (i // 3)) for i in range(12)]
    for i, p in enumerate(nos):
        for q in nos[i + 1:]:
            if math.dist(p, q) < 62: d.line([p, q], fill=ouro, width=1)
    for p in nos: anc(*p)
    g = Image.new("L", (Wd, Hd)); dg = ImageDraw.Draw(g)
    for i in range(90):
        p = (840 + RNG.normal(0, 38), 300 + RNG.normal(0, 70)); q = (p[0] + RNG.normal(0, 30), p[1] + RNG.normal(0, 30))
        dg.line([p, q], fill=200, width=1)
    gl = np.asarray(g.filter(ImageFilter.GaussianBlur(9))).astype(np.float32)[..., None] / 255
    arr = np.asarray(im).astype(np.float32) + np.array([255, 214, 140]) * gl * 1.6 + np.asarray(g).astype(np.float32)[..., None] / 255 * np.array(ouro) * .7
    return np.clip(arr, 0, 255)


def celulas():
    Wd, Hd = 680, 652
    im = Image.new("RGB", (Wd, Hd), (14, 13, 11)); d = ImageDraw.Draw(im)
    est = [(0.0, "fria"), (0.36, "carregando"), (0.66, "cheia"), (0.97, "saturada"), (-1, "queimada")]   # vermelho sujo, laranja vivo, branco
    lay = Image.new("RGB", (Wd, Hd)); dl = ImageDraw.Draw(lay)
    for i, (t, _) in enumerate(est):
        x = round((i + .5) * Wd / 5); y0, y1 = 150, 420
        base = (96, 88, 78) if t <= 0 else tuple(int(v) for v in blackbody(np.array(t)))
        d.rounded_rectangle([x - 40, y0, x + 40, y1], 18, fill=base, outline=(150, 128, 92), width=3)
        if t > 0: dl.rounded_rectangle([x - 40, y0, x + 40, y1], 18, fill=tuple(int(v * .8) for v in base))
        if t < 0:
            xx, yy = x - 8, y0
            for s in range(10):
                nx, ny = xx + RNG.uniform(-14, 14), yy + 23
                d.line([(xx, yy), (nx, ny)], fill=(12, 10, 9), width=3); xx, yy = nx, ny
            d.rectangle([x - 40, y1 - 30, x + 40, y1], fill=(40, 32, 26))
    arr = np.asarray(im).astype(np.float32)
    g = np.asarray(lay.filter(ImageFilter.GaussianBlur(16))).astype(np.float32)
    return np.clip(arr + g * 1.2, 0, 255)


def salva(nome, arr):
    p = f"{TMP}/{nome}.png"; Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(p); return f"file://{p}"


DISC = [("pulso", pulso, "Pulso", "movimento e impulso", "#4F8BD6",
         "Poeira e neve em estrias retas, anéis de choque no ar, e o contragolpe na âncora: chão trincado, bota que afunda."),
        ("brasa", brasa, "Brasa", "energia térmica", "#C8332F",
         "Ar que tremula, vapor, metal em brasa. O calor sempre sai de algum lugar: lá fica a geada."),
        ("trama", trama, "Trama", "ligações e tensões", "#C9A15A",
         "Pedra e metal que rangem; veios de tensão em faixas; fissuras que correm onde a tração é maior."),
        ("clarao", clarao, "Clarão", "luz", "#F2E6C2",
         "Luz real desviada por lente, espelho ou gelo: feixes, cáusticas, bordas de arco-íris. Onde a luz foi tirada, escurece."),
        ("eco", eco, "Eco", "vibração e ressonância", "#9FB7D6",
         "Figuras na poeira, na neve e na água; vidro que canta; sinos e pedras sintônicas."),
        ("carga", carga, "Carga", "cargas elétricas", "#D7B46A",
         "Arco branco-azulado com origem e terra, cheiro de ozônio, cabelo arrepiado, ramos queimados na superfície.")]


def prancha_8():
    b = []
    b.append(panel(0, 0, 1448, 128, img=A("06_personagens/PE-021_ilan_afericao.png"), pos="center 38%",
                   extra='<div class="img fade-r"></div>'
                         '<div style="position:absolute;left:30px;top:22px;z-index:4" class="h1"><span style="font-size:23px">LINGUAGEM VISUAL DA MAGIA ◆ TRANSPOSIÇÃO</span>'
                         '<div class="sc" style="font-size:11.5px;margin-top:6px;letter-spacing:3px">Fonte · Âncora · Elo · Destino · Controle · Retorno</div></div>'
                         '<div class="q" style="position:absolute;left:30px;top:84px;font-size:14px;z-index:4">A magia não sai das mãos: passa pelas coisas, e a conta sempre aparece.</div>'
                         '<div class="sc" style="position:absolute;left:30px;top:108px;font-size:8.5px;z-index:4;color:#9C8A66">Proposta · aguardando aprovação do autor</div>'))
    for i, (k, fn, nome, prop, cor, txt) in enumerate(DISC):
        x, y = 8 + (i % 3) * 480, 136 + (i // 3) * 308
        chip = (f'<div style="position:absolute;right:12px;top:8px;z-index:5;font-family:Cz;font-size:9px;letter-spacing:1.5px;color:#B8A887">'
                f'cor de leitura <span style="display:inline-block;width:13px;height:13px;vertical-align:-2px;background:{cor};border:1px solid #6B5532"></span> {cor}</div>')
        leg = (f'<div style="position:absolute;left:0;right:0;bottom:0;padding:22px 14px 9px;z-index:4;'
               f'background:linear-gradient(rgba(6,5,4,0),rgba(6,5,4,.92) 40%)" class="q"><span style="font-size:12.2px">{txt}</span></div>')
        b.append(panel(x, y, 472, 300, nome, salva(k, fn()), sub=prop, extra=chip + leg))
    b.append(panel(8, 752, 470, 326, "Escala", salva("escala", escala()), sub="a densidade dos elos é a vazão",
                   extra=labels(6, 268, 458, [("Traço", "um elo"), ("Par", "dois"), ("Nó", "encadeado"), ("Malha", "rede"), ("Campo", "território")], 40)))
    pq = lambda s: (f'<span style="font-size:7.6px;letter-spacing:.4px">{s}</span>', "")
    b.append(panel(486, 752, 340, 326, "Células da manopla", salva("celulas", celulas()), sub="o custo",
                   extra=labels(4, 268, 332, [pq(s) for s in ("fria", "carregando", "cheia", "saturada", "queimada")], 30)))
    b.append(panel(834, 752, 290, 326, "Limiares (divino)", A("09_engenharia_arcana/EA-006_transposicao_portal.png"), "center 45%", "",
                   '<div style="position:absolute;left:0;right:0;bottom:0;padding:26px 12px 9px;z-index:4;background:linear-gradient(rgba(6,5,4,0),rgba(6,5,4,.92) 40%)" class="q">'
                   '<span style="font-size:11.5px">Borda que acende num filete de ouro ou branco; o outro lugar, nítido, do outro lado do vão. Vento, neve e calor atravessam. Nada de redemoinho.</span></div>'))
    lst = lambda tit, it, cor: (f'<div class="sc" style="font-size:10.5px;color:{cor};margin:0 0 6px">{tit}</div><ul class="b">'
                                + "".join(f"<li>{t}</li>" for t in it) + "</ul>")
    b.append(panel(1132, 752, 308, 326, "", extra='<div style="position:absolute;left:16px;top:14px;right:12px">'
                   + lst("Sempre", ["fonte, âncora, elo e destino", "efeito físico de verdade", "linhas retas e tensas",
                                    "marcas técnicas a giz", "o custo no corpo ou no equipamento"], "#C9A15A")
                   + '<div style="height:12px"></div>'
                   + lst("Nunca", ["fumaça colorida das mãos", "runas e círculos genéricos", "portal em redemoinho",
                                   "bola de energia", "olhos brilhando em mortais", "luz sem fonte"], "#B5473F") + "</div>"))
    return shot("PR-08_linguagem_visual_da_magia", "".join(b))


if __name__ == "__main__":
    print(prancha_8())
