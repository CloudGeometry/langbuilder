# Langbuilder Platform by Cloud Geometry

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

1. **Python 3.11 or 3.12 (recommended)**
   - **macOS (recommended):**
     ```bash
     brew install python@3.11
     ```
   - **Other platforms:** Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python3.11 --version`
   - **Important**: Python 3.13+ is too new and has compatibility issues. Use Python 3.11 or 3.12 for production deployments.
   - **Note**: On macOS, the system Python is typically 3.9.x. You must explicitly use `python3.11` for all commands.

2. **Node.js 20.19.0+ or 22.x.x LTS (recommended) and npm 6.0.0+**
   - Download from [nodejs.org](https://nodejs.org/)
   - **Recommended**: Use nvm (Node Version Manager) for easier version management:
     ```bash
     # Install nvm
     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
     source ~/.bashrc

     # Install Node.js 22 LTS
     nvm install 22
     nvm use 22
     nvm alias default 22
     ```
   - Verify installation:
     ```bash
     node --version  # Should show v22.x.x or v20.19.0+
     npm --version
     ```

3. **uv (Python package manager)**
   - **Recommended (curl installer):**
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
     **Important:** After installation, add to your PATH:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```
     Add this line to your `~/.bashrc` or `~/.zshrc` for persistence.
   - **Alternative (via pipx):**
     ```bash
     pipx install uv
     ```
   - Verify installation: `uv --version`

