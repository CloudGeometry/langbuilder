# User Journeys

**Change Request:** langwatch-observability-poc
**Generated:** 2026-01-21
**Step:** 4c - User Journeys

---

## Overview

This document maps the key user journeys for the LangWatch observability integration, focusing on the Flow Developer persona (Alex) as the primary POC user.

---

## Journey 1: First-Time Setup

**Persona:** Alex (Flow Developer)
**Goal:** Configure LangWatch observability for LangBuilder
**Trigger:** Wants to enable tracing for their flows

### Journey Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FIRST-TIME SETUP JOURNEY                        │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┤
│  STAGE  │ Discover│  Sign Up │Configure│  Test   │    Confirm      │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ ACTIONS │ Learn   │ Create  │ Add env │ Run a   │ View trace      │
│         │ about   │ LangWat │ variable│ simple  │ in dashboard    │
│         │ LangWatch│ account │ to env  │ flow    │                 │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ EMOTION │ Curious │ Hopeful │ Confident│ Excited │ Satisfied       │
│         │  😮     │   🤞    │   😊    │   🤔    │     ✅          │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ TOUCH-  │ Docs    │LangWatch│.env file│LangBuild│ LangWatch       │
│ POINTS  │         │ website │         │ UI      │ dashboard       │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
```

### Detailed Steps

| Step | Action | System Response | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Read setup documentation | N/A | Understands requirements |
| 2 | Sign up at langwatch.ai | Account created | API key received |
| 3 | Add `LANGWATCH_API_KEY` to environment | N/A | Variable set |
| 4 | Restart LangBuilder backend | Auto-instrumentation activates | No errors |
| 5 | Run any existing flow | Trace sent to LangWatch | 200 OK response |
| 6 | Open LangWatch dashboard | Trace visible | Sees flow execution |

### Time Expectation
- Total setup time: < 5 minutes
- No code changes required

---

## Journey 2: Debug Failed Flow

**Persona:** Alex (Flow Developer)
**Goal:** Find and fix an error in their AI workflow
**Trigger:** Flow returns an error or unexpected result

### Journey Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEBUG FAILED FLOW JOURNEY                        │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┤
│  STAGE  │ Run Flow│ See Err │Open Dash│Find Issue│   Fix Flow      │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ ACTIONS │ Execute │ Notice  │ Navigate│ Drill   │ Update flow     │
│         │ flow in │ failure │ to Lang │ into    │ based on        │
│         │LangBuild│ message │ Watch   │ trace   │ findings        │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ EMOTION │ Hopeful │Frustrated│Determined│ Relieved│ Satisfied      │
│         │   🤞    │   😤    │   🔍   │   😮   │     ✅          │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│PAIN     │         │ What    │         │ Where   │                 │
│POINTS   │         │ happened│         │ exactly?│                 │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
```

### Detailed Steps

| Step | Action | System Response | User Sees |
|------|--------|-----------------|-----------|
| 1 | Run flow in LangBuilder | Flow executes, fails | Error message |
| 2 | Open LangWatch dashboard | Trace loaded | Recent traces list |
| 3 | Click on failed trace | Trace detail view | Visual flow diagram |
| 4 | Identify red/error step | Step highlighted | Error details |
| 5 | View step input/output | Expand step | Exact data |
| 6 | Return to LangBuilder | N/A | Knows what to fix |

### Key Insights Gained
- Which step failed
- What input caused the failure
- Error message and context
- Previous steps' outputs

---

## Journey 3: Optimize Prompts

**Persona:** Alex (Flow Developer)
**Goal:** Improve LLM prompt quality based on trace data
**Trigger:** Flow produces suboptimal results

