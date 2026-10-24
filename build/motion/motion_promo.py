#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Motion promocional de Leis para Matar Deuses (1920×1080, 30 fps, ~58 s, com trilha sintetizada).
Usa só artes do banco (exportacoes/banco_de_arte) e camadas extraídas por build/motion/extrair.py.
Saída: exportacoes/motion/LMD_motion_promocional_1080p.mp4"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance

ROOT = "/home/user/LTKG"; BA = f"{ROOT}/exportacoes/banco_de_arte"; C = f"{ROOT}/build/_motion"
OUT = f"{ROOT}/exportacoes/motion"; os.makedirs(OUT, exist_ok=True)
FT = f"{ROOT}/build/fonts"
W, H, FPS, DUR = 1920, 1080, 30, 58.0
NF = int(DUR * FPS)
random.seed(7)

# ------------------------------------------------------------------ utilidades
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eback(x, s=1.6): x -= 1; return 1 + x * x * ((s + 1) * x + s)
def env(t, a, b, c, d):   # 0 → 1 (a..b), 1 (b..c), 1 → 0 (c..d)
    return seg(t, a, b) * (1 - seg(t, c, d))

def L(name): return Image.open(f"{C}/{name}.png").convert("RGBA")
def LB(path): return Image.open(f"{BA}/{path}").convert("RGB")

_cache = {}
def xf(img, key, scale=1.0, rot=0.0, alpha=1.0):
    """Versão escalada/rotacionada/esmaecida de uma camada RGBA (com cache)."""
    k = (id(img), round(scale, 3), round(rot, 1), round(alpha * 40))
    if k in _cache: return _cache[k]
    im = img
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v, f=alpha: int(v * f)); im = im.copy(); im.putalpha(a)
    if len(_cache) > 1500: _cache.clear()
    _cache[k] = im
    return im

def put(canvas, img, key, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01: return
    im = xf(img, key, scale, rot, alpha)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def glow_of(img, radius=22, boost=1.6, tint=None):
    """Brilho pré-calculado: RGB pré-multiplicado e desfocado, para somar em modo 'tela'."""
    a = np.asarray(img).astype(np.float32); rgb = a[..., :3] * (a[..., 3:4] / 255)
    if tint is not None: rgb = np.dstack([np.full(rgb.shape[:2], c, np.float32) * a[..., 3] / 255 for c in tint])
    pad = radius * 3
    g = Image.fromarray(np.clip(rgb * boost, 0, 255).astype(np.uint8), "RGB")
    big = Image.new("RGB", (g.width + 2 * pad, g.height + 2 * pad)); big.paste(g, (pad, pad))
    return big.filter(ImageFilter.GaussianBlur(radius))

def screen(frame_rgb, glow, cx, cy, amount=1.0):
    if amount <= 0.01: return frame_rgb
    g = glow if amount >= 0.99 else ImageEnhance.Brightness(glow).enhance(amount)
    x0, y0 = int(cx - g.width / 2), int(cy - g.height / 2)
    box = (max(0, x0), max(0, y0), min(W, x0 + g.width), min(H, y0 + g.height))
    if box[2] <= box[0] or box[3] <= box[1]: return frame_rgb
    gc = g.crop((box[0] - x0, box[1] - y0, box[2] - x0, box[3] - y0))
    frame_rgb.paste(ImageChops.screen(frame_rgb.crop(box), gc), box[:2])
    return frame_rgb

def font(name, size): return ImageFont.truetype(f"{FT}/{name}", size)
def text_img(text, fname, size, fill=(226, 196, 126), track=0.0, shadow=True):
    f = font(fname, size); widths = [f.getlength(ch) for ch in text]
    tw = int(sum(widths) + track * size * (len(text) - 1)) + 20; th = int(size * 1.5)
    im = Image.new("RGBA", (tw + 40, th + 40)); d = ImageDraw.Draw(im)
    def draw(dx, dy, col):
        x = 20 + dx
        for ch, w in zip(text, widths):
            d.text((x, 20 + dy), ch, font=f, fill=col); x += w + track * size
    if shadow:
        sh = Image.new("RGBA", im.size); ds = ImageDraw.Draw(sh); x = 20
        for ch, w in zip(text, widths):
            ds.text((x, 22), ch, font=f, fill=(0, 0, 0, 230)); x += w + track * size
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    draw(0, 0, fill + (255,))
    return im.crop(im.getbbox())

def bg_prep(path, dark=0.55, blur=0, sat=1.0, tint=None, size=(2016, 1134)):
    im = LB(path)
    r = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    im = im.crop(((im.width - size[0]) // 2, (im.height - size[1]) // 2, (im.width - size[0]) // 2 + size[0], (im.height - size[1]) // 2 + size[1]))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if sat != 1.0: im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Brightness(im).enhance(dark)
    if tint: im = Image.blend(im, Image.new("RGB", im.size, tint), 0.18)
    return ImageChops.multiply(im, VIG.resize(im.size))

def vignette():
    y, x = np.mgrid[0:540, 0:960]; d = np.sqrt(((x - 480) / 480) ** 2 + ((y - 270) / 270) ** 2)
    v = np.clip(1.15 - 0.75 * d ** 1.6, 0.12, 1) * 255
    return Image.fromarray(np.dstack([v, v, v]).astype(np.uint8), "RGB")
VIG = vignette()

def kb(bg, t, t0, t1, z0=1.0, z1=1.05, dx=0, dy=0):
    """Ken Burns: recorte móvel do fundo pré-ampliado."""
    u = eio(seg(t, t0, t1)); z = z0 + (z1 - z0) * u
    cw, ch = bg.width / z * (W / bg.width) * (bg.width / W), 0
    cw = int(W * (bg.width / W) / z); ch = int(cw * H / W)
    cx = bg.width / 2 + dx * u; cy = bg.height / 2 + dy * u
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
    return bg.crop(box).resize((W, H), Image.BILINEAR)

def radial(rgb, r_frac=0.5, size=(W, H)):
    y, x = np.mgrid[0:size[1] // 2, 0:size[0] // 2]
    d = np.sqrt((x - size[0] / 4) ** 2 + (y - size[1] / 4) ** 2) / (size[1] / 4 * r_frac)
    a = np.clip(1 - d, 0, 1) ** 2
    im = Image.fromarray(np.dstack([a * c for c in rgb]).astype(np.uint8), "RGB")
    return im.resize(size, Image.BILINEAR)

# ------------------------------------------------------------------ partículas (brasas e poeira de ouro)
PART = [dict(x=random.uniform(0, W), y=random.uniform(0, H), vx=random.uniform(-8, 8), vy=random.uniform(-38, -10),
             s=random.uniform(1.2, 3.4), ph=random.uniform(0, 6.28), hot=random.random() < .35) for _ in range(150)]
def particles(canvas, t, amount=1.0, color=None):
    if amount <= 0.02: return
    ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
    for p in PART:
        x = (p["x"] + p["vx"] * t + 14 * math.sin(t * .7 + p["ph"])) % W
        y = (p["y"] + p["vy"] * t) % H
        a = int(255 * amount * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2.1 + p["ph"]))))
        col = color or ((255, 150, 70) if p["hot"] else (235, 205, 140))
        r = p["s"]; d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))
    canvas.alpha_composite(ov.filter(ImageFilter.GaussianBlur(0.8)))

