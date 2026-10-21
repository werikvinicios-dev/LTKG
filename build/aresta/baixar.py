#!/usr/bin/env python3
"""Baixa uma arte gerada (URL do Figma, válida por 7 dias) para o banco de arte e registra a ficha.
Uso: python3 baixar.py <categoria> <codigo_nome> <url> <modelo> "<prompt resumido>" """
import sys, json, os, subprocess, datetime
from PIL import Image
cat, nome, url, modelo, prompt = sys.argv[1:6]
base = "/home/user/LTKG/exportacoes/banco_de_arte"
d = f"{base}/{cat}"; os.makedirs(d, exist_ok=True)
p = f"{d}/{nome}.png"
subprocess.run(["curl", "-sf", "-L", "-o", p, url], check=True)
im = Image.open(p); w, h = im.size
cat_path = f"{base}/catalogo.json"
c = json.load(open(cat_path, encoding="utf-8")) if os.path.exists(cat_path) else []
c = [x for x in c if x["arquivo"] != f"{cat}/{nome}.png"]
c.append(dict(arquivo=f"{cat}/{nome}.png", categoria=cat, largura=w, altura=h, modelo=modelo, versao="v1",
              status="proposta — aguardando aprovação do autor", spoiler=False,
              prompt=prompt, data=datetime.date.today().isoformat()))
json.dump(c, open(cat_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(p, w, h)
