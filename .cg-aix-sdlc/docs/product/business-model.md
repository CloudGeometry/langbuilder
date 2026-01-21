# Business Model - LangBuilder

## Overview

This document describes the core domain entities, business rules, and workflows that define how LangBuilder operates as a product.

---

## Core Domain Entities

### 1. User

The person who interacts with LangBuilder, either through the UI or API.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Username | Login identifier |
| Email | Contact email |
| Password | Encrypted credentials |
| Profile Image | User avatar |
| Store API Key | Personal LangBuilder API key |
| Is Active | Account status |
| Is Superuser | Administrative privileges |
| Created At | Account creation timestamp |
| Updated At | Last modification timestamp |

**Business Rules:**
- Each user must have a unique username and email
- Passwords must meet security requirements
- Superusers have administrative access to all resources
- Users own their flows, API keys, and variables

### 2. Flow

The central entity - an AI workflow definition created by users.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier (UUID) |
| Name | Human-readable flow name |
| Description | Flow purpose description |
| Icon | Visual identifier |
| Icon Background | Icon styling |
| Gradient | UI gradient theme |
| Data | JSON flow definition (nodes, edges, etc.) |
| Folder ID | Parent folder (optional) |
| User ID | Owner of the flow |
| Is Component | Whether this is a reusable component |
| Endpoint Name | API endpoint identifier |
| Updated At | Last modification timestamp |

**Business Rules:**
- Flows must belong to exactly one user
- Flow names should be unique within a user's workspace
- Flow data contains the complete graph definition
- Endpoint names must be unique for API exposure
- Flows can optionally be organized into folders

### 3. Folder

Organizational container for flows and projects.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Name | Folder name |
| Description | Folder purpose |
| Parent ID | Parent folder (for nesting) |
| User ID | Owner of the folder |
| Components | Whether folder contains components |

**Business Rules:**
- Folders can be nested (parent-child relationships)
- Folders belong to exactly one user
- Deleting a folder affects contained flows

### 4. API Key

Authentication credentials for programmatic access.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Name | Key name/label |
| API Key | The secret key value (hashed) |
| User ID | Owner of the key |
| Created At | Creation timestamp |
| Last Used At | Last usage timestamp |
| Total Uses | Usage counter |
| Is Active | Key status |

**Business Rules:**
- API keys are unique and securely generated
- Keys are hashed for storage (original shown once)
- Keys can be deactivated without deletion
- Usage is tracked for auditing

### 5. Variable

Encrypted storage for sensitive credentials and configuration.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Name | Variable name |
| Value | Encrypted value |
| Type | Variable type (secret, credential, etc.) |
| User ID | Owner |
| Created At | Creation timestamp |

**Business Rules:**
- Variable values are encrypted at rest
- Variables are scoped to individual users
- Variable names must be unique per user
- Values are never exposed in logs or API responses

### 6. Message

Conversation messages within flow executions.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Flow ID | Associated flow |
| Session ID | Conversation session |
| Sender | Message origin (user/ai) |
| Sender Name | Display name |
| Text | Message content |
| Files | Attached files |
| Timestamp | Message time |

**Business Rules:**
- Messages belong to a specific flow and session
- Message history enables conversation continuity
- Files can be attached to messages

### 7. Transaction

Execution audit trail for flow runs.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Flow ID | Executed flow |
| User ID | Executor |
| Status | Execution status |
| Error | Error details (if failed) |
| Inputs | Execution inputs |
| Outputs | Execution outputs |
| Timestamp | Execution time |

**Business Rules:**
- Every flow execution creates a transaction
- Transactions capture inputs, outputs, and errors
- Transaction history enables debugging and auditing

### 8. Vertex Build

Individual component build results within a flow execution.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Flow ID | Parent flow |
| Vertex ID | Component identifier |
| Build Data | Build artifacts |
| Status | Build status |
| Timestamp | Build time |

**Business Rules:**
- Each component (vertex) in a flow has build state
- Build data includes component outputs
- Build status tracks success/failure per component

### 9. File

User-uploaded files for flow processing.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| User ID | Owner |
| Flow ID | Associated flow (optional) |
| Path | Storage path |
| Filename | Original filename |
| Size | File size |
| Content Type | MIME type |
| Created At | Upload timestamp |

**Business Rules:**
- Files belong to users
- Files can be associated with specific flows
- File cleanup policies may apply

### 10. Publish Record

Tracking for flows published to external platforms.

| Attribute | Description |
|-----------|-------------|
| ID | Unique identifier |
| Flow ID | Published flow |
| Platform | Target platform (OpenWebUI, etc.) |
| External ID | ID on external platform |
| Status | Publication status |
| Published At | Publication timestamp |

