# Debugging Guide

Comprehensive troubleshooting guide for common issues in LangBuilder development.

## Table of Contents

1. [Common Setup Issues](#common-setup-issues)
2. [Runtime Errors](#runtime-errors)
3. [Database Issues](#database-issues)
4. [Frontend Issues](#frontend-issues)
5. [API Issues](#api-issues)
6. [Component Issues](#component-issues)
7. [Testing Issues](#testing-issues)
8. [Docker Issues](#docker-issues)
9. [How to Get Help](#how-to-get-help)

---

## Common Setup Issues

### Python Version Mismatch

**Symptom:** Errors about Python version or unsupported syntax.

**Solution:**
```bash
# Check current Python version
python --version

# Install correct Python version with uv
uv python install 3.12

# Create venv with specific version
uv venv --python 3.12

# Resync dependencies
uv sync --frozen
```

### uv Not Found

**Symptom:** `command not found: uv`

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with pipx
pipx install uv

# Verify installation
uv --version
```

### Node.js Version Too Old

**Symptom:** npm install fails or frontend won't start.

**Solution:**
```bash
# Check Node version (needs 18+)
node --version

# Install Node 20 using nvm
nvm install 20
nvm use 20
```

### Missing .env File

**Symptom:** `FileNotFoundError` or missing configuration errors.

**Solution:**
```bash
# Copy example file
cp .env.example .env

# Verify file exists
ls -la .env
```

### Permission Denied

**Symptom:** Cannot create files or install packages.

**Solution:**
```bash
# Fix permissions on project directory
chmod -R 755 langbuilder/

# For npm global packages
sudo chown -R $(whoami) ~/.npm
```

### Port Already in Use

**Symptom:** `Address already in use` or `EADDRINUSE`

**Solution:**
```bash
# Find process using port 8002
# macOS/Linux:
lsof -i :8002

# Windows:
netstat -ano | findstr :8002

# Kill the process
# macOS/Linux:
kill -9 <PID>

# Windows:
taskkill /PID <PID> /F

# Or use different port in .env
BACKEND_PORT=8003
FRONTEND_PORT=5176
```

---

## Runtime Errors

### ModuleNotFoundError

**Symptom:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
# Ensure you're using the virtual environment
which python  # Should point to .venv

# Resync dependencies
uv sync --frozen

# If specific package missing
uv add <package-name>
```

### ImportError: cannot import name

**Symptom:** `ImportError: cannot import name 'X' from 'Y'`

**Possible Causes:**
1. Circular imports
2. Module not installed
3. Version mismatch

**Solution:**
```bash
# Check if module exists
uv pip show <package-name>

# Reinstall dependencies
uv sync --reinstall --frozen
```

### Pydantic Validation Error

**Symptom:** `pydantic.error_wrappers.ValidationError`

**Solution:**
1. Check the request payload format
2. Verify required fields are present
3. Check field types match schema

```python
# Example: Debug validation
from pydantic import ValidationError

try:
    obj = MyModel(**data)
except ValidationError as e:
    print(e.json())
```

### AttributeError: 'NoneType' object

**Symptom:** `AttributeError: 'NoneType' object has no attribute 'X'`

**Debugging:**
```python
# Add null checks
if obj is not None:
    result = obj.attribute
else:
    logger.error("Object was None")
```

### Async Runtime Errors

**Symptom:** `RuntimeError: This event loop is already running`

**Solution:**
```python
# Don't nest asyncio.run()
# Wrong:
asyncio.run(some_async_function())  # Inside async context

# Right:
await some_async_function()  # Inside async context
```

---

## Database Issues

### Database File Not Found

**Symptom:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
```bash
# Create data directory
mkdir -p data/

# Check DATABASE_URL in .env
DATABASE_URL='sqlite:///./data/webui.db'
```

### Migration Errors

**Symptom:** Alembic errors about schema mismatch.

**Solution:**
```bash
# Check current state
make alembic-current

# Check pending migrations
make alembic-check

# Apply migrations
make alembic-upgrade

# If corrupted, stamp to latest
make alembic-stamp revision=head
```

### Database Locked (SQLite)

**Symptom:** `sqlite3.OperationalError: database is locked`

**Solution:**
1. Close other connections (other terminals, IDE database viewers)
2. Restart the backend server
3. If persists, delete and recreate:

```bash
rm data/webui.db
make backend
```

### PostgreSQL Connection Refused

**Symptom:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
# macOS:
brew services list | grep postgresql

# Linux:
systemctl status postgresql

# Start if stopped
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Check connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/langbuilder
```

### Foreign Key Constraint Failed

**Symptom:** `sqlalchemy.exc.IntegrityError: FOREIGN KEY constraint failed`

**Solution:**
1. Check related records exist
2. Verify correct IDs are used
3. Check cascade delete settings

---

## Frontend Issues

### npm Install Fails

**Symptom:** Various npm errors during install.

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and lock file
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If still failing, try with legacy peer deps
npm install --legacy-peer-deps
```

### Vite Build Fails

**Symptom:** `Build failed` or TypeScript errors.

**Solution:**
```bash
# Check for TypeScript errors
npm run type-check

# Fix common issues
npm run format

# Clean build
rm -rf build/
npm run build
```

### White Screen / Nothing Renders

**Symptom:** Blank page in browser.

**Debug Steps:**
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests

**Common Fixes:**
```bash
# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)

# Check backend is running
curl http://localhost:8002/health

# Check frontend proxy configuration in vite.config.ts
```

### CORS Errors

**Symptom:** `Access-Control-Allow-Origin` errors in console.

**Solution:**
```bash
# Update .env with correct CORS settings
CORS_ALLOW_ORIGIN="http://localhost:5175;http://localhost:8002"

# Restart backend
```

### Hot Module Replacement Not Working

**Symptom:** Changes don't reflect in browser.

**Solution:**
1. Check Vite is running in watch mode
2. Check for syntax errors preventing reload
3. Force full page refresh

```bash
# Restart frontend server
cd src/frontend
npm start
```

### Component Not Updating

**Symptom:** React component doesn't re-render.

**Debug:**
```typescript
// Add debug logging
console.log('Component rendered', props);

// Check if state is actually changing
useEffect(() => {
  console.log('State changed:', state);
}, [state]);
```

---

## API Issues

### 404 Not Found

**Symptom:** API returns 404.

**Debug Steps:**
1. Check URL is correct
2. Verify route is registered

```bash
# Check available routes
curl http://localhost:8002/docs

# Verify specific route
curl -v http://localhost:8002/api/v1/flows
```

### 401 Unauthorized

**Symptom:** API returns 401.

**Solution:**
```bash
# Check authentication token
# Get token by logging in
curl -X POST http://localhost:8002/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token in requests
curl http://localhost:8002/api/v1/flows \
  -H "Authorization: Bearer <token>"
```

### 422 Validation Error

**Symptom:** API returns 422 with validation details.

**Solution:**
1. Check request body format
2. Verify required fields
3. Check field types

```bash
# Example debug
curl -X POST http://localhost:8002/api/v1/flows \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "data": {"nodes": [], "edges": []}}' \
  -v
```

### 500 Internal Server Error

**Symptom:** API returns 500.

**Debug Steps:**
1. Check backend logs in terminal
2. Look for stack trace
3. Enable debug logging

```bash
# Run with debug logging
GLOBAL_LOG_LEVEL=DEBUG make backend
```

### Slow API Responses

**Symptom:** API calls take too long.

**Debug:**
```python
# Add timing logs
import time

start = time.time()
# ... operation
print(f"Operation took {time.time() - start}s")
```

---

## Component Issues

### Component Not Appearing in UI

**Symptom:** New component doesn't show in sidebar.

**Checklist:**
1. Component registered in `__init__.py`
2. Component class has `display_name`
3. No import errors
4. Backend restarted

```python
# Check component registration
# In components/{category}/__init__.py
from .my_component import MyComponent

__all__ = [
    # ... other exports
    "MyComponent",
]
```

### Component Build Fails

**Symptom:** Error when running flow with component.

**Debug:**
```python
# Add logging to component
from loguru import logger

class MyComponent(Component):
    def process(self):
        logger.debug(f"Processing with params: {self.param}")
        try:
            # ... logic
        except Exception as e:
            logger.error(f"Component failed: {e}")
            raise
```

### Component Inputs Not Validating

**Symptom:** Invalid inputs not caught.

**Solution:**
```python
from pydantic import Field, validator

class MyComponent(Component):
    value: int = Field(..., gt=0, description="Must be positive")

    @validator('value')
    def validate_value(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v
```

---

## Testing Issues

### Tests Not Running

**Symptom:** `pytest` command fails.

**Solution:**
```bash
# Ensure pytest is installed
uv run pytest --version

# Run from correct directory
cd langbuilder
uv run pytest src/backend/tests/ -v
```

### Tests Failing Due to Database

**Symptom:** Database-related test failures.

**Solution:**
```python
# Use test fixtures properly
@pytest.fixture
async def session():
    # Create test database
    async with async_test_session() as session:
        yield session
        await session.rollback()
```

### Async Test Issues

**Symptom:** `RuntimeWarning: coroutine was never awaited`

**Solution:**
```python
# Use pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Import Errors in Tests

**Symptom:** `ImportError` when running tests.

**Solution:**
```bash
# Ensure package is installed in editable mode
uv sync --frozen

# Check Python path
python -c "import langbuilder; print(langbuilder.__file__)"
```

---

## Docker Issues

### Container Won't Start

**Symptom:** Container exits immediately.

**Debug:**
```bash
# Check container logs
docker logs langbuilder-backend-dev

# Run container interactively
docker run -it langbuilder:latest /bin/bash
```

### Cannot Connect to Services

**Symptom:** Services can't communicate.

**Solution:**
```bash
# Ensure services are on same network
docker network ls
docker network inspect langbuilder-network

# Check container IPs
docker inspect langbuilder-backend-dev | grep IPAddress
```

### Volume Mount Issues

**Symptom:** Changes not reflected in container.

**Solution:**
```bash
# Check volume mounts
docker inspect langbuilder-backend-dev | grep -A 10 Mounts

# Rebuild with no cache if necessary
docker-compose build --no-cache
```

### Out of Disk Space

**Symptom:** Docker build fails due to space.

**Solution:**
```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune
```

---

## How to Get Help

### 1. Check the Logs

```bash
# Backend logs
# Look in the terminal running `make backend`

# Frontend logs
# Check browser DevTools console (F12)

# Docker logs
docker logs <container-name>
```

### 2. Enable Debug Logging

```bash
# In .env
GLOBAL_LOG_LEVEL=DEBUG

# Restart backend
```

### 3. Search Existing Issues

Check GitHub Issues: https://github.com/CloudGeometry/langbuilder/issues

### 4. Ask the Team

- Slack: #langbuilder-dev
- Email: dev@langbuilder.org

### 5. Create a Bug Report

Include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Error messages/logs
5. Environment details (OS, Python version, Node version)

### Debug Checklist

When encountering an issue:

- [ ] Check logs for error messages
- [ ] Verify environment variables
- [ ] Ensure dependencies are installed
- [ ] Restart services
- [ ] Clear caches if needed
- [ ] Check for known issues
- [ ] Search documentation
- [ ] Ask for help if stuck

---

## Quick Reference: Common Fixes

| Issue | Quick Fix |
|-------|-----------|
| Dependencies broken | `uv sync --reinstall --frozen` |
| Frontend won't build | `rm -rf node_modules && npm install` |
| Database corrupted | `rm -rf data/ && make backend` |
| Port in use | Kill process or change port in `.env` |
| CORS errors | Check `CORS_ALLOW_ORIGIN` in `.env` |
| Auth failing | Clear cookies and re-login |
| Tests failing | `make clean_all && make unit_tests` |
| Docker issues | `docker-compose down -v && docker-compose up --build` |

---

*Generated by CloudGeometry AIx SDLC - Onboarding Documentation*
