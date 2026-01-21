# High-Level Architecture

**Change Request:** langwatch-observability-poc
**Generated:** 2026-01-21
**Step:** 2a - High-Level Architecture

---

## Context

This document describes the **existing** LangWatch integration architecture in LangBuilder. Since Option A (Use Existing Integration) was selected, no new architecture is being designed - this documents what already exists.

---

## Architecture Overview

### System Context (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LangBuilder System                          │
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐ │
│  │   Frontend  │───▶│   Backend   │───▶│     Flow Execution      │ │
│  │   (React)   │    │  (FastAPI)  │    │       Engine            │ │
│  └─────────────┘    └─────────────┘    └───────────┬─────────────┘ │
│                                                     │               │
│                                          ┌──────────▼──────────┐   │
│                                          │   TracingService    │   │
│                                          │  (Multi-Provider)   │   │
│                                          └──────────┬──────────┘   │
│                                                     │               │
└─────────────────────────────────────────────────────┼───────────────┘
                                                      │
                              ┌────────────────────────┼────────────────────────┐
                              │                        │                        │
                              ▼                        ▼                        ▼
                    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
                    │    LangWatch    │     │    LangSmith    │     │    LangFuse     │
                    │   (External)    │     │   (External)    │     │   (External)    │
                    └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Container Diagram (C4 Level 2)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              LangBuilder Backend                              │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                              Graph Execution                            │  │
│  │                                                                         │  │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │  │
│  │   │   Graph     │───▶│   Vertex    │───▶│  Component  │               │  │
│  │   │  Executor   │    │   Builder   │    │   Build     │               │  │
│  │   └──────┬──────┘    └─────────────┘    └──────┬──────┘               │  │
│  │          │                                      │                      │  │
│  │          │ start_tracers()              trace_component()              │  │
│  │          │                                      │                      │  │
│  │          ▼                                      ▼                      │  │
│  │   ┌────────────────────────────────────────────────────────────────┐  │  │
│  │   │                      TracingService                             │  │  │
│  │   │                                                                 │  │  │
│  │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │  │
│  │   │   │ LangWatch   │  │ LangSmith   │  │  LangFuse   │  ... more │  │  │
│  │   │   │   Tracer    │  │   Tracer    │  │   Tracer    │           │  │  │
│  │   │   └──────┬──────┘  └─────────────┘  └─────────────┘           │  │  │
│  │   │          │                                                      │  │  │
│  │   └──────────┼──────────────────────────────────────────────────────┘  │  │
│  │              │                                                         │  │
│  └──────────────┼─────────────────────────────────────────────────────────┘  │
│                 │                                                             │
└─────────────────┼─────────────────────────────────────────────────────────────┘
                  │
                  │ HTTPS (async)
                  ▼
         ┌─────────────────┐
         │  LangWatch API  │
         │ app.langwatch.ai│
         └─────────────────┘
