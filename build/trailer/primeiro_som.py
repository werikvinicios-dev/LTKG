"""CENA 01 — o primeiro som (0–7 s). Plano macro: um fio de prata esticado no escuro, uma gota que se forma presa nele,
o fio tocado vibra e solta a gota, a câmera desce com a queda e a gota bate numa chapa de aço escovado molhada.
Instantes que o áudio usa: toque leve em .5, toque forte em 3.05, a gota se solta em 4.35 e toca o aço em 5.62."""
import math
import numpy as np, cv2
import base as B
from base import seg, eio, eo, ei, lerp, clamp

T_TOQUE, T_SOLTA, T_CONTATO = 3.05, 4.35, 5.62
_C = {}


def _s():
    return B.H / 1080


# ------------------------------------------------------------------ geometria do mundo (px de saída, câmera em y)
def _yfio():
    return B.H * .40


def _yimpacto():
    return B.H * 2.10


def _yhorizonte():
    return _yimpacto() - B.H * .62


def camera(t):
    """A câmera acompanha a gota: começa no fio e desce com a queda até enquadrar o ponto de contato."""
    alvo_fim = B.H * (.64 if B.W > B.H else .62)
    fim = _yimpacto() - alvo_fim
    if t <= T_SOLTA:
        return 0.0
    if t >= T_CONTATO:
        return fim
    tt = (t - T_SOLTA) / (T_CONTATO - T_SOLTA)
    y0 = fio_y(gota_x()) + B.H * .05
    yw = y0 + (_yimpacto() - y0) * tt ** 2
    return float(clamp(yw - lerp(.46, .64, eo(tt)) * B.H, 0, fim))


def fio_y(x):
    """Centro do fio em coordenadas do mundo: leve diagonal, mais perto (mais grosso) à esquerda."""
    u = x / B.W
    return _yfio() + B.H * (.07 - .12 * u)


def gota_x():
    return B.W * .53


# ------------------------------------------------------------------ fundo: escuro com bokeh frio
def bokeh():
    k = ("bokeh", B.W, B.H)
    if k in _C:
        return _C[k]
    s = _s()
    h = int(B.H * 2.7)
    r = np.random.default_rng(5)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, B.W, dtype=np.float32)[None, :]
    base = (.022 + .05 * np.exp(-(xx ** 2) * 1.4) * np.exp(-((yy - .3) / .35) ** 2))[..., None] * np.array((.55, .7, 1.0), np.float32)
    cam = np.zeros((h, B.W, 3), np.float32)
    for _ in range(46):
        cx, cy = r.uniform(0, B.W), r.uniform(0, h)
        rad = r.uniform(14, 70) * s
        quente = r.random() < .16
        cor = np.array((1.0, .62, .3) if quente else (.42, .58, .85), np.float32) * r.uniform(.05, .2)
        m = np.zeros((h, B.W), np.float32)
        cv2.circle(m, (int(cx), int(cy)), int(rad), 1.0, -1, cv2.LINE_AA)
        borda = np.zeros_like(m)
        cv2.circle(borda, (int(cx), int(cy)), int(rad * .93), 1.0, max(1, int(rad * .1)), cv2.LINE_AA)
        disco = cv2.GaussianBlur(m * .75 + borda * .45, (0, 0), max(1.0, rad * .06))
        cam += disco[..., None] * cor
    _C[k] = np.clip(base + cam, 0, 1)
    return _C[k]


def fundo(cam_y):
    b = bokeh()
    y0 = int(clamp(cam_y * .45, 0, b.shape[0] - B.H))      # o fundo anda menos que o primeiro plano
    return b[y0:y0 + B.H].copy()


# ------------------------------------------------------------------ o fio
def deslocamento(x, t):
    """Amplitudes (px) do modo fundamental entre os apoios, que ficam fora do quadro."""
    u = (x + B.W * .25) / (B.W * 1.5)
    forma = np.sin(np.pi * u)
    s = _s()
    a = 0.0
    if t > .5:
        a += 2.2 * s * math.exp(-(t - .5) * 2.2)
    if t > T_TOQUE:
        a += 24 * s * math.exp(-(t - T_TOQUE) * .95)
    if t > T_SOLTA:
        a += 7 * s * math.exp(-(t - T_SOLTA) * 2.0)            # o fio ricocheteia quando a gota sai
    return forma, a


