# Database Schemas - LangBuilder

## Overview

LangBuilder uses SQLModel (SQLAlchemy + Pydantic) for ORM with support for SQLite (development) and PostgreSQL (production). Database migrations are managed with Alembic.

---

## Database Configuration

| Setting | Value |
|---------|-------|
| ORM | SQLModel 0.0.22 |
| Migrations | Alembic >=1.13.0 |
| Default DB | SQLite |
| Production DB | PostgreSQL (optional) |
| Connection Pool | SQLAlchemy async |

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ password        │
│ is_active       │
│ is_superuser    │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Folder      │────▶│      Flow       │────▶│  PublishRecord  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ name            │     │ name            │     │ flow_id (FK)    │
│ user_id (FK)    │     │ data (JSON)     │     │ platform        │
│ parent_id (FK)  │     │ folder_id (FK)  │     │ external_id     │
└─────────────────┘     │ user_id (FK)    │     │ status          │
                        └────────┬────────┘     └─────────────────┘
         │                       │
         │ 1:N                   │ 1:N
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Variable     │     │   MessageTable  │     │ VertexBuildTable│
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ build_id (PK)   │
│ name            │     │ flow_id (FK)    │     │ flow_id (FK)    │
│ value           │     │ session_id      │     │ vertex_id       │
│ user_id (FK)    │     │ text            │     │ data (JSON)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐     ┌─────────────────┐
│     ApiKey      │     │TransactionTable │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ api_key         │     │ flow_id (FK)    │
│ user_id (FK)    │     │ vertex_id       │
└─────────────────┘     │ inputs (JSON)   │
                        │ outputs (JSON)  │
┌─────────────────┐     └─────────────────┘
│      File       │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ name            │
│ path            │
└─────────────────┘
```

---

## Table Definitions

### User

Stores user account information.

```python
class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str
    profile_image: str | None
    is_active: bool = False
    is_superuser: bool = False
    create_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    store_api_key: str | None
    optins: dict | None  # JSON column
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| username | VARCHAR | UNIQUE, INDEX |
| password | VARCHAR | NOT NULL |
| profile_image | VARCHAR | NULLABLE |
| is_active | BOOLEAN | DEFAULT FALSE |
| is_superuser | BOOLEAN | DEFAULT FALSE |
| create_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NOT NULL |
| last_login_at | DATETIME | NULLABLE |
| store_api_key | VARCHAR | NULLABLE |
| optins | JSON | NULLABLE |

**Relationships**: `api_keys`, `flows`, `variables`, `folders`

---

### Flow

Stores AI workflow definitions.

