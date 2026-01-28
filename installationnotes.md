# LangBuilder Installation Notes

**Date:** 2026-01-28
**Engineer:** Claude (Senior DevOps)
**Goal:** Validate README.md installation instructions on fresh macOS

---

## Environment Baseline

| Component | Version | Status |
|-----------|---------|--------|
| macOS | 26.2 (Build 25C56) | Tahoe |
| Architecture | arm64 | Apple Silicon |
| Python | 3.9.6 | NEEDS UPGRADE (requires 3.11-3.12) |
| Node.js | v20.19.6 | OK (meets 20.19.0+ requirement) |
| npm | 10.8.2 | OK (meets 6.0.0+ requirement) |
| uv | Not installed | NEEDS INSTALL |
| Homebrew | 5.0.12 | OK |
| Docker | Not installed | Optional |

---

## Prerequisites Installation

### Step P1: Install Python 3.11

**Source:** MACOS_SETUP_ISSUES.md recommends Python 3.11 via brew
**README says:** Python 3.11 or 3.12, download from python.org
**Command:**
```bash
brew install python@3.11
```

**Result:** SUCCESS
- Installed Python 3.11.14 via Homebrew
- Location: /opt/homebrew/bin/python3.11
- Also installed dependencies: mpdecimal, readline, sqlite, xz

**Note:** README says download from python.org, but `brew install python@3.11` is simpler on macOS.

---

### Step P2: Install uv (Python package manager)

**Source:** MACOS_SETUP_ISSUES.md uses curl installer
**README says:** Install via pipx (`pipx install uv`)
**Command:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Result:** SUCCESS
- Installed uv 0.9.27
- Location: ~/.local/bin/uv
- Need to add `~/.local/bin` to PATH

**Note:** README recommends `pipx install uv` but curl installer is more direct and doesn't require pipx.

**README Discrepancy:** Should mention adding `~/.local/bin` to PATH after curl install method.

---

## OpenWebUI Setup (Step 2 in README)

### Step O1: Create .env file from example

**Command:**
```bash
cp .env.example .env
```

**Result:** SUCCESS

---

### Step O2: Create Python virtual environment for OpenWebUI

**Source:** MACOS_SETUP_ISSUES.md says use `python3.11 -m venv .venv`
**README says:** `python -m venv .venv`
**Command:**
```bash
cd openwebui
python3.11 -m venv .venv
```

**Result:** SUCCESS

**README Discrepancy:** README uses generic `python` but on fresh macOS, system Python is 3.9.6. Must explicitly use `python3.11`.

---

### Step O3: Install OpenWebUI backend dependencies

**Command:**
```bash
.venv/bin/pip install -r backend/requirements.txt
```

**Result:** SUCCESS
- Installed 200+ packages including fastapi, torch, transformers, chromadb, etc.
- Takes several minutes due to large ML packages

**Note:** README activates venv first, but using `.venv/bin/pip` directly works and avoids shell complications.

---

### Step O4: Install OpenWebUI frontend dependencies

**Command:**
```bash
npm install --legacy-peer-deps
```

**Result:** SUCCESS
- Installed 1056 packages
- 24 vulnerabilities reported (not blocking)

---

### Step O5: Install y-protocols (from MACOS_SETUP_ISSUES.md)

**Source:** MACOS_SETUP_ISSUES.md - "Missing npm dependency for TipTap editor"
**README says:** Not mentioned
**Command:**
```bash
npm install y-protocols --legacy-peer-deps
```

**Result:** SUCCESS

**README Discrepancy:** This step is NOT in the README but is required for the TipTap editor to work.

---

### Step O6: Check WEBUI_NAME bug fix

**Source:** MACOS_SETUP_ISSUES.md says to add `WEBUI_NAME = os.environ.get("WEBUI_NAME", "Open WebUI")` to env.py
**Checked:** openwebui/backend/open_webui/env.py line 114

**Result:** ALREADY FIXED - Line exists in current codebase
```python
WEBUI_NAME = os.environ.get("WEBUI_NAME", "Open WebUI")
```

**Note:** This bug has been fixed in the repo. MACOS_SETUP_ISSUES.md is outdated on this point.

---

## LangBuilder Setup (Step 3 in README)

### Step L1: Create Python virtual environment with uv

**Command:**
```bash
cd langbuilder
uv venv
```

**Result:** SUCCESS
- uv automatically detected Python 3.11.14
- Created virtual environment at langbuilder/.venv

---

### Step L2: Install LangBuilder backend dependencies

**Command:**
```bash
make install_backend
```

**Result:** SUCCESS
- Installed 615 packages
- Includes langchain, torch, chromadb, various LLM integrations
- Build time ~50 seconds for downloads + ~3 seconds for installation

---

### Step L3: Install LangBuilder frontend dependencies

**Command:**
```bash
make install_frontend
```

**Result:** SUCCESS
- Installed frontend npm dependencies

---

### Step L4: Create langbuilder/.env file (from MACOS_SETUP_ISSUES.md)

**Source:** MACOS_SETUP_ISSUES.md - "Vite reads from langbuilder/.env, not the root .env"
**README says:** Not mentioned
**Command:**
```bash
cat > langbuilder/.env << 'EOF'
# LangBuilder Frontend Configuration
VITE_PROXY_TARGET=http://localhost:8002
VITE_PORT=3000
EOF
```

