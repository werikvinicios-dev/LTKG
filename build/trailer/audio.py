"""Áudio do trailer: narração (Piper pt_BR, tratada), trilha original sintetizada e efeitos sincronizados.
Gera stems separados em 48 kHz estéreo e as misturas (completa, sem narração, sem música)."""
import math, os, subprocess, wave, json
import numpy as np
from scipy import signal
import cenas as C

SR = 48000
DUR = 90.0
N = int(SR * DUR)
OUT = "/home/user/LTKG/build/trailer/_cache/audio"
os.makedirs(OUT, exist_ok=True)
MODELO = "/home/user/LTKG/build/trailer/_modelos/pt_BR-faber-medium.onnx"
rng = np.random.default_rng(21)

# ------------------------------------------------------------------ util
def t_(dur): return np.arange(int(dur * SR)) / SR


def adsr(n, a=.01, d=.1, s=.8, r=.2, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    e = np.ones(n, np.float32) * s
    a = min(a, n); e[:a] = np.linspace(0, 1, a)
    d = min(d, n - a); e[a:a + d] = np.linspace(1, s, d)
    r = min(r, n); e[n - r:] *= np.linspace(1, 0, r)
    return e


def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f / (SR / 2), "low", output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f / (SR / 2), "high", output="sos"), x)
def bp(x, f1, f2, o=2): return signal.sosfilt(signal.butter(o, [f1 / (SR / 2), f2 / (SR / 2)], "band", output="sos"), x)


def ressoa(x, f, q=12):
    b, a = signal.iirpeak(f / (SR / 2), q)
    return signal.lfilter(b, a, x)


def ruido(dur): return rng.standard_normal(int(dur * SR)).astype(np.float32)


def por(buf, x, t, g=1.0, pan=0.0):
    """Coloca o som x (mono ou estéreo) em t segundos, com ganho e pan (-1..1)."""
    i = int(t * SR)
    if i >= buf.shape[0]:
        return
    if x.ndim == 1:
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        x = np.stack([x * l, x * r], 1) * 1.414
    n = min(len(x), buf.shape[0] - i)
    buf[i:i + n] += x[:n] * g


def nota(n): return 440.0 * 2 ** ((n - 69) / 12)


def ir_sala(dur=3.2, decai=2.6, tom=4500, seed=1):
    r = np.random.default_rng(seed)
    n = int(dur * SR); tt = np.arange(n) / SR
    e = np.exp(-tt * 6.9 / decai)
    ir = np.stack([lp(r.standard_normal(n) * e, tom), lp(r.standard_normal(n) * e, tom)], 1)
    ir[:int(.012 * SR)] *= np.linspace(0, 1, int(.012 * SR))[:, None]
    return (ir / np.abs(ir).sum(0).max() * 8).astype(np.float32)


def reverb(x, ir, mix=.3):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    w = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in (0, 1)], 1)
    return x * (1 - mix) + w * mix


