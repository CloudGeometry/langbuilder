# Architectural Patterns and Principles - LangBuilder

## Overview

This document describes the architectural patterns, coding conventions, and design principles used throughout the LangBuilder codebase.

## Design Patterns

### 1. Component Pattern (Backend)

LangBuilder uses a component-based architecture for AI workflow building blocks.

```python
# Component base class pattern
from langbuilder.base.component import Component

class OpenAIModelComponent(Component):
    """OpenAI LLM component."""

    display_name = "OpenAI"
    description = "Generate text using OpenAI models"
    icon = "OpenAI"

    # Input parameters
    model_name: str = Field(default="gpt-4", description="Model to use")
    temperature: float = Field(default=0.7, ge=0, le=2)
    api_key: SecretStr = Field(description="OpenAI API key")

    # Output types
    outputs = [
        Output(name="text", display_name="Text", method="generate_text"),
        Output(name="model", display_name="Model", method="build_model"),
    ]

    def build_model(self) -> BaseChatModel:
        """Build the LangChain model instance."""
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key.get_secret_value(),
        )

    def generate_text(self, input_text: str) -> str:
        """Generate text response."""
        model = self.build_model()
        return model.invoke(input_text).content
```

**Benefits**:
- Declarative component definition
- Automatic UI generation from schema
- Type-safe parameter handling
- Reusable across workflows

### 2. Graph Execution Pattern

Workflows are represented as directed acyclic graphs (DAGs) with vertices and edges.

```python
# Graph execution pattern
class Graph:
    def __init__(self, flow_data: dict):
        self.vertices: Dict[str, Vertex] = {}
        self.edges: Dict[str, Edge] = {}
        self._build_graph(flow_data)

    async def execute(self, inputs: dict) -> dict:
        """Execute graph with topological sort."""
        # 1. Determine execution order
        sorted_vertices = self._topological_sort()

        # 2. Execute vertices in parallel where possible
        for level in self._get_parallel_levels(sorted_vertices):
            await asyncio.gather(*[
                self._execute_vertex(v, inputs)
                for v in level
            ])

        # 3. Return final outputs
        return self._collect_outputs()

    async def _execute_vertex(self, vertex: Vertex, inputs: dict):
        """Execute single vertex with dependency resolution."""
        # Get inputs from connected edges
        vertex_inputs = self._resolve_inputs(vertex)

        # Execute the component
        result = await vertex.build(vertex_inputs)

        # Store results for downstream vertices
        self._store_result(vertex.id, result)
```

### 3. Repository Pattern (Data Access)

Data access is abstracted through repository-like patterns in the services layer.

```python
# Service/Repository pattern
class FlowService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_flow(self, flow_id: UUID, user_id: UUID) -> Flow:
        """Get flow by ID with ownership check."""
        stmt = select(Flow).where(
            Flow.id == flow_id,
            Flow.user_id == user_id
        )
        result = await self.session.execute(stmt)
        flow = result.scalar_one_or_none()
        if not flow:
            raise FlowNotFoundError(flow_id)
        return flow

    async def create_flow(self, data: FlowCreate, user_id: UUID) -> Flow:
        """Create new flow."""
        flow = Flow(**data.dict(), user_id=user_id)
        self.session.add(flow)
        await self.session.commit()
        await self.session.refresh(flow)
        return flow

    async def list_flows(
        self,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Flow]:
        """List flows with pagination."""
        stmt = select(Flow).where(Flow.user_id == user_id)
        if folder_id:
            stmt = stmt.where(Flow.folder_id == folder_id)
        stmt = stmt.order_by(Flow.updated_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
```

### 4. Factory Pattern (Service Instantiation)

Services are instantiated through a factory pattern with dependency injection.

```python
# Factory pattern
class ServiceFactory:
    """Factory for creating service instances."""

    @staticmethod
    def create_flow_service(session: AsyncSession) -> FlowService:
        return FlowService(session)

    @staticmethod
    def create_user_service(session: AsyncSession) -> UserService:
        return UserService(session)

    @staticmethod
    def create_graph_service(
        flow: Flow,
        session: AsyncSession
    ) -> GraphService:
        return GraphService(flow, session)

# Dependency injection in FastAPI
async def get_flow_service(
    session: AsyncSession = Depends(get_session)
) -> FlowService:
    return ServiceFactory.create_flow_service(session)
```

