#!/usr/bin/env bash

# LangBuilder + OpenWebUI Complete Stack Startup - macOS Version
# This script starts both OpenWebUI_CG and LangBuilder_CG on macOS
# with comprehensive pre-flight checks to ensure everything works

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Complete Stack Startup (macOS)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

echo -e "${BLUE}Running pre-flight checks...${NC}"
echo ""

PREFLIGHT_PASSED=true

# Check 1: Root .env file exists
if [ -f ".env" ]; then
    echo -e "  ${GREEN}✓${NC} Root .env file exists"
else
    echo -e "  ${RED}✗${NC} Root .env file missing"
    echo -e "    ${YELLOW}→ Copy .env.example to .env and configure${NC}"
    PREFLIGHT_PASSED=false
fi

# Check 2: Python 3.11 is available (required for OpenWebUI)
if command -v python3.11 &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Python 3.11 available"
else
    echo -e "  ${YELLOW}⚠${NC} Python 3.11 not found (OpenWebUI may have compatibility issues)"
    echo -e "    ${YELLOW}→ Install with: brew install python@3.11${NC}"
fi

# Check 3: Node.js and npm available
if command -v npm &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} npm available"
else
    echo -e "  ${RED}✗${NC} npm not found"
    echo -e "    ${YELLOW}→ Install Node.js: brew install node${NC}"
    PREFLIGHT_PASSED=false
fi

# Check 4: uv package manager available
if command -v uv &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} uv package manager available"
else
    echo -e "  ${RED}✗${NC} uv not found"
    echo -e "    ${YELLOW}→ Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    PREFLIGHT_PASSED=false
fi

# Check 5: OpenWebUI virtual environment
if [ -d "openwebui/.venv" ] && [ -f "openwebui/.venv/bin/python" ]; then
    echo -e "  ${GREEN}✓${NC} OpenWebUI virtual environment exists"
else
    echo -e "  ${YELLOW}⚠${NC} OpenWebUI virtual environment missing (will be created)"
fi

# Check 6: LangBuilder virtual environment
if [ -d "langbuilder/.venv" ]; then
    echo -e "  ${GREEN}✓${NC} LangBuilder virtual environment exists"
else
    echo -e "  ${RED}✗${NC} LangBuilder virtual environment missing"
    echo -e "    ${YELLOW}→ Run: cd langbuilder && uv venv${NC}"
    PREFLIGHT_PASSED=false
fi

# Check 7: OpenWebUI node_modules
if [ -d "openwebui/node_modules" ]; then
    echo -e "  ${GREEN}✓${NC} OpenWebUI npm packages installed"
else
    echo -e "  ${YELLOW}⚠${NC} OpenWebUI npm packages missing (will be installed)"
fi

# Check 8: y-protocols specifically (common missing dependency)
if [ -d "openwebui/node_modules/y-protocols" ]; then
    echo -e "  ${GREEN}✓${NC} y-protocols package installed"
else
    echo -e "  ${YELLOW}⚠${NC} y-protocols missing (will be installed)"
fi

# Check 9: LangBuilder local .env with VITE_PROXY_TARGET
if [ -f "langbuilder/.env" ] && grep -q "VITE_PROXY_TARGET" "langbuilder/.env" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} LangBuilder .env configured"
else
    echo -e "  ${YELLOW}⚠${NC} LangBuilder .env missing VITE_PROXY_TARGET (will be created)"
fi

# Check 9b: Ensure LANGBUILDER_AUTO_LOGIN=False (login enabled by default)
if [ -f "langbuilder/.env" ]; then
    if grep -q "^LANGBUILDER_AUTO_LOGIN=False" "langbuilder/.env" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} LangBuilder login mode enabled (AUTO_LOGIN=False)"
    elif grep -q "^LANGBUILDER_AUTO_LOGIN" "langbuilder/.env" 2>/dev/null; then
        # AUTO_LOGIN exists but is not False - update it
        sed -i '' 's/^LANGBUILDER_AUTO_LOGIN=.*/LANGBUILDER_AUTO_LOGIN=False/' "langbuilder/.env"
        echo -e "  ${GREEN}✓${NC} LangBuilder login mode enabled (updated AUTO_LOGIN=False)"
    else
        # AUTO_LOGIN doesn't exist - add it
        echo "" >> "langbuilder/.env"
        echo "# Authentication - Enable Login Mode" >> "langbuilder/.env"
        echo "LANGBUILDER_AUTO_LOGIN=False" >> "langbuilder/.env"
        echo -e "  ${GREEN}✓${NC} LangBuilder login mode enabled (added AUTO_LOGIN=False)"
    fi
fi

# Check 10: OpenWebUI backend WEBUI_NAME fix
if grep -q "^WEBUI_NAME" "openwebui/backend/open_webui/env.py" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} OpenWebUI WEBUI_NAME export configured"
else
    echo -e "  ${RED}✗${NC} OpenWebUI env.py missing WEBUI_NAME export"
    echo -e "    ${YELLOW}→ Add to openwebui/backend/open_webui/env.py:${NC}"
    echo -e "    ${YELLOW}   WEBUI_NAME = os.environ.get(\"WEBUI_NAME\", \"Open WebUI\")${NC}"
    PREFLIGHT_PASSED=false
fi

echo ""

if [ "$PREFLIGHT_PASSED" = false ]; then
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Pre-flight checks failed!${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "${YELLOW}Please fix the issues above before starting.${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}All critical pre-flight checks passed!${NC}"
echo ""

# =============================================================================
# START SERVICES
# =============================================================================

echo -e "${BLUE}Starting services:${NC}"
echo -e "  - OpenWebUI_CG (Backend: 8767, Frontend: 5175)"
echo -e "  - LangBuilder_CG (Backend: 8002, Frontend: 3000)"
echo ""

# Start OpenWebUI_CG
echo -e "${GREEN}Starting OpenWebUI_CG...${NC}"
cd openwebui
./start_openwebui_macos.sh &
OPENWEBUI_PID=$!
cd ..

echo -e "${YELLOW}Waiting 8 seconds for OpenWebUI to initialize...${NC}"
sleep 8

# Start LangBuilder_CG
echo -e "${GREEN}Starting LangBuilder_CG...${NC}"
cd langbuilder
./start_langbuilder_macos.sh &
LANGBUILDER_PID=$!
cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Complete Stack Started (macOS)!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}OpenWebUI_CG:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:5175${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:8767${NC}"
echo ""
echo -e "${BLUE}LangBuilder_CG:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:8002${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Handle Ctrl+C
trap "echo ''; echo -e '${YELLOW}Shutting down all services...${NC}'; kill $OPENWEBUI_PID $LANGBUILDER_PID 2>/dev/null; exit 0" INT TERM

# Keep script running
wait