def salvar(nome, x, pico=.89):
    x = np.asarray(x, np.float32)
    m = np.abs(x).max()
    if m > 0 and pico:
        x = x / m * pico
    caminho = f"{OUT}/{nome}.wav"
    with wave.open(caminho, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    return caminho


def ler_wav(c):
    with wave.open(c) as w:
        sr = w.getframerate(); ch = w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    a = a.reshape(-1, ch).mean(1)
    if sr != SR:
        a = signal.resample_poly(a, SR // math.gcd(SR, sr), sr // math.gcd(SR, sr))
    return a


# ------------------------------------------------------------------ instrumentos
def violoncelo(f, dur, vel=.8, vib=True):
    tt = t_(dur); n = len(tt)
    v = 1 + (.0045 * np.sin(2 * np.pi * 5.3 * tt) * np.clip((tt - .35) / .4, 0, 1) if vib else 0)
    fase = 2 * np.pi * f * np.cumsum(v) / SR
    x = np.zeros(n, np.float32)
    for k in range(1, 22):
        if f * k > 9000:
            break
        x += (1 / k ** 1.05) * np.sin(k * fase + k * .7)
    x = x * .9 + ruido(dur) * .03                      # chiado do arco
    x = sum(ressoa(x, fr, q) * g for fr, q, g in ((210, 3, 1.0), (520, 4, .8), (1150, 5, .5), (2600, 6, .25))) + lp(x, 1800) * .4
    e = adsr(n, .22, .3, .85, .45) * (1 + .08 * np.sin(2 * np.pi * .5 * tt))
    return (x * e * vel).astype(np.float32)


def cordas(fs, dur, vel=.5, ataque=1.2, brilho=2400):
    tt = t_(dur); n = len(tt); x = np.zeros(n, np.float32)
    for f in fs:
        for dt in (-.006, -.002, .003, .007):
            ff = f * (1 + dt)
            ph = rng.uniform(0, 6.28)
            s = np.zeros(n, np.float32)
            for k in range(1, 12):
                if ff * k > 8000:
                    break
                s += np.sin(2 * np.pi * ff * k * tt + ph * k) / k
            x += s
    x = lp(x, brilho) / (len(fs) * 4)
    return (x * adsr(n, ataque, .5, .9, min(1.5, dur * .4)) * vel).astype(np.float32)


def spiccato(f, vel=.5, dur=.16):
    tt = t_(dur); x = np.zeros(len(tt), np.float32)
    for dt in (-.004, .004):
        for k in range(1, 9):
            x += np.sin(2 * np.pi * f * (1 + dt) * k * tt) / k
    x = lp(x, 2600) * np.exp(-tt * 22) * np.clip(tt / .006, 0, 1)
    return (x * vel * .5).astype(np.float32)


def coro(fs, dur, vel=.35, vogal=(800, 1150, 2900)):
    tt = t_(dur); n = len(tt); x = np.zeros(n, np.float32)
    for f in fs:
        for dt in (-.01, 0, .008):
            ff = f * (1 + dt) * (1 + .006 * np.sin(2 * np.pi * (4.8 + dt * 50) * tt))
            fase = 2 * np.pi * np.cumsum(ff) / SR
            src = signal.sawtooth(fase) + .02 * rng.standard_normal(n)
            v = sum(ressoa(src, fr, 8) * g for fr, g in zip(vogal, (1, .5, .25)))
            x += v
    x = lp(x, 3500) / (len(fs) * 3)
    return (x * adsr(n, 1.4, .5, .9, 1.6) * vel).astype(np.float32)


def taiko(vel=1.0, f0=120, f1=42, dur=2.2):
    tt = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-tt * 18)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.6)
    x += lp(ruido(dur), 900) * np.exp(-tt * 30) * .5
    return (np.tanh(x * 1.6) * vel).astype(np.float32)


def braam(dur=3.0, vel=1.0, raiz=26):
    tt = t_(dur); n = len(tt); x = np.zeros(n, np.float32)
    for m in (raiz, raiz + 12, raiz + 19, raiz + 24):
        for dt in (-.004, .004):
            x += signal.sawtooth(2 * np.pi * nota(m) * (1 + dt) * tt)
    abre = np.exp(-tt * 1.3)          # o metal abre e escurece
    y = lp(x, 2500) * abre + lp(x, 320) * (1 - abre)
    y = np.tanh(y * .5)
    return (y * adsr(n, .02, .4, .7, 1.6) * vel).astype(np.float32)


def metal(f=420, dur=2.5, vel=.6, dec=2.2):
    tt = t_(dur); x = np.zeros(len(tt), np.float32)
    for k, a in ((1, 1), (2.76, .6), (5.4, .4), (8.93, .25), (13.3, .12)):
        x += a * np.sin(2 * np.pi * f * k * tt + k) * np.exp(-tt * dec * (1 + k * .25))
    x += hp(ruido(dur), 3000) * np.exp(-tt * 60) * .3
    return (x * vel).astype(np.float32)


def riser(dur=3.0, vel=.6):
    tt = t_(dur)
    f = 200 * 2 ** (tt / dur * 3)
    x = hp(ruido(dur), 800) * (tt / dur) ** 2 * .6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / dur) ** 3 * .25
    return (x * vel).astype(np.float32)


def sub(dur, f=41, vel=.5):
    tt = t_(dur)
    return (np.sin(2 * np.pi * f * tt) * adsr(len(tt), .02, .2, .6, .3) * vel).astype(np.float32)


# ------------------------------------------------------------------ trilha original (tema em ré menor)
# TEMA: Ré–Fá–Mi–Lá(grave) / Ré–Fá–Sol–Lá–Si♭–Lá. Reaparece no coro de Aurelia e nos metais do título.
TEMA_A = [(50, 1.6), (53, 1.2), (52, 1.2), (45, 2.6)]
TEMA_B = [(50, 1.0), (53, 1.0), (55, 1.0), (57, 1.4), (58, .9), (57, 2.2)]


