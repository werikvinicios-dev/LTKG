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
    N = rings
    for k in range(1, N + 1):
        r = R * math.sqrt(k / (N + 0.6))
        dr = R * (math.sqrt((k + 1) / (N + 0.6)) - math.sqrt(k / (N + 0.6)))
        w = max(0.32, min(1.4, dr * 0.36))
        u = k / N
        if u > 0.7 and fringe > 0:
            col = irid(0.1 + u * 1.1)
            mix = clamp((u - 0.7) / 0.3) ** 1.5 * 0.6 * fringe
            inner.append(circ(CX, CY, r, c, w, f'opacity="{1 - mix:.2f}"'))
            inner.append(circ(CX, CY, r, col, w, f'opacity="{mix:.2f}"'))
        else:
            inner.append(circ(CX, CY, r, c, w))
    inner.append(f'<circle cx="{CX}" cy="{CY}" r="{R * math.sqrt(0.45 / (N + 0.6)):.2f}" fill="{c}"/>')
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
    inner.append(f'<path d="{rt}" stroke="{c}" stroke-width="0.5" fill="none" opacity=".9"/>')
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
    if fringe > 0:
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
           plate_op=None, rings=None):
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
        ld, lb = lens(uid + "L", c, mode, crack, rings or (34 if detail >= 2 else 16), knock_sword, focus, fringe)
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
        o.append(f'<path d="{text_path("VOLUME I  ·  O DEUS QUE CAIU DO CÉU", MONOR, 22, cx, 410, 0.42, "middle")}" fill="{c}"/>')
    return "", "".join(o), 440

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
    print("C ok")