```

---

## Component Architecture

### TracingService Component Diagram (C4 Level 3)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               TracingService                                     │
│                     services/tracing/service.py:104                             │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                            TraceContext                                  │    │
│  │                                                                          │    │
│  │   run_id: UUID                                                          │    │
│  │   run_name: str                                                         │    │
│  │   project_name: str                                                     │    │
│  │   tracers: dict[str, BaseTracer]  ◀──┐                                 │    │
│  │   all_inputs: dict                    │                                 │    │
│  │   all_outputs: dict                   │                                 │    │
│  │   traces_queue: asyncio.Queue         │                                 │    │
│  └───────────────────────────────────────┼─────────────────────────────────┘    │
│                                          │                                       │
│  ┌──────────────────────┬────────────────┼────────────────┬─────────────────┐   │
│  │                      │                │                │                 │   │
│  ▼                      ▼                ▼                ▼                 ▼   │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────┐   │
│ │ LangWatch    │ │ LangSmith    │ │  LangFuse    │ │ ArizePhoenix │ │ Opik │   │
│ │   Tracer     │ │   Tracer     │ │   Tracer     │ │    Tracer    │ │Tracer│   │
│ └──────┬───────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────┘   │
│        │                                                                         │
│        │ Each tracer implements BaseTracer interface                            │
│        │                                                                         │
└────────┼─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              BaseTracer (ABC)                                   │
│                        services/tracing/base.py:16                             │
│                                                                                 │
│   Abstract Methods:                                                            │
│   ├── ready: bool                    # Is tracer configured?                   │
│   ├── add_trace()                    # Start a component span                  │
│   ├── end_trace()                    # End a component span                    │
│   ├── end()                          # End entire trace                        │
│   └── get_langchain_callback()       # Get LangChain callback handler          │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### LangWatchTracer Component Detail

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                            LangWatchTracer                                      │
│                    services/tracing/langwatch.py:24                            │
│                                                                                 │
│   Properties:                                                                   │
│   ├── trace_name: str                                                          │
│   ├── trace_type: str                                                          │
│   ├── project_name: str                                                        │
│   ├── trace_id: UUID                                                           │
│   ├── flow_id: str                                                             │
│   ├── _ready: bool                   # Configuration status                    │
│   ├── _client: langwatch             # LangWatch SDK client                    │
│   ├── trace: ContextTrace            # Active trace context                    │
│   └── spans: dict[str, ContextSpan]  # Component spans                         │
│                                                                                 │
│   Methods:                                                                      │
│   ├── setup_langwatch() -> bool      # Check env var, import SDK               │
│   ├── add_trace()                    # Create span for component               │
│   ├── end_trace()                    # Close span with outputs                 │
│   ├── end()                          # Finalize trace, send to API             │
│   ├── get_langchain_callback()       # Return LangChain callback               │
│   └── _convert_to_langwatch_types()  # Convert LangBuilder types               │
│                                                                                 │
│   Environment Variables:                                                        │
│   ├── LANGWATCH_API_KEY (required)   # Enables tracing                         │
│   └── LANGWATCH_ENDPOINT (optional)  # Custom endpoint                         │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Sequence Diagram: Flow Execution with Tracing

```
┌─────────┐     ┌─────────┐     ┌───────────────┐     ┌─────────────┐     ┌───────────┐
│  User   │     │  Graph  │     │TracingService │     │LangWatchTr. │     │LangWatch  │
│         │     │         │     │               │     │             │     │   API     │
└────┬────┘     └────┬────┘     └──────┬────────┘     └──────┬──────┘     └─────┬─────┘
     │               │                 │                     │                   │
     │  Run Flow     │                 │                     │                   │
     │──────────────▶│                 │                     │                   │
     │               │                 │                     │                   │
     │               │ start_tracers() │                     │                   │
     │               │────────────────▶│                     │                   │
     │               │                 │                     │                   │
     │               │                 │ _initialize_langwatch_tracer()          │
     │               │                 │────────────────────▶│                   │
     │               │                 │                     │                   │
     │               │                 │                     │ setup_langwatch() │
     │               │                 │                     │───────┐           │
     │               │                 │                     │       │ Check     │
     │               │                 │                     │◀──────┘ API key   │
     │               │                 │                     │                   │
     │               │                 │                     │ trace.__enter__() │
     │               │                 │                     │──────────────────▶│
     │               │                 │                     │                   │
     │               │   For each component:                 │                   │
     │               │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─│
     │               │                 │                     │                   │
     │               │ trace_component()                     │                   │
     │               │────────────────▶│                     │                   │
     │               │                 │                     │                   │
     │               │                 │ add_trace()         │                   │
     │               │                 │────────────────────▶│                   │
     │               │                 │                     │                   │
     │               │                 │                     │ trace.span()      │
     │               │                 │                     │ (buffered)        │
     │               │                 │                     │                   │
     │               │   [Component executes with LLM calls] │                   │
     │               │                 │                     │                   │
     │               │                 │ set_outputs()       │                   │
     │               │────────────────▶│                     │                   │
     │               │                 │                     │                   │
     │               │                 │ end_trace()         │                   │
     │               │                 │────────────────────▶│                   │
     │               │                 │                     │                   │
     │               │                 │                     │ span.end()        │
     │               │                 │                     │ (buffered)        │
     │               │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─│
     │               │                 │                     │                   │
     │               │ end_tracers()   │                     │                   │
     │               │────────────────▶│                     │                   │
     │               │                 │                     │                   │
     │               │                 │ end()               │                   │
     │               │                 │────────────────────▶│                   │
     │               │                 │                     │                   │
     │               │                 │                     │ trace.__exit__()  │
     │               │                 │                     │──────────────────▶│
     │               │                 │                     │                   │
     │               │                 │                     │                   │ Send traces
     │               │                 │                     │                   │ (async)
     │  Response     │                 │                     │                   │
     │◀──────────────│                 │                     │                   │
     │               │                 │                     │                   │
```

### Data Captured Per Trace

| Data Type | Source | LangWatch Field | Example |
|-----------|--------|-----------------|---------|
| Trace ID | Graph run_id | trace_id | `uuid4()` |
| Flow Name | Graph flow_name | root_span.name | "Chat Flow" |
| Span ID | Vertex ID + nanoid | span_id | "vertex-abc-x1y2z3" |
| Span Type | Component trace_type | type | "workflow", "component" |
| Inputs | Component inputs | input | `{"message": "Hello"}` |
| Outputs | Component outputs | output | `{"response": "Hi!"}` |
| Error | Exception if any | error | `ValueError("...")` |
| Session ID | User session | metadata.thread_id | "session-123" |
| Labels | Flow metadata | metadata.labels | ["Flow: Chat"] |

---

## Key Design Decisions

### 1. Multi-Provider Architecture

The `TracingService` supports multiple tracing providers simultaneously:
- LangWatch
- LangSmith
- LangFuse
- Arize Phoenix
- Opik

Each provider is initialized based on environment variables and operates independently.

### 2. Graceful Degradation

```python
# services/tracing/langwatch.py:61-71
def setup_langwatch(self) -> bool:
    if "LANGWATCH_API_KEY" not in os.environ:
        return False  # Graceful: no key = disabled
    try:
        import langwatch
        self._client = langwatch
    except ImportError:
        logger.exception("Could not import langwatch...")
        return False  # Graceful: no SDK = disabled
    return True
