#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta as saídas textuais da versão revisada de linguagem (V1-RL):

  exportacoes/MANUSCRITO_V1_REVISAO_LINGUAGEM.md    manuscrito integral editável (Markdown)
  exportacoes/MANUSCRITO_V1_REVISAO_LINGUAGEM.docx  manuscrito integral editável (Word)
  exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.epub EPUB 3 de luxo (fontes embutidas, capitulares,
                                                    ornamentos, pranchas, capa)
"""
import glob, os, re, subprocess
from PIL import Image

ROOT = "/home/user/LTKG"
CAP = f"{ROOT}/manuscrito/V1_revisao_linguagem"
EXP = f"{ROOT}/exportacoes"
B = f"{ROOT}/build"
TMP = f"{B}/_epub_tmp"; os.makedirs(TMP, exist_ok=True)

NUM_EXT = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
           "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito",
           "dezenove", "vinte", "vinte e um", "vinte e dois", "vinte e três", "vinte e quatro",
           "vinte e cinco", "vinte e seis", "vinte e sete", "vinte e oito", "vinte e nove", "trinta"]

DESCRICAO = ("Em Vhalessa, quem aquece as casas é um deus. Na noite mais longa do ano, diante de "
             "todos, Calvenor, o Sol de Inverno, cai do alto da própria torre. Ilan Varek, o último "
             "Carrasco vivo de uma ordem que sabia matar deuses, é o suspeito perfeito; Aurelia, "
             "Soberana dos Limiares, assume a custódia dele antes que o frio comece a contar os mortos. "
             "Fantasia épica adulta.")

PLATES_AFTER = {2: ("atrio", "O Átrio de Soleira"), 4: ("ilan_aurelia", "Ilan Varek e a Soberania dos Limiares")}

def chapters():
    for f in sorted(glob.glob(f"{CAP}/[0-9][0-9].md")):
        yield int(os.path.basename(f)[:2]), open(f, encoding="utf-8").read().strip("\n")

def curly(t):
    t = re.sub(r'(^|[\s(\[—–-])"', r'\1“', t)
    return t.replace('"', '”')

def epub_images():
    out = {}
    for name in ("vhalessa", "atrio", "ilan_aurelia"):
        im = Image.open(f"{B}/arte/{name}.jpg").convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS)
        p = f"{TMP}/{name}.jpg"; im.save(p, quality=84); out[name] = p
    emb = Image.open(f"{EXP}/grafico/logo/emblema_bronze_chapado.png")
    emb.resize((240, 240), Image.LANCZOS).save(f"{TMP}/emblema.png")
    logo = Image.open(f"{EXP}/grafico/logo/logotipo_tinta.png")
    logo.resize((1200, round(1200 * logo.height / logo.width)), Image.LANCZOS).save(f"{TMP}/logotipo.png")
    return out

def manuscrito_md():
    parts = ["---", 'title: "Leis para Matar Deuses"', 'subtitle: "Volume 1 — O Deus que Caiu do Céu"',
             'author: "Werik Martins"', "lang: pt-BR",
             'description: "Manuscrito integral — versão revisada de linguagem (V1-RL)"', "...", ""]
    for n, txt in chapters():
        parts.append(txt); parts.append("")
    p = f"{EXP}/MANUSCRITO_V1_REVISAO_LINGUAGEM.md"
    open(p, "w", encoding="utf-8").write("\n".join(parts))
    return p

def epub_md(imgs):
    L = []
    L += ["---", 'title: "Leis para Matar Deuses"', 'subtitle: "Volume 1 — O Deus que Caiu do Céu"',
          "creator:", "  - role: author", '    text: "Werik Martins"', "lang: pt-BR",
          'rights: "© 2026 Werik Martins. Todos os direitos reservados."',
          f'description: "{DESCRICAO}"', 'subject: "Fantasia épica"', 'toc-title: "Sumário"', "...", ""]
    # folha de rosto + créditos + frontispício (antes do primeiro h1)
    L += ['<div class="rosto">', "", f"![]({TMP}/logotipo.png){{.logo}}", "",
          '<p class="volume">VOLUME 1</p>', '<p class="subtitulo">O Deus que Caiu do Céu</p>',
          '<p class="autor">WERIK MARTINS</p>', "", "</div>", "",
          '::: prancha', "", f"![]({imgs['vhalessa']})", "", "Vhalessa, na véspera da noite mais longa", "", ":::", "",
          '::: creditos', "",
          "*Leis para Matar Deuses* — Volume 1: *O Deus que Caiu do Céu*", "",
          "Copyright © 2026 Werik Martins. Todos os direitos reservados.", "",
          "Edição de luxo ilustrada — texto da versão revisada de linguagem (V1-RL).", "",
          "Esta é uma obra de ficção. Nomes, lugares, deuses e acontecimentos são invenção do autor ou usados de forma ficcional.", "",
          "Tipografia: EB Garamond e Cinzel (SIL Open Font License). Identidade visual, emblema e ornamentos: projeto gráfico desta edição. Ilustrações geradas com auxílio de inteligência artificial sob direção de arte desta edição.", "",
          ":::", ""]
    for n, txt in chapters():
        lines = txt.split("\n")
        title = lines[0][2:].strip()
        m = re.match(r"(Cap[íi]tulo\s+(\d+)|Ep[íi]logo)\s*—\s*(.+)", title)
        label = f"Capítulo {NUM_EXT[int(m.group(2))]}" if m.group(2) else "Epílogo"
        name = m.group(3)
        L.append(f"# [{label}]{{.num}}[\u00a0—\u00a0]{{.sep}}{name} {{#cap-{n:02d}}}")
        L += ["", f"![]({TMP}/emblema.png){{.emblema-img width=2.6em}}", ""]
        blocks = [b.strip() for b in re.split(r"\n\s*\n", "\n".join(lines[1:])) if b.strip()]
        first = True
        for b in blocks:
            if b == "---":
                L += ['<p class="quebra">◆ ◆ ◆</p>', ""]; continue
            b = curly(b)
            if b.startswith("*Fim do Volume") or b.startswith("*A saga"):
                L += ["::: fim", "", b, "", ":::", ""]; continue
            if first:
                cls = ".abertura" if b.startswith("— ") or len(b) < 95 else ".abertura .capitular"
                L += [f"::: {{{cls}}}", "", b, "", ":::", ""]; first = False
            else:
                L += [b, ""]
        if n in PLATES_AFTER:
            key, cap = PLATES_AFTER[n]
            L += ["::: prancha", "", f"![]({imgs[key]})", "", cap, "", ":::", ""]
    L += ["::: colofao", "",
          "Composto em EB Garamond, de Georg Duffner e Octavio Pardo, e Cinzel, de Natanael Gama. "
          "Os sete losangos do emblema são as sete leis da Transposição.", "", ":::", ""]
    p = f"{TMP}/livro_epub.md"
    open(p, "w", encoding="utf-8").write("\n".join(L))
    return p

def reference_docx():
    ref = f"{TMP}/reference.docx"
    with open(ref, "wb") as f:
        f.write(subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                               check=True, capture_output=True).stdout)
    import docx
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_LINE_SPACING
    d = docx.Document(ref)
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        st = {s.name: s for s in d.styles}.get(name)
        if st is None:
            continue
        st.font.name = "EB Garamond"; st.font.size = Pt(12)
        pf = st.paragraph_format
        pf.line_spacing = 1.5; pf.space_after = Pt(0); pf.space_before = Pt(0)
        pf.first_line_indent = Cm(0) if name == "First Paragraph" else Cm(1.0)
    by_name = {s.name: s for s in d.styles}
    for name in ("Heading 1", "Title", "Subtitle"):
        st = by_name[name]; st.font.name = "EB Garamond"; st.font.color.rgb = None
    by_name["Heading 1"].font.size = Pt(18); by_name["Heading 1"].paragraph_format.page_break_before = True
    d.save(ref)
    return ref

if __name__ == "__main__":
    imgs = epub_images()
    md = manuscrito_md()
    ref = reference_docx()
    subprocess.run(["pandoc", md, "--toc", "--toc-depth=1", f"--reference-doc={ref}",
                    "-o", f"{EXP}/MANUSCRITO_V1_REVISAO_LINGUAGEM.docx"], check=True)
    emd = epub_md(imgs)
    fonts = [f"{B}/fonts/{f}" for f in ("EBGaramond-Regular.ttf", "EBGaramond-Italic.ttf",
                                        "EBGaramond-SemiBold.ttf", "EBGaramondSC-Regular.ttf",
                                        "Cinzel-Regular.ttf")]
    cmd = ["pandoc", emd, "-f", "markdown+fenced_divs+bracketed_spans+raw_html", "-t", "epub3",
           "--epub-title-page=false", f"--css={B}/epub.css", f"--epub-cover-image={EXP}/capa/capa_ebook.jpg",
           "--toc", "--toc-depth=1", "--split-level=1", "-o", f"{EXP}/Leis_para_Matar_Deuses_Vol1_LUXO.epub"]
    for f in fonts:
        cmd.append(f"--epub-embed-font={f}")
    subprocess.run(cmd, check=True)
    print("ok:", md, "| docx | epub")
