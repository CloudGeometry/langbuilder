#!/usr/bin/env bash

# OpenWebUI Backend Startup Script - macOS Version
# This script starts the OpenWebUI backend using the macOS Python venv path

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit

# Load environment variables from .env
ENV_FILE="$SCRIPT_DIR/../../.env"
if [ -f "$ENV_FILE" ]; then
    # Extract port
    BACKEND_PORT=$(grep '^OPEN_WEBUI_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)

    # Export auth-related variables for OpenWebUI
    export ENABLE_LOGIN_FORM=$(grep '^ENABLE_LOGIN_FORM=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export ENABLE_SIGNUP=$(grep '^ENABLE_SIGNUP=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export ENABLE_OAUTH_SIGNUP=$(grep '^ENABLE_OAUTH_SIGNUP=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export ENABLE_API_KEY=$(grep '^ENABLE_API_KEY=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export WEBUI_NAME=$(grep '^WEBUI_NAME=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export WEBUI_SECRET_KEY=$(grep '^WEBUI_SECRET_KEY=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export JWT_EXPIRES_IN=$(grep '^JWT_EXPIRES_IN=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)

    # OAuth configuration
    export GOOGLE_CLIENT_ID=$(grep '^GOOGLE_CLIENT_ID=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export GOOGLE_CLIENT_SECRET=$(grep '^GOOGLE_CLIENT_SECRET=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)
    export OAUTH_MERGE_ACCOUNTS_BY_EMAIL=$(grep '^OAUTH_MERGE_ACCOUNTS_BY_EMAIL=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)

    # Database
    export DATABASE_URL=$(grep '^DATABASE_URL=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs)

    # CORS - must include frontend origin for credentials to work
    export CORS_ALLOW_ORIGIN="http://localhost:5175"
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
