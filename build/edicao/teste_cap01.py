import sys; sys.path.insert(0, "/home/user/LTKG/build/edicao")
from motor import *
md = open(f"{ROOT}/manuscrito/V2/01.md", encoding="utf-8").read()
tit = md.split("\n", 1)[0].split("—", 1)[1].strip(); corpo = md.split("\n", 1)[1]
A = "exportacoes/acervo_drive"
contrato = documento('<div class="dt">Companhia Arrimo · Seguros e Garantias</div><p><b>Cláusula sétima.</b> O contratado se compromete a não causar dano estrutural ao imóvel segurado.</p>'
  '<p><b>Cláusula oitava.</b> O contratado se compromete a preservar, sempre que possível, o ativo térmico penhorado.</p><p><b>Cláusula nona.</b> O contratado ficará em Vhalessa por três dias depois do serviço.</p>'
  f'<p style="text-align:right;margin-top:4mm"><i>Pelle Dorn, agente</i></p><div class="carimbo">{anel_svg(22, cor="#8E1B22")}</div>', "contrato")
ins = {6: contrato, 40: banda(f"{A}/cenarios/S04_Cozinha_do_Lento.png", "center 45%", 70, "A Cozinha do Lento: o calor do salão vinha da brasa de parede.")}
pecas = [imagem_cheia("exportacoes/capa_v2/capa_ebook.jpg"),
         abertura_parte("I", "O Frio", "Em Vhalessa ninguém queimava lenha para esquentar a casa. Quem esquentava as casas era o deus.", "exportacoes/banco_de_arte/05_mundo/MU-009_vhalessa_fornalha_velha_noite.png"),
         abertura_capitulo(1, tit, "exportacoes/banco_de_arte_4x/06_personagens/PE-024_ilan_estalagem_4x.jpg", "center 30%", "Brasa", "Toda ação retorna. — Sétima Lei"),
         capitulo_texto(1, "Onze páginas de contrato", corpo, ins),
         respiro(f"{A}/cenarios/S01_Vhalessa_Inverno.png", "E no Sete Chaminés, por uma hora, foi verão.", autor="Capítulo 1")]
p = compor(pecas, [(1, "Onze páginas de contrato")], "/tmp/claude-0/-home-user-LTKG/0ae43a17-9955-54f0-9172-040bd4d1f0e3/scratchpad/teste_cap01.pdf")
from pypdf import PdfReader; print(len(PdfReader(p).pages))
