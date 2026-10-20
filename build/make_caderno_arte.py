#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caderno de arte ilustrado de *Leis para Matar Deuses — Vol. 1* (sem spoilers).

A4 horizontal, composto em HTML/CSS + SVG e impresso pelo Chromium headless.
Saída: exportacoes/Caderno_de_Arte_Leis_para_Matar_Deuses_Vol1.pdf (+ prévias PNG).
"""
import os, subprocess

ROOT = "/home/user/LTKG"
B = f"{ROOT}/build"
OUT = f"{ROOT}/exportacoes/Caderno_de_Arte_Leis_para_Matar_Deuses_Vol1.pdf"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
LOGO = f"{ROOT}/exportacoes/grafico/logo"
ART = f"{B}/arte"
F = f"file://{B}/fonts"

def svg(path, cls=""):
    s = open(path, encoding="utf-8").read()
    return s.replace("<svg ", f'<svg class="{cls}" preserveAspectRatio="xMidYMid meet" ', 1)

BR = "#c79a55"
def frame_diamond(inner):
    return (f'<svg viewBox="0 0 120 120" class="sig"><polygon points="60,4 116,60 60,116 4,60" fill="none" '
            f'stroke="{BR}" stroke-width="2.2"/><polygon points="60,13 107,60 60,107 13,60" fill="none" '
            f'stroke="{BR}" stroke-width="0.8" opacity=".6"/>{inner}</svg>')
def frame_circle(inner):
    return (f'<svg viewBox="0 0 120 120" class="sig"><circle cx="60" cy="60" r="54" fill="none" stroke="{BR}" '
            f'stroke-width="2.2"/><circle cx="60" cy="60" r="47" fill="none" stroke="{BR}" stroke-width="0.8" '
            f'opacity=".6"/>{inner}</svg>')
S = f'fill="none" stroke="{BR}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"'
FL = f'fill="{BR}"'

LEIS = [
    ("Conservação", "Nada se cria de graça: nem matéria, nem energia, nem carga, nem impulso.",
     f'<circle cx="47" cy="60" r="15" {S}/><circle cx="73" cy="60" r="15" {S}/>'),
    ("Vínculo", "Sem rota ou acoplamento válido, não há transferência.",
     f'<circle cx="38" cy="60" r="6" {FL}/><circle cx="82" cy="60" r="6" {FL}/><path d="M44 60 H76" {S}/>'),
    ("Compatibilidade", "Fonte, destino e meio precisam suportar o que passa por eles.",
     f'<path d="M40 74 L60 40 L80 74 Z" {S}/><path d="M51 68 L60 53 L69 68 Z" {FL}/>'),
    ("Vazão", "Todo circuito tem um limite de fluxo por tempo.",
     f'<path d="M42 38 H78 L62 58 V62 L78 82 H42 L58 62 V58 Z" {S}/><circle cx="60" cy="74" r="3.5" {FL}/>'),
    ("Dissipação", "Há perdas e desgaste; o que se dispersa não volta sem custo.",
     f'<circle cx="44" cy="60" r="6" {FL}/><path d="M56 48 Q64 60 56 72" {S}/><path d="M66 42 Q77 60 66 78" {S} opacity=".65"/><path d="M76 37 Q90 60 76 83" {S} opacity=".35"/>'),
    ("Capacidade", "Âncoras, corpos, equipamentos e mentes têm limites.",
     f'<path d="M42 40 V74 Q42 82 50 82 H70 Q78 82 78 74 V40" {S}/><path d="M42 58 H78" {S}/><path d="M36 40 H84" {S}/>'),
    ("Retorno", "Toda tensão que não é conduzida volta — como falha ou dano.",
     f'<path d="M76 46 A20 20 0 1 0 80 66" {S}/><path d="M80 52 L77 66 L66 58" {S}/>'),
]
PRINCIPIOS = [
    ("Pulso", "movimento e impulso",
     f'<path d="M36 60 H78" {S}/><path d="M68 48 L82 60 L68 72" {S}/><path d="M38 48 H52 M38 72 H52" {S} opacity=".5"/>'),
    ("Brasa", "energia térmica — calor e frio",
     f'<path d="M60 34 C72 50 76 58 72 70 C69 80 51 80 48 70 C45 60 52 54 56 46 C58 54 62 56 64 52 C64 46 62 40 60 34 Z" {S}/>'),
    ("Trama", "ligações, tensões e estabilidade",
     f'<path d="M40 44 L80 76 M40 76 L80 44 M40 60 H80 M60 38 V82" {S}/>'),
    ("Clarão", "luz e radiação luminosa",
     f'<circle cx="60" cy="60" r="9" {FL}/>' + "".join(
         f'<path d="M{60+16*c:.1f} {60+16*s:.1f} L{60+28*c:.1f} {60+28*s:.1f}" {S}/>'
         for c, s in [(1, 0), (0.707, 0.707), (0, 1), (-0.707, 0.707), (-1, 0), (-0.707, -0.707), (0, -1), (0.707, -0.707)])),
    ("Eco", "vibração, som e ressonância",
     f'<circle cx="42" cy="60" r="5" {FL}/><path d="M54 48 Q60 60 54 72" {S}/><path d="M64 40 Q74 60 64 80" {S}/><path d="M74 34 Q88 60 74 86" {S}/>'),
    ("Carga", "cargas e potenciais elétricos",
     f'<path d="M66 34 L46 64 H60 L52 86 L76 54 H62 Z" {S}/>'),
]

PALETA = [("Noite de Vhalessa", "#10141C"), ("Ardósia", "#2A3342"), ("Geada", "#EFE8D8"),
          ("Bronze polido", "#C79A55"), ("Bronze velho", "#8A6631"), ("Brasa de parede", "#D9792B"),
          ("Tinta", "#1E1A16")]

CSS = f"""
@font-face{{font-family:EBG;src:url('{F}/EBGaramond-Regular.ttf')}}
@font-face{{font-family:EBG;font-style:italic;src:url('{F}/EBGaramond-Italic.ttf')}}
@font-face{{font-family:EBG;font-weight:600;src:url('{F}/EBGaramond-SemiBold.ttf')}}
@font-face{{font-family:EBGSC;src:url('{F}/EBGaramondSC-Regular.ttf')}}
@font-face{{font-family:Cinzel;src:url('{F}/Cinzel-Regular.ttf')}}
@font-face{{font-family:Cinzel;font-weight:700;src:url('{F}/Cinzel-Bold.ttf')}}
@page{{size:297mm 210mm;margin:0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:EBG;color:#e9e2d2;background:#10141c}}
.pg{{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;
  background:radial-gradient(ellipse at 50% 35%,#1b2231 0%,#10141c 72%)}}
.pg.claro{{background:#f3eee3;color:#1e1a16}}
.kicker{{font-family:Cinzel;font-size:3.1mm;letter-spacing:1.5mm;color:#c79a55;text-transform:uppercase}}
h2{{font-family:EBG;font-style:italic;font-weight:400;font-size:11mm;line-height:1.1;margin:2mm 0 5mm}}
.claro h2{{color:#1e1a16}}
p{{font-size:4.3mm;line-height:6.4mm;margin-bottom:3.2mm;text-align:justify;hyphens:auto}}
.small{{font-size:3.4mm;line-height:5mm;color:#b7ad9b}}
.claro .small{{color:#6f6a62}}
.folio{{position:absolute;bottom:8mm;right:14mm;font-family:Cinzel;font-size:2.6mm;letter-spacing:1mm;color:#8a6631}}
.full{{position:absolute;inset:0;background-size:cover;background-position:center}}
.cap{{position:absolute;left:0;right:0;bottom:0;padding:16mm 18mm 12mm;
  background:linear-gradient(to top,rgba(10,13,19,.94),rgba(10,13,19,.6) 60%,rgba(10,13,19,0))}}
.cap p{{max-width:150mm;color:#efe8d8}}
.sig{{width:26mm;height:26mm;display:block;margin:0 auto 3mm}}
.grid7{{display:grid;grid-template-columns:repeat(4,1fr);gap:8mm 10mm;margin-top:4mm}}
.grid6{{display:grid;grid-template-columns:repeat(3,1fr);gap:9mm 14mm;margin-top:6mm}}
.cell{{text-align:center}}
.cell .n{{font-family:Cinzel;font-size:4mm;letter-spacing:.9mm;color:#d8bb83;margin-bottom:1.5mm}}
.cell .d{{font-size:3.6mm;line-height:5mm;color:#d9d1c1;text-align:center}}
.sw{{display:flex;gap:5mm;margin-top:6mm}}
.sw div{{flex:1}}
.sw .c{{height:46mm;border-radius:1mm;box-shadow:0 0 0 .3mm rgba(255,255,255,.12) inset}}
.sw .l{{font-family:EBGSC;font-size:3.6mm;margin-top:2mm;color:#e9e2d2}}
.sw .h{{font-size:3.1mm;color:#9d9483}}
.e{{width:100%;height:100%;display:block}}
"""

def page(inner, cls="", folio=None):
    f = f'<div class="folio">{folio}</div>' if folio else ""
    return f'<section class="pg {cls}">{inner}{f}</section>'

pages = []
# 1 — capa do caderno
pages.append(page(f"""
<div style="position:absolute;left:0;right:0;top:22mm;height:118mm;display:flex;justify-content:center">
  <div style="width:150mm;height:118mm">{svg(f'{LOGO}/logo_vertical_bronze.svg','e')}</div></div>
<div style="position:absolute;left:0;right:0;top:150mm;text-align:center">
  <div class="kicker" style="letter-spacing:2.4mm">Caderno de arte · Volume 1</div>
  <div style="font-style:italic;font-size:6.5mm;margin-top:3mm;color:#efe8d8">O Deus que Caiu do Céu</div>
  <div style="font-family:Cinzel;font-size:3.4mm;letter-spacing:1.6mm;margin-top:7mm;color:#b7ad9b">WERIK MARTINS</div>
</div>"""))
# 2 — apresentação
pages.append(page(f"""
<div style="position:absolute;left:22mm;top:24mm;width:120mm">
  <div class="kicker">Sobre este caderno</div>
  <h2>Inverno e bronze</h2>
  <p>Este caderno reúne a identidade visual e as primeiras imagens do mundo de <i>Leis para Matar Deuses</i>.
  Nada aqui adianta a história: as pranchas mostram o que o leitor encontra logo nas primeiras páginas — a cidade,
  o Átrio, os dois protagonistas — e os símbolos que organizam a magia de Aresta.</p>
  <p>O conceito visual nasce de duas matérias. O inverno é o azul-ardósia das noites de Vhalessa, a geada por
  dentro das janelas, o rio congelado onde a cidade se reúne. O bronze é tudo o que as pessoas construíram para
  não morrer de frio: lentes, placas, batentes, chaves, manoplas. Entre os dois existe uma luz só, dourada e morna,
  que no começo do livro ainda brilha no alto de uma torre.</p>
  <p class="small">A paleta, as fontes, o emblema e os ornamentos deste caderno são os mesmos do miolo, da capa e do
  EPUB da edição de luxo.</p>
</div>
<div style="position:absolute;right:20mm;top:30mm;width:115mm;height:150mm;background:url('{ART}/capa_arte.jpg') center/cover;
  box-shadow:0 2mm 8mm rgba(0,0,0,.6)"></div>""", folio="2"))
# 3 — emblema
pages.append(page(f"""
<div style="position:absolute;left:18mm;top:20mm;width:118mm;height:170mm;display:flex;align-items:center">
  <div style="width:118mm;height:118mm">{svg(f'{LOGO}/emblema_bronze.svg','e')}</div></div>
<div style="position:absolute;left:150mm;top:26mm;width:128mm">
  <div class="kicker">Identidade da saga</div>
  <h2>O emblema</h2>
  <p><b style="color:#d8bb83;font-weight:600">Sete losangos.</b> As sete leis da Transposição — Conservação, Vínculo,
  Compatibilidade, Vazão, Dissipação, Capacidade e Retorno. Nenhuma técnica do livro as suspende.</p>
  <p><b style="color:#d8bb83;font-weight:600">O sol de inverno.</b> As Coroas: os deuses que governam, aquecem e
  sustentam cidades inteiras.</p>
  <p><b style="color:#d8bb83;font-weight:600">A espada-balança.</b> A guarda da espada é o travessão de uma balança,
  e um dos pratos pesa mais. É a Arte do Carrasco — e uma conta que precisa fechar.</p>
  <p><b style="color:#d8bb83;font-weight:600">A rachadura.</b> A primeira imagem do livro: a noite em que tudo
  começa.</p>
  <p class="small">Desenhado em vetor, sem dependência de fontes. Versões: bronze metálico, bronze chapado
  (impressão a uma cor ou hot stamping), tinta sobre claro e geada sobre escuro.</p>
</div>""", folio="3"))
# 4 — assinaturas
pages.append(page(f"""
<div style="position:absolute;left:20mm;top:18mm" class="kicker">Assinaturas</div>
<div style="position:absolute;left:20mm;top:30mm;width:120mm;height:100mm">{svg(f'{LOGO}/logo_vertical_bronze.svg','e')}</div>
<div style="position:absolute;left:152mm;top:36mm;width:125mm;height:40mm">{svg(f'{LOGO}/logo_horizontal_bronze.svg','e')}</div>
<div style="position:absolute;left:152mm;top:86mm;width:125mm;height:62mm;background:#f3eee3;border-radius:1mm;padding:9mm 10mm">
  <div style="width:100%;height:100%">{svg(f'{LOGO}/logo_horizontal_tinta.svg','e')}</div></div>
<div style="position:absolute;left:20mm;top:146mm;width:120mm">
  <p class="small">Vertical (capa, folha de rosto, lombada larga), horizontal (cartazes, banners, assinatura de
  e-mail) e logotipo isolado (lombada, cabeçalhos). Letras em Cinzel, inspirada nas inscrições romanas; o
  “LEIS PARA” entre filetes e losangos repete a geometria do emblema.</p></div>""", folio="4"))
# 5 — paleta e tipografia
sw = "".join(f'<div><div class="c" style="background:{h}"></div><div class="l">{n}</div><div class="h">{h}</div></div>'
             for n, h in PALETA)
pages.append(page(f"""
<div style="position:absolute;left:20mm;right:20mm;top:20mm">
  <div class="kicker">Paleta e tipografia</div>
  <h2>As cores de uma cidade no frio</h2>
  <div class="sw">{sw}</div>
  <div style="display:flex;gap:14mm;margin-top:12mm">
    <div style="flex:1"><div style="font-family:Cinzel;font-size:12mm;color:#d8bb83;line-height:1">Cinzel</div>
      <p class="small" style="margin-top:2mm">Títulos, logotipo, números de capítulo. Maiúsculas de inscrição,
      espaçadas.</p></div>
    <div style="flex:1"><div style="font-family:EBG;font-size:12mm;line-height:1">EB Garamond <i>itálico</i></div>
      <p class="small" style="margin-top:2mm">Texto corrido, títulos de capítulo em itálico, legendas.</p></div>
    <div style="flex:1"><div style="font-family:EBGSC;font-size:12mm;line-height:1;letter-spacing:.6mm">Versalete</div>
      <p class="small" style="margin-top:2mm">Primeiras palavras dos capítulos, cabeçalhos, sumário.</p></div>
  </div>
</div>""", folio="5"))
# 6 — Vhalessa
pages.append(page(f"""
<div class="full" style="background-image:url('{ART}/vhalessa.jpg')"></div>
<div class="cap"><div class="kicker">Lugares</div><h2 style="color:#efe8d8">Vhalessa</h2>
<p>Seiscentas mil pessoas nas duas margens de um rio que congela. No inverno, quem aquece as casas é o deus:
milhares de brasas de parede, placas de bronze embutidas nos tijolos, acesas de novembro a março. No rio, a Feira
do Gelo. Na Fornalha Velha, o bairro que a cidade combinou de não ver.</p></div>""", folio="6"))
# 7 — Torre (capa)
pages.append(page(f"""
<div style="position:absolute;left:22mm;top:16mm;width:122mm;height:178mm;background:url('{ART}/capa_arte.jpg') center/cover;
 box-shadow:0 2mm 8mm rgba(0,0,0,.6)"></div>
<div style="position:absolute;left:160mm;top:40mm;width:116mm">
  <div class="kicker">Lugares</div><h2>A Torre do Meio-Dia</h2>
  <p>Duzentos e vinte metros de pedra cinzenta e bronze. Lá em cima, como uma flor de metal na ponta de uma haste,
  fica o Sol: uma lente enorme de bronze e vidro que, o inverno inteiro, devolve à cidade o calor guardado durante
  o verão.</p>
  <p>Na noite mais longa do ano, Vhalessa inteira se junta na praça, nos telhados e no gelo do rio para ver o
  Acendimento.</p>
  <p class="small">Arte da capa da edição de luxo.</p>
</div>""", folio="7"))
# 8 — Átrio
pages.append(page(f"""
<div class="full" style="background-image:url('{ART}/atrio.jpg')"></div>
<div class="cap"><div class="kicker">Lugares</div><h2 style="color:#efe8d8">O Átrio de Soleira</h2>
<p>Um círculo de pedra branca com quase quinhentos metros de diâmetro, sob uma cúpula de bronze e vidro. Nas três
galerias, trezentas e quarenta e uma portas levam a outros cantos do mundo. Cada uma tem placa, tarifa e fila — e
uma dona que conhece todas como quem conhece o próprio corpo de olhos fechados.</p></div>""", folio="8"))
# 9 — Ilan e Aurelia
pages.append(page(f"""
<div style="position:absolute;left:18mm;top:14mm;width:146mm;height:182mm;background:url('{ART}/ilan_aurelia.jpg') center/cover;
 box-shadow:0 2mm 8mm rgba(0,0,0,.6)"></div>
<div style="position:absolute;left:176mm;top:24mm;width:104mm">
  <div class="kicker">Personagens</div><h2>Ilan Varek</h2>
  <p>Trinta e quatro anos, estatura média, ombros que não chamam atenção e uma quietude que chama. Desliga
  reservatórios por contrato, conta segundos no meio de uma briga e junta dinheiro para um terreno onde nunca
  neva. Seco quando é grave; irônico quando dá.</p>
  <h2 style="margin-top:7mm">Aurelia</h2>
  <p>Soberana dos Limiares, deusa original das passagens. Elegante, precisa, com uma chave de bronze atravessando o
  coque e olhos cor de bronze velho. Governa rotas, tarifas e portas — e responde por cada uma delas.</p>
</div>""", folio="9"))
# 10 — a manopla
pages.append(page(f"""
<div style="position:absolute;left:22mm;top:18mm;width:118mm;height:138mm;background:url('{ART}/detalhe_manopla.jpg') center/cover;
 box-shadow:0 2mm 8mm rgba(0,0,0,.6)"></div>
<svg style="position:absolute;left:0;top:0;width:297mm;height:210mm" viewBox="0 0 297 210">
  <g stroke="#c79a55" stroke-width=".35" fill="none"><path d="M84 66 L150 52"/><path d="M98 120 L150 112"/><path d="M60 40 L150 30"/></g>
  <g fill="#c79a55"><circle cx="84" cy="66" r="1.2"/><circle cx="98" cy="120" r="1.2"/><circle cx="60" cy="40" r="1.2"/></g>
</svg>
<div style="position:absolute;left:154mm;top:20mm;width:124mm">
  <div class="kicker">Objetos</div><h2>A manopla</h2>
  <p style="margin-top:2mm"><b style="color:#d8bb83;font-weight:600">Couro e aço,</b> até o meio do antebraço. É por
  ela que Ilan toca o que os outros só sentem: fios de tensão, âncoras, elos.</p>
  <p><b style="color:#d8bb83;font-weight:600">Três células de cerâmica,</b> encaixadas no dorso como balas grossas.
  Guardam carga e calor por pouco tempo. Cada uma tem limite — e, quando o limite passa, a cerâmica racha e alguém
  paga a conta.</p>
  <p><b style="color:#d8bb83;font-weight:600">A mão que dói.</b> Nada aqui é infinito: o que a manopla recebe
  precisa ir para algum lugar.</p>
  <p class="small">Detalhe da prancha dos protagonistas.</p>
</div>""", folio="10"))
# 11 — as sete leis
cells = "".join(f'<div class="cell">{frame_diamond(g)}<div class="n">{n.upper()}</div><div class="d">{d}</div></div>'
                for n, d, g in LEIS)
pages.append(page(f"""
<div style="position:absolute;left:20mm;right:20mm;top:14mm">
  <div class="kicker">Sinais</div><h2 style="margin-bottom:2mm">As sete leis da Transposição</h2>
  <div class="grid7">{cells}<div class="cell" style="display:flex;align-items:center"><p class="small" style="text-align:left">
  A magia de Aresta não cria nada: controla transferências do que já existe. Toda operação precisa de fonte, âncora,
  elo, destino, controle — e de um caminho para o retorno.</p></div></div>
</div>""", folio="11"))
# 12 — os seis princípios
cells = "".join(f'<div class="cell">{frame_circle(g)}<div class="n">{n.upper()}</div><div class="d">{d}</div></div>'
                for n, d, g in PRINCIPIOS)
pages.append(page(f"""
<div style="position:absolute;left:30mm;right:30mm;top:16mm">
  <div class="kicker">Sinais</div><h2 style="margin-bottom:2mm">Os seis princípios</h2>
  <div class="grid6">{cells}</div>
  <p class="small" style="margin-top:8mm;text-align:center">Fogo, gelo, raio, luz e som não são escolas separadas:
  são usos combinados destes seis princípios, todos sujeitos às mesmas leis.</p>
</div>""", folio="12"))
# 13 — o livro: abertura e miolo
pages.append(page(f"""
<div style="position:absolute;left:18mm;top:16mm" class="kicker">O livro</div>
<div style="position:absolute;left:18mm;top:28mm;display:flex;gap:6mm">
  <img src="{ART}/miolo-007.png" style="height:150mm;box-shadow:0 2mm 7mm rgba(0,0,0,.6)">
  <img src="{ART}/miolo-008.png" style="height:150mm;box-shadow:0 2mm 7mm rgba(0,0,0,.6)">
  <img src="{ART}/miolo-009.png" style="height:150mm;box-shadow:0 2mm 7mm rgba(0,0,0,.6)">
</div>
<div style="position:absolute;left:18mm;right:18mm;top:184mm"><p class="small">Miolo em 16 × 23 cm: EB Garamond
11,3/15,2, margens espelhadas, capitulares em Cinzel bronze, primeiras palavras em versalete, quebras de cena com
três losangos, capítulos sempre em página ímpar, pranchas sobre fundo noturno.</p></div>""", folio="13"))
# 14 — capa completa
pages.append(page(f"""
<div style="position:absolute;left:18mm;top:16mm" class="kicker">A capa</div>
<img src="{ROOT}/exportacoes/capa/capa_completa_previa.png" style="position:absolute;left:18mm;top:28mm;width:261mm;
 box-shadow:0 2mm 7mm rgba(0,0,0,.6)">
<div style="position:absolute;left:18mm;right:18mm;top:184mm"><p class="small">Contracapa, lombada e frente, com
3 mm de sangria. A largura da lombada é calculada a partir do número de páginas e da gramatura do papel.</p></div>""",
                  folio="14"))
# 15 — créditos
pages.append(page(f"""
<div style="position:absolute;left:0;right:0;top:56mm;display:flex;justify-content:center">
  <div style="width:26mm;height:26mm">{svg(f'{LOGO}/emblema_bronze.svg','e')}</div></div>
<div style="position:absolute;left:60mm;right:60mm;top:92mm;text-align:center">
  <p style="text-align:center"><i>Leis para Matar Deuses</i> · Volume 1 · <i>O Deus que Caiu do Céu</i><br>
  © 2026 Werik Martins. Todos os direitos reservados.</p>
  <p class="small" style="text-align:center">Identidade visual, emblema, ornamentos, diagramação e direção de arte desta
  edição. Ilustrações geradas com auxílio de inteligência artificial a partir de descrições do próprio texto, sem
  revelar acontecimentos da história. Tipografia: Cinzel e EB Garamond (SIL Open Font License).</p>
</div>""", folio="15"))

html = (f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
        + "".join(pages) + "</body></html>")
tmp = f"{B}/_caderno.html"
open(tmp, "w", encoding="utf-8").write(html)
subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
                "file://" + tmp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("caderno:", OUT)
