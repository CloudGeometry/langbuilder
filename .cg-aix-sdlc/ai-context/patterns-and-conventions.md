# LangBuilder - Patterns and Conventions

## Python Conventions

### Linting: Ruff
Configuration in `pyproject.toml`. Key rules:
- Line length: 120
- Python 3.10+ features allowed
- Type hints required

### File Organization
```
module/
├── __init__.py      # Public exports
├── model.py         # SQLModel definitions
├── schema.py        # Pydantic schemas
├── crud.py          # Database operations
├── service.py       # Business logic
└── utils.py         # Helpers
```

### Naming
| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `FlowService` |
| Functions | snake_case | `get_flow_by_id` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _prefix | `_internal_method` |
| Async | async prefix | `async def get_flow` |

### Async Pattern
```python
# Always use async for I/O
async def get_flows(user_id: UUID) -> list[Flow]:
    async with session_scope() as session:
        result = await session.exec(
            select(Flow).where(Flow.user_id == user_id)
        )
        return list(result.all())

# Parallel execution
results = await asyncio.gather(
    fetch_data(id1),
    fetch_data(id2),
)
```

### Type Hints
```python
from uuid import UUID
from typing import Optional

async def create_flow(
    data: FlowCreate,
    user_id: UUID,
    folder_id: Optional[UUID] = None
) -> Flow:
    ...
```

## TypeScript Conventions

### Linting: Biome
Configuration in `biome.json`.

### File Organization
```
component/
├── index.tsx        # Main component
├── types.ts         # Type definitions
├── hooks.ts         # Custom hooks
└── utils.ts         # Helpers
```

### Naming
| Element | Convention | Example |
|---------|------------|---------|
| Components | PascalCase | `FlowCanvas` |
| Hooks | useCamelCase | `useFlowStore` |
| Functions | camelCase | `formatDate` |
| Types | PascalCase | `FlowData` |
| Constants | UPPER_SNAKE | `API_BASE_URL` |

### Component Pattern
```typescript
interface FlowNodeProps {
  nodeId: string;
  data: NodeData;
}

export const FlowNode: React.FC<FlowNodeProps> = ({ nodeId, data }) => {
  const { updateNode } = useFlowStore();

  const handleUpdate = useCallback((value: string) => {
    updateNode(nodeId, { value });
  }, [nodeId, updateNode]);

  return <div>...</div>;
};
```

## Component Authoring

### Basic Component
```python
from langbuilder.base.models.model import LCModelComponent
from langbuilder.inputs.inputs import (
    SecretStrInput,
    DropdownInput,
    SliderInput,
)

class MyLLMComponent(LCModelComponent):
    display_name = "My LLM"
    description = "Custom LLM integration"
    icon = "Bot"  # Lucide icon name

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            required=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model",
            options=["model-a", "model-b"],
            value="model-a",
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.7,
            range_spec=RangeSpec(min=0, max=1, step=0.1),
        ),
    ]

    def build_model(self) -> LanguageModel:
        return MyLLM(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature,
        )
```

### Input Types
```python
# Text input
StrInput(name="query", display_name="Query")

# Secret (masked)
SecretStrInput(name="api_key", display_name="API Key")

# Dropdown
DropdownInput(name="model", options=["a", "b"], value="a")

# Slider
SliderInput(name="temp", value=0.5, range_spec=RangeSpec(min=0, max=1))

# Boolean
BoolInput(name="stream", value=True)

# Integer
IntInput(name="max_tokens", value=1000, range_spec=RangeSpec(min=1, max=4096))

# Handle (connection)
HandleInput(name="llm", input_types=["LanguageModel"])

# Data
DataInput(name="documents", input_types=["Data"])
```

### Component Registration
Components are auto-discovered from `langbuilder/components/` directories.
Add to `__init__.py`:

```python
from .my_component import MyLLMComponent

__all__ = ["MyLLMComponent"]
```

## API Patterns

### Router Definition
```python
from fastapi import APIRouter, Depends, HTTPException
from langbuilder.api.utils import CurrentActiveUser, DbSession

router = APIRouter(prefix="/myresource", tags=["MyResource"])

@router.get("/{resource_id}", response_model=ResourceRead)
async def get_resource(
    resource_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
):
    resource = await _get_resource(session, resource_id, current_user.id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
```

### Error Handling
```python
from fastapi import HTTPException, status

# Standard errors
raise HTTPException(status_code=404, detail="Not found")
raise HTTPException(status_code=400, detail="Invalid input")
raise HTTPException(status_code=403, detail="Access denied")

# Validation errors
raise HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"field": "error message"}
)
```

## Testing Patterns

### Backend Tests (pytest)
```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

async def test_create_flow(client, logged_in_headers):
    response = await client.post(
        "/api/v1/flows",
        json={"name": "Test", "data": {"nodes": [], "edges": []}},
        headers=logged_in_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

### Frontend Tests (Jest)
```typescript
import { render, screen } from '@testing-library/react';
import { FlowCanvas } from './FlowCanvas';

describe('FlowCanvas', () => {
  it('renders correctly', () => {
    render(<FlowCanvas flowId="test-123" />);
    expect(screen.getByTestId('flow-canvas')).toBeInTheDocument();
  });
});
```

## Git Conventions

### Commit Messages
```
feat: Add new LLM provider integration
fix: Resolve flow execution timeout
docs: Update API documentation
refactor: Simplify graph execution logic
test: Add tests for flow service
```

### Branch Naming
```
feature/add-openai-o1
fix/flow-execution-timeout
docs/api-reference
```

---
*AI Context Document - CloudGeometry AIx SDLC*
