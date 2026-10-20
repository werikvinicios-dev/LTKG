#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Uma página: a linguagem antes (V1) e depois (V1-RL) da revisão.
Trechos só das primeiras páginas do capítulo 1 (sem spoilers) + métricas do livro inteiro.
Saída: relatorio/Comparativo_linguagem_antes_depois.pdf (A4 horizontal) e .png
"""
import difflib, html, re, subprocess

ROOT = "/home/user/LTKG"
F = f"file://{ROOT}/build/fonts"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
A = open(f"{ROOT}/manuscrito/V1_original_preservado/01.md", encoding="utf-8").read()
B = open(f"{ROOT}/manuscrito/V1_revisao_linguagem/01.md", encoding="utf-8").read()

def cut(text, start, end):
    i = text.index(start); j = text.index(end, i) + len(end)
    return re.sub(r"\s*\n+\s*", " ", text[i:j]).strip()

def diff(a, b):
    """Marca palavras removidas (antes) e acrescentadas (depois)."""
    ta, tb = a.split(" "), b.split(" ")
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    oa, ob = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        sa = html.escape(" ".join(ta[i1:i2])); sb = html.escape(" ".join(tb[j1:j2]))
        if op == "equal":
            oa.append(sa); ob.append(sb)
        else:
            if sa: oa.append(f"<del>{sa}</del>")
            if sb: ob.append(f"<ins>{sb}</ins>")
    return " ".join(oa), " ".join(ob)

PARES = [
    ("Período longo, dividido em frases que se leem de uma vez",
     cut(A, "Ilan contou as janelas", "morrer de frio."),
     cut(B, "Ilan contou as janelas", "morrer de frio.")),
    ("Ação: primeiro o efeito, depois a explicação curta",
     cut(A, "O bastão veio", "dado um passo por ele."),
     cut(B, "O bastão desceu", "dado o passo por ele.")),
    ("Magia: a mesma regra, explicada com menos peso",
     cut(A, "Não brigou com o acoplamento", "na direção contrária."),
     cut(B, "Não brigou com as âncoras", "no sentido contrário.")),
    ("Narração em português brasileiro (próclise, sem “lhe”)",
     cut(A, "Ilan virou-se.", "portas baixas;"),
     cut(B, "Ilan se virou.", "portas baixas.")),
]
TIQUES = [
    (cut(A, "— Vinte e dois", "termômetro da esquina."), cut(B, "— Vinte e dois", "termômetro da esquina.")),
    (cut(A, "Sevran quase sorriu.", "quase sorriu."), cut(B, "Um canto da boca", "se mexeu.")),
    (cut(A, "Os dois homens não se olharam", "lido em voz alta."), cut(B, "Os dois não se olharam", "lido em voz alta.")),
    (cut(A, "— Também é uma opção.", "na frente."), cut(B, "— Também é uma opção.", "na frente.")),
]

METRICAS = [("590 → 301", "frases com mais de 40 palavras"),
            ("105 → 7", "ênclises na narração (“virou-se”, “deu-lhe”)"),
            ("86 → 21", "“ficou calado / em silêncio”"),
            ("48 → 24", "contrastes “Não era X. Era Y.”"),
            ("31/31", "capítulos conferidos sem perda de fato")]

def row(titulo, a, b):
    da, db = diff(a, b)
    return (f'<div class="row"><div class="tag">{titulo}</div>'
            f'<div class="c a">{da}</div><div class="c b">{db}</div></div>')

rows = "".join(row(t, a, b) for t, a, b in PARES)
tiq = "".join(f'<div class="mini"><div class="c a">{x}</div><div class="c b">{y}</div></div>'
              for x, y in (diff(a, b) for a, b in TIQUES))
mets = "".join(f'<div class="m"><div class="n">{n}</div><div class="l">{l}</div></div>' for n, l in METRICAS)

page = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@font-face{{font-family:EBG;src:url('{F}/EBGaramond-Regular.ttf')}}
@font-face{{font-family:EBG;font-style:italic;src:url('{F}/EBGaramond-Italic.ttf')}}
@font-face{{font-family:EBG;font-weight:600;src:url('{F}/EBGaramond-SemiBold.ttf')}}
@font-face{{font-family:EBGSC;src:url('{F}/EBGaramondSC-Regular.ttf')}}
@font-face{{font-family:Cinzel;src:url('{F}/Cinzel-Regular.ttf')}}
@page{{size:297mm 210mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:297mm;height:210mm;background:#f6f2ea;color:#1e1a16;font-family:EBG;padding:10mm 13mm;overflow:hidden}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:.4mm solid #b48c4e;padding-bottom:2.5mm}}
.k{{font-family:Cinzel;font-size:2.6mm;letter-spacing:1.1mm;color:#8a6631}}
h1{{font-style:italic;font-weight:400;font-size:8.2mm;line-height:1.05;margin-top:1mm}}
.mets{{display:flex;gap:5mm}}
.m{{text-align:right;width:31mm}} .m .n{{font-family:Cinzel;font-size:4.6mm;color:#8a6631;white-space:nowrap}}
.m .l{{font-size:2.55mm;line-height:3.2mm;color:#5d5850}}
.head{{display:grid;grid-template-columns:40mm 1fr 1fr;gap:5mm;margin:3mm 0 1.2mm}}
.head div{{font-family:Cinzel;font-size:2.8mm;letter-spacing:.9mm;color:#8a6631}}
.row{{display:grid;grid-template-columns:40mm 1fr 1fr;gap:5mm;padding:2.2mm 0;border-bottom:.2mm solid #ddd3c2}}
.tag{{font-family:EBG;font-style:italic;font-size:3.35mm;line-height:4.2mm;color:#6b5a3e}}
.c{{font-size:3.45mm;line-height:4.55mm;text-align:justify;hyphens:auto}}
.a{{color:#6f6a62}}
del{{text-decoration:line-through;text-decoration-color:rgba(160,60,40,.75);color:#9a5a48;background:rgba(190,90,60,.08)}}
ins{{text-decoration:none;background:rgba(180,140,78,.28);border-radius:.6mm;padding:0 .3mm}}
.mini{{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin-bottom:1.3mm}}
.minis{{grid-column:2 / span 2}}
.foot{{position:absolute;left:13mm;right:13mm;bottom:7mm;font-size:2.7mm;line-height:3.6mm;color:#6f6a62;
  display:flex;justify-content:space-between;gap:10mm}}
.leg del,.leg ins{{padding:0 .8mm}}
</style></head><body>
<div class="top">
  <div><div class="k">Leis para Matar Deuses · Volume 1 · revisão de linguagem</div>
       <h1>Antes e depois</h1></div>
  <div class="mets">{mets}</div>
</div>
<div class="head"><div></div><div>Antes — V1</div><div>Depois — V1-RL</div></div>
{rows}
<div class="row"><div class="tag">Fórmulas repetidas e registro das falas (“com a satisfação de quem…”,
“quase sorriu”, “Não era… Era…”, “teu” na boca de quem diz “você”)</div><div class="minis">{tiq}</div></div>
<div class="foot">
  <div>Trechos tirados só das primeiras páginas do capítulo 1, para não adiantar nada da história. O livro
  inteiro passou pelos mesmos critérios. As métricas acima são do livro completo (V1 × V1-RL).</div>
  <div class="leg" style="white-space:nowrap"><del>removido</del> &nbsp; <ins>acrescentado ou reescrito</ins></div>
</div>
</body></html>"""

tmp = f"{ROOT}/build/_comparativo.html"
open(tmp, "w", encoding="utf-8").write(page)
out = f"{ROOT}/relatorio/Comparativo_linguagem_antes_depois.pdf"
subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out}",
                "file://" + tmp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", out, out[:-4]], check=True)
print(out)
