#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Animações canônicas da magia (Transposição), uma por técnica, a partir das fichas técnicas da bíblia interna e do
GUIA_VISUAL_DA_MAGIA. Cada cena abre com uma pintura do banco de arte e segue para a demonstração do mecanismo.
As cenas do cap. 1 vão para exportacoes/motion/magia/; as demais, para a pasta de spoilers, com nomes neutros.
Uso: python3 magia_canonica.py [--teste <cena> <t> ...] [<cena> ...]"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageChops
from magia_motor import *

OUT = f"{ROOT}/exportacoes/motion/magia"
OUT_S = f"{ROOT}/exportacoes/banco_de_arte/CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/motion"


def mascara_circulo(c, r):
    m = Image.new("L", (W, H)); ImageDraw.Draw(m).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255); return m


def aplica_mascara(q, tmp, m):
    q.luz.paste(ImageChops.add(q.luz, tmp.luz), (0, 0), m)
    t2 = tmp.tinta.copy(); t2.putalpha(ImageChops.multiply(t2.getchannel("A"), m)); q.tinta.alpha_composite(t2)


# ================================================================== 1. Aferição (cap. 1)
def _parede():
    im = PLACA.copy(); d = ImageDraw.Draw(im); rnd = random.Random(2)
    for r, y in enumerate(range(0, H, 46)):
        off = 0 if r % 2 else 70
        for x in range(-140 + off, W, 140):
            c = (54 + rnd.randint(-8, 8), 30 + rnd.randint(-5, 5), 24 + rnd.randint(-4, 4))
            d.rectangle([x + 3, y + 3, x + 137, y + 43], fill=c)
    return Image.blend(im, PLACA, .35)
PAREDE = None
PREGOS = [(360, 860), (610, 735), (860, 610), (1110, 490), (1360, 370)]
TELHADO = (1620, 150)
LENTE = [(250, 900), (1520, 300)]


def afericao(t):
    global PAREDE
    if PAREDE is None: PAREDE = _parede()
    if t < 2.9:
        a_img = abertura(t, "06_personagens/PE-021_ilan_afericao.png", "AFERIÇÃO", "LEITURA COM A LENTE · IGNEO", "capítulo 1").render()
        if t < 2.5: return a_img
    q = Quadro(PAREDE)
    caminho = PREGOS + [TELHADO]
    for i, p in enumerate(PREGOS):                                   # pregos pintados da cor da parede: quase invisíveis
        q.dt.ellipse([p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8], fill=(62, 36, 28, 255))
    q.dt.line([(0, 118), (W, 118)], fill=MUTED + (180,), width=3)
    cola(q, texto("telhado", "Cinzel-SemiBold.ttf", 20, MUTED), 1700, 78)
    u = eio(seg(t, 3.0, 9.6)); c = lerp2(LENTE[0], LENTE[1], u); R = 200
    tmp = Quadro()
    poli_elo(tmp, caminho, t, AMBER, vel=1.0, larg=5, periodo=24)
    poli_elo(tmp, caminho, t + .3, BRASA, vel=1.0, larg=11, periodo=24, base=False, alpha=.45)
    for p in PREGOS: ancora(tmp, p, "prego", r=10)
    aplica_mascara(q, tmp, mascara_circulo(c, R))
    q.dt.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], outline=BRONZE + (255,), width=12)
    q.dt.arc([c[0] - R + 14, c[1] - R + 14, c[0] + R - 14, c[1] + R - 14], 200, 250, fill=(240, 236, 226, 120), width=4)
    q.dt.line([(c[0] + R * .7, c[1] + R * .7), (c[0] + R * 1.25, c[1] + R * 1.25)], fill=BRONZE + (255,), width=14)
    for i, p in enumerate(PREGOS):                                   # o giz fica onde a lente passou
        tp = 3.0 + 6.6 * (i + .5) / len(PREGOS)
        g = seg(t, tp, tp + .7)
        if g > 0:
            n = max(2, int(24 * g)); giz(q, [(p[0] + 30 * math.cos(2 * math.pi * k / 24), p[1] + 30 * math.sin(2 * math.pi * k / 24)) for k in range(n)])
            giz_texto(q, ["I", "II", "III", "IV", "V"][i], p[0] - 70, p[1] - 70, seg(t, tp + .3, tp + .8), 34)
            nx_ = caminho[i + 1]; dx, dy = nx_[0] - p[0], nx_[1] - p[1]; L = math.hypot(dx, dy)
            a0 = (p[0] + dx / L * 50, p[1] + dy / L * 50); a1 = (p[0] + dx / L * 130, p[1] + dy / L * 130)
            e = seg(t, tp + .4, tp + 1.0)
            if e > 0:
                giz(q, [a0, lerp2(a0, a1, e)])
                if e >= 1:
                    ang = math.atan2(dy, dx)
                    for s in (2.6, -2.6): giz(q, [a1, (a1[0] + 22 * math.cos(ang + s), a1[1] + 22 * math.sin(ang + s))])
    cabecalho(q, t, "AFERIÇÃO", "LEITURA · IGNEO · CAPÍTULO 1", 2.7, 10.9)
    rotulo(q, t, 3.6, 6.6, "ÂNCORAS: PREGOS DE COBRE, PINTADOS DA COR DA PAREDE", 470, 940, PREGOS[0], 25)
    rotulo(q, t, 5.4, 8.8, "ELO: SÓ A LENTE MOSTRA", 980, 760, (900, 590), 25)
    a = env(t, 5.6, 6.0, 8.4, 8.8); cola(q, texto("as franjas se inclinam no sentido do fluxo", "EBGaramond-Italic.ttf", 28, (220, 206, 178), 0), 1000, 800, a)
    rotulo(q, t, 7.8, 10.8, "O CALOR SOBE PARA O TELHADO", 1120, 160, (1500, 230), 25)
    lei(q, t, "Detecção: o que se sente, o que se marca e o que a lente revela.", 9.4, 11.0)
    img = q.render()
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_AFERICAO = ([(0.3, "sopro", dict(d=1.6, g=.15)), (3.1, "vidro", dict(f=2400, d=1.6, g=.1)), (9.6, "zumbido", dict(d=1.4, f=90, g=.12))]
               + [(3.0 + 6.6 * (i + .5) / 5, "vidro", dict(f=1500 + 180 * i, d=.9, g=.08)) for i in range(5)]
               + [(3.4 + 6.6 * (i + .5) / 5, "sopro", dict(d=.35, g=.18)) for i in range(5)])


# ================================================================== 2. Reversão do sifão (cap. 1)
BX0, BX1 = 560, 1360
PISO = [880 - 124 * k for k in range(6)]                       # PISO[k] = chão do andar k+1; PISO[5] = teto do último
CANO_X = 960
RES = (960, 960)


def _ember(k, j): return (BX0 + 40 + 266 * j + 40, PISO[k] - 30)


