#!/usr/bin/env bash
# Monta un reel a partir de varias fotos (zoom lento, tipo "Ken Burns") + música libre,
# con transicións de fundido suaves entre fotos (evita calquera corte brusco).
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
N=${#IMAGES[@]}
TRANS="0.8"  # segundos de fundido entre fotos
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Paso 1: cada imaxe nun clip independente, con zoom lento (zoompan illado por proceso).
CLIPS=()
i=0
for IMG in "${IMAGES[@]}"; do
  OUT="$TMPDIR/clip_$i.mp4"
  ffmpeg -y -loop 1 -i "$IMG" \
    -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,zoompan=z='min(zoom+0.0010,1.18)':d=${FRAMES}:s=1280x720:fps=${FPS},setsar=1" \
    -frames:v "$FRAMES" -c:v libx264 -pix_fmt yuv420p "$OUT" -loglevel error
  CLIPS+=("$OUT")
  i=$((i + 1))
done

# Paso 2: unir os clips con fundidos encadeados (xfade), engadir texto e música.
INPUTS=()
for CLIP in "${CLIPS[@]}"; do
  INPUTS+=(-i "$CLIP")
done
INPUTS+=(-i "$MUSIC")

FILTER=""
PREV="[0:v]"
OFFSET=0
for i in $(seq 1 $((N - 1))); do
  OFFSET=$(LC_NUMERIC=C awk "BEGIN{printf \"%.3f\", $i*($SEC_PER_IMG-$TRANS)}")
  NEXTLABEL="[x${i}]"
  if [ "$i" -eq $((N - 1)) ]; then NEXTLABEL="[vcat]"; fi
  FILTER+="${PREV}[${i}:v]xfade=transition=fade:duration=${TRANS}:offset=${OFFSET}${NEXTLABEL}; "
  PREV="[x${i}]"
done
TOTAL_DUR=$(LC_NUMERIC=C awk "BEGIN{printf \"%.3f\", $N*$SEC_PER_IMG-($N-1)*$TRANS}")

FILTER+="[vcat]drawtext=fontfile=${FONT}:text='${HOOK}':fontcolor=white:fontsize=48:borderw=3:bordercolor=black:x=(w-text_w)/2:y=60:enable='between(t,0,2.5)', "
FILTER+="drawtext=fontfile=${FONT}:text='${CAPTION}':fontcolor=white:fontsize=26:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-70[v]; "
FADE_OUT_ST=$(LC_NUMERIC=C awk "BEGIN{printf \"%.3f\", $TOTAL_DUR-2}")
FILTER+="[${N}:a]afade=t=in:st=0:d=1,afade=t=out:st=${FADE_OUT_ST}:d=2[a]"

ffmpeg -y "${INPUTS[@]}" -filter_complex "$FILTER" \
  -map "[v]" -map "[a]" -t "$TOTAL_DUR" \
  -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -pix_fmt yuv420p \
  "$OUTPUT" -loglevel error

echo "Reel de fotos creado: $OUTPUT (${TOTAL_DUR}s)"
