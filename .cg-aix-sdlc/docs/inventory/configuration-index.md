# Configuration Index - LangBuilder

## Overview

LangBuilder uses environment variables, configuration files, and Pydantic settings for application configuration. This document indexes all configuration options.

---

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment variables | Project root |
| `.env.example` | Environment template | Project root |
| `.env.docker.example` | Docker environment | Project root |
| `pyproject.toml` | Python project config | `langbuilder/` |
| `package.json` | Frontend config | `langbuilder/src/frontend/` |
| `alembic.ini` | Database migrations | `langbuilder/src/backend/base/langbuilder/` |
| `docker-compose.dev.yml` | Docker services | Project root |
| `.coderabbit.yaml` | Code review bot | Project root |
| `.pre-commit-config.yaml` | Git hooks | Project root |
| `tsconfig.json` | TypeScript config | `langbuilder/src/frontend/` |
| `vite.config.ts` | Vite build config | `langbuilder/src/frontend/` |
| `tailwind.config.js` | Tailwind CSS | `langbuilder/src/frontend/` |

---

## Environment Variables

### Core Application

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_PORT` | 5175 | Frontend dev server port |
| `BACKEND_PORT` | 8002 | Backend API server port |
| `HOST` | 0.0.0.0 | Server bind address |
| `DATA_DIR` | ./data | Data storage directory |
| `DATABASE_URL` | sqlite:///./data/webui.db | Database connection string |

### CORS & Security

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ALLOW_ORIGIN` | (see example) | Allowed origins (semicolon-separated) |
| `FORWARDED_ALLOW_IPS` | * | Trusted proxy IPs |
| `WEBUI_SECRET_KEY` | (required) | JWT signing key |
| `JWT_EXPIRES_IN` | 24h | JWT token expiration |
| `KMS_MASTER_KEY` | (required) | Encryption master key |

### Telemetry & Analytics

| Variable | Default | Description |
|----------|---------|-------------|
| `SCARF_NO_ANALYTICS` | true | Disable Scarf analytics |
| `DO_NOT_TRACK` | true | Disable tracking |
| `ANONYMIZED_TELEMETRY` | false | Anonymous telemetry |

### LLM Providers

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server URL |
| `OPENAI_API_BASE_URL` | (empty) | OpenAI API base URL |
| `OPENAI_API_KEY` | (empty) | OpenAI API key |

### Google OAuth

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL |
| `GOOGLE_DRIVE_CLIENT_ID` | Google Drive client ID |
| `GOOGLE_DRIVE_CLIENT_SECRET` | Google Drive client secret |

### OAuth Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_OAUTH_SIGNUP` | true | Allow OAuth registration |
| `OAUTH_ALLOWED_DOMAINS` | * | Allowed email domains |
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | true | Merge existing accounts |
| `OAUTH_UPDATE_PICTURE_ON_LOGIN` | true | Update profile picture |
| `OPENID_PROVIDER_URL` | (Google URL) | OpenID configuration URL |

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_SIGNUP` | true | Allow new registrations |
| `ENABLE_LOGIN_FORM` | true | Show login form |
| `ENABLE_API_KEY` | true | Enable API key auth |

### Session Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBUI_SESSION_COOKIE_SAME_SITE` | lax | Cookie SameSite policy |
| `WEBUI_SESSION_COOKIE_SECURE` | false | Require HTTPS for cookies |

### Corporate Authentication

| Variable | Description |
|----------|-------------|
| `CORPORATE_AUTH_CONFIG` | Path to corporate config JSON |
| `GOOGLE_WORKSPACE_DOMAIN` | Workspace domain |
| `GOOGLE_WORKSPACE_ADMIN_EMAIL` | Admin email |
| `GOOGLE_SERVICE_ACCOUNT_KEY_FILE` | Service account key path |
| `CORPORATE_GROUP_MAPPINGS` | JSON group-to-role mapping |

### Zoho OAuth

| Variable | Description |
|----------|-------------|
| `ZOHO_CLIENT_ID` | Zoho OAuth client ID |
| `ZOHO_CLIENT_SECRET` | Zoho OAuth client secret |
| `ZOHO_REDIRECT_URI` | OAuth callback URL |

