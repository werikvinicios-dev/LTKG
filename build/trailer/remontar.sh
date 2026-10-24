#!/bin/bash
# Remonta o trailer: renderiza só as cenas refeitas (1, 3, 5 e 10) e emenda com os trechos que não mudaram
# dos masters anteriores (montagem de 90 s). Uso: bash remontar.sh
set -e
cd /home/user/LTKG/build/trailer
R=/home/user/LTKG/exportacoes/trailer
C=_cache/remonta; mkdir -p $C
A=_cache/audio/mix_completo.wav
cenas() {  # $1 formato, $2 prefixo, resto: variáveis de ambiente
  for c in "1 0 7" "3 16 28.5" "5 38.5 48.5" "10 87.5 95.7"; do
    set -- $c; n=$1; a=$2; b=$3
    [ -f $C/${FMT}${SUF}_c$n.mp4 ] || python3 render.py $FMT $C/${FMT}${SUF}_c$n.mp4 - $a $b
  done
}
FMT=16x9 SUF= cenas
FMT=9x16 SUF= cenas
for n in "3 16 28.5" "5 38.5 48.5"; do set -- $n; [ -f $C/16x9st_c$1.mp4 ] || SEM_TEXTO=1 python3 render.py 16x9 $C/16x9st_c$1.mp4 - $2 $3; done
cp -n $C/16x9_c1.mp4 $C/16x9st_c1.mp4; cp -n $C/16x9_c10.mp4 $C/16x9st_c10.mp4
emenda() {  # $1 master antigo, $2 prefixo das cenas novas, $3 saída
  ffmpeg -v error -y -i $2_c1.mp4 -i "$1" -i $2_c3.mp4 -i $2_c5.mp4 -i $2_c10.mp4 -i $A -filter_complex \
  "[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=7:16,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[1:v]trim=25:35,setpts=PTS-STARTPTS[d];\
[3:v]setpts=PTS-STARTPTS[e];[1:v]trim=45:84,setpts=PTS-STARTPTS[f];[4:v]setpts=PTS-STARTPTS[g];[a][b][c][d][e][f][g]concat=n=7:v=1:a=0[v];\
[5:a]loudnorm=I=-16:TP=-1.5:LRA=14[au]" -map "[v]" -map "[au]" -c:v libx264 -crf 19 -maxrate 6.5M -bufsize 13M -preset medium \
  -pix_fmt yuv420p -r 24 -c:a aac -b:a 320k -ar 48000 -movflags +faststart "$3"
}
emenda $R/LMD_trailer_oficial_90s_1080p.mp4 $C/16x9 $C/oficial.mp4 &
emenda $R/LMD_trailer_90s_1080p_sem_textos.mp4 $C/16x9st $C/sem_textos.mp4 &
emenda $R/LMD_trailer_90s_vertical_1080x1920.mp4 $C/9x16 $C/vertical.mp4 &
wait
echo EMENDAS_OK