### Journey Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPTIMIZE PROMPTS JOURNEY                         │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┤
│  STAGE  │ Run Flow│Review Out│View Trace│Analyze  │   Iterate       │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ ACTIONS │ Execute │ Check   │ Open LW │ Read    │ Modify prompt   │
│         │ flow    │ quality │ trace   │ prompts │ Re-run flow     │
│         │         │ of output│        │ sent    │                 │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ EMOTION │ Hopeful │Disappointed│Curious │Insightful│ Progressive    │
│         │   🤞    │   😕    │   🔍   │   💡   │     📈          │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ VALUE   │         │         │ See     │Understand│ Better         │
│         │         │         │ reality │ problem │ results        │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
```

### Detailed Steps

| Step | Action | User Learns | Next Action |
|------|--------|-------------|-------------|
| 1 | Run flow with test input | Output quality | Proceed to trace |
| 2 | Open trace in LangWatch | Execution path | Find LLM steps |
| 3 | Expand LLM step | Exact prompt sent | Analyze prompt |
| 4 | Review system prompt | How it's structured | Identify improvements |
| 5 | Review user prompt | Context provided | Identify gaps |
| 6 | Review response | What LLM returned | Understand failure mode |
| 7 | Modify prompt in LangBuilder | N/A | Re-run flow |
| 8 | Compare traces | Before/after | Validate improvement |

---

## Journey 4: Track Execution Costs

**Persona:** Alex (Flow Developer)
**Goal:** Understand token usage and costs
**Trigger:** Wants to optimize or report on LLM costs

### Journey Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRACK COSTS JOURNEY                              │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┤
│  STAGE  │ Run Flow│Open Trace│View Token│Identify │   Optimize      │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ ACTIONS │ Execute │ Navigate│ Check   │ Find    │ Adjust model    │
│         │ flow    │ to LW   │ token   │ expensive│ or prompt      │
│         │         │         │ counts  │ steps   │                 │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ INFO    │         │         │ Tokens: │ Step X: │ Now using      │
│ GAINED  │         │         │ 1,234   │ 800 tok │ 50% fewer      │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
```

### Token Visibility Points

| Location | Data Shown | User Value |
|----------|------------|------------|
| Trace overview | Total tokens | Quick cost sense |
| Step detail | Input/output tokens | Identify expensive steps |
| LLM step | Model used + tokens | Compare models |

---

## Journey 5: Validate Before Deploy

**Persona:** Alex (Flow Developer)
**Goal:** Confirm flow works correctly before production
**Trigger:** Finished building a new flow

### Journey Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDATE FLOW JOURNEY                            │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┤
│  STAGE  │Build Flow│Test Cases│Run Tests│Review   │   Approve       │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ ACTIONS │ Complete│ Define  │ Execute │ Check   │ Deploy with     │
│         │ flow    │ test    │ each    │ traces  │ confidence      │
│         │ design  │ inputs  │ case    │         │                 │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┤
│ EVIDENCE│         │         │         │ All     │ Traces prove    │
│         │         │         │         │ green   │ correctness     │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
```

---

## Journey Comparison Matrix

| Journey | Frequency | Complexity | POC Coverage |
|---------|-----------|------------|--------------|
| First-Time Setup | Once | Low | Full |
| Debug Failed Flow | Daily | Medium | Full |
| Optimize Prompts | Weekly | Medium | Full |
| Track Costs | Weekly | Low | Partial |
| Validate Before Deploy | Per release | Medium | Partial |

---

## Happy Path Summary

### POC Happy Path

```
1. Developer adds LANGWATCH_API_KEY to environment
                    │
                    ▼
2. Developer runs a flow in LangBuilder
                    │
                    ▼
3. Trace automatically sent to LangWatch
                    │
                    ▼
4. Developer opens LangWatch dashboard
                    │
                    ▼
5. Developer sees visual trace with:
   - All steps executed
   - LLM prompts and responses
   - Token counts
   - Timing data
                    │
                    ▼
6. Developer gains insights to improve flow
```

---

## Error Paths

### Setup Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| No traces appear | Missing API key | Check env var set |
| Auth error | Invalid API key | Get new key from LangWatch |
| Network error | Firewall/proxy | Check connectivity |

### Runtime Errors

| Error | Cause | Impact |
|-------|-------|--------|
| Partial trace | Flow error mid-execution | Trace shows up to error |
| Missing LLM data | Non-LangChain LLM | Manual instrumentation needed |

---

## Journey Metrics

### POC Success Metrics

| Journey | Metric | Target |
|---------|--------|--------|
| First-Time Setup | Time to first trace | < 5 min |
| Debug Failed Flow | Time to identify issue | < 5 min |
| Optimize Prompts | Prompts visible | 100% |
| Track Costs | Token data available | Yes |

---

**Metadata:**
- change_request: langwatch-observability-poc
- step: 4c-user-journeys
- status: complete
- generated_at: 2026-01-21

*Generated by CloudGeometry AIx SDLC - Phase 1 (Reqs)*
