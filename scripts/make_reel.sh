#!/usr/bin/env bash
# Recorta un fragmento dun vídeo do festival e engade texto, mantendo a
# resolución e proporción orixinais do vídeo (sen bandas difuminadas).
# Uso: make_reel.sh <input.mp4> <inicio_seg> <duracion_seg> <texto_gancho> <texto_pe> <output.mp4>
set -euo pipefail

INPUT="$1"
START="$2"
DUR="$3"
HOOK="$4"
CAPTION="$5"
OUTPUT="$6"

FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

ffmpeg -y -ss "$START" -t "$DUR" -i "$INPUT" -vf "\
drawtext=fontfile=${FONT}:text='${HOOK}':fontcolor=white:fontsize=48:borderw=3:bordercolor=black:x=(w-text_w)/2:y=60:enable='between(t,0,2.5)', \
drawtext=fontfile=${FONT}:text='${CAPTION}':fontcolor=white:fontsize=26:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-70" \
-c:v libx264 -profile:v main -level 3.1 -preset medium -crf 20 -c:a aac -b:a 192k -pix_fmt yuv420p -movflags +faststart "$OUTPUT" -loglevel error

echo "Reel creado: $OUTPUT"
