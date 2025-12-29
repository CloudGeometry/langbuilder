#!/bin/bash

# LangBuilder Stack Startup Script - macOS Version
# This script starts LangBuilder on macOS with proper PyTorch support
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Look for .env in parent directory (project root) and local directory
ENV_FILE="$SCRIPT_DIR/../.env"
LOCAL_ENV="$SCRIPT_DIR/.env"

# Load from root .env first
if [ -f "$ENV_FILE" ]; then
    BACKEND_PORT=$(grep '^LANGBUILDER_BACKEND_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs || echo "8002")
    FRONTEND_PORT=$(grep '^VITE_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" | xargs || echo "3000")
fi

# Load all environment variables from local .env (includes AWS credentials, auth, etc.)
if [ -f "$LOCAL_ENV" ]; then
    echo -e "${GREEN}Loading environment from $LOCAL_ENV...${NC}"
    set -a  # automatically export all variables
    source "$LOCAL_ENV"
    set +a

    # Show what was loaded
    if [ -n "$LANGBUILDER_AUTO_LOGIN" ]; then
        echo -e "${GREEN}Auth: AUTO_LOGIN=$LANGBUILDER_AUTO_LOGIN${NC}"
    fi
    if [ -n "$AWS_ACCESS_KEY_ID" ]; then
        echo -e "${GREEN}AWS: Credentials loaded (key: ${AWS_ACCESS_KEY_ID:0:10}...)${NC}"
    fi
    if [ -n "$AWS_SESSION_TOKEN" ]; then
        echo -e "${GREEN}AWS: Session token loaded (${#AWS_SESSION_TOKEN} chars)${NC}"
    fi
fi

# Default values if not set or empty
BACKEND_PORT="${BACKEND_PORT:-8002}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo -e "${GREEN}Starting LangBuilder_CG (macOS)...${NC}"

# Kill processes on ports
kill_port() {
    local port=$1
    pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
    fi
}

# Clear ports
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT

# Check for virtual environment
if [ ! -d .venv ]; then
    echo -e "${RED}Error: Virtual environment not found. Please run 'uv venv' first.${NC}"
    exit 1
fi

# Ensure local .env file exists with VITE_PROXY_TARGET
# This is critical - vite.config.mts reads from langbuilder/.env, NOT the root .env
LOCAL_ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$LOCAL_ENV_FILE" ] || ! grep -q "VITE_PROXY_TARGET" "$LOCAL_ENV_FILE" 2>/dev/null; then
    echo -e "${YELLOW}Creating local .env with VITE_PROXY_TARGET...${NC}"
    cat > "$LOCAL_ENV_FILE" << EOF
# LangBuilder Frontend Configuration
# This file is required for Vite to properly proxy API requests to the backend
VITE_PROXY_TARGET=http://localhost:${BACKEND_PORT}
VITE_PORT=${FRONTEND_PORT}
EOF
    echo -e "${GREEN}Local .env file created${NC}"
fi

# Setup environment
if [ -f ./scripts/setup/setup_env.sh ]; then
    source ./scripts/setup/setup_env.sh 2>/dev/null || true
fi

# Install PyTorch for macOS (MPS support, not CPU-only)
echo -e "${YELLOW}Ensuring PyTorch is installed for macOS...${NC}"
uv pip install torch torchvision 2>/dev/null || echo "PyTorch already installed or skipping..."

# Start backend
echo -e "${GREEN}Starting backend on port $BACKEND_PORT...${NC}"
uv run uvicorn \
    --factory langbuilder.main:create_app \
    --host 0.0.0.0 \
    --port "$BACKEND_PORT" \
    --loop asyncio \
    --log-level info &
BACKEND_PID=$!

sleep 3  # Give backend time to start

# Start frontend (uses "start" not "dev")
echo -e "${GREEN}Starting frontend on port $FRONTEND_PORT...${NC}"
cd src/frontend && npm run start -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ LangBuilder stack started (macOS)!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "  Backend PID: $BACKEND_PID (http://localhost:$BACKEND_PORT)"
echo -e "  Frontend PID: $FRONTEND_PID (http://localhost:$FRONTEND_PORT)"
echo ""
echo -e "${YELLOW}Stop with: kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "${YELLOW}Or press Ctrl+C${NC}"

# Handle Ctrl+C
trap "echo ''; echo -e '${YELLOW}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# Keep script running
wait
