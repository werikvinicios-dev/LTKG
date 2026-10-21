# -*- coding: utf-8 -*-
"""Motor das animações canônicas da magia: fundo de grafite, tinta (traço), luz (com brilho), elos com franjas,
âncoras, células da manopla, figuras-pictograma, raios, vapor, geada, legendas e trilha sintetizada.
Segue o GUIA_VISUAL_DA_MAGIA (efeito físico, âncoras, elo como franjas na cor de leitura, custo à vista)."""
import math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance

ROOT = "/home/user/LTKG"; BA = f"{ROOT}/exportacoes/banco_de_arte"; FT = f"{ROOT}/build/fonts"
TMP = f"{ROOT}/build/_magia_motion"; os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1920, 1080, 30

GOLD, IVORY, MUTED, DARK = (201, 161, 90), (233, 224, 204), (156, 138, 102), (12, 11, 10)
BRASA, AMBER, PULSO, ECO = (200, 51, 47), (240, 150, 50), (79, 139, 214), (159, 183, 214)
RAIO, CARGA, TRAMA, CLARAO = (200, 215, 255), (215, 180, 106), (201, 161, 90), (242, 230, 194)
FROST, COBRE, BRONZE, PRATA, GELO = (190, 215, 240), (184, 115, 51), (176, 138, 74), (205, 210, 222), (120, 150, 175)


# ------------------------------------------------------------------ tempo
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def env(t, a, b, c, d): return seg(t, a, b) * (1 - seg(t, c, d))
def lerp(a, b, u): return a + (b - a) * u
def lerp2(p, q, u): return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
def mul(c, k): return tuple(int(clamp(v * k, 0, 255)) for v in c)


def blackbody(t):
    pts = [(0, (0, 0, 0)), (.3, (105, 22, 12)), (.5, (196, 52, 22)), (.68, (238, 126, 40)), (.84, (255, 196, 108)), (1, (255, 246, 222))]
    t = clamp(t)
    for (a, ca), (b, cb) in zip(pts, pts[1:]):
        if a <= t <= b:
            u = (t - a) / (b - a); return tuple(int(x + (y - x) * u) for x, y in zip(ca, cb))
    return pts[-1][1]


# ------------------------------------------------------------------ fundo e composição
def _placa():
    rng = np.random.default_rng(3)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    v = np.clip(1.08 - 0.62 * (((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) ** 0.9, 0.25, 1)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 18) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) - 128
    base = np.stack([17 + n * .12, 16 + n * .11, 14 + n * .1], -1) * v[..., None]
    grade = ((x % 120) < 1.2) | ((y % 120) < 1.2)
    base[grade] += np.array([10, 8, 4]) * v[grade][..., None]
    return Image.fromarray(np.clip(base + rng.normal(0, 1.6, (H, W, 1)), 0, 255).astype(np.uint8))
PLACA = _placa()


class Quadro:
    """Um quadro: fundo + tinta (RGBA, traço) + luz (RGB aditiva, com brilho) + fumaça (RGBA)."""
    def __init__(self, fundo=None):
        self.base = (fundo or PLACA).copy()
        self.tinta = Image.new("RGBA", (W, H)); self.dt = ImageDraw.Draw(self.tinta)
        self.luz = Image.new("RGB", (W, H)); self.dl = ImageDraw.Draw(self.luz)
        self.fumo = Image.new("RGBA", (W, H))
        self.topo = Image.new("RGBA", (W, H)); self.dtop = ImageDraw.Draw(self.topo)

    def render(self, bloom=1.0):
        img = self.base.convert("RGBA"); img.alpha_composite(self.fumo); img.alpha_composite(self.tinta)
        img = img.convert("RGB")
        if bloom > 0:
            g1 = self.luz.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
            g2 = self.luz.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
            g = ImageChops.add(ImageEnhance.Brightness(g1).enhance(1.3 * bloom), ImageEnhance.Brightness(g2).enhance(1.1 * bloom))
            img = ImageChops.screen(img, g)
        img = ImageChops.add(img, self.luz)
        img = img.convert("RGBA"); img.alpha_composite(self.topo)
        return img.convert("RGB")


