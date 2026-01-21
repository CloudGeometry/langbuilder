# LangBuilder Documentation

> Auto-generated documentation for the LangBuilder project using CloudGeometry AIx SDLC.

**Project:** langbuilder v1.6.5
**Generated:** 2026-01-21
**License:** MIT

---

## Quick Start

| I want to... | Go to... |
|--------------|----------|
| Understand the product | [Executive Summary](product/EXECUTIVE-SUMMARY.md) |
| Set up my development environment | [Day 1 Setup](onboarding/day-1-setup.md) |
| Understand the architecture | [System Architecture](architecture/system-architecture.md) |
| Work with AI coding assistants | [AI Context Bundle](../ai-context/context-bundle.md) |
| Run tests | [Testing Strategy](testing/TESTING-STRATEGY.md) |
| See all API endpoints | [API Surface](inventory/api-surface.md) |

---

## Documentation Structure

```
.cg-aix-sdlc/
├── docs/
│   ├── README.md                    # This file (Master Index)
│   ├── inventory/                   # Core metadata and inventories
│   ├── architecture/                # C4 diagrams and architecture docs
│   ├── product/                     # Product analysis and positioning
│   ├── testing/                     # Testing strategy and patterns
│   └── onboarding/                  # Developer onboarding guides
└── ai-context/                      # AI-optimized context files
```

---

## Role-Based Navigation

### For Developers

Start here to understand and contribute to the codebase:

1. **[Day 1 Setup](onboarding/day-1-setup.md)** - Get running in 30 minutes
2. **[Week 1 Guide](onboarding/week-1-guide.md)** - First week learning path
3. **[Architecture Overview](architecture/system-architecture.md)** - System design
4. **[Patterns & Conventions](architecture/patterns-and-principles.md)** - Coding standards
5. **[Testing Patterns](testing/test-patterns.md)** - How to write tests

### For Product Managers

Understand the product from a business perspective:

1. **[Executive Summary](product/EXECUTIVE-SUMMARY.md)** - High-level overview
2. **[Product Positioning](product/PRODUCT-POSITIONING.md)** - Market positioning
3. **[Feature Catalog](product/feature-catalog.md)** - Complete feature list
4. **[Roadmap Inputs](product/roadmap-inputs.md)** - Planning foundation

### For Stakeholders

Business and executive documentation:

1. **[Executive Summary](product/EXECUTIVE-SUMMARY.md)** - Start here
2. **[Capabilities Matrix](product/capabilities-matrix.md)** - What the product can do
3. **[Integration Ecosystem](product/integration-ecosystem.md)** - External integrations

### For QA Engineers

Testing and quality assurance:

1. **[Testing Strategy](testing/TESTING-STRATEGY.md)** - Testing philosophy
2. **[Test Inventory](testing/test-inventory.md)** - Existing tests catalog
3. **[Quality Gates](testing/quality-gates.md)** - Quality criteria
4. **[Master Test Plan](testing/master-test-plan.md)** - Release testing

### For AI Coding Assistants

Optimized context for AI-powered development:

1. **[Context Bundle](../ai-context/context-bundle.md)** - All-in-one context (~2000 tokens)
2. **[Codebase Primer](../ai-context/codebase-primer.md)** - Project overview
3. **[Common Tasks](../ai-context/common-tasks.md)** - How to do things

### For DevOps / SRE

Infrastructure and deployment:

1. **[Deployment Topology](architecture/deployment-topology.md)** - Infrastructure
2. **[Configuration Index](inventory/configuration-index.md)** - Environment variables
3. **[Test Environment Setup](testing/test-environment-setup.md)** - Test infrastructure

---

## Documentation Categories

### Inventory (`inventory/`)

Core metadata extracted from the codebase:

| Document | Description |
|----------|-------------|
| [core-metadata.json](inventory/core-metadata.json) | Machine-readable metadata |
| [repository-map.md](inventory/repository-map.md) | Directory structure |
| [service-catalog.md](inventory/service-catalog.md) | Services and packages |
| [technology-stack.md](inventory/technology-stack.md) | Technologies used |
| [api-surface.md](inventory/api-surface.md) | API endpoints |
| [database-schemas.md](inventory/database-schemas.md) | Database models |
| [integration-map.md](inventory/integration-map.md) | External integrations |
| [configuration-index.md](inventory/configuration-index.md) | Configuration files |

### Architecture (`architecture/`)

Technical architecture documentation:

