#!/usr/bin/env bash
# Comproba que o IG_ACCESS_TOKEN funciona lendo os datos básicos da conta.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Falta o ficheiro .env (copia .env.example e enche os valores)." >&2
  exit 1
fi
set -a
source .env
set +a

if [ -z "${IG_ACCESS_TOKEN:-}" ] || [ -z "${IG_USER_ID:-}" ]; then
  echo "IG_ACCESS_TOKEN ou IG_USER_ID non están definidos en .env" >&2
  exit 1
fi

curl -s -G "https://graph.facebook.com/v21.0/${IG_USER_ID}" \
  --data-urlencode "fields=id,username,media_count" \
  --data-urlencode "access_token=${IG_ACCESS_TOKEN}"
echo