### 5. Observer Pattern (Event Streaming)

Real-time updates use Server-Sent Events (SSE) with an observer-like pattern.

```python
# Event streaming pattern
class BuildEventHandler:
    def __init__(self):
        self.subscribers: Dict[str, Queue] = {}

    async def subscribe(self, build_id: str) -> AsyncGenerator:
        """Subscribe to build events."""
        queue = asyncio.Queue()
        self.subscribers[build_id] = queue

        try:
            while True:
                event = await queue.get()
                yield event
                if event.type == "complete":
                    break
        finally:
            del self.subscribers[build_id]

    async def emit(self, build_id: str, event: BuildEvent):
        """Emit event to subscriber."""
        if build_id in self.subscribers:
            await self.subscribers[build_id].put(event)

# Usage in API
@router.get("/build/{flow_id}/events")
async def stream_events(
    flow_id: UUID,
    handler: BuildEventHandler = Depends(get_event_handler)
):
    async def event_generator():
        async for event in handler.subscribe(str(flow_id)):
            yield f"data: {event.json()}\n\n"

    return EventSourceResponse(event_generator())
```

### 6. Store Pattern (Frontend State)

Zustand stores follow a consistent pattern for state management.

```typescript
// Store pattern (TypeScript)
interface FlowState {
  nodes: Node[];
  edges: Edge[];
  selectedNodes: string[];

  // Actions
  addNode: (node: Node) => void;
  updateNode: (id: string, data: Partial<NodeData>) => void;
  deleteNode: (id: string) => void;
  addEdge: (edge: Edge) => void;
  setSelectedNodes: (ids: string[]) => void;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodes: [],

  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),

  updateNode: (id, data) => set((state) => ({
    nodes: state.nodes.map((n) =>
      n.id === id ? { ...n, data: { ...n.data, ...data } } : n
    )
  })),

  deleteNode: (id) => set((state) => ({
    nodes: state.nodes.filter((n) => n.id !== id),
    edges: state.edges.filter(
      (e) => e.source !== id && e.target !== id
    )
  })),

  // ... more actions
}));
```

## Coding Conventions

### Python (Backend)

**File Organization**:
```
module/
├── __init__.py          # Public API exports
├── base.py              # Base classes
├── models.py            # Data models
├── schemas.py           # Pydantic schemas
├── router.py            # API routes
├── service.py           # Business logic
├── utils.py             # Helper functions
└── exceptions.py        # Custom exceptions
```

**Naming Conventions**:
| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `FlowService` |
| Functions | snake_case | `get_flow_by_id` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _prefix | `_internal_method` |
| Type vars | Single caps | `T`, `K`, `V` |

**Async/Await**:
```python
# Prefer async functions for I/O operations
async def get_user(user_id: UUID) -> User:
    async with get_session() as session:
        return await session.get(User, user_id)

# Use asyncio.gather for parallel operations
async def get_all_data(ids: List[UUID]) -> List[Data]:
    return await asyncio.gather(*[
        fetch_data(id) for id in ids
    ])
```

### TypeScript (Frontend)

**File Organization**:
```
component/
├── index.tsx            # Main component
├── styles.ts            # Styled components (if any)
├── types.ts             # Type definitions
├── hooks.ts             # Custom hooks
├── utils.ts             # Helper functions
└── __tests__/           # Unit tests
    └── component.test.tsx
```

**Naming Conventions**:
| Element | Convention | Example |
|---------|------------|---------|
| Components | PascalCase | `FlowCanvas` |
| Hooks | useCamelCase | `useFlowStore` |
| Utilities | camelCase | `formatDate` |
| Constants | UPPER_SNAKE | `API_BASE_URL` |
| Types/Interfaces | PascalCase | `FlowNode` |