| Document | Description |
|----------|-------------|
| [c4-context.md](architecture/c4-context.md) | System Context (Level 1) |
| [c4-container.md](architecture/c4-container.md) | Container Diagram (Level 2) |
| [c4-component-backend.md](architecture/c4-component-backend.md) | Backend Components (Level 3) |
| [c4-component-frontend.md](architecture/c4-component-frontend.md) | Frontend Components (Level 3) |
| [system-architecture.md](architecture/system-architecture.md) | High-level architecture |
| [deployment-topology.md](architecture/deployment-topology.md) | Infrastructure |
| [data-architecture.md](architecture/data-architecture.md) | Data flows and storage |
| [patterns-and-principles.md](architecture/patterns-and-principles.md) | Design patterns |

### Product (`product/`)

Product and business documentation:

| Document | Description |
|----------|-------------|
| [EXECUTIVE-SUMMARY.md](product/EXECUTIVE-SUMMARY.md) | Stakeholder overview |
| [PRODUCT-POSITIONING.md](product/PRODUCT-POSITIONING.md) | Market positioning |
| [feature-catalog.md](product/feature-catalog.md) | Feature inventory |
| [capabilities-matrix.md](product/capabilities-matrix.md) | Role x capabilities |
| [business-model.md](product/business-model.md) | Domain entities |
| [integration-ecosystem.md](product/integration-ecosystem.md) | Integration guide |
| [roadmap-inputs.md](product/roadmap-inputs.md) | Planning foundation |

### Testing (`testing/`)

Testing strategy and documentation:

| Document | Description |
|----------|-------------|
| [TESTING-STRATEGY.md](testing/TESTING-STRATEGY.md) | Master strategy |
| [test-inventory.md](testing/test-inventory.md) | Test catalog |
| [test-coverage-analysis.md](testing/test-coverage-analysis.md) | Coverage analysis |
| [test-patterns.md](testing/test-patterns.md) | Testing patterns |
| [test-infrastructure.md](testing/test-infrastructure.md) | Tooling and CI/CD |
| [quality-gates.md](testing/quality-gates.md) | Quality criteria |
| [master-test-plan.md](testing/master-test-plan.md) | Release test plan |

### Onboarding (`onboarding/`)

Developer onboarding guides:

| Document | Description |
|----------|-------------|
| [day-1-setup.md](onboarding/day-1-setup.md) | Getting started |
| [week-1-guide.md](onboarding/week-1-guide.md) | First week learning |
| [30-day-roadmap.md](onboarding/30-day-roadmap.md) | Month-long mastery |
| [local-development.md](onboarding/local-development.md) | Dev environment |
| [debugging-guide.md](onboarding/debugging-guide.md) | Troubleshooting |

### AI Context (`../ai-context/`)

Optimized context for AI coding assistants:

| Document | Description |
|----------|-------------|
| [context-bundle.md](../ai-context/context-bundle.md) | All-in-one context |
| [codebase-primer.md](../ai-context/codebase-primer.md) | Project overview |
| [architecture-summary.md](../ai-context/architecture-summary.md) | Architecture summary |
| [api-quick-reference.md](../ai-context/api-quick-reference.md) | API cheat sheet |
| [database-quick-reference.md](../ai-context/database-quick-reference.md) | Database cheat sheet |
| [patterns-and-conventions.md](../ai-context/patterns-and-conventions.md) | Coding patterns |
| [common-tasks.md](../ai-context/common-tasks.md) | How to do things |

---

## Project Summary

**LangBuilder** is a visual AI workflow builder platform that enables developers to create, test, and deploy AI-powered applications using LangChain.

### Key Features

- Visual flow builder with drag-and-drop interface
- 24+ LLM provider integrations (OpenAI, Anthropic, Google, AWS, etc.)
- 19+ vector store options for RAG applications
- 30+ enterprise tool integrations (Jira, Confluence, HubSpot, etc.)
- OpenAI-compatible REST API
- MCP (Model Context Protocol) support

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, FastAPI, SQLModel, LangChain |
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Database | SQLite (dev), PostgreSQL (prod) |
| State | Zustand (frontend), SQLModel (backend) |
| Build | uv (Python), npm (Node.js) |

### Repository Statistics

- **Source Files:** 2,524
- **Python Files:** 1,232
- **TypeScript Files:** 1,108
- **Components:** 455+
- **API Routers:** 20

---

## Maintenance

This documentation was auto-generated and should be regenerated when:

- Major refactoring occurs
- New services or components are added
- Significant API changes are made
- Quarterly refresh for accuracy

**Regenerate with:**
```bash
/cg:aix-sdlc:eval:orchestrate
```

---

## Related Resources

- [GitHub Repository](https://github.com/CloudGeometry/langbuilder)
- [Official Documentation](https://docs.langbuilder.org)
- [Progress Tracking](progress.json)
- [Generation Config](config.yaml)

---

*Generated by CloudGeometry AIx SDLC - Phase 0 (Eval)*
