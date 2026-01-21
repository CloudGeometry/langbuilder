# LangBuilder - API Quick Reference

## Base URLs
- API v1: `/api/v1`
- API v2: `/api/v2`
- OpenAI Compatible: `/v1`
- Health: `/health`

## Authentication

### Login
```http
POST /api/v1/login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass
```

Response sets cookies: `access_token_lf`, `refresh_token_lf`

### Using API Key
```http
GET /api/v1/flows
x-api-key: lb-xxxxxxxx
```

## Core Endpoints

### Flows (CRUD)
```http
# List flows
GET /api/v1/flows
GET /api/v1/flows?folder_id={uuid}&header_flows=true

# Get single flow
GET /api/v1/flows/{flow_id}

# Create flow
POST /api/v1/flows
Content-Type: application/json
{"name": "My Flow", "data": {"nodes": [], "edges": []}}

# Update flow
PATCH /api/v1/flows/{flow_id}
{"name": "Updated Name", "data": {...}}

# Delete flow
DELETE /api/v1/flows/{flow_id}

# Batch operations
POST /api/v1/flows/batch/
POST /api/v1/flows/upload/  (multipart/form-data)
DELETE /api/v1/flows?flow_ids=[uuid1,uuid2]
```

### Build/Chat
```http
# Start build (returns SSE stream)
POST /api/v1/build/{flow_id}/flow
Content-Type: application/json
{"inputs": {"input_value": "Hello"}}

# Stream events
GET /api/v1/build/{flow_id}/events

# Cancel build
POST /api/v1/build/{flow_id}/cancel
```

### Run Endpoint
```http
# Execute flow via endpoint name
POST /api/v1/run/{endpoint_name}
{"input_value": "query", "tweaks": {}}

# Webhook trigger
POST /api/v1/webhook/{flow_id}
```

### Files
```http
# Upload file
POST /api/v1/files/upload/{flow_id}
Content-Type: multipart/form-data

# List files
GET /api/v1/files/{flow_id}

# Download file
GET /api/v1/files/download/{file_id}
```

### Folders
```http
GET /api/v1/folders/
POST /api/v1/folders/
PATCH /api/v1/folders/{folder_id}
DELETE /api/v1/folders/{folder_id}
```

### Users
```http
GET /api/v1/users/whoami
PATCH /api/v1/users/{user_id}
```

### Variables (Credentials)
```http
GET /api/v1/variables/
POST /api/v1/variables/
DELETE /api/v1/variables/{variable_id}
```

## V2 Endpoints

### Files (Enhanced)
```http
GET /api/v2/files/
POST /api/v2/files/
DELETE /api/v2/files/{file_id}
```

### MCP Servers
```http
GET /api/v2/mcp/servers
```

## OpenAI Compatible
```http
# List models
GET /v1/models

# Chat completions (pass flow_id as model)
POST /v1/chat/completions
{
  "model": "{flow_id}",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": true
}
```

## Response Formats

### Success
```json
{"id": "uuid", "name": "Flow Name", ...}
```

### Paginated
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### Error
```json
{
  "detail": "Error message"
}
```

### SSE Stream (Build Events)
```
data: {"event": "vertices_sorted", "data": {...}}
data: {"event": "build_start", "data": {...}}
data: {"event": "end_vertex", "data": {...}}
data: {"event": "end", "data": {...}}
```

## Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Unprocessable Entity
- `500`: Internal Server Error

## Rate Limiting
Not enforced by default. Configure via reverse proxy (Traefik/Nginx).

---
*AI Context Document - CloudGeometry AIx SDLC*
