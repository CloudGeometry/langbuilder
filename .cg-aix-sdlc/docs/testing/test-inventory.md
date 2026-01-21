# Test Inventory

## Overview

This document provides a comprehensive catalog of all tests in the LangBuilder project.

## Test Statistics Summary

| Category | Count | Location |
|----------|-------|----------|
| Backend Unit Tests | ~253 files | `src/backend/tests/unit/` |
| Backend Integration Tests | ~36 files | `src/backend/tests/integration/` |
| Backend Performance Tests | 2 files | `src/backend/tests/performance/` |
| Frontend E2E Tests | ~150 specs | `src/frontend/tests/` |
| Frontend Unit Tests | Multiple | `src/frontend/src/**/__tests__/` |

## Backend Tests

### Unit Tests Structure

```
src/backend/tests/unit/
├── api/
│   ├── test_api_utils.py
│   ├── v1/
│   │   ├── test_api_key.py
│   │   ├── test_api_schemas.py
│   │   ├── test_endpoints.py
│   │   ├── test_files.py
│   │   ├── test_flows.py
│   │   ├── test_folders.py
│   │   ├── test_mcp.py
│   │   ├── test_mcp_projects.py
│   │   ├── test_projects.py
│   │   ├── test_rename_flow_to_save.py
│   │   ├── test_schemas.py
│   │   ├── test_starter_projects.py
│   │   ├── test_store.py
│   │   ├── test_users.py
│   │   ├── test_validate.py
│   │   └── test_variable.py
│   └── v2/
│       ├── test_files.py
│       └── test_mcp_servers_file.py
├── base/
│   ├── data/
│   │   ├── test_base_file.py
│   │   └── test_kb_utils.py
│   ├── load/
│   │   └── test_load.py
│   ├── mcp/
│   │   └── test_mcp_util.py
│   └── tools/
│       ├── test_component_toolkit.py
│       ├── test_create_schema.py
│       ├── test_toolmodemixin.py
│       └── test_vector_store_decorator.py
├── components/
│   ├── agents/
│   │   ├── test_agent_component.py
│   │   ├── test_agent_events.py
│   │   ├── test_multimodal_agent.py
│   │   └── test_tool_calling_agent.py
│   └── bundles/
│       ├── composio/
│       │   ├── test_base.py
│       │   ├── test_github.py
│       │   ├── test_gmail.py
│       │   ├── test_googlecalendar.py
│       │   ├── test_outlook.py
│       │   └── test_slack.py
│       └── google/
│           └── test_google_bq_sql_executor_component.py
└── template/
    └── test_starter_projects.py
```

### Integration Tests Structure

```
src/backend/tests/integration/
├── backward_compatibility/
│   └── test_starter_projects.py
├── components/
│   ├── assistants/
│   │   └── test_assistants_components.py
│   ├── astra/
│   │   └── test_astra_component.py
│   ├── helpers/
│   │   └── test_parse_json_data.py
│   ├── inputs/
│   │   ├── test_chat_input.py
│   │   └── test_text_input.py
│   ├── mcp/
│   │   ├── test_mcp_component.py
│   │   ├── test_mcp_memory_leak.py
│   │   └── test_mcp_superuser_flow.py
│   ├── outputs/
│   │   ├── test_chat_output.py
│   │   └── test_text_output.py
│   ├── output_parsers/
│   │   └── test_output_parser.py
│   └── prompts/
│       └── test_prompt.py
├── flows/
│   └── test_basic_prompting.py
├── test_dynamic_import_integration.py
├── test_exception_telemetry.py
├── test_image_providers.py
├── test_misc.py
├── test_openai_responses_extended.py
├── test_openai_responses_integration.py
└── test_openai_streaming_comparison.py
```

### Performance Tests

```
src/backend/tests/performance/
├── test_server_init.py        # Server initialization performance
└── __init__.py
```

### Load Tests (Locust)

```
src/backend/tests/locust/
└── locustfile.py              # Load testing configuration
```

## Frontend Tests

### E2E Tests (Playwright)

