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
           lit=7.0, frame=1.0, bevel=False, crown=1.0, micro=True, glow=0.0, flash=0.0):
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
    if glow > 0:
        defs.append(f'<radialGradient id="{uid}-gl" gradientUnits="userSpaceOnUse" cx="{sx}" cy="{sy}" r="{360 + 140 * flash:.1f}">'
                    f'<stop offset="0" stop-color="{CH1}" stop-opacity="{0.55 * glow + 0.4 * flash:.3f}"/>'
                    f'<stop offset="0.45" stop-color="{CH2}" stop-opacity="{0.16 * glow + 0.15 * flash:.3f}"/>'
                    f'<stop offset="1" stop-color="{CH3}" stop-opacity="0"/></radialGradient>')
        bg.append(f'<g clip-path="url(#{uid}-sky)"><rect x="0" y="0" width="{W}" height="{H}" fill="url(#{uid}-gl)"/></g>')
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

# ------------------------------------------------------------------ guarda: arlequim de losangos com leques
def endpaper(W=3200, H=2000, c="url(#gfoil)", bg=NOITE, A=160, B=212):
    out, clipA = [], []
    fans, plains = [], []
    nx, ny = int(W / (2 * A)) + 2, int(H / (2 * B)) + 2
    for j in range(-1, ny + 1):
        for i in range(-1, nx + 1):
            fans.append((i * 2 * A, j * 2 * B))
            plains.append((i * 2 * A + A, j * 2 * B + B))
    ins = 9
    def loz(x, y, a, b): return f"M{x:.1f},{y - b:.1f} L{x + a:.1f},{y:.1f} L{x:.1f},{y + b:.1f} L{x - a:.1f},{y:.1f} Z"
    k_in = ins * math.hypot(A, B) / A                 # recuo vertical equivalente a 'ins' perpendicular
    for x, y in fans:
        clipA.append(f'<path d="{loz(x, y, A - ins * math.hypot(A, B) / B, B - k_in)}"/>')
    # leques: pivô no vértice inferior de cada losango A
    F = []
    half = math.degrees(math.atan2(A, B))
    for x, y in fans:
        vx, vy = x, y + B
        for k in range(-7, 8):
            ang = 270 + k * (half * 2 / 14) * 0.98
            if k % 2 == 0:
                p0 = polar(vx, vy, 58, ang)
                p1, p2 = polar(vx, vy, 2 * B, ang - 1.3), polar(vx, vy, 2 * B, ang + 1.3)
                F.append(f'<path d="M{P(*p0)} L{P(*p1)} L{P(*p2)} Z" fill="{c}"/>')
            else:
                p0, p1 = polar(vx, vy, 66, ang), polar(vx, vy, 2 * B, ang)
                F.append(f'<path d="M{P(*p0)} L{P(*p1)}" stroke="{c}" stroke-width="0.7"/>')
        for rr, w in ((40, 1.0), (47, 0.6)):
            F.append(f'<circle cx="{vx}" cy="{vy}" r="{rr:.1f}" fill="none" stroke="{c}" stroke-width="{w}"/>')
        F.append(f'<circle cx="{vx}" cy="{vy}" r="30" fill="{c}"/>')
    out.append(f'<g clip-path="url(#gclipA)">{"".join(F)}</g>')
    # losangos B: losangos concêntricos e losango escalonado ao centro
    Bp = []
    for x, y in plains:
        for f_, w in ((0.80, 0.7), (0.74, 0.7), (0.40, 1.2)):
            Bp.append(f'<path d="{loz(x, y, (A - ins) * f_, (B - ins) * f_)}" fill="none" stroke="{c}" stroke-width="{w}"/>')
        Bp.append(f'<path d="{stepped_diamond(x, y, 34, 3)}" fill="none" stroke="{c}" stroke-width="1.1"/>')
        Bp.append(f'<path d="{diamond(x, y, 11, 14)}" fill="{VERDETE}"/>')
        for sgn in (-1, 1):
            Bp.append(f'<path d="{diamond(x, y + sgn * (B - ins) * 0.6, 4, 7)}" fill="{c}"/>')
    out.append("".join(Bp))
    # treliça: fios duplos ao longo das duas diagonais
    L = []
    span = W + H
    for t in range(-int(span / A) - 2, int(span / A) + 3):
        x0 = t * 2 * A
        for dx in (-3.2, 3.2):
            # direção (A, B) e (A, -B) passando pelos vértices
            L.append(f'M{x0 + dx - 10 * A:.1f},{-10 * B + B:.1f} L{x0 + dx + 10 * A:.1f},{10 * B + B:.1f}')
            L.append(f'M{x0 + dx - 10 * A:.1f},{10 * B + B:.1f} L{x0 + dx + 10 * A:.1f},{-10 * B + B:.1f}')
    out.append(f'<path d="{" ".join(L)}" stroke="{c}" stroke-width="0.9" fill="none"/>')
    # cravos nos cruzamentos
    for x, y in fans:
        for vx, vy in ((x - A, y), (x + A, y)):
            pass
    for j in range(-1, ny + 2):
        for i in range(-1, nx + 2):
            for vx, vy in ((i * 2 * A + A, j * 2 * B), (i * 2 * A, j * 2 * B + B)):
                out.append(f'<path d="{diamond(vx, vy, 9, 9)}" fill="{bg}" stroke="{c}" stroke-width="1"/>'
                           f'<path d="{diamond(vx, vy, 4, 4)}" fill="{c}"/>')
    defs = foil_defs("gfoil", (0, 0, W, H)) + f'<clipPath id="gclipA">{"".join(clipA)}</clipPath>'
    return svg(W, H, "".join(out), defs, bg=bg)

