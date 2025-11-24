# RBAC API Reference

Complete API documentation for LangBuilder's Role-Based Access Control (RBAC) system.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Endpoints](#endpoints)
5. [Error Codes](#error-codes)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

## Overview

The RBAC API provides programmatic access to manage role assignments and check permissions in LangBuilder. All endpoints follow REST conventions and return JSON responses.

### Key Features

- **Role Management**: Create, read, update, and delete role assignments
- **Permission Checks**: Verify user permissions programmatically
- **Batch Operations**: Check multiple permissions in a single request
- **Admin-Only Access**: All management endpoints require Admin privileges
- **Audit Trail**: All operations are logged for compliance

### Who Should Use This API?

- **Infrastructure as Code**: Automate role assignments as part of deployment
- **Custom Admin Tools**: Build custom interfaces for role management
- **Integration Scripts**: Sync LangBuilder permissions with external systems
- **Access Reviews**: Automate periodic access audits

## Authentication

All RBAC API endpoints require authentication using a **Bearer token** or **API key**.

### Using Bearer Token

```bash
# Obtain token via login endpoint
curl -X POST https://your-langbuilder.com/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@company.com",
    "password": "your_password"
  }'

# Response includes access_token
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Use token in subsequent requests
curl -X GET https://your-langbuilder.com/api/v1/rbac/roles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Using API Key

```bash
# Use API key header
curl -X GET https://your-langbuilder.com/api/v1/rbac/roles \
  -H "x-api-key: your_api_key_here"
```

### Admin Access Required

Most RBAC endpoints require **Admin privileges**:
- User must be a **superuser** (is_superuser=True), or
- User must have **Global Admin role** assignment

**Exception**: Permission check endpoints (`/check-permission`, `/check-permissions`) are available to all authenticated users.

## Base URL

All RBAC API endpoints are under:

```
https://your-langbuilder.com/api/v1/rbac
```

Replace `your-langbuilder.com` with your LangBuilder instance domain.

## Endpoints

### List Roles

Get all available roles in the system.

**Endpoint**: `GET /api/v1/rbac/roles`

**Authentication**: Admin required

**Query Parameters**: None

**Response**: `200 OK`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Admin",
    "description": "Global administrator with full access",
    "is_system_role": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Owner",
    "description": "Full control over assigned resources",
    "is_system_role": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Editor",
    "description": "Create, read, and update access",
    "is_system_role": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "name": "Viewer",
    "description": "Read-only access",
    "is_system_role": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

**Example Request**:

```bash
curl -X GET https://your-langbuilder.com/api/v1/rbac/roles \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Use Cases**:
- Populate role dropdowns in custom UIs
- Validate role names before creating assignments
- Display available roles to users

---

### List Assignments

Get all role assignments with optional filtering.

**Endpoint**: `GET /api/v1/rbac/assignments`

**Authentication**: Admin required

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | UUID | No | Filter by user ID |
| role_name | string | No | Filter by role name (Admin, Owner, Editor, Viewer) |
| scope_type | string | No | Filter by scope type (Global, Project, Flow) |

**Response**: `200 OK`

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "role_id": "550e8400-e29b-41d4-a716-446655440001",
    "scope_type": "Project",
    "scope_id": "880e8400-e29b-41d4-a716-446655440000",
    "is_immutable": false,
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": "admin_user_id",
    "role": {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Owner",
      "description": "Full control over assigned resources",
      "is_system_role": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
]
```

**Example Requests**:

```bash
# Get all assignments
curl -X GET https://your-langbuilder.com/api/v1/rbac/assignments \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get assignments for a specific user
curl -X GET "https://your-langbuilder.com/api/v1/rbac/assignments?user_id=770e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all Editor role assignments
curl -X GET "https://your-langbuilder.com/api/v1/rbac/assignments?role_name=Editor" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all Project-level assignments
curl -X GET "https://your-langbuilder.com/api/v1/rbac/assignments?scope_type=Project" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combine filters: Editor assignments on Projects
curl -X GET "https://your-langbuilder.com/api/v1/rbac/assignments?role_name=Editor&scope_type=Project" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Use Cases**:
- Audit user access
- Generate access reports
- Sync with external systems
- Identify orphaned assignments

---

### Create Assignment

Create a new role assignment.

**Endpoint**: `POST /api/v1/rbac/assignments`

**Authentication**: Admin required

**Request Body**:

```json
{
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "role_name": "Owner",
  "scope_type": "Project",
  "scope_id": "880e8400-e29b-41d4-a716-446655440000"
}
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | UUID | Yes | ID of the user to assign the role to |
| role_name | string | Yes | Role name: "Admin", "Owner", "Editor", or "Viewer" |
| scope_type | string | Yes | Scope type: "Global", "Project", or "Flow" |
| scope_id | UUID | Conditional | Required for Project/Flow scopes, null for Global |

**Response**: `201 Created`

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "role_id": "550e8400-e29b-41d4-a716-446655440001",
  "scope_type": "Project",
  "scope_id": "880e8400-e29b-41d4-a716-446655440000",
  "is_immutable": false,
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": "admin_user_id",
  "role": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Owner",
    "description": "Full control over assigned resources",
    "is_system_role": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Example Requests**:

```bash
# Assign Owner role on a Project
curl -X POST https://your-langbuilder.com/api/v1/rbac/assignments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "role_name": "Owner",
    "scope_type": "Project",
    "scope_id": "880e8400-e29b-41d4-a716-446655440000"
  }'

# Assign Editor role on a Flow
curl -X POST https://your-langbuilder.com/api/v1/rbac/assignments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "role_name": "Editor",
    "scope_type": "Flow",
    "scope_id": "990e8400-e29b-41d4-a716-446655440000"
  }'

# Assign Global Admin role
curl -X POST https://your-langbuilder.com/api/v1/rbac/assignments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "role_name": "Admin",
    "scope_type": "Global",
    "scope_id": null
  }'
```

**Validation**:
- User must exist (404 if not found)
- Role must exist (404 if not found)
- Scope resource must exist (404 if Flow/Project not found)
- No duplicate assignment (409 if already exists)
- Global scope must not have scope_id (400 if present)
- Project/Flow scope must have scope_id (400 if missing)

**Error Responses**:

```json
// 404 User Not Found
{
  "detail": "User with ID 770e8400-e29b-41d4-a716-446655440000 not found"
}

// 404 Role Not Found
{
  "detail": "Role 'InvalidRole' not found"
}

// 404 Resource Not Found
{
  "detail": "Flow with ID 990e8400-e29b-41d4-a716-446655440000 not found"
}

// 409 Duplicate Assignment
{
  "detail": "Role assignment already exists for this user, role, and scope"
}

// 400 Invalid Scope
{
  "detail": "Global scope should not have scope_id"
}
```

---

### Update Assignment

Update an existing role assignment (change role only).

**Endpoint**: `PATCH /api/v1/rbac/assignments/{assignment_id}`

**Authentication**: Admin required

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| assignment_id | UUID | ID of the assignment to update |

**Request Body**:

```json
{
  "role_name": "Editor"
}
```

**Response**: `200 OK`

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "role_id": "550e8400-e29b-41d4-a716-446655440002",
  "scope_type": "Project",
  "scope_id": "880e8400-e29b-41d4-a716-446655440000",
  "is_immutable": false,
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": "admin_user_id",
  "role": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Editor",
    "description": "Create, read, and update access",
    "is_system_role": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Example Request**:

```bash
curl -X PATCH https://your-langbuilder.com/api/v1/rbac/assignments/660e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "Editor"
  }'
```

**Validation**:
- Assignment must exist (404 if not found)
- Assignment must not be immutable (400 if immutable)
- New role must exist (404 if not found)

**Error Responses**:

```json
// 404 Assignment Not Found
{
  "detail": "Role assignment with ID 660e8400-e29b-41d4-a716-446655440000 not found"
}

// 400 Immutable Assignment
{
  "detail": "Cannot modify immutable role assignment (e.g., Starter Project Owner)"
}