```
src/frontend/tests/
├── core/
│   ├── features/              # Feature-specific E2E tests
│   │   ├── actionsMainPage-shard-1.spec.ts
│   │   ├── auto-login-off.spec.ts
│   │   ├── chatInputOutputUser-shard-0.spec.ts
│   │   ├── componentHoverAdd.spec.ts
│   │   ├── composio.spec.ts
│   │   ├── customComponentAdd.spec.ts
│   │   ├── filterEdge-shard-0.spec.ts
│   │   ├── filterSidebar.spec.ts
│   │   ├── flow-lock.spec.ts
│   │   ├── folders.spec.ts
│   │   ├── freeze-path.spec.ts
│   │   ├── freeze.spec.ts
│   │   ├── globalVariables.spec.ts
│   │   ├── group.spec.ts
│   │   ├── keyboardComponentSearch.spec.ts
│   │   ├── logs.spec.ts
│   │   ├── playground.spec.ts
│   │   ├── publish-flow.spec.ts
│   │   ├── saveComponents.spec.ts
│   │   ├── stop-building.spec.ts
│   │   ├── store-shard-2.spec.ts
│   │   ├── toolModeGroup.spec.ts
│   │   ├── tweaksTest.spec.ts
│   │   ├── user-flow-state-cleanup.spec.ts
│   │   ├── user-progress-track.spec.ts
│   │   └── voice-assistant.spec.ts
│   └── integrations/          # Integration-focused E2E tests
│       ├── Basic Prompting.spec.ts
│       ├── Blog Writer.spec.ts
│       ├── Custom Component Generator.spec.ts
│       ├── decisionFlow.spec.ts
│       ├── Document QA.spec.ts
│       ├── Dynamic Agent.spec.ts
│       ├── Financial Report Parser.spec.ts
│       ├── Gmail Agent.spec.ts
│       ├── Hierarchical Agent.spec.ts
│       ├── Image Sentiment Analysis.spec.ts
│       ├── Instagram Copywriter.spec.ts
│       ├── Invoice Summarizer.spec.ts
│       ├── Market Research.spec.ts
│       ├── Memory Chatbot.spec.ts
│       ├── News Aggregator.spec.ts
│       ├── Pokedex Agent.spec.ts
│       ├── Portfolio Website Code Generator.spec.ts
│       ├── Price Deal Finder.spec.ts
│       ├── Prompt Chaining.spec.ts
│       ├── Research Translation Loop.spec.ts
│       ├── SaaS Pricing.spec.ts
│       ├── SEO Keyword Generator.spec.ts
│       ├── Sequential Task Agent.spec.ts
│       └── similarity.spec.ts
├── extended/                  # Extended test suites
├── templates/                 # Test templates
├── utils/                     # Test utilities
└── assets/                    # Test assets
```

### Test Data Files

```
src/backend/tests/data/
├── basic_example.json
├── complex_example.json
├── Openapi.json
├── grouped_chat.json
├── one_group_chat.json
├── vector_store_grouped.json
├── BasicChatwithPromptandHistory.json
├── ChatInputTest.json
├── TwoOutputsTest.json
├── Vector_store.json
├── SimpleAPITest.json
├── MemoryChatbotNoLLM.json
├── env_variable_test.json
├── LoopTest.json
└── WebhookTest.json
```

## Test Categories by Area

### API Tests

| Test File | Area | Type |
|-----------|------|------|
| `test_api_key.py` | Authentication | Unit |
| `test_endpoints.py` | REST API | Unit |
| `test_flows.py` | Flow Management | Unit |
| `test_users.py` | User Management | Unit |
| `test_validate.py` | Input Validation | Unit |

### Component Tests

| Test File | Component Type | Type |
|-----------|----------------|------|
| `test_agent_component.py` | Agents | Unit |
| `test_chat_input.py` | Input Components | Integration |
| `test_prompt.py` | Prompt Components | Integration |
| `test_mcp_component.py` | MCP Integration | Integration |

### Infrastructure Tests

| Test File | Area | Type |
|-----------|------|------|
| `test_server_init.py` | Performance | Performance |
| `locustfile.py` | Load Testing | Load |
| `test_dynamic_import_integration.py` | Module Loading | Integration |

### E2E Test Suites by Tag

| Tag | Description | Files |
|-----|-------------|-------|
| `@release` | Release verification | All core specs |
| `@components` | Component functionality | Component specs |
| `@starter-projects` | Starter project validation | Integration specs |
| `@workspace` | Workspace features | Feature specs |
| `@api` | API functionality | API-related specs |
| `@database` | Database operations | DB-related specs |

## Test Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | pytest configuration |
| `conftest.py` | Shared fixtures |
| `playwright.config.ts` | Playwright configuration |
| `jest.config.js` | Jest configuration |
| `.test_durations` | Test timing data for parallelization |

## Key Test Files

### conftest.py (Backend)

Primary fixtures provided:
- `client` - Async test client
- `session` - Database session
- `active_user` - Test user fixture
- `logged_in_headers` - Auth headers
- `flow` - Test flow fixture
- `starter_project` - Starter project fixture

### globalTeardown.ts (Frontend)

Handles test cleanup after Playwright runs.

---
*Generated by CG AIx SDLC - Testing Documentation*
