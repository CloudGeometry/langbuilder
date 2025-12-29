# Component Fixes for Content Engine

This document captures the corrections needed for CloudGeometry custom components that were implemented with shortcuts.

---

## Summary of Changes

| Component | Action | Reason |
|-----------|--------|--------|
| Pain Point Mapper | **REMOVE** | Unnecessary - logic moves to prompt |
| Contact Info Extractor | **REWRITE** | Regex too brittle - use LLM via flow |

---

## 1. Pain Point Mapper - REMOVE ENTIRELY

### Why Remove It

The Pain Point Mapper was a hardcoded dictionary with 150 entries mapping `(role, industry, service_type)` to static pain point strings. This was:

1. **Inflexible** - Only worked with 5 predefined industries and 5 roles
2. **Unmaintainable** - Adding one industry required 30 new entries
3. **Unnecessary** - The flow already calls OpenAI for the executive summary

### The Fix

Remove the component from the flow. Instead, enhance the executive summary prompt to include pain point identification:

**Before (with Pain Point Mapper):**
```
Flow: [Pain Point Mapper] → pain_point → [Prompt Template] → [OpenAI]

Prompt: "Write an executive summary. Their primary concern is {pain_point}."
```

**After (no Pain Point Mapper):**
```
Flow: [Merge Lead Data] → [Prompt Template] → [OpenAI]

Prompt: (see below)
```

### New Executive Summary Prompt

```
You are a B2B cloud services expert writing an executive summary for a personalized PDF report.

TARGET AUDIENCE:
- Name: {lead_name}
- Role: {role}
- Company: {company_name}
- Industry: {industry}
- Service Interest: {service_type}
- Annual Cloud Spend: {annual_cloud_spend}

INSTRUCTIONS:
1. First, identify the #1 business pain point for a {role} in the {industry} industry regarding {service_type}. Consider:
   - Industry-specific regulations (HIPAA for healthcare, PCI-DSS for finance, SOX for public companies)
   - Role-specific concerns (CFO: costs/ROI, CTO: architecture/security, VP Eng: velocity/reliability)
   - Service-specific challenges

2. Then write a 3-4 sentence executive summary that:
   - Opens with a hook relevant to their industry
   - Addresses their specific pain point
   - Connects {service_type} benefits to their situation
   - References their potential savings of {calculated_savings}

Write in a consultative, professional tone. Be specific to BOTH their service interest AND industry context.
```

### Benefits

1. **One LLM call** instead of hardcoded lookup + LLM call
2. **Any industry works** - AI understands "Education", "Government", "Non-profit", etc.
3. **Any role works** - "Chief Financial Officer", "CFO", "Finance VP" all work
4. **Better quality** - AI generates contextually relevant pain points, not canned phrases
5. **No maintenance** - No dictionary to update when targeting new industries

### Files to Delete

```
langbuilder/src/backend/base/langbuilder/components/cloudgeometry/pain_point_mapper.py
```

### Flow Changes

1. Remove the Pain Point Mapper node from the flow
2. Remove edges connecting to/from Pain Point Mapper
3. Update the Prompt Template with the new prompt above
4. Connect Merge Lead Data directly to the Prompt Template

---

## 2. Contact Info Extractor - REWRITE TO USE FLOW

### The Problem

Current implementation uses regex that only matches the keyword "about":

```python
topic_match = re.search(r"\babout\s+(.+)$", text, re.IGNORECASE)
```

This fails on natural variations:
- "Ken regarding AI Transformation" - FAILS
- "Ken - AI Transformation" - FAILS
- "email Ken on cloud migration" - FAILS
- "Ken, topic: DevOps" - FAILS

### The Fix

Instead of embedding OpenAI calls in the component (wrong), redesign as a flow pattern:

**New Architecture:**

```
[User Input] → [Contact Info Prompt Builder] → [OpenAI] → [Parse JSON] → [Rest of Flow]
```

### New Component: Contact Info Prompt Builder

This component outputs a prompt (not a result). The prompt gets processed by the flow's OpenAI component.

