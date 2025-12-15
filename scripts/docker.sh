#!/bin/bash
# Docker Compose management script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

COMMAND="${1:-up}"

case "$COMMAND" in
    up)
        echo -e "${GREEN}🐳 Starting Docker Compose services...${NC}"
        docker compose up -d
        echo -e "${GREEN}✅ Services started${NC}"
        echo -e "${BLUE}📊 Web App: http://localhost:8000${NC}"
        echo -e "${BLUE}📖 API Docs: http://localhost:8000/docs${NC}"
        echo -e "${BLUE}🗄️  pgAdmin: http://localhost:5050 (admin@example.com/admin)${NC}"
        ;;
    down)
        echo -e "${YELLOW}🛑 Stopping Docker Compose services...${NC}"
        docker compose down
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;
    restart)
        echo -e "${YELLOW}🔄 Restarting Docker Compose services...${NC}"
        docker compose restart
        echo -e "${GREEN}✅ Services restarted${NC}"
        ;;
    logs)
        echo -e "${BLUE}📋 Showing logs (Ctrl+C to exit)...${NC}"
        docker compose logs -f
        ;;
    build)
        echo -e "${YELLOW}🔨 Building Docker images...${NC}"
        docker compose build
        echo -e "${GREEN}✅ Build completed${NC}"
        ;;
    clean)
        echo -e "${RED}🧹 Removing all containers, volumes, and images...${NC}"
        docker compose down -v --rmi all
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
    status)
        echo -e "${BLUE}📊 Service status:${NC}"
        docker compose ps
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo ""
        echo -e "${YELLOW}Available commands:${NC}"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  build    - Build Docker images"
        echo "  clean    - Remove all containers, volumes, and images"
        echo "  status   - Show service status"
        exit 1
        ;;
esac
