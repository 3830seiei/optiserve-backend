#!/usr/bin/env bash
# optiserve-backend/docker/entrypoint.dev.sh
set -euo pipefail
set -euxo pipefail

# Ensure data dirs exist (in case env overrides the defaults)
mkdir -p "${REPORTS_DIR:-/data/reports}" "${UPLOADS_DIR:-/data/uploads}" /data

# smds_core dependency removed - using standard logging

# Sync backend runtime deps at container start (handy during dev)
if [ -f /app/requirements.txt ]; then
	  pip install --no-cache-dir --root-user-action=ignore -r /app/requirements.txt
fi

# Make sure locale/timezone are in effect (optional)
export LANG="${LANG:-ja_JP.UTF-8}" TZ="${TZ:-Asia/Tokyo}"

# Start API (only app reload-dir needed now)
exec uvicorn \
  --host 0.0.0.0 --port 8000 \
  --reload --reload-dir /app \
  src.main:app

