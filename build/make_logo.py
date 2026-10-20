#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identidade visual da saga *Leis para Matar Deuses*: emblema + logotipo (SVG em curvas e PNG).

Emblema: anel com sete losangos (as sete leis), um sol de inverno rachado (as Coroas),
uma espada vertical cuja guarda é o travessão de uma balança com um prato mais baixo
(a Arte do Carrasco). Tudo em curvas: os SVG não dependem de fontes instaladas.
"""
import math, os
from vetor import text_path, text_width, svg_to_png

OUT = "/home/user/LTKG/exportacoes/grafico/logo"
os.makedirs(OUT, exist_ok=True)

BRONZE = "#B48C4E"
BRONZE_GRAD = [("0", "#F0D9A4"), ("0.35", "#C79A55"), ("0.7", "#8E6430"), ("1", "#D7B271")]
INK = "#1E1A16"
PALE = "#EFE8D8"
NIGHT = "#10141C"

def emblem(fill, uid="e"):
    """Retorna (defs, corpo) do emblema num quadro 0..1000."""
    cx = cy = 500
    parts = []
    # anel e losangos
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="440" fill="none" stroke="{fill}" stroke-width="7"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="412" fill="none" stroke="{fill}" stroke-width="2.4"/>')
    for k in range(7):
        a = -math.pi / 2 + k * 2 * math.pi / 7
        x, y = cx + 440 * math.cos(a), cy + 440 * math.sin(a)
        ca, sa = math.cos(a), math.sin(a)
        r1, r2 = 24, 13  # semidiagonal radial e tangencial
        pts = [(x + ca * r1, y + sa * r1), (x - sa * r2, y + ca * r2),
               (x - ca * r1, y - sa * r1), (x + sa * r2, y - ca * r2)]
        parts.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{px:.1f},{py:.1f}" for px, py in pts), fill))
    # raios do sol (pulando os que cruzariam a espada e o travessão)
    for k in range(24):
        a = k * 2 * math.pi / 24
        deg = math.degrees(a) % 360
        if min(abs(deg - 90), abs(deg - 270)) < 31:
            continue
        r0, r1 = 168, (206 if k % 2 == 0 else 190)
        hw = math.radians(3.2)
        p0 = (cx + r0 * math.cos(a - hw), cy + r0 * math.sin(a - hw))
        p1 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        p2 = (cx + r0 * math.cos(a + hw), cy + r0 * math.sin(a + hw))
        parts.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{px:.1f},{py:.1f}" for px, py in (p0, p1, p2)), fill))
    # lâmina (usada no desenho e como recorte no disco)
    blade = "486,336 514,336 514,768 500,884 486,768"
    crack = "372,404 446,470 428,500 522,562 506,594 628,652"
    defs = f'''<mask id="{uid}-disk" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">
      <rect width="1000" height="1000" fill="white"/>
      <polyline points="{crack}" fill="none" stroke="black" stroke-width="13" stroke-linejoin="miter"/>
      <polygon points="{blade}" fill="black" stroke="black" stroke-width="22" stroke-linejoin="miter"/>
    </mask>'''
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="146" fill="{fill}" mask="url(#{uid}-disk)"/>')
    # espada: pomo, punho, lâmina com sulco
    parts.append(f'<circle cx="500" cy="128" r="21" fill="{fill}"/>')
    parts.append(f'<rect x="491" y="146" width="18" height="150" fill="{fill}"/>')
    for yy in range(160, 290, 22):
        parts.append(f'<rect x="485" y="{yy}" width="30" height="6" fill="{fill}"/>')
    parts.append(f'<polygon points="{blade}" fill="{fill}"/>')
    # travessão-balança (guarda), inclinado: o prato da esquerda pesa mais
    ang = math.radians(-7)
    L = 300
    gx, gy = 500, 316
    def rot(px, py):
        dx, dy = px - gx, py - gy
        return (gx + dx * math.cos(ang) - dy * math.sin(ang), gy + dx * math.sin(ang) + dy * math.cos(ang))
    beam = [rot(gx - L, gy - 8), rot(gx + L, gy - 8), rot(gx + L, gy + 8), rot(gx - L, gy + 8)]
    parts.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{px:.1f},{py:.1f}" for px, py in beam), fill))
    parts.append(f'<polygon points="472,316 500,300 528,316 500,346" fill="{fill}"/>')
    for side in (-1, 1):
        ex, ey = rot(gx + side * L, gy)
        parts.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="11" fill="{fill}"/>')
        py = ey + 172
        hw = 62
        parts.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex-hw+6:.1f}" y2="{py:.1f}" stroke="{fill}" stroke-width="3.2"/>')
        parts.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex+hw-6:.1f}" y2="{py:.1f}" stroke="{fill}" stroke-width="3.2"/>')
        parts.append(f'<path d="M{ex-hw:.1f},{py:.1f} Q{ex:.1f},{py+46:.1f} {ex+hw:.1f},{py:.1f} Z" fill="{fill}"/>')
    return defs, "\n".join(parts)

def grad_def(uid):
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in BRONZE_GRAD)
    return f'<linearGradient id="{uid}-g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1000" y2="1000">{stops}</linearGradient>'

def wordmark(fill, x_center, y_top, scale=1.0):
    """Devolve caminhos do logotipo: 'LEIS PARA' entre filetes + 'MATAR DEUSES'."""
    s = scale
    out = []
    small, big = 64 * s, 128 * s
    y1 = y_top + small
    w1 = text_width("LEIS PARA", "Cinzel-Regular.ttf", small, 0.32)
    out.append(f'<path d="{text_path("LEIS PARA", "Cinzel-Regular.ttf", small, x_center, y1, 0.32, "middle")}" fill="{fill}"/>')
    gap, rule = 34 * s, 150 * s
    for side in (-1, 1):
        xa = x_center + side * (w1 / 2 + gap)
        xb = xa + side * rule
        xl, xr = min(xa, xb), max(xa, xb)
        out.append(f'<rect x="{xl:.1f}" y="{y1 - small*0.36 - 1.3*s:.1f}" width="{xr-xl:.1f}" height="{2.6*s:.1f}" fill="{fill}"/>')
        xd = xb + side * 14 * s
        yd = y1 - small * 0.36
        d = 9 * s
        out.append(f'<polygon points="{xd-d:.1f},{yd:.1f} {xd:.1f},{yd-d:.1f} {xd+d:.1f},{yd:.1f} {xd:.1f},{yd+d:.1f}" fill="{fill}"/>')
    y2 = y1 + 40 * s + big
    out.append(f'<path d="{text_path("MATAR DEUSES", "Cinzel-Bold.ttf", big, x_center, y2, 0.06, "middle")}" fill="{fill}"/>')
    width = max(w1 + 2 * (gap + rule + 30 * s), text_width("MATAR DEUSES", "Cinzel-Bold.ttf", big, 0.06))
    return "\n".join(out), width, y2 - y_top

def svg_doc(w, h, defs, body, bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs>{defs}</defs>{bgrect}{body}</svg>')

def build(variant, fill_kind, bg=None):
    uid = variant
    fill = f"url(#{uid}-g)" if fill_kind == "grad" else fill_kind
    gd = grad_def(uid) if fill_kind == "grad" else ""
    # --- emblema isolado ---
    ed, eb = emblem(fill, uid + "E")
    gd_e = grad_def(uid + "E") if fill_kind == "grad" else ""
    fillE = f"url(#{uid}E-g)" if fill_kind == "grad" else fill_kind
    ed, eb = emblem(fillE, uid + "E")
    em = svg_doc(1000, 1000, gd_e + ed, eb, bg)
    open(f"{OUT}/emblema_{variant}.svg", "w").write(em)
    svg_to_png(em, f"{OUT}/emblema_{variant}.png", 1000, 1000, transparent=bg is None)
    # --- assinatura vertical: emblema + logotipo ---
    W, H = 1600, 1330
    ed2, eb2 = emblem(fill, uid + "V")
    wm, ww, wh = wordmark(fill, W / 2, 1010, 1.0)
    body = f'<g transform="translate({(W-860)/2},40) scale(0.86)">{eb2}</g>{wm}'
    v = svg_doc(W, H, gd + ed2.replace(f'id="{uid}V-disk"', f'id="{uid}V-disk"'), body, bg)
    # o mask do emblema está em coordenadas do emblema: aplicar o mesmo transform via maskUnits userSpaceOnUse
    v = v.replace(f'<mask id="{uid}V-disk" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">',
                  f'<mask id="{uid}V-disk" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">')
    open(f"{OUT}/logo_vertical_{variant}.svg", "w").write(v)
    svg_to_png(v, f"{OUT}/logo_vertical_{variant}.png", W, H, transparent=bg is None)
    # --- assinatura horizontal ---
    W2, H2 = 2400, 760
    ed3, eb3 = emblem(fill, uid + "H")
    wm2, ww2, wh2 = wordmark(fill, 0, 0, 1.25)
    tx = 760 + 60 + ww2 / 2
    body2 = (f'<g transform="translate(40,40) scale(0.68)">{eb3}</g>'
             f'<g transform="translate({tx:.1f},{(H2 - wh2)/2 - 10:.1f})">{wm2}</g>')
    W2 = int(tx + ww2 / 2 + 60)
    h = svg_doc(W2, H2, gd + ed3, body2, bg)
    open(f"{OUT}/logo_horizontal_{variant}.svg", "w").write(h)
    svg_to_png(h, f"{OUT}/logo_horizontal_{variant}.png", W2, H2, transparent=bg is None)
    # --- só o logotipo (para lombadas e cabeçalhos) ---
    wm3, ww3, wh3 = wordmark(fill, 0, 0, 1.0)
    W3, H3 = int(ww3 + 80), int(wh3 + 80)
    t = svg_doc(W3, H3, gd, f'<g transform="translate({W3/2},40)">{wm3}</g>', bg)
    open(f"{OUT}/logotipo_{variant}.svg", "w").write(t)
    svg_to_png(t, f"{OUT}/logotipo_{variant}.png", W3, H3, transparent=bg is None)

if __name__ == "__main__":
    build("bronze", "grad")          # metálico, fundo transparente
    build("bronze_chapado", BRONZE)  # cor única (impressão em 1 cor / hot stamping)
    build("tinta", INK)              # para fundo claro
    build("claro", PALE)             # para fundo escuro
    build("noturno", "grad", NIGHT)  # vitrine: bronze sobre azul-noite
    print("logos gerados em", OUT)
