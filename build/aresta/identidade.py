#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IDENTIDADE ARESTA — emblema, lettering e variantes de Leis para Matar Deuses.
Direção a partir das referências do autor (build/referencias_autor/): arco-limiar, espada vertical com as
sete pérolas das leis, balança na guarda (prato esquerdo mais baixo), faixa carmim, sol de inverno rachado,
ouro envelhecido sobre negro mineral. Tudo vetorial; texto sempre em curvas."""
import math, os, re, sys
sys.path.insert(0, "/home/user/LTKG/build/visual")
from kit import *

OUT = "/home/user/LTKG/exportacoes/identidade_aresta"
os.makedirs(f"{OUT}/logo", exist_ok=True)

# ------------------------------------------------------------------ paleta-base
NEGRO, GRAFITE, PEDRA = "#0D0C0B", "#1C1B1A", "#2B2926"
OURO, OURO_ESC, BRONZE = "#C9A15A", "#7A5A2A", "#9C6F38"
MARFIM, PRATA, AZUL, CARMIM = "#EFE8DA", "#B9BEC5", "#1E3A5C", "#8E1B22"
PAL = [(NEGRO, "Negro mineral"), (GRAFITE, "Grafite"), (PEDRA, "Pedra vulcânica"), (OURO, "Ouro envelhecido"),
       (BRONZE, "Bronze trabalhado"), (MARFIM, "Marfim"), (PRATA, "Prata fria"), (AZUL, "Azul profundo"), (CARMIM, "Vermelho mineral")]

BOLD, SEMI, REG = "Cinzel-Bold.ttf", "Cinzel-SemiBold.ttf", "Cinzel-Regular.ttf"

def metal_defs(p=""):
    """Gradientes metálicos em espaço de usuário 0..1000 (emblema) — ouro, prata, carmim, pérola."""
    return (lin_grad(f"{p}ouro", [(0, "#F6E7B8"), (.18, "#D9B670"), (.42, "#8E672F"), (.6, "#E3C47E"), (.8, "#9A7235"), (1, "#F0D898")], user=(150, 80, 850, 1100))
            + lin_grad(f"{p}ouroB", [(0, "#B8904A"), (.5, "#6F4F22"), (1, "#A8803E")], user=(150, 80, 850, 1100))
            + lin_grad(f"{p}prata", [(0, "#F4F6F8"), (.3, "#A9AFB7"), (.55, "#5D636B"), (.75, "#D3D8DE"), (1, "#7E858E")], user=(200, 100, 800, 1050))
            + lin_grad(f"{p}carmim", [(0, "#3E070B"), (.3, "#8E1B22"), (.5, "#B3303A"), (.7, "#8E1B22"), (1, "#3A0609")], user=(444, 0, 556, 0))
            + f'<radialGradient id="{p}perola" cx="38%" cy="32%" r="70%"><stop offset="0" stop-color="#FFFDF6"/>'
              f'<stop offset=".45" stop-color="#E8DFCB"/><stop offset="1" stop-color="#9C8F78"/></radialGradient>'
            + f'<radialGradient id="{p}raio" cx="500" cy="430" r="560" gradientUnits="userSpaceOnUse"><stop offset=".45" stop-color="#fff"/>'
              f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')

# ------------------------------------------------------------------ geometria do emblema (canvas 1000 × 1160)
CX = 500
SPRING, D_ARC, R_OUT, BAND = 560, 234.2, 472.2, 40
GUARD_Y, BEAM_DEG, BEAM_L, PLATE = 520, -6.0, 330, 190
PEARLS = [590 + k * 68 for k in range(7)]

def arc_pts(R, a0, a1, cx, cy, n=60):
    return [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def ogive(R, leg_bottom, spring=SPRING):
    """Arco ogival: lado esquerdo (arco centrado à direita) e lado direito; devolve pontos do contorno de cima a baixo."""
    cxr, cxl = CX + D_ARC, CX - D_ARC
    apex_y = spring - math.sqrt(R * R - D_ARC * D_ARC)
    aL = math.degrees(math.atan2(apex_y - spring, CX - cxr))      # ângulo do ápice visto do centro direito
    left = arc_pts(R, 180, 360 + aL if aL < 0 else aL, cxr, spring)  # da perna esquerda (180°) ao ápice
    left = [p for p in left]
    aR = math.degrees(math.atan2(apex_y - spring, CX - cxl))
    right = arc_pts(R, aR, 0, cxl, spring)                         # do ápice à perna direita
    lx, rx = cxr - R, cxl + R
    return [(lx, leg_bottom)] + left + right[1:] + [(rx, leg_bottom)], apex_y

def arch_band():
    outer, apex_o = ogive(R_OUT, 1010)
    inner, apex_i = ogive(R_OUT - BAND, 1010)
    d = polyline(outer) + " " + polyline(inner[::-1]) + " Z"
    return d, outer, inner, apex_o, apex_i

def rot_pt(px, py, gx=CX, gy=GUARD_Y, deg=BEAM_DEG):
    g = math.radians(deg); dx, dy = px - gx, py - gy
    return gx + dx * math.cos(g) - dy * math.sin(g), gy + dx * math.sin(g) + dy * math.cos(g)

def engraved_disc(cx, cy, R, gap=4.4):
    lx, ly, lz = -0.5, -0.62, 0.6
    out = []; y = cy - R + gap / 2
    while y < cy + R:
        h = math.sqrt(max(R * R - (y - cy) ** 2, 0)); n = max(8, int(h / 3)); top, bot = [], []
        for i in range(n + 1):
            x = cx - h + 2 * h * i / n
            nx, ny = (x - cx) / R, (y - cy) / R; nz = math.sqrt(max(1 - nx * nx - ny * ny, 0))
            th = min(0.5 + 2.8 * (1 - clamp(nx * lx + ny * ly + nz * lz)) ** 1.25, gap * .9)
            top.append((x, y - th / 2)); bot.append((x, y + th / 2))
        out.append(polyline(top + bot[::-1], True)); y += gap
    return " ".join(out)

SUN = (CX, 410, 104)
CRACK = [(418, 330), (452, 372), (440, 396), (478, 424), (468, 446), (512, 470), (548, 486), (540, 506), (586, 528)]

def layers(fill, mono=False, p=""):
    """Camadas do emblema, de trás para frente: (svg, silhueta para recorte das camadas de baixo, folga)."""
    F = lambda k: fill[k]
    L = []
    # 1. raios
    rays = []
    for a in range(0, 360, 3):
        long_ = a % 15 == 0
        r0, r1 = 300, (560 if long_ else 470)
        x0, y0 = polar(CX, 430, r0, a); x1, y1 = polar(CX, 430, r1, a)
        rays.append(f'M{P(x0, y0)} L{P(x1, y1)}')
    spikes = []
    for a in (-90 + k * 45 for k in range(8)):
        if a in (-90, 90):
            continue
        b = polar(CX, 430, 250, a - 1.6), polar(CX, 430, 600, a), polar(CX, 430, 250, a + 1.6)
        spikes.append(f'<polygon points="{" ".join(P(*q) for q in b)}"/>')
    L.append((f'<g mask="url(#{p}mraio)"><path d="{" ".join(rays)}" stroke="{F("raio")}" stroke-width="1.3" fill="none"/>'
              f'<g fill="{F("raio")}">{"".join(spikes)}</g></g>', "", 0))
    # 2. faixa carmim (estandarte), com rabo de andorinha
    bx0, bx1, by0, by1, notch = 426, 574, 236, 1090, 54
    ban = f"{bx0},{by0} {bx1},{by0} {bx1},{by1} {CX},{by1 - notch} {bx0},{by1}"
    if mono:
        hat = "".join(f'<line x1="{x}" y1="{by0}" x2="{x}" y2="{by1}"/>' for x in range(bx0 + 4, bx1, 7))
        bsvg = (f'<clipPath id="{p}cb"><polygon points="{ban}"/></clipPath><g clip-path="url(#{p}cb)" stroke="{F("faixa")}" stroke-width="2.6">{hat}</g>'
                f'<polygon points="{ban}" fill="none" stroke="{F("faixa")}" stroke-width="3"/>')
    else:
        bsvg = (f'<polygon points="{ban}" fill="{F("faixa")}"/>'
                f'<path d="M{bx0 + 22},{by0} L{bx0 + 22},{by1 - 6} M{bx1 - 22},{by0} L{bx1 - 22},{by1 - 6}" stroke="#000" stroke-opacity=".28" stroke-width="5"/>'
                f'<polygon points="{ban}" fill="none" stroke="{F("filete")}" stroke-width="2.4"/>')
    L.append((bsvg, f'<polygon points="{ban}"/>', 7))
    # 3. sol de inverno rachado: coroa de espigões + disco gravado (metades deslocadas)
    sx, sy, sr = SUN
    sp = "".join(f'<polygon points="{P(*polar(sx, sy, sr + 10, k * 360 / 28 - 3))} {P(*polar(sx, sy, sr + (46 if k % 2 == 0 else 30), k * 360 / 28))} '
                 f'{P(*polar(sx, sy, sr + 10, k * 360 / 28 + 3))}"/>' for k in range(28))
    top_poly = " ".join(P(*q) for q in [(380, 280), (640, 280), (640, 528)] + CRACK[::-1] + [(380, 330)])
    bot_poly = " ".join(P(*q) for q in [(380, 330)] + CRACK + [(640, 528), (640, 540), (380, 540)])
    disc = engraved_disc(sx, sy, sr)
    ssvg = (f'<g fill="{F("sol")}">{sp}</g><circle cx="{sx}" cy="{sy}" r="{sr + 6}" fill="none" stroke="{F("sol")}" stroke-width="3"/>'
            f'<clipPath id="{p}st"><polygon points="{top_poly}"/></clipPath><clipPath id="{p}sb"><polygon points="{bot_poly}"/></clipPath>'
            f'<path d="{disc}" fill="{F("sol")}" clip-path="url(#{p}st)"/>'
            f'<g transform="translate(3 5)"><path d="{disc}" fill="{F("sol")}" clip-path="url(#{p}sb)"/></g>')
    L.append((ssvg, f'<circle cx="{sx}" cy="{sy}" r="{sr + 48}"/>', 6))
    # 4. arco-limiar com crescentes e florão
    d, outer, inner, apex_o, apex_i = arch_band()
    ticks = []
    cxr, cxl = CX + D_ARC, CX - D_ARC
    aL = 360 + math.degrees(math.atan2(apex_o - SPRING, CX - cxr)); aR = math.degrees(math.atan2(apex_o - SPRING, CX - cxl))
    for k in range(1, 12):
        for ccx, a in ((cxr, 180 + (aL - 180) * k / 12), (cxl, aR * (1 - k / 12))):
            ticks.append(f'M{P(*polar(ccx, SPRING, R_OUT - 4, a))} L{P(*polar(ccx, SPRING, R_OUT - BAND + 4, a))}')
    for x0 in (CX - 238, CX + 198):
        for yy in range(600, 1000, 44):
            ticks.append(f'M{x0 + 4},{yy} L{x0 + 36},{yy}')
    mid, _ = ogive(R_OUT - BAND / 2, 1004)
    fin = f"{CX},{apex_o - 62} {CX + 15},{apex_o - 30} {CX},{apex_o + 6} {CX - 15},{apex_o - 30}"
    cres = ""
    for side in (-1, 1):
        x = CX + side * 298; y = 420
        R1, R2 = 62, 78
        sw_o = 0 if side < 0 else 1
        cres += (f'<path d="M{x},{y - R1} A{R1},{R1} 0 1,{sw_o} {x},{y + R1} A{R2},{R2} 0 0,{1 - sw_o} {x},{y - R1} Z" '
                 f'transform="translate({side * 2} 0)" fill="{F("arco_borda")}"/>'
                 f'<circle cx="{x + side * 18}" cy="{y}" r="11" fill="{F("arco_borda")}"/>')
    plinths = "".join(f'<rect x="{x}" y="1010" width="64" height="26" fill="{F("arco_borda")}"/>' for x in (CX - 250, CX + 186))
    if mono:
        asvg = (f'<path d="{d}" fill="{F("arco")}" fill-rule="evenodd"/>'
                f'<path d="{polyline(mid)}" fill="none" stroke="{F("bg_line")}" stroke-width="2.2"/>{cres}{plinths}'
                f'<polygon points="{fin}" fill="{F("arco")}"/>')
    else:
        asvg = (f'<path d="{d}" fill="{F("arco")}" fill-rule="evenodd"/>'
                f'<path d="{" ".join(ticks)}" stroke="#000" stroke-opacity=".35" stroke-width="1.6"/>'
                f'<path d="{polyline(outer)}" fill="none" stroke="{F("arco_borda")}" stroke-width="3.5"/>'
                f'<path d="{polyline(inner)}" fill="none" stroke="{F("arco_borda")}" stroke-width="3.5"/>'
                f'<path d="{polyline(mid)}" fill="none" stroke="{F("arco_borda")}" stroke-width="1.2" opacity=".8"/>'
                f'{cres}{plinths}<polygon points="{fin}" fill="{F("arco_borda")}"/>')
    sil_arch = (f'<path d="{d}" fill-rule="evenodd"/>{cres.replace(chr(34) + F("arco_borda") + chr(34), chr(34) + "#000" + chr(34))}'
                f'<polygon points="{fin}"/>')
    L.append((asvg, sil_arch, 6))
    # 5. balança: travessão (guarda), correntes e pratos — prato esquerdo mais baixo
    bal, sil_b = [], []
    top = [rot_pt(CX - BEAM_L, GUARD_Y - 9), rot_pt(CX + BEAM_L, GUARD_Y - 9), rot_pt(CX + BEAM_L, GUARD_Y + 9), rot_pt(CX - BEAM_L, GUARD_Y + 9)]
    beam = " ".join(P(*q) for q in top)
    bal.append(f'<polygon points="{beam}" fill="{F("ouro")}"/>')
    hl = [rot_pt(CX - BEAM_L + 20, GUARD_Y - 3), rot_pt(CX + BEAM_L - 20, GUARD_Y - 3)]
    if not mono:
        bal.append(f'<line x1="{hl[0][0]:.1f}" y1="{hl[0][1]:.1f}" x2="{hl[1][0]:.1f}" y2="{hl[1][1]:.1f}" stroke="#FFF4D6" stroke-opacity=".55" stroke-width="2"/>')
    sil_b.append(f'<polygon points="{beam}"/>')
    for side in (-1, 1):
        ex, ey = rot_pt(CX + side * BEAM_L, GUARD_Y)
        py = ey + PLATE; hw = 74
        bal.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="14" fill="{F("ouro")}"/>')
        sil_b.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="14"/>')
        for k in (-1, 0, 1):
            bal.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex + k * (hw - 10):.1f}" y2="{py:.1f}" stroke="{F("ouro")}" stroke-width="2.2"/>')
        bowl = f'M{ex - hw:.1f},{py:.1f} Q{ex:.1f},{py + 58:.1f} {ex + hw:.1f},{py:.1f} Z'
        bal.append(f'<path d="{bowl}" fill="{F("ouro")}"/><line x1="{ex - hw - 6:.1f}" y1="{py:.1f}" x2="{ex + hw + 6:.1f}" y2="{py:.1f}" stroke="{F("ouro")}" stroke-width="4"/>')
        if not mono:
            bal.append(f'<path d="M{ex - hw + 14:.1f},{py + 7:.1f} Q{ex:.1f},{py + 42:.1f} {ex + hw - 14:.1f},{py + 7:.1f}" fill="none" stroke="#FFF4D6" stroke-opacity=".45" stroke-width="1.6"/>')
        sil_b.append(f'<path d="{bowl}"/><rect x="{ex - hw - 6:.1f}" y="{py - 3:.1f}" width="{2 * hw + 12}" height="6"/>')
    L.append(("".join(bal), "".join(sil_b), 7))
    # 6. espada: pomo, punho, quillon, lâmina em bisel com as sete pérolas
    sw, sil_s = [], []
    sw.append(f'<polygon points="{CX},{196} {CX + 22},{226} {CX},{256} {CX - 22},{226}" fill="{F("ouro")}"/>')
    sw.append(f'<rect x="{CX - 13}" y="256" width="26" height="246" fill="{F("ouro")}"/>')
    if not mono:
        sw.append("".join(f'<path d="M{CX - 13},{yy + 6} L{CX + 13},{yy}" stroke="#3A2A12" stroke-opacity=".55" stroke-width="2"/>' for yy in range(266, 496, 10)))
    else:
        sw.append("".join(f'<path d="M{CX - 13},{yy + 6} L{CX + 13},{yy}" stroke="{F("bg_line")}" stroke-width="2.2"/>' for yy in range(266, 496, 12)))
    sw.append(f'<rect x="{CX - 22}" y="250" width="44" height="10" fill="{F("ouro")}"/>')
    sw.append(f'<polygon points="{CX - 40},{GUARD_Y} {CX},{GUARD_Y - 26} {CX + 40},{GUARD_Y} {CX},{GUARD_Y + 30}" fill="{F("ouro")}"/>')
    blade_l = f"{CX - 26},{GUARD_Y + 14} {CX},{GUARD_Y + 14} {CX},{1128} {CX - 26},{1010}"
    blade_r = f"{CX},{GUARD_Y + 14} {CX + 26},{GUARD_Y + 14} {CX + 26},{1010} {CX},{1128}"
    sw.append(f'<polygon points="{blade_l}" fill="{F("lamina_l")}"/><polygon points="{blade_r}" fill="{F("lamina_r")}"/>')
    for k, y in enumerate(PEARLS):
        sw.append(f'<circle cx="{CX}" cy="{y}" r="24" fill="{F("encaixe")}"/><circle cx="{CX}" cy="{y}" r="22" fill="none" stroke="{F("ouro")}" stroke-width="2.4"/>')
        sw.append(f'<circle cx="{CX}" cy="{y}" r="17.5" fill="{F("perola")}"/>')
    sil_s.append(f'<polygon points="{CX},{196} {CX + 22},{226} {CX},{256} {CX - 22},{226}"/><rect x="{CX - 22}" y="250" width="44" height="252"/>'
                 f'<polygon points="{CX - 40},{GUARD_Y} {CX},{GUARD_Y - 26} {CX + 40},{GUARD_Y} {CX},{GUARD_Y + 30}"/>'
                 f'<polygon points="{CX - 26},{GUARD_Y + 14} {CX + 26},{GUARD_Y + 14} {CX + 26},1010 {CX},1128 {CX - 26},1010"/>'
                 + "".join(f'<circle cx="{CX}" cy="{y}" r="24"/>' for y in PEARLS))
    sw_svg = "".join(sw)
    if mono:   # pérolas em uma tinta: anel vazado de verdade (funciona também com fundo transparente)
        rings = "".join(f'<circle cx="{CX}" cy="{y}" r="20" fill="none" stroke="black" stroke-width="3.2"/>' for y in PEARLS)
        sw_svg = (f'<mask id="{p}mpr" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1160"><rect width="1000" height="1160" fill="#fff"/>'
                  f'{rings}</mask><g mask="url(#{p}mpr)">{sw_svg}</g>')
    L.append((sw_svg, "".join(sil_s), 7))
    return L

def emblem(style="ouro", p="e", bg=None):
    """style: ouro (metal sobre escuro) · plano (cores chapadas) · mono (uma tinta: fill=ink)."""
    if style == "ouro":
        fill = dict(raio=f"url(#{p}ouro)", faixa=f"url(#{p}carmim)", filete=f"url(#{p}ouro)", sol=f"url(#{p}ouro)",
                    arco=f"url(#{p}prata)", arco_borda=f"url(#{p}ouro)", ouro=f"url(#{p}ouro)", lamina_l=f"url(#{p}ouro)",
                    lamina_r=f"url(#{p}ouroB)", encaixe="#3A2A12", perola=f"url(#{p}perola)", bg_line="#000")
        mono = False
    elif style == "plano":
        fill = dict(raio=OURO, faixa=CARMIM, filete=OURO, sol=OURO, arco="#8D939B", arco_borda=OURO, ouro=OURO,
                    lamina_l="#D8B672", lamina_r="#A47B3C", encaixe="#4A3518", perola=MARFIM, bg_line="#000")
        mono = False
    else:
        ink = style.split(":")[1] if ":" in style else NEGRO
        fill = {k: ink for k in ("raio", "faixa", "filete", "sol", "arco", "arco_borda", "ouro", "lamina_l", "lamina_r", "perola")}
        fill["encaixe"] = ink; fill["bg_line"] = "#000"
        mono = True
    L = layers(fill, mono, p)
    defs = metal_defs(p) + (f'<mask id="{p}mraio" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1160">'
                            f'<rect width="1000" height="1160" fill="url(#{p}raio)"/></mask>')
    body = []
    for i, (s, sil, gap) in enumerate(L):
        above = [(sl, g) for (_, sl, g) in L[i + 1:] if sl]
        if above:
            m = (f'<mask id="{p}k{i}" maskUnits="userSpaceOnUse" x="-50" y="-50" width="1100" height="1260">'
                 f'<rect x="-50" y="-50" width="1100" height="1260" fill="#fff"/>'
                 + "".join(f'<g fill="#000" stroke="#000" stroke-width="{2 * g}" stroke-linejoin="round">{sl}</g>' for sl, g in above) + '</mask>')
            defs += m
            body.append(f'<g mask="url(#{p}k{i})">{s}</g>')
        else:
            body.append(s)
    out = "".join(body)
    if mono:
        # linhas internas (sulcos) viram recorte verdadeiro: transparentes, não pretas
        out = out.replace('stroke="#000"', f'stroke="{bg or "#000"}"')
        if not bg:
            out = re.sub(r'<path d="([^"]+)" fill="none" stroke="#000" stroke-width="2\.2"/>', "", out)
    return defs, out

EW, EH = 1000, 1160

# ------------------------------------------------------------------ lettering
def blade_I(x, base, size):
    """O 'I' de LEIS desenhado como espada de ponta para baixo (lâmina = haste da letra)."""
    s = size / 1000
    cx = x + 194 * s; st = 58 * s; cap = 700 * s
    g = base - cap + 70 * s
    parts = [f"M{cx - st},{g + 26 * s} L{cx + st},{g + 26 * s} L{cx + st},{base - 40 * s} L{cx},{base + 70 * s} L{cx - st},{base - 40 * s} Z",
             f"M{cx - 150 * s},{g} L{cx + 150 * s},{g} L{cx + 150 * s},{g + 26 * s} L{cx - 150 * s},{g + 26 * s} Z",
             f"M{cx - 26 * s},{g} L{cx + 26 * s},{g} L{cx + 26 * s},{base - cap - 70 * s} L{cx - 26 * s},{base - cap - 70 * s} Z",
             f"M{cx},{base - cap - 160 * s} L{cx + 44 * s},{base - cap - 105 * s} L{cx},{base - cap - 50 * s} L{cx - 44 * s},{base - cap - 105 * s} Z"]
    return " ".join(parts), 387 * s

def word(text, font, size, x, y, tracking=0.0, blade_at=None):
    """Palavra em curvas; blade_at = índice da letra I a trocar pela espada."""
    d = []; cx = x
    for i, ch in enumerate(text):
        if blade_at is not None and i == blade_at:
            bd, adv = blade_I(cx, y, size); d.append(bd); cx += adv + tracking * size
            continue
        d.append(text_path(ch, font, size, cx, y)); cx += text_width(ch, font, size) + tracking * size
    return " ".join(d), cx - x - tracking * size

def wordmark(fill="url(#wouro)", shade="#5A3F17", W=1600, sub="SAGA", sub2="ARESTA", crack=True, p="w"):
    """LEIS PARA / MATAR DEUSES / ◆ SAGA ◆ ARESTA ◆ — com fratura em DEUSES."""
    S2 = (W - 110) / (text_width("MATAR DEUSES", BOLD, 1000, 0.03) / 1000); S1 = S2
    w_leis = word("LEIS", BOLD, S1, 0, 0, 0.03, blade_at=2)[1]
    PS = S1 * .46; w_para = text_width("PARA", BOLD, PS, 0.08)
    gap = 34
    tot1 = w_leis + gap + w_para
    x1 = (W - tot1) / 2; y1 = 250
    d_leis, _ = word("LEIS", BOLD, S1, x1, y1, 0.03, blade_at=2)
    d_para = text_path("PARA", BOLD, PS, x1 + w_leis + gap, y1 - .7 * S1 + .7 * PS, 0.08)
    w2 = text_width("MATAR DEUSES", BOLD, S2, 0.03)
    x2 = (W - w2) / 2; y2 = y1 + 1.2 * S1
    d_2 = text_path("MATAR DEUSES", BOLD, S2, x2, y2, 0.03)
    xd = x2 + text_width("MATAR ", BOLD, S2, 0.03)
    # fratura: linha quebrada que atravessa o D de DEUSES; a parte de baixo desliza
    k_ = S2 / 210
    cr = [(xd + 30 * k_, y2 - 170 * k_), (xd + 70 * k_, y2 - 110 * k_), (xd + 52 * k_, y2 - 82 * k_), (xd + 96 * k_, y2 - 34 * k_), (xd + 84 * k_, y2 + 14 * k_)]
    left = " ".join(P(*q) for q in [(x2 - 20, y2 - 200)] + cr + [(x2 - 20, y2 + 40)])
    right = " ".join(P(*q) for q in [(x2 + w2 + 40, y2 - 200)] + cr + [(x2 + w2 + 40, y2 + 40)])
    defs = (lin_grad(f"{p}ouro", [(0, "#F6E7B8"), (.22, "#DDBB74"), (.48, "#94692F"), (.62, "#E7CB86"), (.82, "#A27A3B"), (1, "#F1D99A")], user=(0, 80, 0, 520))
            + f'<clipPath id="{p}cl"><polygon points="{left}"/></clipPath><clipPath id="{p}cr"><polygon points="{right}"/></clipPath>')
    def layer(f, dx=0, dy=0):
        l2 = (f'<path d="{d_2}" fill="{f}" clip-path="url(#{p}cl)"/><g transform="translate(3 4)"><path d="{d_2}" fill="{f}" clip-path="url(#{p}cr)"/></g>'
              if crack else f'<path d="{d_2}" fill="{f}"/>')
        return f'<g transform="translate({dx} {dy})"><path d="{d_leis}" fill="{f}"/><path d="{d_para}" fill="{f}"/>{l2}</g>'
    body = (layer(shade, 0, 5) if shade else "") + layer(fill)
    # linha da saga
    ys = y2 + 90
    d_s = text_path(f"{sub}", SEMI, 46, W / 2 - 40, ys, 0.34, "end")
    d_a = text_path(f"{sub2}", SEMI, 46, W / 2 + 40, ys, 0.34, "start")
    ws_ = text_width(sub2, SEMI, 46, 0.34)
    dia = lambda x, y, r: f'<polygon points="{x},{y - r} {x + r * .62},{y} {x},{y + r} {x - r * .62},{y}" fill="{fill}"/>'
    l0, l1 = x2 + 10, W / 2 - 40 - text_width(sub, SEMI, 46, 0.34) - 34
    r0, r1 = W / 2 + 40 + ws_ + 34, x2 + w2 - 10
    body += (f'<path d="{d_s}" fill="{fill}"/><path d="{d_a}" fill="{fill}"/>' + dia(W / 2, ys - 17, 13)
             + f'<rect x="{l0}" y="{ys - 18.5}" width="{l1 - l0}" height="3" fill="{fill}"/>' + dia(l0, ys - 17, 9)
             + f'<rect x="{r0}" y="{ys - 18.5}" width="{r1 - r0}" height="3" fill="{fill}"/>' + dia(r1, ys - 17, 9))
    return defs, body, (W, 640)

def monogram(fill, p="m"):
    """Monograma compacto: L · espada · D dentro do arco-limiar — para lombada, selo, favicon."""
    d, outer, inner, apex_o, apex_i = arch_band()
    size = 330; base = 930
    wl = text_width("L", BOLD, size); 
    L = text_path("L", BOLD, size, 474 - wl, base); D = text_path("D", BOLD, size, 526, base)
    bd, _ = blade_I(500 - 194 * .6, base, 600)
    sx, sy, sr = SUN
    sp = "".join(f'<polygon points="{P(*polar(sx, sy, sr + 10, k * 360 / 28 - 3))} {P(*polar(sx, sy, sr + (46 if k % 2 == 0 else 30), k * 360 / 28))} '
                 f'{P(*polar(sx, sy, sr + 10, k * 360 / 28 + 3))}"/>' for k in range(28))
    return (f'<path d="{d}" fill="{fill}" fill-rule="evenodd"/><g fill="{fill}" opacity=".9">{sp}</g>'
            f'<path d="{L}" fill="{fill}"/><path d="{D}" fill="{fill}"/><path d="{bd}" fill="{fill}"/>')

# ------------------------------------------------------------------ saídas
def save(name, w, h, body, defs="", bg=None, png_w=None):
    s = svg(w, h, body, defs, bg=bg)
    open(f"{OUT}/logo/{name}.svg", "w", encoding="utf-8").write(s)
    to_png(s, f"{OUT}/logo/{name}.png", png_w or w * 2)
    return s

def lockup_vertical(style, bg, wfill, wshade, p):
    ed, eb = emblem(style, p, bg)
    wd, wb, (ww, wh) = wordmark(wfill, wshade, p=p + "w")
    W, H = 1600, 2040
    return W, H, (f'<g transform="translate({(W - EW * 1.12) / 2} 40) scale(1.12)">{eb}</g>'
                  f'<g transform="translate(0 {1360})">{wb}</g>'), ed + wd

def lockup_horizontal(style, bg, wfill, wshade, p):
    ed, eb = emblem(style, p, bg)
    wd, wb, (ww, wh) = wordmark(wfill, wshade, p=p + "w")
    W, H = 2500, 860
    return W, H, (f'<g transform="translate(60 40) scale(0.67)">{eb}</g>'
                  f'<g transform="translate(760 120) scale(1.0)">{wb}</g>'), ed + wd

if __name__ == "__main__":
    variants = [  # nome, estilo do emblema, fundo, preenchimento do lettering, sombra
        ("principal_ouro_sobre_negro", "ouro", NEGRO, "url(#{p}wouro)", "#4A3413"),
        ("transparente_ouro", "ouro", None, "url(#{p}wouro)", "#4A3413"),
        ("plano_cores", "plano", NEGRO, OURO, None),
        ("monocromatico_tinta", f"mono:{NEGRO}", MARFIM, NEGRO, None),
        ("negativo_marfim", f"mono:{MARFIM}", NEGRO, MARFIM, None),
        ("hot_stamping_uma_cor", f"mono:{NEGRO}", None, NEGRO, None),
    ]
    for name, st, bg, wf, sh in variants:
        p = "v" + name[:3]
        W, H, body, defs = lockup_vertical(st, bg, wf.format(p=p), sh, p)
        save(f"logo_vertical_{name}", W, H, body, defs, bg)
        W, H, body, defs = lockup_horizontal(st, bg, wf.format(p=p), sh, p)
        save(f"logo_horizontal_{name}", W, H, body, defs, bg)
        ed, eb = emblem(st, p + "e", bg)
        save(f"simbolo_{name}", EW, EH, eb, ed, bg)
        wd, wb, (ww, wh) = wordmark(wf.format(p=p + "x"), sh, p=p + "xw")
        save(f"lettering_{name}", ww, wh, wb, wd, bg)
    save("monograma_ouro_sobre_negro", 1000, 1160, monogram(OURO), "", NEGRO)
    save("monograma_tinta", 1000, 1160, monogram(NEGRO), "", None)
    print("identidade ok")