def sifao(t):
    if t < 2.9:
        a_img = abertura(t, "06_personagens/PE-020_ilan_sete_chamines.png", "REVERSÃO DO SIFÃO", "SALDO FINAL · IGNEO", "capítulo 1").render()
        if t < 2.5: return a_img
    q = Quadro()
    lin = IVORY + (170,)
    q.dt.rectangle([BX0, PISO[5], BX1, 1000], outline=lin, width=3)
    for k in range(6): q.dt.line([(BX0, PISO[k]), (BX1, PISO[k])], fill=lin, width=2)
    for k in range(5):
        for j in (1, 2): q.dt.line([(BX0 + 266 * j, PISO[k]), (BX0 + 266 * j, PISO[k + 1])], fill=IVORY + (90,), width=2)
    for i in range(7):                                                # sete chaminés; só duas fumegam
        x = BX0 + 50 + i * 112; q.dt.rectangle([x, PISO[5] - 70, x + 34, PISO[5]], outline=lin, width=2)
        if i in (2, 5): vapor(q, (x + 17, PISO[5] - 74), t + 3, 0, 10, 20, 160, .35, i)
    tanques = [(BX0 + 150, PISO[5] - 46), (BX1 - 230, PISO[5] - 46)]
    for x, y in tanques: q.dt.rectangle([x, y, x + 80, y + 46], outline=lin, width=2)
    cola(q, texto("caixas-d'água", "Cinzel-SemiBold.ttf", 16, MUTED), BX1 - 190, PISO[5] - 80, 1, "ct")
    q.dt.line([(CANO_X, PISO[5]), (CANO_X, 930)], fill=COBRE + (160,), width=4)
    ativo = [6.8 + .75 * k for k in range(5)]
    reverso = lambda k: t >= ativo[k]
    for k in range(5):
        aq = seg(t, ativo[k], ativo[k] + 1.3)
        for j in range(3):
            x0 = BX0 + 266 * j; y0, y1 = PISO[k + 1], PISO[k]
            jan = (x0 + 150, y0 + 26, x0 + 230, y0 + 86)
            q.dt.rectangle(jan, outline=IVORY + (120,), width=2)
            geada(q, jan, .9 * (1 - aq), k * 3 + j)
            if aq > 0: q.dl.rectangle([x0 + 6, y0 + 6, x0 + 260, y1 - 6], fill=mul(AMBER, .07 * aq))
            e = _ember(k, j); cor_e = blackbody(.62)
            q.dt.rectangle([e[0] - 14, e[1] - 10, e[0] + 14, e[1] + 10], fill=(40, 30, 26, 255), outline=BRONZE + (255,))
            q.dl.rectangle([e[0] - 10, e[1] - 6, e[0] + 10, e[1] + 6], fill=cor_e)
            caminho = [e, (CANO_X, e[1] + 14), (CANO_X, 930)]
            if t < 5.7:
                poli_elo(q, caminho, t, AMBER, vel=1.0, larg=4, alpha=seg(t, 2.8, 3.6))
            elif reverso(k):
                poli_elo(q, caminho[::-1], t, AMBER, vel=1.0, larg=5, alpha=.4 + .6 * aq)
            else:
                poli_elo(q, caminho, t, AMBER, vel=.15, larg=3, alpha=.18)
    calor_res = lerp(.92, .38, seg(t, 6.8, 11.5))
    for i in range(-3, 4):                                            # colmeia do reservatório
        for r in range(2):
            cx, cy = RES[0] + i * 38 + (19 if r else 0), RES[1] + r * 30
            hexa = [(cx + 17 * math.cos(math.radians(60 * k + 30)), cy + 17 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            c = blackbody(calor_res - .04 * abs(i)); q.dt.polygon(hexa, fill=c + (255,), outline=(120, 90, 60, 255)); q.dl.polygon(hexa, fill=mul(c, .5))
    q.dt.rectangle([1180, 846, 1226, 900], outline=BRONZE + (255,), width=3)
    braco = eo(seg(t, 5.3, 5.8))
    figura(q, 1290, 996, 150, lado=-1, manopla=.36, braco=braco)
    if 5.7 < t < 6.2: brilho(q, (1203, 873), 90, AMBER, 1 - seg(t, 5.7, 6.2))
    if t > 10.2:
        for k, (x, y) in enumerate(tanques): vapor(q, (x + 40, y - 4), t, 10.2, 45, 70, 360, .9, 20 + k)
    rach = (1,) if t > 10.9 else ()
    celulas(q, 1560, 760, [.3, .82 if t < 10.9 else 0.0, .45], 1.1, rach)
    cabecalho(q, t, "REVERSÃO DO SIFÃO", "SALDO FINAL · IGNEO · CAPÍTULO 1", 2.7, 12.9)
    rotulo(q, t, 2.9, 5.6, "FONTE: IGNEOS DE PAREDE DE CALVENOR", 120, 310, _ember(4, 0), 20)
    rotulo(q, t, 3.6, 5.8, "SIFÃO DE ORSK: DESVIA O CALOR ANTES DOS CÔMODOS", 1000, 190, (CANO_X, 300), 20)
    rotulo(q, t, 4.2, 6.4, "RESERVATÓRIO SUPERAQUECIDO", 380, 1020, (RES[0] - 120, RES[1] + 10), 20)
    rotulo(q, t, 5.6, 7.6, "ILAN DESACOPLA O CONTROLE DE ORSK", 1330, 640, (1203, 846), 20)
    rotulo(q, t, 7.0, 9.4, "OS MESMOS ELOS, A FAVOR DO GRADIENTE", 80, 560, (CANO_X - 80, 640), 20)
    rotulo(q, t, 8.2, 10.8, "RUPTURA DE CADÊNCIA: UM ANDAR POR VEZ", 1400, 420, (BX1 - 20, 440), 20)
    cola(q, texto("≈ 15 min", "EBGaramond-Italic.ttf", 30, MUTED, 0), 1420, 470, env(t, 8.4, 8.8, 10.6, 11.0))
    rotulo(q, t, 10.6, 13.0, "RETORNO: VAPOR NAS CAIXAS-D'ÁGUA · CÉLULA 2 RACHADA", 1060, 60, (tanques[1][0] + 40, tanques[1][1]), 20)
    lei(q, t, "Conservação: o calor volta para onde foi tirado.", 11.3, 13.0)
    img = q.render()
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_SIFAO = ([(0.3, "sopro", dict(d=1.6, g=.15)), (2.8, "zumbido", dict(d=2.9, f=70, g=.14)), (5.75, "estalo", dict(d=.5, g=.6)),
             (5.75, "baque", dict(d=1.2, f0=90, f1=40, g=.4)), (10.2, "chiado", dict(d=2.8, g=.35)), (10.9, "estalo", dict(d=.6, g=.7))]
            + [(6.8 + .75 * k, "sino", dict(f0=196 * 1.122 ** k, d=1.6, g=.16)) for k in range(5)])


# ================================================================== 3. Sondagem dupla × eco atrasado (cap. 8)
DISCOS = [520, 700, 880, 1060, 1240, 1420]; PLAT = 700; REAIS = (0, 5)
SOND = [3.4, 4.2, 5.0, 5.8, 6.6, 6.95, 7.9, 8.15, 9.2]
TL0, TL1, TX0, TX1 = 3.0, 10.0, 300, 1620
def _tx(tt): return TX0 + (TX1 - TX0) * (tt - TL0) / (TL1 - TL0)
FALSAS = [3.4 + .8 * k + .45 for k in range(8)]                     # eco atrasado no ritmo antigo


def sondagem(t):
    if t < 2.9:
        a_img = abertura(t, "05_mundo/MU-009_vhalessa_fornalha_velha_noite.png", "SONDAGEM DUPLA", "RUPTURA DE CADÊNCIA · ECO", "capítulo 8").render()
        if t < 2.5: return a_img
    q = Quadro(); lin = IVORY + (170,)
    q.dt.line([(260, PLAT + 14), (1660, PLAT + 14)], fill=lin, width=3)
    q.dt.line([(420, PLAT + 14), (420, 830)], fill=IVORY + (90,), width=2); q.dt.line([(1500, PLAT + 14), (1500, 830)], fill=IVORY + (90,), width=2)
    cola(q, texto("topo da torre", "Cinzel-SemiBold.ttf", 18, MUTED), 1660, PLAT + 26, 1, "rt")
    rv = seg(t, 9.3, 10.0)
    if rv > 0:                                                         # o acumulador de Retorno escondido sob a rota
        q.dt.rectangle([640, PLAT + 30, 1300, PLAT + 120], outline=mul(BRASA, 1.2) + (int(255 * rv),), width=3)
        for k in range(8): elo(q, (660, PLAT + 40 + k * 10), (1280, PLAT + 40 + k * 10), t, BRASA, vel=.4, alpha=.55 * rv, larg=3, base=False, tremor=.6)
    for i, x in enumerate(DISCOS): ancora(q, (x, PLAT + 8), "disco", r=22)
    figura(q, 330, PLAT + 12, 170, manopla=.36, braco=.7)
    mao = (330 + 170 * .38 * .95, PLAT + 12 - 170 * .8 + 30)
    plt = (180, PLAT - 88)
    figura(q, 200, PLAT + 12, 165, cor=(220, 210, 190), braco=.5)
    q.dt.rectangle([plt[0] + 40, plt[1] - 20, plt[0] + 78, plt[1] + 26], fill=(60, 70, 80, 255), outline=PRATA + (255,), width=2)
    for tp in SOND:                                                    # sondagem: anéis de Eco saindo da manopla
        aneis(q, mao, t, tp, ECO, n=1, vel=560, alpha=.9, larg=3, arco=(-30, 30), vida=1.0)
        for i, x in enumerate(DISCOS):
            if i in REAIS or tp < 6.4:
                aneis(q, (x, PLAT + 8), t, tp + .12 + (x - 400) / 900, ECO, n=1, vel=160, alpha=.8, larg=2)
    for tf in FALSAS:
        if tf < 6.4: continue
        for i, x in enumerate(DISCOS):
            if i not in REAIS: aneis(q, (x, PLAT + 8), t, tf, (220, 170, 150), n=1, vel=160, alpha=.8, larg=2)
    marca = seg(t, 8.5, 9.0)
    for i, x in enumerate(DISCOS):
        if i not in REAIS and marca > 0:
            giz(q, [(x - 16, PLAT - 44), (x + 16, PLAT - 12)], marca); giz(q, [(x + 16, PLAT - 44), (x - 16, PLAT - 12)], marca)
    y0, y1 = 860, 1000                                                 # registro: sondagem × resposta
    q.dt.rectangle([TX0 - 10, y0, TX1 + 10, y1], fill=(10, 10, 12, 200), outline=(90, 84, 72, 255))
    q.dt.line([(TX0, y0 + 46), (TX1, y0 + 46)], fill=(70, 66, 58, 255)); q.dt.line([(TX0, y0 + 106), (TX1, y0 + 106)], fill=(70, 66, 58, 255))
    cola(q, texto("sondagem", "Cinzel-SemiBold.ttf", 15, MUTED), TX0 - 20, y0 + 46, 1, "rc")
    cola(q, texto("resposta", "Cinzel-SemiBold.ttf", 15, MUTED), TX0 - 20, y0 + 106, 1, "rc")
    if t > TL0:
        ph = _tx(min(t, TL1)); q.dt.line([(ph, y0 + 6), (ph, y1 - 6)], fill=GOLD + (200,), width=2)
        for tp in SOND:
            if tp <= t: q.dl.line([(_tx(tp), y0 + 28), (_tx(tp), y0 + 64)], fill=ECO, width=4)
            if tp + .2 <= t: q.dl.line([(_tx(tp + .12), y0 + 92), (_tx(tp + .12), y0 + 120)], fill=ECO, width=3)
        for tf in FALSAS:
            if tf <= t and tf > 6.4: q.dl.line([(_tx(tf), y0 + 92), (_tx(tf), y0 + 120)], fill=(235, 120, 100), width=3)
    reg = env(t, 9.9, 10.2, 11.6, 12.0)
    if reg > 0:
        brilho(q, (plt[0] + 59, plt[1] + 3), 50, ECO, reg)
        if t > 10.8: q.dt.line([(plt[0] + 44, plt[1] - 16), (plt[0] + 62, plt[1] + 4), (plt[0] + 74, plt[1] + 22)], fill=(10, 10, 10, 255), width=2)
    cabecalho(q, t, "SONDAGEM DUPLA", "RUPTURA DE CADÊNCIA · ECO · CAPÍTULO 8", 2.7, 11.9)
    rotulo(q, t, 3.3, 5.9, "SONDAGEM: UMA VIBRAÇÃO PEQUENA, PARA MEDIR A RESPOSTA", 560, 520, (mao[0] + 40, mao[1]), 22)
    rotulo(q, t, 6.4, 8.6, "CADÊNCIA IRREGULAR", 800, 560, (_tx(6.95), 880), 22)
    rotulo(q, t, 7.6, 9.8, "ÂNCORA FALSA: REPETE O RITMO ANTIGO, COM ATRASO", 760, 600, (DISCOS[2], PLAT - 20), 22)
    rotulo(q, t, 9.3, 11.4, "EMBAIXO DA ROTA: UM ACUMULADOR DE RETORNO", 700, 800, (900, PLAT + 90), 22)
    rotulo(q, t, 10.0, 12.0, "REGISTRO DE AFERIÇÃO (MARA) · PLACA 3 TRINCADA", 120, 470, (plt[0] + 59, plt[1] - 20), 22)
    lei(q, t, "Sondar é perguntar, e a resposta falsa se denuncia pelo ritmo.", 10.4, 12.0)
    img = q.render()
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_SONDAGEM = ([(0.3, "sopro", dict(d=1.6, g=.15)), (9.3, "zumbido", dict(d=2.2, f=55, g=.2)), (10.85, "estalo", dict(d=.5, g=.5))]
               + [(tp, "sino", dict(f0=880, d=.9, g=.14)) for tp in SOND] + [(tp + .3, "sino", dict(f0=880, d=.6, g=.06)) for tp in SOND]
               + [(tf, "sino", dict(f0=831, d=.7, g=.09)) for tf in FALSAS if tf > 6.4])


# ================================================================== 4. Guarda de Retorno (cap. 15)
GELO = 820


def _trenó(q, x):
    q.dt.rectangle([x - 70, GELO - 60, x + 70, GELO - 12], fill=(34, 30, 26, 255), outline=IVORY + (150,), width=2)
    q.dt.line([(x - 84, GELO - 4), (x + 84, GELO - 4)], fill=IVORY + (150,), width=3)
    rnd = random.Random(x)
    for k in range(14): px, py = x + rnd.uniform(-60, 60), GELO - 62 - rnd.uniform(0, 18); q.dt.ellipse([px - 7, py - 6, px + 7, py + 6], fill=(18, 17, 16, 255))


def _bode(q, x):
    c = IVORY + (150,)
    q.dt.ellipse([x - 40, GELO - 70, x + 30, GELO - 38], outline=c, width=2)
    for dx in (-30, -12, 10, 24): q.dt.line([(x + dx, GELO - 42), (x + dx, GELO - 2)], fill=c, width=2)
    q.dt.line([(x + 28, GELO - 62), (x + 52, GELO - 86)], fill=c, width=2); q.dt.ellipse([x + 44, GELO - 96, x + 64, GELO - 80], outline=c, width=2)
    q.dt.arc([x + 40, GELO - 120, x + 74, GELO - 88], 200, 320, fill=c, width=2)


def guarda(t):
    if t < 2.9:
        a_img = abertura(t, "05_mundo/MU-002_reinos_do_norte.png", "GUARDA DE RETORNO", "SALDO FINAL · FUSO E IMPETUS", "capítulo 15").render()
        if t < 2.5: return a_img
    q = Quadro()
    q.dt.rectangle([0, GELO, W, H], fill=(20, 26, 32, 255)); q.dt.line([(0, GELO), (W, GELO)], fill=(150, 175, 195, 200), width=3)
    for k in range(9): x = 200 + k * 170; q.dt.rectangle([x, 560, x + 60, 590], outline=MUTED + (70,), width=1); q.dt.line([(x + 30, 560), (x + 30, 520)], fill=MUTED + (70,), width=1)
    cola(q, texto("comboio dos Reinos", "Cinzel-SemiBold.ttf", 16, MUTED), 960, 500, 1, "cb")
    for x in (820, 1080): _trenó(q, x)
    for x in (950, 1210): _bode(q, x)
    px = 430 - 190 * eio(seg(t, 8.1, 8.6))
    braco_t = 1 - eo(seg(t, 9.6, 10.6))
    mt = figura(q, 1560, GELO, 430, cor=(225, 205, 175), lado=-1, braco=.95 * braco_t + .05, martelo=True)
    cab = (mt[0], mt[1] - 430 * .36)
    carga_ = env(t, 2.9, 4.2, 9.6, 10.6)
    for k in range(3):
        if carga_ > 0: descarga(q, (cab[0] - 40, cab[1] + random.uniform(-30, 30)), (cab[0] + 40, cab[1] + random.uniform(-40, 40)), int(t * 15) + k, carga_ * .7, 0, larg=3)
    golpe = env(t, 5.7, 5.8, 6.5, 6.9)
    mao = figura(q, px, GELO, 180, manopla=.36 + .6 * seg(t, 5.8, 7.0), braco=.85)
    if golpe > 0:
        pts = descarga(q, cab, (mao[0] + 4, mao[1]), int(t * 20), golpe, 4, larg=7)
        brilho(q, mao, 120, RAIO, golpe)
    for dx in (-22, 22): ancora(q, (px + dx, GELO - 4), "chapa", r=8)
    trincas(q, (px, GELO + 4), seg(t, 6.0, 7.2), 3, 340)
    estrias(q, (px, GELO - 10), t, 5.9, 1.0, 80, 360, semente=4)
    if 8.1 < t < 8.8: estrias(q, (px + 60, GELO - 40), t, 8.1, .7, 60, 260, semente=5, dir=0.0)
    c3 = .3 + .67 * seg(t, 5.8, 7.0) if t < 10 else lerp(.97, .5, seg(t, 10, 11))
    celulas(q, 1700, 120, [.36, .4, c3], 1.0)
    cabecalho(q, t, "GUARDA DE RETORNO", "SALDO FINAL · FUSO E IMPETUS · CAPÍTULO 15", 2.7, 10.9)
    rotulo(q, t, 3.0, 5.6, "THOR: IMPETUS ACOPLADO AO MARTELO E DESCARGA DE FUSO", 900, 300, (cab[0] - 30, cab[1]), 22)
    rotulo(q, t, 3.8, 6.0, "ENTRE OS DOIS: TRENÓS DE CARVÃO E BODES", 640, 880, (1000, GELO - 60), 22)
    rotulo(q, t, 5.9, 8.2, "O GOLPE ENTRA NA CÉLULA", 120, 360, (mao[0], mao[1]), 22)
    rotulo(q, t, 6.4, 8.8, "O CONTRAGOLPE DESCE PELAS CHAPAS DE LASTRO", 120, 900, (px, GELO), 22)
    rotulo(q, t, 7.0, 9.6, "CÉLULA 3 SATURADA", 1520, 300, (1700 + 2 * 50 + 17, 210), 22)
    rotulo(q, t, 8.3, 10.0, "PASSO VETORIAL NO GELO", 120, 520, (px, GELO - 120), 22)
    rotulo(q, t, 9.6, 11.0, "THOR PARA POR ESCOLHA", 1180, 380, (1500, 520), 22)
    lei(q, t, "Capacidade: uma célula, uma vez.", 9.8, 11.0)
    img = q.render(1.2)
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_GUARDA = [(0.3, "sopro", dict(d=1.6, g=.15)), (3.0, "crepita", dict(d=2.7, g=.25)), (5.75, "baque", dict(d=2.2, f0=70, f1=26, g=.9)),
             (5.75, "estalo", dict(d=.8, g=.8)), (6.0, "crepita", dict(d=1.0, g=.4)), (6.3, "estalo", dict(d=.6, g=.5)),
             (8.1, "sopro", dict(d=.7, g=.4)), (9.8, "zumbido", dict(d=1.2, f=60, g=.12))]


# ================================================================== 5. Desvio da descarga de Ulvra (cap. 18)
CHAO = 900; SOL = (1505, 250); PIVO = (1300, CHAO); CRISTA = (690, 300)


def _dragao(q, a=1.0):
    """Dragão de tempestade em silhueta: asas de membrana com dedos, pescoço longo, cauda e crista de lâminas."""
    c = (205, 200, 215, int(200 * a)); f = (18, 18, 24, int(255 * a))
    asa_t = [(470, 250), (380, 120), (300, 60), (250, 110), (200, 150), (210, 200), (300, 230), (420, 270)]
    asa_f = [(520, 250), (600, 110), (690, 40), (720, 100), (760, 150), (730, 200), (640, 240), (560, 275)]
    D = lambda pts: [(x + 170, y + 70) for x, y in pts]
    asa_t, asa_f = D(asa_t), D(asa_f)
    for asa, base in ((asa_t, (640, 325)), (asa_f, (700, 325))):
        q.dt.polygon(asa, fill=f, outline=c)
        for p in asa[1:5]: q.dt.line([base, p], fill=c, width=2)
    corpo = [(330, 300), (420, 262), (540, 258), (610, 270), (660, 250), (700, 222), (735, 214), (760, 226), (740, 238), (700, 250),
             (640, 292), (560, 310), (440, 312), (360, 330), (260, 360), (180, 352), (250, 330)]
    q.dt.polygon(D(corpo), fill=f, outline=c)
    for k in range(7):
        x = 640 + k * 38 - (k > 4) * 10; y = 332 - (k > 4) * (k - 4) * 12
        q.dt.polygon([(x, y), (x + 9, y - 34 - (k % 2) * 14), (x + 18, y + 2)], fill=(130, 140, 190, int(255 * a)))


def descarga_ulvra(t):
    if t < 2.9:
        a_img = abertura(t, "09_engenharia_arcana/EA-008_redes_divinas_draconicas.png", "DESVIO DA DESCARGA", "SALDO FINAL · FUSO · FIO DE INTERDIÇÃO", "capítulo 18").render()
        if t < 2.5: return a_img
    q = Quadro(); lin = IVORY + (170,)
    q.dt.line([(0, CHAO), (W, CHAO)], fill=lin, width=3)
    q.dt.rectangle([1450, 300, 1560, CHAO], outline=lin, width=3)
    q.dt.ellipse([SOL[0] - 62, SOL[1] - 62, SOL[0] + 62, SOL[1] + 62], fill=(70, 52, 30, 255), outline=BRONZE + (255,), width=4)
    for k in range(12):
        a_ = 2 * math.pi * k / 12; q.dt.line([(SOL[0] + math.cos(a_) * 66, SOL[1] + math.sin(a_) * 66), (SOL[0] + math.cos(a_) * 88, SOL[1] + math.sin(a_) * 88)], fill=BRONZE + (255,), width=4)
    q.dt.line([(1585, SOL[1]), (1585, CHAO + 40)], fill=COBRE + (200,), width=4)
    for k in range(3): q.dt.line([(1585 - 26 + k * 9, CHAO + 46 + k * 10), (1585 + 26 - k * 9, CHAO + 46 + k * 10)], fill=COBRE + (200,), width=3)
    rnd = random.Random(4)
    for k in range(180): x, y = rnd.uniform(520, 1180), CHAO - rnd.uniform(2, 30); q.dt.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(150, 140, 125, 200))
    _dragao(q)
    q.dt.line([PIVO, (PIVO[0], PIVO[1] - 90)], fill=COBRE + (255,), width=7); q.dt.ellipse([PIVO[0] - 16, PIVO[1] - 8, PIVO[0] + 16, PIVO[1] + 6], fill=(220, 214, 200, 255))
    figura(q, 1250, CHAO, 140, cor=(220, 205, 185))
    mao = figura(q, 1400, CHAO, 175, manopla=.36 + .5 * seg(t, 6.0, 9.6), braco=.9, lado=-1)
    lider = seg(t, 2.9, 5.0)
    if t < 5.4:                                                        # canal ionizado procurando a praça
        alvo = (900, CHAO - 30); pts = raio(CRISTA, lerp2(CRISTA, alvo, lider), random.Random(3), 5, .16)
        q.dl.line(pts, fill=mul((150, 140, 230), .35 + .2 * math.sin(t * 30)), width=3)
    dobra = (1300, 520)
    if t >= 5.4:
        acop = seg(t, 5.4, 6.0); principal = env(t, 6.0, 6.1, 9.8, 10.4)
        elo(q, (PIVO[0], PIVO[1] - 90), dobra, t, CARGA, vel=-1.2, alpha=acop, larg=4)
        if principal > 0:
            k = .75 + .25 * math.sin(t * 50)
            descarga(q, CRISTA, dobra, int(t * 18), principal * k, 3, larg=8)
            descarga(q, dobra, SOL, int(t * 18) + 1, principal * k, 2, larg=8)
            brilho(q, SOL, 160, RAIO, principal * .8); brilho(q, (1585, CHAO + 40), 90, RAIO, principal * .6)
            elo(q, (1585, SOL[1] + 90), (1585, CHAO + 30), t, RAIO, vel=1.5, alpha=principal, larg=5, base=False)
        fio_a, fio_b = (1120, 640), (900, 820)
        fio = seg(t, 7.2, 7.6)
        if fio > 0: q.dl.line([fio_a, lerp2(fio_a, fio_b, fio)], fill=PRATA, width=3)
        sec = env(t, 7.7, 7.8, 9.2, 9.6)
        if sec > 0:
            pts = raio((1180, 470), (1010, 730), random.Random(int(t * 18) + 7), 5, .18)
            q.dl.line(pts, fill=mul(RAIO, sec * .9), width=5); brilho(q, (1010, 730), 60, AMBER, sec)
            for kk in range(8):
                ang = random.uniform(0, 2 * math.pi); q.dl.line([(1010, 730), (1010 + math.cos(ang) * 30, 730 + math.sin(ang) * 30)], fill=mul(AMBER, sec), width=2)
    queima = t > 9.8
    celulas(q, 1680, 120, [.5 + .45 * seg(t, 6, 9.6) if not queima else 0.0, .4, .42], 1.0, (0,) if queima else ())
    if 9.8 < t < 10.4: brilho(q, (1697, 166), 80, AMBER, 1 - seg(t, 9.8, 10.4))
    cabecalho(q, t, "DESVIO DA DESCARGA", "SALDO FINAL · FUSO · CAPÍTULO 18", 2.7, 11.9)
    rotulo(q, t, 3.0, 5.4, "CANAL IONIZADO DA CRISTA DE ULVRA", 900, 150, (780, 480), 22)
    rotulo(q, t, 5.5, 8.0, "PIVÔ DE COBRE DE NARA: ÂNCORA INTERMEDIÁRIA", 640, 960, PIVO, 22)
    rotulo(q, t, 6.2, 8.8, "SOL DA TORRE: BRONZE ATERRADO", 1060, 150, (SOL[0] - 60, SOL[1]), 22)
    rotulo(q, t, 7.6, 9.8, "FIO DE INTERDIÇÃO NO CANAL SECUNDÁRIO", 300, 640, (1010, 730), 22)
    rotulo(q, t, 9.6, 12.0, "ILAN NÃO ABSORVE: DESVIA · CÉLULA 1 QUEIMADA", 1020, 330, (1697, 230), 22)
    lei(q, t, "Vínculo: a descarga segue a rota que existe.", 10.4, 12.0)
    img = q.render(1.2)
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_ULVRA = [(0.3, "sopro", dict(d=1.6, g=.15)), (2.9, "crepita", dict(d=2.5, g=.2)), (5.4, "zumbido", dict(d=.8, f=140, g=.12)),
            (6.0, "baque", dict(d=2.6, f0=60, f1=24, g=1.0)), (6.0, "estalo", dict(d=1.0, g=.9)), (6.1, "crepita", dict(d=3.6, g=.45)),
            (7.2, "vidro", dict(f=2600, d=.8, g=.08)), (7.75, "estalo", dict(d=.5, g=.6)), (9.8, "estalo", dict(d=.6, g=.7))]


# ================================================================== 6. Anel de soleira (cap. 17)
def anel_soleira(t):
    if t < 2.9:
        a_img = abertura(t, "06_personagens/PE-008_aurelia_dourada_portal.png", "ANEL DE SOLEIRA", "LIMIARES · AURELIA", "capítulo 17").render()
        if t < 2.5: return a_img
    q = Quadro(); lin = IVORY + (160,)
    for x0, nome in ((140, "um cômodo"), (1000, "outro cômodo, longe dali")):
        q.dt.rectangle([x0, 230, x0 + 780, 860], outline=lin, width=3)
        q.dt.line([(x0 + 120, 700), (x0 + 660, 700)], fill=lin, width=4)
        cola(q, texto(nome, "Cinzel-SemiBold.ttf", 18, MUTED), x0 + 390, 250, 1, "ct")
    A_, B_ = (530, 640), (1390, 640)
    cost = seg(t, 3.0, 4.2)
    for c in (A_, B_):
        q.dt.ellipse([c[0] - 46, c[1] - 46, c[0] + 46, c[1] + 46], outline=BRONZE + (255,), width=10)
        if cost > 0 and t < 9.6:
            q.dl.arc([c[0] - 40, c[1] - 40, c[0] + 40, c[1] + 40], -90, -90 + 360 * cost, fill=(255, 226, 150), width=3)
    if t > 9.6:
        f = 1 - seg(t, 9.6, 10.2); q.dl.ellipse([B_[0] - 40, B_[1] - 40, B_[0] + 40, B_[1] + 40], outline=mul((255, 226, 150), f), width=3)
        q.dl.ellipse([A_[0] - 40, A_[1] - 40, A_[0] + 40, A_[1] + 40], outline=mul((255, 226, 150), f), width=3)
    u = seg(t, 4.6, 6.0)                                               # papel dobrado: entra num anel, sai no outro
    if 0 < u < 1:
        p = lerp2((360, 600), A_, min(1, u * 2)) if u < .5 else lerp2(B_, (1580, 600), (u - .5) * 2)
        q.dt.polygon([(p[0] - 22, p[1] - 8), (p[0] + 22, p[1] - 12), (p[0] + 24, p[1] + 10), (p[0] - 20, p[1] + 12)], fill=(236, 228, 210, 255))
    elif u >= 1: q.dt.polygon([(1580 - 22, 692), (1580 + 22, 688), (1582, 700), (1560, 700)], fill=(236, 228, 210, 255))
    if t > 6.2:
        aneis(q, A_, t, 6.3, ECO, n=3, vel=140, alpha=.8); aneis(q, B_, t, 6.36, ECO, n=3, vel=140, alpha=.8)
        figura(q, 300, 860, 200, cor=(225, 205, 175), braco=.5); figura(q, 1700, 860, 200, cor=(220, 210, 190), lado=-1, braco=.2)
    else:
        figura(q, 300, 860, 200, cor=(225, 205, 175), braco=.5 if t > 4.4 else .2); figura(q, 1700, 860, 200, cor=(220, 210, 190), lado=-1, braco=.2)
    if t > 7.4:
        rnd = random.Random(9)
        for k in range(26):
            nasc = 7.4 + rnd.uniform(0, 1.8); v = (t - nasc) / 1.6
            if 0 < v < 1:
                x = (A_[0] - 160 + v * 160) if v < .5 else (B_[0] + (v - .5) * 320); y = A_[1] + rnd.uniform(-20, 20) + math.sin(v * 8 + k) * 8
                q.dt.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(235, 242, 250, 230))
    cabecalho(q, t, "ANEL DE SOLEIRA", "LIMIARES · AURELIA · CAPÍTULO 17", 2.7, 10.9)
    rotulo(q, t, 3.1, 5.0, "DOIS ANÉIS DE BRONZE: AS PONTAS DE UM LIMIAR MÍNIMO", 560, 900, (B_[0], B_[1] + 46), 22)
    rotulo(q, t, 4.7, 9.0, "PASSA VOZ, PAPEL DOBRADO E AR", 700, 140, (B_[0] - 20, B_[1] - 46), 22)
    rotulo(q, t, 7.8, 10.0, "VAZÃO MINÚSCULA: NÃO PASSA GENTE", 160, 940, (A_[0], A_[1] + 46), 22)
    rotulo(q, t, 9.5, 11.0, "AURELIA PODE FECHÁ-LO", 1220, 900, (B_[0] + 30, B_[1] + 40), 22)
    lei(q, t, "Compatibilidade e Vazão: o limiar só passa o que cabe nele.", 9.6, 11.0)
    img = q.render()
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_ANEL = [(0.3, "sopro", dict(d=1.6, g=.15)), (3.0, "vidro", dict(f=1320, d=2.0, g=.12)), (4.8, "sopro", dict(d=.6, g=.25)),
           (6.3, "sino", dict(f0=440, d=1.2, g=.12)), (6.6, "sino", dict(f0=523, d=1.2, g=.1)), (7.4, "sopro", dict(d=1.8, g=.2)),
           (9.6, "vidro", dict(f=990, d=1.2, g=.1))]


