# Repository Map - LangBuilder

## Overview

LangBuilder is a monorepo containing a Python/TypeScript full-stack application for building AI-powered workflows using LangChain. The project uses `uv` as its workspace manager with 2 main packages.

## Directory Structure

```
langbuilder/
├── .github/                    # GitHub workflows and CI/CD
├── langbuilder/                # Main package (monorepo workspace root)
│   ├── pyproject.toml          # Main package configuration (v1.6.5)
│   └── src/
│       ├── backend/
│       │   └── base/           # langbuilder-base package (v0.6.5)
│       │       ├── pyproject.toml
│       │       └── langbuilder/
│       │           ├── __init__.py
│       │           ├── __main__.py
│       │           ├── alembic.ini
│       │           ├── alembic/          # Database migrations
│       │           ├── api/              # FastAPI routers
│       │           │   ├── router.py     # Main API router
│       │           │   ├── v1/           # API v1 endpoints
│       │           │   └── v2/           # API v2 endpoints
│       │           ├── base/             # Base agent implementations
│       │           ├── components/       # LangChain components (90+ integrations)
│       │           ├── custom/           # Custom component support
│       │           ├── graph/            # Flow graph execution
│       │           ├── helpers/          # Utility helpers
│       │           ├── initial_setup/    # Starter projects setup
│       │           ├── logging/          # Logging configuration
│       │           ├── schema/           # Pydantic schemas
│       │           ├── serialization/    # Data serialization
│       │           ├── services/         # Business logic services
│       │           │   ├── auth/         # Authentication
│       │           │   ├── cache/        # Caching
│       │           │   ├── database/     # Database models & CRUD
│       │           │   └── deps.py       # Dependency injection
│       │           └── utils/            # Utility functions
│       ├── frontend/
│       │   ├── package.json    # Frontend dependencies (React 18)
│       │   └── src/
│       │       ├── App.tsx
│       │       ├── CustomNodes/    # Flow canvas nodes
│       │       ├── alerts/         # Alert components
│       │       ├── assets/         # Static assets
│       │       ├── components/     # UI components
│       │       ├── contexts/       # React contexts
│       │       ├── hooks/          # Custom hooks
│       │       ├── pages/          # Page components
│       │       ├── stores/         # Zustand stores
│       │       └── types/          # TypeScript types
│       └── tests/                  # Test suites
├── openwebui/                  # OpenWebUI integration (ActionBridge)
│   ├── pyproject.toml
│   └── backend/                # OpenWebUI backend
├── src/                        # Additional source (shared?)
├── skills/                     # Claude skills definitions
├── docker-compose.dev.yml      # Docker development config
├── start_all.sh                # Startup script
├── .env.example                # Environment template
└── README.md
```

## Key Directories

### Backend (`langbuilder/src/backend/base/langbuilder/`)

| Directory | Purpose |
|-----------|---------|
| `api/` | FastAPI router definitions with v1 and v2 versioning |
| `components/` | 90+ LangChain component integrations (LLMs, tools, vectorstores) |
| `services/database/` | SQLModel ORM models, CRUD operations, session management |
| `services/auth/` | JWT authentication, API key validation |
| `graph/` | Flow execution engine, vertex building |
| `base/agents/` | Agent implementations (CrewAI, etc.) |
| `alembic/` | Database migration scripts |

### Frontend (`langbuilder/src/frontend/src/`)

| Directory | Purpose |
|-----------|---------|
| `CustomNodes/` | React Flow node components for the canvas |
| `components/` | Reusable UI components (shadcn/ui based) |
| `pages/` | Route page components |
| `stores/` | Zustand state management |
| `contexts/` | React context providers |
| `hooks/` | Custom React hooks |

### Components (`langbuilder/src/backend/base/langbuilder/components/`)

The components directory contains 90+ integrations organized by provider/category:

- **LLM Providers**: openai, anthropic, google, azure, ollama, groq, etc.
- **Vector Stores**: chroma, pinecone, qdrant, milvus, pgvector, etc.
- **Tools**: duckduckgo, serpapi, wikipedia, youtube, etc.
- **Data**: processing, embeddings, document loaders
- **Enterprise**: salesforce, servicenow, workday, sap, jira, hubspot

## Important Files

| File | Purpose |
|------|---------|
| `langbuilder/pyproject.toml` | Main package config, all dependencies |
| `langbuilder/src/backend/base/pyproject.toml` | Base library config |
| `langbuilder/src/backend/base/langbuilder/api/router.py` | API router registration |
| `langbuilder/src/backend/base/langbuilder/services/database/models/__init__.py` | Database model exports |
| `langbuilder/src/frontend/package.json` | Frontend dependencies |
| `.env.example` | Environment variable template |

## Code Organization Patterns

1. **Monorepo with uv workspaces**: Two packages sharing dependencies
2. **FastAPI with versioned routers**: API v1 and v2 coexist
3. **SQLModel for ORM**: Combines SQLAlchemy + Pydantic
4. **Dynamic imports**: Components use lazy loading for performance
5. **React + TypeScript**: Type-safe frontend with shadcn/ui components
6. **Zustand for state**: Lightweight state management
7. **React Flow**: Visual flow builder canvas
