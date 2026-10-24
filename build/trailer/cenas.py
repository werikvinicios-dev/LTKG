"""As dez cenas do trailer (roteiro do autor). Cada cena é uma função f(t_local) -> quadro float RGB (H×W).
O tempo global e os cortes ficam em LINHA (ver o fim do arquivo). Só artes do banco sem spoiler."""
import math
import numpy as np, cv2
import base as B
from base import seg, eio, eo, ei, lerp, env, clamp

P = {
    "rua": f"{B.BA4}/05_mundo/MU-009_vhalessa_fornalha_velha_noite_4x.jpg",
    "cidade": f"{B.BA}/11_edicao/C02-2.png",
    "ilan": f"{B.BA4}/06_personagens/PE-001_ilan_varek_retrato_4x.jpg",
    "ponte": f"{B.BA4}/06_personagens/PE-025_ilan_ponte_nevasca_4x.jpg",
    "mara": f"{B.BA4}/06_personagens/PE-003_mara_quen_retrato_4x.jpg",
    "nara": f"{B.BA}/06_personagens/PE-029_nara_voss_oficina.png",
    "estandartes": f"{B.BA}/04_objetos/OB-004_estandartes.png",
    "livro": f"{B.BA}/08_editorial/ED-001_livro_aberto_capitulo1.png",
    "texturas": f"{B.BA}/08_editorial/ED-003_texturas_e_materiais.png",
    "grupo": f"{B.BA}/06_personagens/PE-006_dinamica_do_grupo.png",
    "templo": f"{B.BA}/05_mundo/MU-007_interiores_sagrados.png",
    "veu": f"{B.BA}/06_personagens/PE-013_aurelia_veu_dourado_vento.png",
    "aurelia": f"{B.BA4}/06_personagens/PE-012_aurelia_dourada_retrato_4x.jpg",
    "lente": f"{B.BA}/06_personagens/PE-021_ilan_afericao.png",
    "golpe": f"{B.BA}/11_edicao/C01-a.png",
    "sotao": f"{B.BA}/11_edicao/C01-c.png",
    "portal": f"{B.BA}/09_engenharia_arcana/EA-006_transposicao_portal.png",
    "emblema": f"{B.BA}/01_identidade/ID-008_emblema_transparente.png",
    "lettering": f"{B.BA}/01_identidade/ID-006_lettering_transparente.png",
    "ordem": f"{B.SIM}/instituicoes/ordem_da_ultima_sentenca_decorativa.png",
}
LEIS = [("conservacao", "CONSERVAÇÃO"), ("vinculo", "VÍNCULO"), ("compatibilidade", "COMPATIBILIDADE"), ("vazao", "VAZÃO"),
        ("dissipacao", "DISSIPAÇÃO"), ("capacidade", "CAPACIDADE"), ("retorno", "RETORNO")]

NEVE_FINA = B.Neve(700, seed=3, vento=(0.10, 0), queda=0.10, tam=(1.0, 4.0))
NEVE = B.Neve(1100, seed=4, vento=(0.30, 0), queda=0.20, tam=(1.0, 6.0))
NEVASCA = B.Neve(1600, seed=5, vento=(0.95, 0), queda=0.30, tam=(1.0, 8.0), turb=0.03)


def V(nome, maxlado=3600):
    return B.placa(P[nome], maxlado)


def plano(nome, t, cx, cy, vista, par=(0, 0), dolly=0.0, rot=0.0, desl=None, maxlado=3600):
    im = V(nome, maxlado)
    d = B.prof(P[nome], im.shape[:2]) if (par != (0, 0) or dolly) else None
    return B.camera(im, cx, cy, vista, d, par, dolly, rot, desl)


def com_vento(nome, t, cx, cy, vista, chaves=("Hair",), amp=5.0, par=(0, 0), dolly=0.0, rajada=1.0, vel=(0.25, 0.05)):
    im = V(nome)
    m = B.mascaras(P[nome], im.shape[:2])
    mm = sum(m[k] for k in chaves if k in m)
    mo = B.vista_mascara(np.clip(mm, 0, 1), cx, cy, vista)
    dx, dy = B.vento(mo, t, amp * vista / 1080, vel=vel, rajada=rajada)
    return plano(nome, t, cx, cy, vista, par, dolly, desl=(dx, dy))


def neve_sobre(img, neve, t, intens=1.0, vento_extra=0.0, cor=(0.92, 0.95, 1.0)):
    s = neve.camada(t, intens, vento_extra)
    return B.misturar(img, np.array(cor, np.float32), s * .9)


def vapor(img, t, boca, inicio, periodo=3.4, dur=1.6, escala=1.0):
    """Hálito no frio: nuvem que sai da boca (px de saída) e se desfaz."""
    fase = (t - inicio) % periodo
    if t < inicio or fase > dur:
        return img
    k = fase / dur
    n = B.campo(B.H, B.W, t, 2.5, (0.4, -0.2), 2) * .5 + .5
    y, x = np.mgrid[0:B.H, 0:B.W].astype(np.float32)
    cx, cy = boca[0] + 120 * k * escala, boca[1] - 30 * k * escala
    r = (40 + 160 * k) * escala * B.W / 1920
    g = np.exp(-(((x - cx) / r) ** 2 + ((y - cy) / (r * .6)) ** 2))
    a = g * n * (math.sin(k * math.pi) ** 1.2) * .35
    return B.misturar(img, np.array((.85, .88, .92), np.float32), a)


def fio(img, t, x0, x1, y, rev, vib=0.0, freq=0.0, tensao=1.0, brilho=1.0, esp=1.6):
    """Fio de prata desenhado em 2D, com revelação (0..1) e vibração em modo fundamental + harmônico."""
    xs = np.linspace(x0, x0 + (x1 - x0) * rev, 400)
    L = max(1.0, x1 - x0)
    u = (xs - x0) / L
    ys = y + vib * (np.sin(np.pi * u) * math.cos(freq * t) + .35 * np.sin(2 * np.pi * u) * math.cos(freq * 2.07 * t + 1)) * tensao
    pts = np.stack([xs, ys], 1).astype(np.int32)
    camada = np.zeros((B.H, B.W), np.float32)
    cv2.polylines(camada, [pts], False, 1.0, max(1, int(esp * B.W / 1920)), cv2.LINE_AA)
    halo = cv2.GaussianBlur(camada, (0, 0), 6 * B.W / 1920)
    cor = np.array((.82, .86, .92), np.float32)
    img = B.soma(img, halo[..., None] * cor, .5 * brilho)
    return B.misturar(img, cor * 1.1, np.clip(camada * brilho, 0, 1))


