"""Áudio do trailer com gravações reais: trilha tocada com a orquestra gravada do VSCO-2-CE e efeitos de bancos CC0
(BigSoundBank e Kenney), sincronizados com as cenas. Fontes e licenças: banco.py e exportacoes/trailer/audio/CREDITOS_SOM.md.
Gera stems separados em 48 kHz estéreo e as misturas (completa e sem música)."""
import math, os, wave
import numpy as np
from scipy import signal
import cenas as C
import amostras as A
from amostras import instrumento as I, acorde as AC, percussao as PC, tympano as TP, som as S, golpe as G

SR = 48000
DUR = 90.0
N = int(SR * DUR)
OUT = "/home/user/LTKG/build/trailer/_cache/audio"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(21)


# ------------------------------------------------------------------ util
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f / (SR / 2), "low", output="sos"), x, axis=0).astype(np.float32)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f / (SR / 2), "high", output="sos"), x, axis=0).astype(np.float32)


def por(buf, x, t, g=1.0, pan=0.0):
    """Coloca o som x (estéreo) em t segundos, com ganho e balanço (-1..1)."""
    i = int(t * SR)
    if i >= buf.shape[0] or x is None or len(x) == 0:
        return
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    l, r = math.cos((pan + 1) * math.pi / 4) * 1.414, math.sin((pan + 1) * math.pi / 4) * 1.414
    n = min(len(x), buf.shape[0] - i)
    buf[i:i + n, 0] += x[:n, 0] * g * l
    buf[i:i + n, 1] += x[:n, 1] * g * r


def longe(x, f=2200, k=.5):
    """Som distante: menos agudos e mais baixo."""
    return lp(x, f) * k


def ir_sala(dur=3.2, decai=2.6, tom=4500, seed=1):
    r = np.random.default_rng(seed)
    n = int(dur * SR); tt = np.arange(n) / SR
    e = np.exp(-tt * 6.9 / decai)
    ir = lp(np.stack([r.standard_normal(n) * e, r.standard_normal(n) * e], 1).astype(np.float32), tom)
    ir[:int(.012 * SR)] *= np.linspace(0, 1, int(.012 * SR))[:, None]
    return (ir / np.abs(ir).sum(0).max() * 8).astype(np.float32)


def reverb(x, ir, mix=.3):
    w = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in (0, 1)], 1)
    return (x * (1 - mix) + w * mix).astype(np.float32)


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


def limitar(x, teto=.95):
    return np.tanh(x / teto) * teto


# ------------------------------------------------------------------ trilha (tema em ré menor, orquestra gravada)
# TEMA: Ré–Fá–Mi–Lá(grave) / Ré–Fá–Sol–Lá–Si♭–Lá. Reaparece na flauta de Aurelia, nas trompas do confronto e no título.
TEMA_A = [(50, 1.6), (53, 1.2), (52, 1.2), (45, 2.6)]
TEMA_B = [(50, 1.0), (53, 1.0), (55, 1.0), (57, 1.4), (58, .9), (57, 2.2)]


def melodia(buf, naipe, tema, t, vel=.55, transp=0, ritmo=1.0, pan=0.0, liga=.35):
    for n_, d in tema:
        por(buf, I(naipe, n_ + transp, d * ritmo + liga, vel, solta=.9, ataque=.12), t, pan=pan)
        t += d * ritmo
    return t


def metais(notas, dur, vel=.9, ataque=.25):
    """Acorde de metais graves (trompas, trombone e tuba): o "braam" gravado."""
    partes = [AC("trompas", [n + 12 for n in notas], dur, vel, 1.2, ataque) * .9,
              AC("trombone", notas, dur, vel, 1.0, ataque), I("tuba", notas[0], dur, vel, 1.2, ataque) * .8]
    out = np.zeros((max(len(p) for p in partes), 2), np.float32)
    for p in partes:
        out[:len(p)] += p
    return out


def impacto(vel=1.0, nota=38):
    """Golpe orquestral: tímpano, bumbo sinfônico e um resto de gongo."""
    out = np.zeros((int(4 * SR), 2), np.float32)
    for p, g in ((TP(nota, vel), 1.0), (PC("BDrumNewhit_v7_*.wav" if vel > .7 else "BDrumNewhit_v4_*.wav"), .9),
                 (PC("gongHit_f.wav" if vel > .7 else "gongHit_p.wav"), .25)):
        n = min(len(p), len(out))
        out[:n] += p[:n] * g * vel
    return out


