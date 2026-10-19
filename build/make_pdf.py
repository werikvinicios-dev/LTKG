#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compõe o PDF de leitura de 'Leis para Matar Deuses — Vol. 1' a partir dos capítulos .md."""
import os, re, glob
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, NextPageTemplate)
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.flowables import Flowable, HRFlowable

CAP_DIR = "/home/user/LTKG/manuscrito/capitulos"
OUT = "/home/user/LTKG/exportacoes/Leis_para_Matar_Deuses_Vol1.pdf"
TITLE = "Leis para Matar Deuses"
AUTHOR = "Werik Martins"

# --- fontes serifadas ---
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_BI = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
pdfmetrics.registerFont(TTFont("Body", SERIF))
pdfmetrics.registerFont(TTFont("Body-B", SERIF_B))
pdfmetrics.registerFont(TTFont("Body-I", SERIF_I))
pdfmetrics.registerFont(TTFont("Body-BI", SERIF_BI))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B",
                              italic="Body-I", boldItalic="Body-BI")

PAGE = A5
ML, MR, MT, MB = 18*mm, 18*mm, 20*mm, 20*mm

styles = {
    "body": ParagraphStyle("body", fontName="Body", fontSize=11.2, leading=16,
                           alignment=TA_JUSTIFY, firstLineIndent=5.2*mm,
                           spaceBefore=0, spaceAfter=0),
    "body_first": ParagraphStyle("body_first", fontName="Body", fontSize=10.3,
                           leading=15.5, alignment=TA_JUSTIFY, firstLineIndent=0,
                           spaceBefore=0, spaceAfter=0),
    "chap_num": ParagraphStyle("chap_num", fontName="Body", fontSize=12,
                           alignment=TA_CENTER, textColor="#8a6a36", leading=16,
                           spaceAfter=4),
    "chap_title": ParagraphStyle("chap_title", fontName="Body-B", fontSize=19,
                           alignment=TA_CENTER, leading=23, spaceAfter=10),
}

def md_inline(t):
    # itálico *...* -> <i>, escapar &<>
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t

class SceneBreak(Flowable):
    def __init__(self):
        Flowable.__init__(self); self.height = 11*mm
    def draw(self):
        self.canv.setFont("Body", 11)
        self.canv.setFillColor("#8a6a36")
        w = self.canv.stringWidth("◇", "Body", 11)
        self.canv.drawString((self.width-w)/2, 4*mm, "◇")

def parse_chapter(path):
    """Retorna (titulo_num, titulo_txt, lista de flowables do corpo)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    title = None
    body = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            title = ln[2:].strip()
        i += 1
    # separar número e nome do capítulo
    num, name = "", title or ""
    m = re.match(r"(Cap[íi]tulo\s+\d+|Ep[íi]logo)\s*—\s*(.+)", title or "")
    if m:
        num, name = m.group(1), m.group(2)
    # construir corpo
    flows = []
    text = "\n".join(lines)
    # remover o título
    text = re.sub(r"^#.*?\n", "", text, count=1, flags=re.S if False else 0)
    # processar parágrafos / separadores
    blocks = re.split(r"\n\s*\n", text)
    first_para = True
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith("# "):
            continue
        if b == "---":
            flows.append(Spacer(1, 2*mm))
            flows.append(SceneBreak())
            flows.append(Spacer(1, 1*mm))
            first_para = True
            continue
        if b.startswith("*Fim do Volume") or b.startswith("*A saga"):
            flows.append(Spacer(1, 6*mm))
            flows.append(Paragraph(md_inline(b), ParagraphStyle(
                "end", parent=styles["body_first"], alignment=TA_CENTER,
                textColor="#8a6a36", fontSize=11)))
            continue
        st = styles["body_first"] if first_para else styles["body"]
        flows.append(Paragraph(md_inline(b.replace("\n", " ")), st))
        first_para = False
    return num, name, flows

class BookDoc(BaseDocTemplate):
    def __init__(self, fn):
        BaseDocTemplate.__init__(self, fn, pagesize=PAGE,
            leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
            title=TITLE, author=AUTHOR)
        fw = PAGE[0]-ML-MR
        fh = PAGE[1]-MT-MB
        frame = Frame(ML, MB, fw, fh, id="f", leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        self.cur_chapter = ""
        self.addPageTemplates([
            PageTemplate(id="plain", frames=[frame], onPage=self._plain),
            PageTemplate(id="chap", frames=[frame], onPage=self._blank),
            PageTemplate(id="title", frames=[frame], onPage=self._blank),
        ])
    def _blank(self, canv, doc):
        pass
    def _plain(self, canv, doc):
        canv.saveState()
        canv.setFont("Body", 8)
        canv.setFillColor("#7a7a7a")
        pn = doc.page
        # cabeçalho discreto: título à esquerda (par), capítulo à direita (ímpar)
        if pn % 2 == 0:
            canv.drawString(ML, PAGE[1]-MT+8*mm, TITLE)
        else:
            canv.drawRightString(PAGE[0]-MR, PAGE[1]-MT+8*mm, self.cur_chapter)
        # número de página centralizado no rodapé
        canv.drawCentredString(PAGE[0]/2, MB-10*mm, str(pn))
        canv.restoreState()

class SetChapter(Flowable):
    """marca o capítulo corrente para o cabeçalho."""
    def __init__(self, doc, name): self.doc=doc; self.name=name; self.width=0; self.height=0
    def draw(self): self.doc.cur_chapter = self.name

doc = BookDoc(OUT)
story = []

# --- folha de rosto ---
story.append(NextPageTemplate("title"))
story.append(Spacer(1, 40*mm))
story.append(Paragraph(TITLE.upper(), ParagraphStyle("t", fontName="Body-B",
    fontSize=28, alignment=TA_CENTER, leading=34, textColor="#1a1a1a")))
story.append(Spacer(1, 6*mm))
story.append(HRFlowable(width="40%", thickness=1, color="#8a6a36", spaceBefore=2, spaceAfter=8))
story.append(Paragraph("VOLUME 1", ParagraphStyle("v", fontName="Body",
    fontSize=13, alignment=TA_CENTER, textColor="#8a6a36", leading=18)))
story.append(Paragraph("<i>O Deus que Caiu do Céu</i>", ParagraphStyle("st",
    fontName="Body-I", fontSize=15, alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 50*mm))
story.append(Paragraph(AUTHOR.upper(), ParagraphStyle("a", fontName="Body",
    fontSize=15, alignment=TA_CENTER, textColor="#1a1a1a")))
story.append(NextPageTemplate("plain"))
story.append(PageBreak())

# --- capítulos ---
files = sorted(glob.glob(os.path.join(CAP_DIR, "[0-9]*.md")))
for idx, f in enumerate(files):
    num, name, flows = parse_chapter(f)
    header_name = name if num.lower().startswith("ep") else f"{num} · {name}"
    story.append(SetChapter(doc, header_name))
    story.append(Spacer(1, 22*mm))
    if num:
        story.append(Paragraph(num.upper(), styles["chap_num"]))
    story.append(Paragraph(name, styles["chap_title"]))
    story.append(HRFlowable(width="18%", thickness=0.8, color="#8a6a36",
                            spaceBefore=2, spaceAfter=12))
    story.extend(flows)
    if idx != len(files)-1:
        story.append(PageBreak())

doc.build(story)
print("PDF gerado:", OUT)