4. **Git Bash or WSL** (Windows users)
   - Git Bash comes with [Git for Windows](https://git-scm.com/download/win)
   - Or install [WSL](https://docs.microsoft.com/en-us/windows/wsl/install)

### Optional but Recommended

5. **Docker Desktop**
   - Download from [docker.com](https://www.docker.com/products/docker-desktop)
   - Required for some OpenWebUI features
   - Start Docker Desktop before running services

---

## Installation


### Step 1: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your favorite editor
nano .env  # or code .env, vim .env, etc.
```

**Important:** After copying `.env.example`, you must fix the port configuration. Change these lines:
```bash
# Change FROM:
OPEN_WEBUI_PORT=${BACKEND_PORT}
PORT=${BACKEND_PORT}

# Change TO:
OPEN_WEBUI_PORT=8767
PORT=8767
```

The `${BACKEND_PORT}` variable reference syntax doesn't work with the startup scripts.

---

### Step 2: Set Up Python Virtual Environment for OpenWebUI

```bash
# Navigate to openwebui directory
cd openwebui

# Create virtual environment (MUST use python3.11 explicitly)
python3.11 -m venv .venv

# Install backend dependencies (no need to activate venv)
.venv/bin/pip install -r backend/requirements.txt

# Install frontend dependencies
# Note: Use --legacy-peer-deps due to @tiptap version conflicts
npm install --legacy-peer-deps

# Install y-protocols (required for TipTap collaborative editor)
npm install y-protocols --legacy-peer-deps

cd ..
```

**Note:** On macOS, do not use `python` or `python3` as these may point to older system versions. Always use `python3.11` explicitly.

### Step 3: Install LangBuilder Dependencies

```bash
cd langbuilder

# Create Python virtual environment with uv
uv venv

# Install backend dependencies using uv
make install_backend

# Install frontend dependencies
make install_frontend
```

**Critical:** Create the LangBuilder frontend environment file. Without this, the frontend cannot connect to the backend:

```bash
# Create langbuilder/.env file (REQUIRED)
cat > .env << 'EOF'
VITE_PROXY_TARGET=http://localhost:8002
VITE_PORT=3000
EOF
```

```bash
cd ..
```

**Note:** The `uv venv` command creates a Python virtual environment in the `.venv` directory. This is required before running any backend commands.

---

## Starting Services

The project consists of 2 main stacks that need to be started:

### Option A: Start Everything with One Command (Easiest)

**macOS:**
```bash
./start_all_macos.sh
```

**Linux/Windows (Git Bash):**
```bash
./start_all.sh
```

**What it does:**
- Runs pre-flight checks to verify dependencies
- Starts OpenWebUI_CG (backend + frontend)
- Waits for initialization
- Starts LangBuilder_CG (backend + frontend)
- All services run together

**Expected URLs:**
- OpenWebUI Frontend: http://localhost:5175
- OpenWebUI Backend: http://localhost:8767
- LangBuilder Frontend: http://localhost:3000
- LangBuilder Backend: http://localhost:8002

### Option B: Start OpenWebUI_CG with Automated Script

```bash
./openwebui/start_openwebui.sh
```

**What it does:**
- Automatically checks and installs frontend dependencies (npm install --legacy-peer-deps)
- Automatically checks and installs backend dependencies (pip install)
- Clears ports 8767 (backend) and 5175 (frontend)
- Starts both backend and frontend services
- Works on both Linux (production) and Windows (development)

### Option C: Start Services Manually (Multiple Terminals)

**Terminal 1: OpenWebUI Backend**

```bash
./openwebui/backend/start_openwebui_simple.sh
```

- Starts the OpenWebUI backend API
- Runs on port `8767` (configurable via OPEN_WEBUI_PORT)
- Handles authentication, file management, and AI model interactions

**Terminal 2: OpenWebUI Frontend**

```bash
cd openwebui
npm run dev -- --port 5175
```

- Starts the OpenWebUI frontend development server
- Runs on port `5175`
- Provides the user interface for OpenWebUI

### Terminal 2 (or 3 if using Option B): LangBuilder Stack

```bash
./langbuilder/start_langbuilder_stack.sh
```

**What it does:**
- Checks Docker Desktop status
- Kills any processes on required ports
- Starts LangBuilder backend (port 8002)
- Starts LangBuilder frontend (port 3000)

**Expected output:**
```
Starting LangBuilder Stack...
Configuration:
  Backend Port: 8002
  Frontend Port: 3000
  OpenWebUI Port: 8767

✓ LangBuilder stack started!
  Backend PID: XXXX (http://localhost:8002)
  Frontend PID: YYYY (http://localhost:3000)
  OpenWebUI: http://localhost:8767
```

**Note:** The script will prompt you to confirm before starting services. Type `y` and press Enter. Ignore docker about open-webui message

---

## Verification

After starting all services, verify they're running correctly:

### 1. Check Service Status

Open your browser and navigate to:

- **OpenWebUI Frontend:** http://localhost:5175
- **LangBuilder Frontend:** http://localhost:3000
- **OpenWebUI Backend API:** http://localhost:8767/docs
- **LangBuilder Backend API:** http://localhost:8002/docs

### 2. Check Process Status

```bash
# Check if all ports are in use
netstat -ano | grep "LISTENING" | grep -E "(5175|3000|8767|8002)"

# Or use the ports individually
netstat -ano | findstr :5175
netstat -ano | findstr :3000
netstat -ano | findstr :8767
netstat -ano | findstr :8002
```

### 3. Check Logs

Look for error messages in each terminal window. All services should show they're running without errors.

---

## Connecting OpenWebUI with LangBuilder

After verifying all services are running correctly, you need to connect OpenWebUI with LangBuilder to use LangBuilder workflows as AI providers in your chat interface.

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
   - **API Base URL**: `http://localhost:8002/v1`
   - **API Key**: Paste the API key you generated in Step 1
8. Click **Save** or **Add Connection**

### Step 3: Verify the Connection

1. Go back to the main OpenWebUI chat interface
2. Start a new conversation
3. Select the **LangBuilder** provider from the model dropdown
4. Send a test message to verify the connection is working

**Note:** Make sure both LangBuilder backend (port 8002) and OpenWebUI (port 5175) are running before attempting to connect them.

---

## Troubleshooting

### Common Issues

**"Invalid value for '--port': '${BACKEND_PORT}' is not a valid integer"**
- The `.env` file contains variable references that aren't evaluated
- Fix: Change `OPEN_WEBUI_PORT=${BACKEND_PORT}` to `OPEN_WEBUI_PORT=8767` in your `.env` file

**"Could not resolve y-protocols/awareness"**
- Missing npm dependency for the TipTap editor
- Fix: `cd openwebui && npm install y-protocols --legacy-peer-deps`

**Vite proxy returns 500 errors / ECONNREFUSED**
- The `langbuilder/.env` file is missing or misconfigured
- Fix: Create `langbuilder/.env` with:
  ```
  VITE_PROXY_TARGET=http://localhost:8002
  VITE_PORT=3000
  ```

**Python version errors / module not found**
- Using wrong Python version (system Python is often 3.9.x)
- Fix: Always use `python3.11` explicitly, not `python` or `python3`

**uv: command not found**
- uv is not in PATH after installation
- Fix: Add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile

**Port already in use**
```bash
# Kill processes on specific ports (macOS/Linux)
lsof -ti:8002 | xargs kill -9  # LangBuilder backend
lsof -ti:3000 | xargs kill -9  # LangBuilder frontend
lsof -ti:8767 | xargs kill -9  # OpenWebUI backend
lsof -ti:5175 | xargs kill -9  # OpenWebUI frontend
```

For more detailed troubleshooting steps, see [INSTALL_STEPS.md](INSTALL_STEPS.md#troubleshooting) and [MACOS_SETUP_ISSUES.md](MACOS_SETUP_ISSUES.md).