# ================================================================== 7. Vetor Passante (cap. 26)
CHAO_V = 800; ARCO_A, ARCO_B = 560, 1360


def _arco(q, x, cor=IVORY):
    q.dt.rectangle([x - 130, CHAO_V - 360, x - 90, CHAO_V], fill=(44, 42, 40, 255), outline=cor + (180,), width=2)
    q.dt.rectangle([x + 90, CHAO_V - 360, x + 130, CHAO_V], fill=(44, 42, 40, 255), outline=cor + (180,), width=2)
    q.dt.arc([x - 130, CHAO_V - 470, x + 130, CHAO_V - 250], 180, 360, fill=cor + (180,), width=40)


def _costura(q, x, u, k=1.0):
    if u <= 0: return
    pts = [(x - 90, CHAO_V)] + [(x + 90 * math.cos(math.radians(180 + a)), CHAO_V - 360 + 90 * math.sin(math.radians(180 + a)) * 1.0) for a in range(0, 181, 6)] + [(x + 90, CHAO_V)]
    pts = [(x - 90, CHAO_V), (x - 90, CHAO_V - 360)] + pts[1:-1] + [(x + 90, CHAO_V - 360), (x + 90, CHAO_V)]
    n = max(2, int(len(pts) * u)); q.dl.line(pts[:n], fill=mul((255, 226, 150), k), width=4)


