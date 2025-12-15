# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

**Highly recommended for development:**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Quick Setup Script

```bash
./scripts/dev.sh  # Auto-creates venv, installs deps, and starts server
```

---

# 🐳 5. Docker Setup

This project uses Docker Compose to orchestrate multiple services:
- **FastAPI Application** (Port 8000)
- **PostgreSQL Database** (Port 5432)
- **pgAdmin** (Port 5050) - Database management interface

## Prerequisites

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

**Windows WSL2 Users**: Enable Docker Desktop integration with WSL2 in Docker Desktop settings.

## Using Docker Compose (Recommended)

**Start all services:**
```bash
./scripts/docker.sh up
# Or manually:
docker compose up -d
```

**Stop all services:**
```bash
./scripts/docker.sh down
```

**View logs:**
```bash
./scripts/docker.sh logs
```

**Access Services:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (admin@example.com / admin)

---

# 🚀 6. Running the Project

## Option 1: Development Mode (Recommended)

**Using the dev script (easiest):**
```bash
./scripts/dev.sh
```
This automatically:
- Creates/activates virtual environment
- Installs dependencies
- Starts FastAPI with auto-reload on http://localhost:8000

**Or manually:**
```bash
source .venv/bin/activate  # .venv\Scripts\activate on Windows
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Option 2: Production Mode

```bash
./scripts/prod.sh
# Or manually:
source .venv/bin/activate
python -m app.database_init  # Initialize database
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Option 3: Docker Compose (Full Stack)

```bash
./scripts/docker.sh up
```

Starts complete stack including database and pgAdmin.

## Accessing the Application

- **API**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

# 🧪 7. Running Tests

**Run all tests:**
```bash
./scripts/test.sh
```

**Run tests with coverage:**
```bash
./scripts/test.sh tests/ --coverage
```

**Run specific test suites:**
```bash
./scripts/test.sh tests/unit/              # Unit tests only
./scripts/test.sh tests/integration/        # Integration tests
./scripts/test.sh tests/e2e/                # End-to-end tests
```

**Or manually:**
```bash
source .venv/bin/activate
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=html  # With coverage
```

**Note**: Integration and E2E tests require a running PostgreSQL database. Use Docker Compose:
```bash
./scripts/docker.sh up
```

---

# 🔐 8. Environment Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

**Important**: Update JWT secret keys in production!

**Required variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens (min 32 characters)
- `JWT_REFRESH_SECRET_KEY` - Secret key for refresh tokens (min 32 characters)
- `REDIS_URL` - Redis connection string (optional)

---

# 📂 9. Project Structure

