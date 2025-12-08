# Docker Development Environment Guide

This guide explains how to run the complete LangBuilder platform using Docker for local development.

## Why Use Docker for Development?

✅ **Consistent Environment**: Everyone on the team uses the same versions of Python, Node.js, and dependencies
✅ **No Local Installation**: No need to install Python, Node.js, PostgreSQL, or uv on your machine
✅ **Hot Reload**: Code changes are immediately reflected without rebuilding containers
✅ **Easy Setup**: One command to start everything
✅ **Isolated**: Keeps your system clean and prevents dependency conflicts
✅ **Production-Like**: Matches production environment more closely

---

## Prerequisites

1. **Docker Desktop** (required)
   - Download from: https://www.docker.com/products/docker-desktop
   - Make sure Docker Desktop is running before starting services

2. **Git** (for cloning the repository)

That's it! No need for Python, Node.js, npm, or uv.

---

## Quick Start

### 1. Start All Services

```bash
./start-docker-dev.sh up
```

This will:
- Build all Docker images (first time only, takes 5-10 minutes)
- Start PostgreSQL database
- Start LangBuilder backend and frontend
- Start OpenWebUI backend and frontend
- Enable hot-reload for all services

### 2. Access the Applications

After startup completes, open your browser:

- **OpenWebUI Frontend**: http://localhost:5175
- **OpenWebUI Backend API**: http://localhost:8767/docs
- **LangBuilder Frontend**: http://localhost:3000
- **LangBuilder Backend API**: http://localhost:8002/docs

### 3. Connect OpenWebUI to LangBuilder

To use LangBuilder workflows as AI models in OpenWebUI:

1. **Generate API Key in LangBuilder:**
   - Open http://localhost:3000
   - Go to **Settings** → **API Keys**
   - Click **Generate New API Key** and copy it

2. **Configure Connection in OpenWebUI:**
   - Open http://localhost:5175
   - Go to **Admin Panel** → **Settings** → **Connections**
   - Click **Add Connection** under "Manage OpenAI API Connections"
   - Fill in:
     - **Name**: `LangBuilder`
     - **API Base URL**: `http://langbuilder-backend:8002/v1`
     - **API Key**: (paste the key from step 1)
   - Click **Save**

> ⚠️ **Important:** Use `http://langbuilder-backend:8002/v1` (not `localhost`). Docker containers communicate through an internal network where `localhost` refers to the container itself, not your host machine. The service name `langbuilder-backend` resolves to the correct container.

### 4. Start Developing

Edit any file in your IDE:
- Backend changes (Python) → Auto-reloads immediately
- Frontend changes (React/Svelte) → Hot-module-replacement (HMR) updates browser

---

## Common Commands

### Start Services
```bash
./start-docker-dev.sh up
# or simply
./start-docker-dev.sh
```

### Stop Services (keep data)
```bash
./start-docker-dev.sh stop
```

### View Logs
```bash
# All services
./start-docker-dev.sh logs

# Specific service
./start-docker-dev.sh logs langbuilder-backend
./start-docker-dev.sh logs langbuilder-frontend
./start-docker-dev.sh logs openwebui-backend
./start-docker-dev.sh logs openwebui-frontend
```

### Restart Services
```bash
./start-docker-dev.sh restart
```

### Stop and Remove Containers
```bash
./start-docker-dev.sh down
```

### Stop and Remove Everything (including data)
```bash
./start-docker-dev.sh down-volumes
```
⚠️ **Warning**: This deletes your database and all persistent data!

### Check Container Status
```bash
./start-docker-dev.sh status
```

### Rebuild Containers
```bash
# Normal rebuild
./start-docker-dev.sh build

# Force rebuild without cache (if dependencies changed)
./start-docker-dev.sh rebuild
```

### Execute Commands in Containers
```bash
# Open bash shell in a container
./start-docker-dev.sh exec langbuilder-backend bash
./start-docker-dev.sh exec openwebui-backend bash

# Run a specific command
./start-docker-dev.sh exec langbuilder-backend python --version
./start-docker-dev.sh exec postgres psql -U langbuilder -d langbuilder
```

---

## Architecture Overview

### Services

| Service | Description | Port | Hot Reload |
|---------|-------------|------|------------|
| **postgres** | PostgreSQL 16 database | 5432 | N/A |
| **langbuilder-backend** | Python 3.12 + FastAPI | 8002 | ✅ Yes |
| **langbuilder-frontend** | Node.js 20 + React + Vite | 3000 | ✅ Yes (HMR) |
| **openwebui-backend** | Python 3.11 + FastAPI | 8767 (internal: 8080) | ✅ Yes |
| **openwebui-frontend** | Node.js 22 + SvelteKit | 5175 | ✅ Yes (HMR) |

### Volume Mounts (for Hot Reload)

Code is mounted from your local filesystem into containers:

**LangBuilder Backend:**
- `./langbuilder/src` → `/app/src`
- Changes to Python files trigger auto-reload

**LangBuilder Frontend:**
- `./langbuilder/src/frontend` → `/app`
- Vite dev server provides HMR

**OpenWebUI Backend:**
- `./openwebui/backend` → `/app/backend`
- Uvicorn auto-reload enabled

**OpenWebUI Frontend:**
- `./openwebui/src` → `/app/src`
- SvelteKit dev server provides HMR

### Persistent Volumes

Data that persists across container restarts:

- `postgres-data`: PostgreSQL database
- `langbuilder-venv`: Python virtual environment (faster rebuilds)
- `openwebui-data`: OpenWebUI user data

---

## Configuration

### Environment Variables

Edit `.env.docker` to customize:

