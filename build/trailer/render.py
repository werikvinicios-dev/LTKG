"""Renderiza o trailer em paralelo (um processo por trecho) e junta com o áudio.
uso: python3 render.py <formato 16x9|9x16> <saida.mp4> [audio.wav] [t0 t1]"""
import os, sys, subprocess, multiprocessing as mp
import numpy as np

TMP = "/home/user/LTKG/build/trailer/_frames"


def trecho(args):
    fmt, i0, i1, saida = args
    import base as B, cenas as C
    if fmt == "9x16":
        B.formato(1080, 1920)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{B.W}x{B.H}", "-r", "24", "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", saida], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(B.para_u8(C.quadro(i / 24, textos=os.environ.get('SEM_TEXTO') != '1')).tobytes())
        if (i - i0) % 120 == 0:
            print(f"[{os.getpid()}] {i}/{i1}", flush=True)
    p.stdin.close(); p.wait()
    return saida


if __name__ == "__main__":
    fmt, saida = sys.argv[1], sys.argv[2]
    audio = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    t0, t1 = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (0.0, 90.0)
    os.makedirs(TMP, exist_ok=True)
    f0, f1 = int(t0 * 24), int(t1 * 24)
    n = 4
    cortes = np.linspace(f0, f1, n + 1).astype(int)
    partes = [(fmt, int(cortes[k]), int(cortes[k + 1]), f"{TMP}/{fmt}_{k}.mp4") for k in range(n)]
    with mp.get_context("spawn").Pool(n) as pool:
        arqs = pool.map(trecho, partes)
    lista = f"{TMP}/{fmt}_lista.txt"
    open(lista, "w").write("".join(f"file '{a}'\n" for a in arqs))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista]
    if audio:
        cmd += ["-ss", str(t0), "-t", str(t1 - t0), "-i", audio, "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-16:TP=-1.5:LRA=14",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", saida]
    subprocess.run(cmd, check=True)
    print("ok", saida)