def vetor(t):
    if t < 2.9:
        a_img = abertura(t, "09_engenharia_arcana/EA-006_transposicao_portal.png", "VETOR PASSANTE", "LIMIARES E IMPETUS · ILAN E AURELIA", "capítulo 26").render()
        if t < 2.5: return a_img
    q = Quadro()
    q.dt.line([(0, CHAO_V), (W, CHAO_V)], fill=IVORY + (170,), width=3)
    _arco(q, ARCO_A); _arco(q, ARCO_B)
    q.dt.line([(ARCO_A, CHAO_V + 60), (ARCO_B, CHAO_V + 60)], fill=MUTED + (220,), width=2)
    for x in (ARCO_A, ARCO_B): q.dt.line([(x, CHAO_V + 48), (x, CHAO_V + 72)], fill=MUTED + (220,), width=2)
    cola(q, texto("30 m", "EBGaramond-Italic.ttf", 30, MUTED, 0), (ARCO_A + ARCO_B) / 2, CHAO_V + 76, 1, "ct")
    cost = seg(t, 3.0, 4.4); k = 1 + .5 * env(t, 6.2, 6.3, 6.6, 6.8)
    _costura(q, ARCO_A, cost, k); _costura(q, ARCO_B, cost, k)
    if cost >= 1:
        for x in (ARCO_A, ARCO_B): q.dl.rectangle([x - 86, CHAO_V - 356, x + 86, CHAO_V - 4], fill=mul((255, 220, 150), .06 * k))
    figura(q, 960, CHAO_V, 190, cor=(240, 220, 170), braco=.9, lado=1)
    q.dl.ellipse([960 - 40, CHAO_V - 196, 960 + 40, CHAO_V - 186], outline=(255, 226, 150), width=2)
    eron_x = 1230; vira = seg(t, 7.3, 7.9)
    figura(q, eron_x, CHAO_V, 185, cor=(200, 190, 200), lado=-1 if vira < .5 else 1, braco=.3 + .5 * vira)
    if t < 6.25:
        x = lerp(220, ARCO_A, eio(seg(t, 4.6, 6.2)))
        figura(q, x, CHAO_V, 180, manopla=.36, braco=.4)
        if t > 4.8: estrias(q, (x - 40, CHAO_V - 90), t, 4.8, 1.4, 40, 200, semente=2, dir=math.pi)
    elif t > 6.7:
        x = lerp(ARCO_B, eron_x + 85, eo(seg(t, 6.7, 7.6)))
        mao = figura(q, x, CHAO_V, 180, manopla=.36, braco=.95, lado=-1)
        if t < 7.3: estrias(q, (x + 40, CHAO_V - 90), t, 6.7, .9, 40, 200, semente=3, dir=0.0)
        trincas(q, (ARCO_B, CHAO_V + 2), seg(t, 6.7, 7.3), 8, 160)
        hit = env(t, 7.7, 7.8, 8.2, 8.7)
        if hit > 0:
            ombro = (eron_x + 12, CHAO_V - 185 * .8); brilho(q, ombro, 90, AMBER, hit)
            q.dl.arc([ombro[0] - 110, ombro[1] - 110, ombro[0] + 110, ombro[1] + 110], 200, 300, fill=mul(PRATA, hit), width=5)
    if 6.2 < t < 6.8:
        cola(q, texto("½ s", "EBGaramond-Italic.ttf", 44, (255, 226, 150), 0), 960, 300, env(t, 6.2, 6.3, 6.6, 6.8), "cc")
    cabecalho(q, t, "VETOR PASSANTE", "LIMIARES E IMPETUS · CAPÍTULO 26", 2.7, 10.9)
    rotulo(q, t, 3.1, 5.4, "COSTURA DE LIMIARES: AURELIA SINCRONIZA OS DOIS ARCOS", 620, 150, (960, CHAO_V - 200), 22)
    rotulo(q, t, 4.7, 6.4, "ILAN ENTRA COM IMPULSO LATERAL", 120, 330, (ARCO_A - 60, CHAO_V - 120), 22)
    rotulo(q, t, 6.1, 7.4, "JANELA DE MEIO SEGUNDO, VISÍVEL PARA QUEM SABE", 600, 220, (ARCO_B, CHAO_V - 380), 22)
    rotulo(q, t, 6.8, 9.4, "NO TRÂNSITO: IMPETUS NO PRÓPRIO CORPO, COM APOIO NO PISO DO ARCO DE SAÍDA", 220, 940, (ARCO_B, CHAO_V), 22)
    rotulo(q, t, 7.9, 10.4, "ERON ANTECIPA EM PARTE: O GOLPE ACERTA O OMBRO", 1100, 330, (eron_x + 12, CHAO_V - 150), 22)
    lei(q, t, "Conservação do momento: o impulso muda de direção, não aparece do nada.", 9.4, 11.0)
    img = q.render()
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_VETOR = [(0.3, "sopro", dict(d=1.6, g=.15)), (3.0, "vidro", dict(f=1100, d=2.4, g=.12)), (4.7, "sopro", dict(d=1.5, g=.35)),
            (6.2, "zumbido", dict(d=.6, f=220, g=.2)), (6.7, "sopro", dict(d=.9, g=.4)), (6.75, "estalo", dict(d=.4, g=.4)),
            (7.75, "baque", dict(d=1.0, f0=140, f1=60, g=.6)), (7.75, "estalo", dict(d=.3, g=.5))]


