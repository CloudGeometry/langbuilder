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

# Set data directory and create if it doesn't exist
export DATA_DIR=./data
mkdir -p "$DATA_DIR"

# Detect OS and set Python path
case "$OSTYPE" in
  msys*|cygwin*|win32)
    PYTHON_PATH="../.venv/Scripts/python.exe"
    ;;
  *)
    PYTHON_PATH="../.venv/bin/python"
    ;;
esac

# Start OpenWebUI
$PYTHON_PATH -m uvicorn open_webui.main:app \
  --host 0.0.0.0 \
  --port ${OPEN_WEBUI_PORT:-8767}
