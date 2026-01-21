# Feature Catalog - LangBuilder

## Overview

This document provides a comprehensive inventory of LangBuilder features organized by category. Each feature includes a description and current implementation status.

**Status Legend:**
- Available - Feature is fully implemented and available
- Beta - Feature is implemented but may have limitations
- Planned - Feature is on the roadmap but not yet implemented

---

## 1. Core Platform Features

### 1.1 Visual Flow Builder

| Feature | Description | Status |
|---------|-------------|--------|
| Node-Based Canvas | Drag-and-drop interface for building AI workflows | Available |
| Component Library | Sidebar with searchable component categories | Available |
| Edge Connections | Visual connections between component inputs/outputs | Available |
| Real-Time Validation | Instant feedback on flow configuration errors | Available |
| Auto-Layout | Automatic arrangement of flow nodes | Available |
| Zoom & Pan | Canvas navigation controls | Available |
| Mini-Map | Overview navigation for large flows | Available |
| Copy/Paste | Duplicate nodes and selections | Available |
| Undo/Redo | Action history for flow editing | Available |
| Keyboard Shortcuts | Productivity shortcuts for common actions | Available |

### 1.2 Flow Management

| Feature | Description | Status |
|---------|-------------|--------|
| Flow CRUD | Create, read, update, delete flows | Available |
| Flow Naming | Custom names and descriptions | Available |
| Flow Duplication | Clone existing flows | Available |
| Flow Import/Export | JSON-based flow sharing | Available |
| Batch Operations | Bulk flow actions | Available |
| Flow Thumbnails | Visual preview of flows | Available |

### 1.3 Project Organization

| Feature | Description | Status |
|---------|-------------|--------|
| Folders | Organize flows into folders | Available |
| Projects | Higher-level project grouping | Available |
| Folder Import/Export | Backup and share folder contents | Available |
| Search | Find flows by name or content | Available |
| Filtering | Filter flows by various criteria | Available |

### 1.4 Flow Execution

| Feature | Description | Status |
|---------|-------------|--------|
| Play/Run | Execute flows from the UI | Available |
| Input Panel | Provide runtime inputs | Available |
| Output Display | View execution results | Available |
| Streaming Output | Real-time response streaming | Available |
| Execution Cancel | Stop running flows | Available |
| Build Status | Visual build progress indicators | Available |

---

## 2. AI & LLM Features

### 2.1 LLM Integration

| Feature | Description | Status |
|---------|-------------|--------|
| OpenAI Models | GPT-4, GPT-4o, GPT-3.5, o1 series | Available |
| Anthropic Models | Claude 3.5, Claude 3 family | Available |
| Google AI | Gemini Pro, Gemini Ultra | Available |
| Azure OpenAI | Enterprise Azure deployment | Available |
| AWS Bedrock | Claude, Llama, Titan via Bedrock | Available |
| Local Models | Ollama, LM Studio integration | Available |
| Model Parameters | Temperature, max tokens, etc. | Available |
| System Prompts | Custom system message configuration | Available |
| Few-Shot Examples | In-context learning setup | Available |
| Response Formats | JSON mode, structured outputs | Available |

### 2.2 Embedding & Retrieval

| Feature | Description | Status |
|---------|-------------|--------|
| Embedding Models | Multiple embedding provider support | Available |
| Vector Store Integration | 19+ vector store options | Available |
| Document Chunking | Text splitting strategies | Available |
| Similarity Search | Find relevant documents | Available |
| Hybrid Search | Combined keyword + semantic | Available |
| Metadata Filtering | Filter by document attributes | Available |

### 2.3 Agent Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Tool Calling | LLM function/tool invocation | Available |
| Multi-Tool Agents | Agents with multiple tools | Available |
| CrewAI Integration | Multi-agent orchestration | Available |
| Memory Components | Conversation memory options | Available |
| Mem0 Integration | Long-term memory management | Available |

---

## 3. Integration Features

### 3.1 LLM Provider Integrations (24+)

| Provider | Models Available | Status |
|----------|-----------------|--------|
| OpenAI | GPT-4, GPT-4o, GPT-3.5, o1 | Available |
| Anthropic | Claude 3.5, Claude 3 | Available |
| Google AI | Gemini Pro, Ultra | Available |
| Azure | Azure OpenAI Service | Available |
| AWS | Bedrock (multiple models) | Available |
| Groq | Fast inference models | Available |
| Mistral | Mistral, Mixtral | Available |
| Cohere | Command, Embed | Available |
| NVIDIA | NIM endpoints | Available |
| Ollama | Local model server | Available |
| Perplexity | Research models | Available |
| DeepSeek | DeepSeek models | Available |
| HuggingFace | Hub models, Inference API | Available |
| IBM | watsonx.ai | Available |
| xAI | Grok models | Available |
| OpenRouter | Multi-provider gateway | Available |
| LM Studio | Local server | Available |
| Vertex AI | Google Cloud models | Available |
| SambaNova | Enterprise AI | Available |
| Cloudflare | Workers AI | Available |
| Maritalk | Brazilian Portuguese | Available |
| Novita | Image + Text | Available |
| NotDiamond | Model routing | Available |
| LiteLLM | Universal interface | Available |

### 3.2 Vector Store Integrations (19+)

