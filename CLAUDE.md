# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangBuilder Platform by Cloud Geometry - A dual-stack application combining:
- **LangBuilder**: Flow-based AI workflow builder (forked from LangFlow 1.6.5)
- **OpenWebUI**: AI chat interface with model integrations

## Architecture

```
├── langbuilder/          # LangBuilder stack
│   ├── src/backend/         # FastAPI backend (Python)
│   │   ├── base/langbuilder/
│   │   │   ├── components/  # Flow components (agents, models, tools, vectorstores, etc.)
│   │   │   ├── api/         # REST API endpoints (v1/)
│   │   │   └── services/    # Database models, services
│   │   └── tests/           # Backend tests
│   └── src/frontend/        # React/TypeScript frontend (Vite, Tailwind, Zustand, React Flow)
│
└── openwebui/            # OpenWebUI stack
    ├── backend/             # FastAPI backend
    └── (frontend at root)   # SvelteKit frontend
```

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| OpenWebUI Frontend | 5175 | http://localhost:5175 |
| OpenWebUI Backend | 8767 | http://localhost:8767 |
| LangBuilder Frontend | 3000 | http://localhost:3000 |
| LangBuilder Backend | 8002 | http://localhost:8002 |

## Development Commands

### Quick Start
```bash
./start_all.sh                           # Start everything
./openwebui/start_openwebui.sh     # Start OpenWebUI only
./langbuilder/start_langbuilder_stack.sh  # Start LangBuilder only
```

### LangBuilder Commands (run from langbuilder/)
```bash
# Setup
uv venv                    # Create Python virtual environment (required first)
make init                  # Install all dependencies + pre-commit hooks
make install_backend       # Install backend dependencies only
make install_frontend      # Install frontend dependencies only

# Development
make backend               # Start backend on port 7860 (dev mode)
make frontend              # Start frontend on port 3000

# Code Quality
make format_backend        # Format Python code (run FIRST before linting)
make format_frontend       # Format TypeScript/JavaScript
make lint                  # Run mypy type checking

# Testing
make unit_tests            # Run backend unit tests
make integration_tests     # Run integration tests
make tests_frontend        # Run frontend Playwright e2e tests
make test_frontend         # Run frontend Jest unit tests

# Single test execution
uv run pytest src/backend/tests/unit/test_specific.py
uv run pytest src/backend/tests/unit/test_file.py::test_method -v

# Database migrations
make alembic-revision message="Description"
make alembic-upgrade
make alembic-current
```

### OpenWebUI Commands (run from openwebui/)
```bash
make install               # Start with docker-compose
make start                 # Start services
make stop                  # Stop services
make update                # Update and rebuild
```

## Component Development (LangBuilder)

### Adding New Components
1. Add to appropriate subdirectory under `src/backend/base/langbuilder/components/`
2. Update `__init__.py` with alphabetical imports
3. Backend auto-restarts on save; refresh browser to see changes

### Component Testing
- Unit tests go in `src/backend/tests/unit/components/`
- Use `ComponentTestBaseWithClient` or `ComponentTestBaseWithoutClient` base classes
- Provide `file_names_mapping` fixture for version compatibility testing

### Test Markers
- `@pytest.mark.api_key_required` - Tests requiring external API keys
- `@pytest.mark.no_blockbuster` - Skip blockbuster plugin

## Pre-commit Workflow

1. `make format_backend` (run FIRST - auto-fixes most issues)
2. `make lint`
3. `make unit_tests`
4. Commit

## Key Technologies

**LangBuilder Backend**: Python 3.10+, FastAPI, SQLAlchemy, uv package manager, LangChain integrations

**LangBuilder Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Zustand, React Flow

**OpenWebUI**: FastAPI backend, SvelteKit frontend, ChromaDB, multiple LLM provider integrations

## Environment Configuration

Copy `.env.example` to `.env` and configure API keys. Both stacks share the root `.env` file.
