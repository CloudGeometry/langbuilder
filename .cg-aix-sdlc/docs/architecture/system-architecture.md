# System Architecture - LangBuilder

## Overview

LangBuilder is an AI workflow builder that enables developers to create, deploy, and manage LangChain-based AI workflows through a visual drag-and-drop interface. This document provides a high-level overview of the system architecture, key decisions, and technology choices.

## System Purpose and Goals

### Primary Goals

1. **Visual Workflow Design**: Enable non-code workflow creation through an intuitive canvas interface
2. **LLM Provider Agnostic**: Support multiple LLM providers with consistent interfaces
3. **Extensibility**: Allow custom components and integrations
4. **Production Ready**: Provide deployment options from development to production
5. **Developer Experience**: Offer both visual and API-based workflow management

### Target Users

| User Type | Primary Use Case |
|-----------|------------------|
| **AI Engineers** | Building complex AI pipelines |
| **Developers** | Integrating AI into applications |
| **Data Scientists** | Prototyping ML workflows |
| **Business Users** | Creating chatbots and automation |

## Architectural Overview

```
                                   ┌─────────────────────────────────────────┐
                                   │            External Systems              │
                                   │  ┌─────────┐ ┌─────────┐ ┌───────────┐  │
                                   │  │   LLM   │ │ Vector  │ │Enterprise │  │
                                   │  │Providers│ │ Stores  │ │   Tools   │  │
                                   │  └────┬────┘ └────┬────┘ └─────┬─────┘  │
                                   └───────│──────────│────────────│────────┘
                                           │          │            │
                    ┌──────────────────────│──────────│────────────│──────────┐
                    │                      │    LangBuilder System │          │
                    │                      v          v            v          │
┌─────────┐         │  ┌─────────────────────────────────────────────────┐   │
│  Users  │◄────────┼─►│                  Backend API                     │   │
│(Browser)│  HTTPS  │  │              (FastAPI + LangChain)               │   │
└─────────┘         │  │                                                  │   │
     │              │  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │   │
     │              │  │  │   API    │  │  Graph   │  │  Component   │   │   │
     │              │  │  │ Routers  │──│  Engine  │──│  Registry    │   │   │
     │              │  │  └──────────┘  └──────────┘  └──────────────┘   │   │
     │              │  │        │                            │           │   │
     │              │  └────────│────────────────────────────│───────────┘   │
     │              │           │                            │               │
     │              │           v                            v               │
     │              │  ┌─────────────┐              ┌─────────────────┐     │
     │              │  │  Database   │              │  Celery Workers │     │
     │              │  │(PostgreSQL) │              │  (Background)   │     │
     │              │  └─────────────┘              └─────────────────┘     │
     │              │                                       │               │
     │              │                               ┌───────┴───────┐       │
     │              │                               │               │       │
     │              │                          ┌────┴───┐     ┌─────┴────┐  │
     │              │                          │ Redis  │     │ RabbitMQ │  │
     │              │                          └────────┘     └──────────┘  │
     │              └──────────────────────────────────────────────────────┘
     │
     │              ┌──────────────────────────────────────────────────────┐
     └──────────────┤                  Frontend Web App                     │
         HTTPS      │                   (React + XY Flow)                   │
                    │                                                       │
                    │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
                    │  │  Pages   │  │  Flow    │  │  State Stores    │    │
                    │  │ (Router) │──│  Canvas  │──│    (Zustand)     │    │
                    │  └──────────┘  └──────────┘  └──────────────────┘    │
                    └──────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

### ADR-001: Monorepo with UV Workspace

**Context**: Need to manage multiple related packages (main app, base library, integrations).

**Decision**: Use UV workspace for Python package management with 3 packages:
- `langbuilder` (main) - Application entry point
- `langbuilder-base` (library) - Core functionality
- `open-webui` (integration) - External integration

**Consequences**:
- Simplified dependency management
- Shared code between packages
- Atomic version updates
- Single repository for all code

### ADR-002: FastAPI for Backend API

**Context**: Need high-performance async API with automatic OpenAPI documentation.

**Decision**: FastAPI with async/await pattern throughout.

**Consequences**:
- Excellent performance for I/O-bound operations
- Auto-generated API documentation
- Type safety with Pydantic
- Native async support for LLM calls

### ADR-003: LangChain as AI Framework

**Context**: Need abstraction layer for multiple LLM providers and AI patterns.

**Decision**: Use LangChain 0.3.x as the core AI framework.

**Consequences**:
- Provider-agnostic LLM integration
- Pre-built chains and agents
- Active community and ecosystem
- Rapid feature development

### ADR-004: Graph-Based Workflow Execution

**Context**: Need flexible workflow execution with parallel processing support.

**Decision**: Custom graph execution engine with vertex/edge model.

**Consequences**:
- Visual representation matches execution model
- Parallel execution of independent nodes
- State management across workflow
- Debugging and monitoring capabilities

### ADR-005: XY Flow for Visual Canvas

**Context**: Need powerful, customizable flow canvas for workflow editing.

**Decision**: Use @xyflow/react for the visual editor.

**Consequences**:
- Rich drag-and-drop experience
- Custom node and edge rendering
- Built-in pan, zoom, and selection
- Active maintenance and community

### ADR-006: Zustand for State Management

**Context**: Need lightweight, performant state management for React.

**Decision**: Zustand over Redux or MobX.

**Consequences**:
- Minimal boilerplate
- Direct state access without selectors
- Easy testing
- Good performance with large state

### ADR-007: SQLModel for ORM

**Context**: Need type-safe database access compatible with FastAPI.

**Decision**: SQLModel (SQLAlchemy + Pydantic hybrid).

**Consequences**:
- Single model for DB and API schemas
- Type checking at compile time
- FastAPI integration
- Async support

## Technology Stack

### Backend Technologies

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **API Framework** | FastAPI | 0.115+ | REST API |
| **AI Framework** | LangChain | 0.3.21 | LLM orchestration |
| **ORM** | SQLModel | 0.0.22 | Database access |
| **Migrations** | Alembic | 1.13+ | Schema migrations |
| **Task Queue** | Celery | - | Background jobs |
| **Runtime** | Python | 3.10-3.14 | Language runtime |
| **Server** | Uvicorn | 0.30+ | ASGI server |

### Frontend Technologies

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Framework** | React | 18.3 | UI framework |
| **Language** | TypeScript | 5.4 | Type safety |
| **Build Tool** | Vite | 5.4 | Development/build |
| **Canvas** | @xyflow/react | 12.3 | Flow editor |
| **State** | Zustand | 4.5 | State management |
| **Styling** | TailwindCSS | 3.4 | CSS framework |
| **Components** | Radix UI | - | UI primitives |

### Infrastructure Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Database** | PostgreSQL 15 / SQLite | Data persistence |
| **Cache** | Redis 6.2 | Caching, sessions |
| **Message Queue** | RabbitMQ 3.x | Task distribution |
| **Load Balancer** | Traefik 3.0 | Reverse proxy, TLS |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Containers** | Docker | Deployment packaging |

## Integration Patterns

### LLM Provider Integration

```
┌─────────────────────────────────────────────────────────┐
│                  Component Layer                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │OpenAIModel │ │AnthropicLLM│ │ GoogleLLM  │  ...     │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘          │
└─────────│──────────────│──────────────│─────────────────┘
          │              │              │
          v              v              v
