.PHONY: help install dev test clean docker-up

help:
@echo "FastAPI Calculator Commands:"
@echo "  make setup       - Complete setup"
@echo "  make dev         - Start dev server"
@echo "  make test        - Run tests"
@echo "  make docker-up   - Start Docker"
@echo "  make clean       - Clean cache"

install:
.venv/bin/pip install -q -r requirements.txt

dev:
./scripts/dev.sh

test:
./scripts/test.sh

clean:
rm -rf __pycache__ .pytest_cache htmlcov .coverage

docker-up:
./scripts/docker.sh up

setup: install
@echo "Setup complete!"
