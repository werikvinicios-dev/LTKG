"""Renderiza quadros de teste e monta uma folha de contato."""
import sys, time, numpy as np
from PIL import Image, ImageDraw
import os
import base as B
if os.environ.get('VERT') == '1': B.formato(1080, 1920)
import cenas as C
ts = [float(x) for x in sys.argv[2:]]
out = sys.argv[1]
ims = []
for t in ts:
    t0 = time.time(); im = Image.fromarray(B.para_u8(C.quadro(t))); print(f"{t:6.2f}s  {time.time() - t0:.2f}s", flush=True)
    im.thumbnail((640, 640)); ImageDraw.Draw(im).text((6, 6), f"{t:.1f}", fill="yellow"); ims.append(im)
cols = 4 if B.W > B.H else 8; w, h = ims[0].size
c = Image.new("RGB", (cols * w, ((len(ims) + cols - 1) // cols) * h))
for i, im in enumerate(ims): c.paste(im, ((i % cols) * w, (i // cols) * h))
c.save(out, quality=88)