// 404 Role Not Found
{
  "detail": "Role 'InvalidRole' not found"
}
```

**Note**: Only the role can be changed. To change the user or scope, delete the assignment and create a new one.

---

### Delete Assignment

Delete a role assignment.

**Endpoint**: `DELETE /api/v1/rbac/assignments/{assignment_id}`

**Authentication**: Admin required

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| assignment_id | UUID | ID of the assignment to delete |

**Response**: `204 No Content`

(Empty response body on success)

**Example Request**:

```bash
curl -X DELETE https://your-langbuilder.com/api/v1/rbac/assignments/660e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Validation**:
- Assignment must exist (404 if not found)
- Assignment must not be immutable (400 if immutable)

**Error Responses**:

```json
// 404 Assignment Not Found
{
  "detail": "Role assignment with ID 660e8400-e29b-41d4-a716-446655440000 not found"
}

// 400 Immutable Assignment
{
  "detail": "Cannot remove immutable role assignment (e.g., Starter Project Owner)"
}
```

**Warning**: Deletion is immediate and irreversible. The user will lose access to the resource as soon as the request completes.

---

### Check Permission

Check if the current user has a specific permission.

**Endpoint**: `GET /api/v1/rbac/check-permission`

**Authentication**: Required (any authenticated user)

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| permission | string | Yes | Permission name: "Create", "Read", "Update", "Delete" |
| scope_type | string | Yes | Scope type: "Global", "Project", "Flow" |
| scope_id | UUID | No | Scope ID (required for Project/Flow, omit for Global) |

**Response**: `200 OK`

```json
{
  "has_permission": true
}
```

**Example Requests**:

```bash
# Check if user can update a specific Flow
curl -X GET "https://your-langbuilder.com/api/v1/rbac/check-permission?permission=Update&scope_type=Flow&scope_id=990e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check if user can delete a Project
curl -X GET "https://your-langbuilder.com/api/v1/rbac/check-permission?permission=Delete&scope_type=Project&scope_id=880e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check if user can create globally (new Projects)
curl -X GET "https://your-langbuilder.com/api/v1/rbac/check-permission?permission=Create&scope_type=Global" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Use Cases**:
- Frontend: Show/hide buttons based on permissions
- Backend: Validate permissions before performing actions
- Mobile apps: Enable/disable features based on permissions

**Notes**:
- This endpoint checks permissions for the **authenticated user** (from token)
- Superusers always have permission (returns true)
- Global Admins always have permission (returns true)
- Permission inheritance: Flow permissions inherit from Project

---

### Batch Check Permissions

Check multiple permissions in a single request (optimized).

**Endpoint**: `POST /api/v1/rbac/check-permissions`

**Authentication**: Required (any authenticated user)

**Request Body**:

```json
{
  "checks": [
    {
      "action": "Update",
      "resource_type": "Flow",
      "resource_id": "990e8400-e29b-41d4-a716-446655440000"
    },
    {
      "action": "Delete",
      "resource_type": "Project",
      "resource_id": "880e8400-e29b-41d4-a716-446655440000"
    },
    {
      "action": "Create",
      "resource_type": "Global",
      "resource_id": null
    }
  ]
}
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| checks | array | Yes | Array of permission checks (max 100) |
| checks[].action | string | Yes | Permission name: "Create", "Read", "Update", "Delete" |
| checks[].resource_type | string | Yes | Scope type: "Global", "Project", "Flow" |
| checks[].resource_id | UUID | Conditional | Resource ID (required for Project/Flow, null for Global) |

**Response**: `200 OK`

```json
{
  "results": [
    {
      "action": "Update",
      "resource_type": "Flow",
      "resource_id": "990e8400-e29b-41d4-a716-446655440000",
      "allowed": true
    },
    {
      "action": "Delete",
      "resource_type": "Project",
      "resource_id": "880e8400-e29b-41d4-a716-446655440000",
      "allowed": false
    },
    {
      "action": "Create",
      "resource_type": "Global",
      "resource_id": null,
      "allowed": true
    }
  ]
}
```

**Example Request**:

```bash
curl -X POST https://your-langbuilder.com/api/v1/rbac/check-permissions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "checks": [
      {
        "action": "Update",
        "resource_type": "Flow",
        "resource_id": "990e8400-e29b-41d4-a716-446655440000"
      },
      {
        "action": "Delete",
        "resource_type": "Project",
        "resource_id": "880e8400-e29b-41d4-a716-446655440000"
      }
    ]
  }'
```

**Performance**:
- Optimized for batch operations (single SQL query)
- Target: <100ms for 10 checks, <500ms for 50 checks
- Much faster than sequential individual checks (5-10x improvement)

**Use Cases**:
- Frontend: Check permissions for list of resources at once
- Mobile apps: Pre-fetch permissions for offline caching
- Backend: Validate bulk operations efficiently

**Limits**:
- Maximum 100 permission checks per request
- Exceeding limit returns 400 error

---

## Error Codes

The RBAC API uses standard HTTP status codes and returns error details in JSON format.

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully (empty response) |
| 400 | Bad Request | Invalid request data or validation error |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Admin access required |
| 404 | Not Found | Resource not found (user, role, assignment, etc.) |
| 409 | Conflict | Duplicate resource (e.g., duplicate assignment) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (contact support) |

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Errors

**401 Unauthorized**:
```json
{
  "detail": "Invalid or expired token"
}
```

**Solution**: Refresh your token via the login endpoint.

**403 Forbidden**:
```json
{
  "detail": "Admin access required"
}
```

**Solution**: Ensure your user has Admin privileges (superuser or Global Admin role).

**404 Not Found**:
```json
{
  "detail": "User with ID 770e8400-e29b-41d4-a716-446655440000 not found"
}
```

**Solution**: Verify the resource ID is correct and the resource exists.

**409 Conflict**:
```json
{
  "detail": "Role assignment already exists for this user, role, and scope"
}
```

**Solution**: Check if the assignment already exists. Use PATCH to update instead of POST to create.

**400 Bad Request**:
```json
{
  "detail": "Global scope should not have scope_id"
}
```

**Solution**: Fix the request data according to validation rules.

## Rate Limiting

The RBAC API implements rate limiting to prevent abuse and ensure system stability.

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| All RBAC endpoints | 1000 requests | 1 hour |
| Permission checks | 5000 requests | 1 hour |

### Rate Limit Headers

Responses include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640995200
```

### Exceeding Limits

When rate limit is exceeded:

**Response**: `429 Too Many Requests`

```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds."
}
```

### Best Practices

- Use batch permission checks instead of individual checks
- Cache permission results on the client side
- Implement exponential backoff when receiving 429 responses
- Monitor your rate limit usage via response headers

## Examples

### Example 1: Onboarding Automation

Automatically assign roles to new team members.

```python
import requests

BASE_URL = "https://your-langbuilder.com/api/v1"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def onboard_user(user_id, project_ids):
    """Assign Editor role on multiple Projects for a new user."""
    for project_id in project_ids:
        assignment = {
            "user_id": user_id,
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": project_id
        }
        response = requests.post(
            f"{BASE_URL}/rbac/assignments",
            headers=headers,
            json=assignment
        )
        if response.status_code == 201:
            print(f"✓ Assigned Editor on Project {project_id}")
        else:
            print(f"✗ Failed: {response.json()['detail']}")

# Onboard new developer
onboard_user(
    user_id="770e8400-e29b-41d4-a716-446655440000",
    project_ids=[
        "880e8400-e29b-41d4-a716-446655440001",
        "880e8400-e29b-41d4-a716-446655440002",
        "880e8400-e29b-41d4-a716-446655440003"
    ]
)
```

### Example 2: Access Audit Script

Generate a report of all role assignments.

```python
import requests
import csv

