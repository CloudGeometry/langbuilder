# Discovery Brief

**Change Request:** langwatch-observability-poc
**Generated:** 2026-01-21
**Step:** 1 - Discovery Kickoff

---

## Executive Summary

Integrate LangWatch observability into LangBuilder to enable trace visualization after running AI workflow flows. This is a POC (Proof of Concept) with a preference for configuration-only integration requiring minimal code changes.

---

## Vision Statement

Enable LangBuilder users to gain visibility into their AI workflow executions through LangWatch observability, showing detailed traces, LLM calls, and performance metrics after running flows.

---

## Problem Statement

### Current State
LangBuilder currently provides AI workflow building capabilities with 24+ LLM providers and 19+ vector stores, but lacks native observability into workflow executions. Users cannot easily:
- View traces of their AI workflow runs
- Debug LLM call chains and responses
- Monitor token usage and costs
- Analyze performance bottlenecks

### Desired State
After running a flow in LangBuilder, users should be able to view comprehensive traces showing:
- Full execution flow visualization
- Individual LLM calls with inputs/outputs
- Token usage and cost tracking
- Performance timing data
- Metadata and custom attributes

---

## Goals & Constraints

### Primary Goal
> POC LangWatch observability for LangBuilder; show traces after running a flow

### Constraints
| Constraint | Priority | Rationale |
|------------|----------|-----------|
| Config-only integration preferred | High | Minimize codebase changes |
| Minimal code changes | High | Reduce implementation risk |
| POC scope | Medium | Validate approach before full integration |

---

## Stakeholder Input

### Source
Direct user research input including LangWatch documentation analysis, competitive evaluation, and technical integration assessment.

### Key Findings

#### LangWatch Platform Overview
- **Type:** AI engineering platform for testing and monitoring AI agents
- **Founded:** 2024, San Francisco
- **Team:** ~4-10 employees
- **Pricing:** Free tier (10K messages/month), Team ($50/month, 100K messages)

#### Integration Approach
LangWatch offers a minimal integration path:

1. **Environment Variable Only:**
   ```
   LANGWATCH_API_KEY=<your-key>
   ```

2. **Custom Trace Hooks (Optional):**
   ```python
   import langwatch
   langwatch.get_current_trace().update(
       input=...,
       output=...,
       metadata={...}
   )
   ```

#### Key Features Relevant to POC
| Feature | Description | POC Priority |
|---------|-------------|--------------|
| Auto-capture LLM calls | Automatic instrumentation of LangChain | High |
| Trace visualization | Visual flow of AI workflow execution | High |
| Token/cost tracking | Usage monitoring per trace | Medium |
| Custom metadata | Add flow-specific context | Medium |
| Evaluation hooks | Post-execution quality checks | Low (future) |

#### Existing LangBuilder Integration Points
From codebase analysis:
- `langbuilder/src/backend/base/langbuilder/components/langwatch/` - Existing LangWatch component
- LangChain integration via existing providers
- FastAPI backend with async execution

---

## Competitive Context

### Alternatives Evaluated
| Platform | Integration Complexity | Key Differentiator |
|----------|----------------------|-------------------|
| LangWatch | Low (env var) | LangChain-native, simple setup |
| LangSmith | Medium | LangChain official, full lifecycle |
| Langfuse | Low-Medium | Open source, self-host option |
| Helicone | Low | Proxy-based, minimal code |

### Selection Rationale
LangWatch selected for POC due to:
1. Simplest integration path (single env var)
2. Good LangChain native support
3. Free tier sufficient for POC validation
4. Custom trace hooks for LangBuilder-specific metadata

---

## Success Criteria

### POC Validation Criteria
| Criteria | Measurement | Target |
|----------|-------------|--------|
| Traces visible | LangWatch dashboard shows flow traces | 100% of test flows |
| Minimal changes | Lines of code modified | < 50 LOC |
| Config-based | Integration via environment/config | Yes |
| LLM calls captured | Individual LLM invocations traced | All providers used |

### POC Scope Boundaries
**In Scope:**
- Basic trace capture for flow execution
- LangWatch dashboard visualization
- Environment-based configuration
- Single flow execution tracing

**Out of Scope (Future):**
- Custom evaluations
- Alerting/monitoring
- Multi-tenant trace isolation
- Cost optimization features
- Production deployment patterns

---

## Technical Context

### Relevant Codebase Areas
From audit documentation:
- **Backend:** FastAPI (Python 3.12+)
- **LLM Integration:** `langbuilder/components/models/` (24 providers)
- **Flow Execution:** `langbuilder/graph/` module
- **Existing LangWatch:** `langbuilder/components/langwatch/`

### Integration Points
1. **Environment Configuration:** Add `LANGWATCH_API_KEY` to env vars
2. **LangChain Auto-Instrumentation:** Leverage existing LangChain integration
3. **Custom Hooks (Optional):** Add flow metadata to traces

---

## Risk Assessment (Preliminary)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LangWatch service availability | Low | Medium | Free tier has reasonable SLA |
| Performance overhead | Low | Low | Auto-instrumentation is lightweight |
| Data privacy concerns | Medium | Medium | Review what data is sent to LangWatch |
| Integration complexity higher than expected | Low | Medium | POC validates before commitment |

---

## Next Steps

1. **Problem Validation (Step 2):** Confirm problem statement and success criteria
2. **Gap Analysis (Step 5):** Identify specific integration points in codebase
3. **Technical Specification:** Detail exact configuration and code changes

---

## References

### Internal Documentation
- `.cg-aix-sdlc/docs/inventory/integration-map.md` - Current integrations
- `.cg-aix-sdlc/docs/architecture/system-architecture.md` - System overview
- `.cg-aix-sdlc/docs/product/feature-catalog.md` - Existing features

### External Documentation
- LangWatch Integration Guide: `integrations-langwatch.mdx`
- LangWatch Python SDK: `langwatch.py`, `service.py`

---

**Metadata:**
- change_request: langwatch-observability-poc
- step: 1-discovery-kickoff
- status: complete
- generated_at: 2026-01-21

*Generated by CloudGeometry AIx SDLC - Phase 1 (Reqs)*
