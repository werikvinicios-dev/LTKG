#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capa de *Leis para Matar Deuses — Vol. 1*: frente (PNG/JPG para EPUB e divulgação) e
capa completa de gráfica (contracapa + lombada + frente, com 3 mm de sangria), em PDF e PNG.

Composta em HTML/CSS + SVG e renderizada no Chromium headless (tipografia vetorial no PDF).
Uso: python3 build/make_capa_luxo.py [páginas_do_miolo] [mm_por_página]
"""
import base64, os, subprocess, sys

ROOT = "/home/user/LTKG"
B = f"{ROOT}/build"
OUT = f"{ROOT}/exportacoes/capa"
os.makedirs(OUT, exist_ok=True)
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"

PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 500
MM_PAGE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.056   # pólen/offset 80 g ≈ 0,11 mm por folha
SPINE = round(PAGES * MM_PAGE, 1)
TW, TH, BL = 160, 230, 3

def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

FONTS_CSS = "\n".join(
    f"@font-face{{font-family:'{fam}';src:url('{b64(f'{B}/fonts/{f}', 'font/ttf')}');"
    f"font-weight:{w};font-style:{st}}}"
    for fam, f, w, st in [("EBG", "EBGaramond-Regular.ttf", 400, "normal"),
                          ("EBG", "EBGaramond-Italic.ttf", 400, "italic"),
                          ("EBG", "EBGaramond-SemiBold.ttf", 600, "normal"),
                          ("EBGSC", "EBGaramondSC-Regular.ttf", 400, "normal"),
                          ("Cinzel", "Cinzel-Regular.ttf", 400, "normal"),
                          ("Cinzel", "Cinzel-Bold.ttf", 700, "normal")])

ART = b64(f"{B}/arte/capa_arte.jpg", "image/jpeg")
LOGOTIPO = open(f"{ROOT}/exportacoes/grafico/logo/logotipo_bronze.svg").read()
EMBLEMA = open(f"{ROOT}/exportacoes/grafico/logo/emblema_bronze.svg").read()

def svg_inline(svg, cls):
    return svg.replace("<svg ", f'<svg class="{cls}" preserveAspectRatio="xMidYMid meet" ', 1)

BLURB = [
    "Em Vhalessa, quem aquece as casas é um deus.",
    "Há quase trezentos anos, na noite mais longa do ano, Calvenor, o Sol de Inverno, sobe ao alto "
    "da Torre do Meio-Dia e acende a lente que mantém viva uma cidade de seiscentas mil pessoas. "
    "Este ano, diante de todos, ele cai.",
    "Ilan Varek desliga reservatórios por encomenda, conta cada segundo de uma briga e junta dinheiro "
    "para um terreno onde nunca neva. Também é o último Carrasco vivo de uma ordem que sabia matar "
    "deuses — o que faz dele o suspeito perfeito.",
    "Aurelia, Soberana dos Limiares, senhora das portas que ligam metade do mundo, assume a custódia "
    "do único homem capaz de explicar o que aconteceu. Ela precisa de respostas antes que o frio "
    "comece a contar os mortos. Ele precisa provar que não foi ele.",
    "Uma fantasia épica adulta sobre leis que nenhum deus pode quebrar, contas que alguém terá de "
    "pagar e o preço de manter uma cidade aquecida.",
]

def front_html(w_mm, h_mm, bleed_mm=0):
    """Frente da capa como bloco HTML (posição relativa)."""
    return f"""
<div class="front" style="width:{w_mm}mm;height:{h_mm}mm">
  <div class="art"></div>
  <div class="shade-top"></div><div class="shade-bot"></div>
  <div class="logo" style="top:{bleed_mm + 13}mm">{svg_inline(LOGOTIPO, 'wm')}</div>
  <div class="vol" style="top:{bleed_mm + 47.5}mm">VOLUME 1</div>
  <div class="sub" style="top:{bleed_mm + 53}mm">O Deus que Caiu do Céu</div>
  <div class="author" style="bottom:{bleed_mm + 11}mm">WERIK MARTINS</div>
</div>"""

CSS = FONTS_CSS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#10141c}
.front{position:relative;overflow:hidden;background:#10141c}
.front .art{position:absolute;inset:0;background:url('""" + ART + """') center top/cover no-repeat}
.shade-top{position:absolute;left:0;right:0;top:0;height:38%;
  background:linear-gradient(to bottom,rgba(8,10,16,.82),rgba(8,10,16,.35) 65%,rgba(8,10,16,0))}
.shade-bot{position:absolute;left:0;right:0;bottom:0;height:24%;
  background:linear-gradient(to top,rgba(8,10,16,.92),rgba(8,10,16,.4) 60%,rgba(8,10,16,0))}
.logo{position:absolute;left:0;right:0;display:flex;justify-content:center}
.wm{width:78%;height:auto;filter:drop-shadow(0 0.6mm 1.2mm rgba(0,0,0,.65))}
.vol{position:absolute;left:0;right:0;text-align:center;font-family:Cinzel;font-size:3.1mm;
  letter-spacing:1.6mm;color:#d8bb83;text-shadow:0 0 2mm rgba(0,0,0,.8)}
.sub{position:absolute;left:0;right:0;text-align:center;font-family:EBG;font-style:italic;
  font-size:6.4mm;color:#efe8d8;text-shadow:0 0.4mm 2mm rgba(0,0,0,.9)}
.author{position:absolute;left:0;right:0;text-align:center;font-family:Cinzel;font-size:5.2mm;
  letter-spacing:2.2mm;color:#efe8d8;text-shadow:0 0 2mm rgba(0,0,0,.9)}
.back{position:relative;background:radial-gradient(ellipse at 50% 30%,#1a2130 0%,#10141c 70%);color:#e9e2d2;overflow:hidden}
.back .emb{position:absolute;opacity:.07}
.back .txt{position:absolute;font-family:EBG;font-size:3.75mm;line-height:5.5mm;text-align:justify;hyphens:auto}
.back .txt p{margin-bottom:2.6mm}
.back .txt p:first-child{font-family:EBG;font-style:italic;font-size:5.2mm;line-height:6.6mm;color:#d8bb83;text-align:left}
.back .saga{position:absolute;font-family:Cinzel;font-size:2.6mm;letter-spacing:1mm;color:#b9935a}
.back .isbn{position:absolute;background:#fff;color:#888;font-family:EBG;font-size:2.4mm;display:flex;align-items:center;justify-content:center}
.spine{position:relative;background:#0c1017;overflow:hidden}
.e{width:100%;height:100%;display:block}
.scol{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:space-between}
.vt{writing-mode:vertical-rl;font-family:Cinzel;white-space:nowrap}
.spine .stxt{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(90deg);white-space:nowrap;
  font-family:Cinzel;color:#d3b47a;display:flex;align-items:center;gap:6mm}
.spine .t1{font-size:4.4mm;letter-spacing:1.2mm;font-weight:700}
.spine .t2{font-size:3mm;letter-spacing:1mm;color:#efe8d8}
.spine .emb{position:absolute;left:50%;transform:translateX(-50%)}
"""