# ------------------------------------------------------------------ CENA 01 — o primeiro som (0–7)
def aco(t):
    """Superfície de aço frio escovado, iluminada de lado."""
    h, w = B.H, B.W
    n = B.campo(h, w * 4, 0, 6.0, (0, 0), 3)[:, ::4]
    esc = cv2.resize(n, (w, h))
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    luz = np.exp(-((x + .15) ** 2) * 2.5) * np.clip((y - .58) * 3.5, 0, 1)
    base = (.06 + .16 * luz + .05 * esc * luz)[..., None] * np.array((.78, .85, .95), np.float32)
    return np.clip(base, 0, 1)


from primeiro_som import cena01          # o plano macro do fio e da gota está em primeiro_som.py


# ------------------------------------------------------------------ CENA 02 — o mundo de Aresta (7–16)
def cena02(t):
    if t < 4.45:            # a rua da Fornalha Velha, travelling para dentro
        k = eio(seg(t, 0, 4.45))
        img = plano("rua", t, lerp(1840, 1870, k), lerp(1140, 1180, k), lerp(1560, 1240, k), par=(lerp(0, 40, k), 0), dolly=lerp(0, .55, k))
        # janelas que respiram (âmbar)
        l = img.max(axis=2); quente = np.clip((img[..., 0] - img[..., 2] - .12) * 4, 0, 1) * np.clip((l - .45) * 3, 0, 1)
        fl = .9 + .1 * B.campo(B.H, B.W, t, 1.5, (.6, .3), 0)
        img = np.clip(img * (1 + (fl[..., None] - 1) * quente[..., None] * 1.6), 0, 1)
        img = B.misturar(img, np.array((.30, .32, .38), np.float32), B.nevoa(t, (.03, -.01), .18, .9, 1) * np.clip(1 - np.linspace(0, 1, B.H)[:, None] * 1.4, 0, 1))
        img = neve_sobre(img, NEVE, t, .8)
        img = B.brilho_pontos(img, .78, 16, .5)
        img = B.graduar(img, (.015, .025, .05), (.97, .92, .84), .85, 1.06)
    else:                    # o rio congelado e a torre, panorâmica lateral
        tt = t - 4.45
        k = eio(seg(tt, 0, 4.55))
        img = plano("cidade", t, lerp(560, 690, k), lerp(410, 395, k), 600, par=(lerp(-30, 30, k), 0))
        img = neve_sobre(img, NEVE_FINA, t, .7)
        img = B.brilho_pontos(img, .75, 22, .55)
        img = B.graduar(img, (.02, .025, .045), (1.0, .9, .78), .82, 1.05)
    return B.vinheta(img, .5)


# ------------------------------------------------------------------ CENA 03 — as sete leis (16–25)
_LEIS_IMG = {}


def lei_img(k):
    if k not in _LEIS_IMG:
        _LEIS_IMG[k] = B.rgba(f"{B.SIM}/leis/{k}_decorativa.png", 800)
    return _LEIS_IMG[k]


