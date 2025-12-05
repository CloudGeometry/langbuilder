#!/usr/bin/env bash

# OpenWebUI Backend Startup Script - macOS Version
# This script starts the OpenWebUI backend using the macOS Python venv path

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit

# Load only essential variables from .env
ENV_FILE="$SCRIPT_DIR/../../.env"
if [ -f "$ENV_FILE" ]; then
    # Only extract OPEN_WEBUI_PORT safely
    BACKEND_PORT=$(grep '^OPEN_WEBUI_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
fi

# Default to 8767 if not set
BACKEND_PORT="${BACKEND_PORT:-8767}"

# Set data directory
export DATA_DIR="$SCRIPT_DIR/data"

# Ensure data directory exists
mkdir -p "$DATA_DIR"

echo "Starting OpenWebUI backend on port $BACKEND_PORT..."

# Start OpenWebUI using macOS venv path
# Use uvicorn directly instead of python -m uvicorn
"$SCRIPT_DIR/../.venv/bin/uvicorn" open_webui.main:app \
  --host 0.0.0.0 \
  --port "$BACKEND_PORT"
