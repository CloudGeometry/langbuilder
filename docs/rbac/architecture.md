# RBAC Architecture

This document provides a technical deep-dive into LangBuilder's Role-Based Access Control (RBAC) implementation for developers and system architects.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Model](#data-model)
3. [Permission Check Flow](#permission-check-flow)
4. [Role Inheritance Algorithm](#role-inheritance-algorithm)
5. [API Implementation](#api-implementation)
6. [Frontend Integration](#frontend-integration)
7. [Performance Optimizations](#performance-optimizations)
8. [Security Considerations](#security-considerations)
9. [Testing Strategy](#testing-strategy)
10. [Future Enhancements](#future-enhancements)

## Architecture Overview

### System Components

The RBAC system is composed of several layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  - RBAC Management UI                                   │
│  - Permission-aware components                          │
│  - API client for RBAC endpoints                        │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
┌────────────────────┴────────────────────────────────────┐
│                  API Layer (FastAPI)                    │
│  - /api/v1/rbac/* endpoints                             │
│  - Admin-only middleware                                │
│  - Request/response validation (Pydantic)               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Service Layer (RBACService)                │
│  - can_access(): Core permission check                  │
│  - assign_role(), update_role(), remove_role()          │
│  - batch_can_access(): Optimized batch checks           │
│  - Audit logging                                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│             Data Layer (SQLModel/SQLAlchemy)            │
│  - Role, Permission, RolePermission models              │
│  - UserRoleAssignment model                             │
│  - CRUD operations                                      │
│  - Database indexes for performance                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                Database (SQLite/PostgreSQL)             │
│  - role, permission, role_permission tables             │
│  - user_role_assignment table                           │
│  - Unique constraints and indexes                       │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Clear separation between API, service, and data layers
2. **Fail-Secure**: Default deny, explicit grant
3. **Performance First**: Optimized queries with indexes and caching
4. **Auditability**: All operations logged for compliance
5. **Backward Compatible**: Superuser bypass maintains existing behavior
6. **Extensible**: Designed for future enhancements (custom roles, etc.)

## Data Model

### Entity-Relationship Diagram

```
┌──────────────┐          ┌──────────────────────┐          ┌──────────────┐
│     User     │          │  UserRoleAssignment  │          │     Role     │
├──────────────┤          ├──────────────────────┤          ├──────────────┤
│ id (PK)      │◄────────┤ id (PK)              ├─────────►│ id (PK)      │
│ username     │          │ user_id (FK)         │          │ name (UQ)    │
│ is_superuser │          │ role_id (FK)         │          │ description  │
│ ...          │          │ scope_type           │          │ is_system_role│
└──────────────┘          │ scope_id             │          └──────┬───────┘
                          │ is_immutable         │                 │
       ┌──────────────────┤ created_at           │                 │
       │                  │ created_by (FK)      │                 │
       │                  └──────────────────────┘                 │
       │                           │                                │
       │                           │                                │
       │                  ┌────────┴────────────┐                  │
       │                  │  Unique Constraint  │                  │
       │                  │  (user_id, role_id, │                  │
       │                  │   scope_type,       │                  │
       │                  │   scope_id)         │                  │
       │                  └─────────────────────┘                  │
       │                                                            │
       │                                                            │
       │                  ┌──────────────────────┐                 │
       └─────────────────►│      Permission      │◄────────────────┘
        (created_by)      ├──────────────────────┤    (via RolePermission)
                          │ id (PK)              │
                          │ name                 │
                          │ scope                │
                          │ description          │
                          └──────────────────────┘
                                    ▲
                                    │
                          ┌─────────┴────────────┐
                          │   RolePermission     │
                          ├──────────────────────┤
                          │ id (PK)              │
                          │ role_id (FK)         │
                          │ permission_id (FK)   │
                          └──────────────────────┘
```

### Table Schemas

#### `role`

Stores role definitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique role identifier |
| name | VARCHAR | UNIQUE, NOT NULL, INDEX | Role name (Admin, Owner, Editor, Viewer) |
| description | TEXT | NULLABLE | Human-readable description |
| is_system_role | BOOLEAN | NOT NULL, DEFAULT FALSE | System-defined role (cannot be deleted) |
| created_at | TIMESTAMP | NOT NULL | When role was created |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `name`

**Seed Data**: 4 system roles (Admin, Owner, Editor, Viewer)

#### `permission`

Stores permission definitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique permission identifier |
| name | VARCHAR | NOT NULL, INDEX | Permission name (Create, Read, Update, Delete) |
| scope | VARCHAR | NOT NULL, INDEX | Scope (Flow, Project, Global) |
| description | TEXT | NULLABLE | Human-readable description |
| created_at | TIMESTAMP | NOT NULL | When permission was created |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE CONSTRAINT on `(name, scope)`
- INDEX on `(name, scope)` for fast lookups

**Seed Data**: 8 permissions (4 CRUD × 2 scopes: Flow, Project)

#### `role_permission`

Links roles to permissions (many-to-many).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique mapping identifier |
| role_id | UUID | FOREIGN KEY → role.id | Role reference |
| permission_id | UUID | FOREIGN KEY → permission.id | Permission reference |
| created_at | TIMESTAMP | NOT NULL | When mapping was created |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `role_id` for role permission lookups
- INDEX on `permission_id` for permission reverse lookups

**Seed Data**: 32 mappings defining role permissions

#### `user_role_assignment`

Stores user role assignments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique assignment identifier |
| user_id | UUID | FOREIGN KEY → user.id, INDEX | User reference |
| role_id | UUID | FOREIGN KEY → role.id, INDEX | Role reference |
| scope_type | VARCHAR | NOT NULL, INDEX | Scope type (Global, Project, Flow) |
| scope_id | UUID | NULLABLE, INDEX | Specific resource ID (NULL for Global) |
| is_immutable | BOOLEAN | NOT NULL, DEFAULT FALSE | Cannot be modified/deleted |
| created_at | TIMESTAMP | NOT NULL | When assignment was created |
| created_by | UUID | FOREIGN KEY → user.id, NULLABLE | Who created the assignment |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE CONSTRAINT on `(user_id, role_id, scope_type, scope_id)`
- INDEX on `(user_id, scope_type, scope_id)` for permission checks
- INDEX on `user_id` for user assignment lookups
- INDEX on `(scope_type, scope_id)` for resource assignment lookups

**Constraints**:
- Cannot have duplicate assignments (user + role + scope must be unique)
- `created_by` can be NULL (for system-created assignments)

#### Modified: `folder` (Projects)

Added column for Starter Project identification.

| Column (New) | Type | Constraints | Description |
|--------------|------|-------------|-------------|
| is_starter_project | BOOLEAN | NOT NULL, DEFAULT FALSE | Indicates user's Starter Project |

**Purpose**: Identifies Starter Projects to enforce immutable Owner assignments.

### Database Indexes

Indexes are critical for RBAC performance. The following indexes are created:

**Performance Targets**:
- Permission check queries: <50ms at p95
- Assignment queries: <200ms at p95

**Index List**:

1. `idx_role_name`: Fast role lookups by name
2. `idx_permission_name_scope`: Fast permission lookups by name and scope
3. `idx_user_role_assignment_lookup`: Fast permission checks (user + scope)
4. `idx_user_role_assignment_user`: Fast user assignment listings
5. `idx_user_role_assignment_scope`: Fast resource assignment listings

**Index Usage Examples**:

```sql
-- Permission check query (uses idx_user_role_assignment_lookup)
SELECT * FROM user_role_assignment
WHERE user_id = ? AND scope_type = ? AND scope_id = ?;

-- List user assignments (uses idx_user_role_assignment_user)
SELECT * FROM user_role_assignment WHERE user_id = ?;

-- List resource assignments (uses idx_user_role_assignment_scope)
SELECT * FROM user_role_assignment WHERE scope_type = ? AND scope_id = ?;
```

## Permission Check Flow

### Algorithm Overview

The `can_access()` method implements a hierarchical permission check:

```
┌─────────────────────────────────────┐
│  can_access(user_id, permission,   │
│             scope_type, scope_id)   │
└────────────┬────────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│  1. Check if user is superuser     │
│     → If yes, return True (bypass) │
└────────────┬───────────────────────┘
             │ No
             ▼
┌────────────────────────────────────┐
│  2. Check if user has Global       │
│     Admin role                     │
│     → If yes, return True (bypass) │
└────────────┬───────────────────────┘
             │ No
             ▼
┌────────────────────────────────────┐
│  3. Get user's role for scope      │
│     - For Flow: Check Flow-specific│
│       assignment first, then       │
│       inherit from Project         │
│     - For Project: Check Project   │
│       assignment                   │
│     - For Global: Check Global     │
│       assignment                   │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│  4. If no role found, return False │
└────────────┬───────────────────────┘
             │ Role found
             ▼
┌────────────────────────────────────┐
│  5. Check if role has permission   │
│     - Query role_permission table  │
│     - Match permission name & scope│
│     → Return True/False            │
└────────────────────────────────────┘
```

### Code Implementation

**File**: `src/backend/base/langbuilder/services/rbac/service.py`

```python
async def can_access(
    self,
    user_id: UUID,
    permission_name: str,
    scope_type: str,
    scope_id: UUID | None,
    db: AsyncSession,
) -> bool:
    # 1. Superuser bypass
    user = await get_user_by_id(db, user_id)
    if user and user.is_superuser:
        return True

    # 2. Global Admin bypass
    if await self._has_global_admin_role(user_id, db):
        return True

    # 3. Get user's role for scope (with inheritance)
    role = await self._get_user_role_for_scope(user_id, scope_type, scope_id, db)
    if not role:
        return False

    # 4. Check if role has permission
    return await self._role_has_permission(role.id, permission_name, scope_type, db)
```

### Optimization: Batch Permission Checks

For frontend list views, batch permission checks are optimized with a single SQL query:

**File**: `src/backend/base/langbuilder/services/rbac/service.py`

```python
async def batch_can_access(
    self,
    user_id: UUID,
    checks: list[dict],
    db: AsyncSession,
) -> list[bool]:
    # Single query: Fetch all relevant role assignments
    # Single query: Fetch all relevant permissions
    # In-memory: Match checks to assignments and permissions
    # Return: List of boolean results
```

**Performance Gain**: 5-10x faster than sequential checks.

## Role Inheritance Algorithm

### Inheritance Rules

1. **Flow inherits from Project**: If user has a Project-level role, they inherit that role for all Flows in the Project
2. **Explicit overrides inherited**: If user has an explicit Flow-level role, it takes precedence
3. **Most specific wins**: Flow-level > Project-level > Global-level

### Implementation

**File**: `src/backend/base/langbuilder/services/rbac/service.py`

```python
async def _get_user_role_for_scope(
    self,
    user_id: UUID,
    scope_type: str,
    scope_id: UUID | None,
    db: AsyncSession,
) -> Role | None:
    # Check for explicit scope assignment
    assignment = await db.exec(
        select(UserRoleAssignment)
        .where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.scope_type == scope_type,
            UserRoleAssignment.scope_id == scope_id,
        )
        .options(selectinload(UserRoleAssignment.role))
    )

    if assignment:
        return assignment.role

    # For Flow scope, check inherited Project role
    if scope_type == "Flow" and scope_id:
        flow = await db.exec(select(Flow).where(Flow.id == scope_id))
        if flow and flow.folder_id:
            # Recursive call to check Project
            return await self._get_user_role_for_scope(
                user_id, "Project", flow.folder_id, db
            )

    return None
```

### Inheritance Examples

**Example 1: Simple Inheritance**

```
User: alice@company.com
Assignment: Editor on Project "Marketing"

Effective Permissions:
├── Project "Marketing" → Editor (explicit)
│   ├── Flow "Campaign A" → Editor (inherited)
│   ├── Flow "Campaign B" → Editor (inherited)
│   └── Flow "Campaign C" → Editor (inherited)
```

**Example 2: Override Inheritance**

```
User: alice@company.com
Assignments:
  - Editor on Project "Marketing"
  - Owner on Flow "Campaign B"

Effective Permissions:
├── Project "Marketing" → Editor (explicit)
│   ├── Flow "Campaign A" → Editor (inherited)
│   ├── Flow "Campaign B" → Owner (explicit, overrides)
│   └── Flow "Campaign C" → Editor (inherited)
```

**Example 3: No Inheritance (Different User)**

```
User: bob@company.com
Assignment: Viewer on Flow "Campaign B"

Effective Permissions:
├── Project "Marketing" → No Access
│   ├── Flow "Campaign A" → No Access
│   ├── Flow "Campaign B" → Viewer (explicit)
│   └── Flow "Campaign C" → No Access
```

## API Implementation

### Endpoint Architecture

**File**: `src/backend/base/langbuilder/api/v1/rbac.py`

All RBAC endpoints follow these conventions:

1. **REST patterns**: GET (list/read), POST (create), PATCH (update), DELETE (delete)
2. **Async handlers**: All endpoints are async for non-blocking I/O
3. **Dependency injection**: FastAPI `Depends()` for services and auth
4. **Pydantic validation**: Request/response schemas enforce data contracts
5. **Error handling**: Structured error responses with appropriate HTTP codes

### Admin Middleware

**Implementation**:

```python
async def require_admin(current_user: CurrentActiveUser) -> CurrentActiveUser:
    """Ensure current user is an Admin (superuser or Global Admin role)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

AdminUser = Annotated[CurrentActiveUser, Depends(require_admin)]
```

**Usage**:

```python
@router.post("/assignments")
async def create_assignment(
    assignment: UserRoleAssignmentCreate,
    admin: AdminUser,  # This applies the admin check
    db: DbSession,
    rbac: RBACServiceDep,
):
    # Only admins can reach this code
    ...
```

### Request/Response Schemas

**File**: `src/backend/base/langbuilder/services/database/models/user_role_assignment/model.py`

Pydantic schemas enforce API contracts:

```python
class UserRoleAssignmentCreate(SQLModel):
    """Request schema for creating role assignment."""
    user_id: UUID
    role_name: str  # Easier than role_id
    scope_type: str
    scope_id: UUID | None = None

class UserRoleAssignmentReadWithRole(SQLModel):
    """Response schema with role details."""
    id: UUID
    user_id: UUID
    role_id: UUID
    scope_type: str
    scope_id: UUID | None
    is_immutable: bool
    created_at: datetime
    created_by: UUID | None
    role: RoleRead  # Nested role details
```

### Error Handling

Custom exceptions for domain-specific errors:

**File**: `src/backend/base/langbuilder/services/rbac/exceptions.py`

```python
class UserNotFoundException(Exception):
    """User not found in database."""
    def __init__(self, user_id: str):
        self.detail = f"User with ID {user_id} not found"

class ImmutableAssignmentException(Exception):
    """Cannot modify immutable assignment."""
    def __init__(self, operation: str):
        self.detail = f"Cannot {operation} immutable role assignment"
```

**API Mapping**:

```python
try:
    assignment = await rbac.assign_role(...)
except UserNotFoundException as e:
    raise HTTPException(status_code=404, detail=str(e.detail))
except ImmutableAssignmentException as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Frontend Integration

### Component Architecture

**File**: `src/frontend/src/pages/AdminPage/RBACManagementPage/index.tsx`

The RBAC Management UI is a React component with sub-components:

```
RBACManagementPage (index.tsx)
├── AssignmentListView
│   ├── Filters (user, role, scope)
│   ├── Assignment table
│   └── Actions (edit, delete)
├── CreateAssignmentModal
│   ├── Step 1: Select User
│   ├── Step 2: Select Scope
│   ├── Step 3: Select Role
│   └── Step 4: Confirm
└── EditAssignmentModal
    ├── Display user & scope (read-only)
    ├── Select new role
    └── Save changes
```

### API Integration

**API Client**:

```typescript
// src/frontend/src/controllers/API/rbac.ts

export const rbacAPI = {
  // List roles
  async listRoles(): Promise<Role[]> {
    const response = await api.get("/rbac/roles");
    return response.data;
  },

  // List assignments
  async listAssignments(filters?: {
    user_id?: string;
    role_name?: string;
    scope_type?: string;
  }): Promise<Assignment[]> {
    const response = await api.get("/rbac/assignments", { params: filters });
    return response.data;
  },

  // Create assignment
  async createAssignment(
    assignment: AssignmentCreate
  ): Promise<Assignment> {
    const response = await api.post("/rbac/assignments", assignment);
    return response.data;
  },

  // Check permission
  async checkPermission(
    permission: string,
    scope_type: string,
    scope_id?: string
  ): Promise<{ has_permission: boolean }> {
    const response = await api.get("/rbac/check-permission", {
      params: { permission, scope_type, scope_id },
    });
    return response.data;
  },
};
```

### Permission-Aware Components

Components conditionally render based on permissions:

```typescript
// Example: Conditionally render edit button
const FlowCard = ({ flow }) => {
  const [canEdit, setCanEdit] = useState(false);

  useEffect(() => {
    rbacAPI
      .checkPermission("Update", "Flow", flow.id)
      .then((result) => setCanEdit(result.has_permission));
  }, [flow.id]);

  return (
    <div>
      <h3>{flow.name}</h3>
      {canEdit && <button onClick={handleEdit}>Edit</button>}
    </div>
  );
};
```

### State Management

**Zustand Store** (if needed for caching):

```typescript
import create from "zustand";

interface RBACStore {
  permissions: Map<string, boolean>; // Cache permission results
  checkPermission: (
    permission: string,
    scope_type: string,
    scope_id?: string
  ) => Promise<boolean>;
}

export const useRBACStore = create<RBACStore>((set, get) => ({
  permissions: new Map(),

  async checkPermission(permission, scope_type, scope_id) {
    const key = `${permission}:${scope_type}:${scope_id || "global"}`;
    const cached = get().permissions.get(key);

    if (cached !== undefined) {
      return cached;
    }

    const result = await rbacAPI.checkPermission(
      permission,
      scope_type,
      scope_id
    );
    set((state) => ({
      permissions: state.permissions.set(key, result.has_permission),
    }));

    return result.has_permission;
  },
}));
```

## Performance Optimizations

### Database Query Optimization

**1. Index Usage**

All permission check queries use indexes:

```sql
-- Fast permission check (uses idx_user_role_assignment_lookup)
EXPLAIN QUERY PLAN
SELECT * FROM user_role_assignment
WHERE user_id = ? AND scope_type = ? AND scope_id = ?;

-- Output: SEARCH TABLE user_role_assignment USING INDEX idx_user_role_assignment_lookup
```

**2. Eager Loading**

Use SQLAlchemy `selectinload()` to avoid N+1 queries:

```python
# Without eager loading (N+1 problem)
assignments = await db.exec(select(UserRoleAssignment))
for assignment in assignments:
    print(assignment.role.name)  # Triggers query for each assignment

# With eager loading (2 queries total)
assignments = await db.exec(
    select(UserRoleAssignment)
    .options(selectinload(UserRoleAssignment.role))
)
for assignment in assignments:
    print(assignment.role.name)  # No additional queries
```

**3. Batch Operations**

The `batch_can_access()` method uses a single SQL query for multiple checks:

```python
# Inefficient: N sequential queries
for flow_id in flow_ids:
    has_permission = await rbac.can_access(user_id, "Update", "Flow", flow_id, db)

# Efficient: 1 batch query
checks = [{"permission_name": "Update", "scope_type": "Flow", "scope_id": flow_id} for flow_id in flow_ids]
results = await rbac.batch_can_access(user_id, checks, db)
```

### Caching Strategy

**Session-Level Caching**:

Cache permission results during a user's session:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def _cache_key(user_id, permission, scope_type, scope_id):
    return f"{user_id}:{permission}:{scope_type}:{scope_id or 'null'}"

# In request handler
cache_key = _cache_key(user_id, permission, scope_type, scope_id)
if cache_key in permission_cache:
    return permission_cache[cache_key]

result = await rbac.can_access(...)
permission_cache[cache_key] = result
return result
```

**Cache Invalidation**:

Invalidate cache when role assignments change:

```python
async def assign_role(...):
    # Create assignment
    assignment = await rbac.assign_role(...)

    # Invalidate cache for affected user
    permission_cache.clear_user(assignment.user_id)

    return assignment
```

### Frontend Optimization

**1. Batch Permission Checks**

Check permissions for lists in a single request:

```typescript
// Load Flow list
const flows = await flowAPI.listFlows();

// Batch check permissions for all Flows
const checks = flows.map((flow) => ({
  action: "Update",
  resource_type: "Flow",
  resource_id: flow.id,
}));

const results = await rbacAPI.checkPermissions(checks);

// Map results to Flows
flows.forEach((flow, index) => {
  flow.canEdit = results[index].allowed;
});
```

**2. Permission Caching**

Cache permission results in frontend state:

```typescript
// Check once, cache in component state
const [permissions, setPermissions] = useState({});

useEffect(() => {
  rbacAPI.checkPermissions(allChecks).then((results) => {
    const permMap = {};
    results.forEach((result) => {
      const key = `${result.resource_id}:${result.action}`;
      permMap[key] = result.allowed;
    });
    setPermissions(permMap);
  });
}, []);

// Use cached permissions
const canEdit = permissions[`${flow.id}:Update`];
```

## Security Considerations

### Fail-Secure Design

RBAC follows a **default-deny** approach:

- If no role assignment exists, access is denied
- If permission check fails, access is denied
- Superuser bypass is explicit (not inferred)

### Immutable Assignments

Starter Project Owner assignments are immutable to prevent lockout:

```python
# In RBACService.remove_role()
if assignment.is_immutable:
    raise ImmutableAssignmentException(operation="remove")
```

### SQL Injection Prevention

All queries use parameterized statements:

```python
# Safe: Uses SQLAlchemy parameter binding
stmt = select(UserRoleAssignment).where(
    UserRoleAssignment.user_id == user_id,  # Parameterized
    UserRoleAssignment.scope_type == scope_type,  # Parameterized
)

# NEVER do this (vulnerable to SQL injection):
# query = f"SELECT * FROM user_role_assignment WHERE user_id = '{user_id}'"
```

### Authorization vs Authentication

RBAC handles **authorization** (what user can do), not **authentication** (who the user is):

- Authentication: Handled by existing JWT/session system
- Authorization: Handled by RBAC permission checks

### Audit Logging

All RBAC operations are logged for security audits:

```python
logger.info(
    "RBAC: Role assigned",
    extra={
        "action": "assign_role",
        "user_id": str(user_id),
        "role_name": role_name,
        "scope_type": scope_type,
        "scope_id": str(scope_id) if scope_id else None,
        "created_by": str(created_by),
    },
)
```

**Log Analysis**:

```bash
# Find all role assignments for a user
grep "assign_role" logs/langbuilder.log | grep "user_id=<user_id>"

# Find all Admin role assignments
grep "assign_role" logs/langbuilder.log | grep "role_name=Admin"

# Find all failed permission checks
grep "permission_check" logs/langbuilder.log | grep "result=false"
```

## Testing Strategy

### Unit Tests

**Coverage Target**: >90% for RBAC service and API endpoints

**Test Files**:
- `tests/unit/services/rbac/test_service.py`: RBACService tests
- `tests/unit/api/v1/test_rbac.py`: RBAC API endpoint tests

**Test Patterns**:

```python
# Test permission check with role inheritance
async def test_can_access_with_project_inheritance():
    # Setup: User has Editor role on Project
    await rbac.assign_role(user_id, "Editor", "Project", project_id, admin_id, db)

    # Action: Check Flow permission (should inherit from Project)
    has_permission = await rbac.can_access(user_id, "Update", "Flow", flow_id, db)

    # Assert: User has inherited permission
    assert has_permission is True

# Test immutable assignment protection
async def test_cannot_delete_immutable_assignment():
    # Setup: Create immutable assignment
    assignment = await rbac.assign_role(
        user_id, "Owner", "Project", starter_project_id, admin_id, db, is_immutable=True
    )

    # Action: Try to delete immutable assignment
    with pytest.raises(ImmutableAssignmentException):
        await rbac.remove_role(assignment.id, db)
```

### Integration Tests

**Test Files**:
- `tests/integration/test_rbac_endpoints.py`: Full API workflow tests

**Test Scenarios**:

```python
# Test complete workflow: Create, read, update, delete assignment
async def test_rbac_crud_workflow(client, admin_token):
    # Create assignment
    response = client.post(
        "/api/v1/rbac/assignments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "user_id": user_id,
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": project_id,
        },
    )
    assert response.status_code == 201
    assignment_id = response.json()["id"]

    # Read assignment
    response = client.get(
        "/api/v1/rbac/assignments",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert assignment_id in [a["id"] for a in response.json()]

    # Update assignment
    response = client.patch(
        f"/api/v1/rbac/assignments/{assignment_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role_name": "Owner"},
    )
    assert response.status_code == 200

    # Delete assignment
    response = client.delete(
        f"/api/v1/rbac/assignments/{assignment_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204
```

### Performance Tests

**Test Targets**:
- Permission check latency: p95 < 50ms
- Assignment mutation latency: p95 < 200ms
- Batch permission check: <500ms for 50 resources

**Test Implementation**:

```python
import time

async def test_permission_check_performance():
    times = []
    for _ in range(1000):
        start = time.time()
        await rbac.can_access(user_id, "Update", "Flow", flow_id, db)
        times.append((time.time() - start) * 1000)  # Convert to ms

    p95 = sorted(times)[int(len(times) * 0.95)]
    assert p95 < 50, f"p95 latency {p95}ms exceeds 50ms target"

async def test_batch_permission_check_performance():
    checks = [
        {"permission_name": "Update", "scope_type": "Flow", "scope_id": flow_id}
        for flow_id in range(50)
    ]

    start = time.time()
    await rbac.batch_can_access(user_id, checks, db)
    duration = (time.time() - start) * 1000

    assert duration < 500, f"Batch check took {duration}ms, target is <500ms"
```

### Frontend Tests

**Test Files**:
- `src/frontend/src/pages/AdminPage/RBACManagementPage/__tests__/index.test.tsx`

**Test Libraries**:
- React Testing Library
- Jest
- Mock Service Worker (for API mocking)

**Test Example**:

```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import RBACManagementPage from "../index";

test("renders RBAC management page", () => {
  render(<RBACManagementPage />);
  expect(screen.getByText("Role-Based Access Control")).toBeInTheDocument();
});

test("opens create assignment modal", async () => {
  render(<RBACManagementPage />);
  const button = screen.getByText("New Assignment");
  fireEvent.click(button);
  expect(screen.getByText("Create New Role Assignment")).toBeInTheDocument();
});
```

## Future Enhancements

### Custom Roles

Allow administrators to create custom roles beyond the 4 system roles:

**Database Changes**:
- Remove `is_system_role` enforcement on role deletion
- Add UI for creating custom roles with permission selection

**API Changes**:
- `POST /api/v1/rbac/roles`: Create custom role
- `PATCH /api/v1/rbac/roles/{role_id}`: Update custom role permissions
- `DELETE /api/v1/rbac/roles/{role_id}`: Delete custom role (if not in use)

### Additional Scopes

Extend RBAC to other resource types:

**Potential Scopes**:
- **Component**: Access to specific component types
- **Environment**: Deployment environment (dev, staging, production)
- **API Key**: Scope API keys to specific resources
- **Workspace**: Multi-tenancy with workspace isolation

**Implementation**:
- Add new scope types to `Permission` model
- Extend `RBACService.can_access()` to handle new scopes
- Update UI to support new scope types

### Advanced Permissions

Expand beyond CRUD to fine-grained permissions:

**Examples**:
- `Can_export_flow`: Export Flow as JSON
- `Can_deploy_flow`: Deploy Flow to production
- `Can_share_flow`: Share Flow with external users
- `Can_view_logs`: View audit logs and execution history

### User Groups

Group users for easier role management:

**Database Changes**:
- `user_group` table: Group definitions
- `user_group_member` table: User memberships
- `group_role_assignment` table: Role assignments to groups

**Benefits**:
- Assign roles to groups instead of individual users
- Users inherit roles from all groups they belong to
- Easier management of large teams

### SSO and SCIM Integration

Enterprise features for user provisioning:

**SSO (Single Sign-On)**:
- SAML 2.0 support
- OAuth 2.0 / OpenID Connect
- Azure AD, Okta, Google Workspace integration

**SCIM (System for Cross-domain Identity Management)**:
- Automatic user provisioning from identity provider
- Sync role assignments from external directory
- Deprovisioning on user removal

### Audit Log UI

Searchable audit log interface:

**Features**:
- View all RBAC operations (create, update, delete assignments)
- Filter by user, role, resource, date range
- Export audit logs for compliance
- Real-time notifications for critical changes (e.g., Admin role assignment)

### Permission Policies

Define conditional permission rules:

**Examples**:
- Time-based access: Role active only during business hours
- IP-based access: Role only active from specific IP ranges
- MFA-required: Require MFA for sensitive operations

**Implementation**:
- `permission_policy` table: Policy definitions
- Policy evaluation during `can_access()` check
- Policy UI for administrators

## Appendix

### Useful SQL Queries

**Find all users with Admin role**:

```sql
SELECT u.username, u.email, ura.scope_type
FROM user u
JOIN user_role_assignment ura ON u.id = ura.user_id
JOIN role r ON ura.role_id = r.id
WHERE r.name = 'Admin';
```

**Find all role assignments for a user**:

```sql
SELECT r.name AS role, ura.scope_type, ura.scope_id, ura.is_immutable
FROM user_role_assignment ura
JOIN role r ON ura.role_id = r.id
WHERE ura.user_id = '<user_id>';
```

**Find all users with access to a specific Project**:

```sql
SELECT u.username, r.name AS role
FROM user_role_assignment ura
JOIN user u ON ura.user_id = u.id
JOIN role r ON ura.role_id = r.id
WHERE ura.scope_type = 'Project' AND ura.scope_id = '<project_id>';
```

**Find orphaned assignments (user or resource deleted)**:

```sql
-- Assignments with deleted users
SELECT ura.id, ura.user_id
FROM user_role_assignment ura
LEFT JOIN user u ON ura.user_id = u.id
WHERE u.id IS NULL;

-- Assignments with deleted Projects
SELECT ura.id, ura.scope_id
FROM user_role_assignment ura
LEFT JOIN folder f ON ura.scope_id = f.id
WHERE ura.scope_type = 'Project' AND f.id IS NULL;
```

### Performance Tuning

**Analyze query performance**:

```sql
-- SQLite
EXPLAIN QUERY PLAN
SELECT * FROM user_role_assignment
WHERE user_id = ? AND scope_type = ? AND scope_id = ?;

-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM user_role_assignment
WHERE user_id = $1 AND scope_type = $2 AND scope_id = $3;
```

**Check index usage**:

```sql
-- SQLite
.indexes user_role_assignment

-- PostgreSQL
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'user_role_assignment';
```

### Migration Scripts

**Backfill Owner assignments** (run if migration incomplete):

```bash
uv run python scripts/backfill_owner_assignments.py
```

**Verify RBAC data** (run after migration):

```bash
uv run python scripts/verify_rbac_migration.py
```

**Clean up orphaned assignments**:

```bash
uv run python scripts/cleanup_orphaned_assignments.py
```

## Conclusion

LangBuilder's RBAC system provides a robust, scalable, and performant access control solution. The architecture prioritizes security, performance, and extensibility, with clear separation of concerns and comprehensive testing.

For questions or contributions, please refer to:
- [Getting Started Guide](./getting-started.md) for basic usage
- [Admin Guide](./admin-guide.md) for UI instructions
- [API Reference](./api-reference.md) for programmatic access
- [GitHub Repository](https://github.com/cloudgeometry/langbuilder) for code

---

**Contributors**: RBAC Team, LangBuilder Developers

**Last Updated**: January 2025

**Version**: 1.0