def metal_escuro():
    h, w = B.H, B.W
    n1 = cv2.resize(B.campo(h // 2, w * 2, 0, 9, (0, 0), 2)[:, ::4], (w, h))
    n2 = B.campo(h, w, 0, 1.2, (0, 0), 3)
    base = .045 + .03 * n2 + .012 * n1
    rng = np.random.default_rng(4); ris = np.zeros((h, w), np.float32)
    for _ in range(120):
        x, y = rng.integers(0, w), rng.integers(0, h); a = rng.uniform(-.3, .3); L = rng.integers(20, 220)
        cv2.line(ris, (int(x), int(y)), (int(x + L * math.cos(a)), int(y + L * math.sin(a))), float(rng.uniform(.2, .6)), 1, cv2.LINE_AA)
    base = base + ris * .03
    return np.clip(base[..., None] * np.array((.92, .9, .86), np.float32), 0, 1)


T_LEI = [0.55 + i * 0.92 for i in range(7)]


def cena03(t):
    img = metal_escuro().copy() * seg(t, 0, .4)
    n = len(LEIS)
    vert = B.W < B.H
    for i, (k, nome) in enumerate(LEIS):
        t0 = T_LEI[i]
        if t < t0:
            continue
        if vert:
            cx = B.W * (.3 if i % 2 == 0 else .7) if i < 6 else B.W * .5
            cy = B.H * (.1 + .083 * i)
            esc = .2
        else:
            cx = B.W * (.11 + .13 * i); cy = B.H * .46
            esc = .26
        el = lei_img(k)
        dx = dy = 0.0; rot = 0.0
        if k == "conservacao":
            rot = .18 * math.exp(-(t - t0) * 2.2) * math.cos((t - t0) * 9)
        if k == "capacidade":
            tr = clamp((t - t0) / .8)
            if tr < 1:
                dx, dy = B.tremor(t, 2 + 9 * tr, 40)
        k_rev = eo(seg(t, t0, t0 + .55))
        # gravação: máscara radial que cresce + borda incandescente
        h, w = el.shape[:2]
        if rot:
            M = cv2.getRotationMatrix2D((w / 2, h / 2), math.degrees(rot), 1.0)
            el = cv2.warpAffine(el, M, (w, h))
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2) / (w * .5)
        m = np.clip((k_rev * 1.25 - r) / .12, 0, 1)
        borda = np.clip(1 - np.abs(k_rev * 1.25 - r) / .05, 0, 1) * (k_rev < 1)
        e2 = el.copy(); e2[..., 3] *= m
        e2[..., :3] = np.clip(e2[..., :3] + borda[..., None] * np.array((1, .55, .2)) * el[..., 3:4] * 1.5, 0, 1)
        B.colar(img, e2, cx + dx, cy + dy, 1.0, esc * B.W / 1920 * (2 if vert else 1))
        # fenômeno físico de cada lei
        if k == "vinculo" and i > 0:
            tens = math.exp(-(t - t0) * 2.0)
            px = B.W * (.11 + .13 * (i - 1)) if not vert else B.W * .3
            img = fio(img, t, px + 40, cx - 40, cy + (95 if not vert else 0), eo(seg(t, t0, t0 + .3)), 10 * tens, 50, brilho=.55)
        if k == "compatibilidade":
            g = np.zeros((B.H, B.W), np.float32)
            cv2.circle(g, (int(cx), int(cy)), int(70 * B.W / 1920), 1.0, -1)
            g = cv2.GaussianBlur(g, (0, 0), 35 * B.W / 1920) * env(t, t0, t0 + .3, t0 + .7, t0 + 2.0)
            img = B.soma(img, g[..., None] * np.array((1.0, .38, .08), np.float32), .9)
        if k == "vazao":
            kk = seg(t, t0 + .15, t0 + .5)
            if kk > 0:
                cam = np.zeros((B.H, B.W), np.float32); rng = np.random.default_rng(9)
                for a in rng.uniform(0, 6.28, 9):
                    L = (40 + rng.uniform(30, 90)) * kk * B.W / 1920
                    cv2.line(cam, (int(cx + 60 * math.cos(a)), int(cy + 60 * math.sin(a))), (int(cx + (60 + L) * math.cos(a)), int(cy + (60 + L) * math.sin(a))), 1.0, 1, cv2.LINE_AA)
                img = B.soma(img, cam[..., None] * np.array((.75, .82, .9), np.float32), .7 * (1 - .6 * seg(t, t0 + 1, t0 + 2)))
        if k == "dissipacao":
            cam = np.zeros((B.H, B.W), np.float32); rng = np.random.default_rng(12)
            for j in range(40):
                f = ((t - t0) * .6 + j / 40) % 1
                ang = -1.2 + f * 2.6
                rr = 110 + 25 * math.sin(j)
                x = cx + rr * math.cos(ang) * B.W / 1920; y = cy - 120 + f * 240 + 20 * math.sin(ang * 2)
                cv2.circle(cam, (int(x), int(y)), 2, float(math.sin(f * math.pi)), -1, cv2.LINE_AA)
            img = B.soma(img, cv2.GaussianBlur(cam, (0, 0), 1)[..., None] * np.array((.6, .75, .95), np.float32), .55 * env(t, t0, t0 + .4, t0 + 2.4, t0 + 3.2))
    # retorno: um pulso de luz percorre a fileira de volta
    tp = T_LEI[6] + .7
    if t > tp and B.W > B.H:
        f = seg(t, tp, tp + 1.0)
        x = B.W * (.89 - .78 * f)
        g = np.zeros((B.H, B.W), np.float32)
        cv2.ellipse(g, (int(x), int(B.H * .46)), (int(90 * B.W / 1920), int(160 * B.W / 1920)), 0, 0, 360, 1.0, -1)
        img = B.soma(img, cv2.GaussianBlur(g, (0, 0), 40)[..., None] * np.array((1, .8, .45), np.float32), .5 * math.sin(f * math.pi))
    # nomes das leis e composição final
    if t > 6.9:
        a = eio(seg(t, 6.9, 7.6))
        for i, (k, nome) in enumerate(LEIS):
            if B.W > B.H:
                cx = B.W * (.11 + .13 * i); cy = B.H * .66
            else:
                cx = B.W * (.3 if i % 2 == 0 else .7) if i < 6 else B.W * .5; cy = B.H * (.1 + .083 * i) + 95
            B.colar(img, B.texto(nome, "Cinzel-Regular.ttf", 21, (.9, .8, .58), .2), cx, cy, a)
    img = B.brilho_pontos(img, .7, 14, .45)
    img = img * (1 - seg(t, 8.75, 9.0))
    return B.vinheta(img, .55)


# ------------------------------------------------------------------ CENA 04 — Ilan Varek (25–35)
CELULAS = [(2080, 2095), (2080, 2205), (2085, 2320)]


def brilho_celula(img, t, cx, cy, vista, idx, cor, forca):
    x0, y0 = CELULAS[idx]
    esc = B.H / vista
    px, py = (x0 - cx) * esc + B.W / 2, (y0 - cy) * esc + B.H / 2
    g = np.zeros((B.H, B.W), np.float32)
    cv2.ellipse(g, (int(px), int(py)), (int(38 * esc), int(46 * esc)), 0, 0, 360, 1.0, -1)
    g = cv2.GaussianBlur(g, (0, 0), 30 * esc)
    return B.soma(img, g[..., None] * np.array(cor, np.float32), forca)


def cena04(t):
    k = eio(seg(t, 1.6, 6.4))
    cx = lerp(2030, 1160, k); cy = lerp(2210, 520, k); vista = lerp(760, 1050, k) - 60 * seg(t, 6.4, 10)
    img = com_vento("ilan", t, cx, cy, vista, ("Hair", "Upper-clothes", "Scarf"), amp=lerp(2.5, 4.5, k), par=(lerp(0, 25, k), 0), rajada=1 + .6 * env(t, 3, 4, 5, 6.5))
    pul = .5 + .5 * math.sin(t * 2.2)
    img = brilho_celula(img, t, cx, cy, vista, 1, (.55, .05, .03), .55 * seg(t, .4, 1.4) * (.6 + .4 * pul))
    img = vapor(img, t, ((1150 - cx) * B.H / vista + B.W / 2, (650 - cy) * B.H / vista + B.H / 2), 6.8, 3.2, 1.7, B.H / vista * 1.3)
    img = neve_sobre(img, NEVE_FINA, t, .55, .2)
    img = B.brilho_pontos(img, .8, 18, .45)
    img = B.graduar(img, (.015, .025, .05), (.96, .93, .88), .82, 1.08)
    return B.vinheta(img, .55)


# ------------------------------------------------------------------ CENA 05 — o último carrasco (35–45)
T_CONGELA = 5.45


def cena05(t):
    tt = min(t, T_CONGELA)
    k = eio(seg(tt, 0, T_CONGELA))
    vista = lerp(2380, 2200, k); cx, cy = lerp(1150, 1520, k), vista / 2 + 5
    img = com_vento("ponte", tt, cx, cy, vista, ("Upper-clothes", "Pants", "Hair", "Scarf"), amp=7, par=(lerp(-80, 80, k), 0), rajada=1.4 + .6 * math.sin(tt * 1.7), vel=(.6, .08))
    img = neve_sobre(img, NEVASCA, tt, 1.0, .3 * math.sin(tt * .9))
    if 2.6 < tt < 3.5:   # rajada que atravessa o quadro
        r = env(tt, 2.6, 2.85, 3.1, 3.5)
        img = B.misturar(img, np.array((.85, .88, .92), np.float32), B.nevoa(tt * 3, (.9, 0), .55, 1.2, 3) * r)
    img = B.graduar(img, (.03, .04, .06), (.92, .94, .97), .7, 1.05)
    if t > T_CONGELA:     # congela e vira gravura de tinta
        g = eio(seg(t, T_CONGELA + .05, T_CONGELA + .65))
        img = B.gravura(img, t=g)
        if t > T_CONGELA + .5:
            a = eio(seg(t, T_CONGELA + .5, T_CONGELA + 1.3))
            papel = np.array((.86, .81, .70), np.float32)
            ex, ey = B.W * (.82 if B.W > B.H else .5), B.H * (.36 if B.W > B.H else .5)
            m = np.zeros((B.H, B.W), np.float32)
            cv2.circle(m, (int(ex), int(ey)), int(150 * B.W / 1920 * (2 if B.W < B.H else 1)), 1.0, -1, cv2.LINE_AA)
            img = B.misturar(img, papel, cv2.GaussianBlur(m, (0, 0), 3) * a)
            cv2.circle(img, (int(ex), int(ey)), int(150 * B.W / 1920 * (2 if B.W < B.H else 1)), (.08, .06, .05), 2, cv2.LINE_AA)
            em = B.rgba(P["ordem"], 700)
            emb = em.copy(); emb[..., :3] = emb[..., :3] * .3      # o brasão impresso em tinta
            B.colar(img, emb, ex, ey, a, .36 * B.W / 1920 * (2 if B.W < B.H else 1))
            a2 = seg(t, T_CONGELA + .9, T_CONGELA + 2.2)
            fx = np.zeros((B.H, B.W), np.float32)
            bx = .22 if B.W > B.H else .06
            cv2.rectangle(fx, (int(B.W * bx), int(B.H * .72)), (int(B.W * (1 - bx)), int(B.H * (.86 if B.W > B.H else .8))), 1.0, -1)
            img = B.misturar(img, papel, cv2.GaussianBlur(fx, (0, 0), 2) * eio(seg(t, T_CONGELA + .7, T_CONGELA + 1.2)))
            for yy in ((.735, .845) if B.W > B.H else (.728, .792)):
                cv2.line(img, (int(B.W * (bx + .02)), int(B.H * yy)), (int(B.W * (.98 - bx)), int(B.H * yy)), (.08, .06, .05), 1, cv2.LINE_AA)
            B.colar(img, B.texto("O ÚLTIMO CARRASCO", "ArestaTitular-Regular.ttf", 64 if B.W > B.H else 40, (.08, .06, .05), .18 if B.W > B.H else .1, sombra=False),
                    B.W / 2, B.H * (.79 if B.W > B.H else .76), 1.0, 1.0, mascara_x=eio(a2))
    img = img * (1 - seg(t, 9.7, 10.0) * .0)
    return B.vinheta(img, .45)


# ------------------------------------------------------------------ CENA 06 — os outros rostos (45–54)
def vela(img, t, forca=.12):
    f = 1 + forca * (B.campo(8, 8, t, 1, (3.1, 1.7), 1)[0, 0])
    return np.clip(img * np.array((f, f * .97, f * .9), np.float32), 0, 1)


def estandarte(t, x_rel):
    el = V("estandartes", 1600)
    # o segundo estandarte (vermelho, a espada) recortado e ondulando
    h, w = el.shape[:2]
    s = el[int(h * .04):int(h * .93), int(w * .095):int(w * .2)]
    sh, sw = s.shape[:2]
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    onda = np.sin(yy / sh * 9 - t * 9) * (yy / sh) * sw * .06
    s = cv2.remap(s, xx + onda, yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    alt = B.H * 1.15
    s = cv2.resize(s, (int(sw * alt / sh), int(alt)))
    out = np.zeros((B.H, B.W, 3), np.float32); a = np.zeros((B.H, B.W), np.float32)
    x0 = int(x_rel * (B.W + s.shape[1]) - s.shape[1]); y0 = int(-B.H * .08)
    xa, xb = max(0, x0), min(B.W, x0 + s.shape[1])
    if xb > xa:
        out[:, xa:xb] = s[-y0:-y0 + B.H, xa - x0:xb - x0]
        a[:, xa:xb] = 1
    return out, a


def livro(t):
    """O livro aberto se fecha com firmeza: a metade direita gira sobre a lombada (perspectiva) e mostra a capa de couro."""
    base = B.camera(V("livro", 1600), 768, 512, 900)
    capa = B.camera(V("texturas", 1600), 945, 690, 330)
    ang = ei(seg(t, .1, .62)) * math.pi                  # acelera e bate
    lomb = B.W * .5
    out = base.copy()
    if ang > 0:
        sombra = np.linspace(1, .35, B.W - int(lomb))[None, :, None] * (ang / math.pi)
        vazio = seg(ang, math.pi * .5, math.pi * .95)
        out[:, int(lomb):] = base[:, int(lomb):] * (1 - sombra) * (1 - .93 * vazio)
        R = B.W - lomb
        xb = lomb + R * math.cos(ang)                    # borda livre da metade que gira
        lev = R * math.sin(ang) * .16                    # sobe na direção da câmera
        src = np.float32([[0, 0], [R, 0], [R, B.H], [0, B.H]])
        dst = np.float32([[lomb, 0], [xb, -lev], [xb, B.H + lev], [lomb, B.H]])
        face = base[:, int(lomb):] if ang < math.pi / 2 else cv2.flip(capa, 1)[:, :int(R)] * .8
        face = np.ascontiguousarray(face[:, :int(R)])
        M = cv2.getPerspectiveTransform(src, dst)
        cam = cv2.warpPerspective(face, M, (B.W, B.H), borderMode=cv2.BORDER_CONSTANT)
        msk = cv2.warpPerspective(np.ones(face.shape[:2], np.float32), M, (B.W, B.H))
        luz = .55 + .45 * abs(math.cos(ang))
        out = B.misturar(out, cam * luz, msk)
    if t > .62:   # bateu: poeira e a câmera sacode
        k = seg(t, .62, 1.3)
        dx, dy = B.tremor(t, 7 * (1 - k), 55)
        out = np.roll(out, (int(dy), int(dx)), (0, 1))
        cam = np.zeros((B.H, B.W), np.float32); rng = np.random.default_rng(3)
        for _ in range(90):
            a = rng.uniform(-.5, .5) + (math.pi if rng.random() < .5 else 0); v = rng.uniform(.3, 1)
            x = lomb + math.cos(a) * v * 420 * eo(k) * B.W / 1920; y = B.H * .5 + math.sin(a) * v * 120 * eo(k) - 60 * k
            cv2.circle(cam, (int(x), int(y)), 2, float(1 - k), -1, cv2.LINE_AA)
        out = B.soma(out, cv2.GaussianBlur(cam, (0, 0), 1.5)[..., None] * np.array((.9, .8, .6), np.float32), .5)
    return out


def cena06(t):
    if t < 1.6:        # Mara sob as velas
        k = eio(seg(t, 0, 1.6))
        img = plano("mara", t, lerp(1150, 1080, k), lerp(1900, 980, k), lerp(1350, 1150, k), par=(lerp(-20, 10, k), 0))
        img = vela(img, t)
    elif t < 3.0:      # os olhos de Mara correm a linha
        k = eio(seg(t, 1.6, 3.0))
        img = plano("mara", t, lerp(1010, 1110, k) + (90 if B.W < B.H else 0), 630, lerp(440, 400, k))
        img = vela(img, t, .08)
    elif t < 4.8:      # Nara ajusta o instrumento
        k = eio(seg(t, 3.0, 4.8))
        img = plano("nara", t, lerp(900, 950, k), 380, lerp(640, 560, k), par=(20 * k, 0))
        tr = B.tremor(t, 1.2, 30)
        img = np.roll(img, (int(tr[1]), int(tr[0])), (0, 1)) if seg(t, 3.9, 4.1) * (1 - seg(t, 4.1, 4.3)) > 0 else img
        img = B.soma(img, B.brasas(t, 45, 7, (.25, .55), cor=(1, .6, .2)), .9)
    elif t < 5.6:      # estandarte atravessa o quadro
        f = eio(seg(t, 4.8, 5.6))
        fundo = livro(0) * .6
        s, a = estandarte(t, f)
        img = B.misturar(fundo, s, a)
    elif t < 6.8:      # o livro se fecha com firmeza
        img = livro(t - 5.6)
    else:              # silhuetas diante da arquitetura
        k = eio(seg(t, 6.8, 9.0))
        img = plano("grupo", t, 768, lerp(540, 520, k), lerp(900, 820, k), par=(0, 0), dolly=.3 * k)
        img = B.raios(img, (.5, .25), t, .35)
    img = B.brilho_pontos(img, .8, 14, .4)
    img = B.graduar(img, (.02, .022, .03), (1.0, .92, .8), .85, 1.06)
    return B.vinheta(img, .5)


# ------------------------------------------------------------------ CENA 07 — Aurelia (54–65)
def cena07(t):
    if t < 2.2:        # luz dourada no templo
        k = eio(seg(t, 0, 2.2))
        img = plano("templo", t, 768, lerp(500, 470, k), lerp(980, 900, k), dolly=.35 * k)
        img = B.raios(img, (.5, .18), t, .5)
    elif t < 4.2:      # o tecido delicado
        k = eio(seg(t, 2.2, 4.2))
        im = V("veu")
        mo = np.ones((B.H, B.W), np.float32)
        dx, dy = B.vento(mo, t, 7, 1.0, (.18, .05), 2)
        img = B.camera(im, lerp(210, 250, k), lerp(720, 660, k), 360, desl=(dx * .36, dy * .36))
    elif t < 5.6:      # a mão
        k = eio(seg(t, 4.2, 5.6))
        im = V("veu")
        mo = np.ones((B.H, B.W), np.float32)
        dx, dy = B.vento(mo, t, 4, 1.0, (.15, .05), 3)
        img = B.camera(im, lerp(920, 935, k), lerp(215, 195, k), 280, desl=(dx * .28, dy * .28))
    else:              # a câmera sobe e revela Aurelia
        k = eio(seg(t, 5.6, 9.4))
        cx = lerp(640, 700, k) + (120 * k if B.W < B.H else 0); cy = lerp(2150, 900, k); vista = lerp(1150, 1300, k)
        img = com_vento("aurelia", t, cx, cy, vista, ("Hair",), amp=4.5, par=(lerp(0, 18, k), 0), vel=(.12, .04))
        # respiração: o peito sobe devagar
        img = B.raios(img, (.55, .1), t, .22, (1, .85, .55))
    img = B.brilho_pontos(img, .82, 22, .5)
    img = B.graduar(img, (.03, .025, .02), (1.0, .95, .86), .9, 1.04)
    return B.vinheta(img, .5)


# ------------------------------------------------------------------ CENA 08 — o impossível (65–77)
CORTES08 = [0.0, 1.3, 2.7, 4.0, 5.5, 7.1, 8.6, 10.1, 12.0]


def rachadura(t, cx, cy, crescer, seed=1):
    rng = np.random.default_rng(seed)
    cam = np.zeros((B.H, B.W), np.float32)
    for r in range(7):
        x, y = cx, cy; a = rng.uniform(0, 6.28)
        passos = int(60 * crescer)
        for i in range(passos):
            a += rng.normal(0, .14)
            nx, ny = x + math.cos(a) * 9 * B.W / 1920, y + math.sin(a) * 9 * B.W / 1920
            cv2.line(cam, (int(x), int(y)), (int(nx), int(ny)), 1.0, 1 if i > 20 else 2, cv2.LINE_AA)
            x, y = nx, ny
            if rng.random() < .05:
                a += rng.choice([-1, 1]) * .9
    return cam


def cena08(t):
    i = max(j for j in range(8) if CORTES08[j] <= t)
    tl = t - CORTES08[i]
    dur = CORTES08[i + 1] - CORTES08[i]
    if i == 0:     # A: o fio se tensiona violentamente
        img = aco(t) * .7
        sh = B.tremor(t, 10, 50)
        img = fio(img, t, -50, B.W + 50, B.H * .5 + sh[1], 1.0, 40 * math.exp(-tl * 3), 70, brilho=1.4, esp=2.2)
    elif i == 1:   # B: a lente revela a perturbação
        cx, cy, vista = 1240, 330, 420
        im = V("lente")
        mo = np.ones((B.H, B.W), np.float32)
        y, x = np.mgrid[0:B.H, 0:B.W].astype(np.float32)
        r = np.sqrt((x - B.W * .5) ** 2 + (y - B.H * .5) ** 2) / (B.H * .3)
        onda = np.sin(r * 18 - tl * 14) * np.clip(1 - r, 0, 1) * 6
        img = B.camera(im, cx, cy, vista - 40 * tl, desl=(onda, onda * .5))
        img = B.soma(img, np.clip(1 - r, 0, 1)[..., None] ** 3 * np.array((1, .5, .15)), .25 * (.6 + .4 * math.sin(tl * 20)))
    elif i == 2:   # C: a célula da manopla reage
        cx, cy, vista = 2080, 2205, 520
        d = B.tremor(t, 6 * seg(tl, .3, .9), 45)
        img = plano("ilan", t, cx + d[0], cy + d[1], vista)
        img = brilho_celula(img, t, cx, cy, vista, 1, (1.0, .35, .08), lerp(.2, 1.6, seg(tl, 0, 1.0)))
        img = brilho_celula(img, t, cx, cy, vista, 0, (1.0, .5, .15), .5 * seg(tl, .6, 1.2))
    elif i == 3:   # D: o gelo racha
        cx, cy, vista = 2900, 2080, 620
        d = B.tremor(t, 3, 30)
        img = plano("ponte", t, cx + d[0], cy + d[1], vista)
        cam = rachadura(t, B.W * .52, B.H * .55, eo(seg(tl, .1, 1.2)))
        cam = cv2.dilate(cam, np.ones((3, 3), np.uint8))
        img = B.misturar(img, np.array((.02, .03, .05), np.float32), cv2.GaussianBlur(cam, (0, 0), 2.5) * .8)
        img = B.misturar(img, np.array((.85, .95, 1.0), np.float32), cam * .95)
        img = B.soma(img, cv2.GaussianBlur(cam, (0, 0), 8)[..., None] * np.array((.5, .75, 1.0)), .6)
    elif i == 4:   # E: Ilan gira o corpo e saca a espada
        k = eo(seg(tl, 0, .45))
        cx = lerp(330, 460, k); vista = lerp(660, 600, seg(tl, 0, 1.6))
        img = plano("golpe", t, cx, 560, vista, par=(14 * k, 0))
        img = np.clip(img * 1.25, 0, 1)
        img = B.borrao_mov(img, 60 * (1 - k), 0)
        if .4 < tl < .55:
            img = np.clip(img + .35 * (1 - abs(tl - .47) / .08), 0, 1)
    elif i == 5:   # F: neve e gelo lançados por uma transferência de força
        cx, cy, vista = 1350, 1500, 1700
        y, x = np.mgrid[0:B.H, 0:B.W].astype(np.float32)
        ox, oy = B.W * .5, B.H * .92
        rr = np.sqrt((x - ox) ** 2 + (y - oy) ** 2)
        frente = eo(seg(tl, .05, .9)) * B.W * .9
        anel = np.exp(-((rr - frente) / 40) ** 2) * (1 - seg(tl, .6, 1.4))
        img = plano("ponte", t, cx, cy, vista, desl=((x - ox) / (rr + 1) * anel * 18, (y - oy) / (rr + 1) * anel * 18))
        cam = np.zeros((B.H, B.W), np.float32); rng = np.random.default_rng(8)
        for _ in range(260):
            a = rng.uniform(-math.pi * .95, -math.pi * .05); v = rng.uniform(.3, 1.2)
            d = eo(seg(tl, .05, 1.4)) * v * B.W * .6
            px, py = ox + math.cos(a) * d, oy + math.sin(a) * d + 300 * seg(tl, .5, 1.5) ** 2 * v
            cv2.circle(cam, (int(px), int(py)), int(1 + 3 * rng.random()), float(1 - seg(tl, .9, 1.5)), -1, cv2.LINE_AA)
        img = B.misturar(img, np.array((.9, .94, 1.0), np.float32), cv2.GaussianBlur(cam, (0, 0), 1.2) * .9)
        img = B.misturar(img, np.array((.85, .9, .95), np.float32), anel * .25)
    elif i == 6:   # G: a estrutura metálica vibra sob pressão
        cx, cy, vista = 1080, 360, 600
        d = B.tremor(t, 2 + 5 * seg(tl, 0, 1.2), 60)
        img = plano("sotao", t, cx + d[0], cy + d[1], vista)
        g = np.zeros((B.H, B.W), np.float32); cv2.circle(g, (int(B.W * .55), int(B.H * .5)), int(B.H * .35), 1.0, -1)
        img = B.soma(img, cv2.GaussianBlur(g, (0, 0), 90)[..., None] * np.array((1, .3, .08)), .35 * seg(tl, 0, 1.2))
        img = B.misturar(img, np.array((.8, .8, .82), np.float32), B.nevoa(t * 2, (.0, -.4), .25, 1.4, 2))
    else:          # H: os olhos de Ilan, concentrado
        k = eio(seg(tl, 0, 1.9))
        img = plano("ilan", t, 1150, 395, lerp(360, 320, k))
        foco = 1 - seg(tl, .1, .6)
        if foco > 0:
            img = cv2.GaussianBlur(img, (0, 0), 1 + 9 * foco)
    # corte seco: um quadro de clarão em cada corte
    if tl < 1 / 24 and i > 0:
        img = np.clip(img * 1.6 + .08, 0, 1)
    img = B.brilho_pontos(img, .82, 14, .45)
    img = B.graduar(img, (.02, .03, .05), (.98, .94, .88), .85, 1.12)
    return B.vinheta(img, .5)


# ------------------------------------------------------------------ CENA 09 — a pergunta (77–84)
def cena09(t):
    k = eio(seg(t, 0, 7))
    img = plano("portal", t, 760, lerp(660, 650, k), lerp(560, 500, k), dolly=.25 * k)
    l = img.mean(axis=2, keepdims=True)
    img = l + (img - l) * .45                      # o que está à frente fica frio e calado
    img = neve_sobre(img, NEVE_FINA, t * .6, .5)
    img = B.graduar(img, (.02, .03, .05), (.86, .9, .96), .8, 1.1, 1.05)
    img = img * (1 - seg(t, 6.6, 6.7))             # corte imediato para preto
    return B.vinheta(img, .6)


# ------------------------------------------------------------------ CENA 10 — o título (84–90)
def varredura(el, f):
    """Reflexo metálico que atravessa o emblema/letreiro."""
    h, w = el.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pos = (xx / w + yy / h * .35) - lerp(-.4, 1.4, f)
    band = np.exp(-(pos / .06) ** 2)
    out = el.copy(); out[..., :3] = np.clip(el[..., :3] + band[..., None] * .55 * el[..., 3:4], 0, 1)
    return out


# A logo se monta por partes. Instantes (s, relativos a 84) em que cada peça trava no lugar; o áudio usa os mesmos.
T_PECAS = {"eixo": .38, "estandarte": .72, "arco": 1.02, "balanca": 1.3, "halo": 1.9}
T_PEROLAS = [1.38 + i * .065 for i in range(7)]
T_LETRAS = (1.95, 2.75)                       # as letras do título entram em sequência neste intervalo
T_FILETE, T_SUB, T_CREDITO = 2.7, 2.95, 3.25
PEROLAS = [(512, y) for y in (310, 381, 453, 524, 596, 666, 737)]
_PECAS = {}


def pecas_emblema():
    """Divide o emblema oficial em peças pela geometria do desenho (sem redesenhar nada)."""
    if _PECAS:
        return _PECAS
    em = B.rgba(P["emblema"], 1024)
    h, w = em.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = em[..., 3] > .02
    r, g, b_ = em[..., 0], em[..., 1], em[..., 2]
    perola = np.zeros((h, w), bool)
    for cx, cy in PEROLAS:
        perola |= (xx - cx) ** 2 + (yy - cy) ** 2 < 33 ** 2
    eixo = a & (np.abs(xx - 512) < 40) & ((yy < 135) | (yy > 205) | (np.abs(xx - 512) < 15)) & ~perola
    vermelho = (r > g * 1.5) & (r > b_ * 1.4) & (r > .12)
    estandarte = a & (np.abs(xx - 512) < 102) & (yy > 212) & (yy < 870) & ~eixo & ~perola
    estandarte &= vermelho | (np.abs(np.abs(xx - 512) - 92) < 12) | (yy > 760)
    balanca = a & (xx > 330) & (xx < 692) & (yy > 248) & (yy < 482) & ~eixo & ~estandarte & ~perola
    balanca &= ((yy >= 300) | ((xx > 376) & (xx < 650))) & (xx > 336) & (xx < 688)
    # arco: o que fica dentro do contorno externo do arco (elipse no topo + pilares)
    dentro = (((xx - 512) / 262) ** 2 + ((yy - 420) / 290) ** 2 < 1) | ((np.abs(xx - 512) < 262) & (yy > 420))
    arco = a & dentro & ~eixo & ~estandarte & ~balanca & ~perola
    halo = a & ~eixo & ~estandarte & ~balanca & ~arco & ~perola
    def peca(m):
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), .7)
        out = em.copy(); out[..., 3] *= m
        return out
    _PECAS.update(eixo=peca(eixo), estandarte=peca(estandarte), balanca=peca(balanca),
                  arco_e=peca(arco & (xx < 512)), arco_d=peca(arco & (xx >= 512)), halo=peca(halo),
                  perolas=[peca((xx - cx) ** 2 + (yy - cy) ** 2 < 33 ** 2) for cx, cy in PEROLAS])
    return _PECAS


