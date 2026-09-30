#!/usr/bin/env bash
# Xera un reel vertical 1080x1920 a partir dun vídeo horizontal do festival.
# Uso: make_reel.sh <input.mp4> <inicio_seg> <duracion_seg> <texto_gancho> <texto_pe> <output.mp4>
set -euo pipefail

INPUT="$1"
START="$2"
DUR="$3"
HOOK="$4"
CAPTION="$5"
OUTPUT="$6"

FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

ffmpeg -y -ss "$START" -t "$DUR" -i "$INPUT" -filter_complex "\
[0:v]split=2[bg][fg]; \
[bg]scale=1080:1920,gblur=sigma=30,eq=brightness=-0.15[bgblur]; \
[fg]scale=1080:-1,setsar=1[fgscaled]; \
[bgblur][fgscaled]overlay=(W-w)/2:(H-h)/2[vid]; \
[vid]drawtext=fontfile=${FONT}:text='${HOOK}':fontcolor=white:fontsize=64:borderw=3:bordercolor=black:x=(w-text_w)/2:y=140:enable='between(t,0,2.5)', \
drawtext=fontfile=${FONT}:text='${CAPTION}':fontcolor=white:fontsize=34:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-160[out]" \
-map "[out]" -map 0:a -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -pix_fmt yuv420p "$OUTPUT" -loglevel error

echo "Reel creado: $OUTPUT"
