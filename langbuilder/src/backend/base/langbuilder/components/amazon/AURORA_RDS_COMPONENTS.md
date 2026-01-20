# Aurora RDS Components - Engineering Documentation

## Overview

The Aurora RDS components provide relational database capabilities for LangBuilder flows. These components enable storing and retrieving structured data from AWS Aurora (PostgreSQL or MySQL compatible).

**AuroraRDSStoreComponent** is a **hybrid component** that works both as:
1. **Deterministic flow component** - Connect inputs/outputs via edges
2. **Agent tool** - LLM agents can invoke it dynamically

**AuroraRDSRetrieveComponent** is a **flow-only component** for data retrieval.

## Source Files

| Component | File | Class Name |
|-----------|------|------------|
| Aurora RDS Store | `aurora_rds_store.py` | `AuroraRDSStoreComponent` |
| Aurora RDS Retrieve | `aurora_rds_retrieve.py` | `AuroraRDSRetrieveComponent` |
| Registration | `__init__.py` | N/A |

**Location:** `langbuilder/src/backend/base/langbuilder/components/amazon/`

---

## Architecture

### Base Classes

| Component | Base Class | Agent Tool Support |
|-----------|------------|-------------------|
| AuroraRDSStore | `LCToolComponent` | Yes |
| AuroraRDSRetrieve | `Component` | No |

```python
# Store - supports Agent tool usage
from langbuilder.base.langchain_utilities.model import LCToolComponent

class AuroraRDSStoreComponent(LCToolComponent):
    ...

# Retrieve - flow component only
from langbuilder.custom.custom_component.component import Component

class AuroraRDSRetrieveComponent(Component):
    ...
```

### Dual Output Pattern (Store Only)

`AuroraRDSStoreComponent` inherits default outputs from `LCToolComponent`:

| Output Name | Display Name | Type | Use Case |
|-------------|--------------|------|----------|
| `api_run_model` | Data | `["Data"]` | Deterministic flow connections |
| `api_build_tool` | Tool | `["Tool"]` | Agent tool connections |

### Component Registration

Components are registered in `__init__.py` via lazy imports:

```python
_dynamic_imports = {
    "AuroraRDSRetrieveComponent": "aurora_rds_retrieve",
    "AuroraRDSStoreComponent": "aurora_rds_store",
    # ... other amazon components
}

__all__ = [
    "AuroraRDSRetrieveComponent",
    "AuroraRDSStoreComponent",
    # ... other amazon components
]
```

---

## AuroraRDSStoreComponent

### Purpose

Stores structured data to AWS Aurora RDS (PostgreSQL or MySQL compatible) for persistence, analytics, and session management.

### Class Definition

```python
class AuroraRDSStoreComponent(LCToolComponent):
    display_name = "Aurora RDS Store"
    description = "Store data to AWS Aurora RDS (MySQL/PostgreSQL). Accepts Data from upstream components for flexible storage."
    documentation = "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html"
    icon = "Amazon"
    name = "AuroraRDSStore"
```

### Inputs

| Input | Type | Required | Default | tool_mode | Purpose |
|-------|------|----------|---------|-----------|---------|
| `structured_data` | DataInput | **Yes** | - | **True** | Data to store (from upstream component) |
| `record_id` | MessageTextInput | No | - | **True** | Primary key (auto-generates UUID if empty) |
| `db_engine` | DropdownInput | Yes | `"postgresql"` | No | Database engine type |
| `host` | StrInput | **Yes** | - | No | Aurora cluster endpoint |
| `port` | IntInput | Yes | `5432` | No | Database port |
| `database` | StrInput | **Yes** | - | No | Database name |
| `table_name` | StrInput | Yes | `"langbuilder_records"` | No | Target table |
| `username` | SecretStrInput | No | - | No | Database username |
| `password` | SecretStrInput | No | - | No | Database password |
| `secret_arn` | StrInput | No | - | No | AWS Secrets Manager ARN (advanced) |
| `region_name` | DropdownInput | No | `"us-east-1"` | No | AWS region (advanced) |
| `use_ssl` | BoolInput | No | `True` | No | Enable SSL/TLS (advanced) |
| `storage_mode` | DropdownInput | No | `"json_column"` | No | How to store data (advanced) |
| `upsert` | BoolInput | No | `True` | No | Update if exists (advanced) |
| `auto_create_table` | BoolInput | No | `True` | No | Auto-create table (advanced) |

