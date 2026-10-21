#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPÇÃO B — LIMIAR. Art déco 1925–1932: cada lei é uma porta, o livro é um limiar.
Arco escalonado (zigurate), sunburst de raios alternados, linhas triplas, champanhe sobre meia-noite."""
import math, os, sys, time
from kit import *

OUT = "/home/user/LTKG/exportacoes/identidade_v2/B_Limiar"
os.makedirs(OUT, exist_ok=True)
NOITE, NOITE2, MARFIM, VERDETE = "#0E1626", "#16213A", "#EFE8DA", "#4E8C7E"
CH1, CH2, CH3, CH4 = "#F4E6C1", "#C8A96A", "#8C6E3C", "#E9D39C"
LEIS = ["CONSERVAÇÃO", "VÍNCULO", "COMPATIBILIDADE", "VAZÃO", "DISSIPAÇÃO", "CAPACIDADE", "RETORNO"]
ROM = ["I", "II", "III", "IV", "V", "VI", "VII"]
PRINC = ["PULSO", "BRASA", "TRAMA", "CLARÃO", "ECO", "CARGA"]
ITA, JL, JB, MAR = "Italiana-Regular.ttf", "JosefinSans-Light.ttf", "JosefinSans-SemiBold.ttf", "Marcellus-Regular.ttf"
GAR, GARI, GARSC = "EBGaramond-Regular.ttf", "EBGaramond-Italic.ttf", "EBGaramondSC-Regular.ttf"
ART = "/home/user/LTKG/build/arte/"

_tp_cache = {}
def tp(text, font, size, x, y, tracking=0.0, anchor="start"):
    k = (text, font, size, round(x, 2), round(y, 2), tracking, anchor)
    if k not in _tp_cache:
        _tp_cache[k] = text_path(text, font, size, x, y, tracking, anchor)
    return _tp_cache[k]

_tc_cache = {}
def tc(text, font, size, cx, cy, r, start, tracking=0.0, inward=False):
    k = (text, font, size, cx, cy, r, round(start, 3), round(tracking, 4), inward)
    if k not in _tc_cache:
        _tc_cache[k] = text_on_circle(text, font, size, cx, cy, r, start, tracking, inward)
    return _tc_cache[k]

def arc_text(text, font, size, cx, cy, r, a0, a1):
    """Texto distribuído exatamente entre os ângulos a0→a1 (horário), base sobre o raio r."""
    w0 = text_width(text, font, size, 0)
    n = max(len(text) - 1, 1)
    L = math.radians(a1 - a0) * r
    trk = (L - w0) / (size * n)
    return tc(text, font, size, cx, cy, r, a0, trk)

# ------------------------------------------------------------------ metal
def foil_defs(uid, box=(0, 0, 1000, 1200), glint=None, kind="champanhe"):
    """Gradiente champanhe em diagonal; glint∈[0,1] acrescenta uma faixa de brilho que varre a peça."""
    x1, y1, x2, y2 = box
    if kind == "champanhe":
        st = [(0, CH1), (0.18, "#E2CC97"), (0.36, CH2), (0.56, CH3), (0.74, "#C9AB70"), (0.88, CH4), (1, CH2)]
    else:
        st = [(0, kind), (1, kind)]
    if glint is not None:
        g = glint * 1.3 - 0.15
        base = [s for s in st if abs(s[0] - g) > 0.09]
        def col_at(o):
            for (a, ca), (b, cb) in zip(st, st[1:]):
                if a <= o <= b:
                    f = (o - a) / (b - a) if b > a else 0
                    ca, cb = ca.lstrip("#"), cb.lstrip("#")
                    return "#" + "".join(f"{round(int(ca[i:i+2],16)*(1-f)+int(cb[i:i+2],16)*f):02X}" for i in (0, 2, 4))
            return st[-1][1]
        band = []
        for o, c in ((g - 0.08, None), (g - 0.025, "#FFF8E6"), (g, "#FFFFFF"), (g + 0.025, "#FFF8E6"), (g + 0.08, None)):
            if 0 <= o <= 1:
                band.append((o, c or col_at(o)))
        st = sorted(base + band, key=lambda s: s[0])
    return lin_grad(uid, [(round(o, 4), c) for o, c in st], user=(x1, y1, x2, y2))

def mix(c1, c2, f):
    a, b = c1.lstrip("#"), c2.lstrip("#")
    return "#" + "".join(f"{round(int(a[i:i+2],16)*(1-f)+int(b[i:i+2],16)*f):02X}" for i in (0, 2, 4))

# ------------------------------------------------------------------ geometria déco
def arch_d(cx, yc, a, ybot):
    """Contorno aberto de porta em arco pleno: ombreira esquerda, arco, ombreira direita."""
    return f"M{cx - a:.2f},{ybot:.2f} V{yc:.2f} A{a:.2f},{a:.2f} 0 0 1 {cx + a:.2f},{yc:.2f} V{ybot:.2f}"

def arch_closed(cx, yc, a, ybot):
    return arch_d(cx, yc, a, ybot) + " Z"

def arch_len(a, yc, ybot):
    return 2 * (ybot - yc) + math.pi * a

def diamond(x, y, w, h):
    return f"M{x:.2f},{y - h:.2f} L{x + w:.2f},{y:.2f} L{x:.2f},{y + h:.2f} L{x - w:.2f},{y:.2f} Z"

def rot_pt(px, py, gx, gy, deg):
    g = math.radians(deg); dx, dy = px - gx, py - gy
    return gx + dx * math.cos(g) - dy * math.sin(g), gy + dx * math.sin(g) + dy * math.cos(g)

def zig_d(cx, steps, ybot):
    """Silhueta de zigurate simétrica. steps = [(meia_largura, y_topo_do_degrau), ...] de baixo para cima."""
    pts = [(cx - steps[0][0], ybot)]
    for k, (w, y) in enumerate(steps):
        pts.append((cx - w, y))
        if k + 1 < len(steps):
            pts.append((cx - steps[k + 1][0], y))
    right = [(2 * cx - x, y) for x, y in reversed(pts)]
    return polyline(pts + right, True)

def offset_steps(steps, d):
    return [(w - d, y + d) for w, y in steps]

# ------------------------------------------------------------------ emblema
EC, EYC, EA0, EYB = 500, 500, 270, 1060        # eixo, centro do arco, meia-largura do vão, soleira
EYH, ERS = 760, 150                            # horizonte, raio do sol
EG = (500, 468)                                # pivô da balança
ZIG = [(404, 352), (364, 256), (304, 184), (226, 128), (132, 84)]   # degraus (meia-largura, topo)
ZBOT = 1112

def sword_geom(beam=-7.0, swing=0.0):
    """Espada (eixo da porta) + balança (travessão), em coordenadas do emblema.
    Retorna (sólidos, cortes, facetas): listas de elementos SVG sem cor; 'facetas' recebem sombreado no foil."""
    S, Cut, Fac = [], [], []
    gx, gy = EG
    # pedra-chave = pomo (trapézio com chanfro, anel do pomo vazado)
    kt = [(EC - 19, 248), (EC - 31, 188), (EC + 31, 188), (EC + 19, 248)]
    S.append(f'<path d="{polyline(kt, True)}"/>')
    S.append(f'<path d="{polyline([(EC - 37, 196), (EC - 37, 186), (EC + 37, 186), (EC + 37, 196)], True)}"/>')
    Cut.append(f'<path d="{polyline([(EC - 15, 242), (EC - 24, 200), (EC + 24, 200), (EC + 15, 242)], True)}" fill="none" stroke-width="1.1"/>')
    Cut.append(f'<circle cx="{EC}" cy="219" r="9.5" fill="none" stroke-width="2"/>')
    Cut.append(f'<circle cx="{EC}" cy="219" r="2.8"/>')
    Fac.append(f'<path d="{polyline([(EC, 186), (EC + 37, 186), (EC + 37, 196), (EC + 31, 196), (EC + 19, 248), (EC, 248)], True)}"/>')
    # empunhadura com anéis
    S.append(f'<rect x="{EC - 8}" y="248" width="16" height="{gy - 248 - 16}"/>')
    for yy in range(262, int(gy - 24), 13):
        Cut.append(f'<rect x="{EC - 9}" y="{yy}" width="18" height="2.4"/>')
    S.append(f'<rect x="{EC - 13}" y="248" width="26" height="6"/>')
    S.append(f'<rect x="{EC - 13}" y="{gy - 26}" width="26" height="7"/>')
    Fac.append(f'<rect x="{EC}" y="248" width="13" height="{gy - 248 - 12}"/>')
    # lâmina facetada
    tipy = 1004
    blade = [(EC - 15, gy + 14), (EC + 15, gy + 14), (EC + 15, 906), (EC, tipy), (EC - 15, 906)]
    S.append(f'<path d="{polyline(blade, True)}"/>')
    Fac.append(f'<path d="{polyline([(EC, gy + 14), (EC + 15, gy + 14), (EC + 15, 906), (EC, tipy)], True)}"/>')
    Cut.append(f'<path d="M{EC},{gy + 34} V{tipy - 34}" fill="none" stroke-width="1.3"/>')
    # travessão (balança)
    L, th = 198, 5.5
    def R(px, py): return rot_pt(px, py, gx, gy, beam)
    bar = [R(gx - L, gy - th), R(gx + L, gy - th), R(gx + L, gy + th), R(gx - L, gy + th)]
    S.append(f'<path d="{polyline(bar, True)}"/>')
    Fac.append(f'<path d="{polyline([R(gx - L, gy), R(gx + L, gy), R(gx + L, gy + th), R(gx - L, gy + th)], True)}"/>')
    a, b = R(gx - L + 22, gy), R(gx - 30, gy)
    c, d = R(gx + 30, gy), R(gx + L - 22, gy)
    Cut.append(f'<path d="M{P(*a)} L{P(*b)} M{P(*c)} L{P(*d)}" fill="none" stroke-width="1.1"/>')
    # botão central em losango escalonado
    S.append(f'<path d="{diamond(gx, gy, 24, 30)}"/>')
    Cut.append(f'<path d="{diamond(gx, gy, 14, 18)}" fill="none" stroke-width="1.6"/>')
    Fac.append(f'<path d="M{gx},{gy - 30} L{gx + 24},{gy} L{gx},{gy + 30} Z"/>')
    # pratos em leque, suspensos das pontas (tigela semicircular com nervuras em leque)
    for side in (-1, 1):
        ex, ey = R(gx + side * L, gy)
        S.append(f'<path d="{diamond(ex, ey, 9, 12)}"/>')
        sw = math.radians(swing * side)
        drop, hw, dep = 128, 56, 40
        def F(px, py):            # pendula em torno do ponto de suspensão
            dx, dy = px, py
            return ex + dx * math.cos(sw) - dy * math.sin(sw), ey + dx * math.sin(sw) + dy * math.cos(sw)
        top = drop
        for k in (-1, 0, 1):
            p0, p1 = F(0, 10), F(k * (hw - 6), top)
            S.append(f'<path d="M{P(*p0)} L{P(*p1)}" fill="none" stroke-width="{2.0 if k else 1.2}" stroke-linecap="round"/>')
        rim = [F(-hw - 6, top - 2), F(hw + 6, top - 2), F(hw + 6, top + 3), F(-hw - 6, top + 3)]
        S.append(f'<path d="{polyline(rim, True)}"/>')
        bl, br, bc = F(-hw, top + 6), F(hw, top + 6), F(0, top + 6)
        ang = math.degrees(sw)
        S.append(f'<path d="M{P(*bl)} A{hw},{dep} {ang:.2f} 0 0 {P(*br)} Z"/>')
        for k in range(1, 8):
            t = math.pi * k / 8
            q = F(-hw * math.cos(t) * 0.94, top + 6 + dep * math.sin(t) * 0.94)
            q0 = F(-hw * math.cos(t) * 0.18, top + 6 + dep * math.sin(t) * 0.18)
            Cut.append(f'<path d="M{P(*q0)} L{P(*q)}" fill="none" stroke-width="1.15"/>')
        Fac.append(f'<path d="M{P(*bc)} L{P(*br)} A{hw},{dep} {ang:.2f} 0 1 {P(*F(0, top + 6 + dep))} Z"/>')
    return S, Cut, Fac, blade

def emblem(c, uid="B", doors=0.0, rays=1.0, rise=1.0, crack=1.0, sword=1.0, beam=-7.0, swing=0.0,
           lit=7.0, frame=1.0, bevel=False, crown=1.0, micro=True):
    """Porta déco. Parâmetros de animação: doors (fração fechada das folhas), rays, rise, crack, sword, beam,
    swing (balanço dos pratos, graus), lit (losangos acesos), frame (desenho dos contornos)."""
    out, defs = [], []
    W, H = 1000, 1200
    cx, yc, a0, yb, yh, rs = EC, EYC, EA0, EYB, EYH, ERS
    sx, sy = cx, yh                                         # centro do sol (no horizonte)
    sdy = (1 - ease_out(rise)) * (rs + 30)                  # sol nascendo
    dy_sw = (1 - ease_out(sword)) * -760
    # ---- primeiro plano (espada + balança) e máscaras
    S, Cut, Fac, blade = sword_geom(beam, swing)
    sol = "".join(S)
    cuts = "".join(Cut)
    fg_tr = f'translate(0 {dy_sw:.1f})'
    defs.append(f'<mask id="{uid}-fg" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                f'<rect width="{W}" height="{H}" fill="white"/><g transform="{fg_tr}" fill="black" stroke="black">{cuts}</g></mask>')
    knock = sol.replace('fill="none"', 'fill="black"')
    defs.append(f'<mask id="{uid}-kn" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                f'<rect width="{W}" height="{H}" fill="white"/>'
                f'<g transform="{fg_tr}" fill="black" stroke="black" stroke-width="15" stroke-linejoin="round">{knock}</g></mask>')
    # ---- clipes: vão da porta e céu
    inner = arch_closed(cx, yc, a0 - 12, yb)
    defs.append(f'<clipPath id="{uid}-sky"><path d="{arch_d(cx, yc, a0 - 12, yh - 8)} Z"/></clipPath>')
    defs.append(f'<clipPath id="{uid}-vao"><path d="{inner}"/></clipPath>')
    bg = []          # tudo o que fica atrás da espada
    # ---- raios do sunburst (alternados grosso/fino), do centro do sol
    if rays > 0:
        rr0 = rs + 22
        rmax = 560
        rl = rr0 + (rmax - rr0) * ease_out(rays)
        R = []
        for k in range(-8, 9):                   # raios grossos (cunhas) a cada 10°
            ang = 270 + k * 10
            p0 = polar(sx, sy, rr0, ang)
            p1, p2 = polar(sx, sy, rl, ang - 1.55), polar(sx, sy, rl, ang + 1.55)
            R.append(f'<path d="M{P(*p0)} L{P(*p1)} L{P(*p2)} Z"/>')
        thin = []
        for k in range(-9, 9):                   # raios finos intercalados
            ang = 275 + k * 10
            p0, p1 = polar(sx, sy, rr0 + 14, ang), polar(sx, sy, rl, ang)
            thin.append(f'M{P(*p0)} L{P(*p1)}')
            for dd in (-2.2, 2.2):               # pares de fios finíssimos ladeando
                q0, q1 = polar(sx, sy, rr0 + 60, ang + dd), polar(sx, sy, rl, ang + dd)
                thin.append(f'M{P(*q0)} L{P(*q1)}')
        bg.append(f'<g clip-path="url(#{uid}-sky)"><g fill="{c}">{"".join(R)}</g>'
                  f'<path d="{" ".join(thin)}" stroke="{c}" stroke-width="0.7" fill="none"/></g>')
    # ---- sol nascente rachado
    if rise > 0:
        # rachadura em zigue-zague déco
        base = [(-94, -117), (-46, -97), (-58, -81), (54, -36), (42, -20), (102, 5)]
        pts = [(-104, -122)] + base + [(116, 11)]
        cp = [(sx + px, sy + py) for px, py in pts]
        left = cp + [(sx + 200, sy + 60), (sx - 260, sy + 60), (sx - 260, sy - 220)]
        right = cp + [(sx + 260, sy + 60), (sx + 260, sy - 220), (sx - 120, sy - 220)]
        defs.append(f'<clipPath id="{uid}-sl"><path d="{polyline(left, True)}"/></clipPath>')
        defs.append(f'<clipPath id="{uid}-sr"><path d="{polyline(right, True)}"/></clipPath>')
        defs.append(f'<clipPath id="{uid}-hz"><rect x="0" y="0" width="{W}" height="{yh - 9}"/></clipPath>')
        cr = ease_out(crack)
        off = (2.4 * cr, 3.0 * cr)
        disk = (f'<circle cx="{sx}" cy="{sy}" r="{rs}"/>')
        ring = (f'<circle cx="{sx}" cy="{sy}" r="{rs + 9}" fill="none" stroke="{c}" stroke-width="1.6"/>')
        inl = f'<circle cx="{sx}" cy="{sy}" r="{rs - 13}" fill="none" stroke="black" stroke-width="1.4"/>'
        defs.append(f'<mask id="{uid}-dk" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                    f'<rect width="{W}" height="{H}" fill="white"/>{inl}'
                    f'<path d="{polyline(cp)}" fill="none" stroke="black" stroke-width="{0.01 + 4.2 * cr:.2f}" stroke-linejoin="miter"/></mask>')
        halves = (f'<g clip-path="url(#{uid}-sl)"><g fill="{c}" mask="url(#{uid}-dk)">{disk}</g></g>'
                  f'<g transform="translate({off[0]:.2f} {off[1]:.2f})"><g clip-path="url(#{uid}-sr)"><g fill="{c}" mask="url(#{uid}-dk)">{disk}</g></g></g>')
        bg.append(f'<g clip-path="url(#{uid}-hz)"><g transform="translate(0 {sdy:.1f})">{ring}{halves}</g></g>')
    # ---- horizonte (linha tripla) e reflexo
    hz = (f'<rect x="{cx - a0}" y="{yh - 2}" width="{2 * a0}" height="4"/>'
          f'<rect x="{cx - a0}" y="{yh + 7}" width="{2 * a0}" height="1.1"/>'
          f'<rect x="{cx - a0}" y="{yh + 13}" width="{2 * a0}" height="1.1"/>')
    refl = []
    yy = yh + 30
    for k in range(7):
        hw = 128 * (0.8 ** k); th = 6.0 * (0.84 ** k)
        refl.append(f'<rect x="{sx - hw:.1f}" y="{yy:.1f}" width="{2 * hw:.1f}" height="{th:.2f}"/>')
        yy += th + 10 + k * 1.6
    rf = ease_out(rise)
    bg.append(f'<g fill="{c}">{hz}</g><g fill="{c}" opacity="{rf:.3f}">{"".join(refl)}</g>')
    # piso em perspectiva: fios que convergem para o sol
    fl = []
    for k in range(-6, 7):
        if k == 0: continue
        xb = cx + k * 44
        t0 = 0.36
        x0, y0 = sx + (xb - sx) * t0, sy + (yb - 44 - sy) * t0
        fl.append(f'M{x0:.1f},{y0:.1f} L{xb:.1f},{yb - 44:.1f}')
    defs.append(f'<linearGradient id="{uid}-flg" gradientUnits="userSpaceOnUse" x1="0" y1="{yh + 110}" x2="0" y2="{yb - 60}">'
                f'<stop offset="0" stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>'
                f'<mask id="{uid}-flm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#{uid}-flg)"/></mask>')
    bg.append(f'<g mask="url(#{uid}-flm)"><path d="{" ".join(fl)}" stroke="{c}" stroke-width="0.8" fill="none" opacity="{rf:.3f}"/></g>')
    # degraus da soleira (pequeno zigurate onde repousa a ponta)
    dais = "".join(f'<rect x="{cx - w}" y="{yb - 14 * (3 - k)}" width="{2 * w}" height="14"/>' for k, w in enumerate((70, 112, 154)))
    dais_cut = "".join(f'<rect x="{cx - w + 4}" y="{yb - 14 * (3 - k) + 3}" width="{2 * w - 8}" height="0.9"/>' for k, w in enumerate((70, 112, 154)))
    defs.append(f'<mask id="{uid}-dm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="white"/><g fill="black">{dais_cut}</g></mask>')
    bg.append(f'<g fill="{c}" mask="url(#{uid}-dm)">{dais}</g>')
    # ---- moldura: arquivoltas (linhas triplas) + faixa de microtexto + faixa dos sete losangos
    def strokeline(a, w, extra=""):
        Ld = arch_len(a, yc, yb)
        dash = "" if frame >= 1 else f' stroke-dasharray="{Ld:.1f} {Ld:.1f}" stroke-dashoffset="{Ld * (1 - ease_in_out(frame)):.1f}"'
        return f'<path d="{arch_d(cx, yc, a, yb)}" fill="none" stroke="{c}" stroke-width="{w}"{dash}{extra}/>'
    fr = []
    for o, w in ((0, 3.2), (7, 1.0), (12, 1.0), (38, 1.0), (80, 1.0), (85, 1.0), (92, 3.2)):
        fr.append(strokeline(a0 + o, w))
    # soleira (base da moldura)
    fr.append(f'<rect x="{cx - a0 - 92}" y="{yb}" width="{2 * (a0 + 92)}" height="3.2" fill="{c}"/>')
    fr.append(f'<rect x="{cx - a0 - 92}" y="{yb + 8}" width="{2 * (a0 + 92)}" height="1" fill="{c}"/>')
    fr.append(f'<rect x="{cx - a0 - 92}" y="{yb + 13}" width="{2 * (a0 + 92)}" height="1" fill="{c}"/>')
    # microtexto das leis no arco (interrompido pela pedra-chave)
    if micro:
        rmt = a0 + 21
        t1 = "CONSERVAÇÃO · VÍNCULO · COMPATIBILIDADE ·"
        t2 = "VAZÃO · DISSIPAÇÃO · CAPACIDADE · RETORNO"
        g1 = arc_text(t1, JB, 10.5, cx, yc, rmt, 182, 262.6)
        g2 = arc_text(t2, JB, 10.5, cx, yc, rmt, 277.4, 358)
        fr.append(f'<path d="{g1} {g2}" fill="{c}" opacity="{clamp(frame * 2 - 1):.3f}"/>')
    # caneluras nas ombreiras (faixas verticais)
    flu = []
    for side in (-1, 1):
        for o in (17, 21, 25, 29, 33):
            x = cx + side * (a0 + o)
            flu.append(f'M{x:.1f},{yc + 26} V{yb - 4}')
        for o in (52, 59, 66):
            x = cx + side * (a0 + o)
            flu.append(f'M{x:.1f},{yc + 34} V{yb - 4}')
    fr.append(f'<path d="{" ".join(flu)}" stroke="{c}" stroke-width="0.6" fill="none" opacity="{clamp(frame * 2 - 1):.3f}"/>')
    # sete losangos ao longo do arco (I à esquerda … VII à direita)
    dia = []
    for k in range(7):
        ang = 180 + 30 * k
        x, y = polar(cx, yc, a0 + 59, ang)
        on = clamp(lit - k)
        rot = ang + 90
        dd = diamond(0, 0, 11, 17)
        dia.append(f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f})">'
                   f'<path d="{dd}" fill="none" stroke="{c}" stroke-width="1.1"/>'
                   f'<path d="{diamond(0, 0, 7.5, 12)}" fill="{c}" opacity="{on:.3f}"/></g>')
    fr.append("".join(dia))
    # coroa escalonada: zigurate em volta do arco, raios radiais do centro do arco
    if crown > 0:
        zo = zig_d(cx, ZIG, ZBOT)
        zi = zig_d(cx, offset_steps(ZIG, 9), ZBOT)
        zi2 = zig_d(cx, offset_steps(ZIG, 14), ZBOT)
        defs.append(f'<clipPath id="{uid}-cr"><path d="{zig_d(cx, offset_steps(ZIG, 22), ZBOT)}"/></clipPath>')
        cro = []
        rin = a0 + 106
        for k, r in enumerate(range(rin, 640, 9)):     # arquivoltas concêntricas (proscênio)
            cro.append(f'<path d="{arch_d(cx, yc, r, ZBOT)}" stroke-width="{1.5 if k % 4 == 0 else 0.6}"/>')
        crown_rays = (f'<g clip-path="url(#{uid}-cr)" stroke="{c}" fill="none" opacity="{crown:.3f}">'
                      ''
                      f'{"".join(cro)}</g>')
        fr.append(crown_rays)
        fr.append(f'<path d="{zo}" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="miter" opacity="{crown:.3f}"/>'
                  f'<path d="{zi}" fill="none" stroke="{c}" stroke-width="1" opacity="{crown:.3f}"/>'
                  f'<path d="{zi2}" fill="none" stroke="{c}" stroke-width="1" opacity="{crown:.3f}"/>')
        # plinto escalonado
        fr.append(f'<rect x="{cx - 404 - 16}" y="{ZBOT}" width="{2 * 420}" height="3.2" fill="{c}"/>'
                  f'<rect x="{cx - 420}" y="{ZBOT + 8}" width="840" height="1" fill="{c}"/>'
                  f'<rect x="{cx - 436}" y="{ZBOT + 16}" width="872" height="3.2" fill="{c}"/>')
    # ---- folhas da porta (fechadas = doors 1)
    leaves = ""
    if doors > 0:
        shift = (1 - doors) * (a0 + 10)
        lf = []
        for side in (-1, 1):
            x0 = cx - a0 if side < 0 else cx
            g = [f'<rect x="{x0}" y="0" width="{a0}" height="{yb}" fill="{NOITE}"/>']
            # gravação de chevrons e fios
            ex = cx - a0 / 2 if side < 0 else cx + a0 / 2
            for k in range(12):
                yy0 = 330 + k * 56
                g.append(f'<path d="M{ex - 96:.1f},{yy0 + 30} L{ex:.1f},{yy0} L{ex + 96:.1f},{yy0 + 30}" fill="none" stroke="{c}" stroke-width="{2 if k % 3 == 0 else 0.8}"/>')
            g.append(f'<rect x="{x0 + 14}" y="0" width="{a0 - 28}" height="{yb - 14}" fill="none" stroke="{c}" stroke-width="1.2"/>')
            lf.append(f'<g transform="translate({side * shift:.1f} 0)">{"".join(g)}</g>')
        leaves = f'<g clip-path="url(#{uid}-vao)">{"".join(lf)}</g>'
    # ---- montagem
    out.append(f'<g mask="url(#{uid}-kn)">{"".join(bg)}{leaves}{"".join(fr)}</g>')
    fg = f'<g transform="{fg_tr}" opacity="{clamp(sword * 4):.3f}"><g mask="url(#{uid}-fg)" fill="{c}" stroke="{c}">{sol}</g>'
    if bevel:
        fg += f'<g mask="url(#{uid}-fg)" fill="{NOITE}" opacity=".26">{"".join(Fac)}</g>'
    fg += '</g>'
    out.append(fg)
    return "".join(defs), "".join(out)


# ------------------------------------------------------------------ texto com fio interno (inline)
def inline_mask(uid, d, size, W, H, k=0.028, w=0.009):
    kk, ww = k * size, w * size
    return (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="-50" y="-50" width="{W + 100}" height="{H + 100}">'
            f'<rect x="-50" y="-50" width="{W + 100}" height="{H + 100}" fill="black"/>'
            f'<path d="{d}" fill="white" stroke="black" stroke-width="{2 * kk + ww:.2f}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="white" stroke-width="{max(2 * kk - ww, 0.01):.2f}" stroke-linejoin="round"/></mask>')

def triple_h(x0, x1, y, c, gap=5.0, heavy="mid", th=(0.8, 2.4, 0.8)):
    """Três fios paralelos horizontais (centro em y)."""
    out = []
    for k, t in zip((-1, 0, 1), th):
        yy = y + k * gap
        out.append(f'<rect x="{min(x0, x1):.2f}" y="{yy - t / 2:.2f}" width="{abs(x1 - x0):.2f}" height="{t}" fill="{c}"/>')
    return "".join(out)

def stepped_diamond(cx, cy, r, n=3):
    """Losango escalonado (degraus) de 'meia-diagonal' r com n degraus por quadrante."""
    st = r / (n + 0.5)
    pts = []
    for k in range(n + 1):                         # quadrante superior direito, do topo para a direita
        pts += [(cx + k * st, cy - r + k * st), (cx + (k + 0.5) * st, cy - r + k * st)] if k < n else [(cx + k * st, cy - r + k * st)]
        if k < n: pts.append((cx + (k + 0.5) * st, cy - r + (k + 1) * st))
    q = pts[:-1] + [(cx + r, cy)]
    full = []
    full += [(x, y) for x, y in q]
    full += [(x, 2 * cy - y) for x, y in reversed(q)]
    full += [(2 * cx - x, 2 * cy - y) for x, y in q]
    full += [(2 * cx - x, y) for x, y in reversed(q)]
    return polyline(full, True)

def step_orn(cx, cy, c, s=1.0):
    """Ornamento central: losango escalonado vazado, ladeado por dois losangos."""
    out = [f'<path d="{stepped_diamond(cx, cy, 17 * s, 3)}" fill="none" stroke="{c}" stroke-width="{1.3 * s:.2f}"/>',
           f'<path d="{diamond(cx, cy, 6.5 * s, 6.5 * s)}" fill="{c}"/>']
    for side in (-1, 1):
        out.append(f'<path d="{diamond(cx + side * 32 * s, cy, 6 * s, 5 * s)}" fill="{c}"/>')
    return "".join(out)

def wordmark(c, uid="W", w=1400, inline=True, sub=True, tr_big=0.16):
    cx = w / 2
    out, defs = [], []
    # LEIS PARA
    t1 = "LEIS PARA"
    s1, tr1 = 44, 0.62
    tw1 = text_width(t1, ITA, s1, tr1)
    out.append(f'<path d="{tp(t1, ITA, s1, cx - tw1 / 2, 64, tr1)}" fill="{c}"/>')
    ym = 64 - 0.36 * s1
    for side in (-1, 1):
        xa = cx + side * (tw1 / 2 + 40); xb = cx + side * (tw1 / 2 + 270)
        out.append(triple_h(xa + side * 22, xb, ym, c, 4.6, th=(0.7, 2.0, 0.7)))
        out.append(f'<path d="{diamond(xa + side * 4, ym, 5.5, 8)}" fill="{c}"/>')
    # MATAR DEUSES
    t2, s2 = "MATAR DEUSES", 150
    tw2 = text_width(t2, ITA, s2, tr_big)
    d2 = tp(t2, ITA, s2, cx - tw2 / 2, 250, tr_big)
    if inline:
        defs.append(inline_mask(f"{uid}-in", d2, s2, w, 420))
        out.append(f'<path d="{d2}" fill="{c}" mask="url(#{uid}-in)"/>')
    else:
        out.append(f'<path d="{d2}" fill="{c}"/>')
    # fios triplos com ornamento escalonado
    yl = 298
    out.append(triple_h(cx - tw2 / 2, cx - 50, yl, c, 5))
    out.append(triple_h(cx + 50, cx + tw2 / 2, yl, c, 5))
    out.append(step_orn(cx, yl, c))
    h = 320
    if sub:
        t3 = "VOLUME I"
        t4 = "O DEUS QUE CAIU DO CÉU"
        s3, tr3 = 25, 0.42
        w3 = text_width(t3, JB, s3, tr3)
        w4 = text_width(t4, JL, s3, tr3)
        gap = 64
        tot = w3 + gap + w4
        x3 = cx - tot / 2
        out.append(f'<path d="{tp(t3, JB, s3, x3, 360, tr3)}" fill="{c}"/>')
        out.append(f'<path d="{diamond(x3 + w3 + gap / 2, 360 - 0.36 * s3, 4.5, 6.5)}" fill="{c}"/>')
        out.append(f'<path d="{tp(t4, JL, s3, x3 + w3 + gap, 360, tr3)}" fill="{c}"/>')
        h = 380
    return "".join(defs), "".join(out), h

# ------------------------------------------------------------------ sinais das leis: sete portas
def zig_auto(yc, R, widths, top_pad=10):
    """Degraus de zigurate que contornam um arco de raio R (centro em yc) sem tocá-lo."""
    st = []
    for k, w in enumerate(widths):
        if k + 1 < len(widths):
            wn = widths[k + 1]
            y = yc - math.sqrt(max(R * R - wn * wn, 0))
        else:
            y = yc - R - top_pad
        st.append((w, y))
    return st

def door_frame(cx, c, num, yc=168, ybot=340, a=70, uid="df"):
    o, d = [], []
    for aa, w in ((a, 1.3), (a + 6, 0.7), (a + 14, 2.6)):
        o.append(f'<path d="{arch_d(cx, yc, aa, ybot)}" fill="none" stroke="{c}" stroke-width="{w}"/>')
    # arco escalonado: zigurate em volta, com arquivoltas finas entre eles
    steps = zig_auto(yc, a + 27, [a + 32, a + 20, a + 4, a - 18, a - 40], 9)
    zo = zig_d(cx, steps, ybot)
    o.append(f'<path d="{zo}" fill="none" stroke="{c}" stroke-width="1.6"/>')
    o.append(f'<path d="{zig_d(cx, offset_steps(steps, 4.5), ybot)}" fill="none" stroke="{c}" stroke-width="0.6"/>')
    d.append(f'<clipPath id="{uid}z"><path d="{zig_d(cx, offset_steps(steps, 8), ybot)}"/></clipPath>')
    arcs = "".join(f'<path d="{arch_d(cx, yc, r, ybot)}"/>' for r in (a + 20, a + 26, a + 32, a + 38))
    o.append(f'<g clip-path="url(#{uid}z)" fill="none" stroke="{c}" stroke-width="0.55">{arcs}</g>')
    # travessa da bandeira (transom) e numeral
    o.append(f'<rect x="{cx - a}" y="{yc - 0.6}" width="{2 * a}" height="1.2" fill="{c}"/>')
    o.append(f'<rect x="{cx - a}" y="{yc + 4.4}" width="{2 * a}" height="0.7" fill="{c}"/>')
    o.append(f'<path d="{tp(num, ITA, 34, cx, yc - 16, 0.06, "middle")}" fill="{c}"/>')
    rr = []
    for ang in (192, 204, 216, 324, 336, 348):
        p0, p1 = polar(cx, yc, 40, ang), polar(cx, yc, a - 8, ang)
        rr.append(f'M{P(*p0)} L{P(*p1)}')
    o.append(f'<path d="{" ".join(rr)}" stroke="{c}" stroke-width="0.6" fill="none"/>')
    # pedra-chave
    o.append(f'<path d="{diamond(cx, yc - a - 7, 4.5, 7)}" fill="{c}"/>')
    # soleira tripla
    o.append(triple_h(cx - a - 40, cx + a + 40, ybot + 8, c, 4, th=(2.2, 0.7, 0.7)))
    return "".join(d), "".join(o)

def law_glyph(i, cx, gy, c, uid):
    o, d = [], []
    if i == 0:      # CONSERVAÇÃO: dois triângulos de mesma área completam o losango
        hw, hh = 40, 54
        o.append(f'<path d="M{cx - hw},{gy - 3} L{cx},{gy - hh} L{cx + hw},{gy - 3} Z" fill="{c}"/>')
        d.append(f'<clipPath id="{uid}"><path d="M{cx - hw + 2.5},{gy + 3} L{cx + hw - 2.5},{gy + 3} L{cx},{gy + hh - 3} Z"/></clipPath>')
        hat = "".join(f'M{cx - hw},{gy + 3 + k * 4:.1f} H{cx + hw}' for k in range(1, 14))
        o.append(f'<path d="M{cx - hw},{gy + 3} L{cx + hw},{gy + 3} L{cx},{gy + hh} Z" fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="miter"/>')
        o.append(f'<path d="{hat}" stroke="{c}" stroke-width="0.8" clip-path="url(#{uid})"/>')
        o.append(f'<path d="{diamond(cx, gy, hw + 12, hh + 16)}" fill="none" stroke="{c}" stroke-width="0.6"/>')
    elif i == 1:    # VÍNCULO: dois anéis entrelaçados (por cima / por baixo)
        r, dx = 35, 21
        A = (cx - dx, gy); B = (cx + dx, gy)
        def ring(pnt, extra=""):
            return (f'<circle cx="{pnt[0]}" cy="{pnt[1]}" r="{r + 2.6}" fill="none" stroke="{c}" stroke-width="1.5"{extra}/>'
                    f'<circle cx="{pnt[0]}" cy="{pnt[1]}" r="{r - 2.6}" fill="none" stroke="{c}" stroke-width="1.5"{extra}/>')
        for half, over, under in (("top", A, B), ("bot", B, A)):
            y0 = gy - 80 if half == "top" else gy
            d.append(f'<clipPath id="{uid}{half}"><rect x="{cx - 90}" y="{y0}" width="180" height="80"/></clipPath>')
            d.append(f'<mask id="{uid}{half}m" maskUnits="userSpaceOnUse" x="{cx - 90}" y="{gy - 90}" width="180" height="180">'
                     f'<rect x="{cx - 90}" y="{gy - 90}" width="180" height="180" fill="white"/>'
                     f'<circle cx="{over[0]}" cy="{over[1]}" r="{r}" fill="none" stroke="black" stroke-width="10"/></mask>')
            o.append(f'<g clip-path="url(#{uid}{half})"><g mask="url(#{uid}{half}m)">{ring(under)}</g>{ring(over)}</g>')
        o.append(f'<path d="{diamond(cx, gy, 4, 6)}" fill="{c}"/>')
        o.append(f'<circle cx="{A[0]}" cy="{gy}" r="2.2" fill="{c}"/><circle cx="{B[0]}" cy="{gy}" r="2.2" fill="{c}"/>')
    elif i == 2:    # COMPATIBILIDADE: dois perfis escalonados que se encaixam
        prof = [(208, -14), (228, -2), (248, 14), (268, -2), (288, -14), (308, None)]
        y0, y1 = gy - 52, gy + 52
        ys = [y0 + k * 20.8 for k in range(6)]
        xs = [-14, -2, 14, -2, -14]
        gap = 6
        L = [(cx - 58, y0)]
        for k in range(5):
            L += [(cx + xs[k], ys[k]), (cx + xs[k], ys[k + 1])]
        L += [(cx - 58, y1)]
        o.append(f'<path d="{polyline(L, True)}" fill="{c}"/>')
        Rr = [(cx + 58, y0)]
        for k in range(5):
            Rr += [(cx + xs[k] + gap, ys[k]), (cx + xs[k] + gap, ys[k + 1])]
        Rr += [(cx + 58, y1)]
        o.append(f'<path d="{polyline(Rr, True)}" fill="none" stroke="{c}" stroke-width="1.4"/>')
        d.append(f'<clipPath id="{uid}"><path d="{polyline(Rr, True)}"/></clipPath>')
        hat = "".join(f'M{cx - 20 + k * 4.2:.1f},{y0} V{y1}' for k in range(20))
        o.append(f'<path d="{hat}" stroke="{c}" stroke-width="0.7" clip-path="url(#{uid})"/>')
        o.append(f'<path d="M{cx - 58},{y0 - 10} H{cx + 58} M{cx - 58},{y1 + 10} H{cx + 58}" stroke="{c}" stroke-width="0.6"/>')
    elif i == 3:    # VAZÃO: canal que se estreita, linhas de fluxo adensando-se
        yt, yn, yb2 = gy - 58, gy + 26, gy + 70
        def w(y):
            if y <= yt + 10: return 56
            if y >= yn: return 13
            f = (y - yt - 10) / (yn - yt - 10)
            f = ease_in_out(f)
            return 56 + (13 - 56) * f
        ys = [yt + k * 2 for k in range(int((yb2 - yt) / 2) + 1)]
        for side in (-1, 1):
            pts = [(cx + side * (w(y) + 3.5), y) for y in ys]
            o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="4"/>')
        n = 9
        for k in range(n):
            f = (k / (n - 1)) - 0.5
            pts = [(cx + f * 2 * (w(y) - 3.5), y) for y in ys]
            o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="{0.9 if k % 4 else 1.3}"/>')
    elif i == 4:    # DISSIPAÇÃO: leque que se abre, fios cada vez mais espaçados e rarefeitos
        ox, oy = cx, gy + 66
        o.append(f'<path d="{diamond(ox, oy, 6, 6)}" fill="{c}"/>')
        for k in range(0, 7):
            th = 3.6 * k ** 1.55
            for sgn in ((1,) if k == 0 else (-1, 1)):
                ang = 270 + sgn * th
                Ln = 128 - k * 9
                wd = max(2.4 - k * 0.32, 0.5)
                if k < 3:
                    p0, p1 = polar(ox, oy, 12, ang), polar(ox, oy, Ln, ang)
                    o.append(f'<path d="M{P(*p0)} L{P(*p1)}" stroke="{c}" stroke-width="{wd:.2f}"/>')
                else:
                    seglen = 18 - k * 2; gapl = 4 + (k - 2) * 4
                    r0 = 12
                    while r0 < Ln:
                        p0, p1 = polar(ox, oy, r0, ang), polar(ox, oy, min(r0 + seglen, Ln), ang)
                        o.append(f'<path d="M{P(*p0)} L{P(*p1)}" stroke="{c}" stroke-width="{wd:.2f}"/>')
                        r0 += seglen + gapl
    elif i == 5:    # CAPACIDADE: vaso escalonado com nível e graduação
        cx0 = cx
        cx = cx - 8
        # vaso escalonado (pé, bojo em degraus, ombro, gargalo, lábio)
        prof = [(30, gy - 60), (30, gy - 54), (19, gy - 54), (19, gy - 40), (31, gy - 40), (31, gy - 32), (41, gy - 32),
                (41, gy + 8), (34, gy + 8), (34, gy + 26), (24, gy + 26), (24, gy + 44), (16, gy + 44), (16, gy + 52),
                (28, gy + 52), (28, gy + 60)]
        left = [(cx - w_, y) for w_, y in prof]
        right = [(cx + w_, y) for w_, y in reversed(prof)]
        vessel = polyline(left + right, True)
        lvl = gy - 12
        d.append(f'<clipPath id="{uid}"><path d="{vessel}"/></clipPath>')
        hat = "".join(f'M{cx - 60},{lvl + 4 + k * 3.4:.1f} H{cx + 60}' for k in range(18))
        o.append(f'<g clip-path="url(#{uid})"><path d="{hat}" stroke="{c}" stroke-width="0.8"/>'
                 f'<rect x="{cx - 60}" y="{lvl - 1.3}" width="120" height="2.6" fill="{c}"/>'
                 f'<rect x="{cx - 60}" y="{gy + 44}" width="120" height="20" fill="{c}"/></g>')
        o.append(f'<path d="{vessel}" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="miter"/>')
        # graduação ao lado
        o.append(f'<path d="M{cx + 56},{gy - 56} V{gy + 56}" stroke="{c}" stroke-width="0.8"/>')
        for k in range(15):
            yy = gy - 56 + k * 8
            ln = 8 if k % 2 == 0 else 4.5
            o.append(f'<path d="M{cx + 56},{yy:.1f} h{ln}" stroke="{c}" stroke-width="0.8"/>')
        o.append(f'<path d="M{cx + 53},{lvl} l-7,-4.5 v9 Z" fill="{c}"/>')
        cx = cx0
    elif i == 6:    # RETORNO: espiral quadrada que volta ao centro
        hs, st = 54, 12
        x, y = cx - hs, gy + hs
        pts = [(x, y)]
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        L = 2 * hs; k = 0
        lens = [2 * hs, 2 * hs, 2 * hs]
        cur = 2 * hs
        seq = [2 * hs, 2 * hs, 2 * hs - st]
        while True:
            Lk = seq[-1] - (st if len(seq) % 2 == 0 else 0)
            seq.append(Lk)
            if Lk <= st: break
        for j, Lk in enumerate(seq):
            dx, dy = dirs[j % 4]
            x += dx * Lk; y += dy * Lk
            pts.append((x, y))
        o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="2.6" stroke-linejoin="miter" stroke-linecap="square"/>')
        o.append(f'<path d="{diamond(pts[-1][0], pts[-1][1], 5, 5)}" fill="{c}"/>')
    return "".join(d), "".join(o)

def law_sign(i, cx, c, uid):
    dd, g = law_glyph(i, cx, 262, c, f"{uid}g{i}")
    d2, fr = door_frame(cx, c, ROM[i], uid=f"{uid}f{i}")
    dd += d2
    nm = LEIS[i]
    size = 15 if len(nm) < 12 else 13.5
    trk = 0.26 if len(nm) < 12 else 0.16
    name = f'<path d="{tp(nm, JB, size, cx, 404, trk, "middle")}" fill="{c}"/>'
    return dd, fr + g + name

# ------------------------------------------------------------------ princípios: seis medalhões octogonais
def octagon(cx, cy, R):
    return polyline([polar(cx, cy, R, 22.5 + 45 * k) for k in range(8)], True)

def principle_medal(name, cx, cy, c, uid, R=112):
    o, d = [], []
    d.append(f'<clipPath id="{uid}"><path d="{octagon(cx, cy, R - 15)}"/></clipPath>')
    T = []
    x0, x1, y0, y1 = cx - R, cx + R, cy - R, cy + R
    if name == "PULSO":          # chevrons empilhados: o compasso de um batimento
        for k in range(-11, 12):
            yy = cy + k * 11
            w = 3.0 if k % 3 == 0 else 0.8
            T.append(f'<path d="M{x0},{yy + 70:.1f} L{cx},{yy:.1f} L{x1},{yy + 70:.1f}" stroke-width="{w}"/>')
    elif name == "BRASA":        # chama déco: ogivas aninhadas sobre a brasa
        base = cy + 62
        for k in range(8):
            w = 78 - k * 9.5; top = cy - 84 + k * 13
            T.append(f'<path d="M{cx - w:.1f},{base} C{cx - w:.1f},{base - 70 + k * 4:.1f} {cx - 6:.1f},{top + 34:.1f} {cx},{top:.1f} '
                     f'C{cx + 6:.1f},{top + 34:.1f} {cx + w:.1f},{base - 70 + k * 4:.1f} {cx + w:.1f},{base}" stroke-width="{2.6 if k % 3 == 0 else 0.8}"/>')
        T.append(f'<path d="M{cx - 30},{base} A30,30 0 0 1 {cx + 30},{base} Z" fill="{c}" stroke="none"/>')
        T.append(f'<path d="M{x0},{base + 0.5} H{x1} M{x0},{base + 8} H{x1} M{x0},{base + 14} H{x1}" stroke-width="0.8"/>')
    elif name == "TRAMA":        # trama de cesto: células alternadas, fios triplos (rede a 45°)
        cs = 20
        cells = []
        ca, sa = math.cos(math.radians(45)), math.sin(math.radians(45))
        def RT(x, y): return cx + x * ca - y * sa, cy + x * sa + y * ca
        for i in range(-7, 8):
            for j in range(-7, 8):
                X, Y = i * cs, j * cs
                for q in (-6, 0, 6):
                    if (i + j) % 2 == 0:
                        a_, b_ = RT(X - cs / 2 + 2, Y + q), RT(X + cs / 2 - 2, Y + q)
                    else:
                        a_, b_ = RT(X + q, Y - cs / 2 + 2), RT(X + q, Y + cs / 2 - 2)
                    cells.append(f'M{P(*a_)} L{P(*b_)}')
        T.append(f'<path d="{" ".join(cells)}" stroke-width="1.1"/>')
    elif name == "CLARÃO":       # explosão de luz: cunhas e fios alternados
        for k in range(16):
            ang = k * 22.5 - 90
            p0 = polar(cx, cy, 22, ang)
            p1, p2 = polar(cx, cy, R, ang - 3.2), polar(cx, cy, R, ang + 3.2)
            T.append(f'<path d="M{P(*p0)} L{P(*p1)} L{P(*p2)} Z" fill="{c}" stroke="none"/>')
            for dd_ in (-7.5, 0.0, 7.5):
                q0, q1 = polar(cx, cy, 30 if dd_ == 0 else 40, ang + 11.25 + dd_), polar(cx, cy, R, ang + 11.25 + dd_)
                T.append(f'<path d="M{P(*q0)} L{P(*q1)}" stroke-width="{0.9 if dd_ == 0 else 0.55}"/>')
        T.append(f'<circle cx="{cx}" cy="{cy}" r="13" fill="{c}" stroke="none"/><circle cx="{cx}" cy="{cy}" r="18" stroke-width="1"/>')
    elif name == "ECO":          # ecos: anéis que se espaçam e se apagam, com anéis perlados entre eles
        r, gap, w = 7, 7, 3.2
        while r < R * 1.1:
            T.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" stroke-width="{w:.2f}"/>')
            rm = r + gap / 2
            if gap > 9:
                n = int(2 * math.pi * rm / 7)
                dots = "".join(f'<circle cx="{polar(cx, cy, rm, q * 360 / n)[0]:.2f}" cy="{polar(cx, cy, rm, q * 360 / n)[1]:.2f}" r="{max(w * 0.55, 0.6):.2f}"/>' for q in range(n))
                T.append(f'<g fill="{c}" stroke="none">{dots}</g>')
            r += gap; gap *= 1.17; w = max(w * 0.8, 0.45)
        T.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{c}" stroke="none"/>')
    elif name == "CARGA":        # carga: ziguezagues paralelos, um fio de força a cada três
        for k in range(-10, 11):
            pts = []; xx = x0; up = True
            yy = cy + k * 10.5
            while xx <= x1 + 12:
                pts.append((xx, yy + (-5 if up else 5))); xx += 12; up = not up
            T.append(f'<path d="{polyline(pts)}" stroke-width="{2.6 if k % 3 == 0 else 0.75}" stroke-linejoin="miter"/>')
    o.append(f'<g clip-path="url(#{uid})" fill="none" stroke="{c}">{"".join(T)}</g>')
    o.append(f'<path d="{octagon(cx, cy, R)}" fill="none" stroke="{c}" stroke-width="2.6"/>')
    o.append(f'<path d="{octagon(cx, cy, R - 7)}" fill="none" stroke="{c}" stroke-width="0.7"/>')
    o.append(f'<path d="{octagon(cx, cy, R - 12)}" fill="none" stroke="{c}" stroke-width="0.7"/>')
    for ang in (-90, 90):
        x, y = polar(cx, cy, R * math.cos(math.radians(22.5)) + 12, ang)
        o.append(f'<path d="{diamond(x, y, 4.5, 7)}" fill="{c}"/>')
    o.append(f'<path d="{tp(name, JB, 17, cx, cy + R + 64, 0.34, "middle")}" fill="{c}"/>')
    return "".join(d), "".join(o)

def build_principles():
    W, H = 2000, 400
    defs, body = [], []
    for k, nm in enumerate(PRINC):
        cx = 205 + k * 318
        defs.append(foil_defs(f"pf{k}", (cx - 140, 60, cx + 140, 400)))
        dd, b = principle_medal(nm, cx, 160, f"url(#pf{k})", f"P{k}")
        defs.append(dd); body.append(b)
    s = svg(W, H, "".join(body), "".join(defs), bg=NOITE)
    open(f"{OUT}/sinais_principios_limiar.svg", "w").write(s)
    to_png(s, f"{OUT}/sinais_principios_limiar.png", 4000)

# ------------------------------------------------------------------ guarda: escamas de leque (sóis nascentes)
def fan_tile(x, y, r, c, bg):
    """Leque déco aberto para cima, centro da base em (x, y)."""
    o = [f'<path d="M{x - r},{y} A{r},{r} 0 0 1 {x + r},{y} Z" fill="{bg}" stroke="{c}" stroke-width="2"/>']
    o.append(f'<path d="M{x - r + 7},{y} A{r - 7},{r - 7} 0 0 1 {x + r - 7},{y}" fill="none" stroke="{c}" stroke-width="0.7"/>')
    o.append(f'<path d="M{x - r + 12},{y} A{r - 12},{r - 12} 0 0 1 {x + r - 12},{y}" fill="none" stroke="{c}" stroke-width="0.7"/>')
    rays = []
    for k in range(1, 18):
        ang = 180 + k * 10
        if k % 2:
            p0 = polar(x, y, r * 0.30, ang)
            p1, p2 = polar(x, y, r - 18, ang - 2.1), polar(x, y, r - 18, ang + 2.1)
            rays.append(f'<path d="M{P(*p0)} L{P(*p1)} L{P(*p2)} Z" fill="{c}"/>')
        else:
            p0, p1 = polar(x, y, r * 0.36, ang), polar(x, y, r - 18, ang)
            rays.append(f'<path d="M{P(*p0)} L{P(*p1)}" stroke="{c}" stroke-width="0.6"/>')
    o.append("".join(rays))
    o.append(f'<path d="M{x - r * .22:.1f},{y} A{r * .22:.1f},{r * .22:.1f} 0 0 1 {x + r * .22:.1f},{y} Z" fill="{c}"/>')
    o.append(f'<path d="M{x - r * .27:.1f},{y} A{r * .27:.1f},{r * .27:.1f} 0 0 1 {x + r * .27:.1f},{y}" fill="none" stroke="{c}" stroke-width="0.7"/>')
    return "".join(o)

def endpaper(W=3200, H=2000, c="url(#gfoil)", bg=NOITE):
    r = 120
    out = []
    rows = int(H / r) + 3
    for k in range(rows):
        y = -r + k * r
        off = (k % 2) * r
        for j in range(-1, int(W / (2 * r)) + 2):
            x = j * 2 * r + off
            out.append(fan_tile(x, y, r, c, bg))
    # losangos nos vãos entre as escamas
    for k in range(rows):
        y = -r + k * r
        off = (k % 2) * r
        for j in range(-1, int(W / (2 * r)) + 2):
            x = j * 2 * r + off + r
            out.append(f'<path d="{diamond(x, y + r * 0.0 - 0.0, 0, 0)}"/>')
    defs = foil_defs("gfoil", (0, 0, W, H))
    return svg(W, H, "".join(out), defs, bg=bg)

def build_signs():
    W, H = 2000, 470
    defs, body = [], []
    for i in range(7):
        cx = 160 + i * 280
        defs.append(foil_defs(f"foil{i}", (cx - 130, 40, cx + 130, 420)))
        dd, b = law_sign(i, cx, f"url(#foil{i})", "L")
        defs.append(dd); body.append(f'<g transform="translate(0 -6)">{b}</g>')
    s = svg(W, H, "".join(body), "".join(defs), bg=NOITE)
    open(f"{OUT}/sinais_leis_limiar.svg", "w").write(s)
    to_png(s, f"{OUT}/sinais_leis_limiar.png", 4000)

def build_logo():
    d, b, h = wordmark("url(#foil)", "W1")
    s = svg(1400, h + 40, f'<g transform="translate(0 20)">{b}</g>', foil_defs("foil", (0, 0, 1400, 420)) + d, bg=NOITE)
    to_png(s, f"{OUT}/logotipo_limiar.png", 2800)
    d, b, h = wordmark(NOITE, "W2")
    open(f"{OUT}/logotipo_limiar.svg", "w").write(svg(1400, h + 40, f'<g transform="translate(0 20)">{b}</g>', d))

def build_emblems():
    ed, eb = emblem(NOITE, uid="E1")
    s = svg(1000, 1200, eb, ed)
    open(f"{OUT}/emblema_limiar.svg", "w").write(s)
    to_png(s, f"{OUT}/emblema_limiar.png", 2000)
    ed, eb = emblem("url(#foil)", uid="E2", bevel=True)
    s = svg(1000, 1200, eb, foil_defs("foil") + ed, bg=NOITE)
    to_png(s, f"{OUT}/emblema_limiar_champanhe_sobre_meia_noite.png", 2000)


if __name__ == "__main__":
    only = sys.argv[1:] or ["all"]
    t0 = time.time()
    if "emblema" in only or "all" in only:
        build_emblems()
    if "logo" in only or "all" in only:
        build_logo()
    if "guarda" in only or "all" in only:
        to_png(endpaper(), f"{OUT}/guarda_limiar.png", 3200)
    if "sinais" in only or "all" in only:
        build_signs()
        build_principles()
    print("B ok", round(time.time() - t0, 1), "s")
