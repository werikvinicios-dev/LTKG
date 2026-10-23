"""Mapas da Edição Imersiva, em vetor (SVG), coerentes com o texto (ver plano_edicao/geografia_*.md).
Sem spoilers: só lugares que o leitor conhece até o capítulo 15 e nada do que se descobre depois."""
import math, random
from motor import *

TINTA, TINTA2, PAPEL, GELO, RIO = "#3B2C1C", "#6B5534", "#EBDDBF", "#DCE6EA", "#9FB4BE"
FONTES = (f'<style>@font-face{{font-family:AT;src:url(file://{FON}/ArestaTitular-Bold.ttf);font-weight:700}}'
          f'@font-face{{font-family:ATR;src:url(file://{FON}/ArestaTitular-Regular.ttf)}}'
          f'@font-face{{font-family:SEL;src:url(file://{FON}/Selar-Regular.ttf)}}'
          f'@font-face{{font-family:FELL;src:url(file://{FON}/IMFeFCit28P.ttf)}}</style>')


def ruido(pts, amp, seed, passos=3):
    """Subdivide uma polilinha fechada com deslocamento aleatório (litoral, margens)."""
    rnd = random.Random(seed)
    for _ in range(passos):
        novo = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            k = rnd.uniform(-amp, amp)
            novo += [a, (m[0] - dy / L * k, m[1] + dx / L * k)]
        pts, amp = novo, amp * 0.55
    return pts


def d_de(pts, fechar=True):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + (" Z" if fechar else "")


def montanhas(x0, y0, x1, y1, n, seed, esc=1.0, cor=TINTA):
    rnd = random.Random(seed)
    s = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        w = rnd.uniform(14, 26) * esc; h = w * rnd.uniform(0.8, 1.2)
        s.append(f'<path d="M{x - w:.1f},{y:.1f} L{x:.1f},{y - h:.1f} L{x + w:.1f},{y:.1f}" fill="{PAPEL}" stroke="{cor}" stroke-width="1.3"/>'
                 f'<path d="M{x:.1f},{y - h:.1f} L{x + w * .35:.1f},{y - h * .35:.1f} L{x + w * .1:.1f},{y:.1f}" fill="{cor}" opacity=".35"/>')
    return "".join(sorted(s, key=lambda t: float(t.split(",")[1].split(" ")[0])))


def arvores(x0, y0, x1, y1, n, seed):
    rnd = random.Random(seed)
    return "".join(f'<path d="M{x:.1f},{y:.1f} l-5,10 h10 Z" fill="{TINTA2}" opacity=".7"/>'
                   for x, y in ((rnd.uniform(x0, x1), rnd.uniform(y0, y1)) for _ in range(n)))


def casas(x0, y0, x1, y1, n, seed, cor=TINTA2):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, w, h = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(6, 12), rnd.uniform(4, 8)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{cor}" opacity="{rnd.uniform(.3, .6):.2f}" '
                   f'transform="rotate({rnd.uniform(-10, 10):.1f} {x + w / 2:.1f} {y + h / 2:.1f})"/>')
    return "".join(out)


def rotulo(x, y, t, tam=15, peso=700, cor=TINTA, esp=2, anc="middle", fam="AT", rot=0):
    return (f'<text x="{x}" y="{y}" text-anchor="{anc}" font-family="{fam}" font-weight="{peso}" font-size="{tam}" fill="{cor}" '
            f'letter-spacing="{esp}" transform="rotate({rot} {x} {y})" paint-order="stroke" stroke="{PAPEL}" stroke-width="3">{esc(t)}</text>')


