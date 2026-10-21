#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPÇÃO A — APÓLICE. Gravura de segurança (cédulas, apólices, selos): guilhochê de rose engine,
microtexto com as sete leis, perlado de moeda, letras hachuradas como talho-doce."""
import math, os
from kit import *

OUT = "/home/user/LTKG/exportacoes/identidade_v2/A_Apolice"
os.makedirs(OUT, exist_ok=True)
IVORY, OXBLOOD, BRONZE, GREEN, INK = "#EEE5D0", "#5E1B17", "#B07D45", "#1F3A32", "#1B1714"
LEIS = ["CONSERVAÇÃO", "VÍNCULO", "COMPATIBILIDADE", "VAZÃO", "DISSIPAÇÃO", "CAPACIDADE", "RETORNO"]
ROM = ["I", "II", "III", "IV", "V", "VI", "VII"]
SC, SCB, IT = "PlayfairDisplaySC-Regular.ttf", "PlayfairDisplaySC-Bold.ttf", "PlayfairDisplay-Italic.ttf"

def foil_defs(uid, kind="bronze"):
    if kind == "bronze":
        st = [(0, "#F3DDA8"), (0.22, "#C99A57"), (0.45, "#8A5E2C"), (0.62, "#D9B271"), (0.8, "#9B6B35"), (1, "#E8C88A")]
    elif kind == "silver":
        st = [(0, "#FFFFFF"), (0.3, "#B9BDC4"), (0.55, "#7D828A"), (0.75, "#DCE0E6"), (1, "#9AA0A8")]
    else:
        st = [(0, kind), (1, kind)]
    return lin_grad(uid, st, user=(0, 0, 1000, 1000))

# ------------------------------------------------------------------ emblema
BLADE = "487,330 513,330 513,760 500,872 487,760"

def hatch_fill(c, poly, uid, ang=0.0, gap=3.0, w=1.1):
    """Hachura de talho-doce recortada num polígono (linhas paralelas inclinadas 'ang' graus)."""
    t = math.tan(math.radians(ang))
    lines = "".join(f'<line x1="{-300 + k * gap:.1f}" y1="0" x2="{-300 + k * gap + 1000 * t:.1f}" y2="1000"/>'
                    for k in range(int(1600 / gap)))
    return (f'<clipPath id="{uid}"><polygon points="{poly}"/></clipPath>'
            f'<g clip-path="url(#{uid})" stroke="{c}" stroke-width="{w}">{lines}</g>'
            f'<polygon points="{poly}" fill="none" stroke="{c}" stroke-width="1.4"/>')

def sword_balance(c, beam_deg=-7.0, plate_drop=172, uid="A", hl=IVORY):
    """Espada vertical + travessão-balança, com bisel de talho-doce: metade iluminada chapada,
    metade em sombra hachurada (como o fio de uma lâmina gravada). Devolve (traço, silhueta)."""
    parts, sil = [], []
    parts.append(f'<polygon points="487,330 500,330 500,872 487,760" fill="{c}"/>')
    parts.append(hatch_fill(c, "500,330 513,330 513,760 500,872", f"{uid}-hb", 0, 2.5, 1.15))
    parts.append(f'<line x1="500" y1="345" x2="500" y2="748" stroke="{hl}" stroke-width="1.5" opacity=".85"/>')
    sil.append(f'<polygon points="{BLADE}"/>')
    # pomo e punho com fio enrolado
    parts.append(f'<circle cx="500" cy="134" r="19" fill="{c}"/><circle cx="500" cy="134" r="10.5" fill="none" stroke="{hl}" stroke-width="1.4"/>'
                 f'<circle cx="500" cy="134" r="3.6" fill="{hl}"/>')
    parts.append(f'<rect x="492" y="152" width="16" height="144" fill="{c}"/>')
    parts.append("".join(f'<path d="M492,{yy + 5} L508,{yy}" stroke="{hl}" stroke-width="1.1" opacity=".7"/>' for yy in range(160, 290, 8)))
    parts.append(f'<rect x="485" y="152" width="30" height="6" fill="{c}"/><rect x="485" y="288" width="30" height="6" fill="{c}"/>')
    sil.append('<circle cx="500" cy="134" r="19"/><rect x="485" y="152" width="30" height="144"/>')
    g = math.radians(beam_deg); gx, gy, L = 500, 312, 292
    def rot(px, py):
        dx, dy = px - gx, py - gy
        return gx + dx * math.cos(g) - dy * math.sin(g), gy + dx * math.sin(g) + dy * math.cos(g)
    top = " ".join(P(*q) for q in [rot(gx - L, gy - 7), rot(gx + L, gy - 7), rot(gx + L, gy), rot(gx - L, gy)])
    bot = " ".join(P(*q) for q in [rot(gx - L, gy), rot(gx + L, gy), rot(gx + L, gy + 7), rot(gx - L, gy + 7)])
    parts.append(f'<polygon points="{top}" fill="{c}"/>')
    parts.append(hatch_fill(c, bot, f"{uid}-hm", 35, 2.3, 1.0))
    sil.append(f'<polygon points="{top}"/><polygon points="{bot}"/>')
    parts.append(f'<polygon points="472,312 500,294 528,312 500,344" fill="{c}"/>'
                 f'<polygon points="483,312 500,302 517,312 500,332" fill="none" stroke="{hl}" stroke-width="1.2"/>')
    sil.append('<polygon points="472,312 500,294 528,312 500,344"/>')
    for side in (-1, 1):
        ex, ey = rot(gx + side * L, gy)
        parts.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="10" fill="{c}"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.4" fill="{hl}"/>')
        py = ey + plate_drop; hw = 58
        for k in (-1, 0, 1):
            parts.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex + k * (hw - 8):.1f}" y2="{py:.1f}" stroke="{c}" stroke-width="1.8"/>')
            sil.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex + k * (hw - 8):.1f}" y2="{py:.1f}" stroke-width="2"/>')
        bowl = f'M{ex - hw:.1f},{py:.1f} Q{ex:.1f},{py + 44:.1f} {ex + hw:.1f},{py:.1f} Z'
        parts.append(f'<path d="{bowl}" fill="{c}"/>')
        parts.append(f'<path d="M{ex - hw + 10:.1f},{py + 5:.1f} Q{ex:.1f},{py + 34:.1f} {ex + hw - 10:.1f},{py + 5:.1f}" fill="none" stroke="{hl}" stroke-width="1.1"/>')
        parts.append(f'<line x1="{ex - hw - 4:.1f}" y1="{py:.1f}" x2="{ex + hw + 4:.1f}" y2="{py:.1f}" stroke="{c}" stroke-width="2.2"/>')
        sil.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="10"/><path d="{bowl}"/>')
    return "".join(parts), "".join(sil)

def engraved_sun(cx=500, cy=500, R=112, gap=4.6):
    """Disco do sol em talho-doce: linhas horizontais de espessura variável (esfera iluminada do alto
    à esquerda), como o retrato de uma cédula."""
    lx, ly, lz = -0.55, -0.6, 0.58
    out = []
    y = cy - R + gap / 2
    while y < cy + R:
        top, bot = [], []
        h = math.sqrt(max(R * R - (y - cy) ** 2, 0))
        n = max(8, int(h / 3))
        for i in range(n + 1):
            x = cx - h + 2 * h * i / n
            nx, ny = (x - cx) / R, (y - cy) / R
            nz = math.sqrt(max(1 - nx * nx - ny * ny, 0))
            lum = clamp(nx * lx + ny * ly + nz * lz)
            th = min(0.35 + 3.1 * (1 - lum) ** 1.3, gap * 0.9)
            top.append((x, y - th / 2)); bot.append((x, y + th / 2))
        out.append(polyline(top + bot[::-1], True))
        y += gap
    return " ".join(out)

CRACK = [(392, 398), (430, 440), (418, 464), (464, 494), (452, 514), (498, 544), (540, 562), (530, 588), (580, 612), (612, 652)]
BRANCH = [(452, 514), (428, 536), (436, 554)]
SUN = engraved_sun()

def emblem(c=OXBLOOD, uid="A", draw=1.0, ring_rot=0.0, rays=1.0, sword=1.0, beam=-7.0, bg=IVORY, diamonds=1.0, crack=1.0):
    """Medalha gravada. Parâmetros de animação: draw (guilhochê), ring_rot, rays, sword, diamonds, crack."""
    cx = cy = 500
    out = []
    out.append(f'<circle cx="{cx}" cy="{cy}" r="480" fill="none" stroke="{c}" stroke-width="1"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="472" fill="none" stroke="{c}" stroke-width="3.4"/>')
    micro = " · ".join(LEIS) + " · "
    out.append(f'<g transform="rotate({ring_rot:.2f} 500 500)"><path d="{text_on_circle(micro, SC, 15.5, cx, cy, 448, -90, 0.06, fill_circle=True)}" fill="{c}"/></g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="440" fill="none" stroke="{c}" stroke-width="0.9"/>')
    # perlado interrompido pelos sete losangos (as sete leis)
    dia = [-90 + k * 360 / 7 for k in range(7)]
    for k in range(147):
        a = k * 360 / 147 - 90
        if min(abs((a - d + 180) % 360 - 180) for d in dia) < 5.5:
            continue
        x, y = polar(cx, cy, 429, a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{c}"/>')
    for k, d in enumerate(dia):
        on = clamp(diamonds * 7 - k)
        if on <= 0:
            continue
        x, y = polar(cx, cy, 429, d)
        s = 0.5 + 0.5 * ease_out(on)
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({d + 90:.1f}) scale({s:.3f})" opacity="{on:.2f}">'
                   f'<polygon points="0,-18 9.5,0 0,18 -9.5,0" fill="{c}"/>'
                   f'<polygon points="0,-10.5 4.8,0 0,10.5 -4.8,0" fill="none" stroke="{bg}" stroke-width="1.2"/></g>')
    # guilhochê: malha de rose engine (30 fios em fase distribuída) com respiração em sete tempos
    n = 1100; m = max(2, int(n * draw))
    def partial(base, amp, lobes, ph, k2=0, amp2=0, ph2=0):
        pts = []
        for i in range(m + 1):
            tt = 2 * math.pi * i / n - math.pi / 2
            r = base + amp * math.sin(lobes * tt + ph) + amp2 * math.sin(k2 * tt + ph2)
            pts.append((cx + r * math.cos(tt), cy + r * math.sin(tt)))
        return polyline(pts, close=(m >= n))
    g = []
    for i in range(14):                       # duas fitas cruzadas, 21 lóbulos (7 × 3), fase aberta em 2,2 rad
        ph = i * 2.2 / 14 - 1.1
        g.append(f'<path d="{partial(374, 28, 21, ph)}"/><path d="{partial(374, -28, 21, ph)}"/>')
    out.append(f'<g fill="none" stroke="{c}" stroke-width="0.6" mask="url(#{uid}-knock)">{"".join(g)}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="330" fill="none" stroke="{c}" stroke-width="2.6"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="322" fill="none" stroke="{c}" stroke-width="0.8"/>')
    # sol: raios finos de talho (alternando longos e curtos) + espigões
    R1 = 160 + (312 - 160) * rays
    ray = "".join(f'M{P(*polar(cx, cy, 166, a / 2 + 0.25))} L{P(*polar(cx, cy, R1 - (0 if a % 4 == 0 else 40 * rays), a / 2 + 0.25))} ' for a in range(720))
    out.append(f'<path d="{ray}" stroke="{c}" stroke-width="0.55" fill="none" mask="url(#{uid}-knock)"/>')
    rs = 124 + 36 * ease_out(clamp(rays * 1.4))
    sp = "".join(f'<polygon points="{P(*polar(cx, cy, 123, k * 360 / 28 - 2.4))} {P(*polar(cx, cy, rs + (9 if k % 2 == 0 else 0), k * 360 / 28))} '
                 f'{P(*polar(cx, cy, 123, k * 360 / 28 + 2.4))}"/>' for k in range(28))
    out.append(f'<g fill="{c}" mask="url(#{uid}-knock)">{sp}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="118" fill="none" stroke="{c}" stroke-width="2.4" mask="url(#{uid}-knock)"/>')
    sr = min(1, rays * 1.6)
    sh = (4 * crack, 6 * crack)
    out.append(f'<g mask="url(#{uid}-disk)"><g transform="translate(500 500) scale({sr:.3f}) translate(-500 -500)">'
               f'<path d="{SUN}" fill="{c}" clip-path="url(#{uid}-top)"/>'
               f'<g transform="translate({sh[0]:.2f} {sh[1]:.2f})"><path d="{SUN}" fill="{c}" clip-path="url(#{uid}-bot)"/></g></g></g>')
    # espada-balança (desce na animação)
    sb, sil = sword_balance(c, beam, uid=uid, hl=bg)
    dy = (1 - ease_out(sword)) * -420
    out.append(f'<g transform="translate(0 {dy:.1f})" opacity="{clamp(sword * 3):.2f}">{sb}</g>')
    top_poly = " ".join(P(*q) for q in [(300, 300), (720, 300), (720, 652)] + CRACK[::-1] + [(300, 398)])
    bot_poly = " ".join(P(*q) for q in [(300, 398)] + CRACK + [(720, 652), (720, 720), (300, 720)])
    nc = max(2, int(len(CRACK) * crack + 0.999)) if crack > 0 else 0
    crack_el = (f'<polyline points="{" ".join(P(*q) for q in CRACK[:nc])}" fill="none" stroke="black" stroke-width="{3.4 * crack:.2f}"/>'
                f'<polyline points="{" ".join(P(*q) for q in BRANCH)}" fill="none" stroke="black" stroke-width="{1.6 * crack:.2f}"/>') if crack > 0 else ""
    defs = (f'<clipPath id="{uid}-top"><polygon points="{top_poly}"/></clipPath>'
            f'<clipPath id="{uid}-bot"><polygon points="{bot_poly}"/></clipPath>'
            f'<mask id="{uid}-disk" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">'
            f'<rect width="1000" height="1000" fill="white"/>{crack_el}'
            f'<g transform="translate(0 {dy:.1f})" fill="black" stroke="black" stroke-width="22" opacity="{clamp(sword * 3):.2f}">{sil}</g></mask>'
            f'<mask id="{uid}-knock" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">'
            f'<rect width="1000" height="1000" fill="white"/>'
            f'<g transform="translate(0 {dy:.1f})" fill="black" stroke="black" stroke-width="16" opacity="{clamp(sword * 3):.2f}">{sil}</g></mask>')
    return defs, "".join(out)

# ------------------------------------------------------------------ logotipo
def wordmark(c=OXBLOOD, uid="Aw", w=1400):
    cx = w / 2
    hatch = (f'<pattern id="{uid}-h" patternUnits="userSpaceOnUse" width="6" height="3.1">'
             f'<rect width="6" height="1.45" fill="{c}"/></pattern>')
    d1 = text_path("Leis para", IT, 74, cx, 92, 0.02, "middle")
    d2 = text_path("MATAR DEUSES", SCB, 168, cx, 262, 0.035, "middle")
    ww = text_width("MATAR DEUSES", SCB, 168, 0.035)
    band = []
    for k in range(9):
        band.append(f'<path d="{wave_band(cx - ww / 2, cx + ww / 2, 300, 6, 38, k * 0.7)}"/>')
    d3 = text_path("VOLUME I  ·  O DEUS QUE CAIU DO CÉU", SC, 26, cx, 356, 0.28, "middle")
    body = (f'<path d="{d1}" fill="{c}"/>'
            f'<path d="{d2}" fill="url(#{uid}-h)"/><path d="{d2}" fill="none" stroke="{c}" stroke-width="2.2"/>'
            f'<g fill="none" stroke="{c}" stroke-width="0.8">{"".join(band)}</g>'
            f'<path d="{d3}" fill="{c}"/>')
    return hatch, body, 380

# ------------------------------------------------------------------ sinais
def law_pattern(i, c, cx, cy):
    """Cada lei escrita pela própria geometria do torno (anel útil entre r≈46 e r≈95)."""
    L = []
    pa = lambda d, op=1: L.append(f'<path d="{d}"' + (f' opacity="{op}"' if op != 1 else "") + '/>')
    if i == 0:      # Conservação: malha fechada e simétrica, nada se perde
        for k in range(12):
            pa(rose(cx, cy, 71, 17, 7, k * 2 * math.pi / 12, 700))
    elif i == 1:    # Vínculo: dois feixes de anéis que se atravessam
        for side in (-1, 1):
            for k in range(9):
                pa(rose(cx + side * 17, cy, 44 + k * 3.2, 1.6, 9, k * 0.5, 500))
    elif i == 2:    # Compatibilidade: 6 e 9 lóbulos sobrepostos, só coincidem onde as fases concordam
        for k in range(8):
            pa(rose(cx, cy, 72, 15, 6, k * 0.16, 700))
            pa(rose(cx, cy, 72, 15, 9, k * 0.16 + math.pi, 700), .75)
    elif i == 3:    # Vazão: braços em espiral escoando para o centro
        for k in range(18):
            pts = []
            for j in range(161):
                u = j / 160; r = 95 - 49 * u
                a = k * 2 * math.pi / 18 + 2.4 * u ** 1.4
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            pa(polyline(pts))
    elif i == 4:    # Dissipação: a onda perde amplitude e os anéis se afastam
        for k in range(13):
            u = k / 12
            pa(rose(cx, cy, 48 + 47 * u ** 0.75, 7 * (1 - u) + 0.2, 10, k * 0.55, 500))
    elif i == 5:    # Capacidade: o vaso enche até a marca
        R = 95; lvl = cy + 12
        y = cy - R + 3
        while y < cy + R:
            h = math.sqrt(max(R * R - (y - cy) ** 2, 0))
            if y > lvl:
                L.append(f'<line x1="{cx - h:.1f}" y1="{y:.1f}" x2="{cx + h:.1f}" y2="{y:.1f}"/>')
            y += 3.2
        L.append(f'<line x1="{cx - 96}" y1="{lvl}" x2="{cx + 96}" y2="{lvl}" stroke-width="1.8"/>')
        gx = cx - 66
        L.append(f'<line x1="{gx}" y1="{cy - 66}" x2="{gx}" y2="{lvl}" stroke-width="0.9"/>')
        for k in range(12):
            yy = lvl - k * 6.5
            L.append(f'<line x1="{gx}" y1="{yy:.1f}" x2="{gx + (9 if k % 4 == 0 else 4.5)}" y2="{yy:.1f}" stroke-width="0.9"/>')
        L.append(f'<polygon points="{gx + 12},{lvl - 3.5} {gx + 18},{lvl} {gx + 12},{lvl + 3.5}" fill="{c}" stroke="none"/>')
    elif i == 6:    # Retorno: hipotrocoide de sete laços, a curva volta exatamente ao ponto de partida
        for k in range(6):
            pa(hypotrochoid(cx, cy, 63, 27, 34 + k * 2.2, n=1600, scale=1.25, rot=k * 0.035 - math.pi / 2))
    return "".join(L)

def law_seal(i, c=OXBLOOD, cx=150, cy=150, R=130, bg=IVORY):
    nm = LEIS[i]
    out = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{c}" stroke-width="2.2"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{R - 7}" fill="none" stroke="{c}" stroke-width="0.7"/>',
           f'<path d="{text_on_circle(nm + " · ", SC, 13, cx, cy, R - 24, -90, 0.12, fill_circle=True)}" fill="{c}"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{R - 32}" fill="none" stroke="{c}" stroke-width="0.7"/>',
           f'<clipPath id="ls{i}{cx:.0f}"><circle cx="{cx}" cy="{cy}" r="{R - 34}"/></clipPath>',
           f'<g clip-path="url(#ls{i}{cx:.0f})" fill="none" stroke="{c}" stroke-width="0.6">{law_pattern(i, c, cx, cy)}</g>',
           f'<circle cx="{cx}" cy="{cy}" r="{R - 86}" fill="{bg}" stroke="{c}" stroke-width="1.4"/>',
           f'<path d="{text_path(ROM[i], SCB, 44 if i < 6 else 38, cx, cy + 15, 0.02, "middle")}" fill="{c}"/>']
    return "".join(out)

def principle_swatch(name, c=GREEN, cx=150, cy=150, R=120, uid="p"):
    cp = f'<clipPath id="{uid}"><circle cx="{cx}" cy="{cy}" r="{R - 10}"/></clipPath>'
    L = []
    x0, x1, y0, y1 = cx - R, cx + R, cy - R, cy + R
    if name == "PULSO":
        for k in range(-13, 14):
            pts = []; yb = cy + k * 9; x = x0; mu = cx + k * 7
            while x <= x1:
                pts.append((x, yb - 13 * math.exp(-((x - mu) / 14) ** 2))); x += 2
            L.append(f'<path d="{polyline(pts)}"/>')
    elif name == "BRASA":
        for k in range(1, 15):
            L.append(f'<path d="{rose(cx, cy, k * 8, 2.2 + k * .25, 9, k * .4, 400)}"/>')
    elif name == "TRAMA":
        for k in range(-14, 15):
            L.append(f'<path d="{wave_band(x0, x1, cy + k * 9, 4, 36, 0)}"/>')
            L.append(f'<path d="{wave_band(x0, x1, cy + k * 9, 4, 36, math.pi)}" opacity=".7"/>')
    elif name == "CLARÃO":
        L.append("".join(f'<path d="M{P(*polar(cx, cy, 10, a))} L{P(*polar(cx, cy, R, a))}"/>' for a in range(0, 360, 3)))
    elif name == "ECO":
        for k in range(1, 16):
            L.append(f'<circle cx="{cx}" cy="{cy}" r="{k * 7.4}"/>')
    elif name == "CARGA":
        for k in range(-12, 13):
            pts = []; x = x0; up = True
            while x <= x1:
                pts.append((x, cy + k * 10 + (5 if up else -5))); x += 9; up = not up
            L.append(f'<path d="{polyline(pts)}"/>')
    tex = f'<g clip-path="url(#{uid})" fill="none" stroke="{c}" stroke-width="0.9">{"".join(L)}</g>'
    frame = (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{c}" stroke-width="2.2"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{R - 10}" fill="none" stroke="{c}" stroke-width="0.8"/>')
    label = f'<path d="{text_path(name, SC, 22, cx, cy + R + 40, 0.3, "middle")}" fill="{c}"/>'
    return cp, tex + frame + label

# ------------------------------------------------------------------ padrão de guarda
def endpaper(w=1600, h=1000, c=OXBLOOD, bg=IVORY):
    """Folha de guarda: fundo de segurança contínuo (renda de torno) com medalhões de sete lóbulos
    cercados de microtexto."""
    L = []
    step = 38
    for j, row in enumerate(range(-step, h + step, step)):
        for k in range(6):
            L.append(f'<path d="{wave_band(-40, w + 40, row, 11, 152, k * 2 * math.pi / 6 + (j % 2) * math.pi / 6, 2.5)}"/>')
    M = []
    sx, sy = 400, 330
    micro = text_on_circle("LEIS PARA MATAR DEUSES · ", SC, 9.5, 0, 0, 80, -90, 0.12, fill_circle=True)
    for r_, yy in enumerate(range(0, h + sy, sy)):
        for xx in range(0, w + sx, sx):
            ox = xx + (sx / 2 if r_ % 2 else 0)
            M.append(f'<circle cx="{ox}" cy="{yy}" r="96" fill="{bg}" stroke="none"/>')
            M.append(f'<circle cx="{ox}" cy="{yy}" r="96" stroke-width="1.8"/><circle cx="{ox}" cy="{yy}" r="91"/>')
            M.append(f'<path d="{micro}" transform="translate({ox} {yy})" fill="{c}" stroke="none"/>')
            M.append(f'<circle cx="{ox}" cy="{yy}" r="74"/>')
            for k in range(10):
                M.append(f'<path d="{rose(ox, yy, 47, 16, 7, k * 2.4 / 10, 420)}"/><path d="{rose(ox, yy, 47, -16, 7, k * 2.4 / 10, 420)}"/>')
            M.append(f'<circle cx="{ox}" cy="{yy}" r="22" fill="{bg}"/>')
            M.append(f'<polygon points="{ox},{yy - 12} {ox + 6.5},{yy} {ox},{yy + 12} {ox - 6.5},{yy}" fill="{c}" stroke="none"/>')
    return svg(w, h, f'<g fill="none" stroke="{c}" stroke-width="0.5" opacity=".8">{"".join(L)}</g>'
                     f'<g fill="none" stroke="{c}" stroke-width="0.6">{"".join(M)}</g>', bg=bg)

# ------------------------------------------------------------------ capa (edição especial)
def cover(edition="tecido"):
    W, H = 1600, 2300
    if edition == "tecido":
        bg, ink, fid = OXBLOOD, "url(#foil)", "bronze"
    else:
        bg, ink, fid = IVORY, OXBLOOD, OXBLOOD
    ed, eb = emblem(ink if edition != "tecido" else "url(#foil)", uid="Ac", bg=bg)
    hatch, wb, wh = wordmark(ink, "Acw", 1400)
    defs = foil_defs("foil", "bronze") + ed + hatch
    # textura de tecido
    cloth = ""
    if edition == "tecido":
        defs += ('<filter id="cloth" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
                 'baseFrequency="0.9 0.35" numOctaves="2" seed="7" result="n"/><feColorMatrix type="matrix" '
                 'values="0 0 0 0 0.10  0 0 0 0 0.02  0 0 0 0 0.02  0 0 0 0.55 0"/></filter>')
        cloth = f'<rect width="{W}" height="{H}" filter="url(#cloth)" opacity=".85"/>'
    # moldura de cédula: dupla linha + faixa guilhochê
    fr = []
    m1, m2 = 70, 108
    fr.append(f'<rect x="{m1}" y="{m1}" width="{W - 2 * m1}" height="{H - 2 * m1}" fill="none" stroke="{ink}" stroke-width="4"/>')
    fr.append(f'<rect x="{m2}" y="{m2}" width="{W - 2 * m2}" height="{H - 2 * m2}" fill="none" stroke="{ink}" stroke-width="1.4"/>')
    band = []
    for k in range(6):
        band.append(f'<path d="{wave_band(m1 + 6, W - m1 - 6, (m1 + m2) / 2, 11, 46, k * 0.9, 3)}"/>')
        band.append(f'<path d="{wave_band(m1 + 6, W - m1 - 6, H - (m1 + m2) / 2, 11, 46, k * 0.9, 3)}"/>')
    vband = "".join(f'<path d="{wave_band(m1 + 6, H - m1 - 6, (m1 + m2) / 2, 11, 46, k * 0.9, 3)}" transform="translate({0} 0)"/>' for k in range(6))
    fr.append(f'<g fill="none" stroke="{ink}" stroke-width="0.9">{"".join(band)}</g>')
    fr.append(f'<g fill="none" stroke="{ink}" stroke-width="0.9" transform="translate({W} 0) rotate(90)">{vband}</g>')
    fr.append(f'<g fill="none" stroke="{ink}" stroke-width="0.9" transform="translate(0 {H}) rotate(-90) translate(0 0)">{vband}</g>')
    for (x, y) in ((m1 + 19, m1 + 19), (W - m1 - 19, m1 + 19), (m1 + 19, H - m1 - 19), (W - m1 - 19, H - m1 - 19)):
        fr.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{bg}" stroke="{ink}" stroke-width="2"/>')
        fr.append(f'<path d="{rose(x, y, 18, 6, 8, 0, 200)}" fill="none" stroke="{ink}" stroke-width="1"/>')
    # numeração da edição
    num = text_path("EDIÇÃO NUMERADA  Nº 0001 / 1187", SC, 24, W / 2, H - 200, 0.25, "middle")
    auth = text_path("WERIK MARTINS", SCB, 48, W / 2, H - 270, 0.3, "middle")
    body = (cloth + "".join(fr) +
            f'<g transform="translate({W / 2 - 520} 300) scale(1.04)">{eb}</g>' +
            f'<g transform="translate({(W - 1400) / 2} 1430)">{wb}</g>' +
            f'<path d="{auth}" fill="{ink}"/><path d="{num}" fill="{ink}" opacity=".9"/>')
    return svg(W, H, body, defs, bg=bg)

def cover_jacket():
    """Sobrecapa: papel apólice com a arte em vinheta oval, como o retrato de uma cédula."""
    W, H = 1600, 2300
    ed, eb = emblem(OXBLOOD, uid="Aj")
    hatch, wb, wh = wordmark(OXBLOOD, "Ajw", 1400)
    art = "/home/user/LTKG/build/arte/capa_arte.jpg"
    defs = ed + hatch + (
        '<filter id="duo"><feColorMatrix type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 1 0"/>'
        '<feComponentTransfer><feFuncR type="table" tableValues="0.27 0.94"/><feFuncG type="table" tableValues="0.08 0.90"/>'
        '<feFuncB type="table" tableValues="0.07 0.80"/></feComponentTransfer></filter>'
        f'<clipPath id="oval"><ellipse cx="{W / 2}" cy="900" rx="430" ry="560"/></clipPath>')
    lines = "".join(f'<ellipse cx="{W / 2}" cy="900" rx="{430 + k * 5}" ry="{560 + k * 5}" fill="none" stroke="{OXBLOOD}" stroke-width="0.7"/>' for k in range(1, 9))
    ros = "".join(f'<path d="{rose(W / 2, 900, 0, 0, 1)}"/>' for _ in range(0))
    guil = "".join(f'<path d="{rose(W / 2, 900, 0, 0, 1)}"/>' for _ in range(0))
    # guilhochê oval em volta da vinheta
    gl = []
    for k in range(20):
        pts = []
        for i in range(901):
            tt = 2 * math.pi * i / 900
            rr = 1 + 0.045 * math.sin(30 * tt + k * 0.21)
            pts.append((W / 2 + 500 * rr * math.cos(tt), 900 + 630 * rr * math.sin(tt)))
        gl.append(f'<path d="{polyline(pts, True)}"/>')
    body = (f'<g fill="none" stroke="{OXBLOOD}" stroke-width="0.5">{"".join(gl)}</g>'
            f'<ellipse cx="{W / 2}" cy="900" rx="452" ry="582" fill="{IVORY}"/>'
            f'<image href="{art}" x="{W / 2 - 430}" y="340" width="860" height="1236" preserveAspectRatio="xMidYMid slice" clip-path="url(#oval)" filter="url(#duo)"/>'
            + lines +
            f'<rect x="70" y="70" width="{W - 140}" height="{H - 140}" fill="none" stroke="{OXBLOOD}" stroke-width="4"/>'
            f'<rect x="96" y="96" width="{W - 192}" height="{H - 192}" fill="none" stroke="{OXBLOOD}" stroke-width="1.2"/>'
            f'<g transform="translate(130 130) scale(0.26)">{eb}</g>'
            f'<path d="{text_path("Nº 0001", SCB, 40, W - 150, 210, 0.1, "end")}" fill="{OXBLOOD}"/>'
            f'<g transform="translate({(W - 1400) / 2} 1640)">{wb}</g>'
            f'<path d="{text_path("WERIK MARTINS", SCB, 46, W / 2, H - 170, 0.3, "middle")}" fill="{OXBLOOD}"/>')
    return svg(W, H, body, defs, bg=IVORY)

# ------------------------------------------------------------------ abertura de capítulo
def chapter_page():
    W, H = 1600, 2300
    L = []
    # selo de capítulo
    cx, cy = W / 2, 470
    L.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="{OXBLOOD}" stroke-width="2.4"/>')
    L.append(f'<path d="{text_on_circle("CAPÍTULO UM · NOITE TROPICAL · ", SC, 15, cx, cy, 128, -90, 0.12, fill_circle=True)}" fill="{OXBLOOD}"/>')
    for k in range(10):
        ph = k * 2.2 / 10 - 1.1
        L.append(f'<path d="{rose(cx, cy, 84, 13, 14, ph, 600)}" fill="none" stroke="{OXBLOOD}" stroke-width="0.5"/>'
                 f'<path d="{rose(cx, cy, 84, -13, 14, ph, 600)}" fill="none" stroke="{OXBLOOD}" stroke-width="0.5"/>')
    L.append(f'<circle cx="{cx}" cy="{cy}" r="56" fill="{IVORY}" stroke="{OXBLOOD}" stroke-width="1.6"/>')
    L.append(f'<path d="{text_path("I", SCB, 70, cx, cy + 25, 0, "middle")}" fill="{OXBLOOD}"/>')
    L.append(f'<path d="{text_path("Noite tropical", IT, 92, cx, 790, 0.01, "middle")}" fill="{INK}"/>')
    for k in range(5):
        L.append(f'<path d="{wave_band(cx - 210, cx + 210, 850, 5, 30, k * 0.9)}" fill="none" stroke="{OXBLOOD}" stroke-width="0.8"/>')
    # capitular gravada
    x0, y0, s = 220, 960, 168
    L.append(f'<rect x="{x0}" y="{y0}" width="{s}" height="{s}" fill="none" stroke="{OXBLOOD}" stroke-width="2"/>')
    L.append("".join(f'<line x1="{x0 + 8}" y1="{y0 + 8 + k * 3.2}" x2="{x0 + s - 8}" y2="{y0 + 8 + k * 3.2}" stroke="{OXBLOOD}" stroke-width="0.8"/>' for k in range(int((s - 16) / 3.2))))
    L.append(f'<circle cx="{x0 + s / 2}" cy="{y0 + s / 2}" r="58" fill="{IVORY}"/>')
    L.append(f'<path d="{text_path("O", SCB, 128, x0 + s / 2, y0 + s / 2 + 45, 0, "middle")}" fill="{OXBLOOD}"/>')
    # texto de amostra (início do capítulo 1), justificado e hifenizado
    paras = ["contrato tinha onze páginas, e Pelle Dorn fazia questão de que Ilan Varek conhecesse cada uma delas antes de entrar no prédio.",
             "— Cláusula sétima — leu o agente da seguradora, segurando o papel aberto contra o vento, o nariz vermelho afundado num "
             "cachecol verde. — “O contratado se compromete a não causar dano estrutural ao imóvel segurado.” Cláusula oitava: “O contratado "
             "se compromete a preservar, na medida do tecnicamente possível, o ativo térmico penhorado, a saber, o calor armazenado no "
             "reservatório objeto da apólice.” Cláusula nona…",
             "— Senhor Dorn.", "— Sim?", "— Está fazendo vinte graus abaixo de zero.",
             "— Vinte e dois — corrigiu Dorn, satisfeito por ter consultado o termômetro da esquina. — Cláusula nona: “O contratado "
             "permanecerá na cidade de Vhalessa por três dias após a conclusão do serviço, para depoimento e eventuais esclarecimentos "
             "à Companhia Arrimo.”"]
    ds, _ = typeset(paras, "EBGaramond-Regular.ttf", 42, 220, 1008, 1160, 60, indent=52, drop=(3, 198),
                    first_font=SC, first_words=2, first_size=36)
    L.append(f'<path d="{" ".join(ds)}" fill="{INK}"/>')
    L.append(f'<path d="{text_path("Leis para Matar Deuses", IT, 28, cx, 140, 0.02, "middle")}" fill="#8b7f6c"/>')
    L.append(f'<path d="{text_path("7", "PlayfairDisplay-Regular.ttf", 30, cx, H - 120, 0, "middle")}" fill="#8b7f6c"/>')
    return svg(W, H, "".join(L), bg=IVORY)

# ------------------------------------------------------------------ animação
def motion_frame(i, t):
    W, H = 1920, 1080
    ed, eb = emblem("url(#foil)", uid=f"Am", bg="#4a1512", draw=ease_in_out(seg(t, 0.0, 0.42)),
                    ring_rot=-50 * (1 - ease_out(seg(t, 0.14, 0.44))), rays=ease_out(seg(t, 0.32, 0.55)),
                    sword=seg(t, 0.5, 0.68), beam=-7 * ease_out(seg(t, 0.62, 0.8)),
                    diamonds=seg(t, 0.2, 0.5), crack=ease_out(seg(t, 0.56, 0.66)))
    hatch, wb, wh = wordmark("url(#foil)", "Amw", 1400)
    glint_x = -400 + 2400 * ease_in_out(seg(t, 0.72, 0.92))
    defs = (foil_defs("foil") + ed + hatch +
            f'<linearGradient id="gl" gradientUnits="userSpaceOnUse" x1="{glint_x - 160}" y1="0" x2="{glint_x + 160}" y2="80">'
            '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff8e0" stop-opacity=".75"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="0" stop-color="#6d211b"/><stop offset="1" stop-color="#2a0b09"/></radialGradient>')
    op = ease(seg(t, 0.66, 0.84))
    body = (f'<rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'<g transform="translate(130 90) scale(0.9)">{eb}</g>'
            f'<g transform="translate({1480 - 700 * 0.56:.1f} {430 + 24 * (1 - op):.1f}) scale(0.56)" opacity="{op:.3f}">{wb}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gl)" style="mix-blend-mode:screen" opacity="{0.9 * (1 - abs(seg(t, .72, .92) * 2 - 1)):.2f}"/>')
    return svg(W, H, body, defs)

if __name__ == "__main__":
    import sys
    ed, eb = emblem(OXBLOOD, uid="A1"); open(f"{OUT}/emblema_apolice.svg", "w").write(svg(1000, 1000, eb, ed))
    to_png(svg(1000, 1000, eb, ed), f"{OUT}/emblema_apolice.png", 2000)
    ed, eb = emblem("url(#foil)", uid="A2", bg=OXBLOOD)
    to_png(svg(1000, 1000, eb, foil_defs("foil") + ed, bg=OXBLOOD), f"{OUT}/emblema_apolice_bronze_sobre_vinho.png", 2000)
    h, wb, wh = wordmark(); open(f"{OUT}/logotipo_apolice.svg", "w").write(svg(1400, wh, wb, h))
    to_png(svg(1400, wh, wb, h, bg=IVORY), f"{OUT}/logotipo_apolice.png", 2800)
    # sinais
    seals = "".join(f'<g transform="translate({60 + (i % 4) * 330} {60 + (i // 4) * 340})">{law_seal(i)}</g>' for i in range(7))
    open(f"{OUT}/sinais_leis_apolice.svg", "w").write(svg(1380, 740, seals, bg=IVORY))
    to_png(svg(1380, 740, seals, bg=IVORY), f"{OUT}/sinais_leis_apolice.png", 2760)
    defs, body = "", ""
    for k, nm in enumerate(["PULSO", "BRASA", "TRAMA", "CLARÃO", "ECO", "CARGA"]):
        cp, b = principle_swatch(nm, GREEN, 150 + k * 300, 160, 120, f"pa{k}")
        defs += cp; body += b
    to_png(svg(1800, 360, body, defs, bg=IVORY), f"{OUT}/sinais_principios_apolice.png", 3600)
    open(f"{OUT}/sinais_principios_apolice.svg", "w").write(svg(1800, 360, body, defs, bg=IVORY))
    to_png(endpaper(), f"{OUT}/guarda_apolice.png", 3200)
    to_png(cover("tecido"), f"{OUT}/capa_tecido_bronze.png", 1600)
    to_png(cover_jacket(), f"{OUT}/sobrecapa_apolice.png", 1600)
    to_png(chapter_page(), f"{OUT}/abertura_capitulo.png", 1600)
    if "--motion" in sys.argv:
        animate(motion_frame, 240, f"{OUT}/animacao_apolice.mp4", gif=f"{OUT}/animacao_apolice.gif")
    print("A ok")
