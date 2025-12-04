#!/usr/bin/env bash

# OpenWebUI Stack Startup Script - macOS Version
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

echo -e "${GREEN}Starting OpenWebUI (macOS)...${NC}"

# Change to script directory
cd "$SCRIPT_DIR"

# Check if npm modules are installed
check_npm_dependencies() {
    if [ ! -d "node_modules" ]; then
        return 1
    fi
    if [ -f "package-lock.json" ] && [ "package-lock.json" -nt "node_modules" ]; then
        return 1
    fi
    return 0
}

# Check if Python venv exists
check_python_venv() {
    if [ ! -d ".venv" ]; then
        return 1
    fi
    if [ -f ".venv/bin/python" ]; then
        if ! ".venv/bin/python" -c "import uvicorn" 2>/dev/null; then
            return 1
        fi
    else
        return 1
    fi
    return 0
}

# Kill process on port
kill_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                kill -9 "$pid" 2>/dev/null || true
            done
            sleep 1
        fi
    fi
}

# Check if y-protocols is installed (critical dependency)
check_y_protocols() {
    if [ -d "node_modules/y-protocols" ]; then
        return 0
    fi
    return 1
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

    # Ensure y-protocols is installed (required for Yjs collaborative editing)
    if ! check_y_protocols; then
        echo -e "${YELLOW}Installing y-protocols (required dependency)...${NC}"
        if ! npm install y-protocols --legacy-peer-deps; then
            echo -e "${RED}Failed to install y-protocols${NC}"
            exit 1
        fi
        echo -e "${GREEN}y-protocols installed successfully${NC}"
    fi
}

# Install backend dependencies
install_backend_deps() {
    # Create venv with Python 3.11 if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        if command -v python3.11 &> /dev/null; then
            python3.11 -m venv .venv
        elif command -v python3 &> /dev/null; then
            python3 -m venv .venv
        else
            python -m venv .venv
        fi
    fi

    # Install backend requirements if needed
    if [ -f "backend/requirements.txt" ]; then
        if ! ".venv/bin/python" -c "import uvicorn" 2>/dev/null; then
            echo -e "${YELLOW}Installing backend dependencies...${NC}"
            if ! ".venv/bin/pip" install -r backend/requirements.txt; then
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
    kill_port "$BACKEND_PORT"
    kill_port "$FRONTEND_PORT"

    # Start backend using macOS script
    echo -e "${GREEN}Starting Backend on port $BACKEND_PORT...${NC}"
    ./backend/start_openwebui_macos.sh &
    BACKEND_PID=$!

    echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
    echo -e "${YELLOW}Waiting 5 seconds for backend initialization...${NC}"
    sleep 5

    # Start frontend
    echo -e "${GREEN}Starting Frontend on port $FRONTEND_PORT...${NC}"
    npm run dev -- --port "$FRONTEND_PORT" &
    FRONTEND_PID=$!

    echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"

    # Display status
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ OpenWebUI Stack Running (macOS)!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${BLUE}Backend:  PID $BACKEND_PID${NC}"
    echo -e "${BLUE}Frontend: PID $FRONTEND_PID${NC}"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "  Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "  Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
    echo ""
    echo -e "${YELLOW}To stop services: kill $BACKEND_PID $FRONTEND_PID${NC}"
    echo -e "${YELLOW}Or press Ctrl+C${NC}"
    echo ""

    # Handle Ctrl+C
    trap "echo ''; echo -e '${YELLOW}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

    wait
}

# Run main function
main
