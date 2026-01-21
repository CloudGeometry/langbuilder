# Day 1 Setup Guide

Get LangBuilder running on your machine in 30 minutes or less.

## Prerequisites

Before starting, ensure you have the following installed:

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.10 - 3.13 | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **uv** | Latest | [uv installer](https://docs.astral.sh/uv/getting-started/installation/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

### Optional (for Docker development)

| Tool | Version | Installation |
|------|---------|--------------|
| **Docker** | 20+ | [docker.com](https://www.docker.com/get-started) |
| **Docker Compose** | 2.0+ | Included with Docker Desktop |

### Verify Prerequisites

```bash
# Check Python version (should be 3.10-3.13)
python --version

# Check Node.js version (should be 18+)
node --version

# Check npm version
npm --version

# Check uv is installed
uv --version

# Check Git
git --version
```

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/CloudGeometry/langbuilder.git

# Navigate to the project root
cd langbuilder
```

## Step 2: Environment Configuration

### Copy Environment File

```bash
# Navigate to the langbuilder package directory
cd langbuilder

# Copy the example environment file
cp .env.example .env
```

### Essential Environment Variables

Edit the `.env` file and configure these essential variables:

```bash
# Ports (default values work for local development)
FRONTEND_PORT=5175
BACKEND_PORT=8002

# CORS Configuration for local development
CORS_ALLOW_ORIGIN="http://localhost:5175;http://localhost:8002"

# Database (SQLite for development - no setup needed)
DATA_DIR='./data'
DATABASE_URL='sqlite:///./data/webui.db'

# Optional: Add your API keys for testing AI features
OPENAI_API_KEY=your-openai-key-here
```

### API Keys (Optional for Day 1)

You can add API keys later. For initial setup, the application will work without them, but AI features will be limited.

## Step 3: Backend Setup

```bash
# From the langbuilder/ directory (not the repo root)
cd langbuilder

# Install Python dependencies using uv
uv sync --frozen

# This will:
# - Create a .venv directory with a virtual environment
# - Install all backend dependencies
# - Install langbuilder-base as an editable package
```

**Expected output**: Dependencies installed with no errors. This may take 2-5 minutes on first run.

## Step 4: Frontend Setup

```bash
# Navigate to frontend directory
cd src/frontend

# Install Node.js dependencies
npm install

# Return to langbuilder directory
cd ../..
```

**Expected output**: `npm install` completes with no critical errors (warnings are OK).

## Step 5: Initialize the Project

The Makefile provides convenient commands. From the `langbuilder/` directory:

```bash
# Full initialization (installs both backend and frontend dependencies)
make init
```

This command:
1. Verifies required tools are installed
2. Installs backend dependencies
3. Installs frontend dependencies
4. Sets up pre-commit hooks

## Step 6: Start the Application

### Option A: Run Backend and Frontend Separately (Recommended for Development)

**Terminal 1 - Backend:**
```bash
# From langbuilder/ directory
make backend
```

**Terminal 2 - Frontend:**
```bash
# From langbuilder/src/frontend directory
npm start
```

### Option B: Run with Single Command

```bash
# From langbuilder/ directory
uv run langbuilder run
```

This builds the frontend and serves everything from the backend on port 8002.

## Step 7: Verify Everything Works

### Access the Application

Open your browser and navigate to:

- **Frontend (if running separately)**: http://localhost:5175
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs

### Verify Backend Health

```bash
# Check API is responding
curl http://localhost:8002/health

# Expected response: {"status": "ok"}
```

### Verify Frontend Loads

1. Open http://localhost:5175 in your browser
2. You should see the LangBuilder login/welcome page
3. Create an account or log in

### Create Your First Flow

1. Click "New Flow" or similar button
2. The flow canvas should load
3. You should see a component sidebar with available nodes
4. Try dragging a component onto the canvas

## Troubleshooting First-Run Issues

### Port Already in Use

```bash
# Find process using port 8002
# On macOS/Linux:
lsof -i :8002

# On Windows:
netstat -ano | findstr :8002

# Kill the process or use different ports in .env
```

### Python Version Issues

```bash
# If you have multiple Python versions, specify version with uv
uv python install 3.12
uv venv --python 3.12
```

### npm Install Fails

```bash
# Clear npm cache and try again
cd src/frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### uv Not Found

```bash
# Install uv using pip or pipx
pipx install uv

# Or on macOS with Homebrew
brew install uv

# Or using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Missing Environment Variables

If you see errors about missing configuration:

```bash
# Ensure you have the .env file
ls -la .env

# If missing, copy from example
cp .env.example .env
```

## What You've Accomplished

By completing this guide, you have:

- Installed all required development tools
- Cloned and configured the LangBuilder repository
- Set up the Python backend with uv
- Set up the React frontend with npm
- Started both backend and frontend services
- Verified the application is running correctly

## Next Steps

1. Explore the UI and create a simple flow
2. Read [Week 1 Guide](./week-1-guide.md) for structured learning
3. Review [Local Development](./local-development.md) for advanced setup options

## Quick Reference

| Action | Command |
|--------|---------|
| Start backend | `make backend` |
| Start frontend | `cd src/frontend && npm start` |
| Run tests | `make unit_tests` |
| Format code | `make format` |
| Check linting | `make lint` |

---

*Generated by CloudGeometry AIx SDLC - Onboarding Documentation*
