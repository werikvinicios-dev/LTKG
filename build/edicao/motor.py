"""Motor de diagramação da Edição Imersiva (HTML → Chromium → PDF digital).

Cada página especial é um bloco HTML de tamanho fixo (página cheia, sem margem). O texto dos capítulos corre
em páginas nomeadas, uma por capítulo, para o cabeçalho levar o título do capítulo."""
import unicodedata, html, os, re, hashlib, subprocess
import pyphen
from PIL import Image

ROOT = "/home/user/LTKG"
B = f"{ROOT}/build/edicao"
FON = f"{ROOT}/build/fonts"
CACHE = f"{B}/_img"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
os.makedirs(CACHE, exist_ok=True)

W, H = 160, 240                     # mm, proporção 2:3 (tablet e celular)
OURO, MARFIM, NEGRO, CARMIM = "#C9A15A", "#EFE8DA", "#0D0C0B", "#8E1B22"
COR = {"Pulso": "#4F8BD6", "Brasa": "#C8332F", "Trama": "#C9A15A", "Clarão": "#F2E6C2", "Eco": "#9FB7D6", "Carga": "#D7B46A"}

_hy = pyphen.Pyphen(lang="pt_BR")


def img(path, maxw=2000, q=84):
    """Copia reduzida (JPG) para o cache; devolve URL file://."""
    if not os.path.isabs(path):
        path = f"{ROOT}/{path}"
    st = os.stat(path)
    k = hashlib.md5(f"{path}{st.st_mtime}{maxw}".encode()).hexdigest()[:12]
    dst = f"{CACHE}/{k}.jpg"
    if not os.path.exists(dst):
        im = Image.open(path).convert("RGB")
        if im.width > maxw:
            im = im.resize((maxw, round(maxw * im.height / im.width)), Image.LANCZOS)
        im.save(dst, quality=q, optimize=True, progressive=True)
    return "file://" + dst


def esc(t):
    return html.escape(t, quote=False)


def hifen(t):
    return " ".join(_hy.inserted(w, hyphen="­") if len(w) > 7 and w.isalpha() else w for w in t.split(" "))


def aspas(t):
    """Aspas retas viram tipográficas."""
    t = re.sub(r'(^|[\s(\[—])"', r"\1“", t)
    return t.replace('"', "”")


def selar(t, maximo=None):
    """A fonte Selar só tem A–Z: tira acentos e pontuação, e corta na palavra."""
    t = unicodedata.normalize("NFD", t.upper()).replace("-", " ")
    t = " ".join(re.sub(r"[^A-Z ]", "", t).split())
    if maximo and len(t) > maximo:
        t = t[:maximo].rsplit(" ", 1)[0]
    return t


def inline(t):
    t = esc(aspas(t))
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", t)
    return t


# ------------------------------------------------------------------ peças gráficas
def anel_svg(tam=60, cor=OURO, letra=None, disciplina=None, extra=""):
    """Selo-medalhão: anel duplo, eixo, pérolas; opcionalmente uma letra no centro (capitular)."""
    c = COR.get(disciplina, cor)
    s = f'''<svg viewBox="0 0 200 200" width="{tam}mm" height="{tam}mm" xmlns="http://www.w3.org/2000/svg" {extra}>
<circle cx="100" cy="100" r="92" fill="none" stroke="{cor}" stroke-width="2.2"/>
<circle cx="100" cy="100" r="80" fill="none" stroke="{cor}" stroke-width="0.9" stroke-dasharray="2 5"/>
<circle cx="100" cy="100" r="72" fill="none" stroke="{c}" stroke-width="1.6" opacity=".85"/>
<line x1="100" y1="2" x2="100" y2="26" stroke="{cor}" stroke-width="2"/><line x1="100" y1="174" x2="100" y2="198" stroke="{cor}" stroke-width="2"/>
<circle cx="100" cy="14" r="5" fill="{c}"/><circle cx="100" cy="186" r="3.4" fill="{cor}"/>
<path d="M30 160 L170 40" stroke="{c}" stroke-width="1" opacity=".55"/>'''
    if letra:
        s += f'<text x="100" y="128" text-anchor="middle" font-family="AT" font-weight="700" font-size="92" fill="{cor}">{esc(letra)}</text>'
    return s + "</svg>"


