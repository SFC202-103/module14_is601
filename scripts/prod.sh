#!/bin/bash
# Production startup script for FastAPI Calculator Application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting FastAPI Calculator Application (Production Mode)${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run scripts/dev.sh first or create venv manually.${NC}"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Production mode requires environment configuration.${NC}"
    exit 1
fi

# Run database initialization
echo -e "${YELLOW}🗄️  Initializing database...${NC}"
python -m app.database_init

# Run the application with production settings
echo -e "${GREEN}✅ Starting FastAPI application on http://0.0.0.0:8000${NC}"
echo -e "${GREEN}📖 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}⚡ Running with 4 workers${NC}"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
