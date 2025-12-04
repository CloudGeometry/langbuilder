#!/bin/bash

# LangBuilder Stack Startup Script - Cross-Platform (Windows/Linux/Mac)
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect OS
detect_os() {
    case "$OSTYPE" in
        linux*)   echo "linux" ;;
        darwin*)  echo "macos" ;;
        msys*|cygwin*|win32) echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

OS_TYPE=$(detect_os)
echo -e "${BLUE}Detected OS: ${OS_TYPE}${NC}"

# More robust .env loading that handles quotes and special characters
# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Look for .env in parent directory (project root)
ENV_FILE="$SCRIPT_DIR/../.env"

if [ -f "$ENV_FILE" ]; then
    # Only load simple PORT variables, skip complex JSON-like entries
    BACKEND_PORT=$(grep '^LANGBUILDER_BACKEND_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "8002")
    FRONTEND_PORT=$(grep '^VITE_PORT=' "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "3000")
else
    BACKEND_PORT="8002"
    FRONTEND_PORT="3000"
fi

# Remove any whitespace
BACKEND_PORT=$(echo $BACKEND_PORT | xargs)
FRONTEND_PORT=$(echo $FRONTEND_PORT | xargs)
OPENWEBUI_PORT="8767"

echo -e "${GREEN}Starting LangBuilder_CG...${NC}"

# Cross-platform kill_port function
kill_port() {
    local port=$1
    local process_name=$2
    local pids=""

    if [ "$OS_TYPE" = "windows" ]; then
        # Windows: Use netstat to find PIDs
        pids=$(netstat -ano 2>/dev/null | grep ":$port " | grep "LISTENING" | awk '{print $5}' | sort -u || true)
        if [ -n "$pids" ]; then
            echo -e "${YELLOW}Killing processes on port $port (Windows)...${NC}"
            for pid in $pids; do
                taskkill //F //PID "$pid" 2>/dev/null || true
            done
            sleep 1
        fi
    else
        # Linux/Mac: Try lsof first, fallback to fuser
        if command -v lsof &> /dev/null; then
            pids=$(lsof -ti:$port 2>/dev/null || true)
            if [ -n "$pids" ]; then
                echo -e "${YELLOW}Killing processes on port $port (Unix)...${NC}"
                for pid in $pids; do
                    kill -9 "$pid" 2>/dev/null || true
                done
                sleep 1
            fi
        elif command -v fuser &> /dev/null; then
            fuser -k ${port}/tcp 2>/dev/null || true
            sleep 1
        fi
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
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ LangBuilder stack started!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Service Information:${NC}"
echo -e "  Backend PID:  $BACKEND_PID"
echo -e "  Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "  OpenWebUI: ${GREEN}http://localhost:$OPENWEBUI_PORT${NC}"
echo ""
echo -e "${YELLOW}To stop services:${NC}"

if [ "$OS_TYPE" = "windows" ]; then
    echo -e "  ${BLUE}taskkill //F //PID $BACKEND_PID //PID $FRONTEND_PID${NC}"
else
    echo -e "  ${BLUE}kill $BACKEND_PID $FRONTEND_PID${NC}"
fi

echo -e "${YELLOW}Or press Ctrl+C${NC}"
echo ""

# Keep script running and handle Ctrl+C gracefully
trap "echo ''; echo -e '${YELLOW}Shutting down services...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait