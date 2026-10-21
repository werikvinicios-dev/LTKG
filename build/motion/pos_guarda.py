#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pós-produção da Guarda de Retorno em 3D: brilho nas altas luzes, granulação, vinheta, faixas de cinema
(2,39:1 dentro de 1920×1080), cartela final e trilha sintetizada. Lê os quadros de build/_blender/guarda/."""
import glob, os, subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from magia_motor import trilha, texto, ROOT, TMP

SRC = f"{ROOT}/build/_blender/guarda"
SAIDA = f"{ROOT}/exportacoes/banco_de_arte/CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/motion/MG3D-S04_cena.mp4"
W, H, FPS, CW, CH = 1920, 1080, 24, 1920, 804
CARTELA = 2.0
rng = np.random.default_rng(3)
yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
VIG = (1 - 0.38 * (((xx - CW / 2) / (CW / 2)) ** 2 + ((yy - CH / 2) / (CH / 2)) ** 2) ** 1.3).clip(.4, 1)[..., None]


def trata(im):
    im = im.convert("RGB").resize((CW, CH), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    lum = a.max(axis=2, keepdims=True); alto = np.clip((lum - .62) / .38, 0, 1) * a
    g = Image.fromarray((alto * 255).astype(np.uint8)).resize((CW // 4, CH // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((CW, CH), Image.BILINEAR)
    a = a + np.asarray(g).astype(np.float32) / 255 * .55
    a = a * np.array([.97, 1.0, 1.04]) * VIG                     # leve frio nas sombras e vinheta
    a = a + rng.normal(0, .012, (CH, CW, 1))
    q = Image.new("RGB", (W, H)); q.paste(Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8)), (0, (H - CH) // 2))
    return q


def cartela(u):
    q = Image.new("RGBA", (W, H), (0, 0, 0, 255)); al = min(1, u * 3, (1 - u) * 3)
    for s, nome, tam, cor, y in (("GUARDA DE RETORNO", "Cinzel-Bold.ttf", 64, (201, 161, 90), H // 2 - 40),
                                 ("Saldo Final · capítulo 15", "EBGaramond-Italic.ttf", 34, (214, 200, 170), H // 2 + 40),
                                 ("LEIS PARA MATAR DEUSES", "Cinzel-SemiBold.ttf", 22, (156, 138, 102), H // 2 + 110)):
        im = texto(s, nome, tam, cor, .14 if "Cinzel" in nome else 0)
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * al)))
        q.alpha_composite(im, (W // 2 - im.width // 2, y - im.height // 2))
    return q.convert("RGB")


if __name__ == "__main__":
    qs = sorted(glob.glob(f"{SRC}/q_*.png")); n = len(qs); dur = n / FPS + CARTELA
    ev = [(0.0, "sopro", dict(d=3.0, g=.25)), (1.25, "baque", dict(d=2.0, f0=45, f1=22, g=.35)), (2.0, "baque", dict(d=1.6, f0=50, f1=24, g=.25)),
          (2.92, "baque", dict(d=2.4, f0=70, f1=24, g=1.0)), (2.92, "estalo", dict(d=1.0, g=.9)), (2.95, "crepita", dict(d=1.1, g=.55)),
          (3.2, "zumbido", dict(d=1.6, f=95, g=.22)), (4.0, "zumbido", dict(d=1.5, f=190, g=.12)),
          (5.6, "estalo", dict(d=.9, g=.85)), (5.62, "baque", dict(d=1.8, f0=60, f1=26, g=.7)), (5.65, "sopro", dict(d=1.4, g=.55)),
          (6.4, "sopro", dict(d=1.6, g=.2)), (n / FPS + .2, "sino", dict(f0=146.8, d=2.2, g=.22)), (n / FPS + .2, "sino", dict(f0=220, d=2.2, g=.12))]
    wav, vid = f"{TMP}/guarda3d.wav", f"{TMP}/guarda3d.mp4"
    trilha(dur, ev, wav, drone=(36.7, 55.0))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for f in qs: p.stdin.write(trata(Image.open(f)).tobytes())
    for k in range(int(CARTELA * FPS)): p.stdin.write(cartela(k / (CARTELA * FPS)).tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", SAIDA], check=True)
    trata(Image.open(qs[len(qs) // 2])).save(SAIDA.replace(".mp4", "_quadro.jpg"), quality=90)
    print(SAIDA, n, "quadros")
