#!/bin/bash

# LangBuilder Stack Startup Script - Windows Compatible
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# More robust .env loading that handles quotes and special characters
# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Look for .env in parent directory (project root)
ENV_FILE="$SCRIPT_DIR/../.env"

if [ -f "$ENV_FILE" ]; then
    # Only load simple PORT variables, skip complex JSON-like entries
    BACKEND_PORT=$(grep '^LANGBUILDER_BACKEND_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "8765")
    FRONTEND_PORT=$(grep '^VITE_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "8766")
else
    BACKEND_PORT="8765"
    FRONTEND_PORT="8766"
fi

# Remove any whitespace
BACKEND_PORT=$(echo $BACKEND_PORT | xargs)
FRONTEND_PORT=$(echo $FRONTEND_PORT | xargs)
OPENWEBUI_PORT="8767"

echo -e "${GREEN}Starting LangBuilder_CG...${NC}"

# Windows-compatible kill_port function
kill_port() {
    local port=$1
    local process_name=$2

    # Try different methods depending on what's available
    if command -v lsof &> /dev/null; then
        # Unix/Linux/MacOS with lsof
        pids=$(lsof -ti:$port 2>/dev/null || true)
    elif command -v netstat &> /dev/null; then
        # Windows with netstat
        pids=$(netstat -ano 2>/dev/null | grep ":$port " | grep "LISTENING" | awk '{print $5}' | sort -u || true)
    else
        return
    fi

    if [ -n "$pids" ]; then
        for pid in $pids; do
            if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
                taskkill //F //PID $pid 2>/dev/null || true
            else
                kill -9 $pid 2>/dev/null || true
            fi
        done
        sleep 1
    fi
}

# Clear ports
kill_port $BACKEND_PORT "backend"
kill_port $FRONTEND_PORT "frontend"

# Start services
cd "$(dirname "$0")"

echo -e "${GREEN}Starting backend on port $BACKEND_PORT...${NC}"
make backend port=$BACKEND_PORT &
BACKEND_PID=$!

sleep 3  # Give backend time to start

echo -e "${GREEN}Starting frontend on port $FRONTEND_PORT...${NC}"
make frontend &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✓ LangBuilder stack started!${NC}"
echo -e "  Backend PID: $BACKEND_PID (http://localhost:$BACKEND_PORT)"
echo -e "  Frontend PID: $FRONTEND_PID (http://localhost:$FRONTEND_PORT)"
echo -e "  OpenWebUI: http://localhost:$OPENWEBUI_PORT"
echo ""
echo -e "${YELLOW}Stop with: taskkill //F //PID $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "${YELLOW}Or press Ctrl+C${NC}"

# Keep script running
wait