#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capa v2 (identidade Aresta) do Volume I: frente a partir da arte CA-001, capa do EPUB, miniatura,
versão sem texto (pôster) e capa completa aberta (verso + lombada + frente) para prévia.
Saída: exportacoes/capa_v2/. Usa a versão ampliada 4× da arte (build/aresta/ampliar.py) quando existe:
capa do e-book com 2560 px de altura e frente em alta resolução (4096 px de largura)."""
import os, subprocess, sys
from PIL import Image
ROOT = "/home/user/LTKG"
BA = f"{ROOT}/exportacoes/banco_de_arte"
OUT = f"{ROOT}/exportacoes/capa_v2"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
F = f"file://{ROOT}/build/fonts"
os.makedirs(OUT, exist_ok=True)
paginas = int(sys.argv[1]) if len(sys.argv) > 1 else 500
lombada = round(paginas * 0.056, 1)          # mm, papel pólen 80 g (mesma regra da capa v1)

A4X = f"{ROOT}/exportacoes/banco_de_arte_4x/07_capas/CA-001_capa_vol1_o_deus_que_caiu_do_ceu_4x.jpg"
src = Image.open(A4X if os.path.exists(A4X) else f"{BA}/07_capas/CA-001_capa_vol1_o_deus_que_caiu_do_ceu.png").convert("RGB")
W, H = src.size; h = round(W * 230 / 160); top = (H - h) // 2
front = src.crop((0, top, W, top + h))
tam = lambda alt: (round(alt * W / h), alt)
front.resize(tam(min(h, 2944)), Image.LANCZOS).save(f"{OUT}/capa_frente_digital.png")
front.resize(tam(min(h, 2560)), Image.LANCZOS).save(f"{OUT}/capa_ebook.jpg", quality=92)
if W >= 4096: front.save(f"{OUT}/capa_frente_alta_resolucao.jpg", quality=93, subsampling=0)
front.resize((200, round(200 * h / W)), Image.LANCZOS).save(f"{OUT}/capa_miniatura_200px.jpg", quality=90)
P4X = f"{ROOT}/exportacoes/banco_de_arte_4x/10_promocional/PR-001_poster_cinematografico_4x.jpg"
poster = Image.open(P4X if os.path.exists(P4X) else f"{BA}/10_promocional/PR-001_poster_cinematografico.png").convert("RGB")
poster.thumbnail((3072, 3072), Image.LANCZOS); poster.save(f"{OUT}/arte_promocional_poster.jpg", quality=92)

Image.open(f"{BA}/01_identidade/ID-001_logo_principal_vertical.png").convert("RGB").crop((0, 1430, 1024, 1536)).resize((1024, 212)).save(f"{ROOT}/build/_pedra.jpg", quality=90)
mm = lambda v: f"{v}mm"
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Cz;src:url('{F}/Cinzel-SemiBold.ttf')}} @font-face{{font-family:Gi;src:url('{F}/EBGaramond-Italic.ttf')}}
@page{{size:{160 * 2 + lombada}mm 230mm;margin:0}} *{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{160 * 2 + lombada}mm;height:230mm;background:#0B0A09;position:relative;overflow:hidden}}
.back{{position:absolute;left:0;top:0;width:160mm;height:230mm;background:linear-gradient(rgba(8,7,6,.35),rgba(8,7,6,.6)),
  url(file://{ROOT}/build/_pedra.jpg) center/cover}}
.spine{{position:absolute;left:160mm;top:0;width:{lombada}mm;height:230mm;background:linear-gradient(90deg,#060505,#16120E 50%,#060505);
  border-left:.3mm solid #5a4628;border-right:.3mm solid #5a4628}}
.front{{position:absolute;left:{160 + lombada}mm;top:0;width:160mm;height:230mm;background:url(file://{OUT}/capa_frente_digital.png) center/cover}}
.q{{position:absolute;left:22mm;right:22mm;top:118mm;font-family:Gi;font-size:13pt;line-height:1.45;color:#D9CDB4;text-align:center}}
.sc{{font-family:Cz;letter-spacing:1.4mm;color:#C9A15A;text-transform:uppercase}}
.frame{{position:absolute;inset:7mm;border:.35mm solid #6B5532}} .frame:after{{content:"";position:absolute;inset:1.6mm;border:.2mm solid rgba(201,161,90,.4)}}
.isbn{{position:absolute;right:16mm;bottom:16mm;width:42mm;height:24mm;border:.3mm dashed #6B5532;color:#6B5532;font-family:Cz;font-size:6pt;
  letter-spacing:.6mm;display:flex;align-items:center;justify-content:center}}
</style></head><body>
<div class="back"><div class="frame"></div>
 <img src="file://{BA}/01_identidade/ID-008_emblema_transparente.png" style="position:absolute;left:50mm;top:26mm;width:60mm">
 <div class="q">Leis são mais que palavras.<br>São armas, fronteiras e memórias.<br>São os vestígios de um mundo que se recusa a morrer.</div>
 <div class="sc" style="position:absolute;left:0;right:0;top:160mm;text-align:center;font-size:8pt">Saga ◆ Aresta · Volume I</div>
 <div class="isbn">ISBN · código de barras</div></div>
<div class="spine">
 <img src="file://{BA}/01_identidade/ID-009_emblema_medalhao.png" style="position:absolute;left:{(lombada - 20) / 2}mm;top:12mm;width:20mm">
 <div style="position:absolute;left:50%;top:118mm;transform:translate(-50%,-50%) rotate(90deg);white-space:nowrap" class="sc">
  <span style="font-size:15pt;letter-spacing:1.2mm;color:#E2C47E">Leis para Matar Deuses</span></div>
 <div class="sc" style="position:absolute;left:0;right:0;top:184mm;text-align:center;font-size:12pt;color:#E2C47E">I</div>
 <div style="position:absolute;left:50%;top:207mm;transform:translate(-50%,-50%) rotate(90deg);white-space:nowrap;font-size:6pt" class="sc">Werik Martins</div>
</div>
<div class="front"></div></body></html>"""
hp = f"{ROOT}/build/_capa_v2.html"; open(hp, "w", encoding="utf-8").write(html)
pdf = f"{OUT}/capa_completa_previa_{paginas}p_lombada{lombada}mm.pdf"
subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                f"--print-to-pdf={pdf}", "file://" + hp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", pdf, f"{OUT}/capa_completa_previa"], check=True)
print(pdf, lombada)
