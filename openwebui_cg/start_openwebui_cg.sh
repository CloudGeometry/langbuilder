#!/usr/bin/env bash

# OpenWebUI_CG Stack Startup Script
# Compatible with Linux (production) and Windows/Git Bash (development)
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_PORT="${OPEN_WEBUI_PORT:-8767}"
FRONTEND_PORT="5175"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

echo -e "${GREEN}Starting OpenWebUI_CG...${NC}"

# Change to script directory
cd "$SCRIPT_DIR"

# Check if npm modules are installed
check_npm_dependencies() {
    if [ ! -d "node_modules" ]; then
        return 1
    fi

    # Check if package-lock.json is newer than node_modules (optional check)
    if [ -f "package-lock.json" ] && [ "package-lock.json" -nt "node_modules" ]; then
        return 1
    fi

    return 0
}

# Check if Python venv exists and has required packages
check_python_venv() {
    if [ ! -d ".venv" ]; then
        return 1
    fi

    # Determine Python executable based on OS
    if [ "$OS_TYPE" = "windows" ]; then
        PYTHON_BIN=".venv/Scripts/python.exe"
        PIP_BIN=".venv/Scripts/pip.exe"
    else
        PYTHON_BIN=".venv/bin/python"
        PIP_BIN=".venv/bin/pip"
    fi

    # Check if uvicorn is installed
    if [ -f "$PYTHON_BIN" ]; then
        if ! "$PYTHON_BIN" -c "import uvicorn" 2>/dev/null; then
            return 1
        fi
    else
        return 1
    fi

    return 0
}

# Kill process on port (cross-platform)
kill_port() {
    local port=$1
    local service_name=$2
    local pids=""

    if [ "$OS_TYPE" = "windows" ]; then
        pids=$(netstat -ano 2>/dev/null | grep ":$port " | grep "LISTENING" | awk '{print $5}' | sort -u || true)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                taskkill //F //PID "$pid" 2>/dev/null || true
            done
            sleep 1
        fi
    else
        if command -v lsof &> /dev/null; then
            pids=$(lsof -ti:$port 2>/dev/null || true)
            if [ -n "$pids" ]; then
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

# Install frontend dependencies
install_frontend_deps() {
    if ! check_npm_dependencies; then
        echo -e "${YELLOW}Installing npm packages...${NC}"
        if ! npm install --legacy-peer-deps; then
            echo -e "${RED}Failed to install npm packages${NC}"
            exit 1
        fi
        echo -e "${GREEN}NPM packages installed successfully${NC}"
    else
        echo -e "${GREEN}NPM packages already installed${NC}"
    fi
}

# Install backend dependencies
install_backend_deps() {
    # Determine Python command
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi

    # Create venv if it doesn't exist
    if [ ! -d ".venv" ]; then
        $PYTHON_CMD -m venv .venv
    fi

    # Determine paths based on OS
    if [ "$OS_TYPE" = "windows" ]; then
        VENV_PYTHON=".venv/Scripts/python.exe"
        VENV_PIP=".venv/Scripts/pip.exe"
    else
        VENV_PYTHON=".venv/bin/python"
        VENV_PIP=".venv/bin/pip"
    fi

    # Install backend requirements if needed
    if [ -f "backend/requirements.txt" ]; then
        if ! "$VENV_PYTHON" -c "import uvicorn" 2>/dev/null; then
            echo -e "${YELLOW}Installing backend dependencies...${NC}"
            if ! "$VENV_PIP" install -r backend/requirements.txt; then
                echo -e "${RED}Failed to install backend dependencies${NC}"
                exit 1
            fi
            echo -e "${GREEN}Backend dependencies installed successfully${NC}"
        else
            echo -e "${GREEN}Backend dependencies already installed${NC}"
        fi
    else
        echo -e "${RED}Error: backend/requirements.txt not found${NC}"
        exit 1
    fi
}

# Main execution
main() {
    # Install dependencies
    install_frontend_deps
    install_backend_deps

    # Clear ports
    kill_port "$BACKEND_PORT" "Backend"
    kill_port "$FRONTEND_PORT" "Frontend"

    # Start services
    echo -e "${GREEN}Starting Backend on port $BACKEND_PORT...${NC}"

    # Start backend in background
    ./backend/start_openwebui_simple.sh &
    BACKEND_PID=$!

    echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
    echo -e "${YELLOW}Waiting 5 seconds for backend initialization...${NC}"
    sleep 5

    echo -e "${GREEN}Starting Frontend on port $FRONTEND_PORT...${NC}"

    # Start frontend in background
    npm run dev -- --port "$FRONTEND_PORT" &
    FRONTEND_PID=$!

    echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"

    # Display status
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ OpenWebUI_CG Stack Running!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${BLUE}Backend:  PID $BACKEND_PID${NC}"
    echo -e "${BLUE}Frontend: PID $FRONTEND_PID${NC}"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "  Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "  Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
    echo ""
    echo -e "${YELLOW}To stop services:${NC}"

    if [ "$OS_TYPE" = "windows" ]; then
        echo -e "  ${BLUE}taskkill //F //PID $BACKEND_PID //PID $FRONTEND_PID${NC}"
    else
        echo -e "  ${BLUE}kill $BACKEND_PID $FRONTEND_PID${NC}"
    fi

    echo -e "${YELLOW}Or press Ctrl+C${NC}"
    echo ""

    # Keep script running and handle Ctrl+C
    trap "echo ''; echo -e '${YELLOW}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

    wait
}

# Run main function
main
