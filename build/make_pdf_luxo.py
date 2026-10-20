#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagramação de luxo de *Leis para Matar Deuses — Vol. 1* (PDF, 16 × 23 cm).

Miolo em EB Garamond (com versaletes reais), títulos em Cinzel, acentos em bronze.
Margens espelhadas, hifenização pt-BR, sem viúvas nem órfãs, capitulares, capítulos
abrindo sempre em página ímpar, pranchas ilustradas, sumário com páginas reais.

Uso: python3 build/make_pdf_luxo.py [--sangria]   (--sangria gera a versão de gráfica,
     com 3 mm de sangria e TrimBox/BleedBox definidos em todas as páginas)
"""
import os, re, sys, glob
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, NextPageTemplate, Flowable)
from reportlab.platypus.flowables import ParagraphAndImage
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg

ROOT = "/home/user/LTKG"
CAP_DIR = f"{ROOT}/manuscrito/V1_revisao_linguagem"
FONTS = f"{ROOT}/build/fonts"
ART = f"{ROOT}/build/arte"
LOGO = f"{ROOT}/exportacoes/grafico/logo"
BLEED = "--sangria" in sys.argv
OUT = (f"{ROOT}/exportacoes/Leis_para_Matar_Deuses_Vol1_GRAFICA_sangria.pdf" if BLEED
       else f"{ROOT}/exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.pdf")

TITLE = "Leis para Matar Deuses"
SUBTITLE = "O Deus que Caiu do Céu"
AUTHOR = "Werik Martins"

# ---------------------------------------------------------------- fontes
def reg(name, file):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, file)))
reg("Gar", "EBGaramond-Regular.ttf"); reg("Gar-I", "EBGaramond-Italic.ttf")
reg("Gar-SB", "EBGaramond-SemiBold.ttf"); reg("Gar-SBI", "EBGaramond-SemiBoldItalic.ttf")
reg("GarSC", "EBGaramondSC-Regular.ttf")
reg("Cin", "Cinzel-Regular.ttf"); reg("Cin-B", "Cinzel-Bold.ttf"); reg("Cin-SB", "Cinzel-SemiBold.ttf")
pdfmetrics.registerFontFamily("Gar", normal="Gar", bold="Gar-SB", italic="Gar-I", boldItalic="Gar-SBI")
pdfmetrics.registerFontFamily("GarSC", normal="GarSC", bold="GarSC", italic="Gar-I", boldItalic="Gar-I")

INK = HexColor("#1b1814")
BRONZE = HexColor("#8a6631")
GREY = HexColor("#6f6a62")
NIGHT = HexColor("#10141c")
PALE = HexColor("#efe8d8")

# ---------------------------------------------------------------- página
TW, TH = 160 * mm, 230 * mm            # formato final (refile)
B = 3 * mm if BLEED else 0             # sangria
PW, PH = TW + 2 * B, TH + 2 * B
M_IN, M_OUT, M_TOP, M_BOT = 22 * mm, 17 * mm, 22 * mm, 26 * mm
FW = TW - M_IN - M_OUT
FH = TH - M_TOP - M_BOT

BODY_SIZE, LEAD = 11.3, 15.2
DROP_DY = 0.0
hy = dict(hyphenationLang="pt_BR", embeddedHyphenation=1, uriWasteReduce=0.3)
ST = {
    "body": ParagraphStyle("body", fontName="Gar", fontSize=BODY_SIZE, leading=LEAD,
                           alignment=TA_JUSTIFY, firstLineIndent=4.6 * mm, textColor=INK,
                           allowWidows=0, allowOrphans=0, **hy),
    "first": ParagraphStyle("first", fontName="Gar", fontSize=BODY_SIZE, leading=LEAD,
                            alignment=TA_JUSTIFY, firstLineIndent=0, textColor=INK,
                            allowWidows=0, allowOrphans=0, **hy),
    "chapnum": ParagraphStyle("chapnum", fontName="Cin", fontSize=9.6, leading=14,
                              alignment=TA_CENTER, textColor=BRONZE),
    "chaptitle": ParagraphStyle("chaptitle", fontName="Gar-I", fontSize=24, leading=29,
                                alignment=TA_CENTER, textColor=INK),
    "center": ParagraphStyle("center", fontName="Gar", fontSize=11, leading=15,
                             alignment=TA_CENTER, textColor=INK),
    "small": ParagraphStyle("small", fontName="Gar", fontSize=8.6, leading=12,
                            alignment=TA_LEFT, textColor=GREY),
    "toc": ParagraphStyle("toc", fontName="Gar", fontSize=10.6, leading=14.6, textColor=INK),
}

NUM_EXT = ["", "Um", "Dois", "Três", "Quatro", "Cinco", "Seis", "Sete", "Oito", "Nove", "Dez",
           "Onze", "Doze", "Treze", "Catorze", "Quinze", "Dezesseis", "Dezessete", "Dezoito",
           "Dezenove", "Vinte", "Vinte e um", "Vinte e dois", "Vinte e três", "Vinte e quatro",
           "Vinte e cinco", "Vinte e seis", "Vinte e sete", "Vinte e oito", "Vinte e nove", "Trinta"]

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def curly(t):
    """Aspas retas → tipográficas (“ ” e ‘ ’)."""
    t = re.sub(r'(^|[\s(\[—–-])"', r'\1“', t)
    t = t.replace('"', '”')
    t = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", t)
    t = t.replace("'", "’")
    return t

def md_inline(t):
    t = esc(curly(t))
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t

# ---------------------------------------------------------------- vetores
_svg_cache = {}
def svg_drawing(path, width):
    key = (path, width)
    if key not in _svg_cache:
        d = svg2rlg(path)
        s = width / d.width
        d.width, d.height = d.width * s, d.height * s
        d.scale(s, s)
        _svg_cache[key] = d
    return _svg_cache[key]

class SVGFlow(Flowable):
    def __init__(self, path, width, align="center"):
        Flowable.__init__(self)
        self.d = svg_drawing(path, width); self.width = width; self.height = self.d.height
        self.align = align
    def wrap(self, aw, ah):
        self.aw = aw
        return aw, self.height
    def draw(self):
        x = (self.aw - self.width) / 2 if self.align == "center" else 0
        self.d.drawOn(self.canv, x, 0)

class Fleuron(Flowable):
    """Filete – losango – filete, em bronze."""
    def __init__(self, w=26 * mm, h=7 * mm):
        Flowable.__init__(self); self.w, self.h = w, h
    def wrap(self, aw, ah):
        self.aw = aw; return aw, self.h
    def draw(self):
        c = self.canv; cx = self.aw / 2; y = self.h / 2
        c.setStrokeColor(BRONZE); c.setFillColor(BRONZE); c.setLineWidth(0.5)
        c.line(cx - self.w / 2, y, cx - 3.2 * mm, y); c.line(cx + 3.2 * mm, y, cx + self.w / 2, y)
        d = 1.7 * mm
        p = c.beginPath(); p.moveTo(cx, y + d); p.lineTo(cx + d, y); p.lineTo(cx, y - d); p.lineTo(cx - d, y); p.close()
        c.drawPath(p, fill=1, stroke=0)

class SceneBreak(Flowable):
    """Três losangos pequenos — quebra de cena."""
    def __init__(self):
        Flowable.__init__(self); self.keepWithNext = True
    def wrap(self, aw, ah):
        self.aw = aw; return aw, LEAD * 1.9
    def draw(self):
        c = self.canv; c.setFillColor(BRONZE); y = LEAD * 0.95
        for dx, d in ((-5.2 * mm, 0.95 * mm), (0, 1.35 * mm), (5.2 * mm, 0.95 * mm)):
            x = self.aw / 2 + dx
            p = c.beginPath(); p.moveTo(x, y + d); p.lineTo(x + d, y); p.lineTo(x, y - d); p.lineTo(x - d, y); p.close()
            c.drawPath(p, fill=1, stroke=0)

class DropCap(Flowable):
    """Capitular de duas linhas em Cinzel bronze (calibrada para o ParagraphAndImage)."""
    LINES = 2
    FIRST_BASE = 8.9           # base da 1ª linha medida a partir do topo da caixa da capitular
    def __init__(self, letter):
        Flowable.__init__(self); self.letter = letter
        cap_h = (self.LINES - 1) * LEAD + BODY_SIZE * 0.66
        self.size = cap_h / 0.70
        self.width = pdfmetrics.stringWidth(letter, "Cin", self.size)
        self.height = self.LINES * LEAD - 0.5
    def wrap(self, aw, ah):
        return self.width, self.height
    def draw(self):
        c = self.canv; c.setFillColor(BRONZE); c.setFont("Cin", self.size)
        base = self.height - (self.FIRST_BASE + (self.LINES - 1) * LEAD) + DROP_DY
        c.drawString(0, base, self.letter)

class Marker(Flowable):
    """Marcador invisível: registra eventos (início de capítulo, página especial)."""
    def __init__(self, kind, value=None):
        Flowable.__init__(self); self.kind, self.value = kind, value; self.width = self.height = 0
    def wrap(self, aw, ah): return 0, 0
    def draw(self):
        doc = self.canv._doctemplate
        if self.kind == "chapter":
            doc.cur_chapter = self.value
            doc.page_flags.add("opening")
            doc.chapter_pages.append((self.value, doc.page))
        elif self.kind == "nofolio":
            doc.page_flags.add("nofolio")
        elif self.kind == "nohead":
            doc.page_flags.add("nohead")

class ToParity(Flowable):
    """Garante que o próximo conteúdo comece em página ímpar (odd=True) ou par.
    Na página errada, ocupa a página inteira (fica em branco) e o conteúdo segue na seguinte."""
    def __init__(self, odd=True):
        Flowable.__init__(self); self.odd = odd; self.width = 0
    def wrap(self, aw, ah):
        page = self.canv._doctemplate.page if hasattr(self, "canv") else _DOC.page
        ok = (page % 2 == 1) == self.odd
        self.height = 0 if ok else ah + 1
        return 0, self.height
    def split(self, aw, ah):
        return [] if self.height else [self]
    def draw(self):
        if self.height == 0:
            return

class PlateMarker(Flowable):
    """Pede ao modelo de página 'prancha' a imagem desta página."""
    def __init__(self, image, caption):
        Flowable.__init__(self); self.image, self.caption = image, caption; self.width = self.height = 0
    def wrap(self, aw, ah): return 0, 0
    def drawOn(self, canvas, x, y, _sW=0):
        doc = canvas._doctemplate
        doc.page_flags.update({"nohead", "nofolio"})
        draw_plate(canvas, self.image, self.caption)
    def draw(self):
        pass

def draw_plate(c, image, caption):
    c.saveState()
    c.setFillColor(NIGHT); c.rect(0, 0, PW, PH, fill=1, stroke=0)
    ir = ImageReader(image); iw, ih = ir.getSize()
    w = PW; h = w * ih / iw
    if h > PH * 0.86:
        h = PH * 0.86; w = h * iw / ih
    x = (PW - w) / 2; y = (PH - h) / 2 + 8 * mm
    c.drawImage(ir, x, y, w, h)
    c.setFillColor(HexColor("#c9a46a")); c.setFont("GarSC", 10.5)
    tw = pdfmetrics.stringWidth(caption, "GarSC", 10.5) + 1.2 * (len(caption) - 1)
    to = c.beginText(); to.setFont("GarSC", 10.5); to.setCharSpace(1.2)
    to.setTextOrigin((PW - tw) / 2, y - 11 * mm); to.textOut(caption); c.drawText(to)
    c.restoreState()

# ---------------------------------------------------------------- documento
_DOC = None
class Book(BaseDocTemplate):
    def __init__(self, fn, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=(PW, PH), leftMargin=0, rightMargin=0,
                                 topMargin=0, bottomMargin=0, title=f"{TITLE} — Volume 1: {SUBTITLE}",
                                 author=AUTHOR, subject="Romance de fantasia épica adulta",
                                 creator="Composição própria (reportlab) — EB Garamond e Cinzel", **kw)
        self.body_frame = Frame(B + M_IN, B + M_BOT, FW, FH, id="body", leftPadding=0, rightPadding=0,
                           topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="body", frames=[self.body_frame], onPage=self._begin,
                                            onPageEnd=self._end)])
        self.cur_chapter = ""; self.page_flags = set(); self.chapter_pages = []
        self.has_content = False
    # margens espelhadas: ímpar (recto) tem a margem interna à esquerda
    def _begin(self, canv, doc):
        canv._doctemplate = self
        if BLEED:   # caixas PDF para a gráfica: refile (TrimBox) e sangria (BleedBox)
            canv.setTrimBox((B, B, B + TW, B + TH))
            canv.setBleedBox((0, 0, PW, PH))
        odd = self.page % 2 == 1
        self.body_frame._x1 = B + (M_IN if odd else M_OUT)
        self.body_frame._geom()
        self.page_flags = set(); self.has_content = False
    def afterFlowable(self, f):
        if not isinstance(f, (Marker, ToParity)):
            self.has_content = True
    def _end(self, canv, doc):
        if not self.has_content and not self.page_flags:
            return   # página em branco
        odd = self.page % 2 == 1
        canv.saveState()
        if "nohead" not in self.page_flags and "opening" not in self.page_flags:
            y = B + TH - M_TOP + 9 * mm
            x_text_l = B + (M_IN if odd else M_OUT); x_text_r = x_text_l + FW
            if odd:
                txt, font, size, cs = self.cur_chapter, "Gar-I", 9.2, 0.15
            else:
                txt, font, size, cs = TITLE, "GarSC", 9.2, 1.4
            w = pdfmetrics.stringWidth(txt, font, size) + cs * (len(txt) - 1)
            t = canv.beginText(); t.setFont(font, size); t.setCharSpace(cs); t.setFillColor(GREY)
            t.setTextOrigin((x_text_l + x_text_r) / 2 - w / 2, y); t.textOut(txt); canv.drawText(t)
        if "nofolio" not in self.page_flags:
            num = str(self.page)
            x_text_l = B + (M_IN if odd else M_OUT)
            yf = B + M_BOT - 13 * mm
            canv.setFont("Gar", 9.6); canv.setFillColor(GREY)
            cx = x_text_l + FW / 2
            canv.drawCentredString(cx, yf, num)
            canv.setFillColor(BRONZE)
            for side in (-1, 1):
                xx = cx + side * (pdfmetrics.stringWidth(num, "Gar", 9.6) / 2 + 3.2 * mm); yy = yf + 2.3
                d = 0.9 * mm
                p = canv.beginPath(); p.moveTo(xx, yy + d); p.lineTo(xx + d, yy); p.lineTo(xx, yy - d); p.lineTo(xx - d, yy); p.close()
                canv.drawPath(p, fill=1, stroke=0)
        canv.restoreState()

def crop_marks(c):
    c.saveState(); c.setStrokeColor(HexColor("#000000")); c.setLineWidth(0.25)
    L = 2.5 * mm
    for (x, y) in ((B, B), (B + TW, B), (B, B + TH), (B + TW, B + TH)):
        dx = -1 if x == B else 1; dy = -1 if y == B else 1
        c.line(x + dx * 0.8 * mm, y, x + dx * (0.8 * mm + L), y)
        c.line(x, y + dy * 0.8 * mm, x, y + dy * (0.8 * mm + L))
    c.restoreState()

# ---------------------------------------------------------------- capítulos
def parse_chapter(path):
    text = open(path, encoding="utf-8").read().strip("\n")
    lines = text.split("\n")
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:])
    m = re.match(r"(Cap[íi]tulo\s+(\d+)|Ep[íi]logo)\s*—\s*(.+)", title)
    if m.group(2):
        n = int(m.group(2)); label = f"Capítulo {NUM_EXT[n].lower()}"; name = m.group(3)
    else:
        n = 0; label = "Epílogo"; name = m.group(3)
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
    return n, label, name, blocks

def opening_paragraph(text):
    """Capitular + primeiras palavras em versalete."""
    t = text.replace("\n", " ")
    if t.startswith("— "):
        rest = t[2:]
        words = rest.split(" ")
        k = 3 if len(words) > 4 else 1
        head, tail = " ".join(words[:k]), " ".join(words[k:])
        return Paragraph(f"— <font name='GarSC'>{md_inline(head)}</font> {md_inline(tail)}", ST["first"])
    if len(t) < 95:
        words = t.split(" ")
        k = 3 if len(words) > 4 else 1
        return Paragraph(f"<font name='GarSC'>{md_inline(' '.join(words[:k]))}</font> {md_inline(' '.join(words[k:]))}", ST["first"])
    m = re.match(r"^([\"“«]?)([A-Za-zÀ-ÿ])(\S*)\s(.*)$", t)
    letter, rest_word, tail = m.group(2), m.group(3), m.group(4)
    words = tail.split(" ")
    k = 2 if len(words) > 3 else 1
    head = rest_word + " " + " ".join(words[:k])
    tail = " ".join(words[k:])
    p = Paragraph(f"<font name='GarSC'>{md_inline(head.strip())}</font> {md_inline(tail)}", ST["first"])
    return ParagraphAndImage(p, DropCap(letter.upper()), xpad=2.6, ypad=0, side="left")

def chapter_story(path, plate=None):
    n, label, name, blocks = parse_chapter(path)
    st = []
    if plate:
        st += [PageBreak(), ToParity(odd=False), PlateMarker(*plate), PageBreak()]
    else:
        st += [PageBreak()]
    st += [ToParity(odd=True), Marker("chapter", name), Spacer(1, 38 * mm),
           SVGFlow(f"{LOGO}/emblema_bronze_chapado.svg", 15 * mm), Spacer(1, 7 * mm),
           Paragraph(label.upper(), ParagraphStyle("cn", parent=ST["chapnum"])),
           Spacer(1, 2.5 * mm), Paragraph(esc(name), ST["chaptitle"]), Spacer(1, 3 * mm),
           Fleuron(), Spacer(1, 12 * mm)]
    first = True
    for b in blocks:
        if b == "---":
            st.append(SceneBreak()); first = "scene"; continue
        if b.startswith("*Fim do Volume") or b.startswith("*A saga"):
            st.append(Spacer(1, 4 * mm))
            st.append(Paragraph(md_inline(b), ParagraphStyle("end", parent=ST["center"], fontName="Gar-I",
                                                             textColor=BRONZE)))
            continue
        if first is True:
            st.append(opening_paragraph(b)); first = False
        elif first == "scene":
            st.append(Paragraph(md_inline(b.replace("\n", " ")), ST["first"])); first = False
        else:
            st.append(Paragraph(md_inline(b.replace("\n", " ")), ST["body"]))
    return n, name, st

# ---------------------------------------------------------------- pré-textuais
def tracked(text, font, size, cs, color=INK, align=TA_CENTER, leading=None):
    return Paragraph(f"<font name='{font}' size='{size}'>{esc(text)}</font>",
                     ParagraphStyle("tr", fontName=font, fontSize=size, leading=leading or size * 1.3,
                                    alignment=align, textColor=color, charSpace=cs))

def front_matter(toc_entries):
    st = [Marker("nofolio"), Marker("nohead"), Spacer(1, 70 * mm),
          SVGFlow(f"{LOGO}/logotipo_tinta.svg", 62 * mm)]
    # 2: frontispício (verso)
    st += [PageBreak(), PlateMarker(f"{ART}/vhalessa.jpg", "Vhalessa, na véspera da noite mais longa")]
    # 3: folha de rosto (recto)
    st += [PageBreak(), Marker("nofolio"), Marker("nohead"), Spacer(1, 30 * mm),
           SVGFlow(f"{LOGO}/emblema_bronze_chapado.svg", 34 * mm), Spacer(1, 10 * mm),
           SVGFlow(f"{LOGO}/logotipo_tinta.svg", 92 * mm), Spacer(1, 9 * mm),
           tracked("VOLUME 1", "Cin", 10, 3.2, BRONZE), Spacer(1, 3 * mm),
           Paragraph(SUBTITLE, ParagraphStyle("sub", fontName="Gar-I", fontSize=17, leading=21,
                                              alignment=TA_CENTER, textColor=INK)),
           Spacer(1, 50 * mm), tracked(AUTHOR.upper(), "Cin", 12, 3.0, INK)]
    # 4: créditos (verso)
    cred = [
        f"<i>{TITLE}</i> — Volume 1: <i>{SUBTITLE}</i>",
        f"Copyright © 2026 {AUTHOR}. Todos os direitos reservados.",
        "Nenhuma parte desta obra pode ser reproduzida sem autorização do autor.",
        "",
        "Edição de luxo ilustrada — texto da versão revisada de linguagem (V1-RL).",
        "Esta é uma obra de ficção. Nomes, lugares, deuses e acontecimentos são invenção do autor "
        "ou usados de forma ficcional.",
        "",
        "Composição: EB Garamond (texto) e Cinzel (títulos), ambas sob a SIL Open Font License.",
        "Identidade visual da saga, emblema, capitulares e ornamentos: projeto gráfico desta edição.",
        "Ilustrações: geradas com auxílio de inteligência artificial sob direção de arte desta edição.",
    ]
    st += [PageBreak(), Marker("nofolio"), Marker("nohead"), Spacer(1, 118 * mm)]
    st += [Paragraph(c if c else "&nbsp;", ST["small"]) for c in cred]
    # 5: sumário (recto)
    st += [PageBreak(), ToParity(odd=True), Marker("nohead"), Marker("nofolio"), Spacer(1, 6 * mm),
           tracked("SUMÁRIO", "Cin", 12, 3.4, BRONZE), Spacer(1, 2 * mm), Fleuron(), Spacer(1, 7 * mm)]
    for label, name, page in toc_entries:
        st.append(TocLine(label, name, page))
    return st

class TocLine(Flowable):
    H = 13.1
    def __init__(self, label, name, page):
        Flowable.__init__(self); self.label, self.name, self.page = label, name, str(page)
    def wrap(self, aw, ah):
        self.aw = aw; return aw, self.H
    def draw(self):
        c = self.canv; y = 3
        lab = self.label
        c.setFillColor(BRONZE)
        t = c.beginText(); t.setFont("GarSC", 9.4); t.setCharSpace(0.6); t.setTextOrigin(0, y); t.textOut(lab); c.drawText(t)
        lw = pdfmetrics.stringWidth(lab, "GarSC", 9.4) + 0.6 * (len(lab) - 1)
        x0 = 33 * mm if lw < 31 * mm else lw + 2 * mm
        c.setFillColor(INK); c.setFont("Gar-I", 10.8); c.drawString(x0, y, self.name)
        nw = pdfmetrics.stringWidth(self.name, "Gar-I", 10.8)
        c.setFont("Gar", 10.4); c.drawRightString(self.aw, y, self.page)
        pw = pdfmetrics.stringWidth(self.page, "Gar", 10.4)
        c.setFillColor(HexColor("#b9b2a6")); c.setFont("Gar", 9)
        xs, xe = x0 + nw + 2.2 * mm, self.aw - pw - 2.2 * mm
        x = xe
        while x > xs:
            c.drawCentredString(x, y, "·"); x -= 2.3 * mm

def back_matter():
    colofao = ("Este livro foi composto em EB Garamond, revival de Georg Duffner e Octavio Pardo "
               "das tipografias de Claude Garamont, com títulos em Cinzel, de Natanael Gama, "
               "inspirada nas inscrições romanas. Os sete losangos do emblema são as sete leis da "
               "Transposição.")
    return [PageBreak(), ToParity(odd=True), Marker("nohead"), Marker("nofolio"), Spacer(1, 120 * mm),
            SVGFlow(f"{LOGO}/emblema_bronze_chapado.svg", 12 * mm), Spacer(1, 6 * mm),
            Paragraph(colofao, ParagraphStyle("col", parent=ST["center"], fontName="Gar-I", fontSize=9.6,
                                              leading=13.5, textColor=GREY)),
            # última página em branco (verso), para o miolo fechar em número par
            PageBreak(), Marker("nofolio"), Marker("nohead"), Spacer(1, 1)]

PLATES = {
    3: (f"{ART}/atrio.jpg", "O Átrio de Soleira"),
    5: (f"{ART}/ilan_aurelia.jpg", "Ilan Varek e a Soberania dos Limiares"),
}

def build(toc_entries):
    global _DOC
    doc = Book(OUT)
    _DOC = doc
    story = front_matter(toc_entries)
    files = sorted(glob.glob(os.path.join(CAP_DIR, "[0-9][0-9].md")))
    for f in files:
        n, name, st = chapter_story(f, PLATES.get(int(os.path.basename(f)[:2])))
        story += st
    story += back_matter()
    doc.build(story)
    return doc

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(CAP_DIR, "[0-9][0-9].md")))
    labels = []
    for f in files:
        n, label, name, _ = parse_chapter(f)
        labels.append((label if n else "Epílogo", name))
    # passo 1: paginação provisória
    doc = build([(l, nm, 0) for l, nm in labels])
    pages = [p for _, p in doc.chapter_pages]
    # passo 2: sumário com páginas reais (o sumário ocupa o mesmo número de páginas)
    doc = build([(l, nm, p) for (l, nm), p in zip(labels, pages)])
    pages2 = [p for _, p in doc.chapter_pages]
    assert pages == pages2, "paginação instável entre os passos"
    print("PDF:", OUT, "| páginas:", doc.page, "| capítulos começam em:", pages[:5], "…")
