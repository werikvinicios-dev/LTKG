"""Aplica os letreiros animados (cenas.letreiro) sobre um vídeo sem textos, quadro a quadro, e junta o áudio.
Uso: python3 letreiros.py <16x9|9x16> entrada_sem_textos.mp4 saida.mp4 audio.wav"""
import subprocess, sys
import numpy as np
import base as B, cenas as C

fmt, ent, sai, audio = sys.argv[1:5]
if fmt == "9x16":
    B.formato(1080, 1920)
W, H = B.W, B.H
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", ent, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                        "-i", audio, "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-16:TP=-1.5:LRA=14",
                        "-c:v", "libx264", "-crf", "19", "-maxrate", "6.5M", "-bufsize", "13M", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", sai], stdin=subprocess.PIPE)
n = W * H * 3
i = 0
while True:
    buf = dec.stdout.read(n)
    if len(buf) < n:
        break
    t = i / 24
    if any(a <= t < b for a, b, *_ in C.LETREIROS):
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        buf = B.para_u8(C.letreiro(img, t)).tobytes()
    enc.stdin.write(buf)
    i += 1
enc.stdin.close(); enc.wait(); dec.wait()
print("ok", i, "quadros")
