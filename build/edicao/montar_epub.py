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


def paragrafos(md, ins):
    blocos = [b.strip() for b in md.strip().split("\n\n") if b.strip()]
    out = []
    for i, b in enumerate(blocos):
        if b == "---":
            out.append('<p class="orn">◆</p>')
        else:
            t = H.escape(b, quote=False)
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
    atlas = renderizar("atlas", [pagina_mapa(mapa_norte()), pagina_mapa(planta_vhalessa()), legenda_vhalessa({})])
    toc_atlas = []
    for k, f in enumerate(atlas):
        L.pagina_imagem(f"atlas{k}", f, ["O Norte", "Vhalessa", "Vhalessa, lugar por lugar"][k], toc_atlas)
    mundo = renderizar("mundo", [ME.placa(f"{ME.R4}/RF-002_sete_leis_4x.jpg", "As Sete Leis", "", ""), ME.placa(f"{ME.R4}/RF-003_seis_disciplinas_4x.jpg", "Os Seis Sinais", "", ""), gramatica_selo(), ME.placa(f"{ME.BA}/02_simbolos/SI-003_etapas_da_transposicao.png", "Toda magia, em seis passos", "Fonte · Selo · Vínculo · Destino · Controle · Retorno", ""), ME.elenco()])
    toc_mundo = []
    for k, f in enumerate(mundo):
        L.pagina_imagem(f"mundo{k}", f, ["As Sete Leis", "Os Seis Sinais", "A gramática do selo", "Toda magia, em seis passos", "O elenco"][k], toc_mundo)
    L.toc += [(epub.Section("Atlas"), toc_atlas), (epub.Section("Antes de começar"), toc_mundo)]
    for num, tit, c0, c1, epi, fonte, im, pos in ME.PARTES:
        tp = []
        L.doc(f"parte{num}", f"Parte {num} · {tit}", f'<div class="fig cheia"><img src="{L.imagem(im)}" alt=""/></div>'
              f'<div class="parte"><p class="pnum">Parte {num}</p><h1>{H.escape(tit)}</h1><p class="cepi">{H.escape(epi)}</p><p class="crot">{H.escape(fonte)}</p></div>', tp)
        for n in range(c0, c1 + 1):
            capitulo(L, n, tp)
        L.toc.append((epub.Section(f"Parte {num} · {tit}"), tp))
    from armorial import aurelia, galeria_acervo, expressoes, arsenal, engenharia
    codex_pecas = aurelia() + expressoes() + galeria_acervo() + arsenal() + engenharia() + armorial() + [ME.glossario()]
    toc_codex = []
    for k, f in enumerate(renderizar("codex", codex_pecas)):
        L.pagina_imagem(f"codex{k:02d}", f, "Codex de Aresta" if k == 0 else f"Codex {k}", toc_codex if k == 0 else None)
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
p.p1::first-letter{font-family:AT;font-size:3.2em;float:left;line-height:.9;margin:.05em .08em 0 0;color:#8E1B22}
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
"""

if __name__ == "__main__":
    print(montar())