def _sobre(base, el):
    a = el[..., 3:4]
    out = base.copy()
    out[..., :3] = el[..., :3] * a + base[..., :3] * (1 - a)
    out[..., 3:4] = a + base[..., 3:4] * (1 - a)
    return out


def _mover(el, dx=0., dy=0., ang=0., esc=1., cx=512, cy=512):
    M = cv2.getRotationMatrix2D((cx, cy), ang, esc); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(el, M, (el.shape[1], el.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))


def eob(x, s=1.9):
    """Sai com um pequeno passo além do alvo e volta (o encaixe)."""
    x = clamp(x, 0, 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def emblema_montado(t):
    pc = pecas_emblema()
    tela = np.zeros_like(pc["eixo"])
    brilhos = []                                         # (cx, cy, força) dos encaixes, para as faíscas
    # halo: os raios vêm de fora para dentro, girando
    k = seg(t, T_PECAS["halo"] - .5, T_PECAS["halo"])
    if k > 0:
        e = eob(k, 1.2)
        tela = _sobre(tela, _mover(pc["halo"], ang=(1 - e) * -28, esc=lerp(1.7, 1.0, e)) * np.array([1, 1, 1, eo(k)], np.float32))
    # arco: as duas metades deslizam dos lados
    k = seg(t, T_PECAS["arco"] - .42, T_PECAS["arco"])
    if k > 0:
        e = eob(k)
        for nome, lado in (("arco_e", -1), ("arco_d", 1)):
            tela = _sobre(tela, _mover(pc[nome], dx=lado * (1 - e) * 420, ang=lado * (1 - e) * 9) * np.array([1, 1, 1, eo(k * 1.6)], np.float32))
    # estandarte: desenrola de cima para baixo
    k = seg(t, T_PECAS["estandarte"] - .36, T_PECAS["estandarte"])
    if k > 0:
        e = eo(k)
        est = pc["estandarte"].copy()
        corte = lerp(195, 875, e)
        yy = np.arange(1024, dtype=np.float32)[:, None]
        est[..., 3] *= np.clip((corte - yy) / 18, 0, 1)
        tela = _sobre(tela, est)
    # balança: cai de cima e assenta
    k = seg(t, T_PECAS["balanca"] - .34, T_PECAS["balanca"])
    if k > 0:
        e = eob(k, 2.4)
        tela = _sobre(tela, _mover(pc["balanca"], dy=-(1 - e) * 260, ang=(1 - e) * 6, cx=512, cy=265) * np.array([1, 1, 1, eo(k * 1.5)], np.float32))
    # eixo (a espada): desce do alto como uma estaca
    k = seg(t, T_PECAS["eixo"] - .3, T_PECAS["eixo"])
    if k > 0:
        e = ei(k)
        tela = _sobre(tela, _mover(pc["eixo"], dy=-(1 - e) * 900))
    # pérolas: acendem uma a uma, de cima para baixo
    for i, tp in enumerate(T_PEROLAS):
        k = seg(t, tp - .12, tp)
        if k > 0:
            e = eob(k, 2.6)
            cx, cy = PEROLAS[i]
            tela = _sobre(tela, _mover(pc["perolas"][i], esc=max(.01, e), cx=cx, cy=cy) * np.array([1, 1, 1, min(1, k * 2)], np.float32))
            brilhos.append((cx, cy, .5 * env(t, tp, tp + .02, tp + .05, tp + .35)))
    for nome, (cx, cy) in (("eixo", (512, 880)), ("estandarte", (512, 820)), ("arco", (512, 140)), ("balanca", (512, 270)), ("halo", (512, 400))):
        tp = T_PECAS[nome]
        f = env(t, tp, tp + .015, tp + .06, tp + (.9 if nome == "halo" else .45))
        if f > 0:
            brilhos.append((cx, cy, f * (1.4 if nome == "halo" else 1.0)))
    return tela, brilhos


_LETRAS = []


def letras_titulo():
    """Glifos do letreiro oficial (componentes ligados após uma dilatação), ordenados por linha e da esquerda à direita."""
    if _LETRAS:
        return _LETRAS
    le = B.rgba(P["lettering"], 1024)
    a = (le[..., 3] > .08).astype(np.uint8)
    d = cv2.dilate(a, np.ones((9, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(d)
    glifos = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if area < 1200 or h < 40 or y > 280 or x < 50 or x + w > 990:   # fora: riscos da textura, filete e subtítulo
            continue
        m = (lab == i) & (a > 0)
        glifos.append((0 if cen[i][1] < 150 else 1, x, m, cen[i]))
    glifos.sort(key=lambda g: (g[0], g[1]))
    resto = np.ones(a.shape, np.float32)
    for g in glifos:
        resto[g[2]] = 0
    yy = np.arange(le.shape[0])[:, None] * np.ones((1, le.shape[1]))
    filete = (yy > 280) & (yy < 318); sub = yy >= 318
    def camada(m):
        out = le.copy(); out[..., 3] *= m.astype(np.float32); return out
    _LETRAS.extend([[camada(g[2]) for g in glifos], [tuple(g[3]) for g in glifos],
                    camada(filete * resto), camada(sub * resto)])
    return _LETRAS


def letreiro_montado(t):
    glifos, centros, filete, sub = letras_titulo()
    tela = np.zeros_like(filete)
    a0, a1 = T_LETRAS
    for i, (g, (cx, cy)) in enumerate(zip(glifos, centros)):
        tp = lerp(a0, a1, i / max(1, len(glifos) - 1))
        k = seg(t, tp - .22, tp)
        if k <= 0:
            continue
        e = eob(k, 2.2)
        lado = -1 if i % 2 else 1
        tela = _sobre(tela, _mover(g, dy=-(1 - e) * 60, ang=lado * (1 - e) * 14, esc=lerp(1.25, 1, e), cx=cx, cy=cy)
                      * np.array([1, 1, 1, min(1, k * 2.2)], np.float32))
    k = eio(seg(t, T_FILETE, T_FILETE + .4))
    if k > 0:                                            # o filete cresce do losango para os lados
        f = filete.copy(); xx = np.abs(np.arange(1024, dtype=np.float32) - 512)[None, :]
        f[..., 3] *= np.clip((k * 380 - xx) / 14, 0, 1); tela = _sobre(tela, f)
    k = eo(seg(t, T_SUB, T_SUB + .5))
    if k > 0:
        tela = _sobre(tela, _mover(sub, dy=(1 - k) * 14) * np.array([1, 1, 1, k], np.float32))
    return tela


def cena10(t):
    img = np.zeros((B.H, B.W, 3), np.float32)
    vert = B.W < B.H
    em, brilhos = emblema_montado(t)
    fl = seg(t, T_PECAS["halo"] + .05, T_PECAS["halo"] + 1.0)
    if fl > 0:
        em = varredura(em, fl)
    ey = B.H * (.32 if not vert else .3)
    esc = (.42 if not vert else .36) * B.H / 1024 * (1.0 + .035 * seg(t, 0, 6))
    B.colar(img, em, B.W / 2, ey, 1.0, esc)
    # luz quente atrás do emblema quando ele fecha
    g = np.zeros((B.H, B.W), np.float32)
    cv2.circle(g, (int(B.W / 2), int(ey)), int(B.H * .2), 1.0, -1)
    img = B.soma(img, cv2.GaussianBlur(g, (0, 0), 120)[..., None] * np.array((.5, .38, .18)),
                 .3 * env(t, T_PECAS["halo"], T_PECAS["halo"] + .1, T_PECAS["halo"] + .8, 4.5))
    # faíscas de cada encaixe
    for cx, cy, f in brilhos:
        px, py = B.W / 2 + (cx - 512) * esc, ey + (cy - 512) * esc
        m = np.zeros((B.H, B.W), np.float32)
        cv2.circle(m, (int(px), int(py)), max(2, int(6 * esc * 2)), 1.0, -1)
        img = B.soma(img, cv2.GaussianBlur(m, (0, 0), 14 * B.H / 1080)[..., None] * np.array((1., .82, .5)), 1.6 * f)
    # onda de choque quando o halo trava
    th = T_PECAS["halo"]
    k = seg(t, th, th + .7)
    if 0 < k < 1:
        m = np.zeros((B.H, B.W), np.float32)
        cv2.circle(m, (int(B.W / 2), int(ey)), int(lerp(.1, .75, eo(k)) * B.H), 1.0, max(2, int(10 * B.H / 1080)))
        img = B.soma(img, cv2.GaussianBlur(m, (0, 0), 6)[..., None] * np.array((.9, .75, .45)), .45 * (1 - k))
    le = letreiro_montado(t)
    fl2 = seg(t, T_LETRAS[1] + .1, T_LETRAS[1] + 1.2)
    if 0 < fl2 < 1:
        le = varredura(le, fl2)
    B.colar(img, le, B.W / 2, B.H * (.66 if not vert else .58), 1.0, (1.02 if not vert else .95) * B.W / 1024 * (.62 if not vert else 1))
    a3 = eio(seg(t, T_CREDITO, T_CREDITO + .7))
    B.colar(img, B.texto("UMA SAGA DE WERIK MARTINS", "Cinzel-Regular.ttf", 24, (.82, .72, .52), .35), B.W / 2, B.H * (.9 if not vert else .7), a3)
    img = img * (1 - seg(t, 5.2, 6.0))
    return img


# ------------------------------------------------------------------ linha do tempo
LINHA = [(0.0, 7.0, cena01), (7.0, 16.0, cena02), (16.0, 25.0, cena03), (25.0, 35.0, cena04), (35.0, 45.0, cena05),
         (45.0, 54.0, cena06), (54.0, 65.0, cena07), (65.0, 77.0, cena08), (77.0, 84.0, cena09), (84.0, 90.0, cena10)]
DUR = 90.0


# ------------------------------------------------------------------ letreiros (no lugar da narração)
# (início, fim, linhas, posição vertical relativa); a segunda linha pode entrar depois (atraso)
LETREIROS = [
    (8.0, 11.45, ["EM ARESTA, A MAGIA NÃO CRIA PODER."], .8, 0.0),
    (9.9, 11.45, ["ELA O MOVE."], .87, 0.0),
    (22.5, 24.75, ["E TUDO QUE SE MOVE…"], .83, 0.0),
    (23.6, 24.75, ["DEIXA UM PREÇO."], .9, 0.0),
    (30.3, 34.7, ["SETE LEIS."], .8, 0.0),
    (31.2, 34.7, ["NENHUMA ESCOLHA SEM CONSEQUÊNCIA."], .87, 0.0),
    (36.4, 40.3, ["ILAN VAREK CONHECIA O PESO DE UMA SENTENÇA."], .86, 0.0),
    (60.5, 64.8, ["MAS HÁ PODERES QUE SE ACOSTUMARAM", "A NUNCA SER QUESTIONADOS."], .82, 0.0),
    (70.6, 72.5, ["ELES PODEM PARECER ETERNOS."], .84, 0.0),
    (73.3, 76.6, ["ISSO NÃO SIGNIFICA", "QUE SEJAM INTOCÁVEIS."], .82, 0.0),
    (78.2, 80.6, ["PARA DERRUBAR UM DEUS…"], .8, 0.0),
    (80.9, 83.7, ["…BASTA DESCOBRIR", "O QUE O SUSTENTA."], .8, 0.0),
]


def _quebra(linhas):
    """No vertical, divide linhas longas em duas."""
    if B.W > B.H:
        return linhas
    out = []
    for l in linhas:
        if len(l) > 22:
            p = l.split(" "); meio = len(p) // 2
            out += [" ".join(p[:meio]), " ".join(p[meio:])]
        else:
            out.append(l)
    return out


def letreiro(img, t):
    for a, b, linhas, y, _ in LETREIROS:
        if not (a <= t < b):
            continue
        ent = eo(seg(t, a, a + .7)); sai = 1 - seg(t, b - .35, b) if b - t > .02 else 0.0
        if b in (11.45, 83.7):
            sai = 1.0                                     # some junto com o corte seco
        al = ent * sai
        ls = _quebra(linhas)
        tam = 40 if B.W > B.H else 50
        alt = tam * (1.75 if B.W > B.H else 1.6) * B.W / (1920 if B.W > B.H else 1080)
        yv = {.8: .7, .87: .86, .83: .78, .9: .9, .86: .8, .82: .74, .84: .78}.get(y, y)
        y0 = B.H * (y if B.W > B.H else yv) - (len(ls) - 1) * alt / 2
        # sombra suave atrás das linhas (legibilidade sobre áreas claras)
        yy = np.arange(B.H, dtype=np.float32)[:, None]
        ym = y0 + (len(ls) - 1) * alt / 2
        faixa = np.exp(-((yy - ym) / (alt * (len(ls) * .55 + .9))) ** 2) * np.ones((1, B.W), np.float32)
        xx = np.linspace(-1, 1, B.W, dtype=np.float32)[None, :]
        faixa = faixa * np.exp(-(xx / .62) ** 2)
        img = img * (1 - .5 * al * faixa[..., None])
        for j, l in enumerate(ls):
            el = B.texto(l, "ArestaTitular-Regular.ttf", tam, (.95, .9, .78), .16)
            if ent < 1:                                   # entra do desfocado para o nítido
                el = el.copy(); el[..., 3] = cv2.GaussianBlur(el[..., 3], (0, 0), .1 + 3 * (1 - ent))
            B.colar(img, el, B.W / 2, y0 + j * alt - 6 * (1 - ent), al)
    return img


def quadro(t, barras=False, textos=True):
    for a, b, f in LINHA:
        if a <= t < b:
            img = f(t - a)
            break
    else:
        img = np.zeros((B.H, B.W, 3), np.float32)
    if textos:
        img = letreiro(img, t)
    img = B.grao(img, t, .03)
    if barras:
        img = B.barras(img)
    return img
