# Service Catalog - LangBuilder

## Overview

LangBuilder consists of multiple services working together to provide a visual AI workflow builder platform.

---

## Backend Services

### 1. LangBuilder API Server

**Type**: FastAPI Application
**Package**: `langbuilder-base`
**Version**: 0.6.5
**Entry Point**: `langbuilder/__main__.py`
**Default Port**: 8002 (configurable via `BACKEND_PORT`)

**Responsibilities**:
- REST API for flow management
- WebSocket for real-time build events
- Authentication (JWT + API keys)
- Database operations
- Flow execution engine
- MCP (Model Context Protocol) server
- OpenAI-compatible API endpoint

**Key Dependencies**:
- FastAPI, Uvicorn, Gunicorn
- SQLModel, Alembic
- LangChain ecosystem
- Pydantic for validation

### 2. Flow Execution Engine

**Type**: Internal Service
**Location**: `langbuilder/graph/`

**Responsibilities**:
- Parse flow definitions (nodes + edges)
- Build and execute individual vertices
- Manage execution state
- Stream results via SSE

---

## Frontend Application

### LangBuilder Web UI

**Type**: React SPA
**Version**: 1.6.5
**Build Tool**: Vite
**Default Port**: 5175 (configurable via `FRONTEND_PORT`)

**Responsibilities**:
- Visual flow canvas (React Flow)
- Component library browser
- Flow management CRUD
- Real-time build monitoring
- Chat interface
- User authentication

**Key Dependencies**:
- React 18.3.1
- @xyflow/react (React Flow)
- Zustand (state management)
- shadcn/ui components
- TailwindCSS
- TypeScript

---

## Integration Services

### 3. OpenWebUI (ActionBridge)

**Type**: Separate Python Application
**Package**: `open-webui`
**Location**: `openwebui/`

**Responsibilities**:
- Chat-based UI alternative
- Model management
- Integration with LangBuilder flows
- External LLM providers

**Key Dependencies**:
- FastAPI, SQLAlchemy, Peewee
- OpenAI, Anthropic, Google GenAI
- ChromaDB, OpenSearch
- Transformers, Sentence-Transformers

---

## Shared Libraries

### 4. langbuilder-base

**Type**: Python Library
**Version**: 0.6.5
**Location**: `langbuilder/src/backend/base/`

**Provides**:
- Core component framework
- Database models and migrations
- API router definitions
- Authentication utilities
- Service abstractions

---

## Component Categories

### LLM Providers (24 integrations)

| Component | Provider | Description |
|-----------|----------|-------------|
| openai | OpenAI | GPT-4, GPT-3.5-turbo |
| anthropic | Anthropic | Claude models |
| google | Google | Gemini, PaLM |
| azure | Microsoft | Azure OpenAI |
| ollama | Ollama | Local LLMs |
| groq | Groq | Fast inference |
| cohere | Cohere | Command models |
| mistral | Mistral AI | Mistral/Mixtral |
| deepseek | DeepSeek | DeepSeek models |
| nvidia | NVIDIA | NIM endpoints |
| amazon | AWS | Bedrock |
| vertexai | GCP | Vertex AI |
| huggingface | HuggingFace | Hub models |
| ibm | IBM | watsonx.ai |

### Vector Stores (20+ integrations)

| Component | Description |
|-----------|-------------|
| ChromaDB | Local/embedded vector DB |
| Pinecone | Managed vector DB |
| Qdrant | Open-source vector DB |
| Milvus | Distributed vector DB |
| PGVector | PostgreSQL extension |
| AstraDB | DataStax Astra DB |
| Elasticsearch | Search + vectors |
| OpenSearch | AWS OpenSearch |
| Redis | In-memory vectors |
| Weaviate | GraphQL vector DB |

### Tools & Utilities (30+ integrations)

| Category | Components |
|----------|------------|
| Search | DuckDuckGo, SerpAPI, Tavily, Exa, Glean |
| Knowledge | Wikipedia, Arxiv, YouTube |
| Enterprise | Jira, Confluence, HubSpot, Salesforce |
| Web Scraping | Firecrawl, ScrapeGraph, Apify |
| Data Processing | Docling, Unstructured |

---

## Service Communication

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│                    Port: 5175 (default)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                      │
│                    Port: 8002 (default)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   REST API   │ │  WebSocket   │ │  MCP Server  │        │
│  │    /api/*    │ │   /build/*   │ │   /mcp/*     │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Flow Execution Engine                    │
├─────────────────────────────────────────────────────────────┤
│                     Database (SQLite/PostgreSQL)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    External Services        │
              │  - LLM APIs (OpenAI, etc.)  │
              │  - Vector DBs               │
              │  - Tool APIs                │
              └─────────────────────────────┘
```

---

## Deployment Options

1. **Local Development**: `start_all.sh` script
2. **Docker**: `docker-compose.dev.yml`
3. **Production**: Gunicorn + Nginx reverse proxy

---

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Backend health check |
| `/api/v1/version` | API version info |
| `/api/v1/config` | Application config |