### Storage Modes

| Mode | Description | Table Schema |
|------|-------------|--------------|
| `json_column` | All data stored as JSON in single column | `id VARCHAR(255), data JSONB, created_at, updated_at` |
| `dynamic_columns` | Creates columns per data field | `id VARCHAR(255), <field1>, <field2>, ..., created_at, updated_at` |

### Output Structure

Returns `Data` object:

```python
# Success
{
    "stored": True,
    "id": "generated-uuid",
    "table": "langbuilder_records",
    "fields": ["field1", "field2"],
    "timestamp": "2026-01-20T12:00:00",
    "error": None
}

# Failure
{
    "stored": False,
    "id": "provided-or-generated-id",
    "error": "Error message"
}
```

### Key Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `run_model` | `() -> Data` | Main execution - stores data to Aurora |
| `build_tool` | `() -> Tool` | Creates `StructuredTool` for Agent use |
| `_get_tools` | `async () -> list[Tool]` | **CRITICAL** - Returns properly named tool |
| `_get_credentials` | `() -> dict` | Gets credentials (Secrets Manager or direct) |
| `_get_connection` | `() -> Connection` | Creates database connection |
| `_ensure_table_exists` | `(conn) -> None` | Creates table if missing |
| `_add_column_if_not_exists` | `(conn, col, value) -> None` | Adds columns dynamically |

### Agent Tool Schema

When used as an Agent tool (`aurora_rds_store`):

```python
class StoreDataInput(BaseModel):
    data_json: str = Field(
        default="{}",
        description="JSON string of data to store"
    )
    record_id: str = Field(
        default="",
        description="Optional record ID. Leave empty to auto-generate UUID."
    )
```

---

## AuroraRDSRetrieveComponent

### Purpose

Retrieves data from AWS Aurora RDS by record ID or custom SQL query.

### Class Definition

```python
class AuroraRDSRetrieveComponent(Component):
    display_name = "Aurora RDS Retrieve"
    description = "Retrieve data from AWS Aurora RDS (MySQL/PostgreSQL) by ID or custom query."
    documentation = "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html"
    icon = "Amazon"
    name = "AuroraRDSRetrieve"
```

### Inputs

| Input | Type | Required | Default | tool_mode | Purpose |
|-------|------|----------|---------|-----------|---------|
| `query_mode` | DropdownInput | Yes | `"by_id"` | No | Query type: `by_id` or `custom_sql` |
| `record_id` | MessageTextInput | No | - | **True** | Primary key to retrieve |
| `custom_sql` | StrInput | No | - | No | Custom SELECT query |
| `sql_params` | StrInput | No | `"[]"` | No | JSON array of SQL parameters |
| `db_engine` | DropdownInput | Yes | `"postgresql"` | No | Database engine type |
| `host` | StrInput | **Yes** | - | No | Aurora cluster endpoint |
| `port` | IntInput | Yes | `5432` | No | Database port |
| `database` | StrInput | **Yes** | - | No | Database name |
| `table_name` | StrInput | Yes | `"langbuilder_records"` | No | Target table (for `by_id` mode) |
| `username` | SecretStrInput | No | - | No | Database username |
| `password` | SecretStrInput | No | - | No | Database password |
| `secret_arn` | StrInput | No | - | No | AWS Secrets Manager ARN (advanced) |
| `region_name` | DropdownInput | No | `"us-east-1"` | No | AWS region (advanced) |
| `use_ssl` | BoolInput | No | `True` | No | Enable SSL/TLS (advanced) |
| `limit` | IntInput | No | `100` | No | Max records to return (advanced) |

### Query Modes

| Mode | Use Case | Required Inputs |
|------|----------|-----------------|
| `by_id` | Fetch single record by primary key | `record_id`, `table_name` |
| `custom_sql` | Execute custom SELECT query | `custom_sql`, optional `sql_params` |

### Output Structure

Returns `Data` object:

```python
# Success
{
    "found": True,
    "records": [
        {"id": "...", "data": {...}, "created_at": "...", "updated_at": "..."},
        ...
    ],
    "count": 5,
    "table": "langbuilder_records",
    "error": None
}

# Not found / Error
{
    "found": False,
    "records": [],
    "count": 0,
    "error": "No record ID provided"  # or None
}
```

