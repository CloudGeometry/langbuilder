# macOS Setup Guide for LangBuilder

When you clone LangBuilder from GitHub onto a Mac, there are several issues you'll encounter that need to be fixed before the platform will run. This guide walks through exactly what needs to be done.

## Prerequisites

Install these first:

```bash
# Python 3.11 (required - Python 3.13 is NOT compatible with OpenWebUI)
brew install python@3.11

# Node.js
brew install node

# uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Step 1: Clone and Configure

```bash
git clone https://github.com/CloudGeometry/LangBuilder.git
cd LangBuilder

# Create your .env file
cp .env.example .env
# Edit .env with your API keys, OAuth credentials, etc.
```

## Step 2: Fix OpenWebUI Code Bug

**Problem:** The backend won't start because `WEBUI_NAME` is imported but never defined.

**Fix:** Edit `openwebui/backend/open_webui/env.py` and add this line around line 114 (near `WEBUI_FAVICON_URL`):

```python
WEBUI_NAME = os.environ.get("WEBUI_NAME", "Open WebUI")
```

## Step 3: Setup OpenWebUI

```bash
cd openwebui

# Create virtual environment with Python 3.11 specifically
python3.11 -m venv .venv

# Install backend dependencies
.venv/bin/pip install -r backend/requirements.txt

# Install frontend dependencies
npm install --legacy-peer-deps

# Install missing y-protocols package (required for TipTap editor)
npm install y-protocols --legacy-peer-deps

cd ..
```

## Step 4: Setup LangBuilder

```bash
cd langbuilder

# Create virtual environment
uv venv

# Install dependencies
make install_backend
make install_frontend
```

**Critical:** Create the local `.env` file. Vite reads from `langbuilder/.env`, not the root `.env`:

```bash
cat > .env << 'EOF'
# LangBuilder Frontend Configuration
VITE_PROXY_TARGET=http://localhost:8002
VITE_PORT=3000
EOF
```

```bash
cd ..
```

## Step 5: Handle Database Migration (if needed)

If you see this error when starting:
```
sqlite3.OperationalError: table publish_record already exists
```

Fix it by stamping the migration:
```bash
cd langbuilder
uv run alembic stamp head
cd ..
```

Or delete the database for a fresh start:
```bash
rm langbuilder/src/backend/base/langbuilder/langbuilder.db
```

## Step 6: Start Everything

```bash
./start_all_macos.sh
```

The script will run pre-flight checks and tell you if anything is missing.

## Service URLs

| Service | URL |
|---------|-----|
| OpenWebUI Frontend | http://localhost:5175 |
| OpenWebUI Backend | http://localhost:8767 |
| LangBuilder Frontend | http://localhost:3000 |
| LangBuilder Backend | http://localhost:8002 |

---

## Summary of Fixes Required

| What | Why | Fix |
|------|-----|-----|
| Use Python 3.11 | Python 3.13 breaks OpenWebUI dependencies | `brew install python@3.11` |
| Add WEBUI_NAME to env.py | Code bug - variable imported but not defined | Add line to `openwebui/backend/open_webui/env.py` |
| Install y-protocols | Missing npm dependency for TipTap editor | `npm install y-protocols --legacy-peer-deps` |
| Create langbuilder/.env | Vite reads wrong .env file, proxy fails | Create file with `VITE_PROXY_TARGET` |
| Use macOS startup scripts | Original scripts have Windows paths | Use `start_all_macos.sh` |

---

## Troubleshooting

### "Cannot import WEBUI_NAME"
You forgot Step 2. Add the WEBUI_NAME line to env.py.

### "Could not resolve y-protocols/awareness"
You forgot to install y-protocols:
```bash
cd openwebui && npm install y-protocols --legacy-peer-deps
```

### Vite proxy returns 500 errors / ECONNREFUSED
The `langbuilder/.env` file is missing or doesn't have `VITE_PROXY_TARGET`:
```bash
echo "VITE_PROXY_TARGET=http://localhost:8002" > langbuilder/.env
```

### "table publish_record already exists"
```bash
cd langbuilder && uv run alembic stamp head
```

### Port already in use
```bash
# Find and kill the process
lsof -ti:8002 | xargs kill -9  # LangBuilder backend
lsof -ti:3000 | xargs kill -9  # LangBuilder frontend
lsof -ti:8767 | xargs kill -9  # OpenWebUI backend
lsof -ti:5175 | xargs kill -9  # OpenWebUI frontend
```
