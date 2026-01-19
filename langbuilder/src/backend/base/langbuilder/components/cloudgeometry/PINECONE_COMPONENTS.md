# Pinecone Components - Engineering Documentation

## Overview

The Pinecone components provide vector database capabilities for LangBuilder flows. These are **hybrid components** that work both as:
1. **Deterministic flow components** - Connect inputs/outputs via edges
2. **Agent tools** - LLM agents can invoke them dynamically

## Source Files

| Component | File | Lines | Class Name |
|-----------|------|-------|------------|
| Pinecone Search Tool | `pinecone_search_tool.py` | 363 | `PineconeSearchToolComponent` |
| Pinecone Store Tool | `pinecone_store_tool.py` | 416 | `PineconeStoreToolComponent` |
| Registration | `__init__.py` | 47 | N/A |

**Location:** `langbuilder/src/backend/base/langbuilder/components/cloudgeometry/`

---

## Architecture

### Base Class: `LCToolComponent`

Both components extend `LCToolComponent` from `langbuilder.base.langchain_utilities.model`:

```python
from langbuilder.base.langchain_utilities.model import LCToolComponent
from langbuilder.base.tools.constants import TOOL_OUTPUT_NAME, TOOL_OUTPUT_DISPLAY_NAME

class PineconeSearchToolComponent(LCToolComponent):
    ...
```

This base class provides:
- Dual output modes (Data for flows, Tool for agents)
- Standard `run_model()` execution pattern
- `to_toolkit()` method for Agent integration

### Dual Output Pattern

Both components define TWO outputs using constants:

```python
outputs = [
    Output(name="api_run_model", display_name="Data", method="run_model"),
    Output(
        name=TOOL_OUTPUT_NAME,  # "component_as_tool"
        display_name=TOOL_OUTPUT_DISPLAY_NAME,  # "Toolset"
        method="to_toolkit",
        types=["Tool"],
    ),
]
```

| Output Name | Constant | Display Name | Type | Use Case |
|-------------|----------|--------------|------|----------|
| `api_run_model` | N/A | Data | `["Data"]` | Deterministic flow connections |
| `component_as_tool` | `TOOL_OUTPUT_NAME` | Toolset | `["Tool"]` | Agent tool connections |

### Component Registration

Components are registered in `__init__.py` via lazy imports:

```python
_dynamic_imports = {
    "PineconeSearchToolComponent": "pinecone_search_tool",
    "PineconeStoreToolComponent": "pinecone_store_tool",
}

__all__ = [
    "PineconeSearchToolComponent",
    "PineconeStoreToolComponent",
]
```

---

## PineconeSearchToolComponent

### Purpose

Performs semantic search against a Pinecone vector index, returning the most similar documents based on embedding similarity.

### Class Definition

```python
class PineconeSearchToolComponent(LCToolComponent):
    display_name = "Pinecone Search Tool"
    description = "Search Pinecone vector index for semantically similar documents"
    documentation = "https://docs.pinecone.io/docs/query-data"
    icon = "Pinecone"
    name = "PineconeSearchTool"
```

### Inputs

| Input | Type | Required | Default | tool_mode | Purpose |
|-------|------|----------|---------|-----------|---------|
| `search_query` | MessageTextInput | No | - | **True** | Query text for semantic search |
| `tool_name` | StrInput | Yes | `"pinecone_search"` | No | Name exposed to LLM |
| `tool_description` | StrInput | Yes | (see code) | No | Description for LLM |
| `pinecone_api_key` | SecretStrInput | No | - | No | API key (or use env var) |
| `index_name` | StrInput | **Yes** | - | No | Pinecone index name |
| `namespace` | StrInput | No | - | No | Optional namespace |
| `number_of_results` | IntInput | No | `5` | No | Top-K results (advanced) |
| `embedding` | HandleInput | No | - | No | External embedding model |
| `use_pinecone_inference` | BoolInput | No | `False` | No | Use Pinecone's inference API (advanced) |
| `pinecone_embed_model` | DropdownInput | No | `"multilingual-e5-large"` | No | Pinecone model (advanced) |
| `openai_api_key` | SecretStrInput | No | - | No | Fallback OpenAI key (advanced) |
| `openai_model` | StrInput | No | `"text-embedding-3-small"` | No | OpenAI model (advanced) |
| `openai_dimensions` | IntInput | No | `1024` | No | OpenAI dimensions (advanced) |

