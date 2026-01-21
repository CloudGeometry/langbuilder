# LangBuilder - Common Development Tasks

## Running the Application

### Backend Only
```bash
cd langbuilder
uv sync
uv run langbuilder run --port 8002
```

### Frontend Only
```bash
cd langbuilder/src/frontend
npm install
npm run dev  # Port 5175
```

### Full Stack (Development)
```bash
# Terminal 1: Backend
uv run langbuilder run

# Terminal 2: Frontend
cd langbuilder/src/frontend && npm run dev
```

### Docker
```bash
docker compose up -d
```

## Adding a New API Endpoint

### 1. Create Router File
`langbuilder/src/backend/base/langbuilder/api/v1/my_resource.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from langbuilder.api.utils import CurrentActiveUser, DbSession

router = APIRouter(prefix="/myresource", tags=["MyResource"])

@router.get("/")
async def list_resources(
    session: DbSession,
    current_user: CurrentActiveUser,
):
    # Implementation
    return []

@router.post("/", status_code=201)
async def create_resource(
    data: ResourceCreate,
    session: DbSession,
    current_user: CurrentActiveUser,
):
    # Implementation
    return resource
```

### 2. Register Router
In `langbuilder/src/backend/base/langbuilder/api/v1/__init__.py`:

```python
from langbuilder.api.v1.my_resource import router as my_resource_router

# Add to router list
v1_router.include_router(my_resource_router)
```

## Creating a New Component

### 1. Create Component File
`langbuilder/src/backend/base/langbuilder/components/{category}/my_component.py`:

```python
from langbuilder.custom import Component
from langbuilder.inputs.inputs import (
    StrInput,
    SecretStrInput,
    DropdownInput,
)
from langbuilder.template.field.base import Output

class MyComponent(Component):
    display_name = "My Component"
    description = "Does something useful"
    icon = "Sparkles"  # Lucide icon

    inputs = [
        StrInput(
            name="query",
            display_name="Query",
            info="The input query",
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            value="MY_API_KEY",  # Env var name
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Result",
            method="process",
        ),
    ]

    def process(self) -> str:
        # Component logic here
        return f"Processed: {self.query}"
```

### 2. Register Component
In `langbuilder/src/backend/base/langbuilder/components/{category}/__init__.py`:

```python
from .my_component import MyComponent

__all__ = ["MyComponent"]
```

## Adding a New LLM Provider

### 1. Create LLM Component
```python
from langbuilder.base.models.model import LCModelComponent
from langchain_core.language_models import BaseChatModel

class MyLLMComponent(LCModelComponent):
    display_name = "My LLM"
    icon = "MessageSquare"

    inputs = [
        *LCModelComponent._base_inputs,
        SecretStrInput(name="api_key", display_name="API Key"),
        DropdownInput(
            name="model_name",
            options=["model-a", "model-b"],
            value="model-a",
        ),
    ]

    def build_model(self) -> BaseChatModel:
        from my_llm_package import MyChatModel

        return MyChatModel(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature,
        )
```

### 2. Add Dependencies
In `langbuilder/src/backend/base/pyproject.toml`:

```toml
[project.optional-dependencies]
my-llm = ["my-llm-package>=1.0.0"]
```

## Modifying Database Schema

### 1. Update Model
```python
# services/database/models/flow/model.py
class Flow(SQLModel, table=True):
    # Add new field
    new_field: str | None = Field(default=None, nullable=True)
```

### 2. Create Migration
```bash
cd langbuilder/src/backend/base
uv run alembic revision --autogenerate -m "Add new_field to flow"
```

### 3. Review Migration
Check generated file in `langbuilder/alembic/versions/`

### 4. Apply Migration
```bash
uv run alembic upgrade head
```

## Adding Tests

### Unit Test
`langbuilder/src/backend/tests/unit/components/test_my_component.py`:

```python
import pytest
from langbuilder.components.my_category import MyComponent

def test_my_component_process():
    component = MyComponent()
    component.query = "test input"
    result = component.process()
    assert "test input" in result

@pytest.mark.asyncio
async def test_my_component_async():
    component = MyComponent()
    result = await component.async_process()
    assert result is not None
```

### API Test
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_resource(client: AsyncClient, logged_in_headers):
    response = await client.post(
        "/api/v1/myresource",
        json={"name": "test"},
        headers=logged_in_headers,
    )
    assert response.status_code == 201
```

### Run Tests
```bash
# All tests
uv run pytest

# Specific file
uv run pytest langbuilder/src/backend/tests/unit/components/test_my_component.py

# With coverage
uv run pytest --cov=langbuilder --cov-report=html

# Integration tests
uv run pytest langbuilder/src/backend/tests/integration/
```

## Frontend Tasks

### Add New Store
`langbuilder/src/frontend/src/stores/myStore.ts`:

```typescript
import { create } from "zustand";

interface MyStoreState {
  data: string[];
  addItem: (item: string) => void;
  clearItems: () => void;
}

export const useMyStore = create<MyStoreState>((set) => ({
  data: [],
  addItem: (item) => set((state) => ({ data: [...state.data, item] })),
  clearItems: () => set({ data: [] }),
}));
```

### Add New API Call
`langbuilder/src/frontend/src/controllers/API/index.ts`:

```typescript
export async function getMyResource(resourceId: string): Promise<MyResource> {
  const response = await api.get(`/api/v1/myresource/${resourceId}`);
  return response.data;
}
```

## Environment Variables

### Backend
```bash
# Database
LANGBUILDER_DATABASE_URL=sqlite+aiosqlite:///./langbuilder.db

# Auth
LANGBUILDER_AUTO_LOGIN=true
LANGBUILDER_SECRET_KEY=your-secret-key

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

### Frontend
```bash
# .env
VITE_API_URL=http://localhost:8002
```

---
*AI Context Document - CloudGeometry AIx SDLC*
