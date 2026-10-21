#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bíblia Visual da Saga (sem spoilers): A4 paisagem, texto selecionável + pranchas.
Saída: exportacoes/identidade_aresta/Biblia_Visual_Leis_para_Matar_Deuses.pdf"""
import json, os, subprocess, collections
ROOT = "/home/user/LTKG"
BA = f"{ROOT}/exportacoes/banco_de_arte"
PR = f"{ROOT}/exportacoes/identidade_aresta/pranchas"
OUT = f"{ROOT}/exportacoes/identidade_aresta/Biblia_Visual_Leis_para_Matar_Deuses.pdf"
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
F = f"file://{ROOT}/build/fonts"
CACHE = f"{ROOT}/build/_jpg"
os.makedirs(CACHE, exist_ok=True)
def jpg(path, maxw=1500, q=84):
    from PIL import Image
    dst = f"{CACHE}/" + path.replace("/", "_").rsplit(".", 1)[0] + f"_{maxw}.jpg"
    if not os.path.exists(dst):
        im = Image.open(path)
        if im.mode in ("RGBA", "LA"):
            return "file://" + path          # transparências ficam em PNG
        im = im.convert("RGB")
        if im.width > maxw: im = im.resize((maxw, round(maxw * im.height / im.width)), Image.LANCZOS)
        im.save(dst, quality=q)
    return "file://" + dst
A = lambda p: jpg(f"{BA}/{p}")
cat = json.load(open(f"{BA}/catalogo.json", encoding="utf-8"))
por_cat = collections.Counter(x["categoria"] for x in cat)

CSS = f"""
@font-face{{font-family:Cz;src:url('{F}/Cinzel-SemiBold.ttf')}} @font-face{{font-family:CzB;src:url('{F}/Cinzel-Bold.ttf')}}
@font-face{{font-family:G;src:url('{F}/EBGaramond-Regular.ttf')}} @font-face{{font-family:Gi;src:url('{F}/EBGaramond-Italic.ttf')}}
@page{{size:297mm 210mm;margin:0}} *{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0B0A09;color:#E6DCC6;font-family:G}}
.pg{{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;padding:16mm 18mm;
  background:linear-gradient(rgba(10,9,8,.93),rgba(10,9,8,.96)),url({jpg(BA + '/01_identidade/ID-001_logo_principal_vertical.png', 500, 70)}) 0 100%/60mm auto}}
.k{{font-family:Cz;font-size:8.5pt;letter-spacing:1.4mm;color:#C9A15A;text-transform:uppercase}}
h1{{font-family:CzB;font-weight:400;font-size:22pt;letter-spacing:1mm;color:#E2C47E;margin:2mm 0 6mm}}
h2{{font-family:Cz;font-weight:400;font-size:11pt;letter-spacing:.8mm;color:#D9BC7C;margin:4mm 0 2mm;text-transform:uppercase}}
p,li{{font-size:11pt;line-height:1.42;color:#DCD2BC}} ul{{padding-left:5mm}} li{{margin:1mm 0}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:10mm}} .cols3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8mm}}
.q{{font-family:Gi;color:#D7CBB2}} .foot{{position:absolute;left:18mm;right:18mm;bottom:8mm;display:flex;justify-content:space-between;
  font-family:Cz;font-size:7pt;letter-spacing:1mm;color:#8C7A58}}
.img{{background-size:cover;background-position:center;border:.3mm solid #6B5532}}
.chip{{display:flex;align-items:center;gap:3mm;margin:1.6mm 0}} .chip b{{display:block;width:12mm;height:9mm;border:.3mm solid #6B5532}}
.full{{width:297mm;height:210mm;page-break-after:always;background-size:contain;background-repeat:no-repeat;background-position:center;background-color:#090807}}
table{{border-collapse:collapse;width:100%}} td,th{{border-bottom:.2mm solid #3A3125;padding:1.4mm 2mm;font-size:10pt;text-align:left;vertical-align:top}}
th{{font-family:Cz;font-weight:400;font-size:8pt;letter-spacing:.6mm;color:#C9A15A}}
"""
N = [0]
def pg(kicker, title, body):
    N[0] += 1
    return (f'<div class="pg"><div class="k">{kicker}</div><h1>{title}</h1>{body}'
            f'<div class="foot"><span>Leis para Matar Deuses · Bíblia Visual da Saga</span><span>{N[0]:02d}</span></div></div>')
def full(img):
    N[0] += 1
    return f'<div class="full" style="background-image:url({jpg(img, 2400, 86)})"></div>'
def im(p, w, h, extra=""):
    return f'<div class="img" style="width:{w}mm;height:{h}mm;background-image:url({A(p)});{extra}"></div>'

pages = []
# capa
N[0] += 1
pages.append(f'''<div class="pg" style="padding:0;background:#090807">
 <div class="img" style="position:absolute;inset:0;border:0;background-image:url({A('05_mundo/MU-001_cidade_de_limiar.png')});opacity:.55"></div>
 <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(9,8,7,.95) 0%,rgba(9,8,7,.55) 55%,rgba(9,8,7,.2))"></div>
 <img src="{A('01_identidade/ID-007_logo_vertical_transparente.png')}" style="position:absolute;left:26mm;top:22mm;height:120mm">
 <div style="position:absolute;left:120mm;top:70mm"><div class="k">Bíblia Visual da Saga</div>
 <div style="font-family:CzB;font-size:30pt;color:#E2C47E;letter-spacing:1mm;margin:3mm 0">Direção de arte,<br>identidade e mundo</div>
 <p class="q" style="font-size:13pt;max-width:140mm">Uma identidade para acompanhar a saga inteira: reconhecível por um símbolo, por um detalhe de página ou por um retrato.</p>
 <p class="k" style="margin-top:8mm">Werik Martins · Saga Aresta · versão 1 · outubro de 2026</p></div></div>''')
pages.append(pg("00 · Como usar", "O que está neste documento", '''<div class="cols"><div>
<p>Esta bíblia fixa a linguagem visual de <i>Leis para Matar Deuses</i> a partir das referências enviadas pelo autor, que passam a ser a direção aprovada.
Tudo que aparece aqui é proposta de produção até o autor aprovar peça por peça. O status fica no catálogo do banco de arte.</p>
<h2>Hierarquia de autoridade</h2><ul><li>1. Decisões explícitas do autor e o manuscrito canônico mais recente.</li>
<li>2. Bíblias técnicas e visuais aprovadas, incluindo estas referências.</li><li>3. Materiais desenvolvidos e ainda não aprovados (este banco de arte).</li>
<li>4. Novas propostas, sempre marcadas como propostas.</li></ul></div><div>
<h2>Regras de spoiler</h2><ul><li>Nenhuma peça pública revela reviravolta, identidade oculta, morte ou traição.</li>
<li>Ilustração de cena só entra no livro depois do trecho correspondente.</li><li>Qualquer material revelador fica em <i>CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA</i>.</li></ul>
<h2>Arquivos</h2><ul><li><i>exportacoes/banco_de_arte/</i>: artes individuais, catálogo com prompt, modelo, versão e status.</li>
<li><i>exportacoes/identidade_aresta/</i>: pranchas, logotipos e símbolos vetoriais para gráfica.</li><li><i>exportacoes/capa_v2/</i>: capa do Volume I.</li></ul></div></div>'''))
pages.append(pg("01 · Alma visual", "Místico · Marcial · Divino", f'''<div class="cols3">
<div>{im('09_engenharia_arcana/EA-002_fluxograma_arcano.png', 76, 52)}<h2>Místico</h2><p>Estruturas invisíveis com lógica própria. Círculos, eixos e pérolas obedecem às sete leis. Nada de runas aleatórias.</p></div>
<div>{im('09_engenharia_arcana/EA-007_interdicao_carrascos.png', 76, 52)}<h2>Marcial</h2><p>Peso, desgaste e consequência. Armas funcionais, couro, aço riscado, movimento econômico. A magia corta, pesa e cobra.</p></div>
<div>{im('05_mundo/MU-007_interiores_sagrados.png', 76, 52)}<h2>Divino</h2><p>Escala, luz e arquitetura no lugar do brilho genérico. Coroas de raios, portais de anéis, salões que diminuem quem entra.</p></div></div>
<p class="q" style="margin-top:6mm;font-size:12.5pt">Um universo belo, perigoso, antigo e vivo: a grandeza da fantasia épica cinematográfica com a mão de uma ilustração autoral.</p>'''))
PAL = [("#0B0B0C", "Obsidiana / negro mineral", "fundos, capas, páginas de nível 3"), ("#1C1B1A", "Grafite", "painéis, sombras"),
       ("#A8823E", "Ouro antigo", "lettering, filetes, hot stamping"), ("#C9A15A", "Ouro claro", "títulos, ícones"),
       ("#7A1218", "Sangue / vermelho mineral", "estandarte, Carrascos, Brasa"), ("#E6DCC6", "Osso / marfim", "miolo, pérolas"),
       ("#5C6168", "Aresta / prata fria", "arco-limiar, metal"), ("#1E3A5C", "Céu de Limiar / azul profundo", "Pulso, Eco, portais"),
       ("#1F3A32", "Floresta sombria", "Delta, acentos raros")]
pages.append(pg("02 · Cor e tipografia", "Paleta-base e tipos", '<div class="cols"><div>' + "".join(
    f'<div class="chip"><b style="background:{c}"></b><div><span class="k" style="font-size:7.5pt">{n}</span><br><span style="font-size:9.5pt">{c} · {u}</span></div></div>' for c, n, u in PAL)
    + '''</div><div><h2>Tipografia</h2>
<p><span style="font-family:CzB;font-size:20pt;color:#E2C47E">LEIS PARA MATAR DEUSES</span><br><span class="k">Cinzel · títulos, lettering, rótulos em versal espaçada</span></p>
<p style="margin-top:4mm"><span style="font-size:15pt">O contrato tinha onze páginas, e Pelle Dorn fazia questão…</span><br><span class="k">EB Garamond · texto corrido e citações em itálico</span></p>
<h2>Regras</h2><ul><li>Título sempre em versal; “PARA” menor e alinhado pelo topo.</li><li>Rótulos com espaçamento de 0,3 em; nunca em caixa-baixa.</li>
<li>Cada região e personagem pode ter paleta secundária, sempre ancorada no negro e no ouro.</li>
<li>Evitar o clichê de fantasia: excesso de roxo, azul elétrico, partículas e névoa.</li></ul></div></div>'''))
pages.append(pg("03 · Logotipo", "Sistema de marca", f'''<div class="cols"><div style="display:grid;grid-template-columns:1fr 1fr;gap:4mm">
{im('01_identidade/ID-001_logo_principal_vertical.png', 60, 80)}{im('01_identidade/ID-003_logo_horizontal.png', 60, 40)}
{im('01_identidade/ID-004_monograma_LMD.png', 60, 40)}{im('01_identidade/ID-005_selo_de_serie.png', 60, 40)}</div><div>
<h2>Versões</h2><ul><li>Principal vertical, com emblema (ID-001).</li><li>Horizontal (ID-003) para faixas, site e lombada larga.</li>
<li>Compacta: monograma LMD (ID-004) e selo de série (ID-005).</li><li>Lettering transparente (ID-006) e logo transparente (ID-007).</li>
<li>Uma cor e negativo: arquivos vetoriais em <i>identidade_aresta/logo</i>, para hot stamping e gravação.</li></ul>
<h2>Uso</h2><ul><li>Área de proteção: a altura do “L” em volta do conjunto.</li><li>Tamanho mínimo: emblema com 12 mm; lettering com 30 mm de largura.</li>
<li>Fundo preferido: negro mineral ou arte escura. Em papel claro, usar o medalhão (ID-009).</li><li>Não distorcer, não recolorir o ouro, não aplicar sobre rosto ou área complexa.</li></ul></div></div>'''))
pages.append(pg("04 · Emblema", "Anatomia do brasão", f'''<div class="cols"><div>{im('01_identidade/ID-002_emblema_isolado.png', 118, 118)}</div><div>
<ul><li><b>Arco-limiar</b> de prata com filete de ouro: a passagem entre mundos.</li>
<li><b>Lança no eixo</b> com anel e crescentes no topo: a lei que aponta para cima e corta para baixo.</li>
<li><b>Sete pérolas</b> em coluna: as sete leis da Transposição, da Conservação ao Retorno.</li>
<li><b>Balança</b> pendurada no travessão, com o <b>prato esquerdo mais baixo</b>: o desequilíbrio que move a saga.</li>
<li><b>Estandarte carmim</b>: o custo, o sangue, a sentença.</li><li><b>Crescentes</b> nos ombros do arco e <b>raios</b> ao fundo: soberanias e o sol de inverno.</li>
<li><b>Ponta</b> para baixo, abaixo do arco: a lei sempre chega ao chão.</li></ul>
<p class="q" style="margin-top:4mm">Versões: metal sobre negro, transparente, medalhão para papel claro e vetor de uma cor para gráfica.</p></div></div>'''))
pages.append(pg("05 · Sistema de símbolos", "Leis, disciplinas e etapas", f'''{im('02_simbolos/SI-001_sete_leis.png', 261, 60, "background-position:center 40%")}
<div class="cols" style="margin-top:4mm"><div>{im('02_simbolos/SI-002_seis_disciplinas.png', 125, 52, "background-position:center 20%")}
<p style="margin-top:2mm">Disciplinas com cor própria: Pulso azul-gelo, Brasa vermelho, Trama ouro, Clarão branco-ouro, Eco azul-prata, Carga ouro.</p></div>
<div>{im('02_simbolos/SI-003_etapas_da_transposicao.png', 125, 52)}<p style="margin-top:2mm">Gramática comum: eixo vertical, círculo de campo e pérola de energia.
Cada sinal comunica o conceito sem inventar regra nova.</p></div></div>'''))
pages.append(pg("06 · Heráldica", "Facções, casas e objetos", f'''<div class="cols"><div>{im('03_faccoes/FA-001_seis_faccoes.png', 125, 84, "background-position:center 10%")}
<p style="margin-top:2mm">Ordem da Última Sentença · O Carrasco · Coroa dos Limiares · Convergência de Limiar · Cidades Livres · Os Dragões.</p></div>
<div>{im('03_faccoes/FA-002_outras_casas.png', 125, 84)}<p style="margin-top:2mm">Aurelia · Ilan Varek · Arquivistas · Círculo do Vazio Profundo · Senhorios de Aresta.
<i>Casas e regiões das referências que ainda não aparecem no Volume I ficam como propostas até aprovação.</i></p></div></div>
<div class="cols3" style="margin-top:3mm">{im('04_objetos/OB-001_selos_de_cera.png', 80, 34)}{im('04_objetos/OB-002_medalhoes.png', 80, 34)}{im('04_objetos/OB-004_estandartes.png', 80, 34)}</div>'''))
pages.append(pg("07 · Ilustração", "Direção de pintura", f'''<div class="cols"><div>
<ul><li><b>Realismo fantástico editorial:</b> anatomia convincente, materiais físicos ricos, ambientes críveis.</li>
<li><b>Pintura digital cinematográfica:</b> luz dramática, profundidade, pincelada visível em pontos escolhidos.</li>
<li><b>Arte de produção:</b> roupa, arma e cidade com construção funcional.</li>
<li><b>Gravura contemporânea</b> só em páginas especiais: hachura, guilhochê, microtexto.</li>
<li><b>Escala</b> comunica o divino; o divino não é uma pessoa brilhando.</li></ul>
<h2>Modelo de prompt (registrado por arte no catálogo)</h2>
<p class="q" style="font-size:10pt">“Cinematic realistic fantasy digital painting … [assunto, ação, lugar] … Palette mineral black, graphite, aged gold, [acento]. Painterly, atmospheric depth, correct anatomy, natural hands, no text, no watermark.”</p></div>
<div>{im('05_mundo/MU-001_cidade_de_limiar.png', 125, 70)}<div style="height:3mm"></div>{im('09_engenharia_arcana/EA-006_transposicao_portal.png', 125, 52)}</div></div>'''))
FICHA = [("Ilan Varek", "PE-001_ilan_varek_retrato", "Humano, 34. Cabelo castanho-escuro curto, barba de três dias, cicatriz fina no queixo, olhos cinzentos. Casaco negro de gola alta, colete com lente de aferição, manopla esquerda com três células cerâmicas, giz e fio de prata, espada de ferro simples. Balança torta marcada no pulso esquerdo.", "Inteligência e experiência no olhar; economia de movimento; nada de músculos exagerados nem fúria permanente."),
         ("Aurelia", "PE-012_aurelia_dourada_retrato", "Deusa original dos Limiares. Cabelo loiro dourado, longo e ondulado até a cintura; olhos âmbar; diadema de raios de ouro; colar de filigrana com pingente em losango; braceletes de ouro nos dois braços; halo de anéis de portal.", "Beleza divina com personalidade: inteligência, autoridade, ironia, autonomia. O mesmo rosto à mesa e na manifestação."),
         ("Mara Quen", "PE-003_mara_quen_retrato", "Humana, ~32. Cabelo escuro preso, óculos redondos finos, casaco carvão de gola alta, colete bordô, livro-razão.", "Rígida e perspicaz; postura ereta, gestos precisos."),
         ("Nara Voss", "PE-028_nara_voss_ponte_da_cidade", "Humana, 29. Cabelo acobreado numa trança longa e grossa, sardas, óculos de latão na cabeça, colete de couro sem mangas, luvas sem dedos, cinto de ferramentas, botas altas; cicatrizes de queimadura nos antebraços. Na rua, no inverno, casaco longo de couro encerado.", "Prática e teimosa; mãos sempre ocupadas."),
         ("Sevran", "PE-005_sevran_retrato", "Humano, ~45. Cabelo cacheado grisalho, barba cheia grisalha, vestes escuras, cachecol creme, livro antigo.", "Irônico e compassivo; olhar cansado, rugas de riso.")]
pages.append(pg("08 · Personagens", "Fichas de continuidade", '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4mm">' + "".join(
    f'<div>{im("06_personagens/" + f + ".png", 48, 66, "background-position:center 20%")}<h2 style="font-size:9.5pt">{n}</h2><p style="font-size:8.6pt;line-height:1.32">{a}</p>'
    f'<p class="q" style="font-size:8.6pt;line-height:1.32;margin-top:1mm">{b}</p></div>' for n, f, a, b in FICHA) + '</div>'
    '<p style="font-size:9pt;margin-top:3mm;color:#B8A887">Imutáveis: rosto, cabelo, idade aparente, proporções. Substituíveis: figurino de viagem, formal e de combate. '
    'Regra absoluta: a imagem nova representa a mesma pessoa. As fichas seguem as referências do autor e devem ser conferidas por ele antes de virarem canônicas.</p>'))
pages.append(pg("09 · Mundo", "Aresta: regiões e atmosfera", f'''<div class="cols"><div>{im('05_mundo/MU-010_mapa_de_aresta_conceitual.png', 125, 84)}
<p style="margin-top:2mm;font-size:9.5pt">Mapa <b>conceitual</b>, das referências do autor. Distâncias e rotas não são canônicas até a geografia ser consolidada.</p></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:3mm">{im('05_mundo/MU-002_reinos_do_norte.png', 61, 40)}{im('05_mundo/MU-003_delta_e_arquivos.png', 61, 40)}
{im('05_mundo/MU-004_ilhas_prisma.png', 61, 40)}{im('05_mundo/MU-005_terras_dos_dragoes.png', 61, 40)}{im('05_mundo/MU-006_cidades_livres.png', 61, 40)}{im('05_mundo/MU-009_vhalessa_fornalha_velha_noite.png', 61, 40)}</div></div>
<p style="font-size:9.5pt;margin-top:3mm">Cada região tem arquitetura própria: o mesmo sistema de magia produz cidades diferentes. Vhalessa (Volume I) é gelo, tijolo e calor penhorado; Limiar é portal e lei; o Delta é água e arquivo.</p>'''))
pages.append(pg("10 · Edição", "Gramática editorial em três níveis", f'''<div class="cols"><div>
<h2>Nível 1 · Leitura limpa</h2><p>Texto integral em EB Garamond, margens generosas, nenhum ornamento disputando atenção.</p>
<h2>Nível 2 · Editorial ilustrado</h2><p>Medalhão do emblema na abertura de capítulo, capitular, divisores, mapas parciais e objetos narrativos, só onde apoiam a história.</p>
<h2>Nível 3 · Cinematográfico</h2><p>Página inteira ou dupla sobre negro, só em momentos de virada visual, sempre depois do trecho correspondente.
O impacto vem da mudança de ritmo: cada página de nível 3 tem páginas calmas antes e depois.</p>
<h2>Acabamentos da edição de colecionador</h2><ul><li>Tecido negro, hot stamping ouro envelhecido no emblema e no título; relevo seco no arco.</li>
<li>Verniz localizado nas pérolas; corte pintado negro com filete de ouro.</li><li>Guardas com os sinais das sete leis; caixa rígida, medalhão, lacre e marcadores.</li></ul></div>
<div>{im('08_editorial/ED-001_livro_aberto_capitulo1.png', 125, 84)}<div style="height:3mm"></div>{im('07_capas/CA-006_caixa_colecionador.png', 125, 60)}</div></div>'''))
linhas = "".join(f"<tr><td>{c.split('_', 1)[1].replace('_', ' ')}</td><td>{n}</td></tr>" for c, n in sorted(por_cat.items()))
pages.append(pg("11 · Banco de arte", "Catálogo, auditoria e pendências", f'''<div class="cols"><div><table><tr><th>Categoria</th><th>Arquivos</th></tr>{linhas}
<tr><td><b>Total</b></td><td><b>{len(cat)}</b></td></tr></table>
<p style="font-size:9pt;margin-top:3mm">Cada arte é um arquivo próprio (PNG) com ficha no <i>catalogo.json</i>: categoria, dimensões, modelo, prompt, versão, data e status de aprovação.</p></div><div>
<h2>Auditoria aplicada</h2><ul><li>Texto das capas, do logotipo e do mapa conferido letra a letra.</li><li>Prato esquerdo mais baixo e sete pérolas conferidos no emblema.</li>
<li>Sem marca-d’água, sem texto narrativo dentro das imagens, sem revelação de trama.</li></ul>
<h2>Pendências reais</h2><ul><li>As artes saem do gerador com 1024–1536 px: suficiente para EPUB, redes e pranchas.
A impressão a 300 dpi pede ampliação profissional ou reprodução em resolução maior.</li>
<li>Rostos: um retrato canônico por personagem. Cenas com os mesmos rostos exigem aprovação desses retratos e um gerador com imagem de referência.</li>
<li>Regiões, facções e volumes II–IV vêm das referências do autor e não foram conferidos com o manuscrito desses volumes.</li>
<li>Graphic novel e experiência digital: fases próprias, a partir desta bíblia.</li></ul></div></div>'''))
for f in sorted(os.listdir(PR)):
    if f.endswith(".png"):
        pages.append(full(f"{PR}/{f}"))
html = f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
hp = f"{ROOT}/build/_biblia.html"; open(hp, "w", encoding="utf-8").write(html)
subprocess.run([SHELL, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                f"--print-to-pdf={OUT}", "file://" + hp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(OUT, N[0], "páginas")
