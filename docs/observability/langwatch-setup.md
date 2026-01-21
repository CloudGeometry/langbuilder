# LangWatch Observability Setup

LangWatch provides tracing and observability for LangBuilder flows, enabling you to monitor LLM calls, debug issues, and track costs.

## Overview

LangBuilder includes built-in integration with [LangWatch](https://langwatch.ai), an AI observability platform. When enabled, LangWatch automatically captures:

- **Flow execution traces** - Complete execution path with timing
- **LLM prompts and responses** - Full prompt/completion text
- **Token usage and costs** - Track spending across models
- **Error context** - Debug failures with full context
- **Component-level spans** - See each component's inputs/outputs

## Prerequisites

- LangBuilder instance (local or deployed)
- LangWatch account (free tier available at [app.langwatch.ai](https://app.langwatch.ai))

## Quick Start (5 minutes)

### 1. Create LangWatch Account

1. Go to [app.langwatch.ai](https://app.langwatch.ai)
2. Click **Sign Up** and create your account
3. Verify your email if required

### 2. Create Project and Get API Key

1. After signing in, create a new project (e.g., "LangBuilder")
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the generated key (starts with `lw_`)

### 3. Configure LangBuilder

Set the `LANGWATCH_API_KEY` environment variable:

**Linux/macOS:**
```bash
export LANGWATCH_API_KEY=lw_your_api_key_here
```

**Windows (Command Prompt):**
```cmd
set LANGWATCH_API_KEY=lw_your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:LANGWATCH_API_KEY="lw_your_api_key_here"
```

**Docker:**
```yaml
services:
  langbuilder:
    environment:
      - LANGWATCH_API_KEY=lw_your_api_key_here
```

### 4. Restart LangBuilder

Restart your LangBuilder backend to apply the configuration.

### 5. Verify Setup

1. Run any flow in LangBuilder
2. Go to your LangWatch dashboard
3. Click **Traces** - you should see your flow execution

## Configuration Reference

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `LANGWATCH_API_KEY` | Yes | None | Your LangWatch API key (starts with `lw_`) |
| `LANGWATCH_ENDPOINT` | No | `https://app.langwatch.ai` | Custom LangWatch endpoint (for self-hosted) |
| `LANGCHAIN_PROJECT` | No | `Langbuilder` | Project name shown in LangWatch |

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       LangBuilder                            │
│                                                             │
│  ┌─────────────┐    ┌───────────────┐    ┌──────────────┐  │
│  │    Flow     │───▶│TracingService │───▶│LangWatchTracer│ │
│  │  Execution  │    │               │    │              │  │
│  └─────────────┘    └───────────────┘    └───────┬──────┘  │
│                                                   │         │
└───────────────────────────────────────────────────┼─────────┘
                                                    │
                                                    │ HTTPS
                                                    ▼
                                          ┌─────────────────┐
                                          │  LangWatch API  │
                                          │ app.langwatch.ai│
                                          └─────────────────┘
```

### What Data is Sent

| Data Type | Sent | Example |
|-----------|------|---------|
| Flow name | ✅ | "My Chat Flow" |
| Component names | ✅ | "OpenAI Chat", "Prompt Template" |
| Component inputs | ✅ | User messages, prompt variables |
| Component outputs | ✅ | LLM responses, processed data |
| LLM prompts | ✅ | Full prompt text sent to model |
| LLM responses | ✅ | Full completion text from model |
| Token usage | ✅ | Input tokens, output tokens |
| Execution timing | ✅ | Start time, duration |
| Errors | ✅ | Exception messages and context |
| Session IDs | ✅ | For conversation threading |

### What Data is NOT Sent

| Data Type | Reason |
|-----------|--------|
| API keys | Masked with `*****` before transmission |
| Database credentials | Not captured in traces |
| System file paths | Not included in trace data |
| User authentication tokens | Not in trace context |

## Privacy Considerations

- **All data is transmitted over HTTPS**
- **API keys in component inputs are automatically masked**
- **LangWatch's data retention policies apply** - see [LangWatch Privacy Policy](https://langwatch.ai/privacy)
- **Consider your data sensitivity** before enabling in production

For sensitive workloads, consider:
- Using LangWatch's data masking features
- Self-hosting LangWatch (Enterprise)
- Reviewing traces before enabling in production

## Using the Dashboard

### Viewing Traces

1. Go to your LangWatch project
2. Click **Traces** in the sidebar
3. Each row is a flow execution
4. Click a trace to expand and see spans

### Understanding Spans

Traces are organized as spans:
- **Root span**: The entire flow execution
- **Component spans**: Each component in the flow
- **LLM spans**: Detailed LLM calls with prompts/responses

### Filtering and Search

- Filter by time range, status, or tags
- Search by flow name or content
- Group by session for conversation views

### Cost Tracking

- View token usage per trace
- See cost estimates by model
- Export usage reports

## Troubleshooting

### Traces Not Appearing

**Check API Key:**
```bash
echo $LANGWATCH_API_KEY
# Should print: lw_xxxxxxxx
```

**Check LangBuilder Logs:**
Look for LangWatch initialization messages or errors.

**Verify Network:**
```bash
curl -I https://app.langwatch.ai
# Should return 200 OK
```

### "SDK Not Found" Error

Install the LangWatch SDK:
```bash
pip install langwatch
```

### Connection Errors

**Firewall:** Ensure outbound HTTPS (port 443) to `app.langwatch.ai` is allowed.

**Proxy:** If behind a proxy, configure standard `HTTPS_PROXY` environment variable.

### Performance Concerns

LangWatch uses async, non-blocking trace collection:
- Traces are buffered and sent in batches
- Flow execution is not blocked by tracing
- Expected overhead: < 50ms per flow

If experiencing issues:
1. Check network latency to LangWatch
2. Verify no errors in logs
3. Consider LangWatch's rate limits (varies by plan)

### Disabling Tracing

To temporarily disable LangWatch:
```bash
unset LANGWATCH_API_KEY
```

Then restart LangBuilder. Flows will continue working normally without tracing.

## Advanced Configuration

### Using with Other Tracers

LangBuilder supports multiple observability platforms simultaneously:
- LangWatch
- LangSmith
- LangFuse
- Arize Phoenix
- Opik

Each tracer is independent - configure any combination via their respective environment variables.

### Custom Endpoint (Self-Hosted)

For self-hosted LangWatch:
```bash
export LANGWATCH_ENDPOINT=https://your-langwatch-instance.com
export LANGWATCH_API_KEY=lw_your_key
```

### Project Naming

Set a custom project name:
```bash
export LANGCHAIN_PROJECT="My Production App"
```

## FAQ

**Q: Is LangWatch required to run LangBuilder?**
A: No. LangWatch is optional. Flows work normally without it configured.

**Q: What happens if LangWatch is unavailable?**
A: Flows continue executing. Tracing gracefully degrades - you'll just miss traces during the outage.

**Q: Can I use LangWatch's evaluations?**
A: Yes! LangBuilder includes a LangWatch Evaluator component for running evaluations within flows.

**Q: How much does LangWatch cost?**
A: LangWatch offers a free tier (10,000 traces/month). See [langwatch.ai/pricing](https://langwatch.ai/pricing) for details.

**Q: Is my data secure?**
A: Data is encrypted in transit (HTTPS). API keys are masked. Review LangWatch's security documentation for details.

## Support

- **LangWatch Documentation:** [docs.langwatch.ai](https://docs.langwatch.ai)
- **LangWatch Support:** Contact through their dashboard
- **LangBuilder Issues:** GitHub issues

---

*Last updated: 2026-01-21*
