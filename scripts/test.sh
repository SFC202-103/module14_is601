#!/bin/bash
# Test runner script for FastAPI Calculator Application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Running Tests for FastAPI Calculator Application${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run scripts/dev.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Parse command line arguments
TEST_PATH="${1:-tests/}"
COVERAGE="${2:-}"

if [ "$COVERAGE" == "--coverage" ]; then
    echo -e "${YELLOW}📊 Running tests with coverage report...${NC}"
    pytest "$TEST_PATH" -v --cov=app --cov-report=html --cov-report=term
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
else
    echo -e "${YELLOW}🧪 Running tests...${NC}"
    pytest "$TEST_PATH" -v
fi

echo -e "${GREEN}✅ Tests completed${NC}"
