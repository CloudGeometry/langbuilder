# Technology Stack - LangBuilder

## Overview

LangBuilder is built with a modern Python/TypeScript stack, leveraging FastAPI for the backend and React for the frontend.

---

## Languages

| Language | Version | Usage |
|----------|---------|-------|
| Python | >=3.10, <3.14 | Backend, API, ML/AI |
| TypeScript | ^5.4.5 | Frontend |
| SQL | N/A | Database queries |

---

## Backend Technologies

### Web Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | >=0.115.2 | REST API framework |
| Uvicorn | >=0.30.0 | ASGI server |
| Gunicorn | >=22.0.0 | Production WSGI server |
| Starlette | (via FastAPI) | ASGI toolkit |

### Database & ORM

| Technology | Version | Purpose |
|------------|---------|---------|
| SQLModel | 0.0.22 | ORM (SQLAlchemy + Pydantic) |
| SQLAlchemy | >=2.0.38 | SQL toolkit |
| Alembic | >=1.13.0 | Database migrations |
| aiosqlite | 0.21.0 | Async SQLite support |
| PostgreSQL | (optional) | Production database |

### Authentication & Security

| Technology | Version | Purpose |
|------------|---------|---------|
| python-jose | >=3.3.0 | JWT tokens |
| passlib | >=1.7.4 | Password hashing |
| bcrypt | 4.0.1 | Password encryption |
| cryptography | >=43.0.1 | Encryption utilities |

### AI/ML Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| LangChain | 0.3.23 | LLM orchestration |
| langchain-core | ~0.3.45 | Core abstractions |
| langchain-community | ~0.3.20 | Community integrations |
| langchain-experimental | >=0.3.4 | Experimental features |
| OpenAI | >=1.68.2 | OpenAI API client |
| Anthropic | (via langchain) | Claude API |
| litellm | >=1.60.2 | Universal LLM interface |

### Vector Stores

| Technology | Version | Purpose |
|------------|---------|---------|
| ChromaDB | >=1.0.0 | Local vector database |
| Pinecone | (via langchain) | Managed vector DB |
| Qdrant | 1.9.2 | Vector search |
| Milvus | (via langchain) | Distributed vectors |
| PGVector | 0.3.6 | PostgreSQL vectors |
| FAISS | 1.9.0 | Facebook AI vectors |

### Data Processing

| Technology | Version | Purpose |
|------------|---------|---------|
| Pydantic | ~2.10.1 | Data validation |
| pandas | 2.2.3 | Data analysis |
| orjson | 3.10.15 | Fast JSON parsing |
| duckdb | >=1.0.0 | In-process SQL |

### Observability

| Technology | Version | Purpose |
|------------|---------|---------|
| Loguru | >=0.7.1 | Logging |
| structlog | >=25.4.0 | Structured logging |
| Sentry SDK | >=2.5.1 | Error tracking |
| OpenTelemetry | >=1.25.0 | Distributed tracing |
| Prometheus | (via otel) | Metrics |
| langfuse | 2.53.9 | LLM observability |

### MCP (Model Context Protocol)

| Technology | Version | Purpose |
|------------|---------|---------|
| mcp | >=1.10.1 | MCP server/client |

---

## Frontend Technologies

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| React | ^18.3.1 | UI framework |
| React DOM | ^18.3.1 | DOM rendering |
| TypeScript | ^5.4.5 | Type safety |

### Build Tools

| Technology | Version | Purpose |
|------------|---------|---------|
| Vite | ^5.4.19 | Build tool / dev server |
| SWC | ^1.6.1 | TypeScript compiler |
| PostCSS | ^8.4.38 | CSS processing |
| Autoprefixer | ^10.4.19 | CSS vendor prefixes |

### UI Components

| Technology | Version | Purpose |
|------------|---------|---------|
| shadcn/ui | ^0.9.4 | Component library |
| Radix UI | Various | Accessible primitives |
| TailwindCSS | ^3.4.4 | Utility-first CSS |
| Lucide React | ^0.503.0 | Icons |
| Framer Motion | ^11.2.10 | Animations |

### State Management

| Technology | Version | Purpose |
|------------|---------|---------|
| Zustand | ^4.5.2 | State management |
| TanStack Query | ^5.49.2 | Server state |
| React Hook Form | ^7.52.0 | Form state |

### Flow Canvas

| Technology | Version | Purpose |
|------------|---------|---------|
| @xyflow/react | ^12.3.6 | Visual flow builder |
| ReactFlow | ^11.11.3 | Legacy flow support |
| elkjs | ^0.9.3 | Graph layout |

### Data Display

| Technology | Version | Purpose |
|------------|---------|---------|
| AG Grid | ^32.0.2 | Data tables |
| React Markdown | ^8.0.7 | Markdown rendering |
| React Syntax Highlighter | ^15.6.1 | Code highlighting |
| vanilla-jsoneditor | ^2.3.3 | JSON editing |

### HTTP Client

| Technology | Version | Purpose |
|------------|---------|---------|
| Axios | ^1.7.4 | HTTP requests |

### Testing

| Technology | Version | Purpose |
|------------|---------|---------|
| Jest | ^30.0.3 | Test runner |
| Testing Library | ^16.0.0 | Component testing |
| Playwright | ^1.52.0 | E2E testing |

---

## Infrastructure

### Containerization

| Technology | Purpose |
|------------|---------|
| Docker | Container runtime |
| Docker Compose | Multi-container orchestration |

### External Services (Integrations)

| Category | Services |
|----------|----------|
| LLM Providers | OpenAI, Anthropic, Google, Azure, AWS Bedrock, Groq, Ollama |
| Vector DBs | Pinecone, Qdrant, Milvus, Weaviate, Chroma |
| Search | DuckDuckGo, SerpAPI, Tavily, Exa |
| Enterprise | Jira, Confluence, Salesforce, HubSpot, ServiceNow |
| Storage | AWS S3 (via boto3), Google Cloud Storage |
| Auth | Google OAuth, Zoho OAuth |

---

## Development Tools

### Code Quality

| Tool | Version | Purpose |
|------|---------|---------|
| Ruff | >=0.12.7 | Python linting/formatting |
| Biome | 2.1.1 | JS/TS linting/formatting |
| MyPy | >=1.11.0 | Python type checking |
| pre-commit | >=3.7.0 | Git hooks |

### Testing (Python)

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | >=8.2.0 | Test framework |
| pytest-asyncio | >=0.23.0 | Async test support |
| pytest-cov | >=5.0.0 | Coverage reporting |
| pytest-xdist | >=3.6.0 | Parallel testing |
| httpx | >=0.28.1 | HTTP test client |

### Package Management

| Tool | Purpose |
|------|---------|
| uv | Python package manager (monorepo) |
| npm | Frontend dependencies |

---

## Version Summary

```
Backend:
  Python: 3.10-3.13
  FastAPI: 0.115.2+
  SQLModel: 0.0.22
  LangChain: 0.3.23
  Pydantic: 2.10.1

Frontend:
  Node.js: (implied by npm)
  React: 18.3.1
  TypeScript: 5.4.5
  Vite: 5.4.19
```
