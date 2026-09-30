#!/usr/bin/env bash
# Troca o IG_SHORT_TOKEN (curta duración) por un token de longa duración (60 días)
# e escribe o resultado como IG_ACCESS_TOKEN en .env.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Falta o ficheiro .env" >&2
  exit 1
fi
set -a
source .env
set +a

if [ -z "${IG_SHORT_TOKEN:-}" ] || [ -z "${APP_ID:-}" ] || [ -z "${APP_SECRET:-}" ]; then
  echo "Faltan IG_SHORT_TOKEN, APP_ID ou APP_SECRET en .env" >&2
  exit 1
fi

RESPONSE=$(curl -s -G "https://graph.facebook.com/v21.0/oauth/access_token" \
  --data-urlencode "grant_type=fb_exchange_token" \
  --data-urlencode "client_id=${APP_ID}" \
  --data-urlencode "client_secret=${APP_SECRET}" \
  --data-urlencode "fb_exchange_token=${IG_SHORT_TOKEN}")

echo "Resposta da API:"
echo "$RESPONSE"

LONG_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$LONG_TOKEN" ]; then
  echo "Non se puido extraer o token longo. Revisa a resposta de arriba." >&2
  exit 1
fi

# Actualiza IG_ACCESS_TOKEN en .env (crea a liña se non existe)
if grep -q '^IG_ACCESS_TOKEN=' .env; then
  sed -i "s|^IG_ACCESS_TOKEN=.*|IG_ACCESS_TOKEN=${LONG_TOKEN}|" .env
else
  echo "IG_ACCESS_TOKEN=${LONG_TOKEN}" >> .env
fi

echo
echo "Feito. IG_ACCESS_TOKEN actualizado en .env (token de ~60 días)."
