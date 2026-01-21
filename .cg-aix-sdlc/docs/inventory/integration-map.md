# Integration Map - LangBuilder

## Overview

LangBuilder provides extensive integrations with LLM providers, vector stores, tools, and enterprise services through its component system. Components are located in `langbuilder/src/backend/base/langbuilder/components/`.

---

## LLM Providers

### OpenAI / OpenAI-Compatible

| Component | Provider | Description |
|-----------|----------|-------------|
| `openai` | OpenAI | GPT-4, GPT-4o, GPT-3.5-turbo, o1, etc. |
| `azure` | Microsoft Azure | Azure OpenAI Service |
| `openrouter` | OpenRouter | Multi-provider gateway |
| `lmstudio` | LM Studio | Local OpenAI-compatible server |
| `litellm` | LiteLLM | Universal LLM interface |

### Major Cloud Providers

| Component | Provider | Models |
|-----------|----------|--------|
| `anthropic` | Anthropic | Claude 3.5, Claude 3, Claude 2 |
| `google` | Google AI | Gemini Pro, Gemini Ultra |
| `vertexai` | Google Cloud | Vertex AI models |
| `amazon` | AWS | Bedrock (Claude, Llama, Titan) |
| `ibm` | IBM | watsonx.ai |

### Specialized AI Providers

| Component | Provider | Focus |
|-----------|----------|-------|
| `groq` | Groq | Ultra-fast inference |
| `nvidia` | NVIDIA | NIM endpoints |
| `cohere` | Cohere | Command, Embed, Rerank |
| `mistral` | Mistral AI | Mistral, Mixtral |
| `deepseek` | DeepSeek | DeepSeek models |
| `perplexity` | Perplexity | Research-focused |
| `sambanova` | SambaNova | Enterprise AI |
| `xai` | xAI | Grok models |
| `huggingface` | HuggingFace | Hub models, Inference API |
| `ollama` | Ollama | Local LLMs |

### Regional/Specialized

| Component | Provider | Region/Focus |
|-----------|----------|--------------|
| `baidu` | Baidu | Qianfan (China) |
| `maritalk` | Maritaca AI | Brazilian Portuguese |
| `novita` | Novita AI | Image + Text |
| `olivya` | Olivya | Agent platform |
| `cloudflare` | Cloudflare | Workers AI |
| `notdiamond` | Not Diamond | Model routing |
| `cleanlab` | Cleanlab | TLM (trustworthy LM) |
| `aiml` | AI/ML | API gateway |

---

## Vector Stores

### Cloud-Managed

| Component | Service | Features |
|-----------|---------|----------|
| `AstraDBVectorStoreComponent` | DataStax Astra | Cassandra-based, serverless |
| `PineconeVectorStoreComponent` | Pinecone | Fully managed |
| `QdrantVectorStoreComponent` | Qdrant Cloud | Filtering, payloads |
| `WeaviateVectorStoreComponent` | Weaviate | GraphQL, modules |
| `MilvusVectorStoreComponent` | Zilliz/Milvus | Distributed |
| `SupabaseVectorStoreComponent` | Supabase | PostgreSQL + pgvector |
| `UpstashVectorStoreComponent` | Upstash | Serverless |

### Self-Hosted/Open Source

| Component | Technology | Features |
|-----------|------------|----------|
| `ChromaVectorStoreComponent` | ChromaDB | Local/embedded |
| `FaissVectorStoreComponent` | FAISS | Facebook AI |
| `PGVectorStoreComponent` | PostgreSQL | pgvector extension |
| `RedisVectorStoreComponent` | Redis | In-memory |
| `ElasticsearchVectorStoreComponent` | Elasticsearch | Full-text + vectors |
| `OpenSearchVectorStoreComponent` | OpenSearch | AWS-compatible |
| `MongoVectorStoreComponent` | MongoDB Atlas | Document + vectors |
| `ClickhouseVectorStoreComponent` | ClickHouse | Analytics + vectors |
| `CouchbaseVectorStoreComponent` | Couchbase | N1QL + vectors |

### Specialized

| Component | Purpose |
|-----------|---------|
| `VectaraVectorStoreComponent` | Vectara RAG platform |
| `VectaraRagComponent` | Vectara RAG-as-a-service |
| `GraphRAGComponent` | Graph-enhanced RAG |
| `LocalDBComponent` | Local file-based storage |
| `CassandraVectorStoreComponent` | Apache Cassandra |
| `HCDVectorStoreComponent` | HCD vectors |

---

## Search & Web

### General Search

| Component | Service | Type |
|-----------|---------|------|
| `duckduckgo` | DuckDuckGo | Privacy-focused search |
| `serpapi` | SerpAPI | SERP scraping |
| `searchapi` | SearchAPI | Multi-engine search |
| `bing` | Microsoft Bing | Web search |
| `yahoosearch` | Yahoo | Web search |
| `tavily` | Tavily | AI-focused search |
| `exa` | Exa | Neural search |
| `glean` | Glean | Enterprise search |