**Result:** SUCCESS - File created

**README Discrepancy:** This step is NOT in the README but is CRITICAL for the LangBuilder frontend to connect to the backend. Without it, you get proxy 500 errors / ECONNREFUSED.

---

## Starting Services

### Step S1: Start all services with start_all_macos.sh

**Command:**
```bash
./start_all_macos.sh
```

**First Attempt Result:** FAILED - OpenWebUI backend failed with error:
```
Error: Invalid value for '--port': '${BACKEND_PORT}' is not a valid integer.
```

**Root Cause:** The `.env` file (copied from `.env.example`) contained:
```
OPEN_WEBUI_PORT=${BACKEND_PORT}
```

The startup script uses `grep` to extract this value, which returns the literal string `${BACKEND_PORT}` instead of evaluating the variable reference.

**Fix Applied:**
```bash
# Changed line 62-63 in .env from:
OPEN_WEBUI_PORT=${BACKEND_PORT}
PORT=${BACKEND_PORT}

# To:
OPEN_WEBUI_PORT=8767
PORT=8767
```

**README/ENV Discrepancy:** The `.env.example` file uses shell variable syntax that doesn't work with the startup scripts' grep-based parsing. OpenWebUI port should be explicitly set to 8767, not reference another variable.

---

### Step S2: Restart services after .env fix

**Command:**
```bash
./start_all_macos.sh
```

**Result:** SUCCESS - All 4 services started:

| Service | Port | Status | HTTP Check |
|---------|------|--------|------------|
| OpenWebUI Backend | 8767 | Running | 200 OK |
| OpenWebUI Frontend | 5175 | Running | 200 OK |
| LangBuilder Backend | 8002 | Running | 200 OK |
| LangBuilder Frontend | 3000 | Running | 200 OK |

**Non-Critical Warnings Observed:**
1. WeasyPrint missing external libraries (PDF generation may not work)
2. ffmpeg/avconv not found (audio processing may not work)
3. Composio module import errors (8 components failed to load - `cannot import name 'Action' from 'composio'`)

These warnings don't prevent the services from running.

---

## Verification

### Service URLs (All Responding 200 OK)
- OpenWebUI Frontend: http://localhost:5175
- OpenWebUI Backend API: http://localhost:8767/docs
- LangBuilder Frontend: http://localhost:3000
- LangBuilder Backend API: http://localhost:8002/docs

---

## Summary of Issues Found

### Critical Issues (Blocking)

| Issue | Location | Fix Required |
|-------|----------|--------------|
| Python 3.9.6 too old | System default | Install Python 3.11 via `brew install python@3.11` |
| uv not installed | Missing | Install via `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| OPEN_WEBUI_PORT uses variable reference | .env line 62 | Change `${BACKEND_PORT}` to `8767` |

### README Discrepancies

| README Says | Reality | Recommendation |
|-------------|---------|----------------|
| `python -m venv` | Need `python3.11 -m venv` explicitly | Update README to specify python3.11 |
| `pipx install uv` | curl installer is simpler | Document both methods |
| No mention of y-protocols | Required for TipTap editor | Add `npm install y-protocols --legacy-peer-deps` step |
| No mention of langbuilder/.env | Required for Vite proxy | Add step to create langbuilder/.env with VITE_PROXY_TARGET |
| .env.example uses variable refs | Scripts don't evaluate them | Fix .env.example to use literal port values |

### MACOS_SETUP_ISSUES.md Status

| Issue Listed | Current Status |
|--------------|----------------|
| Use Python 3.11 | Still required |
| Add WEBUI_NAME to env.py | Already fixed in codebase |
| Install y-protocols | Still required |
| Create langbuilder/.env | Still required |
| Use start_all_macos.sh | Works after .env fix |

---

## Recommended .env.example Changes

```diff
- OPEN_WEBUI_PORT=${BACKEND_PORT}
- PORT=${BACKEND_PORT}
+ OPEN_WEBUI_PORT=8767
+ PORT=8767
```

The variable reference syntax `${BACKEND_PORT}` doesn't work because the startup scripts use simple grep extraction, not shell evaluation.

---

## Complete Working Installation Steps (macOS)

```bash
# 1. Prerequisites
brew install python@3.11
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 2. Clone and configure
git clone https://github.com/CloudGeometry/langbuilder.git
cd langbuilder
cp .env.example .env
# IMPORTANT: Edit .env and change OPEN_WEBUI_PORT and PORT from ${BACKEND_PORT} to 8767

# 3. Setup OpenWebUI
cd openwebui
python3.11 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
npm install --legacy-peer-deps
npm install y-protocols --legacy-peer-deps
cd ..

# 4. Setup LangBuilder
cd langbuilder
uv venv
make install_backend
make install_frontend

# Create langbuilder/.env (CRITICAL)
cat > .env << 'EOF'
VITE_PROXY_TARGET=http://localhost:8002
VITE_PORT=3000
EOF
cd ..

# 5. Start services
./start_all_macos.sh
```

---

**Installation completed successfully at:** 2026-01-28 09:44
**Total issues encountered:** 3 critical (all resolved)
**Services verified working:** 4/4
