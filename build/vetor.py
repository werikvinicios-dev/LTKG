#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilitários de vetor para a identidade visual: texto → caminhos SVG (HarfBuzz + fontTools)
e renderização de SVG/HTML com o Chromium headless."""
import os, subprocess, tempfile
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = "/home/user/LTKG/build/fonts"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

_cache = {}

def _font(name):
    if name not in _cache:
        path = os.path.join(FONTS, name)
        data = open(path, "rb").read()
        face = hb.Face(data)
        hbf = hb.Font(face)
        tt = TTFont(path)
        _cache[name] = (hbf, tt, tt["head"].unitsPerEm)
    return _cache[name]

def text_width(text, font, size, tracking=0.0):
    hbf, tt, upm = _font(font)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": True})
    adv = sum(p.x_advance for p in buf.glyph_positions)
    n = len(buf.glyph_infos)
    return adv * size / upm + tracking * size * max(n - 1, 0)

def text_path(text, font, size, x, y, tracking=0.0, anchor="start"):
    """Devolve o atributo d de um <path> com o texto já em curvas. y = linha de base.
    tracking em fração do corpo (0.1 = 10% do corpo entre letras)."""
    hbf, tt, upm = _font(font)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": True})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    w = text_width(text, font, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    scale = size / upm
    pen = SVGPathPen(gs)
    cx = x
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = order[info.codepoint]
        tpen = TransformPen(pen, (scale, 0, 0, -scale, cx + pos.x_offset * scale, y - pos.y_offset * scale))
        gs[gname].draw(tpen)
        cx += pos.x_advance * scale + tracking * size
    return pen.getCommands()

def render(html_or_svg_path, png_path, width, height, transparent=True, scale=1):
    args = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
            f"--screenshot={png_path}"]
    if transparent:
        args.append("--default-background-color=00000000")
    args.append("file://" + os.path.abspath(html_or_svg_path))
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def svg_to_png(svg_text, png_path, width, height, transparent=True):
    """Renderiza um SVG (texto) no tamanho exato pedido."""
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write("<!doctype html><html><head><meta charset='utf-8'><style>html,body{margin:0;padding:0;"
                + ("background:transparent" if transparent else "background:#fff")
                + "}svg{display:block;width:%dpx;height:%dpx}</style></head><body>%s</body></html>"
                % (width, height, svg_text))
        tmp = f.name
    render(tmp, png_path, width, height, transparent)
    os.unlink(tmp)

def html_to_pdf(html_path, pdf_path):
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
                    "file://" + os.path.abspath(html_path)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
