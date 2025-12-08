#!/usr/bin/env bash

# Docker Development Environment Startup Script
# This script replicates 'make backend' and 'make frontend' behavior in Docker
# Equivalent to: langbuilder/start_langbuilder_stack.sh but using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.dev.yml"
ENV_FILE=".env.docker"

# Print banner
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  LangBuilder Docker Dev Environment  ${NC}"
echo -e "${CYAN}  (Replicates Makefile behavior)      ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}Error: Docker daemon is not running${NC}"
        echo "Please start Docker Desktop and try again"
        exit 1
    fi

    echo -e "${GREEN}✓ Docker is installed and running${NC}"
}

# Check if docker-compose is available
check_docker_compose() {
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo -e "${RED}Error: docker-compose is not available${NC}"
        echo "Please install docker-compose or update Docker Desktop"
        exit 1
    fi

    echo -e "${GREEN}✓ docker-compose is available${NC}"
}

# Check if .env.docker exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}Warning: $ENV_FILE not found${NC}"
        echo "Using default environment variables from docker-compose.dev.yml"
    else
        echo -e "${GREEN}✓ Using $ENV_FILE for environment configuration${NC}"
    fi
}

# Initialize docker-compose command
check_docker_compose

# Parse command line arguments
COMMAND=${1:-up}

case "$COMMAND" in
    up|start)
        echo -e "${BLUE}Starting services...${NC}"
        echo ""

        check_docker
        check_env_file

        echo ""
        echo -e "${BLUE}Building and starting containers...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE up -d --build

        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✓ All services started successfully!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${CYAN}🎯 Primary Services (Makefile equivalent):${NC}"
        echo -e "  ${BLUE}LangBuilder Backend:${NC}   ${GREEN}http://localhost:8002${NC}  (uvicorn with auto-reload)"
        echo -e "  ${BLUE}LangBuilder Frontend:${NC}  ${GREEN}http://localhost:3000${NC}  (Vite HMR)"
        echo ""
        echo -e "${CYAN}🔧 Additional Services:${NC}"
        echo -e "  ${BLUE}OpenWebUI Frontend:${NC}    ${GREEN}http://localhost:5175${NC}"
        echo -e "  ${BLUE}OpenWebUI Backend:${NC}     ${GREEN}http://localhost:8767${NC}"
        echo -e "  ${BLUE}PostgreSQL:${NC}            ${GREEN}localhost:5432${NC} (user: langbuilder, pass: langbuilder)"
        echo ""
        echo -e "${CYAN}📝 Features:${NC}"
        echo -e "  ✓ Hot-reload enabled for backend (like 'make backend')"
        echo -e "  ✓ HMR enabled for frontend (like 'make frontend')"
        echo -e "  ✓ Source code mounted for instant changes"
        echo -e "  ✓ Database migrations run automatically"
        echo ""
        echo -e "${CYAN}🛠️  Useful Commands:${NC}"
        echo -e "  ${BLUE}View all logs:${NC}         ./start-docker-dev.sh logs"
        echo -e "  ${BLUE}View backend logs:${NC}     ./start-docker-dev.sh logs langbuilder-backend"
        echo -e "  ${BLUE}View frontend logs:${NC}    ./start-docker-dev.sh logs langbuilder-frontend"
        echo -e "  ${BLUE}Stop services:${NC}         ./start-docker-dev.sh stop"
        echo -e "  ${BLUE}Restart services:${NC}      ./start-docker-dev.sh restart"
        echo -e "  ${BLUE}Rebuild containers:${NC}    ./start-docker-dev.sh rebuild"
        echo -e "  ${BLUE}Remove everything:${NC}     ./start-docker-dev.sh down"
        echo -e "  ${BLUE}Shell into backend:${NC}    ./start-docker-dev.sh exec langbuilder-backend bash"
        echo ""
        ;;

    down|clean)
        echo -e "${YELLOW}Stopping and removing all containers...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE down
        echo -e "${GREEN}✓ All containers removed${NC}"
        ;;

    down-volumes|clean-all)
        echo -e "${YELLOW}Stopping and removing all containers and volumes...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE down -v
        echo -e "${GREEN}✓ All containers and volumes removed${NC}"
        echo -e "${YELLOW}Note: This will delete all database data!${NC}"
        ;;

    stop)
        echo -e "${YELLOW}Stopping all containers...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE stop
        echo -e "${GREEN}✓ All containers stopped${NC}"
        ;;

    restart)
        echo -e "${YELLOW}Restarting all containers...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE restart
        echo -e "${GREEN}✓ All containers restarted${NC}"
        ;;

    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            echo -e "${BLUE}Showing logs for all services (Ctrl+C to exit)...${NC}"
            $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f
        else
            echo -e "${BLUE}Showing logs for $SERVICE (Ctrl+C to exit)...${NC}"
            $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f $SERVICE
        fi
        ;;

    ps|status)
        echo -e "${BLUE}Container status:${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE ps
        ;;

    build)
        echo -e "${BLUE}Building all containers...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE build
        echo -e "${GREEN}✓ All containers built${NC}"
        ;;

    rebuild)
        echo -e "${BLUE}Rebuilding all containers (no cache)...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE build --no-cache
        echo -e "${GREEN}✓ All containers rebuilt${NC}"
        ;;

    exec)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            echo -e "${RED}Error: Please specify a service name${NC}"
            echo "Available services: langbuilder-backend, langbuilder-frontend, openwebui-backend, openwebui-frontend, postgres"
            exit 1
        fi
        shift 2
        EXEC_CMD=${@:-bash}
        echo -e "${BLUE}Executing in $SERVICE: $EXEC_CMD${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE exec $SERVICE $EXEC_CMD
        ;;

    help|--help|-h)
        echo "Usage: ./start-docker-dev.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  up, start           Start all services (default)"
        echo "  down, clean         Stop and remove containers"
        echo "  down-volumes        Stop and remove containers and volumes (deletes data)"
        echo "  stop                Stop all containers"
        echo "  restart             Restart all containers"
        echo "  logs [service]      Show logs (all services or specific service)"
        echo "  ps, status          Show container status"
        echo "  build               Build all containers"
        echo "  rebuild             Rebuild all containers (no cache)"
        echo "  exec <service> [cmd] Execute command in service container"
        echo "  help                Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./start-docker-dev.sh up"
        echo "  ./start-docker-dev.sh logs langbuilder-backend"
        echo "  ./start-docker-dev.sh exec langbuilder-backend bash"
        echo "  ./start-docker-dev.sh down-volumes"
        ;;

    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo "Run './start-docker-dev.sh help' for usage information"
        exit 1
        ;;
esac