| Vector Store | Type | Status |
|--------------|------|--------|
| ChromaDB | Local/embedded | Available |
| Pinecone | Cloud managed | Available |
| Qdrant | Cloud/self-hosted | Available |
| Weaviate | Cloud/self-hosted | Available |
| Milvus | Distributed | Available |
| FAISS | Local | Available |
| PGVector | PostgreSQL | Available |
| Redis | In-memory | Available |
| Elasticsearch | Full-text + vectors | Available |
| OpenSearch | AWS compatible | Available |
| MongoDB Atlas | Document + vectors | Available |
| Supabase | PostgreSQL based | Available |
| Upstash | Serverless | Available |
| AstraDB | DataStax cloud | Available |
| Cassandra | Apache Cassandra | Available |
| ClickHouse | Analytics + vectors | Available |
| Couchbase | Document + vectors | Available |
| Vectara | RAG platform | Available |
| HCD | HCD vectors | Available |

### 3.3 Enterprise Tool Integrations (30+)

| Category | Tools | Status |
|----------|-------|--------|
| CRM | HubSpot, Salesforce, Zoho, Apollo.io | Available |
| Project Management | Jira, Confluence, Notion | Available |
| Search | DuckDuckGo, Tavily, Exa, SerpAPI | Available |
| Documents | Docling, Unstructured, arXiv | Available |
| Web Scraping | Firecrawl, ScrapeGraph, Apify | Available |
| Media | AssemblyAI, TwelveLabs, YouTube | Available |
| Knowledge | Wikipedia, Wolfram Alpha | Available |
| AWS | DynamoDB, SES, Aurora MySQL | Available |
| Agents | CrewAI, Composio, Mem0 | Available |
| Observability | LangWatch, Langfuse | Available |

---

## 4. API Features

### 4.1 REST API (v1)

| Endpoint Category | Operations | Status |
|-------------------|------------|--------|
| Flows | CRUD, upload, download, batch | Available |
| Build/Chat | Execute flows, events, cancel | Available |
| Users | User management | Available |
| API Keys | Key management, credential store | Available |
| Authentication | Login, logout, refresh, auto-login | Available |
| Files | Upload, download, list, delete | Available |
| Folders | CRUD, backup/restore | Available |
| Variables | Encrypted variable management | Available |
| Monitor | Builds, messages, transactions | Available |
| Endpoints | Run flows via API, webhooks | Available |
| Validation | Flow validation | Available |
| MCP | Model Context Protocol endpoints | Available |
| Voice | Voice mode operations | Beta |

### 4.2 OpenAI-Compatible API

| Feature | Description | Status |
|---------|-------------|--------|
| Chat Completions | `/v1/chat/completions` endpoint | Available |
| Models List | `/v1/models` endpoint | Available |
| Streaming | Server-sent events support | Available |
| Function Calling | Tool/function definitions | Available |

### 4.3 MCP Support

| Feature | Description | Status |
|---------|-------------|--------|
| MCP Server | Expose flows as MCP tools | Available |
| MCP Client | Connect to external MCP servers | Available |
| Per-Project MCP | Project-scoped configuration | Available |
| MCP Projects | Manage MCP server projects | Available |

---

## 5. Administration Features

### 5.1 User Management

| Feature | Description | Status |
|---------|-------------|--------|
| User Registration | Account creation | Available |
| User Authentication | Login/logout | Available |
| Session Management | Token-based sessions | Available |
| Auto-Login | Passwordless single-user mode | Available |
| OAuth Integration | Google, Zoho OAuth | Available |

### 5.2 Security

| Feature | Description | Status |
|---------|-------------|--------|
| API Key Management | Create, rotate, revoke keys | Available |
| Encrypted Variables | Secure credential storage | Available |
| HTTPS | TLS encryption | Available |
| CORS Configuration | Cross-origin settings | Available |

### 5.3 Monitoring

| Feature | Description | Status |
|---------|-------------|--------|
| Build Monitoring | Track flow executions | Available |
| Message History | Conversation logs | Available |
| Transaction Logs | Execution audit trail | Available |
| Health Check | System health endpoint | Available |

---

## 6. Deployment Features

### 6.1 Infrastructure

| Feature | Description | Status |
|---------|-------------|--------|
| Self-Hosted | On-premise deployment | Available |
| Docker Support | Container deployment | Available |
| SQLite Database | Development/small deployments | Available |
| PostgreSQL | Production database | Available |
| Environment Config | Configuration via env vars | Available |

### 6.2 Publishing

| Feature | Description | Status |
|---------|-------------|--------|
| OpenWebUI Publish | Export flows to OpenWebUI | Available |
| Publication Status | Track published flows | Available |

---

## 7. Developer Experience

### 7.1 Development Tools

| Feature | Description | Status |
|---------|-------------|--------|
| Starter Projects | Pre-built example flows | Available |
| Component Documentation | In-app component help | Available |
| Flow Validation | Pre-execution validation | Available |
| Error Messages | Descriptive error feedback | Available |

### 7.2 Extensibility

| Feature | Description | Status |
|---------|-------------|--------|
| Custom Components | Create custom components | Available |
| Component API | Component development API | Available |
| Python Runtime | Execute custom Python code | Available |

---

## Feature Statistics

| Category | Count |
|----------|-------|
| Core Platform Features | 25+ |
| LLM Providers | 24 |
| Vector Stores | 19 |
| Enterprise Integrations | 30+ |
| API Endpoints | 20 routers |
| Database Models | 10 |

---

*Document generated: 2026-01-21*
*Source: LangBuilder v1.6.5 codebase analysis*