### Output Structure

Returns `list[Data]` where each Data object contains:

```python
{
    "id": "vector-id",           # Pinecone vector ID
    "score": 0.85,               # Similarity score (0-1)
    "metadata": {...},           # Full metadata object from Pinecone
    "text": "document text...",  # Extracted from metadata.text
    "title": "document title"    # Extracted from metadata.title (or ID if missing)
}
```

### Key Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `run_model` | `(search_query: str = "", **kwargs) -> list[Data]` | Main execution - embeds query, searches Pinecone |
| `build_tool` | `() -> Tool` | Creates `StructuredTool` for Agent use |
| `_get_tools` | `async () -> list[Tool]` | **CRITICAL** - Returns properly named tool |
| `_get_embedding` | `(text: str, input_type: str = "query") -> list[float]` | 3-tier embedding fallback |
| `_get_pinecone_client` | `() -> Pinecone` | Cached Pinecone client |
| `_get_index` | `() -> Index` | Cached index access |

---

## PineconeStoreToolComponent

### Purpose

Stores documents in Pinecone by creating embeddings and upserting vectors with metadata.

### Class Definition

```python
class PineconeStoreToolComponent(LCToolComponent):
    display_name = "Pinecone Store Tool"
    description = "Store documents in Pinecone vector index for future semantic search"
    documentation = "https://docs.pinecone.io/docs/upsert-data"
    icon = "Pinecone"
    name = "PineconeStoreTool"
```

### Inputs

| Input | Type | Required | Default | tool_mode | Purpose |
|-------|------|----------|---------|-----------|---------|
| `text` | MessageTextInput | No | - | **True** | Document content to store |
| `title` | MessageTextInput | No | - | **True** | Document title |
| `metadata_json` | StrInput | No | `"{}"` | No | Optional JSON metadata (advanced) |
| `tool_name` | StrInput | Yes | `"pinecone_store"` | No | Name exposed to LLM |
| `tool_description` | StrInput | Yes | (see code) | No | Description for LLM |
| `pinecone_api_key` | SecretStrInput | No | - | No | API key (or use env var) |
| `index_name` | StrInput | **Yes** | - | No | Pinecone index name |
| `namespace` | StrInput | No | - | No | Optional namespace |
| `embedding` | HandleInput | No | - | No | External embedding model |
| `use_pinecone_inference` | BoolInput | No | `False` | No | Use Pinecone's inference API (advanced) |
| `pinecone_embed_model` | DropdownInput | No | `"multilingual-e5-large"` | No | Pinecone model (advanced) |
| `openai_api_key` | SecretStrInput | No | - | No | Fallback OpenAI key (advanced) |
| `openai_model` | StrInput | No | `"text-embedding-3-small"` | No | OpenAI model (advanced) |
| `openai_dimensions` | IntInput | No | `1024` | No | OpenAI dimensions (advanced) |

### Output Structure

Returns `Data` object:

```python
# Success
{
    "stored": True,
    "id": "generated-uuid",      # UUID v4
    "title": "document title",
    "text_length": 1234          # Character count
}

# Failure
{
    "stored": False,
    "error": "No text provided"  # or "No title provided"
}
```

### Metadata Handling

**Automatically stored metadata:**
```python
doc_metadata = {
    "title": doc_title,
    "text": doc_text[:1000],  # First 1000 characters only
}
```

**Additional metadata** via `metadata_json` input (JSON string):
```json
{"requester": "John", "date": "2026-01-17", "category": "PRD", "url": "https://..."}
```

This gets merged: `doc_metadata.update(extra_metadata)`

**Note:** Text is truncated to 1000 characters in metadata. The full text is embedded but only the first 1000 chars are stored in metadata for retrieval display.