def ornamento(cor=OURO, larg=60):
    return f'''<div class="orn"><svg viewBox="0 0 300 24" width="{larg}mm" height="{larg * 0.08}mm"><path d="M0 12 H118 M182 12 H300" stroke="{cor}" stroke-width="1"/>
<circle cx="150" cy="12" r="9" fill="none" stroke="{cor}" stroke-width="1.4"/><circle cx="150" cy="12" r="3" fill="{cor}"/>
<circle cx="128" cy="12" r="2" fill="{cor}"/><circle cx="172" cy="12" r="2" fill="{cor}"/><path d="M141 21 L159 3" stroke="{cor}" stroke-width="1"/></svg></div>'''


# ------------------------------------------------------------------ páginas especiais (página cheia)
def pagina(conteudo, classe="", estilo="", nome="cheia"):
    return f'<section class="pg {classe}" style="page:{nome};{estilo}">{conteudo}</section>'


def imagem_cheia(path, pos="center", legenda=None, escurecer=False, fit="cover"):
    g = ('<div class="veu"></div>' if escurecer else "")
    leg = f'<div class="leg">{inline(legenda)}</div>' if legenda else ""
    return pagina(f'<div class="bg" style="background-image:url({img(path)});background-position:{pos};background-size:{fit}"></div>{g}{leg}', "img")


def respiro(path, frase, pos="center", autor=None):
    a = f'<div class="quem">{esc(autor)}</div>' if autor else ""
    return pagina(f'<div class="bg" style="background-image:url({img(path)});background-position:{pos}"></div><div class="veu baixo"></div>'
                  f'<div class="resp"><p>{inline(frase)}</p>{a}</div>', "img respiro")


def abertura_parte(num, titulo, epigrafe, path, pos="center", fonte_epi=None):
    fe = f'<div class="quem">{esc(fonte_epi)}</div>' if fonte_epi else ""
    return (imagem_cheia(path, pos) +
            pagina(f'''<div class="parte">{anel_svg(46)}<div class="pnum">Parte {esc(num)}</div><div class="ptit">{esc(titulo)}</div>
{ornamento()}<div class="pepi"><p>{inline(epigrafe)}</p>{fe}</div><div class="selar">{selar(titulo)}</div></div>''', "noite"))


def abertura_capitulo(n, titulo, path, pos="center", disciplina=None, epigrafe=None, rotulo="Capítulo"):
    epi = f'<div class="cepi">{inline(epigrafe)}</div>' if epigrafe else ""
    num = f'<div class="cnum">{n}</div>' if n else ""
    return (imagem_cheia(path, pos) +
            pagina(f'''<div class="cab">{anel_svg(34, disciplina=disciplina)}<div class="crot">{esc(rotulo)}</div>{num}
<div class="ctit">{esc(titulo)}</div>{ornamento()}{epi}<div class="selar s2">{selar(titulo, 22)}</div></div>''', "noite cap-ab"))


def documento(html_interno, tipo="carta"):
    return f'<div class="doc doc-{tipo}">{html_interno}</div>'


def banda(path, pos="center", altura=78, legenda=None):
    leg = f'<div class="bleg">{inline(legenda)}</div>' if legenda else ""
    return f'<figure class="banda" style="height:{altura}mm"><div class="bg" style="background-image:url({img(path, 1600)});background-position:{pos}"></div>{leg}</figure>'


