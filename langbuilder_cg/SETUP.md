# LangBuilder First-Time Setup Guide

This guide will help you set up and run the project for the first time.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Environment Configuration](#environment-configuration)
4. [Starting Services](#starting-services)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

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
# Create Python virtual environment with uv (REQUIRED)
uv venv

# Install backend dependencies using uv
make install_backend

# Install frontend dependencies
make install_frontend
```

**Important:** You must create the virtual environment with `uv venv` before running `make install_backend`. The backend commands require a virtual environment to be present in the `.venv` directory.

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

The project consists of 3 services that need to be started:

### Option A: Start OpenWebUI_CG with Automated Script (Recommended)

```bash
./openwebui_cg/start_openwebui_cg.sh
```

**What it does:**
- Automatically checks and installs frontend dependencies (npm install --legacy-peer-deps)
- Automatically checks and installs backend dependencies (pip install)
- Clears ports 8767 (backend) and 5175 (frontend)
- Starts both backend and frontend services
- Works on both Linux (production) and Windows (development)

**Expected output:**
```
========================================
   OpenWebUI_CG Stack Startup
========================================
✓ Frontend dependencies OK
✓ Backend dependencies OK
✓ Port 8767 is available
✓ Port 5175 is available
Backend started (PID: XXXX)
Frontend started (PID: YYYY)
========================================
✓ OpenWebUI_CG Stack Running!
========================================
  Frontend: http://localhost:5175
  Backend:  http://localhost:8767
```

### Option B: Start Services Manually (2 Terminals)

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

### Terminal 2 (or 3 if using Option B): LangBuilder Backend

```bash
./start_langbuilder_stack.sh
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


## Quick Reference

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| OpenWebUI Frontend | 5175 | http://localhost:5175 |
| OpenWebUI Backend | 8767 | http://localhost:8767 |
| LangBuilder Frontend | 3000 | http://localhost:3000 |
| LangBuilder Backend | 8002 | http://localhost:8002 |
