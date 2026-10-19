#!/usr/bin/env python3
"""Capa tipográfica para 'Leis para Matar Deuses — Vol. 1'. Sem spoilers."""
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1600, 2400
# paleta: inverno/bronze
BG_TOP = (14, 18, 26)
BG_BOT = (28, 24, 20)
BRONZE = (196, 150, 86)
BRONZE_DIM = (120, 94, 56)
PALE = (228, 224, 214)
ICE = (150, 170, 190)

img = Image.new("RGB", (W, H), BG_TOP)
px = img.load()
# gradiente vertical
for y in range(H):
    t = y / H
    r = int(BG_TOP[0] + (BG_BOT[0]-BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOT[1]-BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOT[2]-BG_TOP[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)

d = ImageDraw.Draw(img, "RGBA")

# --- o Sol de Inverno eclipsado: um disco de bronze com um corte diagonal (a lente rachada), apagado ---
cx, cy, R = W//2, 980, 360
# halo frio
for i in range(60, 0, -1):
    a = int(5 * (i/60))
    d.ellipse([cx-R-i*3, cy-R-i*3, cx+R+i*3, cy+R+i*3], outline=(ICE[0], ICE[1], ICE[2], a), width=3)
# disco
d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(20, 22, 28))
d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=BRONZE, width=10)
# raios curtos de bronze (coroa), alguns apagados
for k in range(24):
    ang = k * (2*math.pi/24)
    r0 = R + 18
    r1 = R + (70 if k % 3 else 30)
    x0, y0 = cx + r0*math.cos(ang), cy + r0*math.sin(ang)
    x1, y1 = cx + r1*math.cos(ang), cy + r1*math.sin(ang)
    col = BRONZE_DIM if k % 2 else BRONZE
    d.line([x0, y0, x1, y1], fill=col, width=6)
# a rachadura diagonal na lente
d.line([cx-R*0.82, cy-R*0.5, cx+R*0.7, cy+R*0.78], fill=(10, 11, 14), width=14)
d.line([cx-R*0.82, cy-R*0.5, cx+R*0.7, cy+R*0.78], fill=(40, 44, 52), width=4)

# --- a torre: duas linhas verticais de bronze subindo do pé da capa até o disco ---
tw = 150
ty0 = cy + R - 20
ty1 = H - 120
d.polygon([(cx-tw//2, ty1), (cx+tw//2, ty1), (cx+tw//3, ty0), (cx-tw//3, ty0)], fill=(22, 24, 30))
d.line([cx-tw//2, ty1, cx-tw//3, ty0], fill=BRONZE_DIM, width=5)
d.line([cx+tw//2, ty1, cx+tw//3, ty0], fill=BRONZE_DIM, width=5)
# janelas da torre (pequenas, apagadas)
for yy in range(int(ty0)+60, int(ty1)-40, 120):
    d.rectangle([cx-10, yy, cx+10, yy+36], fill=(46, 40, 30))

def font(sz, bold=True, italic=False):
    base = "/usr/share/fonts/truetype/dejavu/DejaVuSerif"
    name = base + ("-Bold" if bold and not italic else "") + (".ttf")
    if italic:
        name = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
    try:
        return ImageFont.truetype(name, sz)
    except Exception:
        return ImageFont.load_default()

def centered(text, y, f, fill, tracking=0):
    if tracking:
        # desenhar com espaçamento entre letras
        widths = [d.textlength(ch, font=f) for ch in text]
        total = sum(widths) + tracking*(len(text)-1)
        x = (W - total)/2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=f, fill=fill)
            x += w + tracking
    else:
        w = d.textlength(text, font=f)
        d.text(((W-w)/2, y), text, font=f, fill=fill)

# título
centered("LEIS PARA", 150, font(130), PALE, tracking=10)
centered("MATAR DEUSES", 300, font(130), PALE, tracking=6)
# filete
d.line([W*0.28, 520, W*0.72, 520], fill=BRONZE, width=4)
centered("VOLUME 1", 560, font(52), BRONZE, tracking=18)
centered("O Deus que Caiu do Céu", 630, font(58, italic=True), ICE)

# autor
centered("WERIK MARTINS", H-200, font(60), PALE, tracking=14)

img.save("/home/user/LTKG/build/capa.png", "PNG")
# versão menor para epub
img.resize((1000, 1500), Image.LANCZOS).save("/home/user/LTKG/exportacoes/capa.png", "PNG")
print("capa gerada")
