#!/usr/bin/env bash
# Realza lixeiramente unha foto (máis cor, máis contraste, ton máis cálido)
# para que as fotos de territorio luzan máis vivas e atractivas.
# Uso: enhance_photo.sh <input> <output>
set -euo pipefail
INPUT="$1"
OUTPUT="$2"

convert "$INPUT" \
  -modulate 103,120,100 \
  -brightness-contrast 3x12 \
  -auto-gamma \
  "$OUTPUT"

echo "Realzada: $OUTPUT"
