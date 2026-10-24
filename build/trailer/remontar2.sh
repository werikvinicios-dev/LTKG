#!/bin/bash
# Refaz as cenas 5 (congelamento), 6 (livro) e 8 (gelo) e aplica os letreiros animados.
# 16:9: emenda as cenas novas na versão sem textos e aplica os letreiros por cima.
# 9:16: renderiza o vertical inteiro sem textos e aplica os letreiros por cima.
set -e
cd /home/user/LTKG/build/trailer
R=/home/user/LTKG/exportacoes/trailer
C=_cache/remonta2; mkdir -p $C
A=_cache/audio/mix_completo.wav
for c in "5 38.5 48.5" "6 48.5 57.5" "8 68.5 80.5"; do set -- $c
  [ -f $C/st_c$1.mp4 ] || SEM_TEXTO=1 python3 render.py 16x9 $C/st_c$1.mp4 - $2 $3
done
[ -f $C/vert_st.mp4 ] || SEM_TEXTO=1 python3 render.py 9x16 $C/vert_st.mp4 -
ffmpeg -v error -y -i $R/LMD_trailer_96s_1080p_sem_textos.mp4 -i $C/st_c5.mp4 -i $C/st_c6.mp4 -i $C/st_c8.mp4 -i $A -filter_complex \
"[0:v]trim=0:38.5,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[0:v]trim=57.5:68.5,setpts=PTS-STARTPTS[d];\
[3:v]setpts=PTS-STARTPTS[e];[0:v]trim=80.5:95.7,setpts=PTS-STARTPTS[f];[a][b][c][d][e][f]concat=n=6:v=1:a=0[v];[4:a]loudnorm=I=-16:TP=-1.5:LRA=14[au]" \
-map "[v]" -map "[au]" -c:v libx264 -crf 19 -maxrate 6.5M -bufsize 13M -preset medium -pix_fmt yuv420p -r 24 -c:a aac -b:a 320k -ar 48000 \
-movflags +faststart $C/sem_textos.mp4
python3 letreiros.py 16x9 $C/sem_textos.mp4 $C/oficial.mp4 $A
python3 letreiros.py 9x16 $C/vert_st.mp4 $C/vertical.mp4 $A
echo PRONTO
