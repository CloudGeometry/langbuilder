# Jobs-to-be-Done (JTBD)

**Change Request:** langwatch-observability-poc
**Generated:** 2026-01-21
**Step:** 4a - Jobs-to-be-Done

---

## Overview

This document identifies the core jobs that users are trying to accomplish when they need AI workflow observability in LangBuilder.

---

## Primary Jobs

### Job 1: Debug AI Workflow Execution

**Job Statement:**
> When I run an AI workflow flow, I want to see what happened at each step so I can identify and fix issues in my flow logic.

| Attribute | Value |
|-----------|-------|
| Job Type | Functional |
| Priority | High |
| Frequency | Every development session |
| Current Solution | Manual logging, print statements |
| Pain Level | High |

**Desired Outcomes:**
1. See the sequence of operations executed
2. View inputs/outputs at each step
3. Identify where errors occurred
4. Understand branching/conditional paths taken

**Success Metrics:**
- Time to identify issue location: < 2 minutes
- Steps visible in trace: 100%
- Error context available: Yes

---

### Job 2: Understand LLM Behavior

**Job Statement:**
> When my AI workflow produces unexpected results, I want to see the exact prompts sent to LLMs and responses received so I can improve my prompts.

| Attribute | Value |
|-----------|-------|
| Job Type | Functional |
| Priority | High |
| Frequency | Multiple times per session |
| Current Solution | Add logging around LLM calls |
| Pain Level | High |

**Desired Outcomes:**
1. View exact prompt text sent to LLM
2. See complete LLM response
3. Compare prompts across multiple runs
4. Identify prompt patterns that work/fail

**Success Metrics:**
- Prompt text visibility: 100%
- Response visibility: 100%
- Able to compare runs: Yes

---

### Job 3: Track Token Usage and Costs

**Job Statement:**
> When running AI workflows, I want to know how many tokens each execution uses so I can optimize costs and stay within budget.

| Attribute | Value |
|-----------|-------|
| Job Type | Functional |
| Priority | Medium |
| Frequency | Weekly/Monthly review |
| Current Solution | Manual provider dashboard checks |
| Pain Level | Medium |

**Desired Outcomes:**
1. See token count per LLM call
2. View estimated cost per execution
3. Aggregate costs across runs
4. Identify expensive operations

**Success Metrics:**
- Token count accuracy: Within 5%
- Cost estimation available: Yes
- Per-call breakdown: Yes

---

### Job 4: Monitor Execution Performance

**Job Statement:**
> When my AI workflow runs slowly, I want to see timing data for each step so I can identify and optimize bottlenecks.

| Attribute | Value |
|-----------|-------|
| Job Type | Functional |
| Priority | Medium |
| Frequency | During optimization |
| Current Solution | Timestamp logging |
| Pain Level | Medium |

**Desired Outcomes:**
1. See duration of each step
2. Identify slowest operations
3. Compare timing across runs
4. Track latency trends

**Success Metrics:**
- Timing precision: Millisecond level
- Bottleneck identification: Clear visual
- Historical comparison: Available

---

## Secondary Jobs

### Job 5: Validate Flow Correctness

**Job Statement:**
> After building a new flow, I want to verify it executes as designed before deploying to production.

| Attribute | Value |
|-----------|-------|
| Job Type | Functional |
| Priority | Medium |
| Frequency | After flow changes |
| Current Solution | Test runs with inspection |
| Pain Level | Low-Medium |

---

### Job 6: Share Execution Context

**Job Statement:**
> When collaborating with team members, I want to share a trace of what happened so we can discuss issues together.

| Attribute | Value |
|-----------|-------|
| Job Type | Social |
| Priority | Low |
| Frequency | As needed |
| Current Solution | Screenshots, copy-paste logs |
| Pain Level | Low |

---

## Job Prioritization Matrix

```
                    High Frequency
                          │
    Job 1: Debug          │        Job 2: LLM Behavior
    (Critical)            │        (Critical)
                          │
    ──────────────────────┼──────────────────────
                          │
    Job 4: Performance    │        Job 3: Costs
    (Nice to have)        │        (Important)
                          │
                    Low Frequency
                          │
              Low Pain ◄──┴──► High Pain
```

---

## Job Stories

### Job Story 1: Debugging a Failed Flow
```
WHEN I run my customer support flow and it returns an error
I WANT TO see exactly which step failed and why
SO THAT I can fix the issue quickly and get back to development
```

**Acceptance Criteria:**
- Error step highlighted in trace
- Error message visible
- Input to failed step visible
- Stack trace or context available

---

### Job Story 2: Optimizing Prompt Quality
```
WHEN my flow produces low-quality responses
I WANT TO see the exact prompts being sent
SO THAT I can iterate on prompt engineering
```

**Acceptance Criteria:**
- Full prompt text visible
- System/user/assistant message separation
- Response quality visible
- Easy to copy prompt for editing

---

### Job Story 3: Understanding Cost Impact
```
WHEN I'm evaluating whether to use GPT-4 vs GPT-3.5
I WANT TO see the token/cost difference
SO THAT I can make informed model selection decisions
```

**Acceptance Criteria:**
- Token count per model call
- Cost estimate displayed
- Comparison across models visible

---

## JTBD Hierarchy

```
Main Job: Successfully build and operate AI workflows
    │
    ├─► Core Job: Understand workflow execution
    │       │
    │       ├─► Job 1: Debug execution (Critical)
    │       └─► Job 2: Understand LLM behavior (Critical)
    │
    ├─► Supporting Job: Optimize workflows
    │       │
    │       ├─► Job 3: Track costs (Important)
    │       └─► Job 4: Monitor performance (Nice-to-have)
    │
    └─► Collaborative Job: Team workflow development
            │
            ├─► Job 5: Validate correctness (Important)
            └─► Job 6: Share context (Nice-to-have)
```

---

## POC Scope Mapping

### Jobs Addressed by POC

| Job | POC Coverage | Notes |
|-----|--------------|-------|
| Job 1: Debug | Full | Core LangWatch functionality |
| Job 2: LLM Behavior | Full | Auto-captured by LangWatch |
| Job 3: Costs | Partial | Token tracking included |
| Job 4: Performance | Partial | Timing visible in traces |
| Job 5: Validate | Partial | Manual trace inspection |
| Job 6: Share | Minimal | Dashboard links sharable |

### Jobs Deferred

| Job | Why Deferred |
|-----|--------------|
| Advanced cost analytics | Out of POC scope |
| Team collaboration features | Production feature |
| Automated validation | Requires evaluation setup |

---

## Competing Solutions by Job

| Job | Current Solution | LangWatch Solution | Improvement |
|-----|------------------|-------------------|-------------|
| Debug | Manual logging | Visual trace | Significant |
| LLM Behavior | Print statements | Auto-capture | Significant |
| Costs | Provider dashboards | In-trace costs | Moderate |
| Performance | Timestamps | Visual timeline | Moderate |

---

**Metadata:**
- change_request: langwatch-observability-poc
- step: 4a-jobs-to-be-done
- status: complete
- generated_at: 2026-01-21

*Generated by CloudGeometry AIx SDLC - Phase 1 (Reqs)*
