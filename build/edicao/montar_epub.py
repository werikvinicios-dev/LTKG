#!/usr/bin/env python3
"""EPUB 3 ilustrado e completo da Edição Imersiva (texto que se ajusta à tela + todas as artes).
As páginas especiais (mapas, leis, armorial, galerias) entram como imagens renderizadas da própria diagramação."""
import os, re, subprocess, sys, uuid, html as H
sys.path.insert(0, os.path.dirname(__file__))
from ebooklib import epub
from PIL import Image
import montar_edicao as ME
from motor import compor, ROOT, B, FON
from especiais import leis, disciplinas, gramatica_selo, arquitetura, CSS_ESP
from mapas import planta_vhalessa, mapa_norte, mapa_aresta, pagina_mapa, legenda_vhalessa, CSS_MAPA
from armorial import armorial, CSS_ARM

OUT = f"{ROOT}/exportacoes/edicao_imersiva/Leis_para_Matar_Deuses_Vol1_Edicao_Imersiva.epub"
TMP = f"{B}/_epub"
os.makedirs(TMP, exist_ok=True)
CSS_TODO = CSS_ESP + CSS_MAPA + ME.CSS_LIVRO + CSS_ARM


def renderizar(nome, pecas):
    """Diagrama páginas especiais e devolve a lista de JPGs (uma por página)."""
    pdf = f"{TMP}/{nome}.pdf"
    compor(pecas, [], pdf, extra_css=CSS_TODO)
    for f in os.listdir(TMP):
        if f.startswith(nome + "-") and f.endswith(".jpg"):
            os.remove(f"{TMP}/{f}")
    subprocess.run(["pdftoppm", "-r", "160", "-jpeg", "-jpegopt", "quality=84", pdf, f"{TMP}/{nome}"], check=True)
    return sorted(f"{TMP}/{f}" for f in os.listdir(TMP) if f.startswith(nome + "-") and f.endswith(".jpg"))


class Livro:
    def __init__(self):
        self.b = epub.EpubBook()
        self.b.set_identifier(str(uuid.uuid5(uuid.NAMESPACE_URL, "lmd-vol1-imersiva-v2")))
        self.b.set_title("Leis para Matar Deuses — Volume I: O Deus que Caiu do Céu")
        self.b.set_language("pt-BR")
        self.b.add_author("Werik Martins")
        self.b.add_metadata("DC", "rights", "© Werik Martins")
        self.itens, self.toc, self.n_img = [], [], 0
        for f in ("EBGaramond-Regular.ttf", "EBGaramond-Italic.ttf", "EBGaramond-SemiBold.ttf", "ArestaTitular-Bold.ttf", "ArestaTitular-Regular.ttf", "IMFeFCrm28P.ttf"):
            self.b.add_item(epub.EpubItem(uid=f, file_name=f"fonts/{f}", media_type="font/ttf", content=open(f"{FON}/{f}", "rb").read()))
        self.css = epub.EpubItem(uid="css", file_name="estilo.css", media_type="text/css", content=CSS_EPUB.encode())
        self.b.add_item(self.css)
        self.imgs = {}

    def imagem(self, path, maxw=1600):
        if not os.path.isabs(path):
            path = f"{ROOT}/{path}"
        if path in self.imgs:
            return self.imgs[path]
        self.n_img += 1
        nome = f"img/i{self.n_img:03d}.jpg"
        im = Image.open(path).convert("RGB")
        if im.width > maxw:
            im = im.resize((maxw, round(maxw * im.height / im.width)), Image.LANCZOS)
        from io import BytesIO
        bio = BytesIO(); im.save(bio, "JPEG", quality=82, optimize=True, progressive=True)
        self.b.add_item(epub.EpubItem(uid=f"i{self.n_img}", file_name=nome, media_type="image/jpeg", content=bio.getvalue()))
        self.imgs[path] = nome
        return nome

    def doc(self, nome, titulo, corpo, toc=None, classe=""):
        c = epub.EpubHtml(title=titulo, file_name=f"{nome}.xhtml", lang="pt-BR")
        c.content = f'<html><head><title>{H.escape(titulo)}</title></head><body class="{classe}">{corpo}</body></html>'
        c.add_item(self.css)
        self.b.add_item(c); self.itens.append(c)
        if toc is not None:
            toc.append(c)
        return c

    def pagina_imagem(self, nome, path, titulo, toc=None, alt=""):
        return self.doc(nome, titulo, f'<div class="cheia"><img src="{self.imagem(path)}" alt="{H.escape(alt or titulo)}"/></div>', toc, "img")


