"""Motor do trailer de Leis para Matar Deuses: câmera 2.5D por profundidade, partículas, névoa,
vento em tecido e cabelo, gradação de cor, grão e tipografia. Tudo em numpy/cv2, quadro a quadro."""
import math, os, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/user/LTKG"
BA = f"{ROOT}/exportacoes/banco_de_arte"
BA4 = f"{ROOT}/exportacoes/banco_de_arte_4x"
AC = f"{ROOT}/exportacoes/acervo_drive"
SIM = f"{ROOT}/exportacoes/identidade_aresta/simbolos"
FT = f"{ROOT}/build/fonts"
CACHE = f"{ROOT}/build/trailer/_cache"
os.makedirs(CACHE, exist_ok=True)
FPS = 24

# formato ativo (16:9 ou 9:16); o roteiro de câmera é escrito em pixels da placa e altura de vista,
# então o vertical reaproveita os mesmos movimentos com uma janela mais estreita
W, H = 1920, 1080


def formato(w, h):
    global W, H
    W, H = w, h


# ------------------------------------------------------------------ curvas
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def ei(x): x = clamp(x); return x ** 3
def lerp(a, b, x): return a + (b - a) * x
def env(t, a, b, c, d): return seg(t, a, b) * (1 - seg(t, c, d))


# ------------------------------------------------------------------ placas
_placas = {}


def placa(caminho, maxlado=3600):
    """Imagem RGB float32 0..1 (reduzida para no máximo maxlado), cacheada por processo."""
    k = (caminho, maxlado)
    if k not in _placas:
        im = Image.open(caminho).convert("RGB")
        if max(im.size) > maxlado:
            im.thumbnail((maxlado, maxlado), Image.LANCZOS)
        _placas[k] = np.asarray(im, np.float32) / 255.0
    return _placas[k]


def rgba(caminho, maxlado=2400):
    k = ("rgba", caminho, maxlado)
    if k not in _placas:
        im = Image.open(caminho).convert("RGBA")
        if max(im.size) > maxlado:
            im.thumbnail((maxlado, maxlado), Image.LANCZOS)
        _placas[k] = np.asarray(im, np.float32) / 255.0
    return _placas[k]