def camada_fio(t, cam_y):
    """RGBA pré-multiplicado do fio, com o borrão de obturador da vibração e profundidade de campo."""
    s = _s()
    xs = np.arange(B.W, dtype=np.float32)
    yc = fio_y(xs) - cam_y
    esp = lerp(17, 8, xs / B.W) * s                          # espessura: mais perto à esquerda
    forma, a = deslocamento(xs, t)
    amp = np.abs(forma * a)
    y0 = int(max(0, (yc - amp - esp).min() - 70 * s)); y1 = int(min(B.H, (yc + amp + esp).max() + 70 * s))
    cor = np.zeros((B.H, B.W, 3), np.float32); alfa = np.zeros((B.H, B.W), np.float32)
    if y1 <= y0:
        return np.zeros((B.H, B.W, 4), np.float32)
    yy = np.arange(y0, y1, dtype=np.float32)[:, None]
    # vibração rápida: a câmera vê o fio borrado entre os extremos (média de muitas fases dentro do obturador)
    nf = 28 if a > .6 * s else (6 if a > .05 * s else 1)
    fases = np.sin(np.linspace(0, 2 * np.pi, nf, endpoint=False) + t * 37.0) if nf > 1 else [0.0]
    # brilho que corre ao longo do fio enquanto a luz o descobre
    xs_luz = lerp(-.1, 1.15, eio(seg(t, .5, 2.6))) * B.W
    corrida = 2.6 * np.exp(-((xs - xs_luz) / (.07 * B.W)) ** 2) * (seg(t, .5, .9) * (1 - seg(t, 2.4, 2.9)))
    brilho = (.55 + .45 * np.exp(-((xs - gota_x()) / (.22 * B.W)) ** 2) + corrida)[None, :]
    cb = np.zeros((y1 - y0, B.W, 3), np.float32); ab = np.zeros((y1 - y0, B.W), np.float32)
    e = esp[None, :]
    for f in fases:
        d = yy - (yc + forma * a * f)[None, :]
        corpo = np.clip(e * .5 + .7 - np.abs(d), 0, 1)
        sombra = np.clip(.55 + d / e, 0, 1)                       # cilindro: claro em cima, escuro embaixo
        nucleo = np.exp(-((d + e * .2) / (e * .11)) ** 2)         # reflexo da luz de cima
        reflexo2 = .4 * np.exp(-((d - e * .32) / (e * .07)) ** 2)  # reflexo frio de baixo
        c = (corpo[..., None] * (1 - .75 * sombra[..., None]) * np.array((.34, .37, .42), np.float32)
             + (nucleo * brilho)[..., None] * np.array((1.0, .98, .94), np.float32)
             + (reflexo2 * brilho)[..., None] * np.array((.45, .6, .85), np.float32))
        cb += c * corpo[..., None]; ab += corpo
    cor[y0:y1] = cb / len(fases); alfa[y0:y1] = ab / len(fases)
    # profundidade de campo: nítido perto da gota, desfocado nas pontas; no começo tudo desfocado (foco entrando)
    foco0 = 9.0 * (1 - eo(seg(t, .3, 2.4)))
    sig = foco0 + 11.0 * np.clip(np.abs(xs / B.W - .53) - .12, 0, 1) ** 1.2 * 2.2
    niveis = [0.0, 2.5, 6.0, 12.0, 20.0]
    camadas = []
    for nv in niveis:
        if nv == 0:
            camadas.append(np.concatenate([cor, alfa[..., None]], 2))
        else:
            camadas.append(cv2.GaussianBlur(np.concatenate([cor, alfa[..., None]], 2), (0, 0), nv * s))
    sig = np.clip(sig, 0, niveis[-1])
    idx = np.searchsorted(niveis, sig, side="right") - 1
    idx = np.clip(idx, 0, len(niveis) - 2)
    w = ((sig - np.array(niveis)[idx]) / (np.array(niveis)[idx + 1] - np.array(niveis)[idx]))[None, :, None]
    out = np.zeros_like(camadas[0])
    for i in range(len(niveis) - 1):
        m = (idx == i)[None, :, None]
        out += m * (camadas[i] * (1 - w) + camadas[i + 1] * w)
    return out