# ================================================================== 8. Fechamento de Contas (cap. 26)
PORTAO = (230, 520); CISTERNA = (720, 300); MATRIZ = (1180, 560); LAGO = (1580, 880)
NOS = [(820, 760), (1460, 360), (1500, 640)]
LINKS = [(PORTAO, CISTERNA), (CISTERNA, MATRIZ), (PORTAO, MATRIZ), (PORTAO, NOS[0]), (NOS[0], MATRIZ), (MATRIZ, NOS[1]), (MATRIZ, NOS[2])]


def fechamento(t):
    if t < 2.9:
        a_img = abertura(t, "09_engenharia_arcana/EA-007_interdicao_carrascos.png", "FECHAMENTO DE CONTAS", "SALDO FINAL · OBRA-MESTRA", "capítulo 26").render()
        if t < 2.5: return a_img
    q = Quadro()
    q.dt.ellipse([LAGO[0] - 260, LAGO[1] - 120, LAGO[0] + 260, LAGO[1] + 110], fill=(24, 40, 52, 255), outline=(120, 160, 185, 220), width=3)
    cola(q, texto("lago de degelo", "Cinzel-SemiBold.ttf", 18, (150, 180, 200)), LAGO[0], LAGO[1] + 120, 1, "ct")
    q.dt.ellipse([CISTERNA[0] - 70, CISTERNA[1] - 70, CISTERNA[0] + 70, CISTERNA[1] + 70], fill=(22, 34, 46, 255), outline=(140, 175, 205, 220), width=3)
    cola(q, texto("cisterna fria", "Cinzel-SemiBold.ttf", 18, (150, 180, 200)), CISTERNA[0], CISTERNA[1] - 92, 1, "cb")
    q.dt.ellipse([MATRIZ[0] - 110, MATRIZ[1] - 110, MATRIZ[0] + 110, MATRIZ[1] + 110], outline=(130, 124, 116, 255), width=16)
    cola(q, texto("Matriz", "Cinzel-SemiBold.ttf", 20, MUTED), MATRIZ[0], MATRIZ[1], 1, "cc")
    q.dt.rectangle([PORTAO[0] - 60, PORTAO[1] - 150, PORTAO[0] + 60, PORTAO[1] + 150], outline=IVORY + (170,), width=3)
    q.dl.rectangle([PORTAO[0] - 56, PORTAO[1] - 146, PORTAO[0] + 56, PORTAO[1] + 146], outline=(255, 226, 150), width=2)
    cola(q, texto("corredor", "Cinzel-SemiBold.ttf", 18, MUTED), PORTAO[0], PORTAO[1] + 166, 1, "ct")
    fecha = seg(t, 8.0, 9.2); alvo_m = [lerp2(a, b, .5) for a, b in LINKS]
    for i, (a, b) in enumerate(LINKS):
        marca_t = 5.0 + .42 * i; ativo = t > marca_t
        corte = None
        if a == PORTAO and fecha > 0: corte = None if fecha < 1 else .0
        alpha = 1.0 if fecha < 1 or a != PORTAO else .2
        elo(q, a, b, t, BRASA, vel=1.0, larg=6, alpha=alpha, tremor=(.8 if ativo and t < 9.4 else 0))
        elo(q, a, b, t + .2, AMBER, vel=1.0, larg=2, alpha=alpha * .6, base=False)
        g = seg(t, marca_t, marca_t + .4); m = alvo_m[i]
        if g > 0:
            giz(q, [(m[0] + 26 * math.cos(2 * math.pi * k / 20), m[1] + 26 * math.sin(2 * math.pi * k / 20)) for k in range(max(2, int(21 * g)))])
            giz_texto(q, ["I", "II", "III", "IV", "V", "VI", "VII"][i], m[0] + 26, m[1] - 64, g, 30)
        if ativo and t < 9.6 and i > 0:
            elo(q, alvo_m[i - 1], m, t, AMBER, vel=-1.4, larg=2, alpha=.5 * seg(t, marca_t, marca_t + .5), base=False)
    if fecha > 0:
        h_ = 300 * eio(fecha)
        q.dl.rectangle([PORTAO[0] - 80, PORTAO[1] - 150, PORTAO[0] + 80, PORTAO[1] - 150 + h_], fill=(46, 36, 14))
        for k in range(int(h_ // 18)):
            yy = PORTAO[1] - 150 + k * 18 + (t * 40) % 18; q.dl.line([(PORTAO[0] - 76, yy), (PORTAO[0] + 76, yy)], fill=(70, 56, 24), width=1)
        q.dt.rectangle([PORTAO[0] - 80, PORTAO[1] - 150, PORTAO[0] + 80, PORTAO[1] - 150 + h_], outline=(255, 226, 150, 255), width=3)
    ret = seg(t, 9.4, 10.4)
    if ret > 0:
        caminho = [MATRIZ, (1380, 760), (LAGO[0] - 60, LAGO[1] - 40)]
        poli_elo(q, caminho, t, blackbody(.9), vel=2.0, larg=14, alpha=env(t, 9.4, 9.7, 11.0, 11.8))
        boom = env(t, 10.3, 10.5, 11.5, 12.6); brilho(q, LAGO, 220, (255, 236, 210), boom * .75)
        vapor(q, (LAGO[0], LAGO[1] - 40), t, 10.3, 90, 420, 700, 1.0, 31)
    figura(q, 1000, 1000, 150, manopla=.4 + .5 * seg(t, 9.4, 10.3), braco=.8)
    if t > 10.4: brilho(q, (1000 + 150 * .38 * .7 * .7, 1000 - 150 * .8 + 18), 50, AMBER, .6 + .3 * math.sin(t * 9))
    celulas(q, 1680, 100, [.5, .5, .5] if t < 10.4 else [0, 0, 0], 1.0, quebrada=t > 10.4)
    cabecalho(q, t, "FECHAMENTO DE CONTAS", "SALDO FINAL · OBRA-MESTRA · CAPÍTULO 26", 2.7, 12.9)
    rotulo(q, t, 3.0, 5.2, "JURISDIÇÃO DE DRENO DOS CREDORES: CORREDOR, CISTERNA FRIA, MATRIZ", 300, 980, (520, 410), 22)
    rotulo(q, t, 5.2, 8.0, "SETE PONTOS: CADA ELO PASSA A PAGAR O RETORNO DO VIZINHO", 560, 120, alvo_m[3], 22)
    rotulo(q, t, 8.0, 9.8, "QUEM FECHA É AURELIA: FECHO DE FRONTEIRA", 320, 220, (PORTAO[0] + 80, PORTAO[1] - 100), 22)
    rotulo(q, t, 9.6, 12.0, "O RETORNO DO FECHAMENTO VAI PARA O LAGO DE DEGELO", 860, 690, (1380, 760), 22)
    rotulo(q, t, 10.6, 13.0, "MANOPLA DESTRUÍDA · ANTEBRAÇO QUEIMADO", 1180, 260, (1740, 200), 22)
    lei(q, t, "Retorno: a tensão que não é conduzida cobra de alguém.", 11.2, 13.0)
    img = q.render(1.2)
    return transicao(a_img, img, seg(t, 2.5, 2.9)) if t < 2.9 else img


EV_FECHAMENTO = ([(0.3, "sopro", dict(d=1.6, g=.15)), (3.0, "zumbido", dict(d=5.0, f=65, g=.12)), (8.0, "vidro", dict(f=990, d=1.6, g=.12)),
                  (9.4, "zumbido", dict(d=1.0, f=130, g=.2)), (10.3, "baque", dict(d=3.0, f0=55, f1=22, g=1.0)), (10.3, "chiado", dict(d=2.6, g=.5)),
                  (10.4, "estalo", dict(d=.8, g=.8))]
                 + [(5.0 + .42 * i, "sino", dict(f0=294 * 1.122 ** i, d=1.0, g=.12)) for i in range(7)])


CENAS = {
    "afericao": (11.0, afericao, EV_AFERICAO, f"{OUT}/MG-01_afericao.mp4"),
    "sifao": (13.0, sifao, EV_SIFAO, f"{OUT}/MG-02_reversao_do_sifao.mp4"),
    "sondagem": (12.0, sondagem, EV_SONDAGEM, f"{OUT_S}/MG-S03_cena.mp4"),
    "guarda": (11.0, guarda, EV_GUARDA, f"{OUT_S}/MG-S04_cena.mp4"),
    "ulvra": (12.0, descarga_ulvra, EV_ULVRA, f"{OUT_S}/MG-S05_cena.mp4"),
    "anel": (11.0, anel_soleira, EV_ANEL, f"{OUT_S}/MG-S06_cena.mp4"),
    "vetor": (11.0, vetor, EV_VETOR, f"{OUT_S}/MG-S07_cena.mp4"),
    "fechamento": (13.0, fechamento, EV_FECHAMENTO, f"{OUT_S}/MG-S08_cena.mp4"),
}

if __name__ == "__main__":
    if sys.argv[1:2] == ["--teste"]:
        nome = sys.argv[2]
        for ts in sys.argv[3:]:
            random.seed(1); CENAS[nome][1](float(ts)).save(f"{TMP}/teste_{nome}_{float(ts):04.1f}.jpg", quality=85)
        sys.exit()
    for nome in (sys.argv[1:] or list(CENAS)):
        dur, fn, ev, saida = CENAS[nome]
        print(exporta(nome, dur, fn, ev, saida), flush=True)
