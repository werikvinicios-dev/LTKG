#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SISTEMA DE SÍMBOLOS — Leis para Matar Deuses.
Gramática comum (grade 200 × 200): um EIXO vertical (a lei, a lâmina), CÍRCULOS (o campo onde a lei age) e
PÉROLAS (a unidade de energia que nunca se cria nem se perde). Cada sinal diz o seu conceito com esses três
elementos, sem inventar regra nova. Famílias: leis, disciplinas, etapas da Transposição, instituições e regiões.
Versões: linear · reduzida · selo (sólida, recorte) · decorativa (metal) — SVG e PNG individuais + pranchas."""
import math, os, sys
sys.path.insert(0, "/home/user/LTKG/build/visual")
from kit import *

OUT = "/home/user/LTKG/exportacoes/identidade_aresta/simbolos"
NEGRO, OURO, MARFIM, CARMIM = "#0D0C0B", "#C9A15A", "#EFE8DA", "#8E1B22"
BOLD, SEMI = "Cinzel-Bold.ttf", "Cinzel-SemiBold.ttf"
C = 100

def arc(cx, cy, r, a0, a1, n=48):
    return polyline([polar(cx, cy, r, a0 + (a1 - a0) * i / n) for i in range(n + 1)])

def dia(x, y, rx, ry):
    return f"M{x},{y - ry} L{x + rx},{y} L{x},{y + ry} L{x - rx},{y} Z"

# Cada sinal devolve (traços, pérolas, acento): traços = lista de 'd' (desenhados com stroke),
# pérolas = lista de (x, y, r) preenchidas, acento = lista de 'd' preenchidos na cor da família.
def S(strokes=(), pearls=(), fills=()):
    return list(strokes), list(pearls), list(fills)

# ------------------------------------------------------------------ AS SETE LEIS
def lei_conservacao():      # nada se cria: campo fechado, eixo inteiro, uma pérola em equilíbrio no centro
    return S([arc(C, C, 72, 0, 360), arc(C, C, 30, 0, 360), f"M{C},14 L{C},70", f"M{C},130 L{C},186"], [(C, C, 13)])
def lei_vinculo():          # toda magia exige ligação: dois campos que se atravessam, uma pérola em cada
    return S([arc(C - 26, C, 44, 0, 360), arc(C + 26, C, 44, 0, 360), f"M{C},10 L{C},190"], [(C - 34, C, 9), (C + 34, C, 9)])
def lei_compatibilidade():  # o que não ressoa se rompe: anéis concêntricos; o externo só fecha onde concorda
    return S([arc(C, C, 34, 0, 360), arc(C, C, 56, -60, 240), arc(C, C, 76, 250, 470), f"M{C},8 L{C},44", f"M{C},156 L{C},192"],
             [], [f"M{C + 15},{C} A15,15 0 1,1 {C - 15},{C} A15,15 0 1,1 {C + 15},{C} Z"])
def lei_vazao():            # toda passagem tem limite: o canal se estreita; a pérola passa pela garganta
    return S([f"M{C - 58},20 C{C - 58},80 {C - 14},86 {C - 14},{C} C{C - 14},114 {C - 58},120 {C - 58},180",
              f"M{C + 58},20 C{C + 58},80 {C + 14},86 {C + 14},{C} C{C + 14},114 {C + 58},120 {C + 58},180",
              f"M{C - 70},20 L{C + 70},20", f"M{C - 70},180 L{C + 70},180", f"M{C},34 L{C},76", f"M{C},124 L{C},166"], [(C, C, 9)])
def lei_dissipacao():       # nada permanece: a pérola se desfaz em pérolas menores ao longo do eixo
    return S([arc(C, C - 30, 40, 150, 390), f"M{C},10 L{C},40"], [(C, C - 30, 14), (C, C + 22, 8), (C, C + 46, 5.5), (C, C + 64, 3.8), (C, C + 78, 2.6), (C, C + 89, 1.8)])
def lei_capacidade():       # tudo tem limite: o vaso, a marca de nível, duas pérolas dentro
    return S([f"M{C - 62},62 C{C - 62},150 {C - 30},168 {C},168 C{C + 30},168 {C + 62},150 {C + 62},62",
              f"M{C - 78},62 L{C + 78},62", f"M{C - 44},96 L{C + 44},96", f"M{C},10 L{C},62"], [(C, 116, 11), (C, 146, 11)])
def lei_retorno():          # toda ação retorna: o círculo aberto com a seta que volta ao ponto de partida
    a1 = 330
    tip = polar(C, C, 64, a1); t1 = polar(C, C, 50, a1 - 12); t2 = polar(C, C, 78, a1 - 12)
    return S([arc(C, C, 64, -60, a1), f"M{P(*t1)} L{P(*tip)} L{P(*t2)}", f"M{C},14 L{C},50", f"M{C},150 L{C},186"], [(C, C, 12)])

LEIS = [("I", "Conservação", "Nada se cria. Tudo se transforma.", lei_conservacao),
        ("II", "Vínculo", "Toda magia exige uma ligação.", lei_vinculo),
        ("III", "Compatibilidade", "O que não ressoa se rompe.", lei_compatibilidade),
        ("IV", "Vazão", "Toda passagem tem um limite.", lei_vazao),
        ("V", "Dissipação", "Nada permanece para sempre.", lei_dissipacao),
        ("VI", "Capacidade", "Todo ser, objeto ou lugar tem um limite.", lei_capacidade),
        ("VII", "Retorno", "Toda ação retorna.", lei_retorno)]

# ------------------------------------------------------------------ AS SEIS DISCIPLINAS (cor própria)
def d_pulso():   # movimento: lâmina-relâmpago dentro do anel
    return S([arc(C, C, 66, 0, 360)], [], [f"M{C + 6},14 L{C - 16},96 L{C - 2},96 L{C - 8},186 L{C + 18},88 L{C + 3},88 Z"])
def d_brasa():   # transformação: lâmina em chama
    return S([arc(C, C + 18, 52, 200, 340)], [], [f"M{C},12 C{C + 30},52 {C + 44},86 {C + 30},126 C{C + 22},150 {C + 8},168 {C},188 "
                                                  f"C{C - 8},168 {C - 22},150 {C - 30},126 C{C - 40},98 {C - 22},74 {C - 12},90 C{C - 16},60 {C - 4},40 {C},12 Z"])
def d_trama():   # estrutura: nó entrelaçado de dois quadrados
    q1 = polyline([(C, 22), (C + 78, C), (C, 178), (C - 78, C)], True)
    q2 = polyline([(C - 52, C - 52), (C + 52, C - 52), (C + 52, C + 52), (C - 52, C + 52)], True)
    return S([q1, q2, arc(C, C, 22, 0, 360), f"M{C},8 L{C},192"], [(C, C, 8)])
def d_clarao():  # revelação: estrela de oito pontas com o raio vertical longo
    pts = []
    for k in range(16):
        a = -90 + k * 22.5
        r = (92 if k in (0, 8) else 54 if k % 4 == 0 else 34) if k % 2 == 0 else 11
        pts.append(polar(C, C, r, a))
    return S([arc(C, C, 64, 0, 360)], [], [polyline(pts, True)])
def d_eco():     # ressonância: anéis que se repetem a partir da mira
    return S([arc(C, C, 24, 0, 360), arc(C, C, 46, 0, 360), arc(C, C, 68, 0, 360), f"M{C},8 L{C},70", f"M{C},130 L{C},192",
              f"M18,{C} L70,{C}", f"M130,{C} L182,{C}"], [(C, C, 10)])
def d_carga():   # acúmulo: anéis empilhados no eixo, a pérola no topo
    return S([f"M{C},8 L{C},192", arc(C, 66, 26, 0, 360), arc(C, 118, 34, 0, 360), arc(C, 164, 20, 180, 360)], [(C, 24, 11)])

DISC = [("Impetus", "Movimento", "#4F8BD6", d_pulso), ("Igneo", "Transformação", "#C8332F", d_brasa),
        ("Nexo", "Estrutura", "#C9A15A", d_trama), ("Lume", "Revelação", "#F2E6C2", d_clarao),
        ("Eco", "Ressonância", "#9FB7D6", d_eco), ("Fuso", "Acúmulo", "#D7B46A", d_carga)]

# ------------------------------------------------------------------ ETAPAS DA TRANSPOSIÇÃO
def e_fonte():     # de onde vem: pérola com raios para fora
    return S([f"M{P(*polar(C, C, 34, a))} L{P(*polar(C, C, 70 if a % 90 == 0 else 54, a))}" for a in range(0, 360, 30)] + [arc(C, C, 24, 0, 360)], [(C, C, 13)])
def e_ancora():    # onde se fixa: cristal-âncora cravado na linha
    return S([f"M{C - 72},164 L{C + 72},164", f"M{C},18 L{C},40"], [], [dia(C, 104, 30, 66)])
def e_elo():       # por onde passa: dois elos de corrente
    return S([f"M{C - 62},{C - 22} L{C - 6},{C - 22} A22,22 0 0,1 {C - 6},{C + 22} L{C - 62},{C + 22} A22,22 0 0,1 {C - 62},{C - 22} Z",
              f"M{C + 6},{C - 22} L{C + 62},{C - 22} A22,22 0 0,1 {C + 62},{C + 22} L{C + 6},{C + 22} A22,22 0 0,1 {C + 6},{C - 22} Z"], [(C, C, 9)])
def e_destino():   # onde a lei se aplica: alvo
    return S([arc(C, C, 66, 0, 360), arc(C, C, 40, 0, 360), f"M{C},8 L{C},44", f"M{C},156 L{C},192", f"M8,{C} L44,{C}", f"M156,{C} L192,{C}"], [(C, C, 14)])
def e_controle():  # o que regula: anel com a barra-limitador
    return S([arc(C, C, 66, 0, 360), f"M18,{C} L182,{C}", f"M{C - 30},{C - 26} L{C - 30},{C + 26}", f"M{C + 30},{C - 26} L{C + 30},{C + 26}"], [(C, C - 40, 9)])
def e_retorno():   # para onde volta: espiral que fecha
    pts = [(C + (8 + 60 * t) * math.cos(-math.pi / 2 + 4.2 * math.pi * t), C + (8 + 60 * t) * math.sin(-math.pi / 2 + 4.2 * math.pi * t)) for t in (i / 200 for i in range(201))]
    tip = pts[-1]
    return S([polyline(pts), f"M{tip[0] - 14},{tip[1] - 8} L{tip[0]},{tip[1]} L{tip[0] - 4},{tip[1] + 14}"], [(C, C, 7)])

ETAPAS = [("1", "Fonte", "Origem da energia.", e_fonte), ("2", "Âncora", "Ponto de fixação.", e_ancora),
          ("3", "Elo", "Conexão e transmissão.", e_elo), ("4", "Destino", "Onde a lei se aplica.", e_destino),
          ("5", "Controle", "Regula, limita, mantém.", e_controle), ("6", "Retorno", "O saldo que volta.", e_retorno)]

# ------------------------------------------------------------------ INSTITUIÇÕES E MARCAS (referências do autor)
def arco_simples(w=58, top=24, base=182):
    return f"M{C - w},{base} L{C - w},{C} A{w * 1.9},{w * 1.9} 0 0,1 {C},{top} A{w * 1.9},{w * 1.9} 0 0,1 {C + w},{C} L{C + w},{base}"
def f_ordem():        # Ordem da Última Sentença: arco, espada, balança
    return S([arco_simples(), f"M{C},40 L{C},176", f"M{C - 86},86 L{C + 86},80", f"M{C - 86},86 L{C - 100},126 M{C - 86},86 L{C - 72},126",
              f"M{C - 104},126 Q{C - 86},142 {C - 68},126 Z", f"M{C + 86},80 L{C + 72},118 M{C + 86},80 L{C + 100},118", f"M{C + 68},118 Q{C + 86},134 {C + 104},118 Z"],
             [(C, 36, 7)])
def f_carrasco():     # os Carrascos: espada vertical com o anel na guarda
    return S([arc(C, 70, 26, 0, 360)], [], [f"M{C - 7},20 L{C + 7},20 L{C + 7},150 L{C},192 L{C - 7},150 Z", f"M{C - 46},66 L{C + 46},66 L{C + 46},76 L{C - 46},76 Z"])
def f_coroas():       # Coroas e Soberanias: coroa de lâminas
    pts = [(C - 80, 150), (C - 80, 92), (C - 52, 116), (C - 34, 52), (C - 14, 104), (C, 20), (C + 14, 104), (C + 34, 52), (C + 52, 116), (C + 80, 92), (C + 80, 150)]
    return S([f"M{C - 84},172 L{C + 84},172"], [(C, 140, 9)], [polyline(pts, True)])
def f_limiares():     # os Limiares: portal que divide o disco
    return S([arc(C, C, 72, 0, 360), f"M{C},28 L{C},172", arco_simples(34, 50, 150)], [], [f"M{C},28 A72,72 0 0,1 {C},172 Z"])
def f_cidades():      # Cidades Livres: três torres sob o arco
    return S([f"M20,176 L180,176", arco_simples(78, 16, 176)], [],
             [f"M{C - 12},176 L{C - 12},70 L{C},44 L{C + 12},70 L{C + 12},176 Z", f"M{C - 52},176 L{C - 52},104 L{C - 42},88 L{C - 32},104 L{C - 32},176 Z",
              f"M{C + 32},176 L{C + 32},104 L{C + 42},88 L{C + 52},104 L{C + 52},176 Z"])
def f_dragoes():      # os Dragões: anel que se enrola sobre si (cabeça, chifre, olho)
    pts = [(C + (64 - 10 * t) * math.cos(math.radians(-40 + 320 * t)), C + (64 - 10 * t) * math.sin(math.radians(-40 + 320 * t))) for t in (i / 160 for i in range(161))]
    hx, hy = polar(C, C, 64, -40)
    return S([polyline(pts), arc(C, C, 44, 0, 360)], [(hx + 6, hy - 4, 5)], [f"M{hx - 4},{hy - 8} L{hx + 34},{hy - 40} L{hx + 12},{hy - 4} Z"])
def f_arrimo():       # Companhia Arrimo (seguradora): escudo com a balança e a chave
    return S([f"M{C - 62},30 L{C + 62},30 L{C + 62},104 C{C + 62},146 {C + 30},170 {C},184 C{C - 30},170 {C - 62},146 {C - 62},104 Z",
              f"M{C - 40},72 L{C + 40},72", f"M{C},50 L{C},150", f"M{C - 40},72 L{C - 52},104 M{C - 40},72 L{C - 28},104", f"M{C - 56},104 Q{C - 40},118 {C - 24},104 Z",
              f"M{C + 40},72 L{C + 28},104 M{C + 40},72 L{C + 52},104", f"M{C + 24},104 Q{C + 40},118 {C + 56},104 Z"], [(C, 50, 6)])
def f_aurelia():      # marca pessoal de Aurelia: coroa de raios e a estrela do limiar
    rays = [f"M{P(*polar(C, 120, 50, a))} L{P(*polar(C, 120, 84 if a % 30 == 0 else 66, a))}" for a in range(-165, -10, 15)]
    return S(rays + [arc(C, 120, 40, 180, 360), f"M{C - 50},120 L{C + 50},120"], [], [dia(C, 150, 12, 26)])
def f_ilan():         # marca pessoal de Ilan Varek: lâmina, anel e o prato que pesa
    return S([arc(C, 74, 22, 0, 360), f"M{C - 50},104 L{C + 50},96", f"M{C - 50},104 L{C - 50},132", f"M{C - 66},132 L{C - 34},132"], [],
             [f"M{C - 6},18 L{C + 6},18 L{C + 6},160 L{C},190 L{C - 6},160 Z"])

INST = [("Ordem da Última Sentença", "A lei acima de tudo.", f_ordem), ("Os Carrascos", "Equilíbrio pela ausência.", f_carrasco),
        ("Coroas e Soberanias", "Entre mundos, há um trono.", f_coroas), ("Os Limiares", "Portais exigem testemunhas.", f_limiares),
        ("Cidades Livres", "Povos escolhem.", f_cidades), ("Os Dragões", "Memória mais antiga que os deuses.", f_dragoes),
        ("Companhia Arrimo", "A apólice cobre o que pode.", f_arrimo), ("Aurelia", "Limiares, soberania, escolhas.", f_aurelia),
        ("Ilan Varek", "Sobrevivência é princípio.", f_ilan)]

# ------------------------------------------------------------------ REGIÕES (cartografia conceitual do autor)
def r_glyph(kind):
    if kind == "limiar":   return S([arco_simples(46, 40, 160), arc(C, C, 76, 0, 360)], [(C, 112, 9)])
    if kind == "norte":    return S([f"M{C - 76},160 L{C - 30},70 L{C},120 L{C + 34},50 L{C + 78},160 Z", f"M{C + 34},50 L{C + 34},20"], [], [])
    if kind == "delta":    return S([f"M{C},20 L{C},110", f"M{C},110 C{C - 10},140 {C - 50},150 {C - 70},180", f"M{C},110 C{C + 10},140 {C + 50},150 {C + 70},180", f"M{C},110 L{C},184"], [(C, 110, 9)])
    if kind == "prisma":   return S([polyline([(C, 18), (C + 50, 96), (C, 182), (C - 50, 96)], True), f"M{C - 50},96 L{C + 50},96", f"M{C},18 L{C},182"], [], [])
    if kind == "dragoes":  return f_dragoes()
    if kind == "livres":   return f_cidades()
    if kind == "conf":     return S([arc(C, C, 70, 0, 360)] + [f"M{P(*polar(C, C, 14, a))} L{P(*polar(C, C, 70, a))}" for a in (-90, 30, 150)], [(C, C, 12)])
REGIOES = [("Cidade de Limiar", "limiar"), ("Reinos do Norte", "norte"), ("Delta e Arquivos", "delta"), ("Ilhas-Prisma", "prisma"),
           ("Terras dos Dragões", "dragoes"), ("Cidades Livres", "livres"), ("A Confluência", "conf")]

# ------------------------------------------------------------------ renderização das versões
def draw(sig, ink, sw=5.0, accent=None, pearl=None):
    st, pe, fi = sig
    a = accent or ink; pl = pearl or ink
    return (f'<g fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            + "".join(f'<path d="{d}"/>' for d in st) + "</g>"
            + "".join(f'<path d="{d}" fill="{a}"/>' for d in fi)
            + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{pl}"/>' for x, y, r in pe))

def v_linear(sig, ink=NEGRO):
    return svg(200, 200, draw(sig, ink, 5))

def v_reduzida(sig, ink=NEGRO):
    return svg(200, 200, draw(sig, ink, 11))

def v_selo(sig, uid, ink=NEGRO):
    """Selo sólido: disco de tinta com o sinal vazado (funciona como carimbo, lacre, relevo seco)."""
    inner = draw(sig, "#000", 6, "#000", "#000")
    m = (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="240" height="240"><rect width="240" height="240" fill="#fff"/>'
         f'<g transform="translate(36 36) scale(.84)">{inner}</g><circle cx="120" cy="120" r="104" fill="none" stroke="#000" stroke-width="3"/></mask>')
    return svg(240, 240, f'<circle cx="120" cy="120" r="116" fill="{ink}" mask="url(#{uid})"/>', m)

def v_decorativa(sig, uid, accent=OURO, glow=False):
    """Medalhão decorativo: disco grafite, anéis de ouro, sinal em ouro com acento na cor da família."""
    defs = (lin_grad(f"{uid}o", [(0, "#F6E7B8"), (.35, "#C9A15A"), (.6, "#86602A"), (1, "#E9CF8E")], user=(0, 0, 240, 240))
            + f'<radialGradient id="{uid}b" cx="50%" cy="40%" r="62%"><stop offset="0" stop-color="#2B2926"/><stop offset="1" stop-color="#0D0C0B"/></radialGradient>'
            + f'<radialGradient id="{uid}p" cx="38%" cy="32%" r="70%"><stop offset="0" stop-color="#FFFDF6"/><stop offset=".5" stop-color="#E8DFCB"/><stop offset="1" stop-color="#9C8F78"/></radialGradient>'
            + (f'<filter id="{uid}g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>' if glow else ""))
    ring = (f'<circle cx="120" cy="120" r="116" fill="url(#{uid}b)"/><circle cx="120" cy="120" r="112" fill="none" stroke="url(#{uid}o)" stroke-width="3"/>'
            f'<circle cx="120" cy="120" r="104" fill="none" stroke="url(#{uid}o)" stroke-width="1"/>'
            + "".join(f'<circle cx="{P(*polar(120, 120, 108, k * 360 / 56))[:0] or polar(120, 120, 108, k * 360 / 56)[0]:.1f}" cy="{polar(120, 120, 108, k * 360 / 56)[1]:.1f}" r="1.3" fill="url(#{uid}o)"/>' for k in range(56)))
    pearl = f"url(#{uid}p)" if accent in (OURO, "#C9A15A", "#D7B46A") else accent
    g = (f'<g transform="translate(36 36) scale(.84)" filter="url(#{uid}g)" opacity=".7">{draw(sig, accent, 9, accent, accent)}</g>' if glow else "")
    return svg(240, 240, ring + g + f'<g transform="translate(36 36) scale(.84)">{draw(sig, f"url(#{uid}o)", 5, accent, pearl)}</g>', defs)

def export_family(fam, items, get_sig, accent_of=lambda it: OURO, glow=False):
    d = f"{OUT}/{fam}"; os.makedirs(d, exist_ok=True)
    for i, it in enumerate(items):
        sig = get_sig(it); slug = slugify(it)
        for ver, s in (("linear", v_linear(sig)), ("reduzida", v_reduzida(sig)), ("selo", v_selo(sig, f"m{fam[:2]}{i}")),
                       ("decorativa", v_decorativa(sig, f"d{fam[:2]}{i}", accent_of(it), glow)),
                       ("linear_marfim", v_linear(sig, MARFIM))):
            open(f"{d}/{slug}_{ver}.svg", "w", encoding="utf-8").write(s)
            to_png(s, f"{d}/{slug}_{ver}.png", 800 if ver != "reduzida" else 256)

def slugify(it):
    import unicodedata
    name = it[1] if isinstance(it[0], str) and len(it[0]) <= 3 and it[0][0] in "IVX123456" else it[0]
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return "".join(ch if ch.isalnum() else "_" for ch in s).strip("_")

# ------------------------------------------------------------------ pranchas
def sheet(title, kicker, cells, cols, cw=360, ch=470, uidp="s"):
    """Prancha escura: medalhão decorativo + numeral + nome + frase."""
    W = 120 + cols * cw; rows = math.ceil(len(cells) / cols); H = 300 + rows * ch + 40
    body = [f'<rect width="{W}" height="{H}" fill="{NEGRO}"/>',
            f'<path d="{text_path(kicker, SEMI, 26, 60, 92, 0.32)}" fill="#8F7A55"/>',
            f'<path d="{text_path(title, BOLD, 64, 60, 172, 0.04)}" fill="url(#tt)"/>',
            f'<rect x="60" y="204" width="{W - 120}" height="1.5" fill="#5A4A2E"/>']
    defs = lin_grad("tt", [(0, "#F6E7B8"), (.5, "#C9A15A"), (1, "#E9CF8E")], user=(0, 100, 0, 180))
    for k, (num, name, line, svgtxt) in enumerate(cells):
        x = 60 + (k % cols) * cw; y = 250 + (k // cols) * ch
        inner = svgtxt.split("<defs>", 1)[1]
        idefs, ibody = inner.split("</defs>", 1)
        ibody = ibody.rsplit("</svg>", 1)[0]
        defs += idefs
        body.append(f'<g transform="translate({x + (cw - 260) / 2} {y}) scale({260 / 240})">{ibody}</g>')
        if num:
            body.append(f'<path d="{text_path(num, BOLD, 30, x + cw / 2, y + 312, 0.1, "middle")}" fill="#8F7A55"/>')
        body.append(f'<path d="{text_path(name.upper(), SEMI, 27 if len(name) < 16 else 22, x + cw / 2, y + 352, 0.12, "middle")}" fill="{MARFIM}"/>')
        for j, ln in enumerate(wrap(line, 30)):
            body.append(f'<path d="{text_path(ln, "EBGaramond-Italic.ttf", 25, x + cw / 2, y + 390 + j * 30, 0, "middle")}" fill="#B9AE98"/>')
    return svg(W, H, "".join(body), defs)

def wrap(t, n):
    out, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > n and cur: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    export_family("leis", LEIS, lambda it: it[3]())
    export_family("disciplinas", DISC, lambda it: it[3](), lambda it: it[2], glow=True)
    export_family("etapas_transposicao", ETAPAS, lambda it: it[3]())
    export_family("instituicoes", INST, lambda it: it[2](), lambda it: CARMIM if it[0] == "Os Carrascos" else OURO)
    export_family("regioes_conceituais", REGIOES, lambda it: r_glyph(it[1]))
    sheets = [
        ("prancha_sete_leis", "As sete leis", "Leis para Matar Deuses · fundamentos da Transposição",
         [(n, nm, ln, v_decorativa(f(), f"L{i}")) for i, (n, nm, ln, f) in enumerate(LEIS)], 4),
        ("prancha_seis_disciplinas", "As seis disciplinas", "Formas de aplicação das leis",
         [("", nm, sub, v_decorativa(f(), f"D{i}", col, True)) for i, (nm, sub, col, f) in enumerate(DISC)], 3),
        ("prancha_etapas_transposicao", "Estrutura de uma transposição", "Sequência universal: da fonte ao retorno",
         [(n, nm, ln, v_decorativa(f(), f"E{i}")) for i, (n, nm, ln, f) in enumerate(ETAPAS)], 3),
        ("prancha_instituicoes", "Instituições e marcas", "Ordens, cortes, companhias e assinaturas",
         [("", nm, ln, v_decorativa(f(), f"I{i}", CARMIM if nm == "Os Carrascos" else OURO)) for i, (nm, ln, f) in enumerate(INST)], 3),
        ("prancha_regioes_conceituais", "Regiões de Aresta", "Cartografia conceitual (referências do autor; não canônica)",
         [("", nm, "", v_decorativa(r_glyph(k), f"R{i}")) for i, (nm, k) in enumerate(REGIOES)], 4),
    ]
    for fn, title, kick, cells, cols in sheets:
        s = sheet(title, kick, cells, cols)
        open(f"{OUT}/{fn}.svg", "w", encoding="utf-8").write(s)
        to_png(s, f"{OUT}/{fn}.png")
    print("simbolos ok")