### Key Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `run_model` | `(text: str = "", title: str = "", metadata_json: str = "{}", **kwargs) -> Data` | Main execution |
| `build_tool` | `() -> Tool` | Creates `StructuredTool` for Agent use |
| `_get_tools` | `async () -> list[Tool]` | **CRITICAL** - Returns properly named tool |
| `_get_embedding` | `(text: str, input_type: str = "passage") -> list[float]` | 3-tier embedding fallback |
| `_get_pinecone_client` | `() -> Pinecone` | Cached Pinecone client |
| `_get_index` | `() -> Index` | Cached index access |

---

## Embedding Strategy (3-Tier Fallback)

Both components use identical embedding priority in `_get_embedding()`:

```
1. External Embedding Component (if connected via HandleInput)
   ↓ (if self.embedding is None)
2. Pinecone Inference API (if use_pinecone_inference=True)
   ↓ (if not enabled)
3. OpenAI Embeddings (requires OPENAI_API_KEY)
```

### Pinecone Inference API

```python
result = pc.inference.embed(
    model=model,  # "multilingual-e5-large" or "llama-text-embed-v2"
    inputs=[text],
    parameters={"input_type": input_type, "truncate": "END"}
)
embedding = result[0]['values']  # EmbeddingsList access pattern
```

**Important `input_type` values:**
- `"query"` - For search queries (used by PineconeSearchTool)
- `"passage"` - For documents being stored (used by PineconeStoreTool)

### Dimension Compatibility

| Model | Dimensions | Notes |
|-------|------------|-------|
| multilingual-e5-large | 1024 | Pinecone default |
| llama-text-embed-v2 | 1024 | Alternative Pinecone model |
| text-embedding-3-small | Configurable | Set via `openai_dimensions` (default 1024) |

**Your Pinecone index dimensions must match the embedding model dimensions.**

---

## Critical Implementation Details

### The `_get_tools()` Override

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
    name=self.tool_name,
    description=self.tool_description,
    args_schema=ToolInput,
    func=self.run_model,
    return_direct=False,
    tags=[self.tool_name],  # REQUIRED for Agent tool selection
)
```

### Input Priority (Flow vs Tool)

When `run_model()` is called, inputs follow this priority:
1. **Tool arguments** (passed by Agent when calling the tool)
2. **Component attributes** (set via edge connections in flow)

```python
# Example from PineconeSearchTool.run_model():
query = search_query  # Tool argument first
if not query:
    query = getattr(self, "search_query", "") or ""  # Edge connection fallback
    if hasattr(query, "text"):
        query = query.text
    query = str(query)
```

---

## Usage Patterns

### Pattern 1: Agent Tool (Recommended)

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  ChatInput  │────▶│    Agent    │────▶│  ChatOutput  │
└─────────────┘     └──────┬──────┘     └──────────────┘
                          │
                    tools │ (component_as_tool)
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐
│ PineconeSearch  │ │ PineconeStore   │
│ Tool            │ │ Tool            │
└─────────────────┘ └─────────────────┘
```

- Connect `component_as_tool` output to Agent's `tools` input
- Agent decides when to call tools based on user input
- Dynamic, conversational execution

### Pattern 2: Deterministic Flow

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│  TextInput  │────▶│ PineconeSearch  │────▶│  ChatOutput  │
│   (query)   │     │ Tool            │     │  (results)   │
└─────────────┘     └─────────────────┘     └──────────────┘
```

- Connect inputs via edges to `api_run_model` output
- Component runs when flow executes
- Predictable, testable execution

---

## Connecting to Agent (Edge Format)

### Source Handle (Tool Component)

```python
source_handle = {
    "dataType": "PineconeSearchTool",  # Component's data.type
    "id": tool_node_id,
    "name": "component_as_tool",  # TOOL_OUTPUT_NAME constant
    "output_types": ["Tool"]
}
```

### Target Handle (Agent)

```python
target_handle = {
    "fieldName": "tools",
    "id": agent_node_id,
    "inputTypes": ["Tool"],
    "type": "other"  # CRITICAL: field type is "other", NOT "Tool"
}
```

### Complete Edge Example

```json
{
  "source": "PineconeSearchTool-nNWfI",
  "sourceHandle": "{œdataTypeœ:œPineconeSearchToolœ,œidœ:œPineconeSearchTool-nNWfIœ,œnameœ:œcomponent_as_toolœ,œoutput_typesœ:[œToolœ]}",
  "target": "Agent-ucCHn",
  "targetHandle": "{œfieldNameœ:œtoolsœ,œidœ:œAgent-ucCHnœ,œinputTypesœ:[œToolœ],œtypeœ:œotherœ}",
  "data": {
    "sourceHandle": {
      "dataType": "PineconeSearchTool",
      "id": "PineconeSearchTool-nNWfI",
      "name": "component_as_tool",
      "output_types": ["Tool"]
    },
    "targetHandle": {
      "fieldName": "tools",
      "id": "Agent-ucCHn",
      "inputTypes": ["Tool"],
      "type": "other"
    }
  }
}
```

**Note:** The `œ` character replaces `"` in handle strings (LangBuilder encoding).