```python
class Flow(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str = Field(index=True)
    description: str | None
    icon: str | None
    icon_bg_color: str | None
    gradient: str | None
    data: dict | None  # JSON - flow definition
    is_component: bool = False
    updated_at: datetime | None
    webhook: bool = False
    endpoint_name: str | None
    tags: list[str] | None  # JSON
    locked: bool = False
    mcp_enabled: bool = False
    action_name: str | None
    action_description: str | None
    access_type: AccessTypeEnum = "PRIVATE"
    user_id: UUID | None
    folder_id: UUID | None
    fs_path: str | None
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR | INDEX |
| description | TEXT | NULLABLE, INDEX |
| icon | VARCHAR | NULLABLE |
| icon_bg_color | VARCHAR(7) | NULLABLE |
| gradient | VARCHAR | NULLABLE |
| data | JSON | NULLABLE |
| is_component | BOOLEAN | DEFAULT FALSE |
| updated_at | DATETIME | NULLABLE |
| webhook | BOOLEAN | DEFAULT FALSE |
| endpoint_name | VARCHAR | NULLABLE, INDEX |
| tags | JSON | DEFAULT [] |
| locked | BOOLEAN | DEFAULT FALSE |
| mcp_enabled | BOOLEAN | DEFAULT FALSE |
| action_name | VARCHAR | NULLABLE |
| action_description | TEXT | NULLABLE |
| access_type | ENUM | DEFAULT 'PRIVATE' |
| user_id | UUID | FK(user.id), INDEX |
| folder_id | UUID | FK(folder.id), INDEX |
| fs_path | VARCHAR | NULLABLE |

**Constraints**:
- UNIQUE(user_id, name)
- UNIQUE(user_id, endpoint_name)

**Relationships**: `user`, `folder`, `publish_records`

---

### Folder

Organizes flows into projects/folders.

```python
class Folder(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str = Field(index=True)
    description: str | None
    auth_settings: dict | None  # JSON
    parent_id: UUID | None
    user_id: UUID | None
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR | INDEX |
| description | TEXT | NULLABLE |
| auth_settings | JSON | NULLABLE |
| parent_id | UUID | FK(folder.id), NULLABLE |
| user_id | UUID | FK(user.id), NULLABLE |

**Constraints**: UNIQUE(user_id, name)

**Relationships**: `parent`, `children`, `user`, `flows`

---

### ApiKey

Manages API keys for programmatic access.

```python
class ApiKey(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str | None
    api_key: str
    created_at: datetime
    last_used_at: datetime | None
    total_uses: int = 0
    is_active: bool = True
    user_id: UUID
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR | NULLABLE, INDEX |
| api_key | VARCHAR | UNIQUE, INDEX |
| created_at | DATETIME | NOT NULL |
| last_used_at | DATETIME | NULLABLE |
| total_uses | INTEGER | DEFAULT 0 |
| is_active | BOOLEAN | DEFAULT TRUE |
| user_id | UUID | FK(user.id), INDEX |

**Relationships**: `user`

---

### Variable

Stores encrypted variables and credentials.

```python
class Variable(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    value: str  # encrypted
    default_fields: list[str] | None  # JSON
    type: str | None
    created_at: datetime | None
    updated_at: datetime | None
    user_id: UUID
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR | NOT NULL |
| value | VARCHAR | NOT NULL (encrypted) |
| default_fields | JSON | NULLABLE |
| type | VARCHAR | NULLABLE |
| created_at | DATETIME | NULLABLE |
| updated_at | DATETIME | NULLABLE |
| user_id | UUID | FK(user.id) |

**Relationships**: `user`

---

### MessageTable

Stores chat messages.

```python
class MessageTable(SQLModel, table=True):
    __tablename__ = "message"

    id: UUID = Field(primary_key=True)
    timestamp: datetime
    sender: str
    sender_name: str
    session_id: str
    text: str
    files: list[str]  # JSON
    error: bool = False
    edit: bool = False
    flow_id: UUID | None
    properties: dict  # JSON
    category: str
    content_blocks: list[dict]  # JSON
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| timestamp | DATETIME | NOT NULL |
| sender | VARCHAR | NOT NULL |
| sender_name | VARCHAR | NOT NULL |
| session_id | VARCHAR | NOT NULL |
| text | TEXT | NOT NULL |
| files | JSON | DEFAULT [] |
| error | BOOLEAN | DEFAULT FALSE |
| edit | BOOLEAN | DEFAULT FALSE |
| flow_id | UUID | NULLABLE |
| properties | JSON | NOT NULL |
| category | TEXT | NOT NULL |
| content_blocks | JSON | DEFAULT [] |

---

### File

Tracks uploaded files.

```python
class File(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    user_id: UUID
    name: str
    path: str
    size: int
    provider: str | None
    created_at: datetime
    updated_at: datetime
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK(user.id) |
| name | VARCHAR | UNIQUE, NOT NULL |
| path | VARCHAR | NOT NULL |
| size | INTEGER | NOT NULL |
| provider | VARCHAR | NULLABLE |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NOT NULL |

---

### TransactionTable

Logs execution transactions.

```python
class TransactionTable(SQLModel, table=True):
    __tablename__ = "transaction"

    id: UUID = Field(primary_key=True)
    timestamp: datetime
    vertex_id: str
    target_id: str | None
    inputs: dict | None  # JSON
    outputs: dict | None  # JSON
    status: str
    error: str | None
    flow_id: UUID
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| timestamp | DATETIME | NOT NULL |
| vertex_id | VARCHAR | NOT NULL |
| target_id | VARCHAR | NULLABLE |
| inputs | JSON | NULLABLE |
| outputs | JSON | NULLABLE |
| status | VARCHAR | NOT NULL |
| error | VARCHAR | NULLABLE |
| flow_id | UUID | NOT NULL |

---

### VertexBuildTable

Stores vertex build results.

```python
class VertexBuildTable(SQLModel, table=True):
    __tablename__ = "vertex_build"

    build_id: UUID = Field(primary_key=True)
    timestamp: datetime
    id: str  # vertex_id
    data: dict | None  # JSON
    artifacts: dict | None  # JSON
    params: str | None
    valid: bool
    flow_id: UUID
```

| Column | Type | Constraints |
|--------|------|-------------|
| build_id | UUID | PRIMARY KEY |
| timestamp | DATETIME | NOT NULL |
| id | VARCHAR | NOT NULL |
| data | JSON | NULLABLE |
| artifacts | JSON | NULLABLE |
| params | TEXT | NULLABLE |
| valid | BOOLEAN | NOT NULL |
| flow_id | UUID | NOT NULL |

---

### PublishRecord

Tracks external publications.

```python
class PublishRecord(SQLModel, table=True):
    __tablename__ = "publish_record"

    id: UUID = Field(primary_key=True)
    flow_id: UUID
    platform: str
    platform_url: str
    external_id: str
    published_at: datetime
    published_by: UUID
    status: PublishStatusEnum  # ACTIVE, UNPUBLISHED, ERROR, PENDING
    metadata_: dict | None  # JSON
    last_sync_at: datetime | None
    error_message: str | None
```

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| flow_id | UUID | FK(flow.id), INDEX |
| platform | VARCHAR | INDEX, NOT NULL |
| platform_url | VARCHAR | NOT NULL |
| external_id | VARCHAR | NOT NULL |
| published_at | DATETIME | NOT NULL |
| published_by | UUID | FK(user.id) |
| status | ENUM | DEFAULT 'ACTIVE' |
| metadata_ | JSON | NULLABLE |
| last_sync_at | DATETIME | NULLABLE |
| error_message | TEXT | NULLABLE |

**Constraints**: UNIQUE(flow_id, platform, platform_url, status)

**Relationships**: `flow`, `user`

---

## Migrations

Migrations are located in:
```
langbuilder/src/backend/base/langbuilder/alembic/versions/
```

Key migrations include:
- `260dbcc8b680_adds_tables.py` - Initial tables
- `012fb73ac359_add_folder_table.py` - Folder support
- `d066bfd22890_add_message_table.py` - Message table
- `90be8e2ed91e_create_transactions_table.py` - Transactions
- `0d60fcbd4e8e_create_vertex_builds_table.py` - Vertex builds
- `2a32c0912c60_add_publish_record_table.py` - Publication tracking
- `66f72f04a1de_add_mcp_support.py` - MCP settings

---

## Enumerations

### AccessTypeEnum
```python
class AccessTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
```

### PublishStatusEnum
```python
class PublishStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    UNPUBLISHED = "UNPUBLISHED"
    ERROR = "ERROR"
    PENDING = "PENDING"
```
