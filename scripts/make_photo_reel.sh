#!/usr/bin/env bash
# Monta un reel a partir de varias fotos (zoom lento, tipo "Ken Burns") + música libre.
# As imaxes pásanse coma unha lista separada por "|". Inclúe sempre polo menos
# unha foto do festival entre as de territorio (regra do CLAUDE.md).
#
# Uso: make_photo_reel.sh "<img1>|<img2>|<img3>|..." <musica.mp3> <seg_por_imaxe> \
#        <texto_gancho> <texto_pe> <output.mp4>
set -euo pipefail

IFS='|' read -ra IMAGES <<< "$1"
MUSIC="$2"
SEC_PER_IMG="$3"
HOOK="$4"
CAPTION="$5"
OUTPUT="$6"

FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FPS=25
FRAMES=$(( SEC_PER_IMG * FPS ))
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

i=0
LIST_FILE="$TMPDIR/list.txt"
: > "$LIST_FILE"
for IMG in "${IMAGES[@]}"; do
  OUT="$TMPDIR/clip_$i.mp4"
  ffmpeg -y -loop 1 -i "$IMG" \
    -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,zoompan=z='min(zoom+0.0010,1.18)':d=${FRAMES}:s=1280x720:fps=${FPS}" \
    -frames:v "$FRAMES" -c:v libx264 -pix_fmt yuv420p "$OUT" -loglevel error
  echo "file '$OUT'" >> "$LIST_FILE"
  i=$((i + 1))
done

CONCAT="$TMPDIR/concat.mp4"
ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c copy "$CONCAT" -loglevel error

TOTAL_DUR=$(( ${#IMAGES[@]} * SEC_PER_IMG ))

ffmpeg -y -i "$CONCAT" -i "$MUSIC" -t "$TOTAL_DUR" -filter_complex "\
[0:v]drawtext=fontfile=${FONT}:text='${HOOK}':fontcolor=white:fontsize=48:borderw=3:bordercolor=black:x=(w-text_w)/2:y=60:enable='between(t,0,2.5)', \
drawtext=fontfile=${FONT}:text='${CAPTION}':fontcolor=white:fontsize=26:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-70[v]; \
[1:a]afade=t=in:st=0:d=1,afade=t=out:st=${TOTAL_DUR}:d=1.5[a]" \
-map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -shortest -pix_fmt yuv420p "$OUTPUT" -loglevel error

echo "Reel de fotos creado: $OUTPUT"