def marca(x, y, n, cor=CARMIM):
    return (f'<circle cx="{x}" cy="{y}" r="11" fill="{PAPEL}" stroke="{cor}" stroke-width="1.8"/>'
            f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-family="AT" font-weight="700" font-size="12" fill="{cor}">{n}</text>')


def rosa(x, y, r=48):
    s = f'<g transform="translate({x},{y})"><circle r="{r}" fill="none" stroke="{TINTA}" stroke-width="1"/><circle r="{r * .78}" fill="none" stroke="{TINTA}" stroke-width=".6" stroke-dasharray="2 4"/>'
    for a, L in ((0, 1), (90, .7), (180, .7), (270, .7), (45, .45), (135, .45), (225, .45), (315, .45)):
        t = math.radians(a - 90)
        p = (math.cos(t) * r * L, math.sin(t) * r * L)
        q1 = (math.cos(t + 1.57) * 6, math.sin(t + 1.57) * 6); q2 = (-q1[0], -q1[1])
        s += f'<path d="M{p[0]:.1f},{p[1]:.1f} L{q1[0]:.1f},{q1[1]:.1f} L0,0 Z" fill="{TINTA}"/><path d="M{p[0]:.1f},{p[1]:.1f} L{q2[0]:.1f},{q2[1]:.1f} L0,0 Z" fill="{PAPEL}" stroke="{TINTA}" stroke-width=".6"/>'
    return s + f'<text y="{-r - 8}" text-anchor="middle" font-family="AT" font-weight="700" font-size="16" fill="{CARMIM}">N</text></g>'


def escala(x, y, px_km, km, rot="km"):
    w = px_km * km
    seg = "".join(f'<rect x="{x + i * w / 4:.1f}" y="{y}" width="{w / 4:.1f}" height="6" fill="{TINTA if i % 2 == 0 else PAPEL}" stroke="{TINTA}" stroke-width=".8"/>' for i in range(4))
    return seg + rotulo(x, y - 6, "0", 10, 400, TINTA, 0, "middle", "ATR") + rotulo(x + w, y - 6, f"{km} {rot}", 10, 400, TINTA, 1, "middle", "ATR")


def moldura(W, H):
    return (f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="none" stroke="{TINTA}" stroke-width="2.4"/>'
            f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" fill="none" stroke="{TINTA}" stroke-width=".8"/>'
            f'<text x="{W / 2}" y="{H - 22}" text-anchor="middle" font-family="SEL" font-size="12" fill="{TINTA2}" letter-spacing="9">VHALESSA ARESTA LEIS PARA MATAR DEUSES</text>')


def cartucho(x, y, w, titulo, sub):
    return (f'<g><rect x="{x - w / 2}" y="{y - 34}" width="{w}" height="62" fill="{PAPEL}" stroke="{TINTA}" stroke-width="1.6"/>'
            f'<rect x="{x - w / 2 + 5}" y="{y - 29}" width="{w - 10}" height="52" fill="none" stroke="{TINTA}" stroke-width=".6"/>'
            + rotulo(x, y, titulo, 24, 700, TINTA, 4) + rotulo(x, y + 18, sub, 10.5, 400, TINTA2, 2, "middle", "ATR") + "</g>")


# ------------------------------------------------------------------ Planta de Vhalessa
LOCAIS_VHALESSA = [  # n, nome, x, y, legenda curta
    (1, "Torre do Meio-Dia", 400, 598, "220 m de pedra e bronze; no alto, o Sol"),
    (2, "Praça do Meio-Dia", 445, 655, "o leão de bronze e a escadaria até o gelo"),
    (3, "Feira do Gelo", 430, 742, "a cidade de lonas sobre o rio"),
    (4, "Estação das Portas", 535, 668, "84 arcos para o resto de Aresta"),
    (5, "Casa da Fornalha", 720, 430, "a rotunda da cúpula verde"),
    (6, "Delegação da Câmara", 650, 352, "entre o Conselho e o Banco de Reservas"),
    (7, "Mercado do Sal", 420, 432, "fonte congelada e depósitos de carvão"),
    (8, "Porta da Neve", 412, 150, "o último trecho da muralha velha"),
    (9, "Oficina Voss", 585, 935, "o pátio da porta verde, no Cobre"),
    (10, "Sete Chaminés", 118, 970, "e, no térreo, a Cozinha do Lento"),
    (11, "Hospital de São Brúlio", 905, 1075, "casarão de pedra de quatro andares"),
    (12, "Canal das Tinas", 860, 905, "o trecho que nunca congela"),
    (13, "Escola Politécnica", 830, 500, "o pátio das arcadas"),
    (14, "Pensão Gralha Branca", 770, 838, "a última rua antes do cais"),
]


def planta_vhalessa():
    W, H = 1000, 1500
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" width="{W_MM}mm" height="{H_MM}mm">{FONTES}',
         f'<rect width="{W}" height="{H}" fill="{PAPEL}"/>']
    # relevo: montanhas ao norte, cristas a noroeste, encostas do sul
    s.append(montanhas(30, 60, 970, 140, 46, 1, 1.1))
    s.append(montanhas(30, 140, 300, 300, 26, 2, 1.0))
    # Alta Mesa (planalto): hachura
    am = ruido([(600, 250), (930, 230), (960, 560), (700, 640), (585, 560)], 30, 7)
    s.append(f'<path d="{d_de(am)}" fill="#D9C59C" stroke="{TINTA2}" stroke-width="1.4"/>')
    s.append(f'<path d="{d_de(am)}" fill="url(#hach)" opacity=".5"/>')
    s.insert(1, f'<defs><pattern id="hach" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="{TINTA2}" stroke-width=".7"/></pattern>'
                f'<pattern id="gelo" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 6 H12 M6 0 V12" stroke="#B9CBD3" stroke-width=".5"/></pattern>'
                f'<marker id="seta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="{CARMIM}"/></marker></defs>')
    # Cisternas (subterrâneo, tracejado)
    s.append(f'<ellipse cx="770" cy="470" rx="140" ry="80" fill="none" stroke="{CARMIM}" stroke-width="1" stroke-dasharray="5 5" opacity=".7"/>')
    s.append(rotulo(770, 560, "Cisternas Quentes (sob a rocha)", 9.5, 400, CARMIM, 1, "middle", "FELL"))
    # muralha velha e Porta da Neve
    s.append(f'<path d="M250,170 Q412,135 600,175" fill="none" stroke="{TINTA}" stroke-width="4"/><path d="M250,170 Q412,135 600,175" fill="none" stroke="{PAPEL}" stroke-width="1.5" stroke-dasharray="3 6"/>')
    # estradas
    s.append(f'<path d="M412,150 L412,40" stroke="{TINTA2}" stroke-width="2" stroke-dasharray="7 4" fill="none"/>')
    s.append(rotulo(430, 52, "estrada do norte · Passo de Hrimgard", 10, 400, TINTA2, 1, "start", "FELL"))
    s.append(f'<path d="M330,420 C230,360 120,300 40,250" stroke="{TINTA2}" stroke-width="2" stroke-dasharray="7 4" fill="none"/>')
    s.append(rotulo(150, 305, "estrada do noroeste", 10, 400, TINTA2, 1, "middle", "FELL", -28))
    s.append(f'<path d="M520,1100 L520,1460" stroke="{TINTA2}" stroke-width="2" stroke-dasharray="7 4" fill="none"/>')
    s.append(rotulo(535, 1440, "estrada do sul · três semanas", 10, 400, TINTA2, 1, "start", "FELL"))
    # rio Lento
    norte = [(0, 712), (150, 720), (300, 702), (420, 708), (560, 690), (700, 696), (860, 680), (1000, 690)]
    sul = [(1000, 770), (860, 760), (700, 778), (560, 772), (420, 790), (300, 786), (150, 800), (0, 790)]
    rio = ruido(norte + sul, 6, 11, 2)
    s.append(f'<path d="{d_de(rio)}" fill="{GELO}" stroke="{RIO}" stroke-width="2"/><path d="{d_de(rio)}" fill="url(#gelo)"/>')
    s.append(rotulo(170, 760, "RIO LENTO", 15, 700, "#5C7480", 7))
    s.append(rotulo(150, 785, "congelado de novembro a março", 9, 400, "#5C7480", 1, "middle", "FELL"))
    # canal das Tinas (laço da margem sul)
    s.append(f'<path d="M790,772 C800,880 930,880 940,766" fill="none" stroke="{RIO}" stroke-width="16"/><path d="M790,772 C800,880 930,880 940,766" fill="none" stroke="#C8D9DF" stroke-width="10"/>')
    # ponte
    s.append(f'<path d="M598,640 L615,830" stroke="{TINTA}" stroke-width="9"/><path d="M598,640 L615,830" stroke="{PAPEL}" stroke-width="5"/>')
    s.append(rotulo(640, 760, "a ponte", 10, 400, TINTA, 1, "start", "FELL"))
    # cais
    s.append(f'<path d="M470,690 L700,682" stroke="{TINTA}" stroke-width="3"/><path d="M700,785 L860,775" stroke="{TINTA}" stroke-width="3"/>')
    # bairros
    s.append(casas(300, 330, 560, 670, 150, 3)); s.append(casas(610, 260, 920, 600, 170, 4, TINTA))
    s.append(casas(40, 830, 500, 1120, 230, 5)); s.append(casas(520, 820, 760, 1120, 160, 6)); s.append(casas(760, 880, 980, 1160, 90, 8))
    s.append(rotulo(770, 300, "ALTA MESA", 20, 700, TINTA, 6))
    s.append(rotulo(270, 1110, "FORNALHA VELHA", 17, 700, TINTA, 5))
    s.append(rotulo(640, 1150, "O COBRE", 17, 700, TINTA, 5))
    s.append(rotulo(640, 1170, "ladeiras até o rio", 9.5, 400, TINTA2, 1, "middle", "FELL"))
    s.append(rotulo(470, 520, "MARGEM NORTE", 11, 700, TINTA2, 4))
    s.append(rotulo(470, 860, "MARGEM SUL", 11, 700, TINTA2, 4))
    # torre e praça
    s.append(f'<rect x="405" y="625" width="80" height="45" fill="none" stroke="{TINTA}" stroke-width="1.2"/>')
    s.append(f'<path d="M392,612 L400,520 L408,612 Z" fill="{TINTA}"/><circle cx="400" cy="514" r="9" fill="{OURO}" stroke="{TINTA}" stroke-width="1.2"/>')
    s.append(f'<circle cx="720" cy="430" r="16" fill="#8FA88E" stroke="{TINTA}" stroke-width="1.4"/>')
    # Feira do Gelo
    rnd = random.Random(9)
    s.append("".join(f'<path d="M{x:.0f},{y:.0f} l5,-7 l5,7 Z" fill="{OURO}" opacity=".85"/>' for x, y in
                     ((rnd.uniform(360, 520), rnd.uniform(718, 770)) for _ in range(40))))
    # encostas do sul e poços do leste
    s.append(montanhas(40, 1230, 960, 1330, 36, 12, .9))
    s.append(rotulo(500, 1370, "encostas do sul · Campos de Espelho", 11, 400, TINTA2, 2, "middle", "FELL"))
    s.append("".join(f'<rect x="{x}" y="1205" width="26" height="9" fill="{OURO}" opacity=".55" stroke="{TINTA2}" stroke-width=".6"/>' for x in range(120, 900, 60)))
    s.append(f'<path d="M940,470 L990,470" stroke="{CARMIM}" stroke-width="1.6" marker-end="url(#seta)"/>')
    s.append(rotulo(975, 455, "poços do leste", 9.5, 400, CARMIM, 1, "end", "FELL"))
    s.append(rotulo(60, 690, "← o rio some nas colinas brancas", 9.5, 400, "#5C7480", 0, "start", "FELL"))
    # marcas numeradas
    s.append("".join(marca(x, y, n) for n, _, x, y, _ in LOCAIS_VHALESSA))
    s.append(rosa(905, 1270, 46)); s.append(escala(80, 1290, 250, 1))
    s.append(cartucho(500, 1430, 420, "VHALESSA", "a cidade do Sol de Inverno · ano de 1187"))
    s.append(moldura(W, H))
    return "".join(s) + "</svg>"