**Business Rules:**
- Tracks flow publications to external systems
- Enables unpublishing/updating published flows
- Maintains sync state with external platforms

---

## Entity Relationships

```
User (1) -----> (*) Flow
User (1) -----> (*) Folder
User (1) -----> (*) API Key
User (1) -----> (*) Variable
User (1) -----> (*) File

Folder (1) -----> (*) Flow
Folder (1) -----> (*) Folder (nested)

Flow (1) -----> (*) Message
Flow (1) -----> (*) Transaction
Flow (1) -----> (*) Vertex Build
Flow (1) -----> (*) Publish Record
Flow (1) -----> (*) File
```

---

## Business Rules & Constraints

### Authentication & Authorization

| Rule | Description |
|------|-------------|
| AUTH-001 | Users must authenticate to access the platform |
| AUTH-002 | API keys provide stateless authentication for programmatic access |
| AUTH-003 | Auto-login mode bypasses authentication for single-user deployments |
| AUTH-004 | OAuth providers (Google, Zoho) can be used for social login |
| AUTH-005 | Sessions expire after configurable timeout |

### Flow Management

| Rule | Description |
|------|-------------|
| FLOW-001 | Flows must be validated before execution |
| FLOW-002 | Flow data schema must match expected format |
| FLOW-003 | Circular dependencies in flows are not allowed |
| FLOW-004 | Flows cannot reference non-existent components |
| FLOW-005 | Endpoint names must be URL-safe and unique |

### Execution

| Rule | Description |
|------|-------------|
| EXEC-001 | Flow execution requires valid input parameters |
| EXEC-002 | Execution can be cancelled while in progress |
| EXEC-003 | Streaming responses are delivered via SSE |
| EXEC-004 | Failed component builds halt execution |
| EXEC-005 | Transactions are logged for all executions |

### Security

| Rule | Description |
|------|-------------|
| SEC-001 | API keys are hashed before storage |
| SEC-002 | Variable values are encrypted at rest |
| SEC-003 | Credentials are never logged or exposed in API responses |
| SEC-004 | File uploads are validated for type and size |
| SEC-005 | CORS policies restrict cross-origin access |

### Data Integrity

| Rule | Description |
|------|-------------|
| DATA-001 | Deleting a user cascades to owned resources |
| DATA-002 | Deleting a folder can cascade to contained flows |
| DATA-003 | Foreign key constraints maintain referential integrity |
| DATA-004 | Timestamps are automatically maintained |

---

## Key Workflows

### 1. Flow Creation Workflow

```
1. User opens flow builder
2. User drags components onto canvas
3. User configures component parameters
4. User connects components via edges
5. System validates flow in real-time
6. User saves flow
7. System persists flow data to database
8. Flow is available for execution
```

### 2. Flow Execution Workflow

```
1. User initiates execution (UI or API)
2. System loads flow definition
3. System validates flow structure
4. System builds components in dependency order
5. For each component:
   a. Build component with inputs
   b. Store vertex build result
   c. Pass outputs to connected components
6. Final output returned to user
7. Transaction logged
8. Message history updated (if chat)
```

### 3. API Key Lifecycle

```
1. User requests new API key
2. System generates secure random key
3. System hashes key and stores
4. Original key shown to user once
5. User uses key for API authentication
6. System validates key on each request
7. Usage tracked and logged
8. User can deactivate or delete key
```

### 4. Variable Management Workflow

```
1. User creates variable with name and value
2. System encrypts value before storage
3. Variable name available for flow configuration
4. During execution, system decrypts value
5. Value passed to component (never logged)
6. User can update or delete variable
```

### 5. Publishing Workflow

```
1. User selects flow to publish
2. User chooses target platform (OpenWebUI)
3. System exports flow in target format
4. System calls external platform API
5. External platform registers flow
6. System stores publish record
7. Flow available on external platform
8. User can unpublish to remove
```

---

## Business Metrics

### Usage Metrics

| Metric | Description |
|--------|-------------|
| Active Users | Users who logged in within period |
| Flows Created | Number of new flows |
| Flow Executions | Total execution count |
| API Calls | Programmatic access volume |
| Component Usage | Most-used component types |

### Quality Metrics

| Metric | Description |
|--------|-------------|
| Execution Success Rate | Successful / Total executions |
| Average Execution Time | Mean time to completion |
| Error Rate | Failed executions percentage |
| Build Failures | Component build failure rate |

### Growth Metrics

| Metric | Description |
|--------|-------------|
| User Growth | New user registrations |
| Flow Growth | Cumulative flow count |
| Integration Usage | Adoption of integrations |
| API Adoption | API vs UI usage ratio |

---

*Document generated: 2026-01-21*
*Source: LangBuilder v1.6.5 codebase analysis*