┌─────────────────────────────────────────────────────────┐
│                LangChain Abstraction                     │
│           (BaseChatModel, BaseLanguageModel)             │
└─────────────────────────────────────────────────────────┘
          │              │              │
          v              v              v
     ┌─────────┐   ┌─────────┐   ┌─────────┐
     │ OpenAI  │   │Anthropic│   │ Google  │
     │   API   │   │   API   │   │   API   │
     └─────────┘   └─────────┘   └─────────┘
```

### Vector Store Integration

```
┌─────────────────────────────────────────────────────────┐
│                  Component Layer                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │PineconeVS  │ │ ChromaVS   │ │ QdrantVS   │  ...     │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘          │
└─────────│──────────────│──────────────│─────────────────┘
          │              │              │
          v              v              v
┌─────────────────────────────────────────────────────────┐
│             LangChain VectorStore Interface              │
│      (similarity_search, add_texts, delete)              │
└─────────────────────────────────────────────────────────┘
```

### MCP Protocol Integration

```
┌─────────────┐         ┌─────────────┐
│ LangBuilder │◄──SSE───│  MCP Server │
│   Backend   │───POST──│  (External) │
└─────────────┘         └─────────────┘
       │
       │ Tool Discovery
       │ Tool Execution
       │ Resource Access
       v
┌─────────────────────────────────────┐
│        MCP Protocol Layer           │
│  - stdio transport                  │
│  - SSE transport                    │
│  - Tool/Resource schemas            │
└─────────────────────────────────────┘
```

## Quality Attributes

### Performance

| Metric | Target | Approach |
|--------|--------|----------|
| API Response | <200ms | Async I/O, caching |
| Flow Execution | <5s (simple) | Parallel vertex execution |
| Frontend Load | <3s | Code splitting, lazy loading |
| Concurrent Users | 100+ | Horizontal scaling |

### Scalability

- **Horizontal**: Multiple backend instances behind load balancer
- **Async Processing**: Celery workers for background tasks
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session and data caching

### Security

- **Authentication**: JWT tokens with refresh rotation
- **Authorization**: Role-based access control
- **Data Protection**: Encrypted credential storage
- **API Security**: Rate limiting, input validation
- **Network**: TLS encryption, CORS policies

### Reliability

- **Error Handling**: Graceful degradation, retry logic
- **Health Checks**: Liveness and readiness probes
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Logging**: Structured logging, log aggregation

## Evolution and Extensibility

### Extension Points

1. **Custom Components**: Python-based component creation
2. **Custom Nodes**: Frontend node type additions
3. **API Extensions**: V2 API for new features
4. **Integration Hooks**: Webhook and callback support
5. **MCP Servers**: Dynamic tool discovery

### Future Considerations

- Multi-tenant deployment
- Enterprise SSO integration
- Advanced workflow versioning
- Collaborative editing
- Marketplace for components

---

*Generated by CloudGeometry AIx SDLC - Architecture Documentation*