# ------------------------------------------------------------------ O Norte (regional)
def mapa_norte():
    W, H = 1000, 1500
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" width="{W_MM}mm" height="{H_MM}mm">{FONTES}',
         f'<rect width="{W}" height="{H}" fill="{PAPEL}"/>']
    s.append(f'<defs><marker id="seta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="{TINTA}"/></marker></defs>')
    s.append(montanhas(60, 120, 940, 520, 150, 21, 1.15))
    s.append(montanhas(60, 520, 420, 720, 60, 22, 1.2))
    s.append(montanhas(640, 560, 940, 760, 40, 23, 1.0))
    s.append(montanhas(80, 1000, 920, 1150, 50, 24, .9))
    s.append(arvores(100, 760, 900, 1000, 160, 25)); s.append(arvores(150, 1150, 850, 1350, 120, 26))
    # glaciar do Passo Cinzento
    gl = ruido([(205, 470), (250, 455), (285, 495), (262, 525), (215, 515)], 10, 31)
    s.append(f'<path d="{d_de(gl)}" fill="#E4EEF2" stroke="#8AA6B2" stroke-width="1.4"/>')
    # rio Lento
    s.append(f'<path d="M0,830 C200,860 350,790 500,820 C650,850 800,800 1000,830" fill="none" stroke="{RIO}" stroke-width="10"/>'
             f'<path d="M0,830 C200,860 350,790 500,820 C650,850 800,800 1000,830" fill="none" stroke="{GELO}" stroke-width="6"/>')
    # estradas
    for d in ("M500,800 C505,640 480,520 500,330 C515,250 540,220 560,160", "M490,805 C420,700 330,620 255,520",
              "M500,840 C510,1000 470,1200 500,1470"):
        s.append(f'<path d="{d}" fill="none" stroke="{TINTA}" stroke-width="2.2" stroke-dasharray="8 5"/>')
    # Vhalessa
    s.append(f'<circle cx="500" cy="820" r="22" fill="{PAPEL}" stroke="{TINTA}" stroke-width="2.4"/><circle cx="500" cy="820" r="9" fill="{OURO}" stroke="{TINTA}"/>')
    s.append(rotulo(500, 875, "VHALESSA", 22, 700, TINTA, 5))
    s.append(rotulo(500, 895, "300 m de altitude · 600 mil almas", 10, 400, TINTA2, 1, "middle", "FELL"))
    # lugares
    s.append(f'<circle cx="500" cy="430" r="7" fill="{TINTA}"/>' + rotulo(515, 425, "Passo de Hrimgard", 13, 700, TINTA, 2, "start"))
    s.append(rotulo(515, 443, "três dias de trenó · nove abrigos de pedra", 9.5, 400, TINTA2, 1, "start", "FELL"))
    s.append(f'<circle cx="560" cy="160" r="9" fill="{PAPEL}" stroke="{TINTA}" stroke-width="2"/>' + rotulo(578, 166, "Skarsvik", 14, 700, TINTA, 2, "start"))
    s.append(rotulo(578, 183, "minas de carvão · quatro dias de trenó", 9.5, 400, TINTA2, 1, "start", "FELL"))
    s.append(rotulo(760, 110, "Vale de Skjold", 12, 700, TINTA, 2) + rotulo(760, 126, "a três dias de Skarsvik", 9, 400, TINTA2, 1, "middle", "FELL"))
    s.append(rotulo(500, 70, "REINOS DA TEMPESTADE", 20, 700, TINTA, 6))
    s.append(f'<circle cx="255" cy="520" r="8" fill="{PAPEL}" stroke="{TINTA}" stroke-width="2"/>' + rotulo(240, 600, "Passo Cinzento", 14, 700, TINTA, 2))
    s.append(rotulo(240, 617, "140 km a noroeste · 2.100 m", 9.5, 400, TINTA2, 1, "middle", "FELL"))
    s.append(rotulo(200, 340, "cristas do noroeste", 12, 400, TINTA2, 2, "middle", "FELL", -12))
    s.append(rotulo(780, 690, "poços do leste", 11, 400, CARMIM, 1, "middle", "FELL"))
    s.append(rotulo(500, 1080, "encostas do sul · Campos de Espelho", 11, 400, TINTA2, 1, "middle", "FELL"))
    s.append(rotulo(80, 900, "← o rio some", 10, 400, "#5C7480", 0, "start", "FELL"))
    s.append(rotulo(80, 918, "nas colinas brancas", 10, 400, "#5C7480", 0, "start", "FELL"))
    for y, t in ((1290, "minas de carvão do sul · três semanas de estrada"), (1325, "colinas de Tarvel, onde nunca neva"),
                 (1360, "Tamsin · 1.200 km    ·    Delta das Duas Luas · 2.000 km"), (1395, "Soleira, no outro extremo do continente")):
        s.append(rotulo(500, y, t, 11, 400, TINTA, 1, "middle", "FELL"))
    s.append(f'<path d="M500,1400 L500,1450" stroke="{TINTA}" stroke-width="2" marker-end="url(#seta)"/>')
    s.append(rosa(880, 1000, 50)); s.append(escala(80, 1440, 1.65, 100))
    s.append(cartucho(500, 1200, 360, "O NORTE", "Vhalessa e as montanhas"))
    s.append(moldura(W, H))
    return "".join(s) + "</svg>"


