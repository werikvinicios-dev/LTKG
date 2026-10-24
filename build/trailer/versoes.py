"""Versões derivadas do trailer: teasers de 30 s e 15 s (recortes que não partem os letreiros), versão sem música,
trilha e efeitos separados, e a lista de planos (EDL) em JSON para remontagem."""
import json, os, subprocess, sys
import cenas as C

R = "/home/user/LTKG/exportacoes/trailer"
A = "/home/user/LTKG/build/trailer/_cache/audio"
MESTRE = f"{R}/LMD_trailer_oficial_90s_1080p.mp4"
SEM_TEXTO = f"{R}/LMD_trailer_90s_1080p_sem_textos.mp4"
LN = "loudnorm=I=-16:TP=-1.5:LRA=14"

TEASER30 = [(7.9, 11.45), (30.2, 34.8), (36.3, 40.45), (40.45, 43.0), (60.4, 64.9), (65.0, 72.5), (84.0, 87.5)]
TEASER15 = [(36.3, 40.45), (65.0, 70.5), (84.0, 89.4)]


def run(cmd):
    subprocess.run(cmd, check=True)


def recorte(video, audio, partes, saida, xf=.06):
    """Junta trechos do vídeo e do áudio com microfusões de áudio (sem estalos nos cortes)."""
    fc = []
    for i, (a, b) in enumerate(partes):
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={xf},afade=t=out:st={b - a - xf}:d={xf}[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(partes))) + f"concat=n={len(partes)}:v=1:a=1[v][aa]")
    fc.append(f"[aa]{LN}[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", audio, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
         "-movflags", "+faststart", saida])


def trocar_audio(video, audio, saida):
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-af", LN, "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", saida])


def wav_final(entrada, saida):
    run(["ffmpeg", "-v", "error", "-y", "-i", entrada, "-af", LN, "-ar", "48000", "-c:a", "pcm_s24le", saida])


EDL = [
    (0.0, 7.0, "01 O primeiro som", "procedural: fio de prata, gota, aço escovado", "plano fixo, revelação lenta"),
    (7.0, 11.45, "02a Vhalessa", "05_mundo/MU-009 (4x)", "travelling 2.5D para dentro da rua; neve, fumaça, janelas"),
    (11.45, 16.0, "02b O rio e a torre", "11_edicao/C02-2", "panorâmica lateral com parallax"),
    (16.0, 25.0, "03 As sete leis", "identidade_aresta/simbolos/leis/*", "gravação progressiva + fenômeno físico de cada lei"),
    (25.0, 35.0, "04 Ilan Varek", "06_personagens/PE-001 (4x)", "close na manopla (antebraço esquerdo) e tilt até o rosto"),
    (35.0, 40.45, "05a A ponte", "06_personagens/PE-025 (4x)", "acompanhamento lateral na nevasca"),
    (40.45, 45.0, "05b O último carrasco", "PE-025 + simbolos/instituicoes/ordem_da_ultima_sentenca", "congela e vira gravura"),
    (45.0, 48.0, "06a Mara Quen", "06_personagens/PE-003 (4x)", "tilt da escrita ao rosto; close nos olhos"),
    (48.0, 49.8, "06b Nara Voss", "06_personagens/PE-029", "instrumento, faíscas"),
    (49.8, 50.6, "06c Estandarte", "04_objetos/OB-004", "transição por objeto"),
    (50.6, 51.8, "06d O livro", "08_editorial/ED-001 + ED-003 (couro)", "o livro se fecha com firmeza"),
    (51.8, 54.0, "06e Silhuetas", "06_personagens/PE-006", "push-in com raios de luz"),
    (54.0, 56.2, "07a Luz dourada", "05_mundo/MU-007", "raios volumétricos"),
    (56.2, 59.6, "07b Tecido e mão", "06_personagens/PE-013", "véu ao vento"),
    (59.6, 65.0, "07c Aurelia", "06_personagens/PE-012 (4x)", "tilt de revelação; cabelo ao vento"),
    (65.0, 77.0, "08 O impossível", "procedural + PE-021, PE-001, PE-025, C01-a, C01-c", "8 cortes na percussão"),
    (77.0, 83.7, "09 A pergunta", "09_engenharia_arcana/EA-006", "push-in lento; silêncio; corte para preto"),
    (84.0, 90.0, "10 Título", "01_identidade/ID-008 + ID-006", "reflexo metálico; crédito do autor"),
]

if __name__ == "__main__":
    os.makedirs(R, exist_ok=True)
    quais = sys.argv[1:] or ["teasers", "sem_musica", "stems", "edl"]
    if "teasers" in quais:
        recorte(MESTRE, f"{A}/mix_completo.wav", TEASER30, f"{R}/LMD_teaser_30s_1080p.mp4")
        recorte(MESTRE, f"{A}/mix_completo.wav", TEASER15, f"{R}/LMD_teaser_15s_1080p.mp4")
    if "sem_musica" in quais:
        trocar_audio(MESTRE, f"{A}/mix_sem_musica.wav", f"{R}/LMD_trailer_90s_1080p_sem_musica.mp4")
    if "stems" in quais:
        os.makedirs(f"{R}/audio", exist_ok=True)
        wav_final(f"{A}/musica.wav", f"{R}/audio/LMD_trilha_original.wav")
        wav_final(f"{A}/efeitos.wav", f"{R}/audio/LMD_efeitos_sonoros.wav")
        wav_final(f"{A}/mix_completo.wav", f"{R}/audio/LMD_mix_final.wav")
    if "edl" in quais:
        json.dump({"duracao": 90.0, "fps": 24, "formato": "1920x1080",
                   "planos": [dict(zip(("inicio", "fim", "plano", "fonte", "movimento"), p)) for p in EDL],
                   "letreiros": [{"inicio": a, "fim": b, "linhas": l} for a, b, l, _, _ in C.LETREIROS],
                   "teaser_30s": TEASER30, "teaser_15s": TEASER15},
                  open(f"{R}/LMD_trailer_linha_do_tempo.json", "w"), ensure_ascii=False, indent=1)
    print("ok")
