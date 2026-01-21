# API Surface - LangBuilder

## Overview

LangBuilder exposes a comprehensive REST API via FastAPI with two major versions (v1 and v2). All API routes are prefixed with `/api`.

---

## API Versioning

| Version | Prefix | Status |
|---------|--------|--------|
| v1 | `/api/v1` | Active |
| v2 | `/api/v2` | Active |

---

## Authentication

### Methods
- **JWT Tokens**: Bearer token in Authorization header
- **API Keys**: Via `x-api-key` header or query parameter

### Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/login` | User login, returns JWT |
| POST | `/api/v1/logout` | Invalidate session |
| POST | `/api/v1/refresh` | Refresh JWT token |
| GET | `/api/v1/auto_login` | Auto-login (if enabled) |

---

## V1 API Endpoints

### Flows (`/api/v1/flows`)

Manage AI workflow definitions.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/flows/` | List all flows (paginated) |
| POST | `/api/v1/flows/` | Create a new flow |
| GET | `/api/v1/flows/{flow_id}` | Get flow by ID |
| PATCH | `/api/v1/flows/{flow_id}` | Update flow |
| DELETE | `/api/v1/flows/{flow_id}` | Delete flow |
| DELETE | `/api/v1/flows/` | Delete multiple flows |
| POST | `/api/v1/flows/batch/` | Create multiple flows |
| POST | `/api/v1/flows/upload/` | Upload flows from file |
| POST | `/api/v1/flows/download/` | Download flows as ZIP |
| GET | `/api/v1/flows/basic_examples/` | Get starter examples |
| GET | `/api/v1/flows/public_flow/{flow_id}` | Get public flow |

### Chat/Build (`/api/v1/build`)

Execute flows and stream results.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/build/{flow_id}/flow` | Build entire flow |
| POST | `/api/v1/build/{flow_id}/vertices` | Build specific vertices (deprecated) |
| POST | `/api/v1/build/{flow_id}/vertices/{vertex_id}` | Build single vertex (deprecated) |
| GET | `/api/v1/build/{job_id}/events` | SSE stream for build events |
| POST | `/api/v1/build/{job_id}/cancel` | Cancel build job |
| GET | `/api/v1/build/{flow_id}/flow` | Get flow build results |
| POST | `/api/v1/build_public_tmp/{flow_id}/flow` | Build public flow |

### Users (`/api/v1/users`)

User management.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/` | List users |
| POST | `/api/v1/users/` | Create user |
| GET | `/api/v1/users/{user_id}` | Get user |
| PATCH | `/api/v1/users/{user_id}` | Update user |
| DELETE | `/api/v1/users/{user_id}` | Delete user |

### API Keys (`/api/v1/api_key`)

Manage API keys for programmatic access.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/api_key/` | List API keys |
| POST | `/api/v1/api_key/` | Create API key |
| DELETE | `/api/v1/api_key/{api_key_id}` | Delete API key |
| POST | `/api/v1/api_key/store` | Store external API key |

### Files (`/api/v1/files`)

File upload and management.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/files/upload/{flow_id}` | Upload file for flow |
| GET | `/api/v1/files/download/{flow_id}/{file_name}` | Download file |
| GET | `/api/v1/files/images/{flow_id}/{file_name}` | Get image |
| GET | `/api/v1/files/profile_pictures/{folder}/{file}` | Get profile picture |
| GET | `/api/v1/files/profile_pictures/list` | List profile pictures |
| GET | `/api/v1/files/list/{flow_id}` | List files for flow |
| DELETE | `/api/v1/files/delete/{flow_id}/{file_name}` | Delete file |

### Folders (`/api/v1/folders`)

Folder/project organization.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/folders/` | List folders |
| POST | `/api/v1/folders/` | Create folder |
| GET | `/api/v1/folders/{folder_id}` | Get folder with flows |
| PATCH | `/api/v1/folders/{folder_id}` | Update folder |
| DELETE | `/api/v1/folders/{folder_id}` | Delete folder |
| GET | `/api/v1/folders/download/{folder_id}` | Download folder |
| POST | `/api/v1/folders/upload/` | Upload folder |

### Projects (`/api/v1/projects`)

