#!/usr/bin/env bash

cd "$(dirname "$0")" || exit

# Disable filename expansion (globbing) before loading .env
set -f

# Load .env from project root
set -a
source ../../.env
set +a

# Re-enable filename expansion
set +f

# Set data directory
export DATA_DIR=./data

# Start OpenWebUI
../.venv/Scripts/python.exe -m uvicorn open_webui.main:app \
  --host 0.0.0.0 \
  --port ${OPEN_WEBUI_PORT:-8767}
