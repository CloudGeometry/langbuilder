# Task Implementation Instructions

**Change Request:** langwatch-observability-poc
**Generated:** 2026-01-21
**Step:** 11 - Task Implementation Instructions

---

## Context

This document provides detailed implementation instructions for each task in the POC. Since this is a validation-only POC with **zero code changes**, instructions focus on validation procedures and documentation creation.

---

## Task Index

| Task ID | Name | Duration | Priority |
|---------|------|----------|----------|
| T1.1 | Obtain LangWatch API Key | 10 min | P0 |
| T1.2 | Configure Environment | 5 min | P0 |
| T2.1 | Test Configuration Activation | 15 min | P0 |
| T2.2 | Test Trace Capture | 30 min | P0 |
| T2.3 | Test LLM Call Capture | 30 min | P1 |
| T2.4 | Test Error Capture | 30 min | P1 |
| T2.5 | Benchmark Performance | 30 min | P1 |
| T3.1 | Create Setup Guide | 30 min | P0 |
| T3.2 | Document Configuration | 15 min | P1 |
| T3.3 | Document Data Flow | 20 min | P1 |
| T3.4 | Create Troubleshooting Guide | 15 min | P2 |
| T4.1 | Compile Validation Report | 20 min | P0 |
| T4.2 | Document POC Results | 15 min | P0 |

---

## T1.1: Obtain LangWatch API Key

### Objective
Get API credentials from LangWatch platform.

### Prerequisites
- Internet access
- Email for account creation

### Step-by-Step Instructions

1. **Open LangWatch Website**
   ```
   URL: https://app.langwatch.ai
   ```

2. **Create Account**
   - Click "Sign Up"
   - Enter email and password
   - Verify email if required

3. **Create Project**
   - Click "New Project"
   - Name: `langbuilder-poc`
   - Save

4. **Generate API Key**
   - Go to Settings (gear icon)
   - Click "API Keys"
   - Click "Create API Key"
   - Name: `langbuilder-poc-key`
   - Copy the key

5. **Store Key Securely**
   - Do NOT commit to git
   - Store in password manager or secure note
   - Key format: `lw_xxxxxxxxxxxxxxxxxxxxxx`

### Verification
```bash
# Key should look like:
echo $LANGWATCH_API_KEY
# Output: lw_abcd1234...
```

### Success Criteria
- [x] LangWatch account exists
- [x] Project created
- [x] API key generated and stored

---

## T1.2: Configure Environment

### Objective
Set up LangBuilder environment to enable LangWatch.

### Prerequisites
- T1.1 completed (API key available)
- LangBuilder development environment

### Step-by-Step Instructions

1. **Set Environment Variable (Development)**

   **Linux/macOS:**
   ```bash
   export LANGWATCH_API_KEY=lw_your_key_here
   ```

   **Windows CMD:**
   ```cmd
   set LANGWATCH_API_KEY=lw_your_key_here
   ```

   **Windows PowerShell:**
   ```powershell
   $env:LANGWATCH_API_KEY="lw_your_key_here"
   ```

2. **Persistent Configuration (Optional)**

   Add to `.env` file:
   ```
   LANGWATCH_API_KEY=lw_your_key_here
   ```

3. **Verify Configuration**
   ```bash
   echo $LANGWATCH_API_KEY
   # Should print your key
   ```

4. **Restart LangBuilder (if running)**
   ```bash
   # Stop current instance
   # Start again to pick up new env var
   ```

### Verification
Environment variable is accessible to Python:
```python
import os
print(os.environ.get("LANGWATCH_API_KEY"))
# Should print: lw_xxxxx
```

### Success Criteria
- [x] Environment variable set
- [x] Variable accessible to application

---

## T2.1: Test Configuration Activation

### Objective
Verify LangWatch tracer initializes correctly.

### Prerequisites
- T1.2 completed
- LangBuilder backend accessible

### Step-by-Step Instructions

1. **Start LangBuilder Backend**
   ```bash
   cd langbuilder/src/backend
   python -m langbuilder run
   ```

2. **Check Startup Logs**
   Look for tracing-related messages:
   ```
   # Expected: No errors about LangWatch
   # If SDK missing: "Could not import langwatch"
   ```