### Google Drive Agent

| Variable | Description |
|----------|-------------|
| `GOOGLE_DRIVE_TOKEN` | Drive access token |
| `GOOGLE_DRIVE_USER_ID` | Drive user ID |
| `GOOGLE_DRIVE_AGENT_URL` | Agent endpoint URL |
| `GOOGLE_DRIVE_AGENT_PATH` | Agent installation path |

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBUI_NAME` | ActionBridge | Application display name |
| `WEBUI_URL` | (computed) | Application base URL |
| `OPEN_WEBUI_PORT` | $BACKEND_PORT | OpenWebUI port alias |
| `PORT` | $BACKEND_PORT | Server port alias |
| `GLOBAL_LOG_LEVEL` | DEBUG | Logging verbosity |

---

## Pydantic Settings

LangBuilder uses `pydantic-settings` for typed configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Core settings
    remove_api_keys: bool = True
    # ... additional settings
```

Settings are accessed via dependency injection:
```python
from langbuilder.services.deps import get_settings_service
settings = get_settings_service()
```

---

## Database Configuration

### SQLite (Default)

```
DATABASE_URL=sqlite:///./data/webui.db
```

### PostgreSQL (Production)

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Install with:
```bash
pip install langbuilder[postgresql]
```

---

## Frontend Configuration

### package.json Scripts

| Script | Purpose |
|--------|---------|
| `start` | Development server |
| `dev:docker` | Docker development |
| `build` | Production build |
| `test` | Run tests |
| `format` | Format code |
| `type-check` | TypeScript validation |

### Vite Configuration

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.FRONTEND_PORT || '5175'),
    proxy: {
      '/api': `http://localhost:${process.env.BACKEND_PORT || '8002'}`
    }
  }
})
```

### Proxy Settings

```json
{
  "proxy": "http://localhost:7860"
}
```

---

## Docker Configuration

### docker-compose.dev.yml Services

| Service | Description |
|---------|-------------|
| backend | FastAPI application |
| frontend | React development server |
| db | PostgreSQL (optional) |

### Environment in Docker

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://...
      - BACKEND_PORT=8002
```

---

## Alembic Configuration

### alembic.ini

```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./data/webui.db
```

### Running Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Logging Configuration

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Development debugging |
| INFO | General information |
| WARNING | Warning messages |
| ERROR | Error conditions |
| CRITICAL | Critical failures |

### Loguru Configuration

```python
from loguru import logger

logger.add("debug.log", level="DEBUG")
```

### Structlog Configuration

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(),
        structlog.dev.ConsoleRenderer()
    ]
)
```

---

## Sentry Configuration

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=1.0
)
```

---

## MCP Configuration

MCP servers are configured per-project in the database:

```json
{
  "servers": [
    {
      "name": "server-name",
      "command": ["python", "-m", "mcp_server"],
      "args": []
    }
  ]
}
```

---

## Code Quality Configuration

### Ruff (Python Linting)

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
select = ["ALL"]
ignore = ["C90", "CPY", "COM812", ...]
```

### Biome (JS/TS Linting)

```json
// biome.json
{
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2
  }
}
```

### MyPy (Type Checking)

```toml
# pyproject.toml
[tool.mypy]
plugins = ["pydantic.mypy"]
ignore_missing_imports = true
```

---

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
```

---

## Testing Configuration

### pytest.ini Options

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["src/backend/tests"]
asyncio_mode = "auto"
timeout = 150
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow-running tests"
]
```

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
}
```

---

## Example .env File

```env
# Server Configuration
FRONTEND_PORT=5175
BACKEND_PORT=8002
HOST=0.0.0.0

# Database
DATA_DIR=./data
DATABASE_URL=sqlite:///./data/webui.db

# Security
WEBUI_SECRET_KEY=your-secret-key
KMS_MASTER_KEY=your-kms-key

# LLM Providers
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-...

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
ENABLE_OAUTH_SIGNUP=true

# Telemetry
DO_NOT_TRACK=true
ANONYMIZED_TELEMETRY=false
```