### Web Scraping & Extraction

| Component | Service | Features |
|-----------|---------|----------|
| `firecrawl` | Firecrawl | Web scraping |
| `scrapegraph` | ScrapeGraph | AI-powered scraping |
| `apify` | Apify | Web automation |
| `agentql` | AgentQL | Web agent queries |

---

## Data & Knowledge

### Document Loaders

| Component | Sources |
|-----------|---------|
| `docling` | PDF, DOCX, PPT (IBM) |
| `unstructured` | Multi-format parsing |
| `arxiv` | Academic papers |
| `wikipedia` | Wikipedia articles |
| `youtube` | Video transcripts |
| `git` | Git repositories |

### Media Processing

| Component | Type |
|-----------|------|
| `assemblyai` | Audio transcription |
| `twelvelabs` | Video understanding |

---

## Enterprise Integrations

### CRM & Sales

| Component | Platform | Features |
|-----------|----------|----------|
| `hubspot` | HubSpot | CRM, contacts, deals |
| `salesforce` | Salesforce | (via toolkits) |
| `apollo` | Apollo.io | People search |
| `zoho` | Zoho | CRM integration |

### Project Management

| Component | Platform | Features |
|-----------|----------|----------|
| `jira` | Atlassian Jira | Issues, projects |
| `confluence` | Atlassian Confluence | Documentation |
| `Notion` | Notion | Workspace |

### ERP & Business

| Component | Platform |
|-----------|----------|
| `servicenow` | ServiceNow |
| `workday` | Workday |
| `sap` | SAP |
| `sharepoint` | Microsoft SharePoint |
| `google_sheets` | Google Sheets |

### Communication

| Component | Platform |
|-----------|----------|
| `homeassistant` | Home Assistant |

---

## AI Agents & Tools

### Agent Frameworks

| Component | Framework | Features |
|-----------|-----------|----------|
| `crewai` | CrewAI | Multi-agent orchestration |
| `composio` | Composio | Tool integration |
| `mem0` | Mem0 | Memory management |
| `needle` | Needle | Document QA |

### Utility Tools

| Component | Purpose |
|-----------|---------|
| `wolframalpha` | Computational knowledge |
| `langwatch` | LLM monitoring |
| `icosacomputing` | Specialized compute |

---

## Observability & Monitoring

### LLM Observability

| Integration | Purpose |
|-------------|---------|
| Langfuse | LLM traces, analytics |
| LangWatch | Performance monitoring |
| Langsmith | LangChain tracing |
| Opik | LLM evaluation |
| Arize Phoenix | ML observability |
| Traceloop | OpenTelemetry for LLMs |

### General Observability

| Integration | Purpose |
|-------------|---------|
| OpenTelemetry | Distributed tracing |
| Prometheus | Metrics |
| Sentry | Error tracking |

---

## Storage & Databases

### Cloud Storage

| Integration | Provider |
|-------------|----------|
| AWS S3 | via boto3 |
| Google Cloud Storage | via gcs |

### Databases (Data Sources)

| Component | Database |
|-----------|----------|
| `data.sql_executor` | Generic SQL |
| `amazon.aurora_mysql` | Aurora MySQL |
| `amazon.dynamodb` | DynamoDB |
| `redis` | Redis |

---

## Communication Services

### Email

| Component | Service |
|-----------|---------|
| `amazon.ses` | AWS SES |

---

## Authentication Providers

| Provider | Type |
|----------|------|
| Google OAuth | Social login |
| Zoho OAuth | Social login |
| LDAP | Enterprise (via OpenWebUI) |

---

## MCP (Model Context Protocol)

LangBuilder supports MCP for exposing flows as tools:

| Feature | Description |
|---------|-------------|
| MCP Server | Expose flows as MCP tools |
| MCP Client | Connect to external MCP servers |
| Per-Project MCP | Project-scoped MCP configuration |

---

## External Platforms

### Publishing Targets

| Platform | Description |
|----------|-------------|
| OpenWebUI | Chat UI integration |

---

## Integration Categories Summary

| Category | Count | Examples |
|----------|-------|----------|
| LLM Providers | 24+ | OpenAI, Anthropic, Google |
| Vector Stores | 20+ | Chroma, Pinecone, Qdrant |
| Search Engines | 10+ | DuckDuckGo, Tavily, Exa |
| Enterprise CRM | 5+ | HubSpot, Salesforce, Zoho |
| Document Loaders | 8+ | PDF, DOCX, YouTube |
| Agent Frameworks | 4+ | CrewAI, Composio |
| Observability | 6+ | Langfuse, Sentry |

---

## Adding New Integrations

New integrations are added as components in:
```
langbuilder/src/backend/base/langbuilder/components/<provider>/
```

Each component typically includes:
- `__init__.py` - Component exports
- `<name>.py` - Component implementation
- Optional: Multiple components per provider

Components extend base classes from `langbuilder.custom` or LangChain.
