#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retoque da capa do Vol. I ampliada 4×: remove três borrões claros que o gerador deixou sob
"MATAR D". O fundo é refeito com a cor do anel limpo em volta e com grão igual ao do fundo (≈0,8).
As letras ficam protegidas por máscara de saturação. Roda depois de ampliar.py; sobrescreve o _4x.jpg."""
import numpy as np, cv2
from PIL import Image

P = "/home/user/LTKG/exportacoes/banco_de_arte_4x/07_capas/CA-001_capa_vol1_o_deus_que_caiu_do_ceu_4x.jpg"
X0, Y0, X1, Y1 = 1280, 760, 2320, 1160
BORROES = [(1530, 992, 75, 55), (1868, 988, 75, 80), (2045, 1030, 70, 35)]   # centro e raios, em px da 4×


def componentes(mask, minimo, maximo=None):
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    out = np.zeros(mask.shape, np.uint8)
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        if a >= minimo and (maximo is None or a <= maximo):
            out[lab == i] = 1
    return out


a = np.asarray(Image.open(P).convert("RGB")).copy()
r = a[Y0:Y1, X0:X1].astype(np.float32)
hsv = cv2.cvtColor(r.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
sat, val = hsv[..., 1] / 255, hsv[..., 2] / 255
ell = np.zeros(r.shape[:2], np.uint8)
for cx, cy, rx, ry in BORROES:
    cv2.ellipse(ell, (cx - X0, cy - Y0), (rx, ry), 0, 0, 360, 1, -1)
letras = componentes((sat >= 0.40) & (val > 0.30), 2001)
perto = cv2.dilate(letras, np.ones((21, 21), np.uint8)) > 0
letras = cv2.dilate(letras, np.ones((5, 5), np.uint8)) > 0
m = componentes((val > 0.13) & (ell > 0) & ~letras, 400)
m = cv2.dilate(m, np.ones((15, 15), np.uint8)); m[letras] = 0; m[ell == 0] = 0
anel = ((cv2.dilate(m, np.ones((81, 81), np.uint8)) > 0) & ~(cv2.dilate(m, np.ones((19, 19), np.uint8)) > 0)
        & ~perto & (val < 0.15))
w = anel.astype(np.float32)
den = cv2.GaussianBlur(w, (0, 0), 25)
base = cv2.GaussianBlur(r * w[..., None], (0, 0), 25) / np.maximum(den, 1e-3)[..., None]
base = np.where(den[..., None] > 0.02, base, np.median(r[anel], axis=0))
g = cv2.GaussianBlur(np.random.default_rng(11).normal(0, 1, r.shape[:2]).astype(np.float32), (0, 0), 0.9)
fill = base + (g / g.std())[..., None] * 0.8
soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 5)[..., None]
a[Y0:Y1, X0:X1] = np.clip(r * (1 - soft) + fill * soft + 0.5, 0, 255).astype(np.uint8)
Image.fromarray(a).save(P, quality=93, subsampling=0, optimize=True)
print(P, int(m.sum()), "px retocados")