### Custom SQL Example

```python
# Input configuration
custom_sql = "SELECT * FROM users WHERE status = %s AND created_at > %s"
sql_params = '["active", "2026-01-01"]'

# Executes:
cursor.execute(
    "SELECT * FROM users WHERE status = %s AND created_at > %s",
    ["active", "2026-01-01"]
)
```

---

## Authentication Strategy

Both components support multiple authentication methods:

### Priority Order

```
1. AWS Secrets Manager (if secret_arn provided)
   ↓ (if not configured)
2. Direct Credentials (username/password inputs)
```

### AWS Secrets Manager

```python
# Set secret_arn to retrieve credentials automatically
secret_arn = "arn:aws:secretsmanager:us-east-1:123456789:secret:mydb-credentials"

# Expected secret JSON format:
{
    "username": "dbuser",
    "password": "dbpassword"
}
```

### SecretStr Handling

Credentials properly extract values from Pydantic `SecretStr`:

```python
username = self.username
if hasattr(username, "get_secret_value"):
    username = username.get_secret_value()
```

**Note:** Unlike some components, Aurora RDS components do NOT have default values in `SecretStrInput` fields (following best practices).

---

## Database Engine Support

### PostgreSQL (Default)

```python
db_engine = "postgresql"
port = 5432  # default

# Connection library: psycopg2
# SSL mode: sslmode="require"
# JSON column type: JSONB
```

### MySQL

```python
db_engine = "mysql"
port = 3306  # typical MySQL port

# Connection library: pymysql
# SSL: ssl={"ssl": True}
# JSON column type: JSON
```

### SQL Differences

| Feature | PostgreSQL | MySQL |
|---------|------------|-------|
| Upsert | `ON CONFLICT (id) DO UPDATE` | `ON DUPLICATE KEY UPDATE` |
| Add column | `ADD COLUMN IF NOT EXISTS` | Check `information_schema` first |
| JSON type | `JSONB` | `JSON` |
| Auto-update timestamp | Manual via query | `ON UPDATE CURRENT_TIMESTAMP` |

---

## Critical Implementation Details

### The `_get_tools()` Override (Store Only)

**Without this method, all tools get named "run_model" and Agent tool selection fails.**

```python
async def _get_tools(self):
    """Override to return the named tool from build_tool() instead of generic outputs."""
    tool = self.build_tool()
    if tool and not tool.tags:
        tool.tags = [tool.name]
    return [tool] if tool else []
```

### Tool Tags Requirement

Tools must have `tags` for proper Agent selection:

```python
tool = StructuredTool.from_function(
    name="aurora_rds_store",
    description="Store data to AWS Aurora RDS database...",
    args_schema=StoreDataInput,
    func=_store_data,
    return_direct=False,
    tags=["aurora_rds_store"],  # REQUIRED for Agent tool selection
)
```

### Error Handling Pattern

Both components return `Data` objects with error info instead of raising exceptions:

```python
try:
    conn = self._get_connection()
except Exception as e:
    self.status = f"Connection failed: {e}"
    return Data(data={
        "stored": False,  # or "found": False
        "error": str(e),
        "id": None
    })
```

This allows flows to handle errors gracefully via conditional routing.

---

## Usage Patterns

### Pattern 1: Agent Tool (Store Only)

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  ChatInput  │────▶│    Agent    │────▶│  ChatOutput  │
└─────────────┘     └──────┬──────┘     └──────────────┘
                          │
                    tools │ (api_build_tool)
                          │
                          ▼
                ┌─────────────────┐
                │ Aurora RDS      │
                │ Store           │
                └─────────────────┘
```

- Connect `api_build_tool` output to Agent's `tools` input
- Agent decides when to store data based on conversation
- Dynamic, conversational execution

### Pattern 2: Deterministic Flow (Store)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  ChatInput  │────▶│  LLM Chain   │────▶│ Aurora RDS      │────▶│  ChatOutput  │
└─────────────┘     └──────────────┘     │ Store           │     └──────────────┘
                                         └─────────────────┘
```

- Connect inputs via edges to `api_run_model` output
- Always stores data when flow executes
- Predictable, testable execution