# ------------------------------------------------------------------ texto do capítulo
def capitulo_texto(n, titulo_curto, md, insercoes=None):
    """md sem a linha de título. insercoes: {indice_do_paragrafo: html} entra depois daquele parágrafo."""
    insercoes = insercoes or {}
    blocos = [b.strip() for b in md.strip().split("\n\n") if b.strip()]
    out, primeiro, ip = [], True, 0
    for b in blocos:
        if b == "---":
            out.append(ornamento(larg=34))
            primeiro_pos_quebra = True
        else:
            t = inline(b)
            t = hifen(t) if not t.startswith("<") else t
            if primeiro:
                m = re.match(r"^(—\s*)?([A-Za-zÀ-ÿ])", b)
                letra = m.group(2) if m else b[0]
                resto = t[t.index(letra) + 1:] if letra in t else t[1:]
                pref = "— " if b.startswith("—") else ""
                out.append(f'<p class="p1"><span class="capitular">{anel_svg(19, letra=letra.upper())}</span>{pref}{resto}</p>')
                primeiro = False
            else:
                out.append(f"<p>{t}</p>")
        if ip in insercoes:
            out.append(insercoes[ip])
        ip += 1
    # fim do capítulo: as últimas falas curtas descem juntas, nunca uma linha sozinha numa página nova
    k = 0
    while k < min(3, len(out) - 1) and out[-1 - k].startswith("<p>") and sum(len(x) for x in out[len(out) - 1 - k:]) < 450:
        k += 1
    if k >= 1:
        k = max(k, 2) if out[-2].startswith("<p") else k
        out[-k:] = [f'<div class="fimcap">{"".join(out[-k:])}</div>']
    return f'<section class="texto" style="page:cap{n}">{"".join(out)}</section>'