BASE_URL = "https://your-langbuilder.com/api/v1"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def audit_access():
    """Generate CSV report of all role assignments."""
    response = requests.get(
        f"{BASE_URL}/rbac/assignments",
        headers=headers
    )
    assignments = response.json()

    with open("access_audit.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["User ID", "Role", "Scope Type", "Scope ID", "Created At", "Immutable"])

        for assignment in assignments:
            writer.writerow([
                assignment["user_id"],
                assignment["role"]["name"],
                assignment["scope_type"],
                assignment["scope_id"],
                assignment["created_at"],
                assignment["is_immutable"]
            ])

    print(f"✓ Audit report generated: {len(assignments)} assignments")

audit_access()
```

### Example 3: Permission Check Before Action

Check permissions before performing an action.

```javascript
const BASE_URL = "https://your-langbuilder.com/api/v1";
const TOKEN = "your_access_token";

async function deleteFlowIfAllowed(flowId) {
  // Check permission first
  const checkResponse = await fetch(
    `${BASE_URL}/rbac/check-permission?permission=Delete&scope_type=Flow&scope_id=${flowId}`,
    {
      headers: {
        Authorization: `Bearer ${TOKEN}`,
      },
    }
  );

  const { has_permission } = await checkResponse.json();

  if (has_permission) {
    // User has permission, proceed with deletion
    const deleteResponse = await fetch(`${BASE_URL}/flows/${flowId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${TOKEN}`,
      },
    });

    if (deleteResponse.ok) {
      console.log("✓ Flow deleted successfully");
    }
  } else {
    console.log("✗ Permission denied: Cannot delete this Flow");
  }
}

deleteFlowIfAllowed("990e8400-e29b-41d4-a716-446655440000");
```

### Example 4: Batch Permission Check for List

Efficiently check permissions for multiple resources.

```javascript
const BASE_URL = "https://your-langbuilder.com/api/v1";
const TOKEN = "your_access_token";

async function checkFlowPermissions(flowIds) {
  const checks = flowIds.map((flowId) => ({
    action: "Update",
    resource_type: "Flow",
    resource_id: flowId,
  }));

  const response = await fetch(`${BASE_URL}/rbac/check-permissions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ checks }),
  });

  const { results } = await response.json();

  // Map results back to Flow IDs
  const permissions = {};
  results.forEach((result, index) => {
    permissions[flowIds[index]] = result.allowed;
  });

  return permissions;
}

// Check permissions for 50 Flows in a single request
const flowIds = [
  /* ... 50 Flow IDs ... */
];
const permissions = await checkFlowPermissions(flowIds);

// Use permissions to show/hide edit buttons
flowIds.forEach((flowId) => {
  const canEdit = permissions[flowId];
  console.log(`Flow ${flowId}: Can edit = ${canEdit}`);
});
```

### Example 5: Temporary Access Management

Grant temporary access and set a reminder to revoke.

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "https://your-langbuilder.com/api/v1"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def grant_temporary_access(user_id, project_id, role_name, duration_days):
    """Grant temporary access and return assignment ID."""
    assignment = {
        "user_id": user_id,
        "role_name": role_name,
        "scope_type": "Project",
        "scope_id": project_id
    }

    response = requests.post(
        f"{BASE_URL}/rbac/assignments",
        headers=headers,
        json=assignment
    )

    if response.status_code == 201:
        assignment_id = response.json()["id"]
        expiration = datetime.now() + timedelta(days=duration_days)

        print(f"✓ Temporary access granted")
        print(f"  Assignment ID: {assignment_id}")
        print(f"  Expires: {expiration.isoformat()}")
        print(f"  Revoke with: DELETE /rbac/assignments/{assignment_id}")

        return assignment_id
    else:
        print(f"✗ Failed: {response.json()['detail']}")
        return None

# Grant 14-day access to contractor
grant_temporary_access(
    user_id="contractor_user_id",
    project_id="project_id",
    role_name="Editor",
    duration_days=14
)
```

## Next Steps

- **[Admin Guide](./admin-guide.md)**: Learn to use the RBAC Management UI
- **[Architecture](./architecture.md)**: Understand how RBAC works internally
- **[Getting Started](./getting-started.md)**: Basic RBAC concepts and examples

## Support

For API issues or questions:

1. Check the [README](./README.md) for RBAC concepts
2. Review [Error Codes](#error-codes) section
3. Open an issue on [GitHub](https://github.com/cloudgeometry/langbuilder/issues)
4. Contact [support@langbuilder.io](mailto:support@langbuilder.io)
