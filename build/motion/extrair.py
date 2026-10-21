#!/usr/bin/env python3
"""Extrai camadas RGBA das artes do banco para o motion (cache em build/_motion/)."""
import numpy as np, os
from PIL import Image
from scipy import ndimage
BA = "/home/user/LTKG/exportacoes/banco_de_arte"; C = "/home/user/LTKG/build/_motion"; os.makedirs(C, exist_ok=True)

def key(a, lo=38, span=55):
    """Alfa por luminância (fundo escuro some), saturação alta preservada (carmim)."""
    a = a.astype(np.float32); mx = a.max(2); mn = a.min(2); sat = (mx - mn) / np.maximum(mx, 1)
    al = np.clip((mx - lo) / span, 0, 1)
    al = np.maximum(al, np.where((sat > .45) & (mx > 35), np.clip((mx - 35) / 30, 0, 1), 0))
    return np.dstack([a, al * 255]).astype(np.uint8)

def save(arr, name):
    im = Image.fromarray(arr, "RGBA"); bb = im.getbbox(); im = im.crop(bb) if bb else im
    im.save(f"{C}/{name}.png"); return im.size

def panels(path, n, y0f, y1f, prefix, inset=14):
    """Compartimentos verticais: divisórias = colunas mais claras (filetes de ouro)."""
    a = np.asarray(Image.open(path).convert("RGB"))
    H, W = a.shape[:2]; prof = a[int(H * .3):int(H * .7)].max(2).mean(0)
    sm = ndimage.uniform_filter1d(prof, 5)
    cand = [x for x in range(8, W - 8) if sm[x] == sm[max(0, x - 25):x + 25].max() and sm[x] > np.percentile(sm, 88)]
    # escolhe n+1 divisórias mais próximas da divisão regular
    edges = []
    for k in range(n + 1):
        t = W * (0.012 + 0.976 * k / n)
        best = min(cand, key=lambda x: abs(x - t)) if cand else t
        edges.append(best if abs(best - t) < W / n * .25 else t)
    out = []
    for k in range(n):
        x0, x1 = int(edges[k]) + inset, int(edges[k + 1]) - inset
        crop = a[int(H * y0f):int(H * y1f), x0:x1]
        out.append(save(key(crop), f"{prefix}{k}"))
    return out

print("leis", panels(f"{BA}/02_simbolos/SI-001_sete_leis.png", 7, .06, .94, "lei"))
print("disc", panels(f"{BA}/02_simbolos/SI-002_seis_disciplinas.png", 6, .05, .55, "disc"))
# etapas: 6 medalhões em fundo preto → componentes conexos maiores
a = np.asarray(Image.open(f"{BA}/02_simbolos/SI-003_etapas_da_transposicao.png").convert("RGB"))
m = ndimage.binary_closing(a.max(2) > 60, iterations=6); lab, nl = ndimage.label(m)
objs = sorted([(s[1].start, s) for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) > 120], key=lambda t: t[0])
print("etapas", len(objs), [save(key(a[s[0].start - 6:s[0].stop + 6, s[1].start - 6:s[1].stop + 6]), f"etapa{k}") for k, (_, s) in enumerate(objs[:6])])
# emblema transparente: metades, coluna central, pérolas
e = np.asarray(Image.open(f"{BA}/01_identidade/ID-008_emblema_transparente.png").convert("RGBA")).copy()
H, W = e.shape[:2]; cx = W // 2
rgb = e[..., :3].astype(np.float32); mx = rgb.max(2); mn = rgb.min(2); sat = (mx - mn) / np.maximum(mx, 1)
col_w = int(W * .085)
pearl = (mx > 175) & (sat < .22) & (np.abs(np.arange(W)[None, :] - cx) < col_w)
pearl = ndimage.binary_opening(pearl, iterations=2); pearl = ndimage.binary_dilation(pearl, iterations=3)
lab, nl = ndimage.label(pearl); sl = ndimage.find_objects(lab)
blobs = sorted([(s[0].start, s, i + 1) for i, s in enumerate(sl) if (s[0].stop - s[0].start) > 25 and (s[1].stop - s[1].start) > 25], key=lambda t: t[0])
pp = []
for k, (_, s, i) in enumerate(blobs):
    sub = e[s[0].start:s[0].stop, s[1].start:s[1].stop].copy(); msk = lab[s[0].start:s[0].stop, s[1].start:s[1].stop] == i
    sub[..., 3] = (sub[..., 3] * msk).astype(np.uint8); Image.fromarray(sub, "RGBA").save(f"{C}/perola{k}.png")
    pp.append((s[1].start, s[0].start))
xs = np.arange(W)[None, :]
pm = ndimage.binary_dilation(lab > 0, iterations=1)
def part(cond, name):
    p = e.copy(); p[..., 3] = (p[..., 3] * cond).astype(np.uint8); Image.fromarray(p, "RGBA").save(f"{C}/{name}.png")
colmask = (np.abs(xs - cx) <= col_w) & np.ones((H, 1), bool)
part((xs < cx - col_w) & np.ones((H, 1), bool), "emb_esq"); part((xs > cx + col_w) & np.ones((H, 1), bool), "emb_dir")
part(colmask & ~pm, "emb_coluna")
open(f"{C}/perolas.txt", "w").write("\n".join(f"{x} {y}" for x, y in pp))
print("perolas", len(pp), "emblema", W, H, "col_w", col_w)
# lettering: faixas horizontais separadas por linhas vazias de alfa
l = np.asarray(Image.open(f"{BA}/01_identidade/ID-006_lettering_transparente.png").convert("RGBA"))
rows = (l[..., 3] > 40).sum(1) > 3; bands = []; y = 0
while y < len(rows):
    if rows[y]:
        y0 = y
        while y < len(rows) and rows[y]: y += 1
        if y - y0 > 6: bands.append((y0, y))
    y += 1
print("faixas lettering", bands)
for k, (y0, y1) in enumerate(bands):
    Image.fromarray(l[max(0, y0 - 4):y1 + 4], "RGBA").save(f"{C}/letra{k}.png")
