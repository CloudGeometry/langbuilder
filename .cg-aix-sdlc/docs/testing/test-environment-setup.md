# Test Environment Setup

## Overview

This guide explains how to set up the test environment for running LangBuilder tests locally.

## Prerequisites

### System Requirements

| Component | Minimum Version | Recommended |
|-----------|-----------------|-------------|
| Python | 3.10 | 3.12 |
| Node.js | 18 | 21 |
| npm | 8 | 10 |
| Git | 2.30 | Latest |

### Package Managers

- **Python**: uv (recommended) or pip
- **Node.js**: npm

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/CloudGeometry/langbuilder.git
cd langbuilder/langbuilder
```

### 2. Install uv (Python Package Manager)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pipx
pipx install uv
```

### 3. Initialize Project

```bash
make init
```

This command:
- Installs backend Python dependencies
- Installs frontend npm dependencies
- Sets up pre-commit hooks

### 4. Verify Installation

```bash
# Check Python environment
uv run python --version

# Check Node environment
node --version
npm --version

# Verify pytest
uv run pytest --version
```

## Backend Test Environment

### Install Dependencies

```bash
# Standard installation
make install_backend

# With PostgreSQL support
make install_backend EXTRA_ARGS="--extra postgresql"

# Force reinstall (no cache)
make reinstall_backend
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Test configuration
LANGBUILDER_DATABASE_URL=sqlite:///./test.db
LANGBUILDER_AUTO_LOGIN=true
LANGBUILDER_DEACTIVATE_TRACING=true

# Optional: API keys for integration tests
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

### Database Setup

Tests use SQLite in-memory databases by default. No setup required.

For PostgreSQL testing:
```bash
# Start PostgreSQL container
docker run -d \
  --name langbuilder-test-db \
  -e POSTGRES_PASSWORD=test \
  -p 5432:5432 \
  postgres:15

# Set environment variable
export LANGBUILDER_DATABASE_URL=postgresql://postgres:test@localhost:5432/test
```

## Frontend Test Environment

### Install Dependencies

```bash
cd src/frontend
npm ci  # Clean install from lock file
```

### Install Playwright Browsers

```bash
cd src/frontend
npx playwright install --with-deps chromium
```

### Verify Jest Setup

```bash
cd src/frontend
npm test -- --listTests
```

## Running Tests

### Backend Tests

```bash
# Run all unit tests
make unit_tests

# Run with parallel execution
make unit_tests async=true

# Run last failed tests first
make unit_tests lf=true ff=true

# Run with coverage
make unit_tests args="--cov --cov-report=html"

# Run specific test file
uv run pytest src/backend/tests/unit/api/v1/test_flows.py -v

# Run tests matching pattern
uv run pytest -k "test_create" -v

# Run integration tests
make integration_tests

# Run without API keys
make integration_tests_no_api_keys
```

### Frontend Tests

```bash
cd src/frontend

# Jest unit tests
npm test

# Jest with coverage
npm test -- --coverage

# Jest in watch mode
npm test -- --watch

# Playwright E2E tests
npx playwright test

# Playwright with UI
npx playwright test --ui

# Playwright debug mode
npx playwright test --debug

# Run specific test file
npx playwright test tests/core/features/folders.spec.ts

# Run tests with tag
npx playwright test --grep "@release"
```

## IDE Configuration

### VS Code

Install recommended extensions:
- Python (Microsoft)
- Pylance
- Ruff
- ES7+ React/Redux/React-Native snippets
- Playwright Test for VSCode

**settings.json:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "src/backend/tests"
  ],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### PyCharm

1. Set Python interpreter to `.venv/bin/python`
2. Configure pytest as test runner
3. Set test directory to `src/backend/tests`

## Troubleshooting

### Common Issues

#### 1. Module Not Found

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Reinstall dependencies
make reinstall_backend
```

#### 2. Database Lock Errors

```bash
# Kill any running processes
pkill -f langbuilder

# Remove test database
rm -f test.db test.db-journal
```

#### 3. Playwright Browser Issues

```bash
cd src/frontend

# Reinstall browsers
npx playwright install --force chromium

# Install system dependencies (Ubuntu)
npx playwright install-deps chromium
```

#### 4. Port Already in Use

```bash
# Find process using port
lsof -i :7860
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use Makefile target (includes port cleanup)
make backend
```

#### 5. Async Test Failures

```bash
# Ensure pytest-asyncio is installed
uv pip show pytest-asyncio

# Check asyncio mode in pyproject.toml
# Should be: asyncio_mode = "auto"
```

### Environment Variables Reference

| Variable | Purpose | Default |
|----------|---------|---------|
| `LANGBUILDER_DATABASE_URL` | Database connection | sqlite:///./langbuilder.db |
| `LANGBUILDER_AUTO_LOGIN` | Skip authentication | false |
| `LANGBUILDER_DEACTIVATE_TRACING` | Disable telemetry | false |
| `LANGBUILDER_USE_NOOP_DATABASE` | Use no-op database | false |
| `OPENAI_API_KEY` | OpenAI API access | - |
| `ANTHROPIC_API_KEY` | Anthropic API access | - |

### Debug Mode

```bash
# Python tests with verbose output
uv run pytest -vvv --tb=long

# Playwright with slow motion
npx playwright test --headed --slow-mo=1000

# Enable debug logging
export LANGBUILDER_LOG_LEVEL=DEBUG
make unit_tests
```

## CI/CD Environment Differences

### Local vs CI

| Aspect | Local | CI |
|--------|-------|-----|
| Database | SQLite file | SQLite memory |
| Parallelism | Configurable | Fixed shards |
| Timeout | No limit | 150s per test |
| Retries | 0 | 2-3 |
| Browsers | As installed | Chromium only |

### Simulating CI Locally

```bash
# Run with CI-like settings
CI=true make unit_tests args="--splits 5 --group 1"

# Frontend with CI reporters
cd src/frontend
CI=true npm test

# Playwright with CI config
cd src/frontend
CI=true npx playwright test
```

## Quick Reference

### Commands Summary

```bash
# Setup
make init                       # Full project initialization

# Backend
make unit_tests                # All unit tests
make integration_tests         # All integration tests
make tests                     # Everything

# Frontend
cd src/frontend
npm test                       # Jest tests
npx playwright test            # E2E tests

# Quality
make format                    # Format all code
make lint                      # Lint checks
uvx pre-commit run --all-files # Pre-commit hooks
```

---
*Generated by CG AIx SDLC - Testing Documentation*
