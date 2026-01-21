# LangBuilder - Codebase Primer

## What is LangBuilder?

LangBuilder is a visual AI workflow builder that enables creating LangChain-based AI pipelines through drag-and-drop. It combines a React frontend with a FastAPI backend to let users design, deploy, and manage AI workflows without writing code.

**Key Value**: Build complex AI pipelines visually, then expose them as APIs.

## Project Structure

```
langbuilder/
├── langbuilder/                    # Main package (v1.6.5)
│   ├── src/
│   │   ├── backend/
│   │   │   ├── base/               # langbuilder-base library (v0.6.5)
│   │   │   │   └── langbuilder/
│   │   │   │       ├── api/        # FastAPI routes (v1/, v2/)
│   │   │   │       ├── components/ # 455+ AI components
│   │   │   │       ├── graph/      # Workflow execution engine
│   │   │   │       ├── services/   # Business logic & DB
│   │   │   │       ├── custom/     # Custom component support
│   │   │   │       └── inputs/     # Input type definitions
│   │   │   └── tests/              # pytest tests
│   │   └── frontend/
│   │       └── src/
│   │           ├── stores/         # Zustand state management
│   │           ├── pages/          # React pages
│   │           └── CustomNodes/    # Flow canvas nodes
│   └── pyproject.toml
├── openwebui/                      # ActionBridge integration
└── pyproject.toml                  # UV workspace root
```

## Key Entry Points

| Purpose | Location |
|---------|----------|
| **Backend start** | `langbuilder/langbuilder_launcher:main` |
| **API router** | `langbuilder/src/backend/base/langbuilder/api/router.py` |
| **Component registry** | `langbuilder/src/backend/base/langbuilder/components/__init__.py` |
| **Graph execution** | `langbuilder/src/backend/base/langbuilder/graph/graph/base.py` |
| **Frontend app** | `langbuilder/src/frontend/src/App.tsx` |
| **Flow store** | `langbuilder/src/frontend/src/stores/flowStore.ts` |

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI 0.115+ |
| AI Framework | LangChain 0.3.x |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Migrations | Alembic |
| Frontend | React 18 + TypeScript 5.4 |
| Flow Canvas | @xyflow/react 12.3 |
| State | Zustand |
| Styling | TailwindCSS + Radix UI |

## Quick Navigation

### Adding Backend Features
- **New API endpoint**: `langbuilder/src/backend/base/langbuilder/api/v1/`
- **New component**: `langbuilder/src/backend/base/langbuilder/components/{category}/`
- **Database model**: `langbuilder/src/backend/base/langbuilder/services/database/models/`

### Adding Frontend Features
- **New page**: `langbuilder/src/frontend/src/pages/`
- **New store**: `langbuilder/src/frontend/src/stores/`
- **Flow canvas node**: `langbuilder/src/frontend/src/CustomNodes/`

### Running & Testing
```bash
# Backend
uv sync && uv run langbuilder run

# Frontend
cd langbuilder/src/frontend && npm install && npm run dev

# Tests
uv run pytest langbuilder/src/backend/tests/
```

## Core Concepts

1. **Flow**: A workflow containing nodes and edges (stored as JSON)
2. **Component**: A reusable AI building block (LLM, Vector Store, Tool)
3. **Vertex**: Runtime instance of a component during execution
4. **Graph**: Execution engine that runs vertices in topological order

## Default Ports
- Backend API: `8002`
- Frontend: `5175`

---
*AI Context Document - CloudGeometry AIx SDLC*