```

**Behavior:**
- No API key → Tracer disabled, flow runs normally
- SDK not installed → Warning logged, tracer disabled
- API error → Logged, does not interrupt flow

### 3. Async Queue Processing

```python
# services/tracing/service.py:124-132
async def _trace_worker(self, trace_context: TraceContext) -> None:
    while trace_context.running or not trace_context.traces_queue.empty():
        trace_func, args = await trace_context.traces_queue.get()
        try:
            trace_func(*args)
        except Exception:
            logger.exception("Error processing trace_func")
        finally:
            trace_context.traces_queue.task_done()
```

**Benefits:**
- Non-blocking trace operations
- Flow execution not delayed by tracing
- Errors isolated from main execution

### 4. LangChain Callback Integration

```python
# services/tracing/langwatch.py:181-185
def get_langchain_callback(self) -> BaseCallbackHandler | None:
    if self.trace is None:
        return None
    return self.trace.get_langchain_callback()
```

**Purpose:**
- Captures LLM calls made through LangChain
- Automatic prompt/response capture
- Token usage tracking

---

## Integration Points

### 1. Environment Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `LANGWATCH_API_KEY` | Yes | None | Enables tracing |
| `LANGWATCH_ENDPOINT` | No | `https://app.langwatch.ai` | API endpoint |
| `LANGCHAIN_PROJECT` | No | `Langbuilder` | Project name |

### 2. Code Integration Points

| File | Line | Purpose |
|------|------|---------|
| `services/tracing/service.py` | 152-165 | LangWatch tracer initialization |
| `services/tracing/langwatch.py` | 24-186 | LangWatch tracer implementation |
| `graph/graph/base.py` | 43 | TracingService import |
| `components/langwatch/langwatch.py` | 25-279 | LangWatch Evaluator component |
| `base/langwatch/utils.py` | - | LangWatch utilities |

### 3. External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `langwatch` | >= 0.1.0 | LangWatch Python SDK |
| `nanoid` | - | Unique span ID generation |
| `httpx` | - | Async HTTP for evaluator |

---

## Security Considerations

### Data Flow Security

1. **API Key Storage**: Environment variable only (not in code)
2. **Transport**: HTTPS to LangWatch API
3. **Sensitive Data**: API keys in inputs are masked (`*****`)

```python
# services/tracing/service.py:276-281
@staticmethod
def _cleanup_inputs(inputs: dict[str, Any]):
    inputs = inputs.copy()
    for key in inputs:
        if "api_key" in key:
            inputs[key] = "*****"  # avoid logging api_keys
    return inputs
```

### Data Sent to LangWatch

| Sent | Not Sent |
|------|----------|
| Flow name | User credentials |
| Component inputs/outputs | API keys (masked) |
| LLM prompts/responses | Internal system data |
| Token usage | Database connections |
| Execution timing | File system paths |

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Environment                   │
│                                                             │
│   .env                                                      │
│   └── LANGWATCH_API_KEY=lw_xxxxxx                          │
│                                                             │
│   LangBuilder Backend                                       │
│   └── TracingService                                        │
│       └── LangWatchTracer                                   │
│           └── ready=true                                    │
│                                                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangWatch Cloud                           │
│                  app.langwatch.ai                           │
│                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │   Traces    │  │  Analytics  │  │  Dashboard  │        │
│   │   Storage   │  │   Engine    │  │     UI      │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Compliance

### POC Requirements Coverage

| Requirement | Architecture Support |
|-------------|---------------------|
| FR-001: Env config | `setup_langwatch()` checks `LANGWATCH_API_KEY` |
| FR-002: Auto trace | `TracingService.start_tracers()` auto-initializes |
| FR-003: LLM capture | `get_langchain_callback()` returns handler |
| FR-004: Error capture | `end_trace(error=e)` captures exceptions |
| NFR-001: Performance | Async queue processing, non-blocking |
| NFR-002: Reliability | `_ready` flag for graceful degradation |
| NFR-003: Security | HTTPS transport, API key masking |
| NFR-004: Usability | Single env var enables everything |

---

## Limitations (Existing Implementation)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No UI integration | No trace links in LangBuilder UI | View traces in LangWatch dashboard |
| No custom evaluations | Can't run evaluations from flows | Use LangWatch Evaluator component |
| Single project | All traces go to one project | Configure via LANGCHAIN_PROJECT |
| No sampling | All traces captured | Use LangWatch dashboard filtering |

---

**Metadata:**
- change_request: langwatch-observability-poc
- step: 2a-architecture
- status: complete
- generated_at: 2026-01-21

*Generated by CloudGeometry AIx SDLC - Phase 2 (Specs)*
