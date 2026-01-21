# 30-Day Mastery Roadmap

A comprehensive month-long plan to become a proficient LangBuilder developer.

## Overview

| Week | Focus | Goal |
|------|-------|------|
| Week 1 | Orientation | Running environment, basic understanding |
| Week 2 | Component System | Build and extend components |
| Week 3 | API and Services | Deep dive into backend |
| Week 4 | Advanced Topics | Testing, deployment, optimization |

---

## Week 1: Orientation

*Complete the [Week 1 Guide](./week-1-guide.md) for detailed daily activities.*

### Goals

- [ ] Development environment running
- [ ] Understand project structure
- [ ] Navigate codebase confidently
- [ ] Make first contribution

### Key Milestones

| Day | Milestone |
|-----|-----------|
| Day 1 | Application running locally |
| Day 2 | Understand architecture |
| Day 3 | Navigate backend code |
| Day 4 | Navigate frontend code |
| Day 5 | First commit merged |

---

## Week 2: Component System Deep Dive

### Day 6-7: Component Architecture

#### Learning Objectives

- Understand the component base classes
- Learn the component registration system
- Explore existing components as examples

#### Key Files to Study

```
langbuilder/src/backend/base/langbuilder/components/
├── __init__.py           # Component registration
├── models/               # LLM components
│   ├── openai.py
│   ├── anthropic.py
│   └── ...
├── vectorstores/         # Vector store components
├── tools/                # Tool components
├── inputs/               # Input components
├── outputs/              # Output components
└── helpers/              # Utility components
```

#### Study These Patterns

```python
# Component base class pattern
from langbuilder.base.component import Component

class ExampleComponent(Component):
    display_name = "Example"
    description = "Example component"
    icon = "Example"

    # Input parameters
    param: str = Field(default="", description="Parameter")

    # Output types
    outputs = [
        Output(name="result", display_name="Result", method="process"),
    ]

    def process(self) -> str:
        # Implementation
        return result
```

#### Hands-On Exercise

1. Find and read the OpenAI component code
2. Trace how inputs are validated
3. Understand how outputs are defined

### Day 8-9: Building a Custom Component

#### Step-by-Step Component Creation

1. **Choose a category**: Decide where your component belongs
2. **Create the file**: Add to appropriate category folder
3. **Implement the class**: Follow the component pattern
4. **Register the component**: Add to `__init__.py`
5. **Test the component**: Verify it appears in the UI

#### Example: Creating a Simple Tool Component

```python
# langbuilder/src/backend/base/langbuilder/components/tools/example_tool.py

from langbuilder.base.component import Component
from langbuilder.base.inputs import MessageTextInput
from langbuilder.base.outputs import Output
from pydantic import Field

class ExampleToolComponent(Component):
    """Example tool component."""

    display_name = "Example Tool"
    description = "A simple example tool"
    icon = "Tool"
    category = "tools"

    # Inputs
    input_text: str = MessageTextInput(
        display_name="Input Text",
        info="Text to process"
    )

    # Outputs
    outputs = [
        Output(
            name="processed_text",
            display_name="Processed Text",
            method="process_text"
        ),
    ]

    def process_text(self) -> str:
        """Process the input text."""
        return self.input_text.upper()
```

#### Registration

```python
# In __init__.py for the category
from .example_tool import ExampleToolComponent

__all__ = [
    # ... existing exports
    "ExampleToolComponent",
]
```

### Day 10: Component Testing

#### Writing Component Tests

```python
# langbuilder/src/backend/tests/unit/components/test_example_tool.py

import pytest
from langbuilder.components.tools.example_tool import ExampleToolComponent

class TestExampleToolComponent:
    def test_process_text_uppercase(self):
        component = ExampleToolComponent(input_text="hello")
        result = component.process_text()
        assert result == "HELLO"

    def test_process_text_empty(self):
        component = ExampleToolComponent(input_text="")
        result = component.process_text()
        assert result == ""
```

#### Running Component Tests

```bash
# Run specific component tests
uv run pytest src/backend/tests/unit/components/test_example_tool.py -v

# Run all component tests
uv run pytest src/backend/tests/unit/components/ -v
```