# ------------------------------------------------------------------ moldura déco com cantos escalonados
def notched_rect(x0, y0, x1, y1, n=36, d=0):
    """Retângulo com cantos em degrau duplo (recuo d mantém os degraus paralelos)."""
    x0, y0, x1, y1 = x0 + d, y0 + d, x1 - d, y1 - d
    h = n / 2
    pts = [(x0, y0 + n), (x0 + h, y0 + n), (x0 + h, y0 + h), (x0 + n, y0 + h), (x0 + n, y0),
           (x1 - n, y0), (x1 - n, y0 + h), (x1 - h, y0 + h), (x1 - h, y0 + n), (x1, y0 + n),
           (x1, y1 - n), (x1 - h, y1 - n), (x1 - h, y1 - h), (x1 - n, y1 - h), (x1 - n, y1),
           (x0 + n, y1), (x0 + n, y1 - h), (x0 + h, y1 - h), (x0 + h, y1 - n), (x0, y1 - n)]
    return polyline(pts, True)

def corner_fan(x, y, sx, sy, c, r=120):
    """Leque de quarto de círculo num canto; (sx, sy) = direção para dentro."""
    o = []
    base = math.degrees(math.atan2(sy, sx))           # bissetriz
    for k in range(0, 10):
        ang = base - 45 + k * 10
        if k % 2 == 0:
            p0 = polar(x, y, 26, ang)
            p1, p2 = polar(x, y, r, ang - 1.6), polar(x, y, r, ang + 1.6)
            o.append(f'<path d="M{P(*p0)} L{P(*p1)} L{P(*p2)} Z" fill="{c}"/>')
        else:
            p0, p1 = polar(x, y, 32, ang), polar(x, y, r - 4, ang)
            o.append(f'<path d="M{P(*p0)} L{P(*p1)}" stroke="{c}" stroke-width="0.8"/>')
    a0, a1 = polar(x, y, r + 10, base - 45), polar(x, y, r + 10, base + 45)
    o.append(f'<path d="M{P(*a0)} A{r + 10},{r + 10} 0 0 1 {P(*a1)}" fill="none" stroke="{c}" stroke-width="1"/>')
    a0, a1 = polar(x, y, r + 16, base - 45), polar(x, y, r + 16, base + 45)
    o.append(f'<path d="M{P(*a0)} A{r + 16},{r + 16} 0 0 1 {P(*a1)}" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(f'<path d="M{x},{y} m{-18 * (1 if sx > 0 else -1) * 0},0" />')
    a0, a1 = polar(x, y, 18, base - 45), polar(x, y, 18, base + 45)
    o.append(f'<path d="M{x},{y} L{P(*a0)} A18,18 0 0 1 {P(*a1)} Z" fill="{c}"/>')
    return "".join(o)

def cloth_defs():
    return ('<filter id="cloth" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.95 0.06" numOctaves="2" seed="11" result="w"/>'
            '<feTurbulence type="fractalNoise" baseFrequency="0.05 0.95" numOctaves="2" seed="4" result="v"/>'
            '<feBlend in="w" in2="v" mode="multiply" result="m"/>'
            '<feColorMatrix in="m" type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.62  0 0 0 0 0.80  1.25 0 0 0 -0.52" result="lt"/>'
            '<feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="2" result="slub"/>'
            '<feColorMatrix in="slub" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0.02  0 0 0 0.55 -0.2" result="dk"/>'
            '<feMerge><feMergeNode in="lt"/><feMergeNode in="dk"/></feMerge></filter>'
            '<pattern id="weave" patternUnits="userSpaceOnUse" width="4" height="4">'
            '<rect width="4" height="2" fill="#ffffff" opacity=".022"/><rect width="2" height="4" fill="#000000" opacity=".05"/></pattern>'
            '<filter id="stamp" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="9" result="n"/>'
            '<feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.55 0.55" result="nm"/>'
            '<feComposite in="nm" in2="SourceAlpha" operator="in" result="speck"/>'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="1.1" result="b"/><feOffset in="b" dx="0.6" dy="1.4" result="o"/>'
            '<feFlood flood-color="#03060C" flood-opacity=".85"/><feComposite in2="o" operator="in" result="sh"/>'
            '<feMerge><feMergeNode in="sh"/><feMergeNode in="SourceGraphic"/><feMergeNode in="speck"/></feMerge></filter>')

def cover_cloth():
    W, H = 1600, 2300
    defs = [cloth_defs(), foil_defs("cf", (0, 0, W, H)), foil_defs("foil", (0, 0, 1000, 1200)),
            foil_defs("wf", (0, 0, 1400, 420))]
    ink = "url(#cf)"
    ed, eb = emblem("url(#foil)", uid="Cv", bevel=True)
    wd, wb, wh = wordmark("url(#wf)", "Cw")
    defs += [ed, wd]
    F = []
    # moldura tripla com cantos escalonados
    m = 74
    F.append(f'<path d="{notched_rect(m, m, W - m, H - m, 44, 0)}" fill="none" stroke="{ink}" stroke-width="3.2"/>')
    F.append(f'<path d="{notched_rect(m, m, W - m, H - m, 44, 9)}" fill="none" stroke="{ink}" stroke-width="0.9"/>')
    F.append(f'<path d="{notched_rect(m, m, W - m, H - m, 44, 15)}" fill="none" stroke="{ink}" stroke-width="0.9"/>')
    # leques nos cantos internos
    ci = m + 15 + 44
    for (x, y, sx, sy) in ((ci, ci, 1, 1), (W - ci, ci, -1, 1), (ci, H - ci, 1, -1), (W - ci, H - ci, -1, -1)):
        F.append(corner_fan(x, y, sx, sy, ink, 92))
    # emblema
    es = 0.8
    ex, ey = (W - 1000 * es) / 2, 236
    F.append(f'<g transform="translate({ex:.1f} {ey}) scale({es})">{eb}</g>')
    # horizonte do emblema prolongado até a moldura (linha tripla)
    hy = ey + EYH * es
    zx = (EC - 404) * es + ex
    for xa, xb in ((m + 15, zx - 14), (W - zx + 14, W - m - 15)):
        F.append(triple_h(xa, xb, hy + 0.0, ink, 5.5, th=(0.8, 2.6, 0.8)))
    # título
    ws = 0.92
    wx = (W - 1400 * ws) / 2
    F.append(f'<g transform="translate({wx:.1f} 1262) scale({ws})">{wb}</g>')
    # autor
    F.append(f'<path d="{tp("WERIK MARTINS", ITA, 50, W / 2, 1782, 0.42, "middle")}" fill="{ink}"/>')
    aw = text_width("WERIK MARTINS", ITA, 50, 0.42)
    for side in (-1, 1):
        F.append(f'<path d="{diamond(W / 2 + side * (aw / 2 + 40), 1782 - 18, 5, 7.5)}" fill="{ink}"/>')
    # placa da edição numerada
    py = 1980
    pw, ph = 560, 74
    F.append(f'<path d="{notched_rect(W / 2 - pw / 2, py - ph / 2, W / 2 + pw / 2, py + ph / 2, 14, 0)}" fill="none" stroke="{ink}" stroke-width="1.6"/>')
    F.append(f'<path d="{notched_rect(W / 2 - pw / 2, py - ph / 2, W / 2 + pw / 2, py + ph / 2, 14, 6)}" fill="none" stroke="{ink}" stroke-width="0.7"/>')
    F.append(f'<path d="{tp("EDIÇÃO NUMERADA  Nº 0001 / 1187", JB, 19, W / 2, py + 7, 0.36, "middle")}" fill="{ink}"/>')
    for side in (-1, 1):
        F.append(triple_h(W / 2 + side * (pw / 2 + 16), W / 2 + side * (pw / 2 + 170), py, ink, 4.5, th=(0.7, 1.8, 0.7)))
    body = (f'<rect width="{W}" height="{H}" fill="url(#weave)"/>'
            f'<rect width="{W}" height="{H}" filter="url(#cloth)"/>'
            f'<g filter="url(#stamp)">{"".join(F)}</g>')
    return svg(W, H, body, "".join(defs), bg=NOITE)

# ------------------------------------------------------------------ sobrecapa: janela em arco escalonado
def tritone_filter(fid, lo=(0.035, 0.058, 0.110), mid=(0.235, 0.300, 0.400), hi=(0.965, 0.905, 0.760), gamma=1.0, contrast=1.0):
    tv = lambda k: f"{lo[k]:.3f} {mid[k]:.3f} {hi[k]:.3f}"
    return (f'<filter id="{fid}" color-interpolation-filters="sRGB" x="0" y="0" width="100%" height="100%">'
            '<feColorMatrix type="matrix" values="0.30 0.59 0.11 0 0  0.30 0.59 0.11 0 0  0.30 0.59 0.11 0 0  0 0 0 1 0"/>'
            f'<feComponentTransfer><feFuncR type="gamma" amplitude="{contrast}" exponent="{gamma}" offset="0"/>'
            f'<feFuncG type="gamma" amplitude="{contrast}" exponent="{gamma}" offset="0"/><feFuncB type="gamma" amplitude="{contrast}" exponent="{gamma}" offset="0"/></feComponentTransfer>'
            f'<feComponentTransfer><feFuncR type="table" tableValues="{tv(0)}"/><feFuncG type="table" tableValues="{tv(1)}"/>'
            f'<feFuncB type="table" tableValues="{tv(2)}"/></feComponentTransfer></filter>')

def portal(cx, yc, a0, yb, c, uid, zig_widths=None, lit=7, micro_text=None, crown=True, sill_ext=0):
    """Moldura de portal déco genérica (linhas triplas, faixa dos 7 losangos, coroa em zigurate com arquivoltas)."""
    o, d = [], []
    for off, w in ((0, 3.0), (8, 0.9), (13, 0.9), (36, 0.9), (74, 0.9), (79, 0.9), (86, 3.0)):
        o.append(f'<path d="{arch_d(cx, yc, a0 + off, yb)}" fill="none" stroke="{c}" stroke-width="{w}"/>')
    if micro_text:
        t1, t2 = micro_text
        rmt = a0 + 20
        o.append(f'<path d="{arc_text(t1, JB, 11, cx, yc, rmt, 181.5, 266.5)} {arc_text(t2, JB, 11, cx, yc, rmt, 273.5, 358.5)}" fill="{c}"/>')
        o.append(f'<path d="{diamond(cx, yc - rmt - 4, 4, 6)}" fill="{c}"/>')
    for k in range(7):
        ang = 180 + 30 * k
        x, y = polar(cx, yc, a0 + 55, ang)
        o.append(f'<g transform="translate({x:.2f} {y:.2f}) rotate({ang + 90:.2f})">'
                 f'<path d="{diamond(0, 0, 10, 15)}" fill="none" stroke="{c}" stroke-width="1"/>'
                 f'<path d="{diamond(0, 0, 6.5, 10.5)}" fill="{c}" opacity="{clamp(lit - k):.3f}"/></g>')
    flu = []
    for side in (-1, 1):
        for off in (17, 21, 25, 29):
            flu.append(f'M{cx + side * (a0 + off):.1f},{yc + 24} V{yb - 4}')
        for off in (49, 55, 61):
            flu.append(f'M{cx + side * (a0 + off):.1f},{yc + 30} V{yb - 4}')
    o.append(f'<path d="{" ".join(flu)}" stroke="{c}" stroke-width="0.6" fill="none"/>')
    if crown:
        Ra = a0 + 86
        widths = zig_widths or [Ra + 42, Ra + 2, Ra - 58, Ra - 140, Ra - 236]
        steps = zig_auto(yc, Ra + 30, widths, 40)
        zb = yb + 52
        o.append(f'<path d="{zig_d(cx, steps, zb)}" fill="none" stroke="{c}" stroke-width="3"/>')
        o.append(f'<path d="{zig_d(cx, offset_steps(steps, 9), zb)}" fill="none" stroke="{c}" stroke-width="0.9"/>')
        o.append(f'<path d="{zig_d(cx, offset_steps(steps, 14), zb)}" fill="none" stroke="{c}" stroke-width="0.9"/>')
        d.append(f'<clipPath id="{uid}cr"><path d="{zig_d(cx, offset_steps(steps, 22), zb)}"/></clipPath>')
        arcs = "".join(f'<path d="{arch_d(cx, yc, r, zb)}" stroke-width="{1.4 if k % 4 == 0 else 0.6}"/>'
                       for k, r in enumerate(range(int(Ra + 14), int(Ra + 400), 9)))
        o.append(f'<g clip-path="url(#{uid}cr)" fill="none" stroke="{c}">{arcs}</g>')
        o.append(f'<rect x="{cx - widths[0] - 16 - sill_ext}" y="{zb}" width="{2 * (widths[0] + 16 + sill_ext)}" height="3" fill="{c}"/>')
        o.append(f'<rect x="{cx - widths[0] - 16 - sill_ext}" y="{zb + 8}" width="{2 * (widths[0] + 16 + sill_ext)}" height="0.9" fill="{c}"/>')
    # soleira
    o.append(triple_h(cx - a0 - 86, cx + a0 + 86, yb + 8, c, 5, th=(3, 0.9, 0.9)))
    return "".join(d), "".join(o)

JTONE = dict(gamma=1.9, lo=(0.03, 0.05, 0.095), mid=(0.20, 0.235, 0.30), hi=(0.985, 0.90, 0.70))

def jacket(art="atrio.jpg", fit="xMidYMid slice", tone=JTONE, shift=(0, 0), zoom=1.0):
    W, H = 1600, 2300
    cx, yc, a0, yb = W / 2, 760, 470, 1440
    defs = [foil_defs("jf", (0, 0, W, H)), foil_defs("wf", (0, 0, 1400, 420)),
            tritone_filter("tri", **(tone or {}))]
    ink = "url(#jf)"
    dd, fr = portal(cx, yc, a0, yb, ink, "J", micro_text=("CONSERVAÇÃO · VÍNCULO · COMPATIBILIDADE ·", "VAZÃO · DISSIPAÇÃO · CAPACIDADE · RETORNO"))
    defs.append(dd)
    defs.append(f'<clipPath id="win"><path d="{arch_closed(cx, yc, a0 - 2, yb)}"/></clipPath>')
    iw, ih = 2 * a0 * zoom, (yb - yc + a0) * zoom
    ix, iy = cx - iw / 2 + shift[0], yc - a0 - (ih - (yb - yc + a0)) / 2 + shift[1]
    img = (f'<g clip-path="url(#win)"><image href="{ART}{art}" x="{ix:.1f}" y="{iy:.1f}" width="{iw:.1f}" height="{ih:.1f}" '
           f'preserveAspectRatio="{fit}" filter="url(#tri)"/>'
           f'<rect x="{cx - a0}" y="{yc - a0}" width="{2 * a0}" height="{yb - yc + a0}" fill="url(#jvig)"/></g>')
    defs.append(f'<radialGradient id="jvig" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{(yc - a0 + yb) / 2}" r="{a0 * 1.25}">'
                f'<stop offset="0.55" stop-color="{NOITE}" stop-opacity="0"/><stop offset="1" stop-color="{NOITE}" stop-opacity=".55"/></radialGradient>')
    wd, wb, wh = wordmark("url(#wf)", "Jw")
    defs.append(wd)
    ws = 0.9
    body = (img + fr +
            f'<g transform="translate({(W - 1400 * ws) / 2:.1f} 1618) scale({ws})">{wb}</g>' +
            f'<path d="{tp("WERIK MARTINS", ITA, 48, W / 2, 2108, 0.42, "middle")}" fill="{ink}"/>')
    aw = text_width("WERIK MARTINS", ITA, 48, 0.42)
    for side in (-1, 1):
        body += f'<path d="{diamond(W / 2 + side * (aw / 2 + 40), 2108 - 17, 5, 7.5)}" fill="{ink}"/>'
    body += f'<rect x="40" y="40" width="{W - 80}" height="{H - 80}" fill="none" stroke="{ink}" stroke-width="1.2"/>'
    return svg(W, H, body, "".join(defs), bg=NOITE)

# ------------------------------------------------------------------ abertura de capítulo
P1 = "O contrato tinha onze páginas, e Pelle Dorn fazia questão de que Ilan Varek conhecesse cada uma delas antes de entrar no prédio."
P2 = ("— Cláusula sétima — leu o agente da seguradora, segurando o papel aberto contra o vento, o nariz vermelho "
      "afundado num cachecol verde. — “O contratado se compromete a não causar dano estrutural ao imóvel segurado.”")

def justify(paras, x, y, width, size, lead, drop=None, sc_words=0, indent=0, ink=NOITE):
    """Composição justificada com hifenização (pt_BR); drop=(linhas, recuo) para a capitular; versaletes nas primeiras palavras."""
    import pyphen
    hy = pyphen.Pyphen(lang="pt_BR")
    sp = text_width(" ", GAR, size)
    out = []; line_no = 0
    for pi, para in enumerate(paras):
        raw = para.split(" ")
        toks = []
        k = 0
        while k < len(raw):
            w = raw[k]
            if w == "—" and k + 1 < len(raw):
                w = "— " + raw[k + 1]; k += 1
            toks.append(w); k += 1
        items = []
        for wi, w in enumerate(toks):
            f = GARSC if (pi == 0 and wi < sc_words) else GAR
            items.append([w.lower() if f == GARSC else w, f])
        lines, cur = [], []
        def lim_for(n, first):
            L = width
            if drop and n < drop[0]: L -= drop[1]
            if first and indent and pi > 0: L -= indent
            return L
        i = 0
        while i < len(items):
            t, f = items[i]
            n = line_no + len(lines)
            L = lim_for(n, not lines)
            used = sum(text_width(a, b, size) for a, b in cur) + sp * len(cur)
            tw = text_width(t, f, size)
            if used + tw <= L or not cur:
                cur.append([t, f]); i += 1; continue
            if " " not in t:
                for a_, b_ in hy.iterate(t):
                    if len(a_) >= 3 and len(b_) >= 3 and used + text_width(a_ + "-", f, size) <= L:
                        cur.append([a_ + "-", f]); items[i] = [b_, f]; break
            lines.append((cur, L, n)); cur = []
        if cur:
            n = line_no + len(lines)
            lines.append((cur, lim_for(n, not lines), n))
        for li, (ln, L, n) in enumerate(lines):
            lx = x + (drop[1] if drop and n < drop[0] else 0) + (indent if (li == 0 and indent and pi > 0) else 0)
            ws = [text_width(a, b, size) for a, b in ln]
            last = li == len(lines) - 1
            gap = sp if last or len(ln) == 1 else (L - sum(ws)) / (len(ln) - 1)
            cx_ = lx
            for (tx, f), w_ in zip(ln, ws):
                out.append(text_path(tx, f, size, cx_, y))
                cx_ += w_ + gap
            y += lead
        line_no += len(lines)
    return f'<path d="{" ".join(out)}" fill="{ink}"/>', y

def chapter_page():
    W, H = 1600, 2300
    PAPER, INK = MARFIM, NOITE
    defs = [lin_grad("au", [(0, "#B8955A"), (0.45, CH3), (0.75, "#A88850"), (1, "#7A5E32")], user=(0, 0, W, H))]
    gold = "url(#au)"
    o = []
    # cabeçalho em arco escalonado: numeral do capítulo diante de um sol nascente
    cx, yc, a0, yb = W / 2, 700, 150, 1000
    for aa, w in ((a0, 1.6), (a0 + 7, 0.7), (a0 + 18, 2.6)):
        o.append(f'<path d="{arch_d(cx, yc, aa, yb)}" fill="none" stroke="{gold}" stroke-width="{w}"/>')
    steps = zig_auto(yc, a0 + 18 + 30, [a0 + 52, a0 + 34, a0 + 6, a0 - 30, a0 - 76], 12)
    o.append(f'<path d="{zig_d(cx, steps, yb)}" fill="none" stroke="{gold}" stroke-width="1.8"/>')
    o.append(f'<path d="{zig_d(cx, offset_steps(steps, 6), yb)}" fill="none" stroke="{gold}" stroke-width="0.6"/>')
    defs.append(f'<clipPath id="chz"><path d="{zig_d(cx, offset_steps(steps, 11), yb)}"/></clipPath>')
    arcs = "".join(f'<path d="{arch_d(cx, yc, r, yb)}"/>' for r in range(a0 + 26, a0 + 120, 8))
    o.append(f'<g clip-path="url(#chz)" fill="none" stroke="{gold}" stroke-width="0.55">{arcs}</g>')
    o.append(f'<path d="{diamond(cx, yc - a0 - 9, 5, 8)}" fill="{gold}"/>')
    # sol nascente + raios
    num_d = tp("I", ITA, 330, cx, yb - 36, 0, "middle")
    defs.append(f'<clipPath id="chv"><path d="{arch_closed(cx, yc, a0 - 8, yb - 34)}"/></clipPath>')
    defs.append(f'<mask id="chm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="white"/>'
                f'<path d="{num_d}" fill="black" stroke="black" stroke-width="22" stroke-linejoin="round"/></mask>')
    R = []
    sx, sy = cx, yb - 34
    for k in range(-16, 17):
        ang = 270 + k * 5
        if k % 4 == 0:
            p0 = polar(sx, sy, 92, ang); p1, p2 = polar(sx, sy, 420, ang - 1.1), polar(sx, sy, 420, ang + 1.1)
            R.append(f'<path d="M{P(*p0)} L{P(*p1)} L{P(*p2)} Z" fill="{gold}"/>')
        else:
            p0, p1 = polar(sx, sy, 98 if k % 2 == 0 else 112, ang), polar(sx, sy, 420, ang)
            R.append(f'<path d="M{P(*p0)} L{P(*p1)}" stroke="{gold}" stroke-width="{0.9 if k % 2 == 0 else 0.5}"/>')
    R.append(f'<path d="M{sx - 72},{sy} A72,72 0 0 1 {sx + 72},{sy} Z" fill="{gold}"/>')
    R.append(f'<path d="M{sx - 82},{sy} A82,82 0 0 1 {sx + 82},{sy}" fill="none" stroke="{gold}" stroke-width="1"/>')
    o.append(f'<g clip-path="url(#chv)"><g mask="url(#chm)">{"".join(R)}</g></g>')
    o.append(f'<path d="{num_d}" fill="{INK}"/>')
    o.append(triple_h(cx - a0, cx + a0, sy + 1, gold, 4.5, th=(2.4, 0.7, 0.7)))
    o.append(triple_h(cx - a0 - 70, cx + a0 + 70, yb + 8, gold, 4.5, th=(2.4, 0.7, 0.7)))
    # rótulo, título, fio
    o.append(f'<path d="{tp("CAPÍTULO UM", JB, 22, cx, 1100, 0.6, "middle")}" fill="{INK}"/>')
    o.append(f'<path d="{tp("Noite tropical", ITA, 104, cx, 1232, 0.02, "middle")}" fill="{INK}"/>')
    o.append(triple_h(cx - 250, cx - 46, 1292, gold, 4.5, th=(0.7, 2.0, 0.7)))
    o.append(triple_h(cx + 46, cx + 250, 1292, gold, 4.5, th=(0.7, 2.0, 0.7)))
    o.append(step_orn(cx, 1292, gold, 0.85))
    # capitular déco
    x0, y0 = 200, 1460
    size, lead = 44, 66
    cap_top = y0 - 0.66 * size - 2
    cap_s = 2 * lead + 0.66 * size + 2 + 10
    bx, by = x0, cap_top
    o.append(f'<path d="{notched_rect(bx, by, bx + cap_s, by + cap_s, 18, 0)}" fill="none" stroke="{gold}" stroke-width="2.2"/>')
    o.append(f'<path d="{notched_rect(bx, by, bx + cap_s, by + cap_s, 18, 7)}" fill="none" stroke="{gold}" stroke-width="0.7"/>')
    ccx, ccy = bx + cap_s / 2, by + cap_s - 16
    fan = []
    defs.append(f'<clipPath id="capc"><rect x="{bx + 14}" y="{by + 14}" width="{cap_s - 28}" height="{cap_s - 30}"/></clipPath>')
    for k in range(-8, 9):
        ang = 270 + k * 10.5
        p0, p1 = polar(ccx, ccy, 30, ang), polar(ccx, ccy, cap_s, ang)
        fan.append(f'M{P(*p0)} L{P(*p1)}')
    o.append(f'<path d="{" ".join(fan)}" stroke="{gold}" stroke-width="0.8" clip-path="url(#capc)"/>')
    o.append(f'<rect x="{bx + 14}" y="{ccy}" width="{cap_s - 28}" height="1.6" fill="{gold}"/>')
    capd = tp("O", ITA, 170, ccx, by + cap_s - 24, 0, "middle")
    o.append(f'<path d="{capd}" fill="{PAPER}" stroke="{PAPER}" stroke-width="16" stroke-linejoin="round"/>')
    o.append(f'<path d="{capd}" fill="{INK}"/>')
    txt, yend = justify([P1[2:], P2], x0, y0, W - 2 * x0, size, lead, drop=(3, cap_s + 24), sc_words=2, indent=66, ink=INK)
    o.append(txt)
    # fólio
    o.append(f'<path d="{tp("9", JL, 26, cx, H - 150, 0, "middle")}" fill="{INK}"/>')
    for side in (-1, 1):
        o.append(f'<path d="{diamond(cx + side * 30, H - 159, 3.5, 5.5)}" fill="{gold}"/>')
        o.append(f'<rect x="{min(cx + side * 44, cx + side * 120)}" y="{H - 159.4}" width="76" height="0.8" fill="{gold}"/>')
    return svg(W, H, "".join(o), "".join(defs), bg=PAPER)

# ------------------------------------------------------------------ animação (8 s)
def damped(u, amp, freq=2.2, tau=0.28):
    return amp * math.exp(-u / tau) * math.sin(2 * math.pi * freq * u)

def motion_frame(i, t):
    W, H = 1920, 1080
    es = 0.60
    ex, ey = (W - 1000 * es) / 2, 30
    # cronograma
    fr = ease_in_out(seg(t, 0.03, 0.22))
    cr = ease(seg(t, 0.10, 0.26))
    doors = 1 - ease_in_out(seg(t, 0.24, 0.42))
    rays = seg(t, 0.32, 0.52)
    rise = seg(t, 0.34, 0.54)
    crack = seg(t, 0.545, 0.585)
    flash = math.sin(math.pi * seg(t, 0.545, 0.62)) if 0.545 <= t <= 0.62 else 0.0
    sword = seg(t, 0.56, 0.68)
    ub = seg(t, 0.67, 1.0)
    beam = -7.0 * ease_out(seg(t, 0.67, 0.74)) + (damped(ub * 2.4, 2.2, 1.6, 0.35) if t > 0.67 else 0)
    swing = (damped(ub * 2.4, 6.5, 1.25, 0.42) if t > 0.67 else 0)
    lit = 7 * seg(t, 0.72, 0.86)
    glint = seg(t, 0.80, 0.93)
    glow = ease_out(seg(t, 0.36, 0.6))
    ed, eb = emblem("url(#mf)", uid="M", doors=doors, rays=rays, rise=rise, crack=crack, sword=sword,
                    beam=beam, swing=swing, lit=lit, frame=fr, bevel=True, crown=cr, glow=glow, flash=flash)
    # título com tracking que se fecha
    tu = ease_out(seg(t, 0.74, 0.95))
    wd, wb, wh = wordmark("url(#mw)", "Mw", tr_big=0.16 + 0.34 * (1 - tu))
    ws = 0.56
    wy = 30 + 1200 * es + 18
    defs = [foil_defs("mf", (0, 0, 1000, 1200), glint=glint if 0 < glint < 1 else None),
            foil_defs("mw", (0, 0, 1400, 420), glint=seg(t, 0.86, 0.97) if 0 < seg(t, 0.86, 0.97) < 1 else None),
            foil_defs("mh", (0, 0, W, H)), ed, wd,
            f'<radialGradient id="mbg" gradientUnits="userSpaceOnUse" cx="{W / 2}" cy="{H * 0.42}" r="{W * 0.62}">'
            f'<stop offset="0" stop-color="{NOITE2}"/><stop offset="0.6" stop-color="{NOITE}"/><stop offset="1" stop-color="#070B14"/></radialGradient>']
    # horizonte prolongado (desenha das bordas para o centro)
    hy = ey + EYH * es
    zx = ex + (EC - 404) * es
    hp = ease_in_out(seg(t, 0.0, 0.16))
    hz = ""
    if hp > 0:
        L = (zx - 14) * hp
        hz = (triple_h(0, L, hy, "url(#mh)", 5, th=(0.7, 2.2, 0.7)) +
              triple_h(W - L, W, hy, "url(#mh)", 5, th=(0.7, 2.2, 0.7)))
    # luz que escapa da porta: raios largos e tênues no fundo
    bgr = ""
    rv = ease_out(seg(t, 0.40, 0.70))
    if rv > 0:
        sx, sy = ex + EC * es, ey + EYH * es
        Rr = 300 + 1500 * rv
        wed = []
        for k in range(-8, 9):
            ang = 270 + k * 10
            p0 = polar(sx, sy, 60, ang)
            p1, p2 = polar(sx, sy, Rr, ang - 1.9), polar(sx, sy, Rr, ang + 1.9)
            wed.append(f'M{P(*p0)} L{P(*p1)} L{P(*p2)} Z')
        defs.append(f'<radialGradient id="mrg" gradientUnits="userSpaceOnUse" cx="{sx}" cy="{sy}" r="{Rr:.0f}">'
                    f'<stop offset="0" stop-color="{CH2}" stop-opacity=".065"/><stop offset="1" stop-color="{CH2}" stop-opacity="0"/></radialGradient>')
        defs.append(f'<clipPath id="msky"><rect x="0" y="0" width="{W}" height="{sy - 6:.1f}"/></clipPath>')
        bgr = f'<path d="{" ".join(wed)}" fill="url(#mrg)" clip-path="url(#msky)"/>'
    body = (f'<rect width="{W}" height="{H}" fill="url(#mbg)"/>' + bgr + hz +
            f'<g transform="translate({ex:.1f} {ey}) scale({es})">{eb}</g>'
            f'<g transform="translate({(W - 1400 * ws) / 2:.1f} {wy + 14 * (1 - tu):.1f}) scale({ws})" opacity="{ease(seg(t, 0.74, 0.86)):.3f}">{wb}</g>')
    return svg(W, H, body, "".join(defs))

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
    if "capa" in only or "all" in only:
        to_png(cover_cloth(), f"{OUT}/capa_tecido_champanhe.png", 1600)
    if "sobrecapa" in only or "all" in only:
        to_png(jacket(), f"{OUT}/sobrecapa_limiar.png", 1600)
    if "capitulo" in only or "all" in only:
        to_png(chapter_page(), f"{OUT}/abertura_capitulo.png", 1600)
    if "guarda" in only or "all" in only:
        to_png(endpaper(), f"{OUT}/guarda_limiar.png", 3200)
    if "sinais" in only or "all" in only:
        build_signs()
        build_principles()
    if "frames" in only:
        S = "/tmp/claude-0/-home-user-LTKG/0ae43a17-9955-54f0-9172-040bd4d1f0e3/scratchpad/t/"
        for tt in [float(a) for a in os.environ.get('TT', '0.12,0.33,0.5,0.6,0.78,0.9,1.0').split(',')]:
            t1 = time.time()
            to_png(motion_frame(int(tt * 239), tt), f"{S}mf_{int(tt * 100):03d}.png", 1920)
            print("frame", tt, round(time.time() - t1, 2), "s")
    if "motion" in only or "all" in only:
        animate(motion_frame, 240, f"{OUT}/animacao_limiar.mp4", gif=f"{OUT}/animacao_limiar.gif")
    print("B ok", round(time.time() - t0, 1), "s")
