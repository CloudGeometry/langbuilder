# C4 Context Diagram - LangBuilder

## Overview

This document presents the System Context (Level 1) diagram for LangBuilder, showing the system's boundaries and its interactions with users and external systems.

## System Context Diagram

```mermaid
C4Context
    title System Context Diagram for LangBuilder

    Person(developer, "Developer", "Builds and manages AI workflows using visual canvas")
    Person(endUser, "End User", "Interacts with deployed AI workflows via chat or API")
    Person(admin, "Administrator", "Manages users, API keys, and system configuration")

    System(langbuilder, "LangBuilder", "AI Workflow Builder - Visual platform for creating, deploying, and managing LangChain-based AI workflows")

    System_Ext(openai, "OpenAI", "GPT-4, GPT-3.5 models and embeddings")
    System_Ext(anthropic, "Anthropic", "Claude models")
    System_Ext(google, "Google AI", "Gemini models, VertexAI")
    System_Ext(azure, "Azure OpenAI", "Azure-hosted OpenAI models")
    System_Ext(ollama, "Ollama", "Local LLM inference")
    System_Ext(otherLLM, "Other LLM Providers", "Groq, Cohere, Mistral, DeepSeek, etc.")

    System_Ext(vectorStores, "Vector Databases", "Pinecone, Chroma, Qdrant, PGVector, Milvus, etc.")
    System_Ext(enterpriseTools, "Enterprise Integrations", "HubSpot, Jira, Confluence, Apollo.io")
    System_Ext(searchApis, "Search APIs", "Tavily, DuckDuckGo, SerpAPI, Exa")
    System_Ext(dataLoaders, "Data Sources", "Web scrapers, File loaders, Unstructured")
    System_Ext(openwebui, "Open WebUI", "Chat interface integration")
    System_Ext(mcpServers, "MCP Servers", "Model Context Protocol servers")

    Rel(developer, langbuilder, "Creates and manages workflows", "HTTPS")
    Rel(endUser, langbuilder, "Uses deployed workflows", "HTTPS/WebSocket")
    Rel(admin, langbuilder, "Configures and monitors", "HTTPS")

    Rel(langbuilder, openai, "LLM API calls", "HTTPS")
    Rel(langbuilder, anthropic, "LLM API calls", "HTTPS")
    Rel(langbuilder, google, "LLM API calls", "HTTPS")
    Rel(langbuilder, azure, "LLM API calls", "HTTPS")
    Rel(langbuilder, ollama, "LLM inference", "HTTP")
    Rel(langbuilder, otherLLM, "LLM API calls", "HTTPS")

    Rel(langbuilder, vectorStores, "Vector operations", "HTTPS/gRPC")
    Rel(langbuilder, enterpriseTools, "Data sync and actions", "HTTPS")
    Rel(langbuilder, searchApis, "Web search queries", "HTTPS")
    Rel(langbuilder, dataLoaders, "Data ingestion", "HTTPS")
    Rel(langbuilder, openwebui, "Publishes tools/functions", "HTTPS")
    Rel(langbuilder, mcpServers, "Tool discovery and execution", "stdio/SSE")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Context Description

### Users

| Actor | Description | Primary Interactions |
|-------|-------------|---------------------|
| **Developer** | Technical user who designs AI workflows using the visual canvas interface | Create flows, configure components, test and deploy workflows |
| **End User** | Consumer of deployed AI workflows | Interact via chat interface, API endpoints, or webhooks |
| **Administrator** | System administrator managing the platform | User management, API key configuration, monitoring |

### Core System

**LangBuilder** is an AI workflow builder that provides:

- Visual drag-and-drop canvas for workflow design
- Pre-built components for LLMs, vector stores, tools, and integrations
- Real-time workflow execution and testing
- API endpoints for deployed workflows
- Multi-tenant user management

### External Systems

#### LLM Providers (24 supported)

| Provider | Models | Use Case |
|----------|--------|----------|
| OpenAI | GPT-4, GPT-4o, GPT-3.5-turbo | General purpose, function calling |
| Anthropic | Claude 3.5, Claude 3 | Complex reasoning, long context |
| Google | Gemini Pro, Gemini Flash | Multimodal, fast inference |
| Azure OpenAI | Azure-hosted models | Enterprise compliance |
| Ollama | Llama, Mistral, Phi | Local/private deployment |
| Others | Groq, Cohere, Mistral, etc. | Specialized use cases |

#### Vector Databases (19 supported)

| Category | Examples | Purpose |
|----------|----------|---------|
| Cloud-hosted | Pinecone, Qdrant Cloud, Weaviate | Production RAG applications |
| Self-hosted | Chroma, Milvus, FAISS | Development and on-premise |
| Database extensions | PGVector, OpenSearch | Existing infrastructure leverage |

#### Enterprise Integrations (30+)

| Category | Examples | Capabilities |
|----------|----------|--------------|
| CRM | HubSpot, Apollo.io | Contact search, deal management |
| Collaboration | Jira, Confluence | Issue tracking, knowledge bases |
| Data | AWS DynamoDB, SES | Storage and communication |
| Search | Tavily, DuckDuckGo | Web search augmentation |

## Key Integration Patterns

1. **LLM Integration**: All LLM calls go through LangChain abstractions, enabling provider switching
2. **Vector Store Pattern**: Unified interface for retrieval operations across different vector databases
3. **Tool Invocation**: LangChain tools pattern for external API calls
4. **MCP Protocol**: Model Context Protocol for dynamic tool discovery and execution
5. **Webhook Support**: Inbound webhooks for external system triggers

## Security Boundaries

```
+------------------------------------------+
|           Internet Boundary              |
|  +------------------------------------+  |
|  |        Load Balancer (Traefik)     |  |
|  +------------------------------------+  |
|              |          |                |
|  +-----------|----------|-------------+  |
|  |       LangBuilder System           |  |
|  |  +--------+  +------------------+  |  |
|  |  |Frontend|  |  Backend API     |  |  |
|  |  +--------+  +------------------+  |  |
|  |                     |              |  |
|  |  +------------------+           |  |  |
|  |  |    Database      |           |  |  |
|  |  +------------------+           |  |  |
|  +------------------------------------+  |
+------------------------------------------+
                   |
        External API Calls (HTTPS)
                   |
    +--------------------------------+
    |    External Systems Boundary   |
    |  LLM APIs, Vector Stores, etc. |
    +--------------------------------+
```

## Data Flow Summary

1. **Inbound**: User requests via HTTPS to frontend or API endpoints
2. **Processing**: Backend processes requests, executes workflow graphs
3. **Outbound**: API calls to LLM providers, vector stores, and integrations
4. **Persistence**: Flow definitions and execution results stored in database

---

*Generated by CloudGeometry AIx SDLC - Architecture Documentation*