```
module14_is601/
├── app/                      # Main application package
│   ├── auth/                # Authentication & authorization
│   │   ├── dependencies.py  # Auth dependencies
│   │   ├── jwt.py          # JWT token handling
│   │   └── redis.py        # Redis for token blacklisting
│   ├── core/               # Core configuration
│   │   └── config.py       # Application settings
│   ├── models/             # Database models (SQLAlchemy)
│   │   ├── calculation.py  # Calculation model
│   │   └── user.py         # User model
│   ├── operations/         # Business logic operations
│   ├── schemas/            # Pydantic schemas for validation
│   │   ├── base.py         # Base schemas
│   │   ├── calculation.py  # Calculation schemas
│   │   ├── token.py        # Token schemas
│   │   └── user.py         # User schemas
│   ├── database.py         # Database connection
│   ├── database_init.py    # Database initialization
│   └── main.py             # FastAPI application entry point
├── docs/                   # Documentation
├── scripts/                # Utility scripts
│   ├── dev.sh             # Development server script
│   ├── prod.sh            # Production server script
│   ├── test.sh            # Test runner script
│   └── docker.sh          # Docker management script
├── static/                 # Static files (CSS, JS)
├── templates/              # HTML templates (Jinja2)
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── pytest.ini             # Pytest configuration
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

# 📝 10. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🚀 11. Production Deployment

## Infrastructure Stack

Deploy to production with enterprise-grade infrastructure:

```
┌─────────────────────────────────────────────┐
│         Production Infrastructure            │
├─────────────────────────────────────────────┤
│ 🔐 Multi-layer Security                     │
│    ├── SSH Key Authentication               │
│    ├── UFW Firewall                         │
│    ├── Fail2Ban Protection                  │
│    └── Security Headers                     │
├─────────────────────────────────────────────┤
│ 🐳 Docker Platform                          │
│    ├── Docker Engine 24.0+                  │
│    └── Docker Compose v2                    │
├─────────────────────────────────────────────┤
│ 🌐 Caddy Reverse Proxy                      │
│    ├── Automatic HTTPS (Let's Encrypt)      │
│    ├── HTTP/2 & HTTP/3                      │
│    └── Auto SSL Renewal                     │
├─────────────────────────────────────────────┤
│ 🗄️ PostgreSQL Database                     │
│    ├── PostgreSQL 17                        │
│    ├── pgAdmin Interface                    │
│    └── Automated Backups                    │
├─────────────────────────────────────────────┤
│ 🚀 FastAPI Application                      │
│    ├── Backend API                          │
│    ├── Static Files                         │
│    └── Redis Cache                          │
├─────────────────────────────────────────────┤
│ 🔄 CI/CD Pipeline                           │
│    ├── GitHub Actions                       │
│    ├── Automated Testing                    │
│    └── Zero-Downtime Deployment             │
└─────────────────────────────────────────────┘
```

### Quick Production Deployment

1. **Server Setup** (Ubuntu 22.04 LTS)
   ```bash
   # Security
   sudo apt update && sudo apt install -y ufw fail2ban
   sudo ufw allow 22,80,443/tcp
   sudo ufw enable
   ```

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Deploy Application**
   ```bash
   git clone <your-repo>
   cd <repo-name>
   
   # Configure environment
   cp .env.example .env.production
   # Edit .env.production with production values
   
   # Start services
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Configure GitHub Actions**
   - Add server SSH key to GitHub Secrets
   - Push to `main` branch triggers automatic deployment

### Complete Deployment Guide

For comprehensive production deployment with:
- Multi-layer security setup
- Caddy reverse proxy configuration
- SSL certificate automation
- CI/CD pipeline setup
- Database backup strategies
- Monitoring and maintenance

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions**

---

# 🔥 Quick Reference Commands

## Development Workflow
| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Start Development Server        | `./scripts/dev.sh`                              |
| Start Production Server         | `./scripts/prod.sh`                             |
| Run Tests                       | `./scripts/test.sh`                             |
| Run Tests with Coverage         | `./scripts/test.sh tests/ --coverage`           |
| Start Docker Services           | `./scripts/docker.sh up`                        |
| Stop Docker Services            | `./scripts/docker.sh down`                      |
| View Docker Logs                | `./scripts/docker.sh logs`                      |
| Clean Cache Files               | `find . -name __pycache__ -type d -exec rm -rf {} +` |

## Setup Commands
| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Username          | `git config --global user.name "Your Name"`      |
| Configure Git Email             | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment      | `python3 -m venv .venv`                         |
| Activate Virtual Environment    | `source .venv/bin/activate` (Linux/Mac) / `.venv\Scripts\activate` (Windows) |
| Install Python Packages         | `pip install -r requirements.txt`               |

## Docker Commands
| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Start All Services              | `docker compose up -d`                          |
| Stop All Services               | `docker compose down`                           |
| View Logs                       | `docker compose logs -f`                        |
| Rebuild Images                  | `docker compose build`                          |
| Clean Everything                | `docker compose down -v --rmi all`              |

## Git Commands
| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Check Status                    | `git status`                                    |
| Stage All Changes               | `git add .`                                     |
| Commit Changes                  | `git commit -m "Your message"`                  |
| Push to Remote                  | `git push origin main`                          |
| Pull Latest Changes             | `git pull origin main`                          |

---

# 📋 Important Notes

- **Python 3.10+** required (Python 3.12 recommended)
- **Always use virtual environments** (`.venv`) for Python projects
- **Create `.env` file** from `.env.example` before running the application
- **Change JWT secrets** in production environment
- **Docker** is optional but recommended for full-stack development with database
- Run `./scripts/dev.sh` for the fastest development setup

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