def trilha():
    m = np.zeros((N, 2), np.float32)
    ir = ir_sala(3.4, 3.0)
    # 00–25 mistério: violoncelo solo, drones, silêncio
    por(m, cordas([nota(38), nota(45)], 9.5, .35, 3.0, 900), 7.0)            # drone grave sob a cidade
    t = 8.0
    for n_, d in TEMA_A:
        por(m, violoncelo(nota(n_), d + .3, .55), t, pan=-.15); t += d
    por(m, cordas([nota(38), nota(45), nota(50)], 9.0, .3, 1.5, 1200), 16.0)
    for i, tl in enumerate(C.T_LEI):                                          # batidas metálicas espaçadas
        por(m, taiko(.35, 90, 48, 1.6), 16 + tl, pan=(i - 3) * .1)
    por(m, violoncelo(nota(45), 3.2, .5), 21.8); por(m, violoncelo(nota(50), 2.5, .45), 24.0)
    # 25–54 tensão crescente: pulsação de cordas e percussão grave
    bpm = 96; b = 60 / bpm
    for i in range(int((54 - 25) / (b / 2))):
        tt = 25 + i * b / 2
        f = nota(38 if (i // 8) % 4 != 3 else 41)
        intens = .25 + .45 * (tt - 25) / 29
        por(m, spiccato(f * 2, intens), tt, pan=-.3)
        if i % 2 == 0:
            por(m, spiccato(f * 3, intens * .6), tt + b / 4, pan=.3)
        if i % 4 == 0:
            por(m, sub(.5, 41, .35 + .2 * (tt - 25) / 29), tt)
    por(m, cordas([nota(50), nota(53), nota(57)], 10, .32, 3, 1600), 25.0)
    t = 30.0
    for n_, d in TEMA_B:
        por(m, violoncelo(nota(n_), d + .3, .6), t, pan=-.2); t += d
    por(m, braam(3.5, .9, 26), 40.45)                                          # primeira grande batida (congela)
    por(m, taiko(1.0), 40.45)
    por(m, cordas([nota(46), nota(50), nota(53)], 8.5, .32, 1.0, 1800), 45.5)
    # 54–65 fascínio: percussão sai, coro sem palavras e cordas delicadas (o tema no coro)
    por(m, coro([nota(62), nota(65), nota(69)], 5.5, .3), 54.6)
    por(m, coro([nota(60), nota(64), nota(67)], 5.2, .3, (400, 800, 2600)), 59.6)
    t = 59.8
    for n_, d in TEMA_A:
        por(m, coro([nota(n_ + 24)], d + .8, .22, (500, 900, 2700)), t); t += d
    por(m, cordas([nota(62), nota(69), nota(74)], 10.8, .18, 2.5, 3200), 54.2)
    por(m, riser(3.2, .55), 61.8)
    # 65–77 confronto: orquestra completa, cordas rápidas, percussão forte
    bpm = 132; b = 60 / bpm
    for i in range(int((77 - 65) / (b / 4))):
        tt = 65 + i * b / 4
        seq = [38, 38, 50, 38, 41, 38, 50, 45]
        por(m, spiccato(nota(seq[i % 8] + 12), .55), tt, pan=(-.4 if i % 2 else .4))
        if i % 4 == 0:
            por(m, taiko(.7 if i % 16 else 1.0, 110, 45, 1.2), tt)
    for tc in C.CORTES08[:8]:
        por(m, taiko(1.0, 140, 40, 1.8), 65 + tc)
        por(m, metal(320, 1.5, .25, 3), 65 + tc, pan=.2)
    por(m, braam(2.5, .8, 26), 65.0); por(m, braam(2.5, .8, 29), 70.5); por(m, braam(2.6, .85, 26), 73.6)
    por(m, cordas([nota(50), nota(53), nota(57), nota(62)], 12, .4, .4, 3000), 65.0)
    t = 70.6
    for n_, d in TEMA_B:
        por(m, violoncelo(nota(n_ + 12), d * .7 + .2, .55), t, pan=-.1); t += d * .7
    # 77–84 suspensão: a música corta (só um resto de reverberação)
    # 84–90 assinatura: impacto grave, metais com o tema e nota longa
    por(m, taiko(1.0, 100, 36, 3.0), 84.0); por(m, braam(5.5, 1.0, 26), 84.0)
    t = 84.6
    for n_, d in TEMA_A:
        por(m, cordas([nota(n_ - 12), nota(n_)], d + .4, .35, .25, 2000), t); t += d * .8
    por(m, violoncelo(nota(38), 5.5, .55, False), 84.2)
    m = reverb(m, ir, .32)
    corte = int(77.05 * SR)                                                     # suspensão: silêncio total
    m[corte:int(84 * SR)] *= np.concatenate([np.linspace(1, 0, int(.08 * SR)), np.zeros(int(84 * SR) - corte - int(.08 * SR))])[:, None]
    m[int(89.2 * SR):] *= np.linspace(1, 0, N - int(89.2 * SR))[:, None]
    return m


# ------------------------------------------------------------------ efeitos sonoros
def vento_amb(dur, forca=.4, seed=0):
    r = np.random.default_rng(seed)
    x = r.standard_normal(int(dur * SR)).astype(np.float32)
    lfo = .6 + .4 * np.sin(2 * np.pi * .13 * t_(dur) + seed) * np.sin(2 * np.pi * .041 * t_(dur))
    y = bp(x, 180, 900) * lfo + bp(x, 900, 2600) * lfo ** 3 * .25
    return (y * forca).astype(np.float32)


def estalo(vel=.6):
    x = metal(2400, .25, .4, 25) + hp(ruido(.03), 2500) * np.linspace(1, 0, int(.03 * SR)).astype(np.float32)[:int(.25 * SR)].mean() * 0
    return x * vel


def tensao_fio(dur=2.0, f=180, vel=.4):
    tt = t_(dur)
    x = np.sin(2 * np.pi * (f + 25 * tt) * tt) * (1 + .3 * np.sin(2 * np.pi * 30 * tt))
    x += ressoa(ruido(dur), f * 3, 30) * .4
    return (x * adsr(len(tt), .05, .3, .7, .6) * vel).astype(np.float32)


def gota():
    tt = t_(.4)
    x = np.sin(2 * np.pi * (1800 - 1200 * np.clip(tt / .06, 0, 1)) * tt) * np.exp(-tt * 35)
    return (x * .6).astype(np.float32)


def chiado(dur=.6, vel=.3):
    tt = t_(dur)
    return (hp(ruido(dur), 4000) * np.exp(-tt * 6) * vel).astype(np.float32)


def rajada(dur=1.2, vel=.5):
    tt = t_(dur); env_ = np.sin(np.pi * tt / dur) ** 2
    return (bp(ruido(dur), 300, 3000) * env_ * vel).astype(np.float32)


def baque(vel=.8):
    tt = t_(.8)
    x = np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 9) + lp(ruido(.8), 600) * np.exp(-tt * 25) * .6
    return (x * vel).astype(np.float32)


def rachar(dur=1.2, vel=.5):
    x = np.zeros(int(dur * SR), np.float32)
    for _ in range(50):
        i = int(rng.uniform(0, dur * .9) * SR); n = int(.004 * SR)
        x[i:i + n] += rng.standard_normal(n) * rng.uniform(.3, 1) * np.linspace(1, 0, n)
    return (hp(x, 1500) * vel + lp(x, 300) * vel * .6).astype(np.float32)


def espada(vel=.6):
    tt = t_(.9)
    x = ressoa(ruido(.9), 3200, 6) * np.sin(np.pi * np.clip(tt / .55, 0, 1)) * .5 + metal(1900, .9, .5, 4)
    return (x * vel).astype(np.float32)


def engrenagens(dur=1.8, vel=.3):
    x = np.zeros(int(dur * SR), np.float32)
    for k in range(int(dur * 9)):
        por_i = int((k / 9 + rng.uniform(0, .02)) * SR)
        c = metal(rng.uniform(2500, 4200), .08, .5, 60)
        x[por_i:por_i + len(c)] += c[:len(x) - por_i]
    return x * vel


def papel(dur=.8, vel=.3):
    tt = t_(dur)
    return (bp(ruido(dur), 1500, 7000) * (np.abs(np.sin(2 * np.pi * 7 * tt)) ** 3) * np.sin(np.pi * tt / dur) * vel).astype(np.float32)


def brilho_fino(vel=.12):
    return metal(rng.uniform(2200, 3600), 1.6, vel, 1.8)


def respiro(dur=1.3, vel=.15):
    tt = t_(dur)
    return (bp(ruido(dur), 500, 2500) * np.sin(np.pi * tt / dur) ** 2 * vel).astype(np.float32)


def efeitos():
    s = np.zeros((N, 2), np.float32)
    # 01
    por(s, metal(1700, .5, .35, 14), .5, pan=-.2)
    por(s, tensao_fio(2.5, 160, .12), .6)
    por(s, metal(1500, .5, .45, 12), 3.0, pan=.2)
    por(s, tensao_fio(2.6, 210, .25), 3.05)
    por(s, gota(), 5.62); por(s, metal(5200, 1.2, .12, 5), 5.62)
    v = vento_amb(6, .05, 1); v[:int(1.2 * SR)] *= np.linspace(0, 1, int(1.2 * SR)); por(s, v, 1.0)   # o primeiro instante é silêncio
    # 02 cidade: vento, fumaça, um sino ao longe
    por(s, vento_amb(9, .22, 2), 7.0)
    por(s, metal(196, 4, .1, .9), 9.2, pan=.5); por(s, metal(262, 4, .07, .9), 12.8, pan=-.5)
    por(s, rajada(1.0, .25), 11.25)
    # 03 leis: gravação na matéria
    for i, tl in enumerate(C.T_LEI):
        por(s, chiado(.7, .2), 16 + tl, pan=(i - 3) * .12); por(s, metal(700 + 90 * i, 1.6, .22, 2.5), 16 + tl, pan=(i - 3) * .12)
    por(s, tensao_fio(1.2, 240, .2), 16 + C.T_LEI[1])
    por(s, rachar(.5, .2), 16 + C.T_LEI[3] + .15)
    por(s, rajada(1.0, .15), 16 + C.T_LEI[6] + .7)
    # 04 manopla e vento
    por(s, vento_amb(10, .25, 3), 25.0)
    por(s, tensao_fio(1.6, 90, .12), 25.4)
    for k in range(3):
        por(s, respiro(1.4, .08), 31.8 + k * 3.2)
    # 05 nevasca, tecido, congelamento
    por(s, vento_amb(5.6, .55, 4), 35.0)
    for k in range(6):
        por(s, rajada(.7, .22), 35.3 + k * .9)
    por(s, rajada(1.0, .5), 37.6)
    por(s, baque(.7), 40.45); por(s, chiado(1.2, .25), 40.5)
    por(s, papel(1.2, .15), 41.0)
    # 06 rostos: velas, papel, engrenagens, estandarte, livro, passos
    por(s, papel(1.0, .22), 45.2); por(s, papel(.8, .15), 46.8)
    por(s, engrenagens(1.8, .3), 48.0); por(s, chiado(.4, .12), 48.6)
    por(s, rajada(.8, .45), 49.8)
    por(s, papel(.5, .2), 50.65); por(s, baque(.9), 51.22)
    for k in range(5):
        por(s, baque(.12), 52.0 + k * .45, pan=(k - 2) * .15)
    # 07 Aurelia: quase silêncio, brilhos finos, respiração
    for k in range(9):
        por(s, brilho_fino(.06), 54.4 + k * 1.15, pan=rng.uniform(-.6, .6))
    por(s, respiro(1.8, .06), 61.5)
    # 08 o impossível
    por(s, tensao_fio(1.2, 320, .45), 65.0); por(s, metal(900, 1.0, .4, 6), 65.0)
    por(s, rajada(.6, .25), 66.3); por(s, ressoa(ruido(1.2), 800, 4) * .1, 66.3)
    por(s, tensao_fio(1.3, 600, .25), 67.7)
    por(s, rachar(1.4, .55), 69.0)
    por(s, espada(.7), 70.5); por(s, rajada(.5, .4), 70.5)
    por(s, baque(1.0), 72.12); por(s, rachar(1.2, .35), 72.2); por(s, rajada(1.2, .5), 72.15)
    por(s, tensao_fio(1.5, 70, .4), 73.6); por(s, metal(140, 1.5, .3, 2), 73.6)
    por(s, respiro(1.2, .12), 75.3)
    # 09 suspensão: vento e respiração
    por(s, vento_amb(7, .22, 5), 77.0); por(s, respiro(1.6, .1), 79.6)
    # 10 título
    por(s, baque(1.0), 84.0); por(s, chiado(2.0, .1), 84.6)
    return s


# ------------------------------------------------------------------ narração
FALAS = [  # (início s, texto, velocidade, tipo)
    (8.35, "Em Aresta, a magia não cria poder. Ela o move.", 1.12, "normal"),
    (22.35, "E tudo que se move...", 1.15, "normal"),
    (23.75, "deixa um preço.", 1.15, "normal"),
    (30.7, "Sete leis. Nenhuma escolha sem consequência.", 1.1, "normal"),
    (41.1, "Ilan Varek conhecia o peso de uma sentença.", 1.12, "normal"),
    (60.2, "Mas há poderes que se acostumaram a nunca ser questionados.", 1.08, "normal"),
    (70.65, "Eles podem parecer eternos.", 1.12, "normal"),
    (73.4, "Isso não significa que sejam intocáveis.", 1.1, "normal"),
    (78.3, "Para derrubar um deus...", 1.25, "sussurro"),
    (80.9, "basta descobrir o que o sustenta.", 1.2, "sussurro"),
]


def voz(texto, vel, tipo, i):
    bruto = f"{OUT}/fala_{i:02d}.wav"
    subprocess.run(["python3", "-m", "piper", "-m", MODELO, "-f", bruto, "--length-scale", str(vel), "--sentence-silence", "0.1"],
                   input=texto.encode(), check=True, capture_output=True)
    grave = f"{OUT}/fala_{i:02d}_grave.wav"
    fator = 2 ** (-1.6 / 12)   # 1,6 semitom abaixo, mesma duração
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-af", f"asetrate=22050*{fator:.5f},aresample=48000,atempo={1 / fator:.5f}", grave], check=True)
    y = ler_wav(grave)
    # corpo e rouquidão discreta
    y = y + lp(y, 220) * .5
    y = np.tanh(y * 2.2) / 2.2 * 1.2
    y = hp(y, 70)
    if tipo == "sussurro":
        y = y * .8 + bp(ruido(len(y) / SR), 1500, 6000)[:len(y)] * np.abs(signal.hilbert(y)) * .5
    y = y / (np.abs(y).max() + 1e-6)
    return y.astype(np.float32)


def narracao():
    s = np.zeros((N, 2), np.float32)
    ir = ir_sala(1.2, .6, 6000, 3)
    info = []
    for i, (t0, txt, vel, tipo) in enumerate(FALAS):
        y = voz(txt, vel, tipo, i)
        g = .62 if tipo == "sussurro" else .8
        por(s, y, t0, g)
        info.append({"inicio": t0, "fim": round(t0 + len(y) / SR, 2), "texto": txt})
    s = reverb(s, ir, .12)
    json.dump(info, open(f"{OUT}/narracao_tempos.json", "w"), ensure_ascii=False, indent=1)
    return s, info


# ------------------------------------------------------------------ mistura
def envoltoria(x, ataque=.02, solta=.35):
    a = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    a = lp(a, 8)
    return np.clip(a / (a.max() + 1e-9), 0, 1)


def limitar(x, teto=.95):
    return np.tanh(x / teto) * teto


def misturar(mus, sfx, nar, com_musica=True, com_narracao=True):
    total = np.zeros((N, 2), np.float32)
    if com_narracao:
        env_n = envoltoria(nar)
        duck = 1 - .5 * np.clip(env_n * 4, 0, 1)
    else:
        duck = np.ones(N, np.float32)
    if com_musica:
        total += mus * .55 * duck[:, None]
    total += sfx * .45
    if com_narracao:
        total += nar * .95
    return limitar(total * 1.1)


if __name__ == "__main__":
    # sem narração (decisão do autor): os textos vão na tela; a trilha e os efeitos ocupam todo o espaço
    print("trilha…", flush=True); mus = trilha(); salvar("musica", mus)
    print("efeitos…", flush=True); sfx = efeitos(); salvar("efeitos", sfx)
    mus = mus / np.abs(mus).max(); sfx = sfx / np.abs(sfx).max()
    salvar("mix_completo", limitar((mus * .62 + sfx * .45) * 1.15), .9)
    salvar("mix_sem_musica", limitar(sfx * .8), .9)
    print("ok")