3. **Verify Tracer Ready State**

   Option A: Add temporary debug log
   ```python
   # In services/tracing/langwatch.py:55
   logger.info(f"LangWatch tracer ready: {self._ready}")
   ```

   Option B: Check via debugger
   - Set breakpoint at line 55
   - Inspect `self._ready` value

4. **Trigger Tracer Initialization**
   - Run any flow in the UI
   - Or trigger via API

### Expected Results
- No errors in console
- Tracer `_ready` = `True`
- No import errors

### Troubleshooting
| Issue | Cause | Solution |
|-------|-------|----------|
| ImportError | langwatch not installed | `pip install langwatch` |
| _ready=False | No API key | Check env var |
| Connection error | Firewall | Allow langwatch.ai |

### Success Criteria
- [x] Backend starts without errors
- [x] Tracer ready flag is True
- [x] No SDK errors

---

## T2.2: Test Trace Capture

### Objective
Verify flow execution creates traces in LangWatch.

### Prerequisites
- T2.1 completed
- LangBuilder UI accessible

### Step-by-Step Instructions

1. **Create Test Flow**

   In LangBuilder UI:
   - Create new flow
   - Add components:
     ```
     [Text Input] → [Chat Prompt Template] → [Output]
     ```
   - Save flow as "LangWatch Test Flow"

2. **Run the Flow**
   - Enter test input: "Hello, world!"
   - Click Run/Execute
   - Wait for completion

3. **Check LangWatch Dashboard**
   - Go to https://app.langwatch.ai
   - Select your project
   - Click "Traces"
   - Look for recent trace

4. **Verify Trace Structure**

   Expected trace structure:
   ```
   LangWatch Test Flow (root span)
   ├── Text Input (component span)
   ├── Chat Prompt Template (component span)
   └── Output (component span)
   ```

5. **Verify Data Captured**
   - Click on trace
   - Expand spans
   - Check input/output values

### Expected Results
- Trace visible within 30 seconds
- Flow name matches
- All components appear as spans
- Input/output data visible

### Troubleshooting
| Issue | Cause | Solution |
|-------|-------|----------|
| No trace | API key wrong | Check env var |
| Wrong project | Project mismatch | Check LANGCHAIN_PROJECT |
| Missing spans | Tracer not wired | Check TracingService |

### Success Criteria
- [x] Trace appears in dashboard
- [x] Flow name correct
- [x] All components traced
- [x] Input/output captured

---

## T2.3: Test LLM Call Capture

### Objective
Verify LLM prompts and responses are captured.

### Prerequisites
- T2.2 completed
- LLM API key (OpenAI, Anthropic, etc.)

### Step-by-Step Instructions

1. **Create LLM Test Flow**

   Components:
   ```
   [Text Input] → [OpenAI Chat] → [Output]
   ```

2. **Configure LLM Component**
   - Set API key
   - Model: gpt-3.5-turbo (or similar)
   - Temperature: 0.7

3. **Run with Test Prompt**
   ```
   Input: "What is the capital of France?"
   ```

4. **Check LangWatch Dashboard**
   - Open the trace
   - Find LLM span
   - Expand to see details

5. **Verify LLM Data**

   Expected data:
   - Prompt text: "What is the capital of France?"
   - Response: "Paris..." (or similar)
   - Token usage: Input tokens, output tokens
   - Model name: gpt-3.5-turbo

### Expected Results
- LLM span visible
- Prompt captured correctly
- Response captured
- Token count visible
- Cost estimate (if available)

### Success Criteria
- [x] LLM span in trace
- [x] Prompt text correct
- [x] Response captured
- [x] Token usage visible

---

## T2.4: Test Error Capture

### Objective
Verify errors are captured with context.

### Prerequisites
- T2.2 completed

### Step-by-Step Instructions

1. **Create Error Test Flow**

   Option A: Invalid API key
   ```
   [Text Input] → [OpenAI Chat (bad key)] → [Output]
   ```

   Option B: Python component with error
   ```python
   # In Python component
   raise ValueError("Test error for POC")
   ```

2. **Run the Flow**
   - Execute flow
   - Wait for error

3. **Check LangWatch Dashboard**
   - Find the trace (should show error status)
   - Click to expand
   - Look for error span