### Pattern 3: Retrieve and Process

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐     ┌──────────────┐
│  TextInput  │────▶│ Aurora RDS      │────▶│  LLM Chain  │────▶│  ChatOutput  │
│  (record_id)│     │ Retrieve        │     │ (process)   │     └──────────────┘
└─────────────┘     └─────────────────┘     └─────────────┘
```

- Retrieve data by ID or query
- Process with LLM or other components
- Output results to user

---

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| N/A | Aurora uses direct connection params | N/A |

**Note:** Unlike DynamoDB which uses AWS SDK credentials, Aurora RDS connects directly to the database endpoint. AWS Secrets Manager is optional for credential management.

---

## Dependencies

```
psycopg2-binary>=2.9.0   # PostgreSQL driver
pymysql>=1.0.0           # MySQL driver
boto3>=1.26.0            # AWS Secrets Manager (optional)
langchain-core           # StructuredTool, BaseModel
pydantic>=2.0            # Field, BaseModel
```

---

## Testing

### Via API

```bash
# Test store
curl -X POST "http://localhost:4101/api/v1/run/{flow_id}" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "Store user data: name=John, email=john@example.com",
    "input_type": "chat",
    "output_type": "chat",
    "stream": false
  }'
```

### Via Playground

1. Open flow in LangBuilder UI
2. Configure components:
   - **Host**: Your Aurora cluster endpoint
   - **Database**: Database name
   - **Table Name**: Target table
   - **Username/Password**: Database credentials
   - **DB Engine**: `postgresql` or `mysql`
3. Click **Playground** button
4. Test operations

### Verified Test Configuration

```python
# PostgreSQL Aurora
DB_ENGINE = "postgresql"
HOST = "mydb.cluster-xxxxx.us-east-1.rds.amazonaws.com"
PORT = 5432
DATABASE = "myappdb"
TABLE_NAME = "langbuilder_records"
USE_SSL = True
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Connection timeout | Security group blocking access | Add inbound rule for port 5432/3306 |
| SSL required error | Aurora requires SSL | Ensure `use_ssl=True` (default) |
| Table not found | Table doesn't exist | Enable `auto_create_table=True` |
| Permission denied | User lacks permissions | Grant INSERT/SELECT/UPDATE on table |
| psycopg2 not found | Missing dependency | `pip install psycopg2-binary` |
| pymysql not found | Missing dependency | `pip install pymysql` |
| Tools named "run_model" | Missing `_get_tools()` override | Ensure async `_get_tools()` method exists |
| Agent doesn't select tool | Missing `tags` in StructuredTool | Add `tags=[tool_name]` |

---

## Comparison with DynamoDB Components

| Feature | Aurora RDS | DynamoDB |
|---------|------------|----------|
| Database type | Relational (SQL) | NoSQL (Key-Value) |
| Query language | SQL | DynamoDB API |
| Schema | Flexible (json_column) or structured (dynamic_columns) | Schema-less |
| Connection | Direct TCP | AWS SDK |
| Authentication | Username/password or Secrets Manager | IAM or access keys |
| Auto-create | Table only | Table + TTL enabled |
| Agent tool | Store only | Store only |
| Retrieve component | `Component` base | `Component` base |

---

## Code Review Checklist

When modifying these components:

- [ ] Store extends `LCToolComponent` base class
- [ ] Retrieve extends `Component` base class
- [ ] `_get_tools()` async method present in Store
- [ ] `tags=[tool_name]` in `StructuredTool.from_function()`
- [ ] `tool_mode=True` on inputs that Agent should pass
- [ ] No default values in `SecretStrInput` fields
- [ ] Error handling returns `Data` with error info (doesn't raise)
- [ ] Components registered in `__init__.py` (`_dynamic_imports` and `__all__`)
- [ ] Both PostgreSQL and MySQL engines tested
- [ ] SSL connections work properly
- [ ] Secrets Manager integration tested

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-20 | Initial creation. Added AuroraRDSStoreComponent and AuroraRDSRetrieveComponent. Store supports Agent tool usage via LCToolComponent. Retrieve is flow-only via Component base. Both support PostgreSQL and MySQL Aurora engines. Fixed cursor-after-close bug in Retrieve. |