def aspas(t):
    t = re.sub(r'(^|[\s(\[—])"', r"\1“", t)
    return t.replace('"', "”")


def paragrafos(md, ins):
    blocos = [b.strip() for b in md.strip().split("\n\n") if b.strip()]
    out = []
    for i, b in enumerate(blocos):
        if b == "---":
            out.append('<p class="orn">◆</p>')
        else:
            t = H.escape(aspas(b), quote=False)
            t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
            t = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", t)
            out.append(f'<p class="{"p1" if i == 0 else ""}">{t}</p>')
        out.extend(ins.get(i, []))
    return "".join(out)


def capitulo(L, n, toc_parte):
    rot, titulo, corpo = ME.ler_capitulo(n)
    pl = ME.PLANO.get(n, {})
    abertura, bandas, finais = ME.ARTE[n]
    blocos = [b.strip() for b in corpo.strip().split("\n\n") if b.strip()]
    ins = {}
    alvos = [i for i in pl.get("ilustracoes", []) if i["tipo"] in ("dupla", "spot")]
    for k, b in enumerate(bandas):
        i = ME.achar_paragrafo(blocos, alvos[k]["trecho_ancora"] if k < len(alvos) else "", .45 + .2 * k)
        ins.setdefault(i, []).append(f'<div class="fig"><img src="{L.imagem(ME.arq(b))}" alt=""/></div>')
    for d in pl.get("documentos_do_mundo", [])[:2]:
        i = ME.achar_paragrafo(blocos, d.get("onde_entra", ""), .3)
        txt = re.sub(r"(?i)âncoras?", "selo", d.get("conteudo", ""))
        ins.setdefault(i, []).append('<div class="doc">' + "".join(f"<p>{H.escape(l.strip())}</p>" for l in txt.split("\n") if l.strip()) + "</div>")
    epi = pl.get("epigrafe_sugerida")
    cab = (f'<div class="fig cheia"><img src="{L.imagem(ME.arq(abertura))}" alt=""/></div>'
           f'<div class="cab"><p class="crot">{rot}</p>' + (f'<p class="cnum">{n}</p>' if rot == "Capítulo" else "") +
           f'<h1>{H.escape(titulo)}</h1>' + (f'<p class="cepi">{H.escape(epi)}</p>' if epi else "") + "</div>")
    fim = "".join(f'<div class="fig cheia"><img src="{L.imagem(ME.arq(f))}" alt=""/></div>' for f in finais)
    q = pl.get("citacao_respiro")
    if q:
        fim += (f'<div class="fig cheia"><img src="{L.imagem(ME.RESPIROS[(n - 1) % len(ME.RESPIROS)])}" alt=""/></div>'
                f'<p class="resp">{H.escape(q)}</p>')
    rotulo = f"{n}. {titulo}" if rot == "Capítulo" else f"Epílogo. {titulo}"
    L.doc(f"cap{n:02d}", rotulo, cab + paragrafos(corpo, ins) + fim, toc_parte)


import armorial as AR


def figura(L, path, titulo=None, legenda=None):
    cap = ""
    if titulo or legenda:
        cap = "<figcaption>" + (f"<b>{H.escape(titulo)}</b>" if titulo else "") + (f"<br/>{H.escape(legenda)}" if legenda else "") + "</figcaption>"
    return f'<figure><img src="{L.imagem(path)}" alt="{H.escape(titulo or "")}"/>{cap}</figure>'