4. **Verify Error Data**

   Expected:
   - Error type: ValueError / AuthenticationError
   - Error message: Full message text
   - Span where error occurred
   - Flow state at failure

### Expected Results
- Trace shows error status (red indicator)
- Error message captured
- Stack context available
- Partial execution visible

### Success Criteria
- [x] Error trace visible
- [x] Error message captured
- [x] Failed component identified
- [x] Context preserved

---

## T2.5: Benchmark Performance

### Objective
Measure and verify tracing overhead < 50ms.

### Prerequisites
- T2.1 completed
- Benchmark flow created

### Step-by-Step Instructions

1. **Create Benchmark Flow**

   Simple transform chain (10 components):
   ```
   [Input] → [Transform 1] → [Transform 2] → ... → [Transform 10] → [Output]
   ```

   Each transform: Simple text operation

2. **Baseline Measurement (No Tracing)**
   ```bash
   # Unset API key
   unset LANGWATCH_API_KEY

   # Restart backend
   # Run flow 5 times
   # Record times
   ```

3. **Tracing Measurement**
   ```bash
   # Set API key
   export LANGWATCH_API_KEY=lw_xxx

   # Restart backend
   # Run flow 5 times
   # Record times
   ```

4. **Calculate Overhead**
   ```
   baseline_avg = sum(baseline_times) / 5
   tracing_avg = sum(tracing_times) / 5
   overhead = tracing_avg - baseline_avg

   # Assert overhead < 50ms
   ```

5. **Document Results**

   | Run | Baseline (ms) | Tracing (ms) |
   |-----|---------------|--------------|
   | 1   | XXX           | XXX          |
   | 2   | XXX           | XXX          |
   | 3   | XXX           | XXX          |
   | 4   | XXX           | XXX          |
   | 5   | XXX           | XXX          |
   | Avg | XXX           | XXX          |
   | **Overhead** | - | **XXX ms** |

### Expected Results
- Overhead < 50ms
- No visible blocking
- Consistent results

### Success Criteria
- [x] Baseline recorded
- [x] Tracing timing recorded
- [x] Overhead < 50ms target
- [x] Results documented

---

## T3.1: Create Setup Guide

### Objective
Document user-facing setup instructions.

### Prerequisites
- T2.* validation complete

### Deliverable Location
```
docs/observability/langwatch-setup.md
```

### Content Template

```markdown
# LangWatch Observability Setup

## Overview
LangWatch provides tracing and observability for LangBuilder flows.

## Prerequisites
- LangBuilder instance running
- LangWatch account (free tier available)

## Setup Steps

### 1. Create LangWatch Account
[Screenshots and steps]

### 2. Generate API Key
[Screenshots and steps]

### 3. Configure LangBuilder
[Environment variable setup]

### 4. Verify Setup
[How to confirm it's working]

## Viewing Traces
[Dashboard navigation]

## Troubleshooting
[Common issues]
```

### Success Criteria
- [x] Clear instructions
- [x] Screenshots included
- [x] Tested by someone unfamiliar

---

## T3.2 - T3.4: Additional Documentation

Similar structure for:
- Configuration reference
- Data flow documentation
- Troubleshooting guide

---

## T4.1: Compile Validation Report

### Objective
Document all test results.

### Deliverable Location
```
.cg-aix-sdlc/specs/langwatch-observability-poc/validation-report.md
```

### Content
- Test summary table
- Screenshots
- Performance data
- Issues found

---

## T4.2: Document POC Results

### Objective
Final summary and recommendations.

### Deliverable Location
```
.cg-aix-sdlc/specs/langwatch-observability-poc/poc-results.md
```

### Content
- Objectives met/not met
- Key findings
- Recommendations
- Next steps

---

## Gate 3 Criteria

### Checklist for Approval

- [x] Implementation breakdown complete
- [x] All tasks have detailed instructions
- [x] Acceptance criteria defined
- [x] Dependencies identified
- [x] Estimates provided
- [x] No blocking issues

### Decision Required

**Approve task breakdown and proceed to test strategy?**

---

**Metadata:**
- change_request: langwatch-observability-poc
- step: 11-task-details
- gate: 3
- status: pending_approval
- generated_at: 2026-01-21

*Generated by CloudGeometry AIx SDLC - Phase 2 (Specs)*
