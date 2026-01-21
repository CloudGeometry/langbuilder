# LangBuilder - AI Context Bundle

> Optimized single-file context for AI coding assistants (~2000 tokens)

## Project Identity
- **Name**: LangBuilder v1.6.5
- **Purpose**: Visual AI workflow builder using LangChain
- **Architecture**: FastAPI backend + React frontend
- **License**: MIT

## Directory Map
```
langbuilder/
├── langbuilder/src/backend/base/langbuilder/
│   ├── api/v1/           # REST endpoints
│   ├── components/       # 455+ AI components
│   ├── graph/           # Workflow execution
│   ├── services/database/models/  # SQLModel ORM
│   └── custom/          # Custom component support
└── langbuilder/src/frontend/src/
    ├── stores/          # Zustand state
    └── pages/           # React pages
```

## Tech Stack
| Layer | Tech |
|-------|------|
| API | FastAPI 0.115+, Uvicorn |
| AI | LangChain 0.3.x |
| DB | SQLModel, Alembic, SQLite/PostgreSQL |
| Frontend | React 18, TypeScript 5.4, Zustand |
| Canvas | @xyflow/react 12.3 |

## Core Models
```python
# Flow (workflow definition)
class Flow(SQLModel, table=True):
    id: UUID
    name: str
    data: dict  # {"nodes": [], "edges": []}
    user_id: UUID
    folder_id: UUID | None

# User
class User(SQLModel, table=True):
    id: UUID
    username: str
    password: str  # bcrypt
    is_active: bool
```

## API Patterns
```python
# Endpoint pattern
@router.get("/{id}", response_model=FlowRead)
async def get_flow(id: UUID, session: DbSession, user: CurrentActiveUser):
    flow = await session.get(Flow, id)
    if not flow or flow.user_id != user.id:
        raise HTTPException(404, "Not found")
    return flow
```

## Component Pattern
```python
class MyComponent(LCModelComponent):
    display_name = "My LLM"
    inputs = [
        SecretStrInput(name="api_key"),
        DropdownInput(name="model", options=["a","b"]),
    ]
    def build_model(self):
        return ChatModel(api_key=self.api_key, model=self.model)
```

## Frontend State
```typescript
const useFlowStore = create<FlowStoreType>((set) => ({
    nodes: [],
    edges: [],
    addNode: (n) => set((s) => ({ nodes: [...s.nodes, n] })),
}));
```

## Key Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/v1/login | Auth |
| GET/POST | /api/v1/flows | CRUD |
| POST | /api/v1/build/{id}/flow | Execute |
| POST | /api/v1/run/{endpoint} | API call |
| GET | /health | Status |

## Commands
```bash
# Backend
uv run langbuilder run

# Frontend
cd langbuilder/src/frontend && npm run dev

# Tests
uv run pytest

# Migrations
uv run alembic upgrade head
```

## Ports
- Backend: 8002
- Frontend: 5175

## LLM Providers
OpenAI, Anthropic, Google, Azure, AWS Bedrock, Ollama, Groq + 17 more

## Vector Stores
Chroma, Pinecone, Qdrant, PGVector, Milvus, FAISS + 13 more

---
*For detailed information, see other files in .cg-aix-sdlc/ai-context/*