# ------------------------------------------------------------------ Aresta (continente, conceitual)
REGIOES = [("REINOS DO NORTE", 330, 330, "#C9CDD0"), ("TERRAS DOS DRAGÕES", 700, 360, "#C9A69A"),
           ("CIDADES LIVRES", 250, 650, "#D3BE93"), ("LIMIAR", 520, 650, "#D8CBA8"),
           ("DELTA E ARQUIVOS", 320, 960, "#CDBF8E"), ("ILHAS-PRISMA", 760, 900, "#BFC9D6"), ("A CONFLUÊNCIA", 540, 1000, "#C7D3D2")]


def mapa_aresta():
    W, H = 1000, 1500
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" width="{W_MM}mm" height="{H_MM}mm">{FONTES}',
         f'<rect width="{W}" height="{H}" fill="#B9C8CC"/>',
         f'<defs><pattern id="mar" width="40" height="14" patternUnits="userSpaceOnUse"><path d="M0 7 q10 -6 20 0 t20 0" fill="none" stroke="#8FA4AB" stroke-width=".8"/></pattern>'
         f'<marker id="seta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="{TINTA}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#mar)"/>']
    cx, cy, R = 500, 680, 400
    base = [(cx + R * math.cos(t) * (1 + .08 * math.sin(3 * t)), cy + R * 1.2 * math.sin(t)) for t in [i * math.tau / 18 for i in range(18)]]
    costa = ruido(base, 60, 41, 4)
    s.append(f'<path d="{d_de(costa)}" fill="{PAPEL}" stroke="{TINTA}" stroke-width="2"/>')
    for nome, x, y, cor in REGIOES:
        reg = ruido([(x + 120 * math.cos(t), y + 110 * math.sin(t)) for t in [i * math.tau / 9 for i in range(9)]], 40, hash(nome) % 1000, 3)
        s.append(f'<path d="{d_de(reg)}" fill="{cor}" opacity=".55" stroke="{TINTA2}" stroke-width=".8" stroke-dasharray="4 3"/>')
    s.append(montanhas(180, 220, 470, 420, 50, 51, .9)); s.append(montanhas(560, 230, 840, 440, 50, 52, .9))
    s.append(arvores(150, 560, 360, 760, 70, 53)); s.append(arvores(220, 880, 430, 1050, 50, 54))
    for nome, x, y, _ in REGIOES:
        s.append(rotulo(x, y + 6, nome, 15, 700, TINTA, 3))
    # Vhalessa e Soleira
    s.append(f'<circle cx="500" cy="300" r="10" fill="{OURO}" stroke="{TINTA}" stroke-width="2"/>' + rotulo(500, 278, "Vhalessa", 15, 700, CARMIM, 2))
    s.append(f'<circle cx="520" cy="1150" r="10" fill="{OURO}" stroke="{TINTA}" stroke-width="2"/>' + rotulo(520, 1182, "Soleira", 15, 700, CARMIM, 2))
    s.append(f'<path d="M500,312 C470,600 560,900 520,1138" fill="none" stroke="{OURO}" stroke-width="2" stroke-dasharray="2 6"/>')
    s.append(rotulo(600, 560, "a rede de portas de Aurelia", 10, 400, TINTA2, 1, "start", "FELL", 80))
    s.append(rosa(880, 1290, 52)); s.append(escala(80, 1420, .27, 1000))
    s.append(cartucho(500, 110, 420, "ARESTA", "cartografia conceitual · fronteiras em disputa"))
    s.append(moldura(W, H))
    return "".join(s) + "</svg>"


