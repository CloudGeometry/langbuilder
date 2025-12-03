# Installation Steps for LangBuilder_CG

## Prerequisites

1. **Python 3.11+**
2. **Node.js 18.13.0 to 22.x.x**
3. **npm 6.0.0+**
4. **uv (Python package manager)** - Install with: `pipx install uv`

## Installation Steps

### 1. Create Virtual Environment (REQUIRED)

```bash
# Navigate to langbuilder_cg directory
cd langbuilder_cg

# Create Python virtual environment with uv
uv venv
```

### 2. Install Dependencies

```bash
# Install backend dependencies
make install_backend

# Install frontend dependencies
make install_frontend
```

## Starting Services

### OPTION A - Start LangBuilder Stack (Recommended):
```bash
./start_langbuilder_stack.sh
```

### OPTION B - Start Services Manually:
```bash
# Terminal 1: Backend
make backend port=8765

# Terminal 2: Frontend
make frontend
```

## Troubleshooting

### Error: "No virtual environment found"

This error occurs if you haven't created the virtual environment. Run:
```bash
uv venv
make install_backend
```

### Error: "uv is not installed"

Install uv using pipx:
```bash
pipx install uv
```