Project management (similar to folders).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/` | List projects |
| POST | `/api/v1/projects/` | Create project |
| GET | `/api/v1/projects/{project_id}` | Get project |
| PATCH | `/api/v1/projects/{project_id}` | Update project |
| DELETE | `/api/v1/projects/{project_id}` | Delete project |
| GET | `/api/v1/projects/download/{project_id}` | Download project |
| POST | `/api/v1/projects/upload/` | Upload project |

### Variables (`/api/v1/variables`)

Manage encrypted variables/credentials.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/variables/` | List variables |
| POST | `/api/v1/variables/` | Create variable |
| PATCH | `/api/v1/variables/{variable_id}` | Update variable |
| DELETE | `/api/v1/variables/{variable_id}` | Delete variable |

### Monitor (`/api/v1/monitor`)

Monitoring and observability.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/monitor/builds` | List build history |
| DELETE | `/api/v1/monitor/builds` | Clear build history |
| GET | `/api/v1/monitor/messages/sessions` | List message sessions |
| GET | `/api/v1/monitor/messages` | List messages |
| DELETE | `/api/v1/monitor/messages` | Delete messages |
| PUT | `/api/v1/monitor/messages/{message_id}` | Update message |
| PATCH | `/api/v1/monitor/messages/{message_id}` | Partial update |
| DELETE | `/api/v1/monitor/messages/session/{session_id}` | Delete session |
| GET | `/api/v1/monitor/transactions` | List transactions |

### Run Endpoints (`/api/v1/run`)

Execute flows programmatically.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/all` | List all runnable endpoints |
| POST | `/api/v1/run/{flow_id_or_name}` | Run flow |
| POST | `/api/v1/webhook/{flow_id_or_name}` | Webhook trigger |

### Publish (`/api/v1/publish`)

Publish flows to external platforms.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/publish/flows` | List publishable flows |
| POST | `/api/v1/publish/openwebui` | Publish to OpenWebUI |
| DELETE | `/api/v1/publish/openwebui` | Unpublish from OpenWebUI |
| GET | `/api/v1/publish/status/{flow_id}` | Get publish status |

### MCP (`/api/v1/mcp`)

Model Context Protocol endpoints.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/mcp/sse` | SSE stream for MCP |
| POST | `/api/v1/mcp/` | MCP message handler |

### MCP Projects (`/api/v1/mcp/projects`)

MCP server management per project.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/mcp/projects/{project_id}` | Get project MCP config |
| GET | `/api/v1/mcp/projects/{project_id}/sse` | Project MCP SSE |
| POST | `/api/v1/mcp/projects/{project_id}` | MCP message |
| PATCH | `/api/v1/mcp/projects/{project_id}` | Update MCP config |
| POST | `/api/v1/mcp/projects/{project_id}/install` | Install MCP server |
| GET | `/api/v1/mcp/projects/{project_id}/installed` | List installed servers |

### Starter Projects (`/api/v1/starter-projects`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/starter-projects/` | List starter projects |

### Other Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/version` | Get API version |
| GET | `/api/v1/config` | Get app configuration |
| POST | `/api/v1/custom_component` | Process custom component |
| POST | `/api/v1/custom_component/update` | Update custom component |
| POST | `/api/v1/validate` | Validate flow |

---

## V2 API Endpoints

### Files (`/api/v2/files`)

Enhanced file management.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v2/files/` | List files |
| POST | `/api/v2/files/` | Upload file |
| GET | `/api/v2/files/{file_id}` | Get file |
| PUT | `/api/v2/files/{file_id}` | Update file |
| DELETE | `/api/v2/files/{file_id}` | Delete file |
| DELETE | `/api/v2/files/batch/` | Batch delete |
| POST | `/api/v2/files/batch/` | Batch operations |

### MCP (`/api/v2/mcp`)

MCP server management.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v2/mcp/servers` | List MCP servers |
| GET | `/api/v2/mcp/servers/{server_name}` | Get server details |
| POST | `/api/v2/mcp/servers/{server_name}` | Add MCP server |
| PATCH | `/api/v2/mcp/servers/{server_name}` | Update server |
| DELETE | `/api/v2/mcp/servers/{server_name}` | Remove server |

---

## OpenAI-Compatible API

For compatibility with OpenAI clients.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/models` | List available models |
| POST | `/v1/chat/completions` | Chat completions |

---

## Health & Utility

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

---

## Request/Response Patterns

### Standard Response

```json
{
  "id": "uuid",
  "name": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  ...
}
```

### Paginated Response

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 50,
  "pages": 2
}
```

### Error Response

```json
{
  "detail": "Error message"
}
```

### SSE Event Stream

```
event: vertex_build
data: {"vertex_id": "...", "status": "...", "result": {...}}

event: end
data: {"status": "completed"}
```