# ------------------------------------------------------------------ a gota (refração do que está atrás)
def desenhar_gota(img, cx, cy, rx, ry, pescoco=0.0, desfoque=0.0):
    """Gota d'água: mostra o fundo invertido e ampliado, borda escura de Fresnel, reflexo e cáustica."""
    if rx < 1 or cy < -ry * 3 or cy > B.H + ry * 3:
        return img
    pad = int(max(rx, ry) * 2.2 + 6)
    x0, y0 = int(cx - pad), int(cy - pad - ry * pescoco * 1.5)
    x1, y1 = int(cx + pad), int(cy + pad)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(B.W, x1), min(B.H, y1)
    if xb <= xa or yb <= ya:
        return img
    yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
    u, v = (xx - cx) / rx, (yy - cy) / ry
    # pescoço: o alto da gota se estica para cima quando está para se soltar
    v_ef = np.where(v < 0, v / (1 + pescoco * 1.6), v)
    lado = np.where(v < 0, 1 - pescoco * .55 * np.clip(-v, 0, 1), 1.0)
    rr = (u / lado) ** 2 + v_ef ** 2
    dentro = np.clip((1 - rr) * max(rx, ry) * .9, 0, 1)
    if dentro.max() <= 0:
        return img
    # refração: amostra o fundo invertido e ampliado (a gota funciona como lente)
    mx = np.clip(cx - u * rx * 3.2, 0, B.W - 1).astype(np.float32)
    my = np.clip(cy - v * ry * 3.2, 0, B.H - 1).astype(np.float32)
    ref = cv2.remap(img, mx, my, cv2.INTER_LINEAR)
    ref = cv2.GaussianBlur(ref, (0, 0), max(.6, rx * .05)) * .75 + .015
    borda = np.clip(rr, 0, 1) ** 2.5
    corpo = ref * (1 - .85 * borda[..., None]) + np.array((.02, .025, .035), np.float32) * borda[..., None]
    # anel claro fino do lado de baixo (luz que atravessa) e reflexo da luz de cima
    anel = np.exp(-((rr - .86) / .06) ** 2) * np.clip(v, 0, 1) * .55
    spec = np.exp(-(((u + .32) / .2) ** 2 + ((v + .42) / .14) ** 2)) * 1.1
    caus = np.exp(-(((u - .05) / .3) ** 2 + ((v - .52) / .2) ** 2)) * .35
    luz = (anel + caus)[..., None] * np.array((.7, .82, 1.0), np.float32) + spec[..., None] * np.array((1, 1, 1), np.float32)
    g = np.clip(corpo + luz, 0, 1.2)
    a = dentro[..., None]
    if desfoque > .4:
        g = cv2.GaussianBlur(g, (0, 0), desfoque); a = cv2.GaussianBlur(a, (0, 0), desfoque)[..., None] if a.ndim == 3 else a
        a = a.reshape(g.shape[0], g.shape[1], 1)
    sub = img[ya:yb, xa:xb]
    img[ya:yb, xa:xb] = sub * (1 - a) + g * a
    return img


def gota_estado(t, cam_y):
    """Posição (tela) e forma da gota."""
    s = _s()
    gx = gota_x()
    forma, a = deslocamento(np.array([gx]), t)
    f = math.sin(t * 37.0)
    cresce = eo(seg(t, .8, 3.0))
    r = lerp(9, 36, cresce) * s
    if t > T_TOQUE:
        r *= 1 + .1 * seg(t, T_TOQUE, T_SOLTA)                 # a vibração junta mais água
    esp = lerp(17, 8, gx / B.W) * s
    topo = fio_y(gx) + esp * .5 - cam_y
    if t < T_SOLTA:
        balanco = forma[0] * a * f * .9 if a < 3 * s else forma[0] * a * .25 * math.sin(t * 7.0)   # a gota pesa: segue devagar
        pesc = eo(seg(t, T_TOQUE + .2, T_SOLTA)) * .9
        osc = .08 * math.sin((t - T_TOQUE) * 22) * math.exp(-(t - T_TOQUE) * 1.5) if t > T_TOQUE else 0
        ry = r * (1.12 + .25 * pesc + osc)
        return gx, topo + ry * (1.0 + pesc * .7) + balanco, r * (1 - osc * .5), ry, pesc
    tt = (t - T_SOLTA) / (T_CONTATO - T_SOLTA)
    y0 = fio_y(gx) + esp * .5 + r * 1.9
    yw = y0 + (_yimpacto() - r - y0) * tt ** 2
    osc = .12 * math.sin((t - T_SOLTA) * 26) * math.exp(-(t - T_SOLTA) * 2.2)   # a gota oscila depois de se soltar
    vel = 2 * tt * (_yimpacto() - y0) / (T_CONTATO - T_SOLTA) / 24        # px por quadro (borrão de movimento)
    return gx, yw - cam_y, r * (1 + osc), r * (1 - osc) + min(vel * .25, r * .6), 0.0