**Component Pattern**:
```typescript
// Functional component with typed props
interface FlowCanvasProps {
  flowId: string;
  onSave?: (data: FlowData) => void;
}

export const FlowCanvas: React.FC<FlowCanvasProps> = ({
  flowId,
  onSave
}) => {
  // Hooks at top
  const { nodes, edges } = useFlowStore();
  const [isLoading, setIsLoading] = useState(false);

  // Callbacks
  const handleSave = useCallback(() => {
    onSave?.({ nodes, edges });
  }, [nodes, edges, onSave]);

  // Render
  return (
    <div className="flow-canvas">
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <ReactFlow nodes={nodes} edges={edges} />
      )}
    </div>
  );
};
```

## Error Handling Patterns

### Backend Error Handling

```python
# Custom exception hierarchy
class LangBuilderError(Exception):
    """Base exception for LangBuilder."""
    status_code = 500
    detail = "Internal server error"

class NotFoundError(LangBuilderError):
    status_code = 404

    def __init__(self, resource: str, id: str):
        self.detail = f"{resource} with id {id} not found"

class ValidationError(LangBuilderError):
    status_code = 422

    def __init__(self, errors: List[dict]):
        self.detail = errors

class AuthenticationError(LangBuilderError):
    status_code = 401
    detail = "Authentication required"

# Global exception handler
@app.exception_handler(LangBuilderError)
async def langbuilder_error_handler(
    request: Request,
    exc: LangBuilderError
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### Frontend Error Handling

```typescript
// Error boundary component
class ErrorBoundary extends React.Component<Props, State> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    // Report to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}

// API error handling
const handleApiError = (error: AxiosError) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        // Redirect to login
        break;
      case 404:
        // Show not found
        break;
      default:
        // Show generic error
    }
  } else if (error.request) {
    // Network error
  }
};
```

## Security Patterns

### Authentication

```python
# JWT token pattern
def create_access_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    payload = {
        "sub": str(user.id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["type"] != "access":
            raise InvalidTokenError()
        return payload
    except JWTError:
        raise InvalidTokenError()
```

### Authorization

```python
# Role-based access control
def require_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Superuser access required"
        )
    return current_user

# Resource ownership check
async def check_flow_ownership(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    service: FlowService = Depends(get_flow_service)
) -> Flow:
    flow = await service.get_flow(flow_id)
    if flow.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    return flow
```

### Input Validation

```python
# Pydantic validation
class FlowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    data: dict = Field(...)

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('data')
    def data_must_be_valid_flow(cls, v):
        if 'nodes' not in v or 'edges' not in v:
            raise ValueError('Invalid flow data structure')
        return v
```

## Performance Patterns

### Caching

```python
# Redis caching decorator
def cache(key_prefix: str, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"

            # Try cache first
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute and cache
            result = await func(*args, **kwargs)
            await redis.set(cache_key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return decorator

@cache("flow", ttl=300)
async def get_flow_with_cache(flow_id: UUID) -> dict:
    return await flow_service.get_flow(flow_id)
```

### Pagination

```python
# Consistent pagination pattern
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

async def paginate(
    query,
    page: int = 1,
    page_size: int = 20
) -> PaginatedResponse:
    total = await session.scalar(select(func.count()).select_from(query.subquery()))

    items = await session.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )

    return PaginatedResponse(
        items=list(items.scalars().all()),
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size)
    )
```

## Testing Patterns

### Unit Testing (Backend)

```python
# Pytest with async support
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def authenticated_client(client, test_user):
    token = create_access_token(test_user)
    client.headers["Authorization"] = f"Bearer {token}"
    return client

async def test_create_flow(authenticated_client, test_user):
    response = await authenticated_client.post(
        "/api/v1/flows",
        json={"name": "Test Flow", "data": {"nodes": [], "edges": []}}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Flow"
```

### Component Testing (Frontend)

```typescript
// Vitest with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { FlowCanvas } from './FlowCanvas';

describe('FlowCanvas', () => {
  it('renders flow nodes', () => {
    render(<FlowCanvas flowId="test-123" />);
    expect(screen.getByTestId('flow-canvas')).toBeInTheDocument();
  });

  it('calls onSave when save button clicked', async () => {
    const onSave = vi.fn();
    render(<FlowCanvas flowId="test-123" onSave={onSave} />);

    fireEvent.click(screen.getByRole('button', { name: /save/i }));

    expect(onSave).toHaveBeenCalled();
  });
});
```

---

*Generated by CloudGeometry AIx SDLC - Architecture Documentation*
