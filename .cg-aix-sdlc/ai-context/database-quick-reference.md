# LangBuilder - Database Quick Reference

## ORM: SQLModel
SQLModel combines SQLAlchemy and Pydantic for type-safe database access.

## Core Models

### User
```python
# Location: services/database/models/user/model.py
class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str  # bcrypt hashed
    profile_image: str | None
    is_active: bool = False
    is_superuser: bool = False
    create_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    store_api_key: str | None

    # Relationships
    api_keys: list["ApiKey"]
    flows: list["Flow"]
    variables: list["Variable"]
    folders: list["Folder"]
```

### Flow
```python
# Location: services/database/models/flow/model.py
class Flow(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str = Field(index=True)
    description: str | None
    data: dict | None  # JSON: {"nodes": [], "edges": []}
    user_id: UUID = Field(foreign_key="user.id")
    folder_id: UUID | None = Field(foreign_key="folder.id")
    is_component: bool = False
    endpoint_name: str | None = Field(index=True)
    webhook: bool = False
    mcp_enabled: bool = False
    access_type: AccessTypeEnum = "PRIVATE"  # or "PUBLIC"
    updated_at: datetime

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name"),
        UniqueConstraint("user_id", "endpoint_name"),
    )
```

### Folder
```python
class Folder(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    description: str | None
    user_id: UUID = Field(foreign_key="user.id")
    parent_id: UUID | None = Field(foreign_key="folder.id")

    flows: list["Flow"]
```

### ApiKey
```python
class ApiKey(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    api_key: str  # hashed
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime
    last_used_at: datetime | None
    is_active: bool = True
```

### Variable (Encrypted Credentials)
```python
class Variable(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    value: str  # encrypted
    user_id: UUID = Field(foreign_key="user.id")
    type: str  # "credential", "generic"
```

### MessageTable
```python
class MessageTable(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    flow_id: UUID = Field(foreign_key="flow.id")
    session_id: str
    sender: str  # "User", "Machine"
    sender_name: str
    text: str
    files: list[str] | None
    timestamp: datetime
```

### TransactionTable
```python
class TransactionTable(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    flow_id: UUID
    source: str
    target: str
    target_args: dict
    status: str  # "success", "error"
    error: str | None
    timestamp: datetime
```

### VertexBuildTable
```python
class VertexBuildTable(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    flow_id: UUID = Field(foreign_key="flow.id")
    vertex_id: str
    build_id: UUID
    params: str  # JSON
    outputs: str | None  # JSON
    artifacts: str | None  # JSON
    timestamp: datetime
```

## Database Session

### Async Session Pattern
```python
from langbuilder.services.deps import session_scope

async with session_scope() as session:
    result = await session.exec(select(Flow).where(Flow.id == flow_id))
    flow = result.first()
```

### FastAPI Dependency
```python
from langbuilder.api.utils import DbSession

@router.get("/flows/{flow_id}")
async def get_flow(flow_id: UUID, session: DbSession):
    stmt = select(Flow).where(Flow.id == flow_id)
    result = await session.exec(stmt)
    return result.first()
```

## Common Queries

### List with Pagination
```python
from fastapi_pagination.ext.sqlmodel import apaginate

stmt = select(Flow).where(Flow.user_id == user_id)
return await apaginate(session, stmt, params=params)
```

### Filter with Multiple Conditions
```python
stmt = select(Flow).where(
    Flow.user_id == user_id,
    Flow.folder_id == folder_id,
    Flow.is_component == False
).order_by(Flow.updated_at.desc())
```

### Eager Loading Relationships
```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(
    selectinload(User.flows),
    selectinload(User.api_keys)
).where(User.id == user_id)
```

## Migrations (Alembic)

### Create Migration
```bash
uv run alembic revision --autogenerate -m "description"
```

### Run Migrations
```bash
uv run alembic upgrade head
```

### Migration Location
`langbuilder/src/backend/base/langbuilder/alembic/versions/`

## Database Configuration

### Environment Variables
```bash
LANGBUILDER_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
# or
LANGBUILDER_DATABASE_URL=sqlite+aiosqlite:///./langbuilder.db
```

## CRUD Patterns

### Create
```python
db_flow = Flow.model_validate(flow_create, from_attributes=True)
session.add(db_flow)
await session.commit()
await session.refresh(db_flow)
```

### Update
```python
for key, value in update_data.items():
    setattr(db_flow, key, value)
session.add(db_flow)
await session.commit()
```

### Delete
```python
await session.delete(flow)
await session.commit()
```

---
*AI Context Document - CloudGeometry AIx SDLC*
