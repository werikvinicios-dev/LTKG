#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit vetorial da identidade visual (v2): texto em curvas, microtexto em círculo,
curvas de guilhochê (rose engine), utilidades de SVG, rasterização (resvg) e animação (ffmpeg)."""
import math, os, subprocess, io
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import resvg_py

FONTS = "/home/user/LTKG/build/fonts"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
_cache = {}

# ------------------------------------------------------------------ fontes → curvas
def _font(name):
    if name not in _cache:
        path = os.path.join(FONTS, name)
        hbf = hb.Font(hb.Face(open(path, "rb").read()))
        tt = TTFont(path)
        _cache[name] = (hbf, tt, tt["head"].unitsPerEm, tt.getGlyphSet(), tt.getGlyphOrder())
    return _cache[name]

def _shape(text, font, features=None):
    hbf, tt, upm, gs, order = _font(font)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, features or {"kern": True, "liga": True})
    return buf.glyph_infos, buf.glyph_positions, upm, gs, order

def text_width(text, font, size, tracking=0.0, features=None):
    infos, pos, upm, _, _ = _shape(text, font, features)
    return sum(p.x_advance for p in pos) * size / upm + tracking * size * max(len(infos) - 1, 0)

def text_path(text, font, size, x, y, tracking=0.0, anchor="start", features=None):
    """d de um <path> com o texto em curvas; y = linha de base."""
    infos, pos, upm, gs, order = _shape(text, font, features)
    w = text_width(text, font, size, tracking, features)
    if anchor == "middle": x -= w / 2
    elif anchor == "end": x -= w
    s = size / upm
    pen = SVGPathPen(gs); cx = x
    for info, p in zip(infos, pos):
        tp = TransformPen(pen, (s, 0, 0, -s, cx + p.x_offset * s, y - p.y_offset * s))
        gs[order[info.codepoint]].draw(tp)
        cx += p.x_advance * s + tracking * size
    return pen.getCommands()

def text_on_circle(text, font, size, cx, cy, r, start_deg=-90, tracking=0.0, inward=False, fill_circle=False):
    """Texto ao longo de um círculo (sentido horário a partir de start_deg; 0° = direita).
    fill_circle=True repete o texto até fechar a volta."""
    infos, pos, upm, gs, order = _shape(text, font, None)
    s = size / upm
    adv = [p.x_advance * s + tracking * size for p in pos]
    circ = 2 * math.pi * r
    seq = list(zip(infos, adv))
    if fill_circle:
        total = sum(adv); reps = max(1, int(circ // total))
        seq = seq * reps
        extra = (circ - total * reps) / max(len(seq), 1)
        seq = [(i, a + extra) for i, a in seq]
    pen = SVGPathPen(gs)
    a = math.radians(start_deg)
    for info, ad in seq:
        mid = a + (ad / 2) / r
        gname = order[info.codepoint]
        gw = gs[gname].width * s
        # base do glifo tangente ao círculo, centrada em 'mid'
        ang = mid + (math.pi / 2 if not inward else -math.pi / 2)
        ca, sa = math.cos(ang), math.sin(ang)
        bx, by = cx + r * math.cos(mid), cy + r * math.sin(mid)
        # posição do canto esquerdo da base, recuado meia largura ao longo da tangente
        ox, oy = bx - ca * gw / 2, by - sa * gw / 2
        if not inward:
            m = (s * ca, s * sa, s * sa, -s * ca, ox, oy)   # x ao longo da tangente, y para fora
        else:
            m = (s * ca, s * sa, -s * sa, s * ca, ox, oy)
        gs[gname].draw(TransformPen(pen, m))
        a += ad / r
    return pen.getCommands()

# ------------------------------------------------------------------ geometria
def P(x, y): return f"{x:.2f},{y:.2f}"

def polyline(points, close=False):
    d = "M" + " L".join(P(x, y) for x, y in points)
    return d + (" Z" if close else "")

def polar(cx, cy, r, deg):
    a = math.radians(deg); return cx + r * math.cos(a), cy + r * math.sin(a)

def rose(cx, cy, base, amp, lobes, phase=0.0, n=720, k2=0, amp2=0.0, phase2=0.0):
    """Curva de 'rose engine': r(θ) = base + amp·sin(lobes·θ + phase) + amp2·sin(k2·θ + phase2)."""
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        r = base + amp * math.sin(lobes * t + phase) + amp2 * math.sin(k2 * t + phase2)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return polyline(pts, True)

def hypotrochoid(cx, cy, R, r, d, turns=None, n=2400, scale=1.0, rot=0.0):
    g = math.gcd(int(R), int(r)); turns = turns or int(r // g)
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * turns * i / n
        x = (R - r) * math.cos(t) + d * math.cos((R - r) / r * t)
        y = (R - r) * math.sin(t) - d * math.sin((R - r) / r * t)
        xr = x * math.cos(rot) - y * math.sin(rot); yr = x * math.sin(rot) + y * math.cos(rot)
        pts.append((cx + scale * xr, cy + scale * yr))
    return polyline(pts)

def wave_band(x0, x1, y, amp, period, phase=0.0, step=2.0):
    pts = []; x = x0
    while x <= x1:
        pts.append((x, y + amp * math.sin(2 * math.pi * (x - x0) / period + phase))); x += step
    return polyline(pts)

# ------------------------------------------------------------------ svg / render
def svg(w, h, body, defs="", bg=None, extra=""):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" {extra}><defs>{defs}</defs>{b}{body}</svg>')

def lin_grad(uid, stops, x1=0, y1=0, x2=1, y2=1, user=None):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + '/>'
                 for o, c, *rest in stops for a in [rest[0] if rest else None])
    units = f' gradientUnits="userSpaceOnUse"' if user else ""
    if user: x1, y1, x2, y2 = user
    return f'<linearGradient id="{uid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{units}>{st}</linearGradient>'

def to_png(svg_text, path, width=None):
    kw = {"svg_string": svg_text}
    if width: kw["width"] = int(width)
    data = resvg_py.svg_to_bytes(**kw)
    open(path, "wb").write(data)
    return path

def png_bytes(svg_text, width=None):
    kw = {"svg_string": svg_text}
    if width: kw["width"] = int(width)
    return resvg_py.svg_to_bytes(**kw)

def animate(frame_fn, n_frames, out_mp4, fps=30, width=1920, height=1080, gif=None, gif_width=720):
    """frame_fn(i, t∈[0,1]) → svg; gera MP4 H.264 (e GIF opcional)."""
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps),
                          "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                          "-preset", "medium", "-movflags", "+faststart", out_mp4], stdin=subprocess.PIPE)
    for i in range(n_frames):
        p.stdin.write(png_bytes(frame_fn(i, i / (n_frames - 1)), width))
    p.stdin.close(); p.wait()
    if gif:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out_mp4, "-vf",
                        f"fps=15,scale={gif_width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160[p];[b][p]paletteuse=dither=sierra2_4a",
                        gif], check=True)

def html_to_pdf(html_path, pdf_path):
    subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", "file://" + os.path.abspath(html_path)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): return x * x * (3 - 2 * x)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

# ------------------------------------------------------------------ composição de texto (justificado, com hifenização)
def typeset(paras, font, size, x, y, width, lead, indent=0.0, drop=None, first_font=None, first_words=0,
            first_size=None, lang="pt_BR", last_line_max=None):
    """Compõe parágrafos justificados em curvas. paras: lista de strings. drop=(n_linhas, recuo) reserva espaço
    para a capitular nas primeiras linhas do 1º parágrafo; first_font/first_words: versaletes nas primeiras palavras.
    Devolve (lista de d, y final)."""
    import pyphen
    hy = pyphen.Pyphen(lang=lang)
    space = text_width(" ", font, size)
    out = []; line_no = 0
    for pi, para in enumerate(paras):
        words = para.split()
        toks = []
        for wi, w in enumerate(words):
            if pi == 0 and first_font and wi < first_words:
                toks.append([w.upper(), first_font, first_size or size])
            else:
                toks.append([w, font, size])
        lines = []; cur = []; i = 0
        while i < len(toks):
            t = toks[i]
            tw = text_width(t[0], t[1], t[2])
            used = sum(text_width(a[0], a[1], a[2]) for a in cur) + space * len(cur)
            lim = width - (drop[1] if drop and pi == 0 and len(lines) < drop[0] else 0) - (indent if (not lines and indent and not (drop and pi == 0)) else 0)
            if used + tw <= lim or not cur:
                cur.append(t); i += 1; continue
            # tenta hifenizar
            for a_, b_ in hy.iterate(t[0]):
                if used + text_width(a_ + "-", t[1], t[2]) <= lim and len(a_) >= 2 and len(b_) >= 3:
                    cur.append([a_ + "-", t[1], t[2]]); toks[i] = [b_, t[1], t[2]]; break
            lines.append((cur, lim, False)); cur = []
        if cur: lines.append((cur, width, True))
        for li, (ln, lim, last) in enumerate(lines):
            lx = x + (drop[1] if drop and pi == 0 and line_no < drop[0] else 0) + (indent if (li == 0 and indent and not (drop and pi == 0)) else 0)
            if drop and pi == 0 and line_no < drop[0]: lim = width - drop[1]
            elif li == 0 and indent and not (drop and pi == 0): lim = width - indent
            else: lim = width
            ws = [text_width(a[0], a[1], a[2]) for a in ln]
            gap = space if last or len(ln) == 1 else (lim - sum(ws)) / (len(ln) - 1)
            cx = lx
            for (tx, f, s), w_ in zip(ln, ws):
                out.append(text_path(tx, f, s, cx, y))
                cx += w_ + gap
            y += lead; line_no += 1
    return out, y