```python
"""
Contact Info Prompt Builder - LangBuilder Custom Component

Builds a prompt for extracting contact info from natural language.
The prompt is processed by the flow's OpenAI component.
"""

from langbuilder.custom import Component
from langbuilder.io import MessageTextInput, Output
from langbuilder.schema import Data


class ContactInfoPromptBuilder(Component):
    """
    Builds an extraction prompt for the flow's LLM to process.

    This component does NOT call OpenAI directly. It outputs a prompt
    that should be connected to an OpenAI component in the flow.
    """

    display_name = "Contact Info Prompt Builder"
    description = "Builds prompt for AI extraction of contact info from natural language"
    icon = "users"
    name = "ContactInfoPromptBuilder"

    inputs = [
        MessageTextInput(
            name="text_input",
            display_name="Text Input",
            required=True,
            info="Natural language input to extract contact info from"
        ),
    ]

    outputs = [
        Output(
            name="extraction_prompt",
            display_name="Extraction Prompt",
            method="build_prompt",
        ),
    ]

    def build_prompt(self) -> Data:
        """
        Build the extraction prompt.

        Returns:
            Data object with the prompt and original input
        """
        text = self.text_input.strip() if self.text_input else ""

        if not text:
            self.status = "No input provided"
            return Data(data={
                "prompt": "",
                "raw_input": text,
                "has_input": False
            })

        prompt = f'''Extract contact information from this text. Return ONLY valid JSON.

Text: "{text}"

Extract:
1. contact_id: A number with 7+ digits (if present)
2. contact_name: The person's name (if present, not a number)
3. topic: The subject/topic/service mentioned

Return this exact JSON format:
{{"contact_id": null, "contact_name": null, "topic": null}}

Replace null with the extracted value as a string, or keep null if not found.

Examples:
Input: "Ken about AI"
Output: {{"contact_id": null, "contact_name": "Ken", "topic": "AI"}}

Input: "4364201 Cloud Migration"
Output: {{"contact_id": "4364201", "contact_name": null, "topic": "Cloud Migration"}}

Input: "email for John Smith regarding DevOps"
Output: {{"contact_id": null, "contact_name": "John Smith", "topic": "DevOps"}}

Now extract from the text above:'''

        self.status = f"Prompt built for: {text[:30]}..."

        return Data(data={
            "prompt": prompt,
            "raw_input": text,
            "has_input": True
        })
```

### Flow Wiring

```
[Chat/Webhook Input]
        ↓
[Contact Info Prompt Builder] → prompt
        ↓
[OpenAI] (json_mode=true, temperature=0)
        ↓
[ParseJSONData] (query: ".")
        ↓
[HubSpot Contact Search] (uses contact_name or contact_id)
        ↓
[Rest of Flow...]
```

### OpenAI Component Settings

| Setting | Value |
|---------|-------|
| Model | gpt-4o-mini |
| Temperature | 0 |
| JSON Mode | true |
| Max Tokens | 100 |
| System Message | "You are a JSON extraction assistant. Output only valid JSON, no explanation." |

### Why This Approach

1. **Uses platform's OpenAI component** - API key managed through global variables
2. **No duplicate credential management** - Single API key configuration
3. **Follows LangBuilder patterns** - Components output data, LLM components process it
4. **Testable** - Can test the prompt builder separately from LLM
5. **Flexible** - Can swap LLM models without changing component code

### Files to Modify

Replace:
```
langbuilder/src/backend/base/langbuilder/components/cloudgeometry/contact_info_extractor.py
```

With the new `ContactInfoPromptBuilder` implementation above.

---

## Implementation Checklist

### Pain Point Mapper Removal

- [ ] Delete `pain_point_mapper.py`
- [ ] Update Content Engine flow to remove Pain Point Mapper node
- [ ] Update Prompt Template with new combined prompt
- [ ] Remove edges to/from Pain Point Mapper
- [ ] Test flow with various industries (including ones not in old matrix)
- [ ] Test flow with role variations ("CFO" vs "Chief Financial Officer")

### Contact Info Extractor Rewrite

- [ ] Replace `contact_info_extractor.py` with `ContactInfoPromptBuilder`
- [ ] Add OpenAI node after Contact Info Prompt Builder in flow
- [ ] Configure OpenAI with json_mode=true, temperature=0
- [ ] Add ParseJSONData to extract fields from OpenAI response
- [ ] Test with various natural language inputs:
  - "Ken about AI Transformation"
  - "Ken regarding AI Transformation"
  - "Ken - AI Transformation"
  - "email Ken on cloud migration"
  - "4364201 Cloud Migration"
  - "Generate report for Jennifer Kim about DevOps"

---

## Cost Impact

| Change | Cost Impact |
|--------|-------------|
| Pain Point Mapper removal | **Neutral** - same number of LLM calls, just different prompt |
| Contact Info Extractor | **+1 LLM call** per extraction (~$0.0002 with gpt-4o-mini) |

Total additional cost: ~$0.20 per 1000 extractions - negligible for the reliability gain.

---

*Document created: December 2024*
