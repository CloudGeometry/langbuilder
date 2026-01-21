# LangBuilder - Architecture Summary

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  Flow Canvas (XYFlow) → Zustand Stores → API Client          │
├─────────────────────────────────────────────────────────────┤
│                    API Layer (FastAPI)                       │
│  v1 Routers (18) │ v2 Routers (2) │ OpenAI Compat Router     │
├─────────────────────────────────────────────────────────────┤
│                   Services Layer                             │
│  Auth │ Flow │ Chat │ Database │ Cache │ Storage             │
├─────────────────────────────────────────────────────────────┤
│                   Graph Engine                               │
│  Vertex → Edge → Topological Sort → Parallel Execution       │
├─────────────────────────────────────────────────────────────┤
│                   Component Registry                         │
│  455+ Components: LLMs │ Embeddings │ VectorStores │ Tools   │
├─────────────────────────────────────────────────────────────┤
│                   Data Layer                                 │
│  SQLModel ORM → Alembic Migrations → SQLite/PostgreSQL       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Action (Frontend)
    ↓
API Request (FastAPI Router)
    ↓
Service Layer (Business Logic)
    ↓
Graph Engine (for Flow execution)
    ↓
Component Execution (LangChain)
    ↓
Database/Cache Operations
    ↓
Response (JSON/SSE Stream)
```

## Key Patterns

### 1. Component Pattern
Components are declarative Python classes with inputs/outputs that generate UI automatically:

```python
class OpenAIModelComponent(LCModelComponent):
    display_name = "OpenAI"
    inputs = [
        SecretStrInput(name="api_key", ...),
        DropdownInput(name="model_name", ...),
    ]

    def build_model(self) -> LanguageModel:
        return ChatOpenAI(...)
```

### 2. Graph Execution
Workflows are DAGs executed with topological sorting:
- Vertices execute in parallel when independent
- Results propagate through edges
- State is tracked per-vertex for debugging

### 3. Service Factory
Services are injected via FastAPI dependencies:

```python
async def get_flow_service(
    session: AsyncSession = Depends(get_session)
) -> FlowService:
    return FlowService(session)
```

### 4. Zustand Stores (Frontend)
State management with minimal boilerplate:

```typescript
const useFlowStore = create<FlowStoreType>((set, get) => ({
    nodes: [],
    edges: [],
    addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),
}));
```

## Important Modules

| Module | Purpose | Location |
|--------|---------|----------|
| `api/router.py` | Route registration | `backend/base/langbuilder/api/` |
| `graph/graph/base.py` | Graph execution engine | `backend/base/langbuilder/graph/` |
| `services/database/` | DB models & CRUD | `backend/base/langbuilder/services/` |
| `components/` | All AI components | `backend/base/langbuilder/components/` |
| `flowStore.ts` | Flow state management | `frontend/src/stores/` |

## Integration Points

### LLM Providers (24)
OpenAI, Anthropic, Google, Azure, AWS Bedrock, Ollama, Groq, etc.

### Vector Stores (19)
Chroma, Pinecone, Qdrant, PGVector, Milvus, FAISS, etc.

### External Tools
MCP Protocol, Jira, Confluence, HubSpot, Salesforce, etc.

## Authentication
- JWT tokens (access + refresh)
- Cookie-based sessions
- Auto-login mode for development
- API key authentication for endpoints

---
*AI Context Document - CloudGeometry AIx SDLC*
