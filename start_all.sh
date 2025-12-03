#!/usr/bin/env bash

# LangBuilder + OpenWebUI Complete Stack Startup
# This script starts both OpenWebUI_CG and LangBuilder_CG

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Complete Stack Startup${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Starting:${NC}"
echo -e "  • OpenWebUI_CG (Backend: 8767, Frontend: 5175)"
echo -e "  • LangBuilder_CG (Backend: 8002, Frontend: 3000)"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Start OpenWebUI_CG
cd openwebui_cg
./start_openwebui_cg.sh &
OPENWEBUI_PID=$!
cd ..

echo -e "${YELLOW}Waiting 8 seconds for OpenWebUI to initialize...${NC}"
sleep 8

# Start LangBuilder_CG
cd langbuilder_cg
./start_langbuilder_stack.sh &
LANGBUILDER_PID=$!
cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Complete Stack Started!${NC}"
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

# Keep script running
wait