---

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `PINECONE_API_KEY` | Pinecone authentication | Yes (or provide in component) |
| `OPENAI_API_KEY` | Fallback embedding authentication | Only if using OpenAI fallback |

---

## Dependencies

```
pinecone>=3.0.0        # Pinecone client with inference API
langchain-core         # StructuredTool, BaseModel
pydantic>=2.0          # Field, create_model
openai                 # Fallback embeddings (optional)
```

---

## Testing

### Via API

```bash
# Test search
curl -X POST "http://localhost:4100/api/v1/run/{flow_id}" \
  -H "x-api-key: {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "Search for Kubernetes best practices",
    "input_type": "chat",
    "output_type": "chat",
    "stream": false
  }'
```

### Via Playground

1. Open flow in LangBuilder UI
2. Configure components:
   - **Index Name**: Your Pinecone index (e.g., `case-studies-cg-2026-01`)
   - **Namespace**: Optional (e.g., `case-studies`)
   - **Use Pinecone Inference**: Toggle ON
   - **Pinecone API Key**: Your API key (or leave empty if env var is set)
3. Click **Playground** button
4. Test queries:
   - Search: `"Find documents about AWS migration"`
   - Store: `"Store this document: Title 'Test Doc', Content 'This is test content'"`

### Verified Test Configuration

```python
PINECONE_INDEX = "case-studies-cg-2026-01"
PINECONE_NAMESPACE = "case-studies"
USE_PINECONE_INFERENCE = True
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Tools all named "run_model" | Missing `_get_tools()` override | Ensure async `_get_tools()` method exists |
| Agent doesn't select tool | Missing `tags` in StructuredTool | Add `tags=[self.tool_name]` |
| Dimension mismatch error | Index dimensions ≠ embedding dimensions | Ensure `openai_dimensions` matches index (default 1024) |
| "No embedding method" error | No embedding configured | Enable Pinecone inference, connect embedding, or set OPENAI_API_KEY |
| "Index not found" error | Wrong index name or missing API key | Verify `index_name` and `pinecone_api_key` |
| Component not in UI | Not registered in `__init__.py` | Add to `_dynamic_imports` and `__all__` |
| Edge not connecting | Wrong output name | Use `component_as_tool`, not `api_build_tool` |
| Edge silently dropped | Wrong target handle type | Use `type: "other"`, not `type: "Tool"` |

---

## Code Review Checklist

When modifying these components:

- [ ] Extends `LCToolComponent` base class
- [ ] Uses `TOOL_OUTPUT_NAME` and `TOOL_OUTPUT_DISPLAY_NAME` constants for Tool output
- [ ] `_get_tools()` async method present and returns properly named tool
- [ ] `tags=[self.tool_name]` in `StructuredTool.from_function()`
- [ ] `tool_mode=True` on inputs that Agent should pass
- [ ] Input priority handles both tool args and edge connections
- [ ] Embedding fallback chain works (external → Pinecone inference → OpenAI)
- [ ] Component registered in `__init__.py` (`_dynamic_imports` and `__all__`)
- [ ] Error handling provides clear messages
- [ ] Metadata handling documented and tested

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-17 | Updated documentation to match actual source code. Fixed output names (`component_as_tool` not `api_build_tool`). Added edge format examples. Added metadata handling section. Added API and Playground testing instructions. |
