#!/bin/sh
set -eu

: "${FRONTEND_URL:?Set FRONTEND_URL to the deployed storefront origin.}"
: "${BACKEND_URL:?Set BACKEND_URL to the deployed backend origin.}"

frontend_url=${FRONTEND_URL%/}
backend_url=${BACKEND_URL%/}

curl --fail --silent --show-error --location --max-time 15 "${frontend_url}/" >/dev/null
curl --fail --silent --show-error --max-time 10 "${backend_url}/health/live/" \
  | grep --fixed-strings '"status": "ok"' >/dev/null
curl --fail --silent --show-error --max-time 10 "${backend_url}/health/ready/" \
  | grep --fixed-strings '"status": "ok"' >/dev/null

echo "BeanCo deployment smoke checks passed."