def coletar(L, fn):
    """Roda as funções do Codex do PDF trocando a diagramação por figuras com legenda (mesmo conteúdo)."""
    out = []
    salvo = {k: getattr(AR, k) for k in ("placa", "galeria", "heroi", "divisor", "insignias")}
    AR.placa = lambda path, titulo, legenda, rotulo="": out.append(figura(L, path, titulo, legenda)) or ""
    AR.galeria = lambda titulo, itens, *a, **k: out.append(f"<h2>{H.escape(titulo)}</h2>" + "".join(figura(L, p, t, x) for p, t, x in itens)) or ""
    AR.heroi = lambda path, titulo, sub, pos="": out.append(figura(L, path, titulo, sub)) or ""
    AR.divisor = lambda titulo, sub, selar="": out.append(f'<p class="nota">{H.escape(sub)}</p>') or ""
    AR.insignias = lambda: out.append("<h2>Insígnias</h2><div class=\"insg\">" + "".join(
        f'<div class="ins"><img src="{L.imagem(f"{ROOT}/{AR.SIM}/instituicoes/{k}_decorativa.png", 500)}" alt="{H.escape(t)}"/><p>{H.escape(t)}</p></div>' for k, t in AR.INSIGNIAS) + "</div>") or ""
    try:
        fn()
    finally:
        for k, v in salvo.items():
            setattr(AR, k, v)
    return "".join(out)