### Week 2 Checklist

- [ ] Understand component architecture
- [ ] Read 5+ existing components
- [ ] Build a custom component
- [ ] Write tests for your component
- [ ] Component appears in UI

---

## Week 3: API and Services

### Day 11-12: FastAPI Deep Dive

#### Learning Objectives

- Understand FastAPI route patterns
- Learn dependency injection patterns
- Explore request/response schemas

#### Key API Patterns

```python
# Router pattern
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/flows", tags=["flows"])

@router.post("/", response_model=FlowRead)
async def create_flow(
    flow: FlowCreate,
    current_user: User = Depends(get_current_user),
    service: FlowService = Depends(get_flow_service),
) -> FlowRead:
    return await service.create_flow(flow, current_user.id)
```

#### Study These Files

| File | Purpose |
|------|---------|
| `api/router.py` | Main router aggregation |
| `api/v1/flows.py` | Flow CRUD operations |
| `api/v1/build.py` | Flow execution |
| `api/v1/chat.py` | Chat interface |

#### Hands-On Exercise

1. Add a new endpoint to an existing router
2. Create request/response schemas
3. Write tests for your endpoint

### Day 13-14: Service Layer

#### Learning Objectives

- Understand service patterns
- Learn database operations
- Explore transaction handling

#### Service Pattern

```python
# Service pattern
class FlowService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_flow(
        self,
        data: FlowCreate,
        user_id: UUID
    ) -> Flow:
        flow = Flow(**data.dict(), user_id=user_id)
        self.session.add(flow)
        await self.session.commit()
        await self.session.refresh(flow)
        return flow
```

#### Database Migrations

```bash
# Create a new migration
make alembic-revision message="Add new field"

# Apply migrations
make alembic-upgrade

# Check current revision
make alembic-current

# View migration history
make alembic-history
```

### Day 15: Graph Execution Engine

#### Learning Objectives

- Understand how flows are executed
- Learn the vertex/edge model
- Explore parallel execution

#### Key Files

```
langbuilder/src/backend/base/langbuilder/graph/
├── graph/
│   ├── base.py          # Graph class
│   └── vertex.py        # Vertex implementation
├── edge/
│   └── base.py          # Edge implementation
└── utils/
    └── topological.py   # Execution ordering
```

#### Execution Flow

```
1. Flow JSON → Parse nodes and edges
2. Create Graph object
3. Build vertices from nodes
4. Topological sort for execution order
5. Execute vertices (parallel where possible)
6. Collect and return outputs
```

### Week 3 Checklist

- [ ] Add endpoint to existing router
- [ ] Create a new service method
- [ ] Run a database migration
- [ ] Understand graph execution
- [ ] Debug a flow execution

---

## Week 4: Advanced Topics

### Day 16-17: Testing Strategy

#### Test Types

| Type | Location | Purpose |
|------|----------|---------|
| Unit | `tests/unit/` | Individual components |
| Integration | `tests/integration/` | API endpoints |
| Frontend | `src/frontend/` | React components |

#### Running Tests

```bash
# Unit tests with parallelization
make unit_tests

# Integration tests
make integration_tests

# Tests with coverage
make coverage

# Specific test with verbose output
uv run pytest src/backend/tests/unit/test_specific.py -v -s
```

#### Writing Effective Tests

```python
# Use pytest fixtures
@pytest.fixture
async def test_user(session):
    user = User(username="test", email="test@test.com")
    session.add(user)
    await session.commit()
    return user

# Test with fixtures
async def test_create_flow(authenticated_client, test_user):
    response = await authenticated_client.post(
        "/api/v1/flows",
        json={"name": "Test Flow", "data": {"nodes": [], "edges": []}}
    )
    assert response.status_code == 201
```

### Day 18-19: Performance and Optimization

#### Backend Optimization

- Use async/await properly
- Implement caching where appropriate
- Profile slow endpoints

#### Frontend Optimization

- Use React.memo for expensive renders
- Implement virtual scrolling for lists
- Optimize bundle size

