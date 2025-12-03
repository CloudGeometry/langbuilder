# Installation Steps for LangBuilder Platform

## Prerequisites

Ensure you have the following installed:

1. **Python 3.11+** - `python --version`
2. **Node.js 18.13.0 to 22.x.x** - `node --version`
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
cd openwebui_cg

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
cd langbuilder_cg

# Create Python virtual environment with uv (REQUIRED)
uv venv

# Install backend dependencies
make install_backend

# Install frontend dependencies
make install_frontend

cd ..
```

### 4. Configure Environment Variables

Review and update the `.env` file in the root directory with your API keys and configuration.

## Starting Services

### OPTION A - Start All Services (Recommended):
```bash
./start_all.sh
```

### OPTION B - Start OpenWebUI_CG Only:
```bash
./openwebui_cg/start_openwebui_cg.sh
```

### OPTION C - Start LangBuilder_CG Only:
```bash
./langbuilder_cg/start_langbuilder_stack.sh
```

### OPTION D - Start Services Manually:
```bash
# Terminal 1: OpenWebUI Backend
./openwebui_cg/backend/start_openwebui_simple.sh

# Terminal 2: OpenWebUI Frontend
cd openwebui_cg && npm run dev -- --port 5175

# Terminal 3: LangBuilder Backend
cd langbuilder_cg && make backend port=8765

# Terminal 4: LangBuilder Frontend
cd langbuilder_cg && make frontend
```

## Service URLs

- **OpenWebUI Frontend**: http://localhost:5175
- **OpenWebUI Backend**: http://localhost:8767
- **LangBuilder Frontend**: http://localhost:8766
- **LangBuilder Backend**: http://localhost:8765

## Troubleshooting

### Error: "No virtual environment found"

If you get this error when running `make backend`:
```bash
cd langbuilder_cg
uv venv
make install_backend
```

### Error: "uv is not installed"

Install uv using pipx:
```bash
pipx install uv
```

Or follow the instructions at: https://github.com/astral-sh/uv