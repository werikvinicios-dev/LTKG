"""Mapas de profundidade (Depth Anything V2 Small) para o 2.5D do trailer. Cache em build/trailer/_cache/prof_*.npy."""
import os, sys, numpy as np
from PIL import Image
CACHE = "/home/user/LTKG/build/trailer/_cache"; os.makedirs(CACHE, exist_ok=True)
_pipe = None


def mapa(caminho, larg=1400):
    """Profundidade normalizada (0 = longe, 1 = perto), no tamanho da imagem original."""
    nome = os.path.splitext(os.path.basename(caminho))[0]
    dst = f"{CACHE}/prof_{nome}.npy"
    if os.path.exists(dst):
        return np.load(dst)
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
    im = Image.open(caminho).convert("RGB")
    pequeno = im.copy(); pequeno.thumbnail((larg, larg))
    d = np.array(_pipe(pequeno)["depth"], dtype=np.float32)
    d = np.array(Image.fromarray(d).resize(im.size, Image.BICUBIC), dtype=np.float32)
    d = (d - d.min()) / max(1e-6, d.max() - d.min())
    np.save(dst, d.astype(np.float16))
    return d


if __name__ == "__main__":
    for c in sys.argv[1:]:
        d = mapa(c); Image.fromarray((np.asarray(d, np.float32) * 255).astype(np.uint8)).save(f"{CACHE}/prof_{os.path.basename(c)}.png"); print(c, d.shape)
