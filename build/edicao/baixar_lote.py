"""Baixa ilustrações geradas e registra no manifesto da edição.
Uso: python3 baixar_lote.py <<< 'ID URL' (uma por linha). Salva em exportacoes/banco_de_arte/11_edicao/ID.png"""
import sys, json, os, subprocess
from PIL import Image
D = "/home/user/LTKG/exportacoes/banco_de_arte/11_edicao"; os.makedirs(D, exist_ok=True)
MAN = "/home/user/LTKG/build/edicao/arte_edicao.json"
m = json.load(open(MAN)) if os.path.exists(MAN) else {}
for l in sys.stdin:
    if not l.strip(): continue
    k, url = l.split()[:2]
    p = f"{D}/{k}.png"
    subprocess.run(["curl", "-sfL", "-o", p, url], check=True)
    w, h = Image.open(p).size
    m[k] = {"arquivo": f"exportacoes/banco_de_arte/11_edicao/{k}.png", "w": w, "h": h}
    print(k, w, h)
json.dump(m, open(MAN, "w"), ensure_ascii=False, indent=1)