def prof(caminho, forma):
    """Profundidade (0 longe .. 1 perto) no tamanho da placa usada, suavizada para não rasgar bordas."""
    k = ("prof", caminho, forma)
    if k not in _placas:
        from profundidade import mapa
        d = np.asarray(mapa(caminho), np.float32)
        d = cv2.resize(d, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
        d = cv2.GaussianBlur(d, (0, 0), max(2, forma[1] / 400))
        _placas[k] = d
    return _placas[k]


_seg = None


def mascaras(caminho, forma):
    """Máscaras de cabelo, rosto, roupa de cima, saia/vestido e echarpe (segformer de roupas), cacheadas."""
    nome = os.path.splitext(os.path.basename(caminho))[0]
    dst = f"{CACHE}/mask_{nome}.npz"
    if not os.path.exists(dst):
        global _seg
        from transformers import pipeline
        if _seg is None:
            _seg = pipeline("image-segmentation", model="mattmdjaga/segformer_b2_clothes", device="cpu")
        im = Image.open(caminho).convert("RGB"); im.thumbnail((1280, 1280))
        r = {x["label"]: np.asarray(x["mask"], np.uint8) for x in _seg(im)}
        z = np.zeros(im.size[::-1], np.uint8)
        np.savez_compressed(dst, **{k: r.get(k, z) for k in ("Hair", "Face", "Upper-clothes", "Dress", "Skirt", "Scarf", "Pants", "Background")})
    m = np.load(dst)
    out = {}
    for k in m.files:
        a = cv2.resize(m[k].astype(np.float32) / 255.0, (forma[1], forma[0]), interpolation=cv2.INTER_LINEAR)
        out[k] = cv2.GaussianBlur(a, (0, 0), max(1.5, forma[1] / 600))
    return out


# ------------------------------------------------------------------ ruído suave (para vento, névoa e tremor)
def _ruido_base(n=256, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.random((n, n)).astype(np.float32)
    acc = np.zeros((n, n), np.float32); amp = 1.0
    for oct_ in range(5):
        s = 2 ** oct_ * 4
        acc += amp * cv2.resize(cv2.resize(r, (s, s), interpolation=cv2.INTER_AREA), (n, n), interpolation=cv2.INTER_CUBIC)
        amp *= .5
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc


_RU = {s: _ruido_base(256, s) for s in range(4)}


def campo(h, w, t, escala=1.0, vel=(0.05, 0.0), seed=0):
    """Campo de ruído -1..1 do tamanho (h,w), deslizando no tempo (vento, tremor de ar)."""
    base = _RU[seed % 4]
    ys = (np.arange(h, dtype=np.float32) / h * escala * 2 + t * vel[1]) * 255
    xs = (np.arange(w, dtype=np.float32) / w * escala * 3 + t * vel[0]) * 255
    mx, my = np.meshgrid(xs % 255, ys % 255)
    return cv2.remap(base, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP) * 2 - 1


# ------------------------------------------------------------------ câmera 2.5D
def camera(img, cx, cy, vista, d=None, par=(0.0, 0.0), dolly=0.0, rot=0.0, desl=None):
    """Recorta uma vista de altura `vista` (px da placa) centrada em (cx,cy) e a leva a W×H.
    Com profundidade d: par=(px,py) desloca o que está perto mais do que o que está longe (parallax);
    dolly>0 aproxima o perto mais rápido que o fundo (travelling para dentro).
    desl: campo extra (dx,dy) em px da placa, já no tamanho de saída (vento, respiração)."""
    h0, w0 = img.shape[:2]
    if W < H:
        vista *= 1.7          # no vertical, a mesma cena com um pouco mais de ar (senão os closes ficam estreitos demais)
    # a vista nunca sai da imagem (sem bordas espelhadas): limita o tamanho e prende o centro
    vista = min(vista, h0 * .995, w0 * H / W * .995)
    vw = vista * W / H
    cx = min(max(cx, vw / 2 + abs(par[0]) * .5), w0 - vw / 2 - abs(par[0]) * .5)
    cy = min(max(cy, vista / 2 + abs(par[1]) * .5), h0 - vista / 2 - abs(par[1]) * .5)
    esc = vista / H
    u = (np.arange(W, dtype=np.float32) - W / 2) * esc
    v = (np.arange(H, dtype=np.float32) - H / 2) * esc
    mu, mv = np.meshgrid(u, v)
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        mu, mv = c * mu - s * mv, s * mu + c * mv
    mx = cx + mu; my = cy + mv
    if d is not None and (par != (0.0, 0.0) or dolly):
        dd = cv2.remap(d, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        k = 1.0 / (1.0 + dolly * (dd - .35))
        mx = cx + mu * k - par[0] * (dd - .5)
        my = cy + mv * k - par[1] * (dd - .5)
    if desl is not None:
        mx = mx + desl[0]; my = my + desl[1]
    return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def vento(mask_out, t, amp=6.0, escala=1.4, vel=(0.25, 0.05), seed=1, rajada=1.0):
    """Deslocamento de tecido/cabelo: só onde a máscara (já na vista de saída) existe."""
    h, w = mask_out.shape
    nx = campo(h, w, t, escala, vel, seed); ny = campo(h, w, t + 7.3, escala * 1.3, vel, seed + 1)
    a = amp * rajada * mask_out
    return nx * a, ny * a * .6


def vista_mascara(m, cx, cy, vista):
    return camera(m[..., None].repeat(3, 2), cx, cy, vista)[..., 0]


# ------------------------------------------------------------------ partículas
class Neve:
    """Neve em três profundidades. Posições determinísticas no tempo (não há estado entre quadros)."""
    def __init__(self, n=900, seed=3, vento=(0.35, 0.0), queda=0.22, tam=(1.0, 5.5), turb=0.06):
        rng = np.random.default_rng(seed)
        self.p = rng.random((n, 2)).astype(np.float32)
        self.z = rng.random(n).astype(np.float32) ** 1.6          # 0 longe .. 1 perto
        self.ph = rng.random(n).astype(np.float32) * 6.28
        self.v, self.q, self.tam, self.turb = vento, queda, tam, turb

    def camada(self, t, intens=1.0, vento_extra=0.0, foco=None):
        img = np.zeros((H, W), np.float32)
        z = self.z
        vel = (0.35 + 1.6 * z)
        x = (self.p[:, 0] + t * (self.v[0] + vento_extra) * vel + self.turb * np.sin(t * 1.3 + self.ph)) % 1.2 - .1
        y = (self.p[:, 1] + t * self.q * vel) % 1.2 - .1
        r = self.tam[0] + (self.tam[1] - self.tam[0]) * z
        for zi, (lo, hi, blur) in enumerate(((0, .45, 0), (.45, .8, 1.2), (.8, 1.01, 3.5))):
            s = (z >= lo) & (z < hi)
            layer = np.zeros((H, W), np.float32)
            esc = (W + H) / 3000
            for xx, yy, rr, zz in zip(x[s], y[s], r[s], z[s]):
                cv2.circle(layer, (int(xx * W), int(yy * H)), max(1, int(rr * esc)), float(.35 + .65 * zz), -1, cv2.LINE_AA)
            if blur:
                layer = cv2.GaussianBlur(layer, (0, 0), blur * esc * (2.2 if foco == "perto" and zi == 2 else 1))
            img = np.maximum(img, layer)
        return np.clip(img * intens, 0, 1)


def nevoa(t, vel=(0.02, 0.0), dens=0.25, escala=0.8, seed=2):
    n = campo(H, W, t, escala, vel, seed) * .5 + .5
    return np.clip((n - .35) * 1.8, 0, 1) * dens


def brasas(t, n=60, seed=5, origem=(0.5, 1.05), sobe=0.12, cor=(1.0, .55, .18)):
    rng = np.random.default_rng(seed)
    p = rng.random((n, 3))
    img = np.zeros((H, W, 3), np.float32)
    for (a, b, c) in p:
        vida = (t * .25 + c) % 1.0
        x = origem[0] + (a - .5) * .9 + .05 * math.sin(t * 2 + a * 9)
        y = origem[1] - vida * (0.6 + b * .6)
        al = math.sin(vida * math.pi) * (.4 + .6 * b)
        cv2.circle(img, (int(x * W), int(y * H)), max(1, int(1 + 2.5 * b)), tuple(float(k * al) for k in cor), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(img, (0, 0), 1.2)


# ------------------------------------------------------------------ luz e acabamento
def tela(a, b): return 1 - (1 - a) * (1 - b)
def soma(a, b, k=1.0): return np.clip(a + b * k, 0, 1)


def misturar(base, cor, alpha):
    a = alpha[..., None] if alpha.ndim == 2 else alpha
    return base * (1 - a) + cor * a


def brilho_pontos(img, limiar=.82, raio=18, ganho=.55):
    """Bloom suave nas luzes (lanternas, janelas, ouro)."""
    l = img.max(axis=2)
    m = np.clip((l - limiar) / (1 - limiar), 0, 1)[..., None] * img
    return np.clip(img + cv2.GaussianBlur(m, (0, 0), raio * W / 1920) * ganho, 0, 1)


def raios(img, centro, t, forca=.35, cor=(1.0, .82, .5), dec=.965, passos=48):
    """Raios de luz volumétricos (god rays) a partir de um ponto, por amostragem radial das luzes."""
    l = np.clip((img.max(axis=2) - .6) * 2.5, 0, 1)
    peq = cv2.resize(l, (W // 4, H // 4))
    acc = np.zeros_like(peq); cx, cy = centro[0] * peq.shape[1], centro[1] * peq.shape[0]
    hh, ww = peq.shape
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    w = 1.0
    for i in range(passos):
        f = 1 - i / passos * .9
        acc += cv2.remap(peq, (cx + (xx - cx) * f).astype(np.float32), (cy + (yy - cy) * f).astype(np.float32), cv2.INTER_LINEAR) * w
        w *= dec
    acc = cv2.resize(acc / passos * 3, (W, H), interpolation=cv2.INTER_CUBIC)
    return np.clip(img + acc[..., None] * np.array(cor, np.float32) * forca, 0, 1)


def graduar(img, sombra=(0.02, 0.035, 0.06), luz=(1.0, .93, .82), sat=0.9, contraste=1.08, gama=1.0):
    """Gradação: sombras frias (negro mineral/azul), altas âmbar, saturação contida."""
    l = img.mean(axis=2, keepdims=True)
    img = l + (img - l) * sat
    img = np.clip((img - .5) * contraste + .5, 0, 1) ** gama
    sh = np.array(sombra, np.float32); hi = np.array(luz, np.float32)
    return np.clip(sh + img * (hi - sh), 0, 1)


_VIN = {}


def vinheta(img, forca=.45, raio=.9):
    k = (W, H, forca, raio)
    if k not in _VIN:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / raio
        _VIN[k] = (1 - forca * np.clip(r ** 2.2, 0, 1))[..., None].astype(np.float32)
    return img * _VIN[k]


_GR = None


def grao(img, t, forca=.035):
    global _GR
    if _GR is None or _GR[0].shape[:2] != (H, W):
        rng = np.random.default_rng(11)
        _GR = [cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), .7) for _ in range(6)]
    g = _GR[int(t * FPS) % 6]
    return np.clip(img + g[..., None] * forca * (1.2 - img), 0, 1)


def tremor(t, amp=4.0, freq=11.0, seed=0):
    return (amp * math.sin(t * freq + seed) * math.sin(t * freq * .61 + 1.7 + seed),
            amp * math.sin(t * freq * 1.3 + 2.1 + seed) * math.sin(t * freq * .47 + seed))


def borrao_mov(img, dx, dy):
    """Borrão de movimento linear (chicote de câmera)."""
    n = int(max(abs(dx), abs(dy)))
    if n < 2:
        return img
    k = np.zeros((2 * n + 1, 2 * n + 1), np.float32)
    cv2.line(k, (n - int(dx / 2), n - int(dy / 2)), (n + int(dx / 2), n + int(dy / 2)), 1.0, 1)
    k /= k.sum()
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)


def gravura(img, papel=(0.86, 0.81, 0.70), tinta=(0.06, 0.05, 0.05), t=1.0):
    """Transforma o quadro em gravura de tinta negra (hachura por limiar + bordas)."""
    g = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    g = cv2.equalizeHist((g * 255).astype(np.uint8)).astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W]
    hach = ((xx + yy) % 7 < 3).astype(np.float32) * .5 + ((xx - yy) % 9 < 2).astype(np.float32) * .5
    tom = np.where(g < .25, 1.0, np.where(g < .5, hach, np.where(g < .7, ((xx + yy) % 7 < 2) * .7, 0.0)))
    ed = cv2.Canny((g * 255).astype(np.uint8), 60, 140).astype(np.float32) / 255
    tom = np.clip(tom + cv2.GaussianBlur(ed, (0, 0), .8) * 1.5, 0, 1)
    p, k = np.array(papel, np.float32), np.array(tinta, np.float32)
    out = p * (1 - tom[..., None]) + k * tom[..., None]
    return img * (1 - t) + out * t


def barras(img, prop=2.39):
    """Faixas pretas de cinema (só no 16:9)."""
    if W < H:
        return img
    hb = int((H - W / prop) / 2)
    if hb > 0:
        img[:hb] = 0; img[-hb:] = 0
    return img


# ------------------------------------------------------------------ tipografia
_TX = {}


def texto(s, fonte="Cinzel-Regular.ttf", tam=60, cor=(.92, .86, .72), esp=0.0, sombra=True):
    """Bloco de texto RGBA (float) com espaçamento entre letras; cacheado."""
    k = (s, fonte, tam, cor, esp, sombra, W)
    if k not in _TX:
        tam_px = int(tam * W / 1920) if W > H else int(tam * W / 1080)
        f = ImageFont.truetype(f"{FT}/{fonte}", tam_px)
        larg = int(sum(f.getlength(c) for c in s) + esp * tam_px * (len(s) - 1)) + 40
        alt = int(tam_px * 1.6) + 20
        im = Image.new("RGBA", (larg, alt), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        x = 20
        for c in s:
            d.text((x, 10), c, font=f, fill=tuple(int(v * 255) for v in cor) + (255,))
            x += f.getlength(c) + esp * tam_px
        a = np.asarray(im, np.float32) / 255
        if sombra:
            sh = cv2.GaussianBlur(a[..., 3], (0, 0), tam_px / 10)
            out = np.zeros_like(a); out[..., :3] = a[..., :3]; out[..., 3] = np.maximum(a[..., 3], sh * .55)
            out[..., :3] = a[..., :3] * a[..., 3:4] / np.maximum(out[..., 3:4], 1e-4)
            a = out
        _TX[k] = a
    return _TX[k]


def colar(img, el, cx, cy, alpha=1.0, escala=1.0, mascara_x=None):
    """Cola um RGBA centrado em (cx,cy) em px de saída. mascara_x: revelação da esquerda (0..1)."""
    if alpha <= 0:
        return img
    if escala != 1.0:
        el = cv2.resize(el, (max(1, int(el.shape[1] * escala)), max(1, int(el.shape[0] * escala))), interpolation=cv2.INTER_AREA)
    h, w = el.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya:
        return img
    sub = el[ya - y0:yb - y0, xa - x0:xb - x0]
    a = sub[..., 3:4] * alpha
    if mascara_x is not None:
        xs = np.linspace(0, 1, w, dtype=np.float32)[xa - x0:xb - x0]
        m = np.clip((mascara_x * 1.15 - xs) / .15, 0, 1)
        a = a * m[None, :, None]
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - a) + sub[..., :3] * a
    return img


def para_u8(img):
    return (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
