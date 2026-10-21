#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPÇÃO C — INSTRUMENTO. O brasão como um astrolábio que afere deuses: limbo graduado, rete com sete
ponteiros (os sete losangos), sol-lente com anéis de Newton rachada, espada-alidade e guarda-balança
de precisão. Prata sobre obsidiana; latão como acento; iridescência de película fina só na lente."""
import math, os, random, sys, time
import kit
from kit import *
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = "/home/user/LTKG/exportacoes/identidade_v2/C_Instrumento"
ART = "/home/user/LTKG/build/arte"
os.makedirs(OUT, exist_ok=True)

OBS, OBS2 = "#0B0C0E", "#15171B"
BRASS, BRASS_D = "#B9975B", "#8C7142"
PAPER, INK = "#F2EFE8", "#16181C"
SILVER = [(0, "#FFFFFF"), (0.33, "#BFC4CB"), (0.66, "#7B818A"), (1, "#E3E7EC")]
IRID = ["#7A5CFF", "#29C3C9", "#E8D27A", "#F06AA8"]
IS, ISI = "InstrumentSerif-Regular.ttf", "InstrumentSerif-Italic.ttf"
MONO, MONOR = "IBMPlexMono-Light.ttf", "IBMPlexMono-Regular.ttf"
GAR, GARI = "EBGaramond-Regular.ttf", "EBGaramond-Italic.ttf"
LEIS = ["Conservação", "Vínculo", "Compatibilidade", "Vazão", "Dissipação", "Capacidade", "Retorno"]
ROM = ["I", "II", "III", "IV", "V", "VI", "VII"]
PRINC = ["Pulso", "Brasa", "Trama", "Clarão", "Eco", "Carga"]
LAW_DEG = [-90 + k * 360 / 7 for k in range(7)]          # posição canônica dos sete losangos
SEPT = "51°25′43″"                                        # 360/7 em sexagesimal

# ------------------------------------------------------------------ utilidades próprias
def f2(x): return f"{x:.2f}"

def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))

def irid(u):
    """Cor de película fina (cíclica) para u em [0,1)."""
    u = (u % 1.0) * 4; i = int(u); return hexmix(IRID[i % 4], IRID[(i + 1) % 4], u - i)

def silver_grad(uid, x1=0, y1=0, x2=1000, y2=1000, reflect=True):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in SILVER)
    sp = ' spreadMethod="reflect"' if reflect else ""
    return (f'<linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{sp}>'
            f'{st}</linearGradient>')

def irid_grad(uid, x1, y1, x2, y2):
    st = "".join(f'<stop offset="{k / 3:.3f}" stop-color="{c}"/>' for k, c in enumerate(IRID))
    return f'<linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>'

def arc_d(cx, cy, r, a0, a1):
    """Arco (graus SVG, sentido horário de a0 para a1)."""
    x0, y0 = polar(cx, cy, r, a0); x1, y1 = polar(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{P(x0, y0)} A{r:.2f},{r:.2f} 0 {large} 1 {P(x1, y1)}"

def circ(cx, cy, r, c, w, extra=""):
    return f'<circle cx="{f2(cx)}" cy="{f2(cy)}" r="{f2(r)}" fill="none" stroke="{c}" stroke-width="{w}" {extra}/>'

def ticks_d(cx, cy, r0, r1, degs):
    return "".join(f"M{P(*polar(cx, cy, r0, a))} L{P(*polar(cx, cy, r1, a))} " for a in degs)

def label_on_arc(text, font, size, cx, cy, r, center_deg, tracking=0.0, flip=None):
    """Texto centrado num ângulo. Metade de cima: lê no sentido horário, topo para fora.
    Metade de baixo (flip): lê no sentido anti-horário, topo para dentro (fica de pé)."""
    infos, pos, upm, gs, order = kit._shape(text, font)
    s = size / upm
    adv = [p.x_advance * s + tracking * size for p in pos]
    total = sum(adv) - tracking * size
    if flip is None:
        cd = center_deg % 360
        flip = 0 < cd < 180
    pen = SVGPathPen(gs)
    span = total / r
    a = math.radians(center_deg) + (span / 2 if flip else -span / 2)
    for info, ad in zip(infos, adv):
        gname = order[info.codepoint]
        if not flip:
            t = (-math.sin(a), math.cos(a)); u = (math.cos(a), math.sin(a))
        else:
            t = (math.sin(a), -math.cos(a)); u = (-math.cos(a), -math.sin(a))
        bx, by = cx + r * math.cos(a), cy + r * math.sin(a)
        m = (s * t[0], s * t[1], s * u[0], s * u[1], bx, by)
        gs[gname].draw(TransformPen(pen, m))
        a += (-ad / r) if flip else (ad / r)
    return pen.getCommands()

def rotp(px, py, ox, oy, deg):
    g = math.radians(deg); dx, dy = px - ox, py - oy
    return ox + dx * math.cos(g) - dy * math.sin(g), oy + dx * math.sin(g) + dy * math.cos(g)

# Uma "camada" é uma lista de itens ('f', d) preenchido, ('s', d, largura) traço, com transform opcional.
def draw_items(items, c, op=1.0):
    out = []
    for it in items:
        tr = f' transform="{it[3]}"' if len(it) > 3 and it[3] else ""
        if it[0] == "f":
            out.append(f'<path d="{it[1]}" fill="{c}"{tr}/>')
        else:
            out.append(f'<path d="{it[1]}" fill="none" stroke="{c}" stroke-width="{it[2]}" stroke-linecap="round" stroke-linejoin="round"{tr}/>')
    g = "".join(out)
    return g if op >= 1 else f'<g opacity="{op:.3f}">{g}</g>'

def knock_items(items, gap):
    out = []
    for it in items:
        tr = f' transform="{it[3]}"' if len(it) > 3 and it[3] else ""
        if it[0] == "f":
            out.append(f'<path d="{it[1]}" fill="black" stroke="black" stroke-width="{2 * gap}" stroke-linejoin="round"{tr}/>')
        else:
            out.append(f'<path d="{it[1]}" fill="none" stroke="black" stroke-width="{it[2] + 2 * gap}" stroke-linecap="round" stroke-linejoin="round"{tr}/>')
    return "".join(out)

def mask(uid, inner, w=1000, h=1000, x=0, y=0):
    return (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>{inner}</mask>')

# ------------------------------------------------------------------ geometria do astrolábio
CX = CY = 500.0
R_CAP = 376.0                       # trópico de Capricórnio = aro da rete
R_EQ = R_CAP / math.tan(math.radians((90 + 23.44) / 2))
R_CAN = R_EQ * math.tan(math.radians((90 - 23.44) / 2))
ECL_R = (R_CAP + R_CAN) / 2; ECL_OFF = (R_CAP - R_CAN) / 2
LAT = 48.0                          # latitude fictícia da lâmina

def plate_lines():
    """Lâmina (tímpano): almucântaras e azimutes da projeção estereográfica real para LAT."""
    d = []
    yup = lambda dec: R_EQ * math.tan(math.radians((90 - dec) / 2))
    for alt in list(range(0, 90, 6)) + [-18]:
        z = 90 - alt
        y1, y2 = yup(LAT - z), yup(LAT + z)
        c = (y1 + y2) / 2; r = abs(y1 - y2) / 2
        d.append(("circle", CX, CY - c, r, 0.9 if alt in (0, -18) else 0.5, alt == -18))
    # azimutes: círculos que passam pelo zênite e pelo nadir projetados
    yz, yn = yup(LAT), yup(LAT + 180)
    mid = (yz + yn) / 2; half = (yz - yn) / 2
    for az in range(15, 180, 15):
        k = half / math.tan(math.radians(az))
        for s in (-1, 1):
            cxp = CX + s * k; r = math.hypot(k, half)
            d.append(("circle", cxp, CY - mid, r, 0.45, False))
    return d, (CX, CY - yz)

def pointer_d(th, sweep=-17.0, rtip=290.0, w0=5.4):
    """Ponteiro de estrela em espinho curvo: nasce sob o losango e afina até a estrela."""
    pol = lambda da, r: polar(CX, CY, r, th + da)
    T = pol(sweep, rtip); r0 = R_CAP - 13
    A = pol(-math.degrees(w0 / r0), r0); B = pol(math.degrees(w0 / r0), r0)
    rm = (r0 + rtip) / 2
    cA = pol(sweep * .15 - math.degrees(w0 * .55 / rm), rm + 6)
    cB = pol(sweep * .15 + math.degrees(w0 * .55 / rm), rm - 4)
    return f"M{P(*A)} Q{P(*cA)} {P(*T)} Q{P(*cB)} {P(*B)} Z", T

def lozenge_d(th, rc=None, hl=23.0, hw=12.5):
    rc = rc or R_CAP
    q = [polar(CX, CY, rc + hl, th), polar(CX, CY, rc, th + math.degrees(hw / rc)),
         polar(CX, CY, rc - hl, th), polar(CX, CY, rc, th - math.degrees(hw / rc))]
    return polyline(q, True)

def rete_items(rot=0.0, lw=1.0):
    """Rete vazada: aro (trópico), eclíptica graduada, sete losangos no aro e sete ponteiros curvos."""
    it = []
    for rr, w in ((R_CAP + 2.2, 2.0), (R_CAP - 3.6, 0.6)):
        it.append(("s", f"M{P(CX - rr, CY)} a{rr:.2f},{rr:.2f} 0 1 0 {2 * rr:.2f},0 a{rr:.2f},{rr:.2f} 0 1 0 {-2 * rr:.2f},0", w * lw))
    ex, ey = CX, CY - ECL_OFF
    ro, ri = ECL_R - 1, ECL_R - 12
    for rr, w in ((ro, 1.2), (ri, 0.6)):
        it.append(("s", f"M{P(ex - rr, ey)} a{rr:.2f},{rr:.2f} 0 1 0 {2 * rr:.2f},0 a{rr:.2f},{rr:.2f} 0 1 0 {-2 * rr:.2f},0", w * lw))
    tk = "".join(f"M{P(*polar(ex, ey, ri, a))} L{P(*polar(ex, ey, ri + (11 if a % 30 == 0 else 5.5 if a % 10 == 0 else 3.2), a))} "
                 for a in range(0, 360, 2))
    it.append(("s", tk, 0.5 * lw))
    for th in LAW_DEG:
        d, T = pointer_d(th)
        it.append(("f", d))
        it.append(("s", f"M{P(T[0] - 2.6, T[1])} a2.6,2.6 0 1 0 5.2,0 a2.6,2.6 0 1 0 -5.2,0", 0.8 * lw))
        it.append(("f", lozenge_d(th)))
    if rot:
        it = [(x[0], x[1], x[2] if x[0] == "s" else 0, f"rotate({rot:.3f} {CX} {CY})") for x in it]
    return it

def lozenge_engrave(rot=0.0):
    """Bisel interno dos losangos (linha gravada) e ponto central."""
    out = []
    for th in LAW_DEG:
        out.append(("s", lozenge_d(th + rot, hl=15, hw=7.0), 0.9))
        # nervura gravada ao longo do ponteiro
        pol = lambda da, r: polar(CX, CY, r, th + rot + da)
        r0, rt, sw = R_CAP - 26, 300, -17.0 * (300 - 290 + 1) / 11
        pts = []
        for i in range(0, 21):
            u = i / 20
            # mesma curva quadrática do eixo do ponteiro (raiz → controle → ponta)
            A = pol(0, R_CAP - 13); C = pol(-17 * .15, (R_CAP - 13 + 290) / 2 + 1); T = pol(-17, 290)
            x = (1 - u) ** 2 * A[0] + 2 * u * (1 - u) * C[0] + u * u * T[0]
            y = (1 - u) ** 2 * A[1] + 2 * u * (1 - u) * C[1] + u * u * T[1]
            pts.append((x, y))
        out.append(("s", polyline(pts[1:15]), 0.7))
    return out

def sword_items(srot=0.0, beam=-7.0, lw=1.0):
    """Espada-alidade (vertical) + travessão-balança graduado. srot gira a espada em torno do centro."""
    solid, lines, eng = [], [], []
    T = (lambda x, y: rotp(x, y, CX, CY, srot)) if srot else (lambda x, y: (x, y))
    def poly(pts, close=True): return polyline([T(*p) for p in pts], close)
    # lâmina
    blade = [(489, 344), (511, 344), (507.5, 806), (500, 884), (492.5, 806)]
    solid.append(("f", poly(blade)))
    eng.append(("s", poly([(500, 358), (500, 790)], False), 1.2))
    tk = ""
    for k, yy in enumerate(range(366, 786, 12)):
        L = 6.5 if k % 5 == 0 else 3.6
        tk += poly([(490.6, yy), (490.6 + L, yy)], False) + " "
    eng.append(("s", tk, 0.55))
    # colar / ricasso
    solid.append(("f", poly([(484, 338), (516, 338), (512, 348), (488, 348)])))
    # punho com fio enrolado
    solid.append(("f", poly([(492.5, 232), (507.5, 232), (507.5, 318), (492.5, 318)])))
    wr = "".join(poly([(492.5, yy), (507.5, yy - 5)], False) + " " for yy in range(240, 318, 5))
    eng.append(("s", wr, 0.55))
    solid.append(("f", poly([(488, 226), (512, 226), (509, 233), (491, 233)])))
    # pomo = anel de suspensão
    px, py = T(500, 212)
    solid.append(("f", f"M{P(px - 14, py)} a14,14 0 1 0 28,0 a14,14 0 1 0 -28,0 Z M{P(px - 7, py)} a7,7 0 1 1 14,0 a7,7 0 1 1 -14,0 Z"))
    # travessão (pivô gira com a espada)
    gx, gy = T(500, 330)
    L = 200
    def B(x, y): return rotp(gx + x, gy + y, gx, gy, beam + srot)
    beam_poly = [B(-L, -3.1), B(-30, -6.6), B(0, -7.4), B(30, -6.6), B(L, -3.1), B(L, 3.1), B(30, 6.6), B(0, 7.4), B(-30, 6.6), B(-L, 3.1)]
    solid.append(("f", polyline(beam_poly, True)))
    eng.append(("s", polyline([B(-L + 10, 0), B(-16, 0)]) + " " + polyline([B(16, 0), B(L - 10, 0)]), 0.6))
    # graduação sobre o travessão (régua)
    gt = ""
    for s in (-1, 1):
        for k in range(1, 20):
            x = s * k * 9.5
            h = 6.5 if k % 5 == 0 else 3.4
            yb = -(3.1 + (7.4 - 3.1) * (1 - abs(x) / L)) - 1.8
            gt += polyline([B(x, yb), B(x, yb - h)]) + " "
    lines.append(("s", gt, 0.55 * lw))
    # extremidades: anéis
    ends = []
    for s in (-1, 1):
        ex, ey = B(s * L, 0)
        solid.append(("f", f"M{P(ex - 6.5, ey)} a6.5,6.5 0 1 0 13,0 a6.5,6.5 0 1 0 -13,0 Z"))
        eng.append(("s", f"M{P(ex - 2.6, ey)} a2.6,2.6 0 1 0 5.2,0 a2.6,2.6 0 1 0 -5.2,0", 1.0))
        ends.append((ex, ey))
    # pivô: mancal + cutelo
    solid.append(("f", f"M{P(gx - 11, gy)} a11,11 0 1 0 22,0 a11,11 0 1 0 -22,0 Z"))
    eng.append(("s", f"M{P(gx - 5, gy)} a5,5 0 1 0 10,0 a5,5 0 1 0 -10,0", 1.0))
    solid.append(("f", poly([(500, 314), (507, 326), (493, 326)])))
    # pratos (pendem na vertical)
    drop, hw = 136, 41
    for ex, ey in ends:
        py_ = ey + drop
        for k in (-1, 0, 1):
            lines.append(("s", f"M{P(ex, ey + 6)} L{P(ex + k * (hw - 5), py_ - 1)}", (0.75 if k else 0.5) * lw))
        solid.append(("f", f"M{P(ex - hw, py_)} Q{P(ex, py_ + 30)} {P(ex + hw, py_)} L{P(ex + hw - 2, py_ - 2.4)} L{P(ex - hw + 2, py_ - 2.4)} Z"))
        eng.append(("s", f"M{P(ex - hw + 7, py_ + 3.2)} Q{P(ex, py_ + 22)} {P(ex + hw - 7, py_ + 3.2)}", 0.6))
        solid.append(("f", f"M{P(ex - 3, py_ + 14.5)} L{P(ex + 3, py_ + 14.5)} L{P(ex, py_ + 21)} Z"))
    return solid + lines, eng, (gx, gy), ends

def tilt_gauge(gx, gy, beam=-7.0, c="#000", lw=1.0, acc=None):
    """Nível tracejado + pequeno arco graduado à direita do pivô: o travessão é o índice; o setor em
    acento marca a inclinação e a leitura fica logo abaixo do nível."""
    acc = acc or c
    out = []
    out.append(f'<path d="M{P(gx - 262, gy)} L{P(gx + 262, gy)}" stroke="{c}" stroke-width="{0.5 * lw}" stroke-dasharray="5 3.5" fill="none"/>')
    R = 150
    out.append(f'<path d="{arc_d(gx, gy, R, -16, 3)}" stroke="{c}" stroke-width="{0.55 * lw}" fill="none"/>')
    tk = ""
    for k in range(-3, 17):
        a = -k
        L = 7 if k % 5 == 0 else 3.6
        tk += f"M{P(*polar(gx, gy, R, a))} L{P(*polar(gx, gy, R + L, a))} "
    out.append(f'<path d="{tk}" stroke="{c}" stroke-width="{0.5 * lw}" fill="none"/>')
    if abs(beam) > 0.2:
        a0, a1 = min(0, beam), max(0, beam)
        p1 = polar(gx, gy, R, a0); p2 = polar(gx, gy, R, a1); p3 = polar(gx, gy, R - 6, a1); p4 = polar(gx, gy, R - 6, a0)
        out.append(f'<path d="M{P(*p1)} A{R},{R} 0 0 1 {P(*p2)} L{P(*p3)} A{R - 6},{R - 6} 0 0 0 {P(*p4)} Z" fill="{acc}"/>')
    rd = f"{abs(beam):.0f}°" if abs(beam - round(beam)) < 0.05 else f"{abs(beam):.1f}°"
    x, y = polar(gx, gy, R - 3, 5.2)
    out.append(f'<path d="{text_path(rd, MONOR, 9.5, x, y + 3.3, 0.02, "middle")}" fill="{acc}"/>')
    return "".join(out)

def lens(uid, c, mode="ink", crack=1.0, rings=34, gap_mask="", focus=1.0, fringe=1.0):
    """Sol de inverno como lente: anéis de Newton (r ∝ √k), franja de película fina, rachadura que desloca as metades."""
    R = 118
    defs, body = [], []
    rng = random.Random(7)
    # rachadura (pontos locais), do alto-esquerdo ao baixo-direito
    a0, a1 = math.radians(-138), math.radians(42)
    S = (math.cos(a0) * 150, math.sin(a0) * 150); E = (math.cos(a1) * 150, math.sin(a1) * 150)
    pts = [S]
    n = 15
    for i in range(1, n):
        u = i / n
        x = S[0] + (E[0] - S[0]) * u; y = S[1] + (E[1] - S[1]) * u
        j = rng.uniform(-1, 1) * (13 if 0.15 < u < 0.85 else 6)
        nx, ny = -(E[1] - S[1]), (E[0] - S[0]); nl = math.hypot(nx, ny)
        pts.append((x + nx / nl * j, y + ny / nl * j))
    pts.append(E)
    absP = [(CX + x, CY + y) for x, y in pts]
    A = absP + [(CX + 220, CY + 220), (CX + 220, CY - 220), (CX - 220, CY - 220)]
    Bp = absP + [(CX + 220, CY + 220), (CX - 220, CY + 220), (CX - 220, CY - 220)]
    defs.append(f'<clipPath id="{uid}-ha"><polygon points="{" ".join(P(*q) for q in A)}"/></clipPath>')
    defs.append(f'<clipPath id="{uid}-hb"><polygon points="{" ".join(P(*q) for q in Bp)}"/></clipPath>')
    defs.append(f'<clipPath id="{uid}-disc"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>')
    # conteúdo da lente
    inner = []
    if mode == "foil":
        defs.append(f'<radialGradient id="{uid}-glass" cx="{CX - 30}" cy="{CY - 36}" r="{R * 1.25}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0" stop-color="#2A2E35"/><stop offset="0.55" stop-color="#121418"/><stop offset="1" stop-color="#07080A"/></radialGradient>')
        inner.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#{uid}-glass)"/>')
    rc = c
    if mode == "holo":   # foil holográfico: cunhas cônicas iridescentes + brilho central
        nw = 120
        inner.append(f'<circle cx="{CX}" cy="{CY}" r="{R + 1}" fill="{c}"/>')
        wd = []
        for i in range(nw):
            p0 = polar(CX, CY, R + 2, i * 360 / nw - 0.3); p1 = polar(CX, CY, R + 2, (i + 1) * 360 / nw + 0.3)
            wd.append(f'<path d="M{CX},{CY} L{P(*p0)} L{P(*p1)} Z" fill="{hexmix(irid(i / nw * 2 + 0.08), "#DDE2E8", 0.38)}"/>')
        inner.append(f'<g opacity=".78">{"".join(wd)}</g>')
        defs.append(f'<radialGradient id="{uid}-hg" cx="{CX - 22}" cy="{CY - 26}" r="{R * 1.1}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0" stop-color="#FFFFFF" stop-opacity=".75"/><stop offset=".45" stop-color="#FFFFFF" stop-opacity=".18"/>'
                    f'<stop offset="1" stop-color="#000000" stop-opacity=".25"/></radialGradient>')
        inner.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#{uid}-hg)"/>')
        rc = OBS
    N = rings
    for k in range(1, N + 1):
        r = R * math.sqrt(k / (N + 0.6))
        dr = R * (math.sqrt((k + 1) / (N + 0.6)) - math.sqrt(k / (N + 0.6)))
        w = max(0.32, min(1.4, dr * 0.36))
        u = k / N
        if mode == "holo":
            inner.append(circ(CX, CY, r, rc, w, 'opacity=".45"'))
        elif u > 0.7 and fringe > 0:
            col = irid(0.1 + u * 1.1)
            mix = clamp((u - 0.7) / 0.3) ** 1.5 * 0.6 * fringe
            inner.append(circ(CX, CY, r, c, w, f'opacity="{1 - mix:.2f}"'))
            inner.append(circ(CX, CY, r, col, w, f'opacity="{mix:.2f}"'))
        else:
            inner.append(circ(CX, CY, r, c, w))
    inner.append(f'<circle cx="{CX}" cy="{CY}" r="{R * math.sqrt(0.45 / (N + 0.6)):.2f}" fill="{rc}"/>')
    if mode == "foil":   # reflexo especular em crescente (luz alta à esquerda)
        inner.append(f'<path d="M{CX - R},{CY} a{R},{R} 0 1 0 {2 * R},0 a{R},{R} 0 1 0 {-2 * R},0 Z '
                     f'M{CX - R + 16},{CY + 10} a{R - 4},{R - 4} 0 1 0 {2 * (R - 4)},0 a{R - 4},{R - 4} 0 1 0 {-2 * (R - 4)},0 Z" '
                     f'fill="#FFFFFF" fill-rule="evenodd" opacity=".13"/>')
    # retícula fina dentro da lente (eixos e escala)
    rt = f"M{CX - R + 8},{CY} L{CX + R - 8},{CY} "
    for k in range(-10, 11):
        if k == 0: continue
        L = 5 if k % 5 == 0 else 2.6
        rt += f"M{CX + k * 10},{CY - L} L{CX + k * 10},{CY + L} "
    inner.append(f'<path d="{rt}" stroke="{rc}" stroke-width="{0.5 if mode != "holo" else 0.9}" fill="none" opacity=".9"/>')
    inner_s = "".join(inner)
    sh = 2.6 * crack
    half_a = f'<g clip-path="url(#{uid}-ha)"><g transform="translate({sh * .78:.2f} {-sh * .62:.2f}) rotate({0.6 * crack:.2f} {CX} {CY})" clip-path="url(#{uid}-disc)">{inner_s}</g></g>'
    half_b = f'<g clip-path="url(#{uid}-hb)"><g clip-path="url(#{uid}-disc)">{inner_s}</g></g>'
    # máscara: rachadura + ramificações + recorte da lâmina
    nvis = max(2, int(len(absP) * clamp(crack * 1.0001)))
    crk = f'<polyline points="{" ".join(P(*q) for q in absP[:nvis])}" fill="none" stroke="black" stroke-width="{2.4 * clamp(crack * 3):.2f}" stroke-linejoin="miter"/>' if crack > 0 else ""
    br = ""
    if crack > 0.6:
        for idx, ang, ln in ((5, -40, 34), (10, 130, 26)):
            bx, by = absP[idx]
            pts2 = [(bx, by)]
            for s in range(1, 4):
                pts2.append((bx + math.cos(math.radians(ang + rng.uniform(-18, 18))) * ln * s / 3,
                             by + math.sin(math.radians(ang + rng.uniform(-18, 18))) * ln * s / 3))
            br += f'<polyline points="{" ".join(P(*q) for q in pts2)}" fill="none" stroke="black" stroke-width="{1.1 * (crack - .6) / .4:.2f}"/>'
    defs.append(mask(f"{uid}-crk", crk + br + gap_mask))
    blur = ""
    if focus < 0.999:
        defs.append(f'<filter id="{uid}-blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{(1 - focus) * 9:.2f}"/></filter>')
        blur = f' filter="url(#{uid}-blur)"'
    body.append(f'<g mask="url(#{uid}-crk)"><g{blur}>{half_b}{half_a}</g></g>')
    # aro (bezel) + franja iridescente cônica (segmentos)
    bez = circ(CX, CY, R + 1.6, c, 2.4) + circ(CX, CY, R + 6, c, 0.5)
    fr = []
    if fringe > 0 and mode != "holo":
        nseg = 120
        for i in range(nseg):
            a0d, a1d = i * 360 / nseg - 0.4, (i + 1) * 360 / nseg + 0.4
            fr.append(f'<path d="{arc_d(CX, CY, R - 1.2, a0d, a1d)}" stroke="{irid(i / nseg * 2)}" stroke-width="1.7" fill="none"/>')
    body.append(f'<g mask="url(#{uid}-gapb)">{bez}<g opacity="{0.8 * fringe:.2f}">{"".join(fr)}</g></g>')
    defs.append(mask(f"{uid}-gapb", gap_mask))
    return "".join(defs), "".join(body)

def sun_rays(c, lw=1.0):
    d1 = ticks_d(CX, CY, 131, 156, [a for a in range(0, 360, 2) if a % 4 == 0])
    d2 = ticks_d(CX, CY, 131, 146, [a for a in range(0, 360, 2) if a % 4 == 2])
    d3 = ticks_d(CX, CY, 131, 166, LAW_DEG)
    return (f'<path d="{d1}" stroke="{c}" stroke-width="{0.6 * lw}" fill="none"/>'
            f'<path d="{d2}" stroke="{c}" stroke-width="{0.45 * lw}" fill="none"/>'
            f'<path d="{d3}" stroke="{c}" stroke-width="{1.3 * lw}" fill="none"/>')

def limb(c, rot=0.0, ticks=1.0, lw=1.0, nums=True):
    o = []
    o.append(circ(CX, CY, 483, c, 0.7 * lw) + circ(CX, CY, 477, c, 2.4 * lw) + circ(CX, CY, 467, c, 0.6 * lw)
             + circ(CX, CY, 452, c, 0.6 * lw) + circ(CX, CY, 426, c, 0.7 * lw))
    nt = int(round(360 * ticks))
    d1 = ticks_d(CX, CY, 467, 477, [a - 90 for a in range(nt) if a % 5])
    d5 = ticks_d(CX, CY, 459, 477, [a - 90 for a in range(nt) if a % 5 == 0 and a % 10])
    d10 = ticks_d(CX, CY, 452, 477, [a - 90 for a in range(nt) if a % 10 == 0])
    g = (f'<path d="{d1}" stroke="{c}" stroke-width="{0.6 * lw}" fill="none"/>'
         f'<path d="{d5}" stroke="{c}" stroke-width="{0.85 * lw}" fill="none"/>'
         f'<path d="{d10}" stroke="{c}" stroke-width="{1.15 * lw}" fill="none"/>')
    if nums:
        nd = ""
        for a in range(0, 360, 30):
            if a >= nt and ticks < 1: continue
            fl = 0 < ((a - 90) % 360) < 180
            nd += label_on_arc(f"{a:03d}", MONOR, 13.5, CX, CY, 434 + (0.698 * 13.5 if fl else 0), a - 90, 0.04, flip=fl)
        dots = "".join(f'<circle cx="{f2(polar(CX, CY, 439, a - 90)[0])}" cy="{f2(polar(CX, CY, 439, a - 90)[1])}" r="1.25"/>'
                       for a in range(10, 360, 10) if a % 30 and (a < nt or ticks >= 1))
        g += f'<path d="{nd}" fill="{c}"/><g fill="{c}">{dots}</g>'
    o.append(f'<g transform="rotate({rot:.3f} {CX} {CY})">{g}</g>' if rot else g)
    return "".join(o)

def law_band(c, lw=1.0, micro=True, ink_op=1.0):
    o = [circ(CX, CY, 404, c, 0.6 * lw)]
    lab = ""
    spans = []
    for k, th in enumerate(LAW_DEG):
        t = f"{ROM[k]} · {LEIS[k].upper()}"
        size, tr = 10.2, 0.26
        w = text_width(t, MONO, size, tr)
        flip = 0 < (th % 360) < 180
        rb = 411.4 if not flip else 411.4 + 0.698 * size
        lab += label_on_arc(t, MONO, size, CX, CY, rb, th, tr, flip=flip)
        half = math.degrees(w / 2 / 415) + 2.2
        spans.append((th - half, th + half))
    o.append(f'<path d="{lab}" fill="{c}"/>')
    # pontos-guia entre os nomes
    dots = []
    for k in range(7):
        a0 = spans[k][1]; a1 = spans[(k + 1) % 7][0] + (360 if k == 6 else 0)
        a = a0 + 1.0
        while a < a1 - 0.6:
            x, y = polar(CX, CY, 415, a); dots.append(f'<circle cx="{f2(x)}" cy="{f2(y)}" r="0.75"/>'); a += 1.5
    o.append(f'<g fill="{c}">{"".join(dots)}</g>')
    if micro:
        mt = " · ".join(l.upper() for l in LEIS) + " · "
        o.append(f'<path d="{text_on_circle(mt, MONO, 5.3, CX, CY, 398.4, -90, 0.08, fill_circle=True)}" fill="{c}"/>')
        o.append(circ(CX, CY, 396.2, c, 0.45 * lw))
    return "".join(o)

def construction(c, lw=1.0):
    o = []
    o.append(circ(CX, CY, 336, c, 0.45 * lw, 'stroke-dasharray="1.5 4"'))
    # cota angular entre III e IV (360/7): o texto interrompe a linha de cota
    a0, a1 = LAW_DEG[2], LAW_DEG[3]
    R = 334
    mid = (a0 + a1) / 2
    size = 7.6
    half = math.degrees((text_width(SEPT, MONO, size, 0.06) / 2 + 5) / R)
    for x0, x1 in ((a0 + .5, mid - half), (mid + half, a1 - .5)):
        o.append(f'<path d="{arc_d(CX, CY, R, x0, x1)}" stroke="{c}" stroke-width="{0.5 * lw}" fill="none"/>')
    for a, s in ((a0, 1), (a1, -1)):
        tip = polar(CX, CY, R, a)
        b1 = polar(CX, CY, R - 2.6, a + s * 2.0); b2 = polar(CX, CY, R + 2.6, a + s * 2.0)
        o.append(f'<path d="M{P(*tip)} L{P(*b1)} L{P(*b2)} Z" fill="{c}"/>')
        o.append(f'<path d="M{P(*polar(CX, CY, R - 8, a))} L{P(*polar(CX, CY, R_CAP - 24, a))}" stroke="{c}" stroke-width="{0.45 * lw}" fill="none"/>')
    o.append(f'<path d="{label_on_arc(SEPT, MONO, size, CX, CY, R + 0.698 * size / 2, mid, 0.06, flip=True)}" fill="{c}"/>')
    # marcas de registro nos quatro pontos cardeais (fora do limbo)
    rm = ""
    for a in (0, 90, 180, 270):
        rm += f"M{P(*polar(CX, CY, 487, a))} L{P(*polar(CX, CY, 497, a))} "
    o.append(f'<path d="{rm}" stroke="{c}" stroke-width="{0.7 * lw}" fill="none"/>')
    return "".join(o)

def emblem(c=INK, uid="C", mode="ink", detail=2, lw=1.0, limb_rot=0.0, ticks=1.0, rete_rot=0.0,
           focus=1.0, crack=1.0, sword_rot=0.0, beam=-7.0, show=None, accent=None, fringe=1.0,
           plate_op=None, rings=None, lens_mode=None):
    """Astrolábio frontal (viewBox 1000×1000). mode 'ink' (transparente) ou 'foil' (sobre obsidiana).
    show: dict com opacidades de partes para animação."""
    sh = {"limb": 1, "band": 1, "plate": 1, "rete": 1, "sun": 1, "lens": 1, "sword": 1, "cons": 1, "gauge": 1}
    if show: sh.update(show)
    accent = accent or c
    defs, body = [], []
    sw_items, sw_eng, (gx, gy), ends = sword_items(sword_rot, beam, lw)
    rt_items = rete_items(rete_rot, lw)
    gap = 5.0
    knock_sword = knock_items(sw_items, gap) if sh["sword"] > 0 else ""
    knock_rete = knock_items(rt_items, 3.2) if sh["rete"] > 0 else ""
    lens_knock = f'<circle cx="{CX}" cy="{CY}" r="{126 + 3}" fill="black"/>' if sh["lens"] > 0 else ""
    defs.append(mask(f"{uid}-mfg", knock_sword))
    defs.append(mask(f"{uid}-mg", knock_items(sw_items, 2.6) if sh["sword"] > 0 else ""))
    defs.append(mask(f"{uid}-mbg", knock_sword + knock_rete + lens_knock))
    defs.append(f'<clipPath id="{uid}-plate"><circle cx="{CX}" cy="{CY}" r="{R_CAP - 6}"/></clipPath>')
    defs.append(mask(f"{uid}-eng", knock_items(sw_eng, 0) if True else ""))
    # 1) lâmina do tímpano (linhas de projeção) — fundo
    if detail >= 1 and sh["plate"] > 0:
        pl, zen = plate_lines()
        po = plate_op if plate_op is not None else (0.42 if mode == "ink" else 0.5)
        g = []
        for _, x, y, r, w, dash in pl:
            g.append(circ(x, y, r, c, w * lw, 'stroke-dasharray="3 3"' if dash else ""))
        for rr in (R_EQ, R_CAN):
            g.append(circ(CX, CY, rr, c, 0.6 * lw))
        g.append(f'<path d="M{CX - R_CAP},{CY} L{CX + R_CAP},{CY}" stroke="{c}" stroke-width="{0.5 * lw}" stroke-dasharray="6 3 1 3"/>')
        body.append(f'<g mask="url(#{uid}-mbg)" opacity="{po * sh["plate"]:.3f}"><g clip-path="url(#{uid}-plate)">{"".join(g)}</g></g>')
    # 2) limbo + faixa das leis + construção
    if sh["limb"] > 0:
        body.append(f'<g opacity="{sh["limb"]:.3f}">{limb(c, limb_rot, ticks, lw)}</g>')
    if sh["band"] > 0:
        body.append(f'<g mask="url(#{uid}-mbg)" opacity="{sh["band"]:.3f}">{law_band(c, lw, micro=detail >= 2)}</g>')
    if sh["cons"] > 0 and detail >= 1:
        body.append(f'<g mask="url(#{uid}-mbg)" opacity="{sh["cons"]:.3f}">{construction(c, lw)}</g>')
    # 3) raios do sol (mostrador "soleil")
    if sh["sun"] > 0:
        body.append(f'<g mask="url(#{uid}-mbg)" opacity="{sh["sun"]:.3f}">{sun_rays(c, lw)}</g>')
    # 4) rete
    if sh["rete"] > 0:
        rete = draw_items(rt_items, c)
        lz = lozenge_engrave(rete_rot)
        defs.append(mask(f"{uid}-lz", knock_items(lz, 0)))
        body.append(f'<g mask="url(#{uid}-mfg)" opacity="{sh["rete"]:.3f}"><g mask="url(#{uid}-lz)">{rete}</g></g>')
    # 5) lente
    if sh["lens"] > 0:
        ld, lb = lens(uid + "L", c, lens_mode or mode, crack, rings or (34 if detail >= 2 else 16), knock_sword, focus, fringe)
        defs.append(ld)
        body.append(f'<g opacity="{sh["lens"]:.3f}">{lb}</g>')
    # 6) espada-balança + medidor de inclinação
    if sh["gauge"] > 0:
        body.append(f'<g mask="url(#{uid}-mg)" opacity="{sh["gauge"]:.3f}">{tilt_gauge(gx, gy, beam, c, lw, accent)}</g>')
    if sh["sword"] > 0:
        body.append(f'<g mask="url(#{uid}-eng)" opacity="{sh["sword"]:.3f}">{draw_items(sw_items, c)}</g>')
    return "".join(defs), "".join(body)

# ------------------------------------------------------------------ logotipo
def ruler(x0, x1, y, c, lw=1.0, majors=7, minors=10, down=True, labels=True, size=9.0, acc=None):
    """Régua graduada: 'majors' intervalos, 'minors' subdivisões; números 0..majors em Plex Mono."""
    sg = 1 if down else -1
    o = [f'<path d="M{x0:.2f},{y:.2f} L{x1:.2f},{y:.2f}" stroke="{c}" stroke-width="{0.8 * lw}"/>']
    n = majors * minors
    d = ""
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        L = 15 if i % minors == 0 else (8 if i % (minors // 2) == 0 else 4.5)
        d += f"M{x:.2f},{y:.2f} L{x:.2f},{y + sg * L:.2f} "
    o.append(f'<path d="{d}" stroke="{c}" stroke-width="{0.7 * lw}" fill="none"/>')
    if labels:
        for k in range(majors + 1):
            x = x0 + (x1 - x0) * k / majors
            o.append(f'<path d="{text_path(str(k), MONO, size, x + 3, y + sg * (15 + size * .2) + (size * .7 if down else 0) - (0 if down else 0), 0, "start")}" fill="{acc or c}"/>')
    return "".join(o)

def wordmark(c=INK, uid="Cw", w=1400, acc=None, sub=True):
    """'Leis para' (itálico) / 'Matar Deuses' / régua / 'VOLUME I · O DEUS QUE CAIU DO CÉU'."""
    cx = w / 2
    acc = acc or c
    o = []
    o.append(f'<path d="{text_path("Leis para", ISI, 78, cx, 92, 0.0, "middle")}" fill="{c}"/>')
    T = "Matar Deuses"; size = 226
    tw = text_width(T, IS, size, -0.005)
    o.append(f'<path d="{text_path(T, IS, size, cx, 292, -0.005, "middle")}" fill="{c}"/>')
    x0, x1 = cx - tw / 2, cx + tw / 2
    o.append(ruler(x0, x1, 334, c, 1.0, 7, 10, True, True, 9.5, acc))
    # marcas de registro nas pontas da régua
    for x in (x0 - 26, x1 + 26):
        o.append(f'<path d="M{x - 7:.2f},334 L{x + 7:.2f},334 M{x:.2f},327 L{x:.2f},341" stroke="{c}" stroke-width=".8"/>'
                 f'<circle cx="{x:.2f}" cy="334" r="3.6" fill="none" stroke="{c}" stroke-width=".7"/>')
    if sub:
        o.append(f'<path d="{text_path("VOLUME I · O DEUS QUE CAIU DO CÉU", MONOR, 22, cx, 410, 0.42, "middle")}" fill="{c}"/>')
    return "", "".join(o), 440

# ------------------------------------------------------------------ sinais das leis (figuras de tratado)
def arrow(x, y, deg, c, L=9.0, W=3.4):
    a = math.radians(deg); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    bx, by = x - ux * L, y - uy * L
    return f'<path d="M{P(x, y)} L{P(bx + nx * W, by + ny * W)} L{P(bx + ux * L * .25, by + uy * L * .25)} L{P(bx - nx * W, by - ny * W)} Z" fill="{c}"/>'

def formula(parts, cx, y, c):
    """parts: [(texto, fonte, tamanho, dy)] composto lado a lado e centrado."""
    ws = [text_width(t, f, z) for t, f, z, _ in parts]
    x = cx - sum(ws) / 2; o = ""
    for (t, f, z, dy), w in zip(parts, ws):
        o += f'<path d="{text_path(t, f, z, x, y + dy)}" fill="{c}"/>'; x += w
    return o

def fig_frame(c, acc, num, lw=1.0):
    o = [f'<rect x="0" y="0" width="300" height="300" fill="none" stroke="{c}" stroke-width="{0.9 * lw}"/>']
    d = ""
    for k in range(1, 30):
        L = 7 if k % 5 == 0 else 3.5
        d += f"M{k * 10},300 L{k * 10},{300 - L} M0,{k * 10} L{L},{k * 10} "
    o.append(f'<path d="{d}" stroke="{c}" stroke-width="{0.5 * lw}" fill="none"/>')
    cm = ""
    for x, y, sx, sy in ((0, 0, -1, -1), (300, 0, 1, -1), (0, 300, -1, 1), (300, 300, 1, 1)):
        cm += f"M{x + sx * 6},{y} L{x + sx * 18},{y} M{x},{y + sy * 6} L{x},{y + sy * 18} "
    o.append(f'<path d="{cm}" stroke="{c}" stroke-width="{0.6 * lw}" fill="none"/>')
    o.append(f'<path d="{text_path(num, MONOR, 13, 18, 30, 0.12)}" fill="{acc}"/>')
    o.append(f'<path d="M150,{150 - 6} L150,{150 + 6} M{150 - 6},150 L{150 + 6},150" stroke="{c}" stroke-width="0.4" opacity=".6"/>')
    return "".join(o)

def law_figure(i, c, acc, lw=1.0):
    S = lambda w: w * lw
    o = []
    if i == 0:   # Conservação: canal fechado, fluxo circulante
        o.append(circ(150, 150, 92, c, S(1.5)) + circ(150, 150, 66, c, S(1.5)))
        o.append(circ(150, 150, 79, c, S(0.5), 'stroke-dasharray="2 3"'))
        for a in (-90, 30, 150):
            x, y = polar(150, 150, 79, a + 8); o.append(arrow(x, y, a + 8 + 90, c, 11, 4.2))
        o.append(circ(150, 150, 108, c, S(0.45), 'stroke-dasharray="1 4"'))
        o.append(f'<path d="{ticks_d(150, 150, 92, 98, range(0, 360, 10))}" stroke="{c}" stroke-width="{S(.5)}" fill="none"/>')
        o.append(f'<circle cx="150" cy="150" r="3" fill="{c}"/>')
        f = [("ΔE = 0", GARI, 26, 0)]
    elif i == 1:   # Vínculo: dois nós ligados por mola (sete espiras)
        for x in (62, 238):
            o.append(circ(x, 150, 20, c, S(1.5)) + f'<circle cx="{x}" cy="150" r="7.5" fill="{c}"/>')
        pts = []; n = 7; x0, x1 = 98, 202
        for k in range(0, 901):
            t = k / 900
            pts.append((x0 + (x1 - x0) * t - 6.5 * math.sin(2 * math.pi * n * t), 150 - 17 * math.sin(2 * math.pi * n * t)))
        o.append(f'<path d="M82,150 L{x0},150 M{x1},150 L218,150" stroke="{c}" stroke-width="{S(1.4)}"/>')
        o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="{S(1.1)}"/>')
        # cota do comprimento
        o.append(f'<path d="M62,96 L62,124 M238,96 L238,124" stroke="{c}" stroke-width="{S(.5)}"/>')
        o.append(f'<path d="M70,104 L138,104 M162,104 L230,104" stroke="{c}" stroke-width="{S(.6)}"/>')
        o.append(arrow(63, 104, 180, c, 8, 2.8) + arrow(237, 104, 0, c, 8, 2.8))
        o.append(f'<path d="{text_path("x", GARI, 22, 150, 110, 0, "middle")}" fill="{c}"/>')
        o.append(f'<path d="M40,196 L260,196" stroke="{c}" stroke-width="{S(.5)}" stroke-dasharray="4 3"/>')
        f = [("F = −k x", GARI, 26, 0)]
    elif i == 2:   # Compatibilidade: duas ondas em fase
        lam = 72
        for y0, w in ((112, 1.5), (192, 1.5)):
            o.append(f'<path d="{wave_band(42, 258, y0, 24, lam, -math.pi / 2 + 2 * math.pi * 6 / lam, 1.5)}" fill="none" stroke="{c}" stroke-width="{S(w)}"/>')
        for k in range(4):
            x = 42 + 30 + k * lam - 0
            x = 48 + k * lam
        crest = [42 + lam / 4 - 6 + k * lam for k in range(3)]
        crest = []
        for k in range(-1, 5):
            x = 42 - 6 + k * lam + 0
            if 42 <= x <= 258: crest.append(x)
        for x in crest:
            o.append(f'<path d="M{x:.1f},74 L{x:.1f},236" stroke="{c}" stroke-width="{S(.5)}" stroke-dasharray="2 3"/>')
        x0, x1 = crest[0], crest[1]
        o.append(f'<path d="M{x0 + 2:.1f},62 L{x1 - 2:.1f},62" stroke="{c}" stroke-width="{S(.6)}"/>' + arrow(x0, 62, 180, c, 8, 2.8) + arrow(x1, 62, 0, c, 8, 2.8))
        o.append(f'<path d="{text_path("λ", GARI, 20, (x0 + x1) / 2, 56, 0, "middle")}" fill="{c}"/>')
        f = [("Δφ = 0", GARI, 26, 0)]
    elif i == 3:   # Vazão: escoamento por um orifício, linhas de corrente
        hid = f"hz{id(o) % 10000}"
        o.append(f'<clipPath id="{hid}"><rect x="142" y="44" width="16" height="88"/><rect x="142" y="168" width="16" height="88"/></clipPath>')
        o.append(f'<rect x="142" y="44" width="16" height="88" fill="none" stroke="{c}" stroke-width="{S(1.4)}"/>'
                 f'<rect x="142" y="168" width="16" height="88" fill="none" stroke="{c}" stroke-width="{S(1.4)}"/>')
        hatch = "".join(f"M{130 + k * 5},{40} L{130 + k * 5 + 40},{80} " for k in range(-10, 60))
        hatch = "".join(f"M138,{y} L162,{y - 24} " for y in range(44, 290, 5))
        o.append(f'<path d="{hatch}" stroke="{c}" stroke-width="{S(.5)}" clip-path="url(#{hid})"/>')
        n = 9
        for k in range(n):
            u = (k - (n - 1) / 2) / ((n - 1) / 2)
            y0 = 150 + u * 82; yo = 150 + u * 11; y1 = 150 + u * 40
            o.append(f'<path d="M38,{y0:.1f} C102,{y0:.1f} 122,{yo:.1f} 150,{yo:.1f} C178,{yo:.1f} 214,{y1:.1f} 262,{y1:.1f}" fill="none" stroke="{c}" stroke-width="{S(0.9 if k != (n - 1) // 2 else 1.3)}"/>')
            if k in (1, 4, 7):
                o.append(arrow(70, y0 + (yo - y0) * 0.04, 0, c, 8, 3))
                o.append(arrow(244, y1 - (y1 - yo) * 0.02, 0, c, 8, 3))
        f = [("Q = A · v", GARI, 26, 0)]
    elif i == 4:   # Dissipação: espiral que perde amplitude
        b = math.log(100 / 5.5) / (9 * math.pi)
        pts = []
        for k in range(0, 1801):
            th = 9 * math.pi * k / 1800
            r = 100 * math.exp(-b * th)
            pts.append((150 + r * math.cos(th - math.pi / 2 * 0 + math.pi), 150 + r * math.sin(th + math.pi)))
        o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="{S(1.3)}"/>')
        o.append(circ(150, 150, 100, c, S(.5), 'stroke-dasharray="2 3"'))
        o.append(f'<path d="M40,150 L260,150" stroke="{c}" stroke-width="{S(.5)}"/>')
        # marcas de amplitude decrescente sobre o eixo
        tk = ""
        for k in range(0, 9):
            r = 100 * math.exp(-b * k * math.pi)
            x = 150 - r if k % 2 == 0 else 150 + r
            tk += f"M{x:.1f},143 L{x:.1f},157 "
        o.append(f'<path d="{tk}" stroke="{c}" stroke-width="{S(.7)}"/>')
        ex, ey = pts[-1]; px, py = pts[-12]
        o.append(arrow(ex, ey, math.degrees(math.atan2(ey - py, ex - px)), c, 7, 2.6))
        f = [("A = A₀ e", GARI, 26, 0), ("−λt", GARI, 16, -11)]
    elif i == 5:   # Capacidade: recipiente graduado com nível
        o.append(f'<path d="M92,58 L100,66 L100,232 Q100,246 114,246 L186,246 Q200,246 200,232 L200,60" fill="none" stroke="{c}" stroke-width="{S(1.5)}"/>')
        gid = f"cp{i}"
        o.append(f'<clipPath id="{gid}"><path d="M101,138 Q150,134 199,138 L199,245 L101,245 Z"/></clipPath>')
        o.append(f'<path d="{"".join(f"M100,{y} L200,{y} " for y in range(140, 246, 4))}" stroke="{c}" stroke-width="{S(.5)}" clip-path="url(#{gid})"/>')
        o.append(f'<path d="M101,138 Q150,132 199,138" fill="none" stroke="{c}" stroke-width="{S(1.2)}"/>')
        tk = ""
        for k, y in enumerate(range(236, 70, -8)):
            L = 14 if k % 5 == 0 else 7
            tk += f"M100,{y} L{100 + L},{y} "
        o.append(f'<path d="{tk}" stroke="{c}" stroke-width="{S(.6)}"/>')
        o.append(f'<path d="M86,76 L214,76" stroke="{c}" stroke-width="{S(.6)}" stroke-dasharray="5 3"/>')
        o.append(f'<path d="M222,76 L222,136" stroke="{c}" stroke-width="{S(.5)}"/>' + arrow(222, 77, -90, c, 7, 2.6) + arrow(222, 136, 90, c, 7, 2.6))
        o.append(f'<path d="M206,138 L232,138" stroke="{c}" stroke-width="{S(.5)}"/>')
        o.append(f'<path d="M206,138 l-9,-5 l0,10 Z" fill="{c}"/>')
        f = [("V ≤ C", GARI, 26, 0)]
    else:   # Retorno: trajetória que volta à origem (cardioide com cúspide em O)
        a = 84; ox, oy = 72, 150
        pts = []
        for k in range(0, 721):
            th = math.pi + 2 * math.pi * k / 720
            r = a * (1 + math.cos(th))
            pts.append((ox + r * math.cos(th), oy + r * math.sin(th)))
        o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="{S(1.4)}"/>')
        for kk in (150, 360, 570):
            x, y = pts[kk]; px, py = pts[kk - 4]
            o.append(arrow(x, y, math.degrees(math.atan2(y - py, x - px)), c, 10, 3.8))
        o.append(f'<path d="M{ox - 30},{oy} L{ox + 200},{oy}" stroke="{c}" stroke-width="{S(.5)}" stroke-dasharray="4 3"/>')
        o.append(circ(ox, oy, 7, c, S(1.0)) + f'<circle cx="{ox}" cy="{oy}" r="2.4" fill="{c}"/>')
        o.append(f'<path d="{text_path("O", GARI, 18, ox - 13, oy - 9, 0, "end")}" fill="{c}"/>')
        f = [("r(T) = r(0)", GARI, 26, 0)]
    return "".join(o), f

def law_plate(i, c=INK, acc=BRASS, lw=1.0):
    fig, f = law_figure(i, c, acc, lw)
    o = fig_frame(c, acc, ROM[i], lw) + fig
    o += f'<path d="{text_path(LEIS[i], IS, 42, 150, 358, 0.0, "middle")}" fill="{c}"/>'
    o += formula(f, 150, 398, c)
    return o

def law_sheet(c, acc, bg):
    W, H = 1480, 1080
    body = []
    for i in range(7):
        r, k = divmod(i, 4)
        x = 80 + k * 340 if r == 0 else 80 + 170 + k * 340
        y = 80 + r * 490
        body.append(f'<g transform="translate({x} {y})">{law_plate(i, c, acc)}</g>')
    return svg(W, H, "".join(body), bg=bg)

# ------------------------------------------------------------------ princípios: mostradores
def dial(name, c, acc, uid, lw=1.0):
    cx = cy = 150; R = 118
    S = lambda w: w * lw
    o = [circ(cx, cy, R, c, S(1.8)), circ(cx, cy, R - 5, c, S(0.5))]
    defs = f'<clipPath id="{uid}"><circle cx="{cx}" cy="{cy}" r="{R - 14}"/></clipPath>'
    inner = []
    def needle(deg, r1, r0=-14, w=1.4, col=None):
        col = col or c
        x1, y1 = polar(cx, cy, r1, deg); x0, y0 = polar(cx, cy, r0, deg)
        return (f'<path d="M{P(x0, y0)} L{P(x1, y1)}" stroke="{col}" stroke-width="{S(w)}" stroke-linecap="round"/>'
                f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="{col}"/><circle cx="{cx}" cy="{cy}" r="1.8" fill="{OBS}"/>')
    if name != "Carga" and name != "Brasa":
        o.append(f'<path d="{ticks_d(cx, cy, R - 12, R - 5, [a for a in range(0, 360, 6) if a % 30])}" stroke="{c}" stroke-width="{S(.5)}" fill="none"/>')
        o.append(f'<path d="{ticks_d(cx, cy, R - 15, R - 5, range(0, 360, 30))}" stroke="{c}" stroke-width="{S(.9)}" fill="none"/>')
    if name == "Pulso":       # osciloscópio: trem de pulsos sobre retícula
        g = "".join(f"M{x},40 L{x},260 " for x in range(50, 260, 20)) + "".join(f"M40,{y} L260,{y} " for y in range(50, 260, 20))
        inner.append(f'<path d="{g}" stroke="{c}" stroke-width="{S(.35)}" opacity=".55"/>')
        inner.append(f'<path d="M30,150 L270,150 M150,30 L150,270" stroke="{c}" stroke-width="{S(.6)}" opacity=".8"/>')
        tk = "".join(f"M{x},147 L{x},153 " for x in range(30, 271, 4))
        inner.append(f'<path d="{tk}" stroke="{c}" stroke-width="{S(.35)}" opacity=".8"/>')
        pts = []; x = 30.0
        while x < 272:
            ph = (x - 30) % 52
            if ph < 22: y = 172
            elif ph < 25: y = 172 - (ph - 22) / 3 * 92
            elif ph < 29: y = 80 + (ph - 25) / 4 * 112
            elif ph < 33: y = 192 - (ph - 29) / 4 * 20
            else: y = 172
            pts.append((x, y)); x += 0.5
        inner.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="{S(1.4)}" stroke-linejoin="round"/>')
    elif name == "Brasa":     # termômetro de mostrador: 270°, zona quente em acento
        a0, a1 = 135, 405
        o.append(f'<path d="{arc_d(cx, cy, R - 18, a0, a1)}" stroke="{c}" stroke-width="{S(.6)}" fill="none"/>')
        tk = ""
        for k in range(0, 55):
            a = a0 + (a1 - a0) * k / 54
            L = 13 if k % 9 == 0 else 6
            tk += f"M{P(*polar(cx, cy, R - 18, a))} L{P(*polar(cx, cy, R - 18 - L, a))} "
        o.append(f'<path d="{tk}" stroke="{c}" stroke-width="{S(.6)}" fill="none"/>')
        hz = "".join(f"M{P(*polar(cx, cy, R - 8, a))} L{P(*polar(cx, cy, R - 16, a + 3))} " for a in [a0 + (a1 - a0) * (0.72 + k * 0.0093) for k in range(0, 30)])
        o.append(f'<path d="{hz}" stroke="{acc}" stroke-width="{S(.8)}" fill="none"/>')
        for k in range(0, 7):
            a = a0 + (a1 - a0) * k / 6
            x, y = polar(cx, cy, R - 44, a)
            o.append(f'<path d="{text_path(str(k * 200), MONO, 9, x, y + 3.2, 0, "middle")}" fill="{c}"/>')
        o.append(needle(a0 + (a1 - a0) * 0.86, R - 22, -16, 1.5))
        o.append(f'<path d="{arc_d(cx, cy, 36, 300, 420)}" stroke="{c}" stroke-width="{S(.5)}" fill="none" stroke-dasharray="2 2"/>')
    elif name == "Trama":     # tafetá: urdume e trama alternando por cima e por baixo
        sp, hw = 20, 6.5
        xs = [cx + k * sp for k in range(-6, 7)]
        def vband(x, y0, y1, edges=True):
            r = f'<rect x="{x - hw:.1f}" y="{y0:.1f}" width="{2 * hw:.1f}" height="{y1 - y0:.1f}" fill="{OBS}"/>'
            if edges:
                r += f'<path d="M{x - hw:.1f},{y0:.1f} L{x - hw:.1f},{y1:.1f} M{x + hw:.1f},{y0:.1f} L{x + hw:.1f},{y1:.1f}" stroke="{c}" stroke-width="{S(.8)}"/>'
                r += f'<path d="M{x:.1f},{y0:.1f} L{x:.1f},{y1:.1f}" stroke="{c}" stroke-width="{S(.35)}" opacity=".7"/>'
            return r
        def hband(y, x0, x1):
            return (f'<rect x="{x0:.1f}" y="{y - hw:.1f}" width="{x1 - x0:.1f}" height="{2 * hw:.1f}" fill="{OBS}"/>'
                    f'<path d="M{x0:.1f},{y - hw:.1f} L{x1:.1f},{y - hw:.1f} M{x0:.1f},{y + hw:.1f} L{x1:.1f},{y + hw:.1f}" stroke="{c}" stroke-width="{S(.8)}"/>'
                    f'<path d="M{x0:.1f},{y:.1f} L{x1:.1f},{y:.1f}" stroke="{c}" stroke-width="{S(.35)}" opacity=".7"/>')
        for x in xs: inner.append(vband(x, 20, 280))
        for y in xs: inner.append(hband(y, 20, 280))
        for i, x in enumerate(xs):
            for j, y in enumerate(xs):
                if (i + j) % 2 == 0:
                    inner.append(vband(x, y - hw - 1.2, y + hw + 1.2))
    elif name == "Clarão":    # íris: oito lâminas, clarão na abertura
        n = 8; ra = 34
        poly = [polar(cx, cy, ra, k * 360 / n + 11) for k in range(n)]
        for k in range(n):
            p0 = polar(cx, cy, R - 14, k * 360 / n - 58)
            p1 = poly[k]
            inner.append(f'<path d="M{P(*p0)} A{R * .78:.1f},{R * .78:.1f} 0 0 1 {P(*p1)}" fill="none" stroke="{c}" stroke-width="{S(1.0)}"/>')
            q0 = polar(cx, cy, R - 14, k * 360 / n - 50)
            inner.append(f'<path d="M{P(*q0)} A{R * .8:.1f},{R * .8:.1f} 0 0 1 {P(*polar(cx, cy, ra + 16, k * 360 / n + 9))}" fill="none" stroke="{c}" stroke-width="{S(.45)}"/>')
        inner.append(f'<path d="{polyline(poly, True)}" fill="none" stroke="{c}" stroke-width="{S(1.2)}"/>')
        rays = "".join(f"M{P(*polar(cx, cy, 4, a))} L{P(*polar(cx, cy, 30 if a % 15 == 0 else 20, a))} " for a in range(0, 360, 5))
        inner.append(f'<path d="{rays}" stroke="{c}" stroke-width="{S(.55)}"/>')
    elif name == "Eco":       # sonar: anéis de alcance, varredura e retornos
        for r in range(20, 104, 20):
            inner.append(circ(cx, cy, r, c, S(.5), 'stroke-dasharray="2 3"' if r % 40 else ""))
        for k in range(30):
            a = -40 - k * 1.6
            x, y = polar(cx, cy, 104, a)
            inner.append(f'<path d="M{cx},{cy} L{P(x, y)}" stroke="{c}" stroke-width="{S(.6)}" opacity="{(1 - k / 30) ** 2 * .7:.3f}"/>')
        x, y = polar(cx, cy, 104, -40)
        inner.append(f'<path d="M{cx},{cy} L{P(x, y)}" stroke="{c}" stroke-width="{S(1.3)}"/>')
        for r, a, sp in ((64, -58, 9), (86, -70, 6), (42, -120, 7)):
            for j in range(3):
                inner.append(f'<path d="{arc_d(cx, cy, r + j * 4.5, a - sp, a + sp)}" stroke="{c}" stroke-width="{S(1.1 - j * .3)}" fill="none" opacity="{1 - j * .3:.2f}"/>')
        inner.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{c}"/>')
    elif name == "Carga":     # voltímetro de quadrante com espelho + curva de carga
        a0, a1 = -145, -35
        for rr, w in ((R - 22, .6), (R - 30, .5)):
            o.append(f'<path d="{arc_d(cx, cy, rr, a0, a1)}" stroke="{c}" stroke-width="{S(w)}" fill="none"/>')
        tk = ""
        for k in range(0, 51):
            a = a0 + (a1 - a0) * k / 50
            L = 14 if k % 5 == 0 else 7
            tk += f"M{P(*polar(cx, cy, R - 22, a))} L{P(*polar(cx, cy, R - 22 - L, a))} "
        o.append(f'<path d="{tk}" stroke="{c}" stroke-width="{S(.6)}" fill="none"/>')
        for k in range(0, 11, 2):
            a = a0 + (a1 - a0) * k / 10
            x, y = polar(cx, cy, R - 12, a)
            o.append(f'<path d="{label_on_arc(str(k), MONO, 9, cx, cy, R - 14, a, 0, flip=False)}" fill="{c}"/>')
        o.append(f'<path d="{arc_d(cx, cy, R - 30, a0 + (a1 - a0) * 0.8, a1)}" stroke="{acc}" stroke-width="{S(3)}" fill="none"/>')
        o.append(needle(a0 + (a1 - a0) * 0.92, R - 24, 0, 1.4))
        # curva de carga 1 − e^(−t)
        gx, gy, gw, gh = 92, 222, 116, 52
        o.append(f'<path d="M{gx},{gy - gh} L{gx},{gy} L{gx + gw},{gy}" stroke="{c}" stroke-width="{S(.7)}" fill="none"/>')
        pts = [(gx + gw * t / 100, gy - gh * (1 - math.exp(-t / 22))) for t in range(0, 101)]
        o.append(f'<path d="{polyline(pts)}" fill="none" stroke="{c}" stroke-width="{S(1.3)}"/>')
        o.append(f'<path d="M{gx},{gy - gh} L{gx + gw},{gy - gh}" stroke="{c}" stroke-width="{S(.45)}" stroke-dasharray="3 3"/>')
    o.insert(2, f'<g clip-path="url(#{uid})">{"".join(inner)}</g>')
    o.append(f'<path d="{text_path(name, IS, 36, cx, cy + R + 52, 0, "middle")}" fill="{c}"/>')
    return defs, "".join(o)

def principles_sheet(c, acc, bg):
    W, H = 2020, 420
    defs, body = "", ""
    for k, nm in enumerate(PRINC):
        d, b = dial(nm, c, acc, f"pd{k}")
        defs += d; body += f'<g transform="translate({60 + k * 320} 30)">{b}</g>'
    return svg(W, H, body, defs, bg=bg)

# ------------------------------------------------------------------ guarda: carta celeste
ASTER = [(0, -236), (0, -118), (-158, -98.6), (158, -137.4), (-158, 30), (158, -10), (0, 262)]   # o brasão como asterismo
ASTER_MAG = [4.2, 7.0, 4.8, 4.8, 3.6, 3.6, 5.4]
ASTER_LINKS = [(0, 1), (1, 6), (2, 1), (1, 3), (2, 4), (3, 5)]

def asterism(ox, oy, c, acc, sc=1.0, lw=1.0):
    pts = [(ox + x * sc, oy + y * sc) for x, y in ASTER]
    o = []
    for a, b in ASTER_LINKS:
        (x0, y0), (x1, y1) = pts[a], pts[b]
        L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
        g0 = ASTER_MAG[a] * sc + 7; g1 = ASTER_MAG[b] * sc + 7
        o.append(f'<path d="M{P(x0 + ux * g0, y0 + uy * g0)} L{P(x1 - ux * g1, y1 - uy * g1)}" stroke="{c}" stroke-width="{0.9 * lw}"/>')
    # o sol-lente do brasão como círculo tracejado, rachado
    sx, sy = ox, oy + 38 * sc
    o.append(f'<path d="{arc_d(sx, sy, 62 * sc, -58, 212)}" fill="none" stroke="{c}" stroke-width="{0.7 * lw}" stroke-dasharray="3 3"/>')
    o.append(f'<path d="{arc_d(sx + 2.5 * sc, sy - 2 * sc, 62 * sc, 218, 296)}" fill="none" stroke="{c}" stroke-width="{0.7 * lw}" stroke-dasharray="3 3"/>')
    for k, ((x, y), m) in enumerate(zip(pts, ASTER_MAG)):
        o.append(f'<circle cx="{f2(x)}" cy="{f2(y)}" r="{m * sc:.2f}" fill="{acc if k == 1 else c}"/>')
        if k == 1:
            o.append(circ(x, y, m * sc + 4.5, acc, 0.8 * lw))
            o.append(f'<path d="{ticks_d(x, y, m * sc + 7, m * sc + 13, range(0, 360, 45))}" stroke="{acc}" stroke-width="{0.8 * lw}"/>')
    return "".join(o)

def endpaper(W=3200, H=2000, c="#BFC4CB", acc=BRASS, bg=OBS):
    o = []
    # grade de coordenadas (global, contínua)
    g1 = "".join(f"M{x},0 L{x},{H} " for x in range(0, W + 1, 40) if x % 200) + "".join(f"M0,{y} L{W},{y} " for y in range(0, H + 1, 40) if y % 200)
    g2 = "".join(f"M{x},0 L{x},{H} " for x in range(0, W + 1, 200)) + "".join(f"M0,{y} L{W},{y} " for y in range(0, H + 1, 200))
    o.append(f'<path d="{g1}" stroke="{c}" stroke-width=".6" opacity=".09"/>')
    o.append(f'<path d="{g2}" stroke="{c}" stroke-width=".9" opacity=".2"/>')
    tk = "".join(f"M{x},{y - 3} L{x},{y + 3} " for y in range(0, H + 1, 200) for x in range(0, W + 1, 8) if x % 40)
    o.append(f'<path d="{tk}" stroke="{c}" stroke-width=".6" opacity=".22"/>')
    # módulo 800×1000 em meia-gota
    TW, TH = 800, 1000
    rng = random.Random(11)
    stars = [(rng.uniform(0, TW), rng.uniform(0, TH), rng.choice([0.6, 0.7, 0.8, 0.9, 1.1, 1.4, 1.9, 2.4])) for _ in range(150)]
    def tile():
        t = []
        t.append(f'<g transform="rotate(-12 400 500)">'
                 f'<ellipse cx="400" cy="500" rx="318" ry="122" fill="none" stroke="{c}" stroke-width=".8" stroke-dasharray="6 5" opacity=".6"/>'
                 f'<ellipse cx="400" cy="500" rx="252" ry="84" fill="none" stroke="{c}" stroke-width=".6" opacity=".35"/></g>')
        px, py = rotp(400 + 318 * math.cos(2.3), 500 + 122 * math.sin(2.3), 400, 500, -12)
        t.append(f'<circle cx="{f2(px)}" cy="{f2(py)}" r="6" fill="{bg}" stroke="{c}" stroke-width="1"/><circle cx="{f2(px)}" cy="{f2(py)}" r="2" fill="{c}"/>')
        t.append(asterism(400, 500, c, acc, 1.0))
        for x, y, r in stars:
            if math.hypot(x - 400, y - 500) < 30: continue
            t.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" opacity="{0.4 + r / 5:.2f}"/>')
            if r >= 2.4:
                t.append(f'<path d="M{x - 9:.1f},{y:.1f} L{x + 9:.1f},{y:.1f} M{x:.1f},{y - 9:.1f} L{x:.1f},{y + 9:.1f}" stroke="{c}" stroke-width=".5" opacity=".7"/>')
        # pequeno limbo de 360 traços
        lx, ly = 650, 170
        t.append(circ(lx, ly, 52, c, .8) + circ(lx, ly, 40, c, .5))
        t.append(f'<path d="{ticks_d(lx, ly, 46, 52, [a for a in range(0, 360, 5) if a % 30])}" stroke="{c}" stroke-width=".5"/>')
        t.append(f'<path d="{ticks_d(lx, ly, 40, 52, range(0, 360, 30))}" stroke="{c}" stroke-width=".8"/>')
        t.append(f'<path d="{label_on_arc(SEPT, MONO, 6.5, lx, ly, 56, -90, 0.08)}" fill="{acc}"/>')
        for k in range(7):
            x, y = polar(lx, ly, 28, -90 + k * 360 / 7); t.append(f'<circle cx="{f2(x)}" cy="{f2(y)}" r="1.8" fill="{c}"/>')
        t.append(f'<path d="{polyline([polar(lx, ly, 28, -90 + k * 360 / 7 * 3) for k in range(8)])}" fill="none" stroke="{c}" stroke-width=".5"/>')
        # escala de magnitudes
        mx, my = 90, 860
        for k, r in enumerate((6, 4.8, 3.8, 2.8, 1.9, 1.1)):
            t.append(f'<circle cx="{mx + k * 22}" cy="{my}" r="{r}" fill="{c}"/>')
            t.append(f'<path d="{text_path(str(k + 1), MONO, 8, mx + k * 22, my + 20, 0, "middle")}" fill="{c}" opacity=".8"/>')
        return "".join(t)
    # eclíptica contínua (senoide) com graduação, e equador
    ec = [(x, H / 2 + 330 * math.sin(2 * math.pi * x / 3200 + 0.6)) for x in range(-10, W + 11, 4)]
    o.append(f'<path d="{polyline(ec)}" fill="none" stroke="{acc}" stroke-width="1.1" opacity=".75"/>')
    et = ""
    for k in range(0, 3200 // 20 + 1):
        x = k * 20; y = H / 2 + 330 * math.sin(2 * math.pi * x / 3200 + 0.6)
        dy = 330 * 2 * math.pi / 3200 * math.cos(2 * math.pi * x / 3200 + 0.6); n = math.hypot(1, dy)
        L = 9 if k % 5 == 0 else 4.5
        et += f"M{x:.1f},{y:.1f} L{x + dy / n * L:.1f},{y - 1 / n * L:.1f} "
    o.append(f'<path d="{et}" stroke="{acc}" stroke-width=".7" opacity=".75"/>')
    o.append(f'<path d="M0,{H / 2} L{W},{H / 2}" stroke="{c}" stroke-width="1" stroke-dasharray="14 5 2 5" opacity=".45"/>')
    # coordenadas fictícias (globais)
    for j, y in enumerate(range(200, H, 200)):
        dec = (H / 2 - y) / 200 * 10
        lab = ("+" if dec > 0 else "−" if dec < 0 else "") + f"{abs(dec):.0f}°"
        for x in range(0, W, 800):
            o.append(f'<path d="{text_path(lab, MONO, 11, x + 8, y - 6, 0.1)}" fill="{acc}" opacity=".85"/>')
    for i, x in enumerate(range(200, W, 400)):
        lab = f"{(i * 2) % 24:02d}h"
        for y in (H - 10, 22):
            o.append(f'<path d="{text_path(lab, MONO, 11, x + 6, y, 0.1)}" fill="{acc}" opacity=".85"/>')
    T = tile()
    for col in range(-1, W // TW + 1):
        for row in range(-1, H // TH + 2):
            x = col * TW; y = row * TH + (TH / 2 if col % 2 else 0)
            if x > W or y > H or x + TW < 0 or y + TH < 0: continue
            o.append(f'<g transform="translate({x} {y})">{T}</g>')
    return svg(W, H, "".join(o), bg=bg)

# ------------------------------------------------------------------ capa em tecido (hot-stamping)
def cloth_defs(uid="cl", seed=3):
    return (f'<filter id="{uid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.95 0.06" numOctaves="2" seed="{seed}" result="a"/>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.06 0.95" numOctaves="2" seed="{seed + 5}" result="b"/>'
            f'<feBlend in="a" in2="b" mode="multiply" result="ab"/>'
            f'<feColorMatrix in="ab" type="matrix" values="0 0 0 0 0.62  0 0 0 0 0.64  0 0 0 0 0.68  1.1 0 0 0 -0.32" result="w"/>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="2" seed="{seed + 9}" result="m"/>'
            f'<feColorMatrix in="m" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.9 0.62" result="mo"/>'
            f'<feComposite in="w" in2="mo" operator="in"/></filter>')

def stamp_filter(uid="st"):
    return (f'<filter id="{uid}" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="1.1" result="b"/>'
            f'<feOffset in="b" dx="0" dy="1.4" result="o"/><feFlood flood-color="#000" flood-opacity=".85"/>'
            f'<feComposite in2="o" operator="in" result="sh"/>'
            f'<feOffset in="b" dx="0" dy="-0.8" result="o2"/><feFlood flood-color="#9AA0A8" flood-opacity=".18"/>'
            f'<feComposite in2="o2" operator="in" result="hi"/>'
            f'<feMerge><feMergeNode in="sh"/><feMergeNode in="hi"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')

def frame_ruler(W, H, m, c, lw=1.0, step=10):
    """Moldura retangular graduada (régua nas quatro bordas)."""
    o = [f'<rect x="{m}" y="{m}" width="{W - 2 * m}" height="{H - 2 * m}" fill="none" stroke="{c}" stroke-width="{1.8 * lw}"/>',
         f'<rect x="{m + 26}" y="{m + 26}" width="{W - 2 * m - 52}" height="{H - 2 * m - 52}" fill="none" stroke="{c}" stroke-width="{0.8 * lw}"/>']
    d = ""
    x0, x1, y0, y1 = m + 26, W - m - 26, m + 26, H - m - 26
    n = int((x1 - x0) // step)
    off = ((x1 - x0) - n * step) / 2
    for k in range(n + 1):
        x = x0 + off + k * step
        L = 14 if k % 10 == 0 else (9 if k % 5 == 0 else 5)
        d += f"M{x:.1f},{y0} L{x:.1f},{y0 - L} M{x:.1f},{y1} L{x:.1f},{y1 + L} "
    n = int((y1 - y0) // step); off = ((y1 - y0) - n * step) / 2
    for k in range(n + 1):
        y = y0 + off + k * step
        L = 14 if k % 10 == 0 else (9 if k % 5 == 0 else 5)
        d += f"M{x0},{y:.1f} L{x0 - L},{y:.1f} M{x1},{y:.1f} L{x1 + L},{y:.1f} "
    o.append(f'<path d="{d}" stroke="{c}" stroke-width="{0.9 * lw}" fill="none"/>')
    for x, y in ((m, m), (W - m, m), (m, H - m), (W - m, H - m)):
        o.append(circ(x, y, 11, c, 1.1 * lw) + f'<path d="M{x - 18},{y} L{x + 18},{y} M{x},{y - 18} L{x},{y + 18}" stroke="{c}" stroke-width="{0.9 * lw}"/>')
    return "".join(o)

def cover_cloth():
    W, H = 1600, 2300
    ink = "url(#foil)"
    sc = 1.17
    # a lente é o único ponto iridescente (foil holográfico); todo o resto, prata
    ed, eb = emblem(ink, uid="Ct", mode="foil", detail=1, lw=1.7, rings=13, accent=ink, lens_mode="holo", fringe=0)
    dw, wb, wh = wordmark(ink, "Ctw", 1400)
    defs = (silver_grad("foil", 300, 120, 900, 1100) + cloth_defs() + stamp_filter() + ed + dw +
            f'<radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#15171B"/><stop offset="1" stop-color="#060708"/></radialGradient>')
    ecx, ecy = 800, 770
    tr = f"translate({ecx - 500 * sc:.1f} {ecy - 500 * sc:.1f}) scale({sc})"
    body = (f'<rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'<rect width="{W}" height="{H}" filter="url(#cl)" opacity=".55"/>'
            f'<g filter="url(#st)">'
            f'{frame_ruler(W, H, 58, ink, 1.0)}'
            f'<g transform="{tr}">{eb}</g>'
            f'<g transform="translate({(W - 1400 * 0.8) / 2} 1478) scale(0.8)">{wb}</g>'
            f'<path d="{text_path("Werik Martins", IS, 66, W / 2, 1932, 0.01, "middle")}" fill="{ink}"/>'
            f'{ruler(W / 2 - 170, W / 2 + 170, 2052, ink, 1.4, 4, 10, False, False)}'
            f'<path d="{text_path("EDIÇÃO NUMERADA  Nº 0001 / 1187", MONOR, 19, W / 2, 2110, 0.32, "middle")}" fill="{ink}"/>'
            f'</g>'
            f'<rect width="{W}" height="{H}" filter="url(#cl)" opacity=".22" style="mix-blend-mode:multiply"/>')
    return svg(W, H, body, defs)

# ------------------------------------------------------------------ sobrecapa: o instrumento mede a cena
def cover_jacket():
    W, H = 1600, 2300
    art = f"{ART}/capa_arte.jpg"
    S = W / 1536
    dx, dy, dr = 765 * S, 832 * S, 150 * S          # disco luminoso da arte, em coordenadas da capa
    c, acc = "#D9DDE2", BRASS
    dw, wb, wh = wordmark("url(#jf)", "Jw", 1400)
    defs = (silver_grad("jf", 300, 0, 1100, 420) + dw +
            '<filter id="cold" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0.30 0.58 0.12 0 0  0.30 0.58 0.12 0 0  0.30 0.58 0.12 0 0  0 0 0 1 0"/>'
            '<feComponentTransfer><feFuncR type="table" tableValues="0.035 0.10 0.36 0.80 1.0"/>'
            '<feFuncG type="table" tableValues="0.040 0.115 0.385 0.83 1.0"/>'
            '<feFuncB type="table" tableValues="0.050 0.14 0.43 0.87 1.0"/></feComponentTransfer></filter>'
            '<linearGradient id="jt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B0C0E" stop-opacity=".92"/>'
            '<stop offset=".26" stop-color="#0B0C0E" stop-opacity=".55"/><stop offset=".42" stop-color="#0B0C0E" stop-opacity="0"/>'
            '<stop offset=".8" stop-color="#0B0C0E" stop-opacity="0"/><stop offset=".93" stop-color="#0B0C0E" stop-opacity=".7"/><stop offset="1" stop-color="#0B0C0E" stop-opacity=".95"/></linearGradient>'
            '<radialGradient id="jv" cx="50%" cy="42%" r="80%"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>')
    o = [f'<image href="{art}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" filter="url(#cold)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#jt)"/><rect width="{W}" height="{H}" fill="url(#jv)"/>']
    L = []
    # retículo principal sobre o disco (teodolito)
    R1, R2 = dr + 52, dr + 92
    L.append(circ(dx, dy, dr + 14, c, 0.7))
    L.append(circ(dx, dy, R1, c, 0.6, 'stroke-dasharray="2 4"'))
    for a0 in (8, 98, 188, 278):
        L.append(f'<path d="{arc_d(dx, dy, R2, a0, a0 + 74)}" stroke="{c}" stroke-width="1.1" fill="none"/>')
    tk = ""
    for a in range(0, 360):
        if a % 90 in (0, 1, 2, 3, 4, 5, 6, 7) or a % 90 > 82: continue
        Lk = 16 if a % 10 == 0 else (10 if a % 5 == 0 else 5.5)
        tk += f"M{P(*polar(dx, dy, R2, a))} L{P(*polar(dx, dy, R2 + Lk, a))} "
    L.append(f'<path d="{tk}" stroke="{c}" stroke-width=".7" fill="none"/>')
    nd = ""
    for a in range(30, 360, 30):
        if a % 90 == 0: continue
        fl = 0 < ((a - 90) % 360) < 180
        nd += label_on_arc(f"{a:03d}", MONO, 13, dx, dy, R2 + 24 + (0.698 * 13 if fl else 0), a - 90, 0.06, flip=fl)
    L.append(f'<path d="{nd}" fill="{c}"/>')
    # franja iridescente (o único ponto de cor): fina, em volta do disco
    for i in range(90):
        L.append(f'<path d="{arc_d(dx, dy, dr + 7, i * 4 - .3, i * 4 + 4.3)}" stroke="{irid(i / 90 * 2)}" stroke-width="2" fill="none" opacity=".85"/>')
    # cruz do retículo com escala (mil) e interrupção no centro
    gap = R2 + 44
    L.append(f'<path d="M70,{dy:.1f} L{dx - gap:.1f},{dy:.1f} M{dx + gap:.1f},{dy:.1f} L{W - 70},{dy:.1f}" stroke="{c}" stroke-width=".7"/>')
    mt = "".join(f"M{x:.1f},{dy - (7 if (x - dx) % 50 == 0 else 3.5):.1f} L{x:.1f},{dy + (7 if (x - dx) % 50 == 0 else 3.5):.1f} "
                 for x in [dx + k * 10 for k in range(-70, 71)] if abs(x - dx) > gap and 70 < x < W - 70)
    L.append(f'<path d="{mt}" stroke="{c}" stroke-width=".6"/>')
    L.append(f'<path d="M{dx:.1f},{dy - gap:.1f} L{dx:.1f},{dy - gap - 46:.1f} M{dx:.1f},{dy + gap:.1f} L{dx:.1f},{dy + gap + 60:.1f}" stroke="{c}" stroke-width=".7"/>')
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, y0 = dx + sx * (dr + 26), dy + sy * (dr + 26)
            L.append(f'<path d="M{x0:.1f},{y0 - sy * 26:.1f} L{x0:.1f},{y0:.1f} L{x0 - sx * 26:.1f},{y0:.1f}" stroke="{c}" stroke-width="1.2" fill="none"/>')
    # cota do diâmetro do disco
    yy = dy - dr - 26
    # leitura de altitude/azimute com linha de chamada
    lx, ly = dx + R2 + 70, dy - R2 + 10
    p0 = polar(dx, dy, R2 + 2, -52)
    L.append(f'<path d="M{P(*p0)} L{lx - 8:.1f},{ly + 6:.1f} L{lx + 236:.1f},{ly + 6:.1f}" stroke="{c}" stroke-width=".7" fill="none"/>')
    L.append(f'<circle cx="{P(*p0).split(",")[0]}" cy="{P(*p0).split(",")[1]}" r="3" fill="{c}"/>')
    L.append(f'<path d="{text_path("ALT  +61°12′07″", MONO, 15, lx, ly - 22, 0.08)}" fill="{c}"/>')
    L.append(f'<path d="{text_path("AZ  184°06′51″", MONO, 15, lx, ly - 2, 0.08)}" fill="{c}"/>')
    L.append(f'<path d="{text_path("Ø  0°41′18″", MONO, 15, lx, ly + 28, 0.08)}" fill="{acc}"/>')
    # régua de elevação ao longo da torre
    tx = 548
    y_top, y_bot = dy - dr, 2060
    L.append(f'<path d="M{tx},{y_top:.1f} L{tx},{y_bot}" stroke="{c}" stroke-width=".8"/>')
    st = ""
    n = 60
    for k in range(n + 1):
        y = y_bot - (y_bot - y_top) * k / n
        Lk = 14 if k % 10 == 0 else (8 if k % 5 == 0 else 4)
        st += f"M{tx},{y:.1f} L{tx - Lk},{y:.1f} "
        if k % 10 == 0:
            L.append(f'<path d="{text_path(f"{k * 2:03d}", MONO, 12, tx - 20, y + 4, 0.06, "end")}" fill="{c}"/>')
    L.append(f'<path d="{st}" stroke="{c}" stroke-width=".7"/>')
    L.append(f'<path d="M{tx - 6},{y_top:.1f} L{tx + 6},{y_top:.1f} M{tx - 6},{y_bot} L{tx + 6},{y_bot}" stroke="{c}" stroke-width="1.2"/>')
    # feixe de luz: marcador vertical tracejado com coordenada
    bx = 904 * S
    L.append(f'<path d="M{bx + 18:.1f},{dy + dr + 30:.1f} L{bx + 18:.1f},2010" stroke="{c}" stroke-width=".6" stroke-dasharray="3 6"/>')
    for yv in (1300, 1600, 1900):
        L.append(f'<path d="M{bx + 12:.1f},{yv} L{bx + 24:.1f},{yv}" stroke="{c}" stroke-width=".9"/>')
    L.append(f'<path d="{text_path("587,6 nm", MONO, 12, bx + 32, 1604, 0.08)}" fill="{c}"/>')
    # horizonte com escala de azimute
    hy = 1792
    L.append(f'<path d="M70,{hy} L{W - 70},{hy}" stroke="{c}" stroke-width=".6" stroke-dasharray="10 4 2 4" opacity=".9"/>')
    hz = "".join(f"M{x},{hy} L{x},{hy + (10 if x % 100 == 0 else 5)} " for x in range(80, W - 70, 20))
    L.append(f'<path d="{hz}" stroke="{c}" stroke-width=".6"/>')
    for x in range(100, W - 70, 200):
        L.append(f'<path d="{text_path(f"{(x - 100) // 200 * 15 + 135:03d}°", MONO, 11, x + 4, hy + 24, 0.06)}" fill="{c}" opacity=".9"/>')
    # coordenadas fictícias nas margens
    L.append(f'<path d="{text_path("47°58′12″ N", MONO, 13, 78, 1010, 0.08)}" fill="{c}" opacity=".85"/>')
    L.append(f'<path d="{text_path("011°04′40″ E", MONO, 13, W - 78, 1010, 0.08, "end")}" fill="{c}" opacity=".85"/>')
    # moldura de visor: cantos finos
    for x, y, sx, sy in ((60, 60, 1, 1), (W - 60, 60, -1, 1), (60, H - 60, 1, -1), (W - 60, H - 60, -1, -1)):
        L.append(f'<path d="M{x},{y + sy * 46} L{x},{y} L{x + sx * 46},{y}" stroke="{c}" stroke-width="1.2" fill="none"/>')
    o.append(f'<g>{"".join(L)}</g>')
    # título e autor
    o.append(f'<g transform="translate({(W - 1400 * 0.84) / 2:.1f} 150) scale(0.84)">{wb}</g>')
    o.append(f'<path d="{text_path("Werik Martins", IS, 60, W / 2, 2190, 0.01, "middle")}" fill="url(#jf)"/>')
    return svg(W, H, "".join(o), defs)

# ------------------------------------------------------------------ abertura de capítulo
P1 = ("O contrato tinha onze páginas, e Pelle Dorn fazia questão de que Ilan Varek conhecesse cada uma delas "
      "antes de entrar no prédio.")
P2 = ("— Cláusula sétima — leu o agente da seguradora, segurando o papel aberto contra o vento, o nariz vermelho "
      "afundado num cachecol verde. — “O contratado se compromete a não causar dano estrutural ao imóvel segurado.”")

def set_paragraph(words, widths_fn, line_w, first_indent=0.0, first_lines_indent=(0, 0.0)):
    """Quebra ótima (programação dinâmica, custo = Σ(espaço/espaço_ideal − 1)²) + justificação.
    words: lista de (texto, fonte). Retorna [(x_offsets, palavras, razão_do_espaço)]."""
    from functools import lru_cache
    n_ind, ind = first_lines_indent
    sp = widths_fn(" ", GAR)
    ww = [widths_fn(t, f) for t, f in words]
    N = len(words)
    def avail(k): return line_w - (ind if k < n_ind else 0) - (first_indent if k == 0 else 0)
    @lru_cache(None)
    def best(i, k):
        if i >= N: return 0.0, ()
        res = (1e18, ())
        tot = 0.0
        for j in range(i, N):
            tot += ww[j]
            gaps = j - i
            A = avail(k)
            if tot + gaps * sp * 0.82 > A: break
            last = j == N - 1
            if last:
                c = 0.0 if tot + gaps * sp <= A else ((A - tot) / max(gaps, 1) / sp - 1) ** 2 * 60
            else:
                r = (A - tot) / gaps / sp if gaps else 3.0
                c = (r - 1) ** 2 * (60 if r < 1 else 30) + (25 if gaps == 0 else 0)
            sub = best(j + 1, k + 1)
            if c + sub[0] < res[0]: res = (c + sub[0], (j + 1,) + sub[1])
        return res
    _, breaks = best(0, 0)
    out, i = [], 0
    for k, j in enumerate(breaks):
        ln = words[i:j]; A = avail(k)
        x0 = (ind if k < n_ind else 0) + (first_indent if k == 0 else 0)
        tot = sum(ww[i:j]); last = j == N
        gap = sp if (last and tot + (len(ln) - 1) * sp <= A) or len(ln) == 1 else (A - tot) / (len(ln) - 1)
        xs, x = [], x0
        for q in range(i, j):
            xs.append(x); x += ww[q] + gap
        out.append((xs, ln, gap / sp)); i = j
    return out

def chapter_page():
    W, H = 1600, 2300
    ink, acc, grey = INK, BRASS_D, "#7D7A72"
    o = []
    X0, X1 = 300, 1360
    FS, LEAD = 44, 66
    # régua de margem = grade de linhas de base (traço maior a cada linha de texto)
    base0 = 1452
    DY = 250
    rx = 150
    y_top, y_bot = 210, 2110
    o.append(f'<path d="M{rx},{y_top} L{rx},{y_bot}" stroke="{acc}" stroke-width="1"/>')
    d = ""; first = base0 - LEAD * ((base0 - y_top) // LEAD)
    y = first - LEAD; k = -((base0 - y_top) // LEAD) - 1
    nums = []
    while y <= y_bot:
        for j in range(6):
            yy = y + j * LEAD / 6
            if y_top <= yy <= y_bot:
                L = 16 if j == 0 else (9 if j == 3 else 5)
                d += f"M{rx},{yy:.1f} L{rx + L},{yy:.1f} "
        if k >= 0 and k % 5 == 0 and y_top <= y <= y_bot:
            nums.append(f'<path d="{text_path(f"{k:02d}", MONO, 11, rx - 10, y + 4, 0.06, "end")}" fill="{acc}"/>')
        y += LEAD; k += 1
    o.append(f'<path d="{d}" stroke="{acc}" stroke-width=".8"/>' + "".join(nums))
    # cabeçalho: 01 + Capítulo um + régua + título
    o.append(f'<path d="{text_path("01", MONO, 150, X0 - 10, 640 + DY, -0.02)}" fill="{ink}"/>')
    w01 = text_width("01", MONO, 150, -0.02)
    rx0 = X0 + w01 + 34
    o.append(f'<path d="{text_path("Capítulo um", ISI, 54, rx0, 558 + DY, 0.0)}" fill="{ink}"/>')
    o.append(ruler(rx0, X1, 590 + DY, ink, 1.0, 5, 10, True, False))
    o.append(f'<path d="{text_path("Noite tropical", IS, 176, X0 - 8, 860 + DY, -0.005)}" fill="{ink}"/>')
    # cota fina sob o título (largura da medida)
    o.append(f'<path d="M{X0},{930 + DY} L{X1},{930 + DY}" stroke="{ink}" stroke-width=".6"/>'
             f'<path d="M{X0},{922 + DY} L{X0},{938 + DY} M{X1},{922 + DY} L{X1},{938 + DY}" stroke="{ink}" stroke-width=".8"/>')
    o.append(arrow(X0 + 1, 930 + DY, 180, ink, 10, 3) + arrow(X1 - 1, 930 + DY, 0, ink, 10, 3))
    # capitular-mira
    size = 228
    cap_h = 0.739 * size
    ox, oy = X0, base0 + 2 * LEAD          # base da 3ª linha
    gx = ox + 0.270 * size; gy = oy - 0.3605 * size
    Rr = cap_h / 2 + 22
    cx_ = X0 + Rr - 4
    shift = cx_ - gx
    o.append(f'<path d="{text_path("O", IS, size, ox + shift, oy, 0)}" fill="{ink}"/>')
    gx = cx_
    o.append(circ(gx, gy, Rr, acc, 1.0) + circ(gx, gy, Rr - 7, acc, 0.5))
    o.append(f'<path d="{ticks_d(gx, gy, Rr - 7, Rr, [a for a in range(0, 360, 10) if a % 90])}" stroke="{acc}" stroke-width=".6"/>')
    o.append(f'<path d="M{gx - Rr - 14:.1f},{gy:.1f} L{gx - 30:.1f},{gy:.1f} M{gx + 30:.1f},{gy:.1f} L{gx + Rr + 14:.1f},{gy:.1f} '
             f'M{gx:.1f},{gy - Rr - 14:.1f} L{gx:.1f},{gy - 52:.1f} M{gx:.1f},{gy + 52:.1f} L{gx:.1f},{gy + Rr + 14:.1f}" stroke="{acc}" stroke-width=".9"/>')
    o.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="2.2" fill="{acc}"/>')
    drop_w = 2 * Rr + 30
    # texto corrido
    SCF = "EBGaramondSC-Regular.ttf"
    wf = lambda t, f: text_width(t, f, FS, 0.05 if f == SCF else 0.0)
    w1 = P1.split(" ")[1:]
    words1 = [(w, SCF if i < 2 else GAR) for i, w in enumerate(w1)]
    lines1 = set_paragraph(words1, wf, X1 - X0, 0, (3, drop_w))
    words2 = [(w, GAR) for w in P2.split(" ")]
    lines2 = set_paragraph(words2, wf, X1 - X0, FS * 1.2)
    y = base0
    for lines in (lines1, lines2):
        for xs, ln, ratio in lines:
            for x, (t, f) in zip(xs, ln):
                o.append(f'<path d="{text_path(t, f, FS, X0 + x, y, 0.05 if f == SCF else 0.0)}" fill="{ink}"/>')
            y += LEAD
    # fólio
    o.append(f'<path d="{text_path("11", MONO, 20, W / 2, 2160, 0.1, "middle")}" fill="{ink}"/>')
    o.append(f'<path d="M{W / 2 - 60},2153 L{W / 2 - 26},2153 M{W / 2 + 26},2153 L{W / 2 + 60},2153" stroke="{ink}" stroke-width=".7"/>')
    o.append(f'<path d="{text_path("Leis para Matar Deuses", ISI, 26, X1, 2160, 0.0, "end")}" fill="{grey}"/>')
    info = [(ratio, " ".join(t for t, _ in ln)) for xs, ln, ratio in lines1 + lines2]
    return svg(W, H, "".join(o), bg=PAPER), info

# ------------------------------------------------------------------ saída
def jpg_preview(png, name, maxw=1400, crop=None):
    from PIL import Image
    im = Image.open(png)
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (128, 128, 128) if "transp" in name else (240, 240, 240)); bg.paste(im, mask=im.split()[3]); im = bg
    im = im.convert("RGB")
    if crop: im = im.crop(crop)
    im.thumbnail((maxw, maxw))
    p = f"/tmp/claude-0/-home-user-LTKG/0ae43a17-9955-54f0-9172-040bd4d1f0e3/scratchpad/C/{name}.jpg"
    im.save(p, quality=88); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "emblem" in args or not args:
        ed, eb = emblem(INK, uid="C1")
        open(f"{OUT}/emblema_instrumento.svg", "w").write(svg(1000, 1000, eb, ed))
        to_png(svg(1000, 1000, eb, ed), f"{OUT}/emblema_instrumento.png", 2000)
        ed, eb = emblem("url(#ag)", uid="C2", mode="foil", accent=BRASS)
        to_png(svg(1000, 1000, eb, silver_grad("ag", 250, 80, 620, 640) + ed, bg=OBS), f"{OUT}/emblema_instrumento_prata_sobre_obsidiana.png", 2000)
    if "logo" in args or not args:
        d, b, h = wordmark(INK, "Cw1")
        open(f"{OUT}/logotipo_instrumento.svg", "w").write(svg(1400, h, b, d))
        d, b, h = wordmark("url(#lg)", "Cw2", acc=BRASS)
        to_png(svg(1400, h, b, silver_grad("lg", 300, 0, 900, 440) + d, bg=OBS), f"{OUT}/logotipo_instrumento.png", 2800)
        d, b, h = wordmark(INK, "Cw3")
        to_png(svg(1400, h, b, d, bg=PAPER), f"{OUT}/logotipo_instrumento_papel.png", 2800)
    if "laws" in args or not args:
        sv = law_sheet("url(#sg)", BRASS, OBS).replace("<defs>", "<defs>" + silver_grad("sg", 0, 0, 700, 500), 1)
        open(f"{OUT}/sinais_leis_instrumento.svg", "w").write(sv)
        to_png(sv, f"{OUT}/sinais_leis_instrumento.png", 2960)
    if "princ" in args or not args:
        sv = principles_sheet("url(#sg)", BRASS, OBS).replace("<defs>", "<defs>" + silver_grad("sg", 0, 0, 900, 400), 1)
        open(f"{OUT}/sinais_principios_instrumento.svg", "w").write(sv)
        to_png(sv, f"{OUT}/sinais_principios_instrumento.png", 4040)
    if "guarda" in args or not args:
        to_png(endpaper(), f"{OUT}/guarda_instrumento.png", 3200)
    if "capa" in args or not args:
        t0 = time.time(); to_png(cover_cloth(), f"{OUT}/capa_tecido_prata.png", 1600); print("capa", time.time() - t0)
    if "sobrecapa" in args or not args:
        to_png(cover_jacket(), f"{OUT}/sobrecapa_instrumento.png", 1600)
    if "capitulo" in args or not args:
        sv, info = chapter_page()
        for r, t in info: print(f"{r:4.2f}  {t}")
        to_png(sv, f"{OUT}/abertura_capitulo.png", 1600)
    print("C ok")