def trilha():
    m = np.zeros((N, 2), np.float32)
    ir = ir_sala(3.4, 3.0)
    # 07–25 mistério: violoncelos sobre um pedal grave, a cidade em silêncio
    por(m, I("contrabaixo", 38, 9.0, .35, 2.0, 3.0), 7.0)
    por(m, I("violoncelos", 45, 8.5, .25, 2.0, 3.0), 7.2, pan=.2)
    melodia(m, "violoncelos", TEMA_A, 8.0, .5, pan=-.15)
    por(m, AC("violas", [50, 57], 9.0, .3, 1.5, 1.5), 16.0, pan=.15)
    por(m, I("contrabaixo", 38, 9.0, .3, 1.5, 1.5), 16.0)
    harpa = [62, 64, 65, 67, 69, 70, 72]                       # uma nota de harpa para cada lei gravada
    for i, tl in enumerate(C.T_LEI):
        por(m, TP(38, .35), 16 + tl, pan=(i - 3) * .1)
        por(m, I("harpa", harpa[i], 2.2, .45, 1.2), 16 + tl, pan=(i - 3) * .12)
    por(m, I("violoncelos", 45, 3.2, .45, 1.0, .2), 21.8); por(m, I("violoncelos", 50, 2.5, .42, 1.0, .2), 24.0)
    # 25–54 tensão crescente: ostinato de cordas em spiccato e percussão grave
    b = 60 / 96
    for i in range(int((54 - 25) / (b / 2))):
        tt = 25 + i * b / 2
        nn = 38 if (i // 8) % 4 != 3 else 41
        intens = .3 + .5 * (tt - 25) / 29
        por(m, I("violoncelos_spic", nn + 12, .3, intens, .12), tt, pan=-.3)
        if i % 2 == 0:
            por(m, I("violinos_spic", nn + 19, .25, intens * .55, .1), tt + b / 4, pan=.3)
        if i % 4 == 0:
            por(m, I("contrabaixo_spic", nn, .35, .4 + .3 * (tt - 25) / 29, .15), tt)
        if i % 8 == 0 and tt > 30:
            por(m, TP(nn, .3 + .3 * (tt - 25) / 29), tt)
    por(m, AC("violas", [50, 53, 57], 10, .3, 2.0, 2.5), 25.0, pan=.1)
    melodia(m, "violoncelos", TEMA_B, 30.0, .58, pan=-.2)
    por(m, metais([38, 45, 50], 3.5, .95, .08), 40.45)          # primeira grande batida (congela)
    por(m, impacto(1.0), 40.45)
    por(m, PC("cymbal-crash1_mf_*.wav"), 40.45, .25)
    por(m, AC("violinos", [58, 62, 65], 8.5, .28, 2.0, 1.0), 45.5, pan=.15)
    por(m, AC("violoncelos", [46, 53], 8.5, .3, 2.0, 1.0), 45.5, pan=-.15)
    # 54–65 fascínio: a percussão sai; violinos agudos, harpa e o tema na flauta
    por(m, AC("violinos", [74, 77, 81], 10.8, .2, 2.5, 2.5), 54.2, pan=.2)
    por(m, AC("violas", [62, 69], 10.8, .18, 2.5, 2.5), 54.2, pan=-.2)
    for k in range(16):                                         # arpejo lento de harpa
        por(m, I("harpa", [62, 65, 69, 74][k % 4] + (12 if k % 8 > 3 else 0), 2.5, .3, 1.5), 54.6 + k * .62, pan=.35 * math.sin(k))
    melodia(m, "flauta", TEMA_A, 59.8, .42, transp=24, pan=.1, liga=.5)
    for k in range(5):
        por(m, PC("Glock/glock_medium_*.wav", .12, k % 6), 55.0 + k * 1.9, pan=rng.uniform(-.5, .5))
    por(m, PC("susCymb1-cresc-Median_v1.wav", .5), 61.6)
    por(m, PC("Timpani/Rolls/Timpani3_Roll_*.wav", .4), 62.2)
    # 65–77 confronto: orquestra inteira, cordas rápidas, percussão forte e o tema nas trompas
    b = 60 / 132
    seq = [38, 38, 50, 38, 41, 38, 50, 45]
    for i in range(int((77 - 65) / (b / 4))):
        tt = 65 + i * b / 4
        por(m, I("violinos_spic", seq[i % 8] + 24, .2, .5, .08), tt, pan=(-.4 if i % 2 else .4))
        if i % 2 == 0:
            por(m, I("violoncelos_spic", seq[i % 8] + 12, .25, .6, .1), tt, pan=-.2)
        if i % 4 == 0:
            por(m, TP(38 if (i // 16) % 2 == 0 else 41, .75 if i % 16 else 1.0), tt)
    for tc in C.CORTES08[:8]:
        por(m, impacto(1.0), 65 + tc)
        por(m, PC("Anvil_Hit1_v3_Sum.wav", .35), 65 + tc, pan=.2)
    por(m, metais([38, 45, 50], 2.5, .9), 65.0); por(m, metais([41, 48, 53], 2.5, .9), 70.5); por(m, metais([38, 45, 50], 2.8, 1.0), 73.6)
    por(m, AC("violinos_trem", [62, 65, 69], 12, .3, .8, .4), 65.0, pan=.25)
    por(m, AC("violoncelos_trem", [50, 57], 12, .35, .8, .4), 65.0, pan=-.25)
    melodia(m, "trompas", TEMA_B, 70.6, .8, transp=12, ritmo=.7, liga=.2)
    melodia(m, "violoncelos", TEMA_B, 70.6, .6, ritmo=.7, pan=-.2, liga=.2)
    por(m, PC("cymbal-crash1_ff_*.wav"), 73.6, .35)
    # 77–84 suspensão: a música corta (só um resto de reverberação)
    # 84–90 assinatura: cada peça da logo trava com um golpe; o halo fecha com a orquestra
    t0, tp = 84.0, C.T_PECAS
    por(m, impacto(.9, 38), t0 + tp["eixo"])
    por(m, I("contrabaixo", 38, 5.0, .35, 1.0, .6), t0 + tp["eixo"])
    por(m, TP(41, .6), t0 + tp["estandarte"])
    por(m, TP(45, .7), t0 + tp["arco"], pan=-.2); por(m, PC("Anvil_Hit1_v2_Sum.wav", .3), t0 + tp["arco"], pan=.2)
    por(m, TP(50, .75), t0 + tp["balanca"]); por(m, PC("BrakeDrum1_Hammer_v2_Sum.wav", .25), t0 + tp["balanca"])
    for i, tq in enumerate(C.T_PEROLAS):                         # as pérolas sobem o arpejo no glockenspiel
        por(m, A.transpor(PC("Glock/glock_medium_C6.wav", .32), [2, 5, 9, 14, 17, 21, 26][i] - 12), t0 + tq, pan=(i - 3) * .08)
    por(m, PC("susCymb1-cresc-Short_v1.wav", .35), t0 + tp["halo"] - 1.4)
    por(m, impacto(1.0, 38), t0 + tp["halo"]); por(m, PC("gongHit_fff.wav", .5), t0 + tp["halo"])
    por(m, PC("cymbal-crash1_ff_*.wav", .35), t0 + tp["halo"])
    por(m, metais([38, 45, 50, 53], 3.6, 1.0, .05), t0 + tp["halo"])
    a0, a1 = C.T_LETRAS
    harpa = [62, 65, 69, 72, 74, 77, 81, 84, 86, 89, 93, 96, 98, 101, 105]
    for k, nn in enumerate(harpa):                              # glissando de harpa enquanto as letras entram
        por(m, I("harpa", nn, 1.8, .3, 1.2), t0 + a0 + (a1 - a0) * k / (len(harpa) - 1), pan=-.5 + k / (len(harpa) - 1))
    melodia(m, "violinos", TEMA_A, t0 + 2.2, .4, transp=12, ritmo=.75, liga=.5)
    por(m, I("violoncelos", 38, 3.6, .5, 1.2, .1), t0 + tp["halo"])
    m = reverb(m, ir, .3)
    corte = int(77.05 * SR)                                     # suspensão: silêncio total
    m[corte:int(84 * SR)] *= np.concatenate([np.linspace(1, 0, int(.08 * SR)), np.zeros(int(84 * SR) - corte - int(.08 * SR))])[:, None]
    m[int(89.2 * SR):] *= np.linspace(1, 0, N - int(89.2 * SR))[:, None]
    return m


# ------------------------------------------------------------------ efeitos sonoros (gravações)
def vento(ini, dur, vel=.4, forte=False, entra=1.0, sai=1.0):
    return S("0625" if forte else "0595", ini, dur, vel, entra, sai)


def efeitos():
    s = np.zeros((N, 2), np.float32)
    ir = ir_sala(2.2, 1.8, 6000, 3)
    # 01 o primeiro som: um fio sob tensão, a gota no aço
    por(s, PC("susCymb1-bow-2.wav", .25), .6, pan=-.2)                    # fio vibrando (prato friccionado com arco)
    por(s, S("0725", 0, 2.5, .5), .5, pan=-.2)
    por(s, PC("susCymb1-bow-3.wav", .35), 3.0, pan=.2)
    por(s, S("0725", 0, 2.5, .6), 3.0, pan=.2)
    por(s, G("1383", 3, .9, .9), 5.62)                                   # a gota
    por(s, PC("TB_hit_C5_v4_rr1.wav", .18), 5.62)
    por(s, vento(20, 6, .12, entra=1.2), 1.0)
    # 02 a cidade: vento entre as casas e um sino ao longe
    por(s, vento(10, 9, .45, True, 1.5), 7.0)
    por(s, longe(G("0135", 0, 4.0), 1800, .35), 9.2, pan=.5); por(s, longe(G("0135", 1, 4.0), 1500, .25), 12.8, pan=-.5)
    por(s, vento(40, 1.4, .5, True, .3, .6), 11.0)
    # 03 as leis: cada símbolo é gravado na matéria
    for i, tl in enumerate(C.T_LEI):
        pan = (i - 3) * .12
        por(s, G("0833", i, .5, .45), 16 + tl, pan=pan)                   # lâmina riscando metal
        por(s, S(f"impactMetal_light_00{i % 5}", vel=.35), 16 + tl, pan=pan)
    por(s, G("3426", 2, 1.2, .35), 16 + C.T_LEI[1])                      # tensão de corda
    por(s, G("2209", 4, .8, .5), 16 + C.T_LEI[3] + .15)                  # gelo estalando
    por(s, S("2131", 0, 1.4, .4), 16 + C.T_LEI[5])                       # o calor acende
    por(s, vento(55, 1.4, .45, False, .3, .6), 16 + C.T_LEI[6] + .6)
    # 04 Ilan: vento, a manopla, respiração
    por(s, vento(30, 10, .35, entra=1.0), 25.0)
    por(s, G("0359", 0, 1.6, .4), 25.4, pan=-.3)                         # metal da manopla
    for k in range(3):
        por(s, S("1404", 2.6, 1.6, .22), 31.8 + k * 3.2)
    # 05 a ponte: nevasca, tecido, o congelamento
    por(s, vento(50, 5.8, .75, True, .4), 35.0)
    for k in range(5):
        por(s, S("0399", 2 + k * 3.1, .9, .35, .1, .3), 35.4 + k * 1.0, pan=rng.uniform(-.5, .5))   # casaco ao vento
    for k in range(6):
        por(s, S(f"footstep_snow_00{k % 5}", vel=.35), 35.6 + k * .62, pan=-.1)
    por(s, G("1022", 1, 1.8, .7), 40.45)                                 # o golpe que congela
    por(s, G("0148", 0, 1.6, .5), 40.5); por(s, G("2209", 9, 1.2, .5), 40.6)
    por(s, G("0785", 2, 1.2, .3), 41.0)
    # 06 os rostos: papel, engrenagens, o estandarte, o livro, passos
    por(s, S("0164", vel=.45), 45.2); por(s, G("0785", 4, .8, .3), 46.8)
    por(s, S("1567", 1.0, 1.9, .35, .05, .3), 48.0); por(s, G("0378", 3, .6, .35), 48.2)
    por(s, S("2131", 0, 1.0, .35), 48.6)                                  # faísca no instrumento de Nara
    por(s, S("0399", 9.0, 1.0, .6, .05, .3), 49.8)                         # o estandarte
    por(s, S("bookFlip2", vel=.4), 50.65)
    por(s, S("bookClose", vel=.9), 51.22); por(s, S("1588", vel=.45), 51.22)   # o livro se fecha com firmeza
    for k in range(5):
        por(s, G("0606", k, .7, .25), 52.0 + k * .45, pan=(k - 2) * .15)
    # 07 Aurelia: quase silêncio, brilhos finos, respiração
    for k in range(6):
        por(s, PC("Triangle3-HitM_v1_*.wav", .06), 54.4 + k * 1.7, pan=rng.uniform(-.6, .6))
    por(s, PC("BellTree_Stroke2_v1_Sum.wav", .12), 56.2, pan=.3)
    por(s, S("1404", 2.6, 1.8, .18), 61.5)
    # 08 o impossível
    por(s, S("0725", 0, 1.4, .6), 65.0); por(s, G("0616", 3, 1.0, .35), 65.0)
    por(s, vento(60, .8, .55, True, .1, .3), 66.3); por(s, S("0128", vel=.6), 66.3)
    por(s, G("3426", 5, 1.3, .4), 67.7)
    por(s, G("0148", 1, 1.6, .8), 69.0); por(s, G("2209", 15, 1.2, .6), 69.1)   # o gelo parte
    por(s, S("drawKnife2", vel=.7), 70.3); por(s, S("0129", vel=.8), 70.5); por(s, S("0128", vel=.6), 70.5)
    por(s, G("1022", 3, 1.6, .9), 72.12); por(s, G("0148", 3, 1.2, .5), 72.2); por(s, vento(70, 1.2, .6, True, .1, .5), 72.15)
    por(s, G("0616", 7, 1.5, .45), 73.6); por(s, S("impactPlate_heavy_002", vel=.5), 73.6)
    por(s, S("1404", 2.6, 1.3, .25), 75.3)
    # 09 a pergunta: vento e respiração
    por(s, vento(5, 6.8, .3, entra=.3, sai=.5), 77.0); por(s, S("2195", 10, 1.8, .2, .2, .4), 79.6)
    # 10 título: o som de cada peça da logo travando no lugar
    t0, tp = 84.0, C.T_PECAS
    por(s, S("0128", vel=.5), t0 + tp["eixo"] - .3)                       # a espada caindo
    por(s, S("impactMetal_heavy_001", vel=.9), t0 + tp["eixo"]); por(s, G("1022", 5, 1.2, .5), t0 + tp["eixo"])
    por(s, S("cloth3", vel=.6), t0 + tp["estandarte"] - .35); por(s, S("0399", 9.0, .6, .4, .05, .2), t0 + tp["estandarte"] - .3)
    por(s, S("impactMetal_heavy_002", vel=.8), t0 + tp["arco"], pan=-.5); por(s, S("impactMetal_heavy_003", vel=.8), t0 + tp["arco"] + .015, pan=.5)
    por(s, G("0619", 4, .6, .45), t0 + tp["balanca"] - .1); por(s, S("impactPlate_heavy_000", vel=.6), t0 + tp["balanca"])
    for i, tq in enumerate(C.T_PEROLAS):
        por(s, S(f"impactGlass_light_00{i % 5}", vel=.25), t0 + tq, pan=(i - 3) * .08)
    por(s, S("0128", vel=.5), t0 + tp["halo"] - .25)
    por(s, S("impactBell_heavy_000", vel=.9), t0 + tp["halo"]); por(s, S("impactMetal_heavy_004", vel=.9), t0 + tp["halo"])
    centros = C.letras_titulo()[1]
    a0, a1 = C.T_LETRAS
    for k, (cx, cy) in enumerate(centros):
        por(s, S(f"impactMetal_light_00{k % 5}", vel=.18), t0 + a0 + (a1 - a0) * k / max(1, len(centros) - 1), pan=(cx - 512) / 600)
    return reverb(s, ir, .18)


if __name__ == "__main__":
    print("trilha…", flush=True); mus = trilha(); salvar("musica", mus)
    print("efeitos…", flush=True); sfx = efeitos(); salvar("efeitos", sfx)
    mus = mus / np.abs(mus).max(); sfx = sfx / np.abs(sfx).max()
    salvar("mix_completo", limitar((mus * .62 + sfx * .45) * 1.15), .9)
    salvar("mix_sem_musica", limitar(sfx * .8), .9)
    print("ok")