# ------------------------------------------------------------------ a chapa de aço molhada
def textura_escovada():
    k = ("escovado", B.W)
    if k not in _C:
        r = np.random.default_rng(3)
        n = r.standard_normal((900, 2400)).astype(np.float32)
        n = cv2.GaussianBlur(n, (0, 0), sigmaX=26, sigmaY=.5)
        n = (n - n.mean()) / (n.std() + 1e-6)
        _C[k] = n
    return _C[k]


def chapa(img, t, cam_y):
    yh = _yhorizonte() - cam_y
    if yh >= B.H:
        return img
    s = _s()
    ys = np.arange(max(0, int(yh) + 1), B.H, dtype=np.float32)
    if len(ys) == 0:
        return img
    prof = B.H / (ys - yh + 1.0) * .62                         # distância de cada linha (maior perto do horizonte)
    xx = np.arange(B.W, dtype=np.float32)
    cx = gota_x()
    X = (xx[None, :] - cx) / B.H * prof[:, None]
    Z = prof[:, None] * np.ones((1, B.W), np.float32)
    Zi = B.H / (_yimpacto() - _yhorizonte() + 1.0) * .62
    # ondas na película d'água a partir do impacto
    tau = t - T_CONTATO
    dh = np.zeros_like(X)
    if tau > 0:
        rr = np.sqrt(X ** 2 + ((Z - Zi) * 1.0) ** 2)
        for v_, k_, amp in ((1.4, 9.0, 1.0), (1.0, 14.0, .6), (.65, 20.0, .35)):
            frente = v_ * tau
            jan = np.clip((frente - rr) * 14, 0, 1) * np.exp(-np.clip(frente - rr, 0, None) * 4.0)
            dh += amp * np.cos(k_ * (rr - frente)) * jan * np.exp(-tau * .8) * np.exp(-rr * .7) * (1 - np.exp(-(rr / .06) ** 2))
    tex = textura_escovada()
    ty = np.clip((Z * 900) % tex.shape[0], 0, tex.shape[0] - 1).astype(np.float32)
    tx = np.clip((X * 420 + 1200 + dh * 5) % tex.shape[1], 0, tex.shape[1] - 1).astype(np.float32)
    riscos = cv2.remap(tex, tx, ty, cv2.INTER_LINEAR)
    # aço escovado: o reflexo da luz vira uma faixa larga e riscada, perpendicular ao escovado
    xr = (xx[None, :] - (cx + B.W * .1) - dh * 30 * s) / B.W
    faixa = np.exp(-(xr / .2) ** 2) * (.4 + .6 * np.exp(-(ys[:, None] - yh) / (B.H * .9)))
    luz = .05 + .2 * faixa * (1 + .3 * riscos) + .015 * riscos * (.4 + faixa)
    luz = luz + np.clip(dh, -1, 1) * .42 * (.3 + faixa) + np.clip(dh - .55, 0, 1) * .3
    cor = luz[..., None] * np.array((.74, .82, .93), np.float32)
    # a película d'água: um reflexo frio mais nítido perto do impacto
    yi_ = _yimpacto() - cam_y
    filme = np.exp(-(((xx[None, :] - cx) / (B.W * .28)) ** 2 + ((ys[:, None] - yi_) / (B.H * .16)) ** 2))
    cor += (filme * (.012 + .12 * np.clip(dh, 0, 1)))[..., None] * np.array((.6, .75, 1.0), np.float32)
    # borda chanfrada da chapa: uma linha de luz fina no limite de trás
    bisel = np.exp(-((ys[:, None] - yh - 3 * s) / (2.2 * s)) ** 2) * (.25 + .75 * np.exp(-(((xx[None, :] - cx) / (B.W * .35)) ** 2)))
    # profundidade de campo: o fundo da chapa desfocado, o ponto de impacto nítido
    cor_n = cor
    cor_b = cv2.GaussianBlur(cor, (0, 0), 9 * s)
    yi = _yimpacto() - cam_y
    w = np.clip(np.abs(ys - yi) / (B.H * .18), 0, 1)[:, None, None]
    cor = cor_n * (1 - w) + cor_b * w
    # a borda distante funde no escuro
    a = np.clip((ys - yh) / (B.H * .35), 0, 1)[:, None, None] ** 1.5
    y0 = int(ys[0])
    img[y0:] = img[y0:] * (1 - a) + cor * a
    return img