#### Profiling Commands

```bash
# Run tests with profiling
uv run pytest --profile src/backend/tests/

# Memory profiling
uv run python -m memory_profiler your_script.py
```

### Day 20-21: Docker and Deployment

#### Development with Docker

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Build images
make docker_build

# Run with docker-compose
make docker_compose_up
```

#### Docker Compose Structure

```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"

  langbuilder-backend:
    build:
      context: ./langbuilder
    ports:
      - "8002:8002"
    environment:
      - LANGBUILDER_DATABASE_URL=postgresql://langbuilder:langbuilder@postgres:5432/langbuilder

  langbuilder-frontend:
    build:
      context: ./langbuilder/src/frontend
    ports:
      - "3000:3000"
```

#### Production Considerations

- Use PostgreSQL instead of SQLite
- Configure proper CORS settings
- Set up SSL/TLS
- Configure logging and monitoring

### Day 22-24: Security and Authentication

#### Authentication Flow

1. User registers or logs in
2. Server issues JWT token
3. Client stores token
4. Token sent with each request
5. Server validates token

#### Key Security Files

| File | Purpose |
|------|---------|
| `services/auth/` | Authentication logic |
| `api/v1/login.py` | Login endpoints |
| `dependencies.py` | Auth dependencies |

#### OAuth Integration

```bash
# Configure OAuth in .env
GOOGLE_CLIENT_ID='your-client-id'
GOOGLE_CLIENT_SECRET='your-secret'
GOOGLE_REDIRECT_URI='http://localhost:8002/oauth/google/callback'
```

### Day 25-27: Frontend Advanced Topics

#### State Management Patterns

```typescript
// Zustand store pattern
export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],

  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),

  // Async actions
  fetchFlow: async (id) => {
    const response = await api.getFlow(id);
    set({ nodes: response.nodes, edges: response.edges });
  }
}));
```

#### React Flow Customization

- Custom node types
- Custom edge types
- Custom controls
- Keyboard shortcuts

### Day 28-30: Integration and Review

#### Complete a Feature

1. Choose a meaningful feature
2. Plan the implementation
3. Write backend API
4. Write frontend UI
5. Add tests
6. Document your changes
7. Submit PR

#### Code Review Checklist

- [ ] Code follows project conventions
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance considered

---

## Month-End Assessment

### Skills Checklist

#### Backend

- [ ] Create and modify API endpoints
- [ ] Write service layer code
- [ ] Create database migrations
- [ ] Build custom components
- [ ] Write comprehensive tests

#### Frontend

- [ ] Navigate React codebase
- [ ] Work with Zustand stores
- [ ] Customize flow editor
- [ ] Debug frontend issues

#### DevOps

- [ ] Run Docker environments
- [ ] Configure environment variables
- [ ] Deploy to staging

### Recommended Reading

- FastAPI documentation: https://fastapi.tiangolo.com
- LangChain documentation: https://python.langchain.com
- React documentation: https://react.dev
- React Flow documentation: https://reactflow.dev

### Next Steps After 30 Days

1. **Specialize**: Choose an area (backend, frontend, components)
2. **Contribute**: Take on larger features
3. **Mentor**: Help onboard new team members
4. **Innovate**: Propose new features or improvements

---

## Quick Reference

### Daily Commands

```bash
# Start development
make backend          # Terminal 1
cd src/frontend && npm start  # Terminal 2

# Test your changes
make unit_tests
make format
make lint

# Commit changes
git add .
git commit -m "feat: Description"
git push origin feature-branch
```

### Key Directories

| Path | Purpose |
|------|---------|
| `langbuilder/src/backend/base/langbuilder/api/` | API routes |
| `langbuilder/src/backend/base/langbuilder/components/` | Components |
| `langbuilder/src/backend/base/langbuilder/services/` | Business logic |
| `langbuilder/src/frontend/src/stores/` | State management |
| `langbuilder/src/frontend/src/pages/` | Page components |
| `langbuilder/src/backend/tests/` | Backend tests |

---

*Generated by CloudGeometry AIx SDLC - Onboarding Documentation*