W_MM, H_MM = W - 20, H - 30


def pagina_mapa(svg, titulo=None):
    return pagina(f'<div class="mapa">{svg}</div>', "perg")


def legenda_vhalessa(imagens):
    """Página de vinhetas numeradas: cada lugar do mapa com uma ilustração."""
    itens = []
    for n, nome, _, _, leg in LOCAIS_VHALESSA:
        im = imagens.get(n)
        bg = f'background-image:url({img(im, 700)})' if im else ""
        itens.append(f'<div class="lv"><div class="lvi" style="{bg}"></div><div class="lvt"><span class="lvn">{n}</span> {esc(nome)}</div><div class="lvl">{esc(leg)}</div></div>')
    return pagina(f'<div class="esp"><div class="ek">Atlas</div><div class="et">Vhalessa, lugar por lugar</div>{ornamento()}'
                  f'<div class="lvgrid">{"".join(itens)}</div></div>', "noite")


CSS_MAPA = f"""
.mapa{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}}
.lvgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:3.2mm 3mm;margin-top:3mm;text-align:left}}
.lvi{{height:23mm;background-size:cover;background-position:center;border:.3mm solid #6B5532;border-radius:.6mm}}
.lvt{{font:700 7.6pt AT;color:#E2C47E;margin-top:1mm;letter-spacing:.3mm}} .lvn{{color:#C8332F}}
.lvl{{font:italic 7.4pt/1.2 EBG;color:#CFC4AC}}
"""