def coluna(img, cx, cy, altura, r0, r1):
    """Coluna d'água afunilada: bordas escuras, núcleo claro e o fundo visto através dela."""
    if altura < 2:
        return img
    pad = int(r0 * 2 + 4)
    x0, x1 = max(0, int(cx - pad)), min(B.W, int(cx + pad))
    y0, y1 = max(0, int(cy - altura - r1 * 2)), min(B.H, int(cy + r0))
    if x1 <= x0 or y1 <= y0:
        return img
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    f = np.clip((cy - yy) / altura, 0, 1)
    raio = lerp(r0, r1, f ** .6) * np.sqrt(np.clip(1 - f ** 6, 0, 1)) * (1 + 1.1 * np.exp(-f / .07)) * np.where(cy - yy > altura, 0, 1)
    raio = raio * np.clip((cy - yy) / 3 + 1, 0, 1)                   # nasce da película, sem degrau
    u = (xx - cx) / np.maximum(raio, 1e-3)
    dentro = np.clip((1 - np.abs(u)) * raio * .8, 0, 1) * (raio > 0)
    mx = np.clip(cx - u * raio * 2.5, 0, B.W - 1).astype(np.float32)
    ref = cv2.remap(img, mx, yy, cv2.INTER_LINEAR) * .8 + .015
    borda = np.abs(u) ** 3
    g = (ref * (1 - .5 * borda[..., None]) + (borda * .32)[..., None] * np.array((.62, .72, .86), np.float32)
         + (np.exp(-((u + .38) / .12) ** 2) * .55)[..., None] * np.array((.9, .95, 1.0), np.float32))
    a = np.clip(dentro, 0, 1)[..., None]
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a) + g * a
    return img


def respingos(img, t, cam_y):
    """Coroa de gotículas e o jato que sobe do impacto e cai de volta."""
    tau = t - T_CONTATO
    if tau <= 0:
        return img
    s = _s()
    cx, cy = gota_x(), _yimpacto() - cam_y
    r = np.random.default_rng(8)
    g = 5200 * s                                                # gravidade em px/s² (câmera lenta)
    for i in range(18):
        ang = i / 18 * 2 * np.pi + r.uniform(-.15, .15)
        v = r.uniform(300, 620) * s
        vx, vz, vy = v * math.cos(ang), v * math.sin(ang) * .32, r.uniform(800, 1500) * s
        x = cx + vx * tau
        y = cy + vz * tau - vy * tau + .5 * g * tau ** 2
        if y > cy + vz * tau + 2:
            continue
        rad = r.uniform(4, 9) * s * (1 - .5 * clamp(tau / 1.4))
        img = desenhar_gota(img, x, y, rad, rad * 1.15)
    # jato de Worthington: uma coluna d'água sobe, solta uma gotinha no alto e volta
    if .12 < tau < .75:
        kj = (tau - .12) / .63
        altura = math.sin(kj * math.pi) * 210 * s
        img = coluna(img, cx, cy, altura, 24 * s * (1 - .3 * kj), 9 * s)
        if kj <= .45:
            img = desenhar_gota(img, cx, cy - altura * .97, 10 * s, 10.5 * s)
        if kj > .45:
            kk = (kj - .45) / .55
            yd = cy - altura - 50 * s * math.sin(kk * math.pi * .8)
            img = desenhar_gota(img, cx, yd, 10 * s, 11 * s)
    return img


# ------------------------------------------------------------------ composição
def cena01(t):
    cam_y = camera(t)
    img = fundo(cam_y)
    img = chapa(img, t, cam_y)
    fio = camada_fio(t, cam_y)
    img = img * (1 - fio[..., 3:4]) + fio[..., :3]
    if t < T_CONTATO:
        gx, gy, rx, ry, pesc = gota_estado(t, cam_y)
        img = desenhar_gota(img, gx, gy, rx, ry, pesc, desfoque=9.0 * (1 - eo(seg(t, .3, 2.4))) * B.H / 1080)
    else:
        img = respingos(img, t, cam_y)
    # o primeiro instante é escuro e a luz entra devagar
    img = img * (.15 + .85 * eo(seg(t, .2, 2.2))) * 1.25
    img = B.brilho_pontos(img, .7, 10, .45)
    img = B.graduar(img, (.012, .018, .03), (.9, .95, 1.0), .85, 1.06)
    img = img * (1 - seg(t, 6.55, 7.0))
    return B.vinheta(img, .55)
