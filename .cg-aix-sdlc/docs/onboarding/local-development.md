# Local Development Guide

Comprehensive guide for setting up and configuring your local development environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [IDE Configuration](#ide-configuration)
4. [Running the Application](#running-the-application)
5. [Hot Reload Setup](#hot-reload-setup)
6. [Docker Development](#docker-development)
7. [Database Management](#database-management)
8. [Environment Variables](#environment-variables)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Recommended Version | Installation |
|----------|-----------------|---------------------|--------------|
| Python | 3.10 | 3.12 | [python.org](https://python.org) |
| Node.js | 18.x | 20.x | [nodejs.org](https://nodejs.org) |
| uv | Latest | Latest | See below |
| Git | 2.30+ | Latest | [git-scm.com](https://git-scm.com) |

### Optional Software

| Software | Purpose | Installation |
|----------|---------|--------------|
| Docker | Container development | [docker.com](https://docker.com) |
| PostgreSQL | Production database | [postgresql.org](https://postgresql.org) |
| VS Code | IDE | [code.visualstudio.com](https://code.visualstudio.com) |
| PyCharm | IDE | [jetbrains.com](https://jetbrains.com/pycharm) |

### Installing uv

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Using pip:**
```bash
pip install uv
```

**Using pipx:**
```bash
pipx install uv
```

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/CloudGeometry/langbuilder.git
cd langbuilder
```

### 2. Backend Setup

```bash
# Navigate to the main package
cd langbuilder

# Create virtual environment and install dependencies
uv sync --frozen

# With PostgreSQL support (for production-like development)
uv sync --frozen --extra "postgresql"
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd src/frontend

# Install Node dependencies
npm install
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required for basic operation:
# - FRONTEND_PORT=5175
# - BACKEND_PORT=8002
# - DATABASE_URL=sqlite:///./data/webui.db
```

### 5. Initialize Pre-commit Hooks

```bash
# From langbuilder/ directory
uvx pre-commit install
```

---

## IDE Configuration

### VS Code

#### Recommended Extensions

Create `.vscode/extensions.json`:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "biomejs.biome"
  ]
}
```

#### Workspace Settings

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/langbuilder/.venv/Scripts/python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[typescriptreact]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "biomejs.biome"
  },
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit"
  },
  "ruff.path": ["${workspaceFolder}/langbuilder/.venv/Scripts/ruff.exe"],
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

#### Launch Configurations

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI Backend",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "--factory",
        "langbuilder.main:create_app",
        "--host",
        "0.0.0.0",
        "--port",
        "8002",
        "--reload"
      ],
      "cwd": "${workspaceFolder}/langbuilder",
      "envFile": "${workspaceFolder}/langbuilder/.env",
      "jinja": true
    },
    {
      "name": "Python: Current Test File",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "cwd": "${workspaceFolder}/langbuilder"
    },
    {
      "name": "JavaScript: Chrome Frontend",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5175",
      "webRoot": "${workspaceFolder}/langbuilder/src/frontend/src"
    }
  ]
}
```

### PyCharm

#### Project Structure

1. Open `langbuilder/` as the project root
2. Mark these as source roots:
   - `langbuilder/src/backend/base/`
   - `langbuilder/src/backend/base/langbuilder/`

#### Interpreter Configuration

1. Go to Settings > Project > Python Interpreter
2. Add new interpreter > Existing Environment
3. Select: `langbuilder/.venv/bin/python` (or `.venv/Scripts/python.exe` on Windows)

#### Run Configurations

**Backend:**
- Script: `uvicorn`
- Parameters: `--factory langbuilder.main:create_app --host 0.0.0.0 --port 8002 --reload`
- Working directory: `langbuilder/`
- Environment: Load from `.env`

**Tests:**
- pytest
- Target: `src/backend/tests/`
- Working directory: `langbuilder/`

---

## Running the Application

### Method 1: Separate Terminals (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd langbuilder
make backend

# Or manually:
uv run uvicorn --factory langbuilder.main:create_app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 2 - Frontend:**
```bash
cd langbuilder/src/frontend
npm start

# Or:
npm run dev:docker  # For Docker network access
```

### Method 2: Using Make

```bash
cd langbuilder

# Full application (builds frontend first)
uv run langbuilder run

# Or use Makefile targets
make run_cli
```

### Method 3: Docker Compose

```bash
# From repository root
docker-compose -f docker-compose.dev.yml up
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5175 | React development server |
| Backend | http://localhost:8002 | FastAPI backend |
| API Docs | http://localhost:8002/docs | Swagger UI |
| ReDoc | http://localhost:8002/redoc | Alternative API docs |

---

## Hot Reload Setup

### Backend Hot Reload

The backend uses Uvicorn's built-in reload:

```bash
uv run uvicorn --factory langbuilder.main:create_app --host 0.0.0.0 --port 8002 --reload
```

Changes to Python files automatically trigger a reload.

**Excluded from reload:**
- Test files
- Migration files
- Cache directories

### Frontend Hot Reload

Vite provides Hot Module Replacement (HMR):

```bash
npm start
```

Changes to React components update instantly in the browser.

**HMR Features:**
- Component state preservation
- CSS hot update
- Error overlay

### Combined Development

For the best experience:

1. Run backend with `--reload` flag
2. Run frontend with `npm start`
3. Both will auto-reload on changes

---

## Docker Development

### Using Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Start specific service
docker-compose -f docker-compose.dev.yml up langbuilder-backend

# Rebuild after dependency changes
docker-compose -f docker-compose.dev.yml up --build

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

### Services in Development Docker Compose

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL database |
| langbuilder-backend | 8002 | FastAPI backend |
| langbuilder-frontend | 3000 | React frontend |
| openwebui-backend | 8767 | ActionBridge backend |
| openwebui-frontend | 5175 | ActionBridge frontend |

### Docker Environment File

Create `.env.docker` for Docker-specific settings:

```bash
# Database (use container name as host)
LANGBUILDER_DATABASE_URL=postgresql://langbuilder:langbuilder@postgres:5432/langbuilder

# API settings
LANGBUILDER_HOST=0.0.0.0
LANGBUILDER_PORT=8002

# CORS for Docker network
CORS_ALLOW_ORIGIN=http://localhost:3000;http://localhost:5175;http://localhost:8002
```

### Building Individual Images

```bash
cd langbuilder

# Build all Docker images
make docker_build

# Build backend only
make docker_build_backend

# Build frontend only
make docker_build_frontend
```

---

## Database Management

### SQLite (Development)

SQLite is the default for development. No setup required.

```bash
# Database location
langbuilder/data/webui.db
```

### PostgreSQL (Production-like Development)

```bash
# Install PostgreSQL support
uv sync --frozen --extra "postgresql"

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/langbuilder
```

### Database Migrations

```bash
cd langbuilder

# Check current migration status
make alembic-current

# View migration history
make alembic-history

# Create new migration
make alembic-revision message="Add new table"

# Apply migrations
make alembic-upgrade

# Rollback one migration
make alembic-downgrade

# Check if migrations are pending
make alembic-check
```

### Fresh Database

```bash
# Remove SQLite database
rm -rf data/

# Restart backend (will recreate database)
make backend
```

---

## Environment Variables

### Essential Variables

```bash
# Port Configuration
FRONTEND_PORT=5175
BACKEND_PORT=8002

# Database
DATA_DIR='./data'
DATABASE_URL='sqlite:///./data/webui.db'

# CORS (development)
CORS_ALLOW_ORIGIN="http://localhost:5175;http://localhost:8002"
```

### AI Provider Keys (Optional)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GOOGLE_API_KEY=...

# AWS (for Bedrock)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

### OAuth Configuration (Optional)

```bash
# Google OAuth
GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-secret'
GOOGLE_REDIRECT_URI="http://localhost:8002/oauth/google/callback"

# Enable OAuth
ENABLE_OAUTH_SIGNUP=true
```

### Debug and Logging

```bash
# Log level
GLOBAL_LOG_LEVEL='DEBUG'  # or INFO, WARNING, ERROR

# Disable telemetry
SCARF_NO_ANALYTICS=true
DO_NOT_TRACK=true
ANONYMIZED_TELEMETRY=false
```

---

## Common Makefile Commands

| Command | Description |
|---------|-------------|
| `make init` | Initialize project (install all dependencies) |
| `make backend` | Start backend with hot reload |
| `make unit_tests` | Run unit tests |
| `make integration_tests` | Run integration tests |
| `make coverage` | Run tests with coverage |
| `make format` | Format all code |
| `make format_backend` | Format Python code only |
| `make lint` | Run linting |
| `make build` | Build frontend and packages |
| `make docker_build` | Build Docker images |
| `make clean_all` | Clean all caches |

### Frontend Makefile Commands

Commands for frontend development (from `langbuilder/` directory):

| Command | Description |
|---------|-------------|
| `make install_frontend` | Install npm dependencies |
| `make build_frontend` | Build frontend for production |
| `make format_frontend` | Format TypeScript/React code |

---

## Troubleshooting Development Issues

See the [Debugging Guide](./debugging-guide.md) for comprehensive troubleshooting.

### Quick Fixes

**Dependencies out of sync:**
```bash
uv sync --frozen
cd src/frontend && npm install
```

**Cache issues:**
```bash
make clean_all
```

**Port in use:**
```bash
# Find and kill process on port 8002
# macOS/Linux:
lsof -i :8002 | grep LISTEN | awk '{print $2}' | xargs kill

# Windows:
netstat -ano | findstr :8002
taskkill /PID <PID> /F
```

**Database corrupted:**
```bash
rm -rf data/
make backend
```

---

*Generated by CloudGeometry AIx SDLC - Onboarding Documentation*
