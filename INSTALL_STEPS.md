# Installation Steps for LangBuilder Platform

## Prerequisites

Ensure you have the following installed:

1. **Python 3.11 or 3.12 (recommended)** - `python --version`
   - **Note**: Python 3.13+ is too new and has compatibility issues with some dependencies. Use Python 3.12 for best compatibility.
   - **Recommended**: Use pyenv for version management on newer Ubuntu versions (25.04+)
2. **Node.js 20.19.0+ or 22.x.x LTS (recommended)** - `node --version`
   - **Recommended**: Use nvm (Node Version Manager) for version management
3. **npm 6.0.0+** - `npm --version`
4. **uv (Python package manager)** - Install with: `pipx install uv`
5. **Git** - For cloning the repository

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LangBuilder
```

### 2. Set Up OpenWebUI_CG

```bash
cd openwebui

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows (Git Bash):
# source .venv/Scripts/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
npm install --legacy-peer-deps

cd ..
```

### 3. Set Up LangBuilder_CG

```bash
cd langbuilder

# Create Python virtual environment with uv (REQUIRED)
uv venv

# Install backend dependencies
make install_backend

# Install frontend dependencies
make install_frontend

cd ..
```

**Important Notes:**
- On **Windows**: Use Git Bash or WSL to run these commands
- The scripts are **cross-platform** and work on Windows, Linux, and macOS
- If `uv venv` fails on Windows, remove `.venv` manually first: `rm -rf .venv`

### 4. Configure Environment Variables

Review and update the `.env` file in the root directory with your API keys and configuration.

## Starting Services

### OPTION A - Start All Services (Recommended):
```bash
./start_all.sh
```

### OPTION B - Start OpenWebUI_CG Only:
```bash
./openwebui/start_openwebui.sh
```

### OPTION C - Start LangBuilder_CG Only:
```bash
./langbuilder/start_langbuilder_stack.sh
```

### OPTION D - Start Services Manually:
```bash
# Terminal 1: OpenWebUI Backend
./openwebui/backend/start_openwebui_simple.sh

# Terminal 2: OpenWebUI Frontend
cd openwebui && npm run dev -- --port 5175

# Terminal 3: LangBuilder Backend
cd langbuilder && make backend port=8002

# Terminal 4: LangBuilder Frontend
cd langbuilder && make frontend
```

## Service URLs

- **OpenWebUI Frontend**: http://localhost:5175
- **OpenWebUI Backend**: http://localhost:8767
- **LangBuilder Frontend**: http://localhost:3000
- **LangBuilder Backend**: http://localhost:8002

---

## Connecting OpenWebUI with LangBuilder

After everything is working correctly, you need to connect OpenWebUI with LangBuilder to use LangBuilder workflows as AI providers.

### Step 1: Generate an API Key in LangBuilder

1. Open LangBuilder Frontend: http://localhost:3000
2. Navigate to **Settings** or **API Keys** section
3. Click **Generate New API Key** or **Create API Key**
4. Copy the generated API key (save it securely, you'll need it in the next step)

### Step 2: Configure LangBuilder as OpenAI Provider in OpenWebUI

1. Open OpenWebUI Frontend: http://localhost:5175
2. Click on your **username** at the **bottom left** corner
3. Select **Admin Panel**
4. Navigate to **Settings** → **Connections**
5. Find **Manage OpenAI API Connections** section
6. Click **Add Connection**
7. Fill in the connection details:
   - **Name**: `LangBuilder` (or any name you prefer)
   - **API Base URL**: See table below depending on your setup
   - **API Key**: Paste the API key you generated in Step 1
8. Click **Save** or **Add Connection**

#### API Base URL Configuration

| Setup Type | API Base URL |
|------------|--------------|
| **Docker** (using `./start-docker-dev.sh`) | `http://langbuilder-backend:8002/v1` |
| **Local/Manual** (using `./start_all.sh` or manual) | `http://localhost:8002/v1` |

> **Important:** When running with Docker, containers communicate through an internal network. Using `localhost` inside a container refers to the container itself, not your host machine. Use the Docker service name `langbuilder-backend` instead.

### Step 3: Verify the Connection

1. Go back to the main OpenWebUI chat interface
2. Start a new conversation
3. Select the **LangBuilder** provider from the model dropdown
4. Send a test message to verify the connection is working

**Note:** Make sure both LangBuilder backend (port 8002) and OpenWebUI (port 5175) are running before attempting to connect them.

---

## Troubleshooting

### Error: "No virtual environment found"

If you get this error when running `make backend`:
```bash
cd langbuilder
uv venv
make install_backend
```

### Error: "Función incorrecta" or "Failed to create virtual environment" (Windows)

On Windows, if `uv venv` fails to replace an existing virtual environment:
```bash
cd langbuilder
# Remove the old virtual environment
rm -rf .venv
# Create a new one
uv venv
make install_backend
```

### Error: "ModuleNotFoundError: No module named 'langbuilder'"

This means the backend dependencies are not installed:
```bash
cd langbuilder
uv venv
make install_backend
```

## Verifying Services

Check if all ports are running:
```bash
# Using ss (recommended)
ss -tlnp | grep -E ':(3000|8002|8767|5175)'

# Or check each port individually
for port in 3000:LangBuilder-Frontend 8002:LangBuilder-Backend 8767:OpenWebUI-Backend 5175:OpenWebUI-Frontend; do
  p=$(echo $port | cut -d: -f1)
  name=$(echo $port | cut -d: -f2)
  echo -n "$name (port $p): "
  ss -tlnp | grep ":$p " > /dev/null && echo "✓ Running" || echo "✗ Not running"
done
```

### Error: "uv is not installed"

Install uv using pipx:
```bash
pipx install uv
```

Or follow the instructions at: https://github.com/astral-sh/uv