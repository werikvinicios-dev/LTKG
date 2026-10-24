"""Sampler das gravações reais (VSCO-2-CE, BigSoundBank, Kenney, OpenGameArt). Tudo em 48 kHz estéreo float32.
- instrumento(): toca uma nota de um naipe gravado, com transposição curta a partir da amostra mais próxima,
  camada de dinâmica pela intensidade, laço com fusão cruzada quando a nota é mais longa que a gravação, e soltura.
- som(): um efeito gravado (trecho por tempo) ; golpes(): os ataques isolados de um arquivo com vários golpes.
"""
import functools, glob, os, re, subprocess
import numpy as np

SR = 48000
F = "/home/user/LTKG/build/trailer/_cache/fontes"
NOMES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}

# naipe → (pasta, deslocamento de oitava do nome do arquivo para a altura real, medido por autocorrelação)
NAIPES = {
    "violoncelos": ("Strings/Cello Section/susvib", 1), "violoncelos_spic": ("Strings/Cello Section/spic", 1),
    "violoncelos_trem": ("Strings/Cello Section/trem", 1), "violas": ("Strings/Viola Section/susvib", 1),
    "violinos": ("Strings/Violin Section/susVib", 1), "violinos_spic": ("Strings/Violin Section/Spic", 1),
    "violinos_trem": ("Strings/Violin Section/Trem", 1), "contrabaixo": ("Strings/Solo Contrabass/SusVib", 1),
    "contrabaixo_spic": ("Strings/Solo Contrabass/Spic", 1), "harpa": ("Strings/Harp", 0),
    "trompas": ("Brass/F Horn/sus", 1), "trombone": ("Brass/Tenor Trombone/sus", 1), "tuba": ("Brass/Tuba/sus", 1),
    "trompete": ("Brass/Trumpet/sus", 1), "flauta": ("Woodwinds/Flute/susNV", 1),
}
rng = np.random.default_rng(7)


@functools.lru_cache(maxsize=512)
def ler(caminho):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", caminho, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2).copy()


def aparar(x, limiar=.003):
    """Tira o silêncio antes do ataque."""
    a = np.abs(x).max(1)
    i = int(np.argmax(a > max(limiar, a.max() * .01)))
    return x[max(0, i - int(.004 * SR)):]


@functools.lru_cache(maxsize=None)
def indice(naipe):
    pasta, desl = NAIPES[naipe]
    itens = []
    for c in sorted(glob.glob(f"{F}/vsco/{pasta}/*.wav")):
        m = re.search(r"_([A-G]#?)(-?\d)(?:_|\.wav)", os.path.basename(c))
        if not m:
            continue
        midi = 12 * (int(m.group(2)) + desl + 1) + NOMES[m.group(1)]
        v = re.search(r"_v(\d)", os.path.basename(c))
        itens.append((midi, int(v.group(1)) if v else 1, c))
    return itens


def transpor(x, semitons):
    if abs(semitons) < 1e-3:
        return x
    r = 2 ** (semitons / 12)
    n = int(len(x) / r)
    pos = np.arange(n) * r
    return np.stack([np.interp(pos, np.arange(len(x)), x[:, k]) for k in range(2)], 1).astype(np.float32)