# ------------------------------------------------------------------ pinturas do banco (abertura de cada cena)
_bgcache = {}
def pintura(path, dark=0.62):
    if path in _bgcache: return _bgcache[path]
    im = Image.open(f"{BA}/{path}").convert("RGB"); size = (2112, 1188)
    r = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    im = im.crop(((im.width - size[0]) // 2, (im.height - size[1]) // 2, (im.width - size[0]) // 2 + size[0], (im.height - size[1]) // 2 + size[1]))
    im = ImageEnhance.Brightness(im).enhance(dark)
    _bgcache[path] = im; return im


def kenburns(bg, u, z0=1.0, z1=1.08, dx=0, dy=0):
    z = lerp(z0, z1, eio(u)); cw = int(bg.width / z / 1.1); ch = int(cw * H / W)
    cx, cy = bg.width / 2 + dx * u, bg.height / 2 + dy * u
    return bg.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)).resize((W, H), Image.BILINEAR)


# ------------------------------------------------------------------ texto
_fc, _tc = {}, {}
def fonte(nome, tam):
    k = (nome, tam)
    if k not in _fc: _fc[k] = ImageFont.truetype(f"{FT}/{nome}", tam)
    return _fc[k]


def texto(s, nome="Cinzel-SemiBold.ttf", tam=30, cor=GOLD, track=0.08, sombra=True):
    k = (s, nome, tam, cor, track)
    if k in _tc: return _tc[k]
    f = fonte(nome, tam); ws = [f.getlength(ch) for ch in s]
    tw = int(sum(ws) + track * tam * max(0, len(s) - 1)) + 40; th = int(tam * 1.6) + 30
    im = Image.new("RGBA", (tw, th)); d = ImageDraw.Draw(im)
    def escreve(dd, ox, oy, c):
        x = 20 + ox
        for ch, w in zip(s, ws): dd.text((x, 12 + oy), ch, font=f, fill=c); x += w + track * tam
    if sombra:
        sh = Image.new("RGBA", im.size); escreve(ImageDraw.Draw(sh), 0, 2, (0, 0, 0, 235)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    escreve(d, 0, 0, cor + (255,))
    im = im.crop(im.getbbox()); _tc[k] = im; return im


def cola(q, im, x, y, alpha=1.0, ancora="lt"):
    if alpha <= 0.01: return
    if alpha < 0.99:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    if ancora[0] == "c": x -= im.width // 2
    elif ancora[0] == "r": x -= im.width
    if ancora[1] == "c": y -= im.height // 2
    elif ancora[1] == "b": y -= im.height
    q.topo.alpha_composite(im, (int(x), int(y)))


def rotulo(q, t, t0, t1, s, x, y, ponto=None, tam=24, cor=IVORY, ancora="lt"):
    """Etiqueta que aparece e some, com filete até o ponto descrito."""
    a = env(t, t0, t0 + .35, t1 - .35, t1)
    if a <= 0: return
    if ponto:
        q.dtop.line([ponto, (x, y + 16)], fill=MUTED + (int(200 * a),), width=2)
        q.dtop.ellipse([ponto[0] - 4, ponto[1] - 4, ponto[0] + 4, ponto[1] + 4], outline=GOLD + (int(255 * a),), width=2)
    cola(q, texto(s, "Cinzel-SemiBold.ttf", tam, cor, .06), x, y, a, ancora)


def cabecalho(q, t, nome, sub, t0, t1):
    a = env(t, t0, t0 + .5, t1 - .4, t1)
    cola(q, texto(nome, "Cinzel-Bold.ttf", 34, GOLD, .14), 60, 40, a)
    cola(q, texto(sub, "Cinzel-SemiBold.ttf", 19, MUTED, .14), 62, 92, a)


def lei(q, t, s, t0, t1):
    a = env(t, t0, t0 + .5, t1 - .4, t1)
    if a <= 0: return
    q.dtop.rectangle([0, H - 96, W, H], fill=(6, 5, 4, int(170 * a)))
    cola(q, texto(s, "EBGaramond-Italic.ttf", 34, (223, 210, 182), 0), W // 2, H - 50, a, "cc")


def abertura(t, path, nome, sub, cap, fim=2.6, dx=0, dy=-20):
    """Abertura sobre pintura do banco: título, disciplina e capítulo."""
    bg = kenburns(pintura(path), seg(t, 0, fim + .6), 1.0, 1.07, dx, dy)
    q = Quadro(bg)
    a = env(t, .25, .9, fim - .5, fim)
    q.dtop.rectangle([0, H // 2 - 120, W, H // 2 + 120], fill=(6, 5, 4, int(150 * a)))
    cola(q, texto(nome, "Cinzel-Bold.ttf", 76, GOLD, .16), W // 2, H // 2 - 30, a, "cc")
    cola(q, texto(sub, "Cinzel-SemiBold.ttf", 26, (214, 200, 170), .2), W // 2, H // 2 + 50, a, "cc")
    cola(q, texto(cap, "EBGaramond-Italic.ttf", 28, MUTED, 0), W // 2, H // 2 + 92, a, "cc")
    return q


def transicao(img_a, img_b, u):
    return Image.blend(img_a, img_b, eio(clamp(u)))


# ------------------------------------------------------------------ elementos
def elo(q, a, b, t, cor, vel=1.0, alpha=1.0, larg=4, periodo=26, corte=None, base=True, tremor=0.0):
    """Fio reto e tenso com franjas que correm no sentido a→b (vel<0 inverte). corte: fração onde o elo termina."""
    if alpha <= 0.01: return
    L = math.dist(a, b); n = max(2, int(L / 6)); fim = corte if corte is not None else 1.0
    if base:
        q.dt.line([a, lerp2(a, b, fim)], fill=mul(cor, .45) + (int(150 * alpha),), width=max(1, larg // 2))
    nx, ny = (b[1] - a[1]) / (L + 1e-6), -(b[0] - a[0]) / (L + 1e-6)
    for i in range(n):
        s0, s1 = i / n, (i + 1) / n
        if s0 >= fim: break
        f = 0.5 + 0.5 * math.cos(2 * math.pi * (s0 * L / periodo - t * vel * 2.2))
        k = alpha * (0.25 + 0.75 * f ** 2)
        j = tremor * math.sin(t * 40 + i * 1.7) * 3
        p, r = lerp2(a, b, s0), lerp2(a, b, min(s1, fim))
        q.dl.line([(p[0] + nx * j, p[1] + ny * j), (r[0] + nx * j, r[1] + ny * j)], fill=mul(cor, k), width=larg)
    if corte is not None and corte < 1:
        c = lerp2(a, b, corte)
        for k in range(6):
            ang = random.uniform(0, 2 * math.pi); rr = random.uniform(4, 16)
            q.dl.line([c, (c[0] + math.cos(ang) * rr, c[1] + math.sin(ang) * rr)], fill=mul(AMBER, alpha), width=2)


def poli_elo(q, pts, t, cor, **kw):
    for p, r in zip(pts, pts[1:]): elo(q, p, r, t, cor, **kw)


def ancora(q, p, tipo="prego", alpha=1.0, r=9):
    if alpha <= 0.01: return
    x, y = p; A = int(255 * alpha)
    if tipo == "prego":
        q.dt.ellipse([x - r, y - r, x + r, y + r], fill=COBRE + (A,), outline=mul(COBRE, 1.4) + (A,), width=2)
    elif tipo == "pino":
        q.dt.ellipse([x - r, y - r, x + r, y + r], outline=BRONZE + (A,), width=3); q.dt.ellipse([x - 3, y - 3, x + 3, y + 3], fill=BRONZE + (A,))
    elif tipo == "chapa":
        q.dt.rectangle([x - r * 2, y - r * .6, x + r * 2, y + r * .6], fill=(96, 90, 82, A), outline=(150, 140, 125, A))
    elif tipo == "disco":
        q.dt.ellipse([x - r * 2, y - r * .7, x + r * 2, y + r * .7], fill=(70, 66, 60, A), outline=(150, 140, 125, A), width=2)


def giz(q, pts, alpha=1.0, larg=3):
    """Traço de giz branco, levemente irregular."""
    if alpha <= 0.01 or len(pts) < 2: return
    rnd = random.Random(int(pts[0][0] * 7 + pts[0][1]))
    jit = [(x + rnd.uniform(-1.2, 1.2), y + rnd.uniform(-1.2, 1.2)) for x, y in pts]
    q.dt.line(jit, fill=(235, 232, 222, int(220 * alpha)), width=larg)


def giz_texto(q, s, x, y, alpha=1.0, tam=30, rot=-4):
    if alpha <= 0.01: return
    im = texto(s, "EBGaramond-Italic.ttf", tam, (236, 233, 224), 0, False).rotate(rot, expand=True, resample=Image.BICUBIC)
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha * .9)))
    q.tinta.alpha_composite(im, (int(x), int(y)))


def celulas(q, x, y, estados, escala=1.0, rachada=(), quebrada=False, rotulo_txt="manopla"):
    """Três células cerâmicas; estado 0..1 (0 fria, .36 vermelho sujo, .66 laranja vivo, .97 saturada)."""
    w, h, gap = 34 * escala, 92 * escala, 16 * escala
    q.dt.rounded_rectangle([x - 18 * escala, y - 18 * escala, x + 3 * w + 2 * gap + 18 * escala, y + h + 18 * escala], 14 * escala,
                           fill=(30, 28, 26, 230), outline=(120, 104, 78, 255), width=2)
    for i, e in enumerate(estados):
        x0 = x + i * (w + gap)
        if quebrada:
            for k in range(5):
                fx, fy = x0 + random.uniform(-20, w + 20), y + random.uniform(-20, h + 20)
                q.dt.polygon([(fx, fy), (fx + random.uniform(6, 16), fy + random.uniform(-6, 6)), (fx + random.uniform(-4, 6), fy + random.uniform(6, 16))], fill=(90, 84, 76, 255))
            continue
        cor = (92, 86, 78) if e <= 0.05 else blackbody(e)
        q.dt.rounded_rectangle([x0, y, x0 + w, y + h], 10 * escala, fill=cor + (255,), outline=(160, 136, 96, 255), width=2)
        if e > 0.05: q.dl.rounded_rectangle([x0, y, x0 + w, y + h], 10 * escala, fill=mul(cor, .55 + .45 * e))
        if i in rachada:
            xx, yy = x0 + w * .55, y
            rnd = random.Random(i * 31)
            for s in range(7):
                nx_, ny_ = xx + rnd.uniform(-w * .35, w * .35), yy + h / 7
                q.dt.line([(xx, yy), (nx_, ny_)], fill=(8, 7, 6, 255), width=3); xx, yy = nx_, ny_
    cola(q, texto(rotulo_txt, "Cinzel-SemiBold.ttf", int(16 * escala) + 2, MUTED, .1), x + (3 * w + 2 * gap) / 2, y + h + 26 * escala, 1, "ct")


def figura(q, x, y, h, cor=IVORY, lado=1, manopla=None, braco=0.0, martelo=False, alpha=1.0, preenchimento=(22, 20, 18)):
    """Pictograma de pessoa (vista lateral simplificada). y = pés. braco: 0 baixo .. 1 estendido à frente."""
    A = int(255 * alpha); c = cor + (A,); f = preenchimento + (A,)
    hd = h * .12; cx = x
    q.dt.ellipse([cx - hd * .55, y - h, cx + hd * .55, y - h + hd * 1.1], fill=f, outline=c, width=2)
    tronco = [(cx - h * .13, y - h * .86), (cx + h * .13, y - h * .86), (cx + h * .2, y - h * .3), (cx - h * .2, y - h * .3)]
    q.dt.polygon(tronco, fill=f, outline=c)
    q.dt.line([(cx - h * .07, y - h * .3), (cx - h * .11, y)], fill=c, width=max(2, int(h * .03)))
    q.dt.line([(cx + h * .07, y - h * .3), (cx + h * .11, y)], fill=c, width=max(2, int(h * .03)))
    ombro = (cx + h * .06 * lado, y - h * .8)
    ang = math.radians(lerp(80, 0, braco)); mao = (ombro[0] + math.cos(ang) * h * .38 * lado, ombro[1] + math.sin(ang) * h * .38)
    q.dt.line([ombro, mao], fill=c, width=max(3, int(h * .04)))
    if manopla is not None:
        mm = lerp2(ombro, mao, .7)
        q.dt.ellipse([mm[0] - h * .035, mm[1] - h * .035, mm[0] + h * .035, mm[1] + h * .035], fill=(150, 150, 155, A))
        q.dl.ellipse([mm[0] - h * .03, mm[1] - h * .03, mm[0] + h * .03, mm[1] + h * .03], fill=mul(blackbody(max(.3, manopla)), alpha))
    if martelo:
        q.dt.line([mao, (mao[0], mao[1] - h * .3)], fill=c, width=max(3, int(h * .03)))
        q.dt.rectangle([mao[0] - h * .1, mao[1] - h * .42, mao[0] + h * .1, mao[1] - h * .3], fill=(60, 58, 56, A), outline=c)
    return mao


def raio(a, b, rnd, gerações=6, desvio=.22):
    pts = [a, b]
    for _ in range(gerações):
        novo = [pts[0]]
        for p, r in zip(pts, pts[1:]):
            L = math.dist(p, r) * desvio; m = ((p[0] + r[0]) / 2 + rnd.gauss(0, L), (p[1] + r[1]) / 2 + rnd.gauss(0, L))
            novo += [m, r]
        pts = novo
    return pts


def descarga(q, a, b, semente, intensidade=1.0, ramos=3, cor=RAIO, larg=5):
    if intensidade <= 0.01: return []
    rnd = random.Random(semente); pts = raio(a, b, rnd)
    q.dl.line(pts, fill=mul(cor, intensidade), width=larg)
    q.dl.line(pts, fill=mul((255, 255, 255), intensidade), width=max(1, larg - 3))
    for k in range(ramos):
        p = pts[rnd.randrange(len(pts) // 5, len(pts) - 2)]
        ang = rnd.uniform(-1.3, 1.3) + math.atan2(b[1] - a[1], b[0] - a[0]); L = rnd.uniform(60, 180)
        q.dl.line(raio(p, (p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L), rnd, 4), fill=mul(cor, intensidade * .7), width=max(1, larg - 3))
    return pts


def brilho(q, p, r, cor, k=1.0):
    if k <= 0.01: return
    for i in range(6, 0, -1):
        rr = r * i / 6
        q.dl.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=mul(cor, k * (1 - i / 7) * .6))


def aneis(q, c, t, t0, cor, n=3, vel=260, alpha=1.0, larg=3, arco=None, vida=1.6):
    for k in range(n):
        tt = t - t0 - k * .18
        if tt < 0: continue
        r = tt * vel; a = alpha * max(0, 1 - tt / vida)
        if a <= 0.02: continue
        box = [c[0] - r, c[1] - r, c[0] + r, c[1] + r]
        if arco: q.dl.arc(box, arco[0], arco[1], fill=mul(cor, a), width=larg)
        else: q.dl.ellipse(box, outline=mul(cor, a), width=larg)


_disc = {}
def _soft(r):
    r = max(2, int(r) // 2 * 2)
    if r in _disc: return _disc[r]
    y, x = np.mgrid[-r:r, -r:r].astype(np.float32); a = np.clip(1 - np.hypot(x, y) / r, 0, 1) ** 1.8
    im = Image.fromarray(np.dstack([np.full_like(a, 235), np.full_like(a, 238), np.full_like(a, 242), a * 255]).astype(np.uint8), "RGBA")
    _disc[r] = im; return im


def vapor(q, origem, t, t0, quant=40, larg=120, alt=420, alpha=1.0, semente=1):
    """Plumas de vapor que sobem de uma origem a partir de t0."""
    if t < t0: return
    rnd = random.Random(semente)
    for k in range(quant):
        nasc = t0 + rnd.uniform(0, 3.0); vida = rnd.uniform(1.6, 3.2); u = (t - nasc) / vida
        if u < 0 or u > 1: continue
        x = origem[0] + rnd.uniform(-larg / 2, larg / 2) + math.sin(u * 3 + k) * 30 * u
        y = origem[1] - u * alt * rnd.uniform(.7, 1.2); r = 18 + u * rnd.uniform(40, 90)
        s = _soft(r); s2 = s.copy(); s2.putalpha(s.getchannel("A").point(lambda v, a=alpha * (1 - u) * .55: int(v * a)))
        q.fumo.alpha_composite(s2, (int(x - s.width / 2), int(y - s.height / 2)))


_geada = {}
def geada(q, box, amount, semente=0):
    """Cristais de geada num retângulo (janelas, luvas)."""
    if amount <= 0.02: return
    x0, y0, x1, y1 = [int(v) for v in box]; k = (x1 - x0, y1 - y0, semente)
    if k not in _geada:
        im = Image.new("RGBA", (x1 - x0, y1 - y0)); d = ImageDraw.Draw(im); rnd = random.Random(semente)
        for _ in range(int((x1 - x0) * (y1 - y0) / 140)):
            px, py = rnd.uniform(0, x1 - x0), rnd.uniform(0, y1 - y0); ang = rnd.uniform(0, 2 * math.pi); L = rnd.uniform(4, 22)
            d.line([(px, py), (px + math.cos(ang) * L, py + math.sin(ang) * L)], fill=FROST + (rnd.randint(120, 230),), width=1)
        _geada[k] = im
    im = _geada[k].copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * amount)))
    q.tinta.alpha_composite(im, (x0, y0))


def trincas(q, c, amount, semente=0, raio_max=260, n=9, cor=(230, 240, 250)):
    if amount <= 0.02: return
    rnd = random.Random(semente)
    for k in range(n):
        ang = rnd.uniform(-math.pi, 0) if rnd.random() < .5 else rnd.uniform(0, math.pi)
        ang = rnd.uniform(0, 2 * math.pi); L = raio_max * rnd.uniform(.5, 1) * amount; x, y = c
        for s in range(6):
            nx_, ny_ = x + math.cos(ang) * L / 6 + rnd.uniform(-8, 8), y + math.sin(ang) * L / 6 * .35 + rnd.uniform(-3, 3)
            q.dt.line([(x, y), (nx_, ny_)], fill=cor + (int(200 * amount),), width=2); x, y = nx_, ny_


def estrias(q, c, t, t0, dur=.9, n=90, raio=420, cor=(200, 210, 225), semente=0, dir=None):
    u = seg(t, t0, t0 + dur)
    if u <= 0 or u >= 1: return
    rnd = random.Random(semente)
    for k in range(n):
        ang = rnd.uniform(0, 2 * math.pi) if dir is None else dir + rnd.uniform(-.5, .5)
        r0 = rnd.uniform(30, raio) * u; L = rnd.uniform(20, 70) * (1 - u)
        p = (c[0] + math.cos(ang) * r0, c[1] + math.sin(ang) * r0 * .6)
        q.dl.line([p, (p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L * .6)], fill=mul(cor, (1 - u) * .8), width=2)


# ------------------------------------------------------------------ som
SR = 48000
def trilha(dur, eventos, caminho, drone=(36.7, 55.0), nivel=.3):
    from scipy.signal import fftconvolve, butter, lfilter
    n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros(n); rng = np.random.default_rng(5)
    def add(sig, at, g=1.0):
        s = int(at * SR); e = min(n, s + len(sig))
        if s < n: out[s:e] += sig[:e - s] * g
    def x_(d): return np.arange(int(d * SR)) / SR
    def sino(f0, d=2.0, g=.2):
        x = x_(d); return g * sum(a * np.sin(2 * np.pi * f0 * m * x) * np.exp(-x * (2.2 + m)) for m, a in ((1, 1), (2.76, .45), (5.4, .2)))
    def baque(d=1.6, f0=80, f1=30, g=.7):
        x = x_(d); f = f1 + (f0 - f1) * np.exp(-x * 3); return g * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 1.8) + rng.normal(0, .2, len(x)) * np.exp(-x * 10))
    def ruido(d, lo, hi, g, forma=None):
        x = x_(d); z = lfilter(*butter(2, [lo / (SR / 2), hi / (SR / 2)], btype="band"), rng.normal(0, 1, len(x)))
        return g * z * (np.sin(np.pi * x / d) ** 2 if forma is None else forma(x / d))
    def estalo(d=.5, g=.5): return ruido(d, 1500, 9000, g, lambda u: np.exp(-u * 8)) * (rng.random(int(d * SR)) > .7)
    def crepita(d=1.0, g=.4): return ruido(d, 2000, 12000, g) * (rng.random(int(d * SR)) > .985) * 6
    def zumbido(d=2.0, f=110, g=.15): x = x_(d); return g * np.sin(2 * np.pi * f * x) * (np.sin(2 * np.pi * 3 * x) * .3 + .7) * np.sin(np.pi * x / d)
    def chiado(d=2.0, g=.25): return ruido(d, 3000, 11000, g)
    def sopro(d=1.0, g=.2): return ruido(d, 400, 2600, g)
    def vidro(f=1800, d=1.4, g=.12): return sino(f, d, g) + sino(f * 1.5, d, g * .5)
    fn = dict(sino=sino, baque=baque, estalo=estalo, crepita=crepita, zumbido=zumbido, chiado=chiado, sopro=sopro, vidro=vidro)
    out += sum(a * np.sin(2 * np.pi * f * tt) for f, a in zip(drone, (.5, .3))) * nivel * (0.6 + 0.4 * np.sin(2 * np.pi * tt / 6))
    out += lfilter(*butter(2, [2000 / (SR / 2), 8000 / (SR / 2)], btype="band"), rng.normal(0, 1, n)) * .012
    for at, nome, kw in eventos: add(fn[nome](**kw), at)
    ir = rng.normal(0, 1, int(1.8 * SR)) * np.exp(-np.arange(int(1.8 * SR)) / SR * 3) * .04
    wet = fftconvolve(out, ir)[:n]
    st = np.vstack([out + wet, np.roll(out, 200) + np.roll(wet, 700)]).T
    st *= np.interp(tt, [0, .3, dur - .6, dur], [0, 1, 1, 0])[:, None]
    st = np.tanh(st / (np.abs(st).max() + 1e-9) * 1.5) * .88
    with wave.open(caminho, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())


def exporta(nome, dur, quadro, eventos, saida, drone=(36.7, 55.0)):
    """Renderiza os quadros por ffmpeg, sintetiza a trilha e junta tudo em MP4."""
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    vid, wav = f"{TMP}/{nome}.mp4", f"{TMP}/{nome}.wav"
    trilha(dur, eventos, wav, drone)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        random.seed(i * 7919 + len(nome))
        p.stdin.write(quadro(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", "-shortest", saida], check=True)
    return saida
