#!/bin/sh
set -eu

if [ "${SEED_CATALOG_ON_START:-false}" = "true" ]; then
    python manage.py seed_catalog
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 30 \
    --error-logfile -