def alongar(x, n, fusao=.35):
    """Repete o miolo sustentado da nota com fusão cruzada até chegar a n amostras."""
    if len(x) >= n:
        return x[:n]
    a, b = int(len(x) * .35), int(len(x) * .85)
    f = int(fusao * SR)
    meio = x[a:b]
    out = x[:b].copy()
    rampa = np.linspace(0, 1, f, dtype=np.float32)[:, None]
    while len(out) < n:
        k = int(rng.integers(0, max(1, len(meio) // 3)))
        trecho = np.concatenate([meio[k:], meio[:k]]) if k else meio
        cauda = out[-f:] * (1 - rampa) + trecho[:f] * rampa
        out = np.concatenate([out[:-f], cauda, trecho[f:]])
    return out[:n]


def instrumento(naipe, midi, dur, vel=.6, solta=.8, ataque=0.0):
    itens = indice(naipe)
    perto = min(abs(m - midi) for m, _, _ in itens)
    cands = [(m, v, c) for m, v, c in itens if abs(m - midi) == perto]
    camadas = sorted({v for _, v, _ in cands})
    alvo = camadas[min(len(camadas) - 1, int(vel * len(camadas)))]
    m, _, c = [t for t in cands if t[1] == alvo][int(rng.integers(0, len([t for t in cands if t[1] == alvo])))]
    x = aparar(ler(c))
    x = x / (np.abs(x).max() + 1e-9)
    x = transpor(x, midi - m)
    n = int((dur + solta) * SR)
    x = alongar(x, n) if len(x) < n else x[:n]
    env = np.ones(len(x), np.float32)
    s = int(solta * SR)
    env[-s:] = np.linspace(1, 0, s) ** 1.5
    if ataque > 0:
        a = int(ataque * SR)
        env[:a] *= np.linspace(0, 1, a) ** 1.2
    return x * env[:, None] * vel


def acorde(naipe, notas, dur, vel=.5, solta=1.0, ataque=0.0):
    partes = [instrumento(naipe, n, dur, vel / len(notas) ** .5, solta, ataque) for n in notas]
    out = np.zeros((max(len(p) for p in partes), 2), np.float32)
    for p in partes:
        out[:len(p)] += p
    return out


def percussao(padrao, vel=.8, i=None):
    """Um golpe de percussão gravada (padrão glob dentro de Percussion/)."""
    cs = sorted(glob.glob(f"{F}/vsco/Percussion/{padrao}"))
    c = cs[i if i is not None else int(rng.integers(0, len(cs)))]
    x = aparar(ler(c))
    return x / (np.abs(x).max() + 1e-9) * vel


def tympano(midi, vel=.8, dur=None):
    """Tímpano afinado: escolhe a pele mais próxima da nota e transpõe o resto."""
    peles = {2: 35, 3: 37, 4: 40, 5: 42}        # Timpani2..5 medidos em B1, C#2, E2, F#2
    k = min(peles, key=lambda p: abs(peles[p] - midi))
    camada = "v4" if vel > .7 else ("v3" if vel > .4 else "v1")
    cs = sorted(glob.glob(f"{F}/vsco/Percussion/Timpani/Timpani{k}_Hit_{camada}_*.wav")) or \
        sorted(glob.glob(f"{F}/vsco/Percussion/Timpani/Timpani{k}_Hit_*.wav"))
    x = aparar(ler(cs[int(rng.integers(0, len(cs)))]))
    x = transpor(x / (np.abs(x).max() + 1e-9), midi - peles[k])
    return (x[:int(dur * SR)] if dur else x) * vel


def arquivo(nome):
    if nome.startswith("oga:"):                       # OpenGameArt (pacotes CC0): caminho dentro de _cache/fontes/oga
        return f"{F}/oga/{nome[4:]}"
    if re.fullmatch(r"\d{4}", nome):
        for e in ("flac", "aiff"):
            c = f"{F}/bsb/{nome}.{e}"
            if os.path.exists(c):
                return c
    c = f"{F}/kenney/{nome}.ogg"
    if os.path.exists(c):
        return c
    raise FileNotFoundError(nome)


def som(nome, ini=0.0, dur=None, vel=1.0, entra=.02, sai=.05, normal=True):
    """Trecho de um efeito gravado. nome: número do BigSoundBank ('0595') ou arquivo do Kenney ('footstep_snow_000')."""
    x = ler(arquivo(nome))
    a = int(ini * SR)
    x = x[a:a + int(dur * SR)] if dur else x[a:]
    x = x.copy()
    if normal:
        x /= np.abs(x).max() + 1e-9
    e, s = int(entra * SR), int(sai * SR)
    if e:
        x[:e] *= np.linspace(0, 1, e)[:, None]
    if s:
        x[-s:] *= np.linspace(1, 0, s)[:, None]
    return x * vel


@functools.lru_cache(maxsize=None)
def golpes(nome, limiar=.25, minimo=.12):
    """Instantes (s) dos ataques num arquivo com vários golpes."""
    x = np.abs(ler(arquivo(nome))).max(1)
    h = int(.005 * SR)
    e = x[:len(x) // h * h].reshape(-1, h).max(1)
    e = e / (e.max() + 1e-9)
    t, ult = [], -1e9
    for i in range(1, len(e)):
        if e[i] > limiar and e[i] > 2.5 * e[max(0, i - 4):i].mean() + 1e-4 and (i - ult) * h / SR > minimo:
            t.append(i * h / SR); ult = i
    return tuple(t)


def golpe(nome, k, dur=.8, vel=1.0, pre=.006):
    t = golpes(nome)
    return som(nome, max(0, t[k % len(t)] - pre), dur, vel, entra=.002, sai=min(.2, dur / 3))