def page(html, w_mm, h_mm):
    return (f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>@page{{size:{w_mm}mm {h_mm}mm;margin:0}}"
            f"{CSS}</style></head><body style='width:{w_mm}mm;height:{h_mm}mm'>{html}</body></html>")

def render_png(html_path, png, w_px, h_px):
    subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w_px},{h_px}", f"--screenshot={png}", "file://" + html_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_pdf(html_path, pdf):
    subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + html_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    tmp = f"{B}/_capa_tmp"; os.makedirs(tmp, exist_ok=True)
    # ---- frente (sem sangria) — 300 dpi
    fh = page(front_html(TW, TH), TW, TH)
    p = f"{tmp}/frente.html"; open(p, "w").write(fh)
    # 1 mm = 300/25.4 px; a janela em CSS px (96/in) → usar escala via zoom: renderizar em 1890x2717
    W300, H300 = round(TW / 25.4 * 300), round(TH / 25.4 * 300)
    zoom = W300 / (TW / 25.4 * 96)
    fh_png = fh.replace("<body ", f"<body style='zoom:{zoom}' data-z ", 1).replace("data-z style=", "data-y=")
    p2 = f"{tmp}/frente_png.html"; open(p2, "w").write(fh_png)
    render_png(p2, f"{OUT}/capa_frente_300dpi.png", W300, H300)
    render_pdf(p, f"{OUT}/capa_frente.pdf")
    from PIL import Image
    im = Image.open(f"{OUT}/capa_frente_300dpi.png").convert("RGB")
    im.save(f"{OUT}/capa_frente.jpg", quality=92)
    im.resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS).save(f"{ROOT}/exportacoes/capa_ebook.jpg", quality=90)
    # ---- capa completa com sangria
    W = BL + TW + SPINE + TW + BL; H = BL + TH + BL
    blurb = "".join(f"<p>{t}</p>" for t in BLURB)
    back = f"""
<div class="back" style="position:absolute;left:0;top:0;width:{BL+TW}mm;height:{H}mm">
  <div class="emb" style="left:{BL+20}mm;top:{BL+48}mm;width:120mm;height:120mm">{svg_inline(EMBLEMA,'e')}</div>
  <div class="txt" style="left:{BL+20}mm;top:{BL+24}mm;width:{TW-38}mm">{blurb}</div>
  <div class="saga" style="left:{BL+20}mm;bottom:{BL+20}mm">LEIS PARA MATAR DEUSES · VOLUME 1</div>
  <div class="isbn" style="right:{18}mm;bottom:{BL+14}mm;width:38mm;height:22mm">espaço para ISBN</div>
</div>
<div class="spine" style="position:absolute;left:{BL+TW}mm;top:0;width:{SPINE}mm;height:{H}mm">
  <div class="scol" style="padding:{BL+9}mm 0 {BL+12}mm 0">
    <div style="width:{min(SPINE-8, 15)}mm;height:{min(SPINE-8, 15)}mm">{svg_inline(EMBLEMA,'e')}</div>
    <div class="vt" style="font-size:5.2mm;letter-spacing:1.3mm;font-weight:700;color:#d3b47a">LEIS PARA MATAR DEUSES</div>
    <div class="vt" style="font-size:3mm;letter-spacing:1.1mm;color:#efe8d8">VOLUME 1</div>
    <div class="vt" style="font-size:3.2mm;letter-spacing:1.2mm;color:#efe8d8">WERIK MARTINS</div>
  </div>
</div>
<div style="position:absolute;left:{BL+TW+SPINE}mm;top:0">{front_html(TW+BL, H, BL)}</div>
"""
    ch = page(back, W, H)
    p3 = f"{tmp}/completa.html"; open(p3, "w").write(ch)
    render_pdf(p3, f"{OUT}/capa_completa_grafica_{PAGES}p_lombada{SPINE}mm.pdf")
    zoomc = 1200 / (W / 25.4 * 96)
    p4 = f"{tmp}/completa_png.html"
    open(p4, "w").write(ch.replace("<body ", f"<body style='zoom:{zoomc}' data-y=", 1))
    render_png(p4, f"{OUT}/capa_completa_previa.png", 1200, round(1200 * H / W))
    print(f"capa: lombada {SPINE} mm para {PAGES} páginas; arquivos em {OUT}")
