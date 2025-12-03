# Langbuilder Platform by Cloud Geometry

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

1. **Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **Node.js (18.13.0 to 22.x.x) and npm (6.0.0+)**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify installation:
     ```bash
     node --version
     npm --version
     ```

3. **uv (Python package manager)**
   - Install via pipx:
     ```bash
     pipx install uv
     ```
   - Or follow instructions at [uv documentation](https://github.com/astral-sh/uv)
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


### Step 2: Set Up Python Virtual Environment for OpenWebUI

```bash
# Navigate to openwebui_cg directory
cd openwebui_cg

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (Git Bash):
source .venv/Scripts/activate
# On Linux/Mac:
# source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
# Note: Use --legacy-peer-deps due to @tiptap version conflicts
npm install --legacy-peer-deps

cd ..
```

### Step 3: Install LangBuilder Dependencies

```bash
cd langbuilder_cg

# Create Python virtual environment with uv
uv venv

# Install backend dependencies using uv
make install_backend

# Install frontend dependencies
make install_frontend

cd ..
```

**Note:** The `uv venv` command creates a Python virtual environment in the `.venv` directory. This is required before running any backend commands.

---

## Environment Configuration

### Step 1: Configure Environment Variables

The project includes a `.env` file in the root directory. Review and update it with your API keys and configuration:

```bash
# Edit .env file with your favorite editor
nano .env  # or code .env, vim .env, etc.
```

---

## Starting Services

The project consists of 2 main stacks that need to be started:

### Option A: Start Everything with One Command (Easiest)

```bash
./start_all.sh
```

**What it does:**
- Starts OpenWebUI_CG (backend + frontend)
- Waits for initialization
- Starts LangBuilder_CG (backend + frontend)
- All services run together

**Expected URLs:**
- OpenWebUI Frontend: http://localhost:5175
- OpenWebUI Backend: http://localhost:8767
- LangBuilder Frontend: http://localhost:8766
- LangBuilder Backend: http://localhost:8765

### Option B: Start OpenWebUI_CG with Automated Script

```bash
./openwebui_cg/start_openwebui_cg.sh
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
./openwebui_cg/backend/start_openwebui_simple.sh
```

- Starts the OpenWebUI backend API
- Runs on port `8767` (configurable via OPEN_WEBUI_PORT)
- Handles authentication, file management, and AI model interactions

**Terminal 2: OpenWebUI Frontend**

```bash
cd openwebui_cg
npm run dev -- --port 5175
```

- Starts the OpenWebUI frontend development server
- Runs on port `5175`
- Provides the user interface for OpenWebUI

### Terminal 2 (or 3 if using Option B): LangBuilder Stack

```bash
./langbuilder_cg/start_langbuilder_stack.sh
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