def fig_gramatica():
    import especiais
    pg = especiais.gramatica_selo()
    i0 = pg.index('<svg viewBox="0 0 400 330"'); svg = pg[i0:pg.index("</svg>", i0) + 6].replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    hp, png = f"{TMP}/gram.html", f"{TMP}/gram.png"
    open(hp, "w").write(f'<html><head><style>{CSS_TODO}</style></head><body style="margin:0;background:#141210">{svg.replace("width=\"128mm\" height=\"106mm\"", "width=\"1200\" height=\"990\"")}</body></html>')
    subprocess.run([ME.SHELL, "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,990", f"--screenshot={png}", "file://" + hp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return png


def montar():
    L = Livro()
    capa = f"{ROOT}/exportacoes/capa_v2/capa_ebook.jpg"
    L.b.set_cover("capa.jpg", open(capa, "rb").read())
    L.pagina_imagem("guarda", renderizar("guarda", [ME.mapa_ref()])[0], "Aresta")
    L.pagina_imagem("frontispicio", f"{ME.B4}/PE-019_ilan_e_aurelia_vhalessa_v2_4x.jpg", "Frontispício")
    L.doc("rosto", "Folha de rosto", '<div class="rosto"><p class="r1">Leis para Matar Deuses</p><p class="r2">Volume I</p>'
          '<p class="r3">O Deus que Caiu do Céu</p><p class="r4">Werik Martins</p></div>')
    L.doc("creditos", "Créditos", '<div class="cred"><p>© Werik Martins. Todos os direitos reservados.</p><p>Edição Digital Imersiva, outubro de 2026. Texto da V2.</p>'
          '<p>Tipografia: Aresta Titular e Selar (criadas para esta edição), EB Garamond e IM Fell (SIL Open Font License).</p>'
          '<p><i>Fantasia para adultos. Contém violência, morte, linguagem forte e cenas de sexo.</i></p></div>')
    atlas = renderizar("atlas", [pagina_mapa(mapa_norte()), pagina_mapa(planta_vhalessa())])
    toc_atlas = []
    L.doc("atlas0", "Aresta", figura(L, f"{ME.R4}/RF-001_mapa_de_aresta_4x.jpg", "Aresta", "o continente, as suas terras e os caminhos que as ligam"), toc_atlas)
    L.pagina_imagem("atlas1", atlas[0], "O Norte", toc_atlas)
    L.pagina_imagem("atlas2", atlas[1], "Vhalessa", toc_atlas)
    import mapas
    L.doc("atlas3", "Vhalessa, lugar por lugar", "<h2>Vhalessa, lugar por lugar</h2>" + "".join(
        f'<p class="lug"><b>{n}. {H.escape(nm)}</b> — {H.escape(lg)}</p>' for n, nm, _, _, lg in mapas.LOCAIS_VHALESSA), toc_atlas)
    toc_mundo = []
    import especiais
    L.doc("mundo0", "As Sete Leis", "<h2>As Sete Leis</h2>" + figura(L, f"{ME.R4}/RF-002_sete_leis_4x.jpg") +
          "".join(f'<p class="lei"><b>{r} · {H.escape(n)}.</b> {H.escape(x)}</p>' for r, n, _, x in especiais.LEIS) +
          '<p class="nota">Valem para mortais, deuses e dragões. Nenhum selo, nenhuma coroa e nenhuma prece muda uma vírgula delas.</p>', toc_mundo)
    L.doc("mundo1", "Os Seis Sinais", "<h2>Os Seis Sinais</h2>" + figura(L, f"{ME.R4}/RF-003_seis_disciplinas_4x.jpg") +
          "".join(f'<p class="lei"><b>{H.escape(n)}.</b> {H.escape(x)}; acende os selos em luz {c}.</p>' for n, _, x, c in especiais.DISC), toc_mundo)
    L.doc("mundo2", "A gramática do selo", "<h2>A gramática do selo</h2>" + figura(L, fig_gramatica()) +
          '<p class="lei"><b>1 · Sinal:</b> qual disciplina passa. <b>2 · Cauda:</b> por onde pode passar. <b>3 · Tamanho:</b> quanto cabe. <b>4 · Traço de terra:</b> para onde vai o contragolpe.</p>'
          '<p class="lei"><b>Selo conjurado.</b> Sai da mão, do pé ou do olhar treinado. Um risco fino de luz que todo mundo vê. Dura segundos. É rápido, fraco e cansa.</p>'
          '<p class="lei"><b>Selo gravado.</b> Fixado em pedra, couro, bronze ou osso, com tempo e ferramenta. Forte, dura anos. Pode ser raspado, rasurado ou tomado.</p>'
          '<p class="nota">Um selo não é uma força. É um endereço. Quem paga a conta é o mundo. Selo sem traço de terra devolve o contragolpe a quem fez.</p>', toc_mundo)
    L.doc("mundo3", "Toda magia, em seis passos", "<h2>Toda magia, em seis passos</h2>" + figura(L, f"{ME.BA}/02_simbolos/SI-003_etapas_da_transposicao.png") +
          '<p class="lei">Fonte (de onde sai) · Selo (onde se prende) · Vínculo (por onde passa) · Destino (para onde vai) · Controle (quem segura) · Retorno (o que volta).</p>'
          '<p class="nota">A magia não cria nada. Ela muda de lugar o que já existe.</p>', toc_mundo)
    L.doc("mundo4", "O elenco", "<h2>O elenco</h2>" + "".join(
        f'<div class="el"><img src="{L.imagem(p, 900)}" alt="{H.escape(n)}"/><p class="lei"><b>{H.escape(n)}.</b> {H.escape(t)}</p></div>' for n, p, t in ME.ELENCO), toc_mundo)
    L.toc += [(epub.Section("Atlas"), toc_atlas), (epub.Section("Antes de começar"), toc_mundo)]
    for num, tit, c0, c1, epi, fonte, im, pos in ME.PARTES:
        tp = []
        L.doc(f"parte{num}", f"Parte {num} · {tit}", f'<div class="fig cheia"><img src="{L.imagem(im)}" alt=""/></div>'
              f'<div class="parte"><p class="pnum">Parte {num}</p><h1>{H.escape(tit)}</h1><p class="cepi">{H.escape(epi)}</p><p class="crot">{H.escape(fonte)}</p></div>', tp)
        for n in range(c0, c1 + 1):
            capitulo(L, n, tp)
        L.toc.append((epub.Section(f"Parte {num} · {tit}"), tp))
    toc_codex = []
    for nome, titulo, fn in (("codexA", "A Senhora dos Limiares", lambda: AR.aurelia()), ("codexB", "Galeria de personagens", lambda: AR.expressoes() + AR.galeria_acervo()),
                             ("codexC", "Arsenal e artefatos", lambda: AR.arsenal()), ("codexD", "Engenharia arcana", lambda: AR.engenharia()),
                             ("codexE", "Armorial de Aresta", lambda: AR.armorial())):
        L.doc(nome, titulo, f"<h1>{H.escape(titulo)}</h1>" + coletar(L, fn).replace(f"<h2>{H.escape(titulo)}</h2>", ""), toc_codex)
    L.doc("codexF", "Glossário", "<h1>Glossário</h1>" + "".join(f'<p class="lei"><b>{H.escape(t)}.</b> {H.escape(x)}</p>' for t, x in ME.GLOSSARIO), toc_codex)
    L.toc.append((epub.Section("Codex de Aresta"), toc_codex))
    L.pagina_imagem("contracapa", f"{ME.DR}/capas_e_marca/C02_Contracapa_Arte_Sem_Texto.png", "Contracapa")
    L.b.toc = L.toc
    L.b.add_item(epub.EpubNcx()); L.b.add_item(epub.EpubNav())
    L.b.get_item_with_id("cover").is_linear = True
    L.b.spine = ["cover", "nav"] + L.itens
    epub.write_epub(OUT, L.b)
    return OUT


CSS_EPUB = """
@font-face{font-family:EBG;src:url(fonts/EBGaramond-Regular.ttf)} @font-face{font-family:EBG;font-style:italic;src:url(fonts/EBGaramond-Italic.ttf)}
@font-face{font-family:EBG;font-weight:600;src:url(fonts/EBGaramond-SemiBold.ttf)} @font-face{font-family:AT;src:url(fonts/ArestaTitular-Bold.ttf)}
@font-face{font-family:FELL;src:url(fonts/IMFeFCrm28P.ttf)}
body{font-family:EBG,serif;line-height:1.5;margin:0 4%} p{margin:0;text-indent:1.2em;text-align:justify} p.p1,p.orn+p{text-indent:0}
p.p1::first-letter{font-family:AT;font-size:1.9em;color:#8E1B22;line-height:1} p.p1::first-line{font-variant:small-caps;letter-spacing:.04em}
h1{font-family:AT;font-weight:normal;text-align:center;font-size:1.5em;letter-spacing:.06em;margin:.3em 0 .6em}
.cab,.parte{text-align:center;margin:1.5em 0 2em} .crot,.pnum{font-family:AT;letter-spacing:.3em;font-size:.8em;color:#9C7A3C;text-indent:0;text-align:center}
.cnum{font-family:AT;font-size:3em;color:#9C7A3C;text-indent:0;text-align:center;margin:.1em 0}
.cepi{font-style:italic;text-indent:0;text-align:center;margin-top:1em} p.orn{text-align:center;text-indent:0;color:#9C7A3C;margin:1em 0}
.fig{margin:1.2em 0;text-align:center} .fig img{max-width:100%} .cheia img{width:100%}
.doc{font-family:FELL,serif;background:#EEE2C8;color:#2B2216;padding:.8em 1em;margin:1.2em 0;border:1px solid #B79E6E}
.doc p{text-indent:0;text-align:left;margin:0 0 .4em}
.resp{font-style:italic;text-align:center;text-indent:0;margin:.6em 0 2em}
body.img{margin:0} .cheia{margin:0;text-align:center}
.rosto{text-align:center;margin-top:30%} .rosto p{text-indent:0;text-align:center} .r1{font-family:AT;font-size:2em}
.r2{font-family:AT;letter-spacing:.3em;margin-top:1em} .r3{font-style:italic;font-size:1.2em} .r4{font-family:AT;margin-top:3em}
.cred p{text-indent:0;margin:.6em 0;font-size:.9em}
h2{font-family:AT;font-weight:normal;text-align:center;font-size:1.25em;letter-spacing:.05em;margin:1.4em 0 .6em;color:#6B5220}
figure{margin:1.2em 0;text-align:center;page-break-inside:avoid} figure img{max-width:100%;max-height:92vh}
figcaption{font-size:.85em;font-style:italic;margin-top:.4em;text-align:center} figcaption b{font-family:AT;font-style:normal;letter-spacing:.04em}
p.lei{text-indent:0;text-align:left;margin:.5em 0} p.nota{text-indent:0;font-style:italic;text-align:center;margin:1em 0} p.lug{text-indent:0;margin:.35em 0}
.el{margin:1.2em 0;page-break-inside:avoid} .el img{width:42%;float:left;margin:0 .8em .4em 0;border-radius:4px} .el:after{content:"";display:block;clear:both}
.insg{text-align:center} .ins{display:inline-block;width:30%;vertical-align:top;margin:.4em 1%} .ins img{width:100%} .ins p{text-indent:0;text-align:center;font-size:.75em}
.fig img,.cheia img{max-height:95vh}
"""

if __name__ == "__main__":
    print(montar())
