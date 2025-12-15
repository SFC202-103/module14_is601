#!/bin/bash
# Development startup script for FastAPI Calculator Application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting FastAPI Calculator Application (Development Mode)${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}📥 Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create one with required environment variables.${NC}"
    echo -e "${YELLOW}   Using default configuration...${NC}"
fi

# Run the application
echo -e "${GREEN}✅ Starting FastAPI application on http://localhost:8000${NC}"
echo -e "${GREEN}📖 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}🔄 Auto-reload enabled for development${NC}"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