# ------------------------------------------------------------------ recursos
print("preparando recursos…", flush=True)
BG1 = bg_prep("05_mundo/MU-001_cidade_de_limiar.png", .62)
BG2 = bg_prep("05_mundo/MU-008_a_confluencia.png", .30, blur=5, sat=.7)
BG3 = bg_prep("09_engenharia_arcana/EA-006_transposicao_portal.png", .32, blur=4, sat=.8)
BG5 = bg_prep("09_engenharia_arcana/EA-007_interdicao_carrascos.png", .78, sat=.75)
def pedra():
    rng = np.random.default_rng(3); a = np.zeros((567, 1008))
    for s, w in ((3, .5), (9, .3), (27, .2)):
        n = rng.standard_normal((567 // s + 2, 1008 // s + 2)); a += w * np.asarray(Image.fromarray(n.astype(np.float32)).resize((1008, 567), Image.BICUBIC))
    a = (a - a.min()) / (a.max() - a.min()); v = 10 + 26 * a
    im = Image.fromarray(np.dstack([v * 1.05, v, v * .9]).clip(0, 255).astype(np.uint8), "RGB").resize((2016, 1134), Image.BICUBIC)
    return ImageChops.multiply(im, VIG.resize(im.size))
BG6 = pedra()   # pedra negra procedural
BG7 = bg_prep("05_mundo/MU-001_cidade_de_limiar.png", .30, blur=3, sat=.6)
COVER = Image.open(f"{BA}/07_capas/CA-001_capa_vol1_o_deus_que_caiu_do_ceu.png").convert("RGBA")
LEIS = [L(f"lei{k}") for k in range(7)]; LEIS_G = [glow_of(i, 18, 1.3) for i in LEIS]
DISC = [L(f"disc{k}") for k in range(6)]; DISC_G = [glow_of(i, 26, 1.8) for i in DISC]
ETAP = [L(f"etapa{k}") for k in range(6)]; ETAP_G = [glow_of(i, 24, 1.5) for i in ETAP]
EM_E, EM_D, EM_C = L("emb_esq"), L("emb_dir"), L("emb_coluna")
PER = [L(f"perola{k}") for k in range(7)]
PER_XY = [tuple(map(int, l.split())) for l in open(f"{C}/perolas.txt").read().split("\n") if l.strip()]
EMB_FULL = Image.open(f"{BA}/01_identidade/ID-008_emblema_transparente.png").convert("RGBA")
LET = [L(f"letra{k}") for k in (2, 3, 4, 5)]
LET_Y = [35, 154, 283, 334]
LIGHT_GOLD = radial((255, 200, 120), 1.0); LIGHT_COL = {}

NOMES_LEIS = ["Conservação", "Vínculo", "Compatibilidade", "Vazão", "Dissipação", "Capacidade", "Retorno"]
FRASES_LEIS = ["Nada se cria.", "Tudo se conecta.", "O que não ressoa, rompe.", "Toda passagem tem limite.", "Nada permanece.", "Tudo tem limite.", "Toda ação retorna."]
ROM = ["I", "II", "III", "IV", "V", "VI", "VII"]
ETAPAS = ["Fonte", "Âncora", "Elo", "Destino", "Controle", "Retorno"]
DISC_N = [("Impetus", "Movimento", (80, 140, 230)), ("Igneo", "Transformação", (220, 70, 45)), ("Nexo", "Estrutura", (220, 175, 90)),
          ("Lume", "Revelação", (255, 240, 205)), ("Eco", "Ressonância", (160, 190, 230)), ("Fuso", "Acúmulo", (225, 185, 100))]
for _, _, col in DISC_N: LIGHT_COL[col] = radial(col, .85)

GOLD, SOFT, IVORY = (226, 196, 126), (200, 186, 158), (236, 228, 210)
T = {}
def tx(key, text, fname="Cinzel-SemiBold.ttf", size=40, fill=GOLD, track=0.12):
    if key not in T: T[key] = text_img(text, fname, size, fill, track)
    return T[key]
tx("a1", "Em Aresta, a magia não é milagre.", "EBGaramond-Italic.ttf", 58, IVORY, 0.0)
tx("a2", "É arquitetura.", "Cinzel-SemiBold.ttf", 64, GOLD, 0.18)
tx("l0", "Toda magia obedece a sete leis.", "EBGaramond-Italic.ttf", 50, IVORY, 0.0)
for k in range(7):
    tx(f"lr{k}", ROM[k], "Cinzel-SemiBold.ttf", 26, GOLD, 0.1)
    tx(f"ln{k}", NOMES_LEIS[k].upper(), "Cinzel-SemiBold.ttf", 19, GOLD, 0.08)
    tx(f"lf{k}", FRASES_LEIS[k], "EBGaramond-Italic.ttf", 23, SOFT, 0.0)
tx("t0", "Toda transposição segue um caminho.", "EBGaramond-Italic.ttf", 50, IVORY, 0.0)
for k in range(6): tx(f"tn{k}", ETAPAS[k].upper(), "Cinzel-SemiBold.ttf", 26, GOLD, 0.2)
tx("t1", "Nada se cria. Tudo retorna.", "Cinzel-SemiBold.ttf", 44, GOLD, 0.14)
tx("d0", "Seis disciplinas tornam a lei ação.", "EBGaramond-Italic.ttf", 50, IVORY, 0.0)
for k, (n, s, _) in enumerate(DISC_N):
    tx(f"dn{k}", n.upper(), "Cinzel-SemiBold.ttf", 26, GOLD, 0.2); tx(f"ds{k}", s, "EBGaramond-Italic.ttf", 24, SOFT, 0.0)
tx("p0", "Mas toda lei cobra o seu preço.", "EBGaramond-Italic.ttf", 56, IVORY, 0.0)
tx("p1", "Onde os Carrascos passam, a magia se cala.", "Cinzel-SemiBold.ttf", 38, (225, 120, 105), 0.1)
tx("e0", "VOLUME I", "Cinzel-SemiBold.ttf", 30, GOLD, 0.5)
tx("e1", "O Deus que Caiu do Céu", "EBGaramond-Italic.ttf", 66, IVORY, 0.0)
tx("e2", "WERIK MARTINS", "Cinzel-SemiBold.ttf", 34, GOLD, 0.4)
tx("e3", "Saga Aresta", "EBGaramond-Italic.ttf", 34, SOFT, 0.0)
LET_END = [i for i in LET]

# ------------------------------------------------------------------ cenas
def scene_abertura(t):
    f = kb(BG1, t, 0, 6, 1.0, 1.07, 0, -30)
    f = ImageEnhance.Brightness(f).enhance(0.15 + 0.85 * eo(seg(t, 0.4, 3.2)))
    c = f.convert("RGBA"); particles(c, t, .9)
    put(c, T["a1"], "a1", W / 2, 470 - 10 * eo(seg(t, .6, 2)), alpha=env(t, .6, 1.8, 4.5, 5.2))
    put(c, T["a2"], "a2", W / 2, 580 - 10 * eo(seg(t, 2.4, 3.4)), alpha=env(t, 2.4, 3.3, 4.6, 5.2))
    return c

def scene_leis(t):
    c = kb(BG2, t, 5, 15.5, 1.03, 1.0).convert("RGBA"); particles(c, t, .6)
    put(c, T["l0"], "l0", W / 2, 150, alpha=env(t, 5.2, 6.0, 14.8, 15.5))
    f = c.convert("RGB")
    xs = [W / 2 + (k - 3) * 258 for k in range(7)]
    for k in range(7):
        t0 = 6.0 + k * 1.15; a = env(t, t0, t0 + .5, 14.8, 15.5)
        s = 0.5 + 0.06 * eo(seg(t, t0, t0 + .7))
        pulse = 0.9 * (1 - seg(t, t0, t0 + 1.0)) + 0.35 * env(t, 14.0, 14.3, 14.4, 15.0)
        if a > 0: f = screen(f, xf(LEIS_G[k].convert("RGBA"), f"lg{k}", s).convert("RGB"), xs[k], 520, pulse * a)
    c = f.convert("RGBA")
    for k in range(7):
        t0 = 6.0 + k * 1.15; a = env(t, t0, t0 + .5, 14.8, 15.5)
        s = 0.5 + 0.06 * eo(seg(t, t0, t0 + .7))
        put(c, LEIS[k], f"l{k}", xs[k], 520 + 20 * (1 - eo(seg(t, t0, t0 + .7))), s, alpha=a)
        put(c, T[f"lr{k}"], f"lr{k}", xs[k], 772, alpha=a * seg(t, t0 + .2, t0 + .7))
        put(c, T[f"ln{k}"], f"ln{k}", xs[k], 808, alpha=a * seg(t, t0 + .3, t0 + .8))
        put(c, T[f"lf{k}"], f"lf{k}", xs[k], 842, alpha=a * seg(t, t0 + .5, t0 + 1.0))
    return c

ETX = [W / 2 + (k - 2.5) * 290 for k in range(6)]; ETY = [470 - 50 * math.sin(math.pi * k / 5) for k in range(6)]
def path_pts(n_seg=40):
    pts = []
    for k in range(5):
        for i in range(n_seg):
            u = i / n_seg; pts.append((ETX[k] + (ETX[k + 1] - ETX[k]) * u, ETY[k] + (ETY[k + 1] - ETY[k]) * u))
    pts.append((ETX[5], ETY[5]))
    back = [(W / 2 + 725 * math.cos(a), 600 + 150 * math.sin(a)) for a in np.linspace(0, math.pi, 80)]
    return pts, back
PATH, BACK = path_pts()

def scene_transposicao(t):
    c = kb(BG3, t, 15.5, 28.5, 1.0, 1.06, 0, 20).convert("RGBA"); particles(c, t, .45, (150, 190, 255))
    put(c, T["t0"], "t0", W / 2, 140, alpha=env(t, 15.7, 16.4, 27.8, 28.5))
    hop = 1.25; t0 = 16.6
    prog = clamp((t - t0) / (hop * 5)) * (len(PATH) - 1)
    d = ImageDraw.Draw(c)
    fade = 1 - seg(t, 27.8, 28.5)
    if t >= t0:   # trilha percorrida
        n = int(prog) + 1
        d.line(PATH[:max(2, n)], fill=(240, 205, 130, int(200 * fade)), width=3)
    tb0 = t0 + hop * 5 + .3; bp = clamp((t - tb0) / 2.2)
    if bp > 0:
        nb = max(2, int(bp * (len(BACK) - 1)) + 1)
        d.line(BACK[::-1][:nb], fill=(120, 170, 255, int(170 * fade)), width=3)
    f = c.convert("RGB")
    for k in range(6):
        reach = t0 + hop * k; a = env(t, 15.9 + k * .12, 16.5 + k * .12, 27.8, 28.5)
        act = 1 - seg(t, reach, reach + 1.1) if t >= reach else 0
        f = screen(f, ETAP_G[k], ETX[k], ETY[k], a * (0.25 + 1.1 * act + (0.8 if k == 0 and bp >= 1 else 0) * env(t, tb0 + 2.2, tb0 + 2.4, tb0 + 2.6, tb0 + 3.4)))
    c = f.convert("RGBA")
    for k in range(6):
        reach = t0 + hop * k; a = env(t, 15.9 + k * .12, 16.5 + k * .12, 27.8, 28.5)
        lit = seg(t, reach, reach + .25)
        put(c, ETAP[k], f"e{k}", ETX[k], ETY[k], 0.92 + 0.08 * lit, alpha=a * (0.45 + 0.55 * lit))
        put(c, T[f"tn{k}"], f"tn{k}", ETX[k], ETY[k] + 175, alpha=a * seg(t, reach, reach + .5))
    # o orbe de energia
    if t0 <= t <= tb0 + 2.2:
        if t < tb0: i = min(int(prog), len(PATH) - 1); ox, oy = PATH[i]
        else: i = min(int(bp * (len(BACK) - 1)), len(BACK) - 1); ox, oy = BACK[::-1][i]
        orb = Image.new("RGBA", (120, 120)); od = ImageDraw.Draw(orb)
        for r, al in ((44, 40), (28, 90), (14, 200), (7, 255)):
            od.ellipse((60 - r, 60 - r, 60 + r, 60 + r), fill=(255, 240, 205, al))
        c.alpha_composite(orb.filter(ImageFilter.GaussianBlur(3)), (int(ox - 60), int(oy - 60)))
    put(c, T["t1"], "t1", W / 2, 860, alpha=env(t, tb0 + 1.4, tb0 + 2.2, 27.8, 28.5))
    return c

def scene_disciplinas(t):
    base = Image.new("RGB", (W, H), (8, 7, 6)); f = ImageChops.multiply(base, VIG.resize((W, H)))
    xs = [W / 2 + (k - 2.5) * 290 for k in range(6)]; y = 500
    for k, (_, _, col) in enumerate(DISC_N):
        t0 = 29.2 + k * 1.0
        f = screen(f, LIGHT_COL[col], xs[k], y, 0.55 * env(t, t0, t0 + .15, t0 + .4, t0 + 1.3))
    c = f.convert("RGBA"); particles(c, t, .35)
    put(c, T["d0"], "d0", W / 2, 140, alpha=env(t, 28.6, 29.2, 35.4, 36.0))
    d = ImageDraw.Draw(c)
    for k, (_, _, col) in enumerate(DISC_N):   # anel de onda (Eco ganha três)
        t0 = 29.2 + k * 1.0
        for j in range(3 if k == 4 else 1):
            u = seg(t, t0 + j * .22, t0 + 1.1 + j * .22)
            if 0 < u < 1:
                r = 60 + 230 * eo(u); al = int(200 * (1 - u))
                d.ellipse((xs[k] - r, y - r, xs[k] + r, y + r), outline=col + (al,), width=3)
    f = c.convert("RGB")
    for k in range(6):
        t0 = 29.2 + k * 1.0; a = env(t, 28.8 + k * .08, 29.3 + k * .08, 35.4, 36.0)
        f = screen(f, DISC_G[k], xs[k], y, a * (0.25 + 1.2 * env(t, t0, t0 + .1, t0 + .35, t0 + 1.1)))
    c = f.convert("RGBA")
    for k in range(6):
        t0 = 29.2 + k * 1.0; a = env(t, 28.8 + k * .08, 29.3 + k * .08, 35.4, 36.0)
        hit = env(t, t0, t0 + .08, t0 + .2, t0 + .6)
        put(c, DISC[k], f"d{k}", xs[k], y, 0.72 + 0.06 * hit, alpha=a * (0.55 + 0.45 * seg(t, t0, t0 + .2)))
        put(c, T[f"dn{k}"], f"dn{k}", xs[k], 800, alpha=a * seg(t, t0, t0 + .4))
        put(c, T[f"ds{k}"], f"ds{k}", xs[k], 838, alpha=a * seg(t, t0 + .2, t0 + .6))
    return c

def scene_preco(t):
    f = kb(BG5, t, 36, 41.5, 1.0, 1.09, 40, -10)
    f = ImageEnhance.Brightness(f).enhance(eo(seg(t, 36.0, 36.8)) * (1 - 0.8 * seg(t, 40.6, 41.4)))
    c = f.convert("RGBA")
    put(c, T["p0"], "p0", W / 2, 420, alpha=env(t, 36.4, 37.2, 39.4, 40.0))
    put(c, T["p1"], "p1", W / 2, 520, alpha=env(t, 38.0, 38.8, 40.6, 41.3))
    # glifos das leis se apagando sob a linha vermelha da interdição
    sweep = seg(t, 38.0, 40.2) * (W + 400) - 200
    for k in range(7):
        x = W / 2 + (k - 3) * 170
        a = env(t, 36.6, 37.4, 40.4, 41.0) * (0.15 if x < sweep else 0.75)
        put(c, LEIS[k], f"lp{k}", x, 860, 0.17, alpha=a)
    if 38.0 <= t <= 40.4:
        d = ImageDraw.Draw(c); d.line([(sweep, 760), (sweep, 960)], fill=(200, 40, 40, 210), width=3)
    return c

EMB_S = 0.60; EMB_TOP = 34; ECX = W / 2
def emb_pos(px, py): return ECX + (px - 512) * EMB_S, EMB_TOP + py * EMB_S
def scene_logo(t):
    f = kb(BG6, t, 41, 52, 1.04, 1.0)
    f = ImageEnhance.Brightness(f).enhance(eo(seg(t, 41.0, 41.8)))
    f = screen(f, LIGHT_GOLD, W / 2, 340, 0.55 * eo(seg(t, 41.2, 43.4)) + 0.4 * env(t, 43.35, 43.45, 43.6, 44.6))
    c = f.convert("RGBA"); particles(c, t, .55 + .4 * env(t, 43.3, 43.5, 43.7, 45))
    shake = 6 * math.sin(t * 90) * env(t, 43.35, 43.4, 43.5, 43.9)
    cy0 = EMB_TOP + 512 * EMB_S + shake
    u = seg(t, 42.0, 43.4)
    if u > 0:
        k = eback(u, 1.3)
        put(c, EM_E, "ee", ECX - 640 * (1 - k), cy0, EMB_S, -9 * (1 - k), alpha=clamp(u * 2.5))
        put(c, EM_D, "ed", ECX + 640 * (1 - k), cy0, EMB_S, 9 * (1 - k), alpha=clamp(u * 2.5))
    v = seg(t, 43.4, 44.5)
    if v > 0:   # coluna desce e se revela de cima para baixo
        col = xf(EM_C, "ec", EMB_S)
        hh = int(col.height * eo(v)); cut = col.crop((0, 0, col.width, max(1, hh)))
        c.alpha_composite(cut, (int(ECX - col.width / 2), int(cy0 - col.height / 2 - 30 * (1 - eo(v)))))
    for k, (px, py) in enumerate(PER_XY):   # sete pérolas, de cima para baixo
        tp = 44.5 + k * 0.28; w_ = seg(t, tp, tp + .45)
        if w_ > 0:
            sc = EMB_S * (eback(w_, 2.2) if w_ < 1 else 1.0)
            p = PER[k]; x, y = emb_pos(px + p.width / 2, py + p.height / 2)
            put(c, p, f"p{k}", x, y + shake, max(.05, sc), alpha=clamp(w_ * 3))
    f = c.convert("RGB")
    for k, (px, py) in enumerate(PER_XY):
        tp = 44.5 + k * 0.28; x, y = emb_pos(px + PER[k].width / 2, py + PER[k].height / 2)
        f = screen(f, PER_G, x, y, 0.9 * env(t, tp, tp + .1, tp + .2, tp + .8))
    # brilho que varre o emblema
    for ts in (46.6, 50.2):   # reflexo diagonal que corre só sobre o metal do emblema
        g = seg(t, ts, ts + 1.0)
        if 0 < g < 1:
            yy, xx = np.mgrid[0:270, 0:480].astype(np.float32) * 4
            pos = -300 + (W + 600) * eio(g)
            band = np.exp(-(((xx - pos) + (yy - 340) * 0.35) / 90) ** 2) * (1 - abs(2 * g - 1)) ** .5
            bm = Image.fromarray((band * 255).astype(np.uint8), "L").resize((W, H), Image.BILINEAR)
            m = ImageChops.multiply(bm, EMB_MASK)
            glint = Image.merge("RGB", [m.point(lambda v, c=c: int(v * c / 255)) for c in (255, 228, 170)])
            f = ImageChops.screen(f, glint)
    c = f.convert("RGBA")
    if t > 46.6:   # reaplica o emblema por cima da varredura para não lavar o metal
        pass
    # lettering
    Ls = 0.62; LX = W / 2; LY0 = 628
    for k, (img, y0) in enumerate(zip(LET, LET_Y)):
        ts = [47.0, 47.6, 48.3, 48.7][k]; a = seg(t, ts, ts + .6)
        if a <= 0: continue
        y = LY0 + (y0 + img.height / 2) * Ls
        if k == 2:   # filete se desenha a partir do centro
            im = xf(img, "lt2", Ls); w2 = max(2, int(im.width * eo(a)))
            c.alpha_composite(im.crop(((im.width - w2) // 2, 0, (im.width + w2) // 2, im.height)), (int(LX - w2 / 2), int(y - im.height / 2)))
        elif k == 1:
            put(c, img, "lt1", LX, y, Ls * (1.08 - 0.08 * eo(a)), alpha=eo(a))
        else:
            put(c, img, f"lt{k}", LX, y + 18 * (1 - eo(a)), Ls, alpha=eo(a))
    fo = seg(t, 51.4, 52.2)
    if fo > 0: c = Image.blend(c, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fo)
    return c

def scene_final(t):
    f = kb(BG7, t, 52, 58, 1.0, 1.05)
    f = ImageEnhance.Brightness(f).enhance(eo(seg(t, 52.0, 52.8)))
    c = f.convert("RGBA"); particles(c, t, .5)
    a = eo(seg(t, 52.4, 53.4))
    put(c, COVER, "cov", 600 - 60 * (1 - a), 540, 0.56, alpha=a)
    put(c, LET[0], "fl0", 1270, 330, 0.62, alpha=eo(seg(t, 52.8, 53.5)))
    put(c, LET[1], "fl1", 1270, 404, 0.62, alpha=eo(seg(t, 52.9, 53.6)))
    put(c, LET[3], "fl3", 1270, 470, 0.62, alpha=eo(seg(t, 53.1, 53.8)))
    put(c, T["e0"], "e0", 1270, 600, alpha=eo(seg(t, 53.5, 54.2)))
    put(c, T["e1"], "e1", 1270, 668, alpha=eo(seg(t, 53.7, 54.4)))
    put(c, T["e2"], "e2", 1270, 790, alpha=eo(seg(t, 54.2, 54.9)))
    fo = seg(t, 57.0, 58.0)
    if fo > 0: c = Image.blend(c, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fo)
    return c

PER_G = glow_of(PER[0], 14, 2.2)
EMB_MASK = Image.new("L", (W, H), 0)
_em = EMB_FULL.resize((int(1024 * EMB_S), int(1024 * EMB_S)), Image.LANCZOS).getchannel("A")
EMB_MASK.paste(_em, (int(ECX - _em.width / 2), int(EMB_TOP)))
SWEEP = (lambda: (lambda g: g.resize((520, 1100)).filter(ImageFilter.GaussianBlur(40)))(
    Image.fromarray((np.clip(1 - np.abs(np.linspace(-1, 1, 260))[None, :] * 1.0, 0, 1)[..., None] * np.array([90, 75, 45])[None, None, :]
                     * np.ones((550, 1, 1))).astype(np.uint8), "RGB").rotate(-18, expand=False)))()

def frame(i):
    t = i / FPS
    if t < 5.2: c = scene_abertura(t)
    elif t < 15.5: c = scene_leis(t)
    elif t < 28.5: c = scene_transposicao(t)
    elif t < 36.0: c = scene_disciplinas(t)
    elif t < 41.5: c = scene_preco(t)
    elif t < 52.2: c = scene_logo(t)
    else: c = scene_final(t)
    # transições curtas por preto entre cenas
    for tc in (5.2, 15.5, 28.5, 36.0, 41.5):
        k = 1 - abs(t - tc) / 0.35
        if k > 0: c = Image.blend(c, Image.new("RGBA", (W, H), (0, 0, 0, 255)), clamp(k) * .85)
    return c.convert("RGB")

# ------------------------------------------------------------------ trilha sonora sintetizada
def trilha(path):
    from scipy.signal import fftconvolve, butter, lfilter
    sr = 48000; n = int(DUR * sr); tt = np.arange(n) / sr; out = np.zeros(n)
    def add(sig, at, gain=1.0):
        s = int(at * sr); e = min(n, s + len(sig)); out[s:e] += sig[:e - s] * gain
    def bell(f0, dur=2.4, gain=.25):
        x = np.arange(int(dur * sr)) / sr
        return gain * sum(a * np.sin(2 * np.pi * f0 * m * x) * np.exp(-x * (2.2 + m)) for m, a in ((1, 1), (2.76, .5), (5.4, .25), (8.93, .12)))
    def boom(dur=2.2, f0=70, f1=28, gain=.9):
        x = np.arange(int(dur * sr)) / sr; f = f1 + (f0 - f1) * np.exp(-x * 3)
        ph = 2 * np.pi * np.cumsum(f) / sr
        nz = np.random.randn(len(x)) * np.exp(-x * 9) * .25
        return gain * (np.sin(ph) * np.exp(-x * 1.6) + nz)
    def whoosh(dur=1.0, gain=.25, hi=False):
        x = np.arange(int(dur * sr)) / sr; nz = np.random.randn(len(x))
        b, a = butter(2, [800 / (sr / 2), (6000 if hi else 2500) / (sr / 2)], btype="band"); nz = lfilter(b, a, nz)
        return gain * nz * np.sin(np.pi * x / dur) ** 2
    # drone em ré menor, com respiração lenta
    dr = sum(a * np.sin(2 * np.pi * f * tt + p) for f, a, p in ((36.7, .5, 0), (55.0, .35, 1), (73.4, .25, 2), (110.0, .08, .5)))
    dr *= (0.55 + 0.45 * np.sin(2 * np.pi * tt / 7.5)) * np.interp(tt, [0, 4, 36, 38.5, 41, 47, 55, 58], [0, .55, .7, .35, .9, 1.0, .7, 0])
    out += dr * .32
    air = lfilter(*butter(2, [2000 / (sr / 2), 9000 / (sr / 2)], btype="band"), np.random.randn(n)) * .02
    out += air * np.interp(tt, [0, 5, 41, 47, 58], [0, 1, 1, 1.6, 0])
    esc = [293.7, 349.2, 440.0, 523.3, 587.3, 659.3, 698.5]
    add(boom(2.5, 60, 30, .5), 0.4); add(whoosh(1.4, .18), 2.2)
    for k in range(7): add(bell(esc[k], 2.6, .22), 6.0 + k * 1.15)
    add(bell(880, 3.0, .12), 14.0)
    for k in range(6): add(bell(esc[k % 7] / 2, 1.8, .2), 16.6 + 1.25 * k); add(whoosh(.9, .1, True), 16.6 + 1.25 * k + .2)
    add(whoosh(2.2, .2), 23.4); add(bell(587.3, 3.2, .25), 25.9); add(boom(1.8, 90, 40, .35), 25.9)
    for k in range(6):
        t0 = 29.2 + k * 1.0
        if k == 0: add(whoosh(.5, .35, True), t0)
        elif k == 1: add(np.random.randn(int(.8 * sr)) * (np.random.rand(int(.8 * sr)) > .996) * .5, t0); add(boom(.8, 120, 60, .3), t0)
        elif k == 2: add(bell(220, 1.2, .3), t0)
        elif k == 3: add(bell(1318.5, 1.6, .22), t0); add(whoosh(.4, .25, True), t0)
        elif k == 4:
            for j in range(4): add(bell(440, 1.2, .2 * .55 ** j), t0 + j * .22)
        else:
            x = np.arange(int(1 * sr)) / sr; add(.18 * np.sin(2 * np.pi * (180 + 300 * x) * x) * np.exp(-x * 2.5), t0)
    add(boom(2.6, 55, 25, .7), 36.1); add(whoosh(2.4, .15), 38.0)
    x = np.arange(int(2.4 * sr)) / sr; add(.25 * np.sin(2 * np.pi * (90 * x + 140 * x * x)) * (x / 2.4) ** 2, 41.0); add(whoosh(2.4, .3) * np.linspace(0, 1, int(2.4 * sr)), 41.0)
    add(boom(3.0, 75, 26, 1.0), 43.4); add(bell(110, 3.5, .35), 43.4); add(bell(155.6, 3.5, .2), 43.4)
    add(whoosh(1.0, .2), 43.4)
    for k in range(7): add(bell(esc[k] * 2, 1.6, .16), 44.5 + k * .28)
    add(whoosh(1.0, .15, True), 46.6); add(boom(2.6, 65, 28, .8), 47.6); add(bell(293.7, 4.5, .3), 47.6); add(bell(440, 4.5, .18), 47.6)
    add(whoosh(1.0, .12, True), 50.2); add(boom(3.5, 55, 25, .55), 52.4); add(bell(587.3, 5, .2), 53.7)
    ir = np.random.randn(int(2.4 * sr)) * np.exp(-np.arange(int(2.4 * sr)) / sr * 2.6) * .05
    wet = fftconvolve(out, ir)[:n]
    mixL = out + wet; mixR = np.roll(out, 240) + np.roll(wet, 900)
    st = np.vstack([mixL, mixR]).T; st *= np.interp(tt, [0, 0.3, 57, 58], [0, 1, 1, 0])[:, None]
    st = np.tanh(st / np.abs(st).max() * 1.6) * .89
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if "--teste" in sys.argv:
        for ts in [float(x) for x in sys.argv[2:]]:
            frame(int(ts * FPS)).save(f"{C}/teste_{ts:05.1f}.jpg", quality=85)
        sys.exit()
    wav = f"{C}/trilha.wav"; trilha(wav); print("trilha ok", flush=True)
    vid = f"{C}/video.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame(i).tobytes())
        if i % 150 == 0: print(f"quadro {i}/{NF}", flush=True)
    p.stdin.close(); p.wait()
    final = f"{OUT}/LMD_motion_promocional_1080p.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", final], check=True)
    frame(int(50.0 * FPS)).save(f"{OUT}/LMD_motion_quadro_logo.jpg", quality=92)
    print(final)