```bash
# Database
LANGBUILDER_DATABASE_URL=postgresql://langbuilder:langbuilder@postgres:5432/langbuilder

# API Keys
OPENAI_API_KEY=your-key-here

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret

# Ports (external)
FRONTEND_PORT=5175
BACKEND_PORT=8002
OPEN_WEBUI_PORT=8767
VITE_PORT=3000
```

After changing `.env.docker`, restart services:
```bash
./start-docker-dev.sh restart
```

---

## Troubleshooting

### Services won't start

**Check Docker is running:**
```bash
docker info
```

**View container logs:**
```bash
./start-docker-dev.sh logs
```

### Port already in use

Kill the process using the port:
```bash
# Linux/Mac
lsof -ti:8002 | xargs kill -9

# Windows
netstat -ano | findstr :8002
taskkill /PID <PID> /F
```

Or change ports in `docker-compose.dev.yml`.

### Code changes not reflecting

**Backend (Python):**
- Check if container restarted: `./start-docker-dev.sh logs langbuilder-backend`
- If no restart, check Python syntax errors

**Frontend (React/Svelte):**
- Check browser console for errors
- Try hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

### Container keeps restarting

```bash
# Check logs for errors
./start-docker-dev.sh logs <service-name>

# Common issues:
# - Missing dependencies → rebuild: ./start-docker-dev.sh rebuild
# - Database not ready → wait a few seconds and check again
# - Port conflict → change port in docker-compose.dev.yml
```

### Out of disk space

```bash
# Remove old containers and images
docker system prune -a

# Remove volumes (⚠️ deletes data)
./start-docker-dev.sh down-volumes
```

### Dependencies not updating

If you added new dependencies:

**Python (LangBuilder):**
```bash
# Rebuild container to reinstall dependencies
./start-docker-dev.sh rebuild
```

**Node.js:**
```bash
# Rebuild container
./start-docker-dev.sh rebuild

# Or manually install in running container
./start-docker-dev.sh exec langbuilder-frontend npm install
```

### Database connection errors

```bash
# Check postgres is running
./start-docker-dev.sh status

# Check postgres logs
./start-docker-dev.sh logs postgres

# Reset database (⚠️ deletes all data)
./start-docker-dev.sh down-volumes
./start-docker-dev.sh up
```

### Can't connect to Ollama

If using Ollama on your host machine:
- Make sure Ollama is running: `ollama serve`
- Use `http://host.docker.internal:11434` in `.env.docker`

### OpenWebUI can't connect to LangBuilder

If you get "connection refused" or "not found" errors when configuring LangBuilder in OpenWebUI:

**Problem:** You're using `http://localhost:8002/v1` as the API URL.

**Solution:** Use the Docker service name instead:
```
http://langbuilder-backend:8002/v1
```

**Why?** Inside Docker containers, `localhost` refers to the container itself, not your host machine. Containers on the same Docker network communicate using service names defined in `docker-compose.dev.yml`.

| Setup | Correct API Base URL |
|-------|---------------------|
| Docker | `http://langbuilder-backend:8002/v1` |
| Local/Manual | `http://localhost:8002/v1` |

---

## Development Workflow

### Typical Day

1. **Start services:**
   ```bash
   ./start-docker-dev.sh up
   ```

2. **Open your IDE** and start coding

3. **View changes** in browser (auto-reloads)

4. **Check logs** if something breaks:
   ```bash
   ./start-docker-dev.sh logs
   ```

5. **Stop services** when done:
   ```bash
   ./start-docker-dev.sh stop
   ```

### Adding Dependencies

**Python (pyproject.toml):**
1. Add dependency to `pyproject.toml`
2. Rebuild container:
   ```bash
   ./start-docker-dev.sh rebuild
   ```

**Node.js (package.json):**
1. Add dependency to `package.json`
2. Rebuild container:
   ```bash
   ./start-docker-dev.sh rebuild
   ```

### Database Operations

**Access PostgreSQL:**
```bash
./start-docker-dev.sh exec postgres psql -U langbuilder -d langbuilder
```

**Run migrations:**
```bash
./start-docker-dev.sh exec langbuilder-backend bash
# Then inside container:
alembic upgrade head
```

**Backup database:**
```bash
docker exec langbuilder-postgres-dev pg_dump -U langbuilder langbuilder > backup.sql
```

**Restore database:**
```bash
cat backup.sql | docker exec -i langbuilder-postgres-dev psql -U langbuilder -d langbuilder
```

---

## Comparison: Docker vs Local

| Aspect | Docker Development | Local Development |
|--------|-------------------|-------------------|
| **Setup Time** | 5-10 min (first build) | 15-30 min |
| **Prerequisites** | Docker only | Python, Node.js, uv, npm |
| **Consistency** | ✅ Same for everyone | ❌ Depends on local setup |
| **Hot Reload** | ✅ Yes | ✅ Yes |
| **Performance** | ~Same (native on Linux, slight overhead on Mac/Win) | Native |
| **Resource Usage** | Higher (containers) | Lower |
| **Isolation** | ✅ Full isolation | ❌ Shares system |
| **Database** | ✅ Included | Manual PostgreSQL setup |

---

## Next Steps

- **Production Deployment**: See `DEPLOYMENT.md` (coming soon)
- **CI/CD**: See `.github/workflows/` for GitHub Actions
- **Testing**: Run tests inside containers with `./start-docker-dev.sh exec`

---

## Need Help?

- Check logs: `./start-docker-dev.sh logs`
- View container status: `./start-docker-dev.sh status`
- Restart everything: `./start-docker-dev.sh restart`
- Full reset: `./start-docker-dev.sh down-volumes && ./start-docker-dev.sh up`

For more help:
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Docker Documentation: https://docs.docker.com/
