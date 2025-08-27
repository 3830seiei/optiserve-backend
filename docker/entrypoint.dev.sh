#!/usr/bin/env bash
# optiserve-backend/docker/entrypoint.dev.sh
set -euo pipefail
set -euxo pipefail

# Ensure data dirs exist (in case env overrides the defaults)
mkdir -p "${REPORTS_DIR:-/data/reports}" "${UPLOADS_DIR:-/data/uploads}" /data

# Editable install for smds_core if mounted; ignore if absent
if [ -d /smds_core ]; then
	  pip install --no-cache-dir --root-user-action=ignore -e /smds_core
fi

# Sync backend runtime deps at container start (handy during dev)
if [ -f /app/requirements.txt ]; then
	  pip install --no-cache-dir --root-user-action=ignore -r /app/requirements.txt
fi

# Make sure locale/timezone are in effect (optional)
export LANG="${LANG:-ja_JP.UTF-8}" TZ="${TZ:-Asia/Tokyo}"

# Star API (add reload-dirs for both codebases)
exec uvicorn \
  --host 0.0.0.0 --port 8000 \
  --reload --reload-dir /app --reload-dir /smds_core \
  src.main:app