def css(capitulos):
    """capitulos: lista de (n, título curto do cabeçalho)."""
    cab = "".join(
        f'@page cap{n}{{margin:19mm 17mm 21mm;@top-left{{content:"Leis para Matar Deuses";font:7pt AT;letter-spacing:.6mm;color:#9A8A6A}}'
        f'@top-right{{content:"{t}";font:7pt AT;letter-spacing:.6mm;color:#9A8A6A}}@bottom-center{{content:counter(page);font:8.5pt EBG;color:#7A6A4A}}}}'
        for n, t in capitulos)
    return f"""
@font-face{{font-family:AT;src:url(file://{FON}/ArestaTitular-Bold.ttf);font-weight:700}}
@font-face{{font-family:AT;src:url(file://{FON}/ArestaTitular-Regular.ttf);font-weight:400}}
@font-face{{font-family:SEL;src:url(file://{FON}/Selar-Regular.ttf)}}
@font-face{{font-family:EBG;src:url(file://{FON}/EBGaramond-Regular.ttf)}}
@font-face{{font-family:EBG;src:url(file://{FON}/EBGaramond-Italic.ttf);font-style:italic}}
@font-face{{font-family:EBG;src:url(file://{FON}/EBGaramond-SemiBold.ttf);font-weight:600}}
@font-face{{font-family:FELL;src:url(file://{FON}/IMFeFCrm28P.ttf)}}
@font-face{{font-family:FELL;src:url(file://{FON}/IMFeFCit28P.ttf);font-style:italic}}
@font-face{{font-family:FELLSC;src:url(file://{FON}/IMFeFCsc28P.ttf)}}
@page{{size:{W}mm {H}mm;margin:0}}
@page cheia{{margin:0}}
{cab}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0}}
body{{font-family:EBG;color:#2A2420;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:{W}mm;height:{H}mm;position:relative;overflow:hidden;break-after:page;break-before:page;background:#0D0C0B url(file://{B}/_tex/noite.jpg) center/cover}}
.pg.claro{{background:#F3ECDD url(file://{B}/_tex/papel.jpg) center/cover}}
.pg.perg{{background:#E5D6B8 url(file://{B}/_tex/pergaminho.jpg) center/cover}}
.bg{{position:absolute;inset:0;background-size:cover;background-repeat:no-repeat}}
.veu{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,7,6,.0) 40%,rgba(8,7,6,.72) 100%)}}
.veu.baixo{{background:linear-gradient(180deg,rgba(8,7,6,0) 46%,rgba(8,7,6,.86) 100%)}}
.leg{{position:absolute;left:14mm;right:14mm;bottom:10mm;font:italic 9pt EBG;color:#E9DFC8;text-align:center;text-shadow:0 0 3mm #000}}
.resp{{position:absolute;left:16mm;right:16mm;bottom:22mm;text-align:center;color:#F1E8D4}}
.resp p{{font:italic 15pt/1.35 EBG;margin:0;text-shadow:0 0 4mm rgba(0,0,0,.9)}}
.quem{{font:7.5pt AT;letter-spacing:1mm;color:{OURO};margin-top:4mm;text-transform:uppercase}}
.parte,.cab{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:{MARFIM};padding:0 18mm}}
.pnum{{font:400 11pt AT;letter-spacing:2.4mm;color:{OURO};margin-top:7mm;text-transform:uppercase}}
.ptit{{font:700 27pt/1.1 AT;letter-spacing:1mm;color:#E2C47E;margin:4mm 0 5mm}}
.pepi p{{font:italic 11.5pt/1.45 EBG;color:#E6DCC6;margin:6mm 0 0}}
.selar{{position:absolute;bottom:12mm;left:0;right:0;font:13pt SEL;letter-spacing:3mm;color:rgba(201,161,90,.45)}}
.selar.s2{{font-size:10pt;bottom:10mm}}
.crot{{font:400 9pt AT;letter-spacing:2.2mm;color:{OURO};margin-top:6mm;text-transform:uppercase}}
.cnum{{font:700 54pt/1 AT;color:#E2C47E;margin:2mm 0 3mm}}
.ctit{{font:700 18pt/1.2 AT;letter-spacing:.6mm;color:{MARFIM};margin-bottom:4mm;max-width:118mm}}
.cepi{{font:italic 10.5pt/1.45 EBG;color:#D9CFB8;margin-top:6mm;max-width:110mm}}
.orn{{text-align:center;margin:4mm 0}} .texto .orn{{margin:5mm 0 4mm}}
.texto{{font:10.6pt/1.47 EBG;text-align:justify;color:#2A2420}}
.texto p{{margin:0;text-indent:5mm;orphans:2;widows:2}}.fimcap{{break-inside:avoid}}
.texto p.p1,.texto .orn + p{{text-indent:0}}
.capitular{{float:left;width:19mm;height:19mm;margin:.6mm 2.5mm 0 -1mm}}
.banda{{margin:5mm 0;position:relative;break-inside:avoid;border-radius:.6mm;overflow:hidden;box-shadow:0 .4mm 1.6mm rgba(0,0,0,.35)}}
.bleg{{position:absolute;left:0;right:0;bottom:0;padding:6mm 5mm 2.4mm;font:italic 8.4pt EBG;color:#EFE6D2;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.7))}}
.doc{{break-inside:avoid;margin:6mm 2mm;padding:7mm 8mm;background:#EADBBE url(file://{B}/_tex/pergaminho.jpg) center/cover;
  box-shadow:0 .6mm 2.4mm rgba(60,40,10,.35);font:10pt/1.42 FELL;color:#2B2216;position:relative;text-align:left;text-indent:0}}
.doc p{{text-indent:0 !important;margin:0 0 2mm}} .doc .dt{{font:12pt FELLSC;letter-spacing:.5mm;text-align:center;margin-bottom:3mm}}
.doc .carimbo{{position:absolute;right:6mm;bottom:5mm;width:22mm;height:22mm;opacity:.82;transform:rotate(-14deg)}}
.doc-aviso{{background:#E8E0CC;border:1.2mm double #3A2E20}} .doc-livro{{font-family:EBG;background:#F1E8D2}}
"""


def compor(pecas, capitulos, saida_pdf, titulo="Leis para Matar Deuses", extra_css=""):
    hp = f"{B}/_html_" + os.path.basename(saida_pdf).replace(".pdf", ".html")
    doc = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{esc(titulo)}</title>'
           f'<style>{css(capitulos)}{extra_css}</style></head><body>{"".join(pecas)}</body></html>')
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=60000", f"--print-to-pdf={saida_pdf}", "file://" + hp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return saida_pdf
