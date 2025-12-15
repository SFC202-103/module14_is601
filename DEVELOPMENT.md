# Development Guide

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd module14_is601

# Quick setup and run
./scripts/dev.sh
```

That's it! The application will be running at http://localhost:8000

## Development Scripts

We provide several convenience scripts in the `scripts/` directory:

### `./scripts/dev.sh` - Development Server
- Auto-creates virtual environment if missing
- Installs/updates dependencies
- Starts FastAPI with hot-reload
- Perfect for local development

### `./scripts/prod.sh` - Production Server
- Runs database initialization
- Starts with multiple workers
- No auto-reload
- Use for production-like testing

### `./scripts/test.sh` - Test Runner
```bash
./scripts/test.sh                    # Run all tests
./scripts/test.sh tests/ --coverage  # With coverage report
./scripts/test.sh tests/unit/        # Specific test directory
```

### `./scripts/docker.sh` - Docker Management
```bash
./scripts/docker.sh up       # Start all services
./scripts/docker.sh down     # Stop all services
./scripts/docker.sh logs     # View logs
./scripts/docker.sh build    # Rebuild images
./scripts/docker.sh clean    # Remove everything
./scripts/docker.sh status   # Check status
```

## Project Architecture

### Application Structure

```
app/
├── main.py          # FastAPI application and routes
├── database.py      # Database connection and session management
├── auth/            # Authentication and authorization
├── core/            # Configuration and settings
├── models/          # SQLAlchemy ORM models
├── operations/      # Business logic operations
└── schemas/         # Pydantic models for validation
```

### Key Components

1. **FastAPI Application** (`app/main.py`)
   - RESTful API endpoints
   - HTML template routes
   - Lifespan management

2. **Database Models** (`app/models/`)
   - `User`: User authentication and management
   - `Calculation`: Mathematical calculations storage

3. **Schemas** (`app/schemas/`)
   - Request/response validation
   - Data transformation
   - Type safety

4. **Authentication** (`app/auth/`)
   - JWT token generation
   - Token refresh mechanism
   - Redis-based token blacklisting

## Database Setup

### Local Development (without Docker)

1. Install PostgreSQL locally
2. Create database:
   ```sql
   CREATE DATABASE fastapi_db;
   CREATE DATABASE fastapi_test_db;
   ```
3. Update `.env` with connection strings
4. Initialize tables:
   ```bash
   source .venv/bin/activate
   python -m app.database_init
   ```

### Docker Compose (Recommended)

```bash
./scripts/docker.sh up
```

This starts:
- PostgreSQL database on port 5432
- pgAdmin on port 5050
- FastAPI application on port 8000

Access pgAdmin at http://localhost:5050:
- Email: admin@example.com
- Password: admin

## Testing

### Test Structure

```
tests/
├── unit/            # Unit tests (no external dependencies)
├── integration/     # Integration tests (database required)
└── e2e/             # End-to-end tests (full stack required)
```

### Running Tests

```bash
# All tests
./scripts/test.sh

# With coverage
./scripts/test.sh tests/ --coverage
open htmlcov/index.html  # View coverage report

# Specific test file
./scripts/test.sh tests/unit/test_calculator.py

# Specific test function
pytest tests/unit/test_calculator.py::test_add -v
```

### Test Requirements

- **Unit tests**: No external dependencies
- **Integration tests**: Require PostgreSQL database
- **E2E tests**: Require full Docker Compose stack

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Common Development Tasks

### Adding a New Endpoint

1. Define Pydantic schema in `app/schemas/`
2. Add route in `app/main.py`
3. Create tests in `tests/`
4. Update documentation

### Adding a New Database Model

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Create migration (if using Alembic) or reinit database
4. Create corresponding schemas
5. Add tests

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL`: PostgreSQL connection
- `JWT_SECRET_KEY`: JWT signing key (32+ chars)
- `JWT_REFRESH_SECRET_KEY`: Refresh token key (32+ chars)
- `REDIS_URL`: Redis connection (optional)

## Code Quality

### Formatting (Optional)

Install formatters:
```bash
pip install black isort pylint
```

Format code:
```bash
black app/ tests/
isort app/ tests/
```

Lint code:
```bash
pylint app/
```

### Pre-commit Checks

Before committing:
1. Run tests: `./scripts/test.sh`
2. Check for errors: No Python syntax errors
3. Update requirements if needed: `pip freeze > requirements.txt`

## Debugging

### Enable Debug Mode

Set in `.env`:
```
DEBUG=True
```

### VS Code Launch Configuration

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Connection**: Check PostgreSQL is running
3. **Port Already in Use**: Kill process on port 8000
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

## Docker Development

### Hot Reload with Docker

The `docker-compose.yml` includes volume mounting for hot reload:
```yaml
volumes:
  - .:/app
```

Code changes will automatically reload the application.

### Rebuilding After Dependency Changes

```bash
./scripts/docker.sh build
./scripts/docker.sh up
```

## Production Deployment

### Environment Setup

1. Set production environment variables
2. Generate secure JWT secrets (min 32 characters)
3. Use production database credentials
4. Set `DEBUG=False`

### Using Docker

```bash
docker build -t fastapi-calculator .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET_KEY=... \
  fastapi-calculator
```

### Security Checklist

- [ ] Update JWT secret keys
- [ ] Set strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Set rate limiting
- [ ] Enable security headers
- [ ] Regular dependency updates

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Getting Help

1. Check the README.md
2. Review API documentation at `/docs`
3. Check existing issues in the repository
4. Ask your team or instructor
