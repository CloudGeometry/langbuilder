# LangBuilder Custom Components Documentation

This document provides comprehensive documentation for all custom components developed by CloudGeometry for LangBuilder. For each component, we explain not just **what** it does, but **how** it works internally.

---

## Table of Contents

1. [CloudGeometry Components](#cloudgeometry-components)
   - [Pain Point Mapper](#pain-point-mapper)
   - [Savings Calculator](#savings-calculator)
   - [Template Selector](#template-selector)
   - [Jinja2 Renderer](#jinja2-renderer)
   - [WeasyPrint PDF Generator](#weasyprint-pdf-generator)
   - [Contact Info Extractor](#contact-info-extractor)

2. [HubSpot Integration Components](#hubspot-integration-components)
   - [HubSpot Contact Search](#hubspot-contact-search)
   - [HubSpot Contact Fetcher](#hubspot-contact-fetcher)
   - [HubSpot Contact Updater](#hubspot-contact-updater)
   - [HubSpot Company Fetcher](#hubspot-company-fetcher)
   - [HubSpot File Uploader](#hubspot-file-uploader)
   - [HubSpot Note Creator](#hubspot-note-creator)

3. [Zoho Recruit Integration Components](#zoho-recruit-integration-components)
   - [Zoho Recruit Auth](#zoho-recruit-auth)
   - [Zoho Recruit Candidates](#zoho-recruit-candidates)
   - [Zoho Recruit Job Openings](#zoho-recruit-job-openings)
   - [Zoho Recruit Attachments](#zoho-recruit-attachments)
   - [Zoho Recruit Notes](#zoho-recruit-notes)

4. [Flow Patterns](#flow-patterns)

---

## CloudGeometry Components

### Pain Point Mapper

**Location:** `components/cloudgeometry/pain_point_mapper.py`

#### What It Does

Returns a business pain point string based on who the lead is (role), what industry they're in, and which CloudGeometry service they're interested in.

#### How It Works (Implementation Details)

**This is a hardcoded lookup table.** The component contains a Python dictionary called `PAIN_POINT_MATRIX` with exactly 150 pre-written entries. There is no AI, no database, no external API - just a dictionary lookup.

**The data structure:**
```python
PAIN_POINT_MATRIX = {
    # Key is a tuple: (role, industry, service_type)
    # Value is a pain point string

    ("CFO", "Healthcare", "AI Transformation"):
        "AI implementation ROI and HIPAA-compliant ML infrastructure costs",

    ("CTO", "Fintech", "Cloud Migration"):
        "secure cloud architecture, PCI-DSS compliance, and multi-region setup",

    ("VP Engineering", "Retail", "DevOps Acceleration"):
        "high-velocity deployments during campaigns and sales",

    # ... 147 more entries like this
}
```

**The lookup logic:**
```python
def map_pain_point(self):
    # 1. Extract text from inputs (handles Message, Data, or string)
    role = self._extract_value(self.role)        # e.g., "CTO"
    industry = self._extract_value(self.industry) # e.g., "Healthcare"
    service = self._extract_value(self.service_type)  # e.g., "AI Transformation"

    # 2. Create lookup key as tuple
    lookup_key = (role, industry, service)

    # 3. Simple dictionary lookup
    pain_point = self.PAIN_POINT_MATRIX.get(lookup_key)

    # 4. If no match found, return generic fallback
    if pain_point is None:
        pain_point = f"cloud optimization and {service.lower()} best practices"
        is_default = True
```

**Supported combinations (must match exactly):**

| Roles (5) | Industries (5) | Services (6) |
|-----------|----------------|--------------|
| CFO | Healthcare | AI Transformation |
| CTO | Fintech | App Modernization |
| CIO | Technology | Cloud Migration |
| VP Engineering | Retail | DevOps Acceleration |
| Engineering Manager | Manufacturing | Data Platform |
| | | Managed Services |

**Total entries:** 5 roles × 5 industries × 6 services = **150 hardcoded pain points**

#### Sample Entries

Here are some actual entries from the matrix:

| Role | Industry | Service | Pain Point |
|------|----------|---------|------------|
| CFO | Healthcare | AI Transformation | "AI implementation ROI and HIPAA-compliant ML infrastructure costs" |
| CTO | Fintech | Cloud Migration | "secure cloud architecture, PCI-DSS compliance, and multi-region setup" |
| CIO | Technology | Data Platform | "data strategy, governance framework, and self-service enablement" |
| VP Engineering | Retail | DevOps Acceleration | "high-velocity deployments during campaigns and sales" |
| Engineering Manager | Manufacturing | Managed Services | "production support and shift coverage" |

#### What Happens If There's No Match

If the input combination doesn't exist in the matrix (e.g., role="Sales Manager"), the component returns a generic fallback:

```python
pain_point = f"cloud optimization and {service_type.lower()} best practices"
is_default = True  # Flag indicating fallback was used
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | HandleInput (Message, Data) | Yes | Must be one of: CFO, CTO, CIO, VP Engineering, Engineering Manager |
| `industry` | HandleInput (Message, Data) | Yes | Must be one of: Healthcare, Fintech, Technology, Retail, Manufacturing |
| `service_type` | HandleInput (Message, Data) | Yes | Must be one of the 6 services listed above |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `pain_point` | Data | `{"pain_point": "...", "role": "...", "industry": "...", "service_type": "...", "is_default": bool}` |

#### Limitations

1. **Exact string matching** - "CFO" works, "Chief Financial Officer" does not
2. **No fuzzy matching** - Typos or variations will trigger the fallback
3. **Fixed vocabulary** - Adding new roles/industries requires code changes
4. **English only** - All pain points are in English

#### When to Extend

If you need to add a new industry (e.g., "Education"), you'd need to add 30 new entries to the dictionary (5 roles × 6 services).

---

### Savings Calculator

**Location:** `components/cloudgeometry/savings_calculator.py`

#### What It Does

Calculates projected cost savings as a simple percentage of annual cloud spend.

#### How It Works (Implementation Details)

**This is basic arithmetic.** There's no complex financial modeling - just multiplication.

**The calculation:**
```python
def calculate_savings(self):
    # 1. Parse the annual spend (handles "$500,000" or "500000" or 500000)
    spend = self._parse_amount(self.annual_cloud_spend)  # e.g., 500000.0

    # 2. Get savings rate (default 30%)
    rate = self.savings_rate  # e.g., 0.30

    # 3. Simple multiplication
    savings_amount = spend * rate  # e.g., 150000.0

    # 4. Format for display
    savings_formatted = f"${savings_amount:,.0f}"  # e.g., "$150,000"
```

**The number parsing logic:**
```python
def _parse_amount(self, value):
    # Extract text from Message/Data objects
    text = self._extract_value(value)

    # Remove currency symbols and commas: "$1,500,000" -> "1500000"
    cleaned = re.sub(r'[^\d.]', '', text)

    # Convert to float
    return float(cleaned) if cleaned else 0.0
```

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `annual_cloud_spend` | HandleInput | Yes | - | Accepts: "500000", "$500,000", or numeric 500000 |
| `savings_rate` | FloatInput | No | 0.30 | Percentage as decimal (0.30 = 30%) |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `savings` | Data | `{"savings_amount": 150000.0, "savings_formatted": "$150,000", "annual_spend": 500000.0, "spend_formatted": "$500,000", "savings_rate": 0.30}` |

#### Example

```
Input:  annual_cloud_spend = "$2,000,000", savings_rate = 0.25
Output: savings_amount = 500000.0, savings_formatted = "$500,000"
```

---

### Template Selector

**Location:** `components/cloudgeometry/template_selector.py`

#### What It Does

Returns a URL or file path to an HTML template based on the service type.

#### How It Works (Implementation Details)

**This is another hardcoded dictionary lookup.**

**The data structure:**
```python
TEMPLATE_MAP = {
    "AI Transformation": "ai_transformation_template.html",
    "App Modernization": "app_modernization_template.html",
    "Cloud Migration": "cloud_migration_template.html",
    "DevOps Acceleration": "devops_template.html",
    "Data Platform": "data_analytics_template.html",
    "Managed Services": "managed_services_template.html",
}
DEFAULT_TEMPLATE = "generic_template.html"
```

**The lookup logic:**
```python
def select_template(self):
    service = self._extract_value(self.service_type)

    # Dictionary lookup with fallback
    template_file = self.TEMPLATE_MAP.get(service, self.DEFAULT_TEMPLATE)

    # Combine with base URL
    if self.source_type == "url":
        return f"{self.base_url}/{template_file}"
    else:
        return f"{self.base_path}/{template_file}"
```

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `service_type` | HandleInput | Yes | - | Service name to look up |
| `base_url` | StrInput | No | GitHub raw URL | Base URL for templates |
| `source_type` | DropdownInput | No | "url" | "url" or "file" |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `template_source` | Data | `{"template_url": "https://...", "template_name": "ai_transformation_template.html", "service_type": "AI Transformation"}` |

---

### Jinja2 Renderer

**Location:** `components/cloudgeometry/jinja2_renderer.py`

#### What It Does

Fetches an HTML template (from URL or file), replaces `{{ variable }}` placeholders with actual values, and returns the final HTML.

#### How It Works (Implementation Details)

**This uses the Jinja2 templating library** - a standard Python library for template rendering.

**Step-by-step process:**
```python
async def render_template(self):
    # 1. Get template source (URL or path)
    template_data = self.template_source.data
    template_url = template_data.get("template_url")

    # 2. Fetch template content via HTTP
    async with httpx.AsyncClient() as client:
        response = await client.get(template_url)
        template_html = response.text

    # 3. Create Jinja2 template object
    from jinja2 import Template
    template = Template(template_html)

    # 4. Build context dictionary from inputs
    context = {
        "company_name": self._extract_value(self.company_name),
        "lead_name": self._extract_value(self.lead_name),
        "role": self._extract_value(self.role),
        "industry": self._extract_value(self.industry),
        "ai_executive_summary": self._extract_value(self.ai_executive_summary),
        "savings_formatted": savings_data.get("savings_formatted", "$0"),
        "savings_amount": savings_data.get("savings_amount", 0),
        "render_date": datetime.now().strftime("%B %d, %Y"),
    }

    # 5. Render template with context
    rendered_html = template.render(**context)

    return rendered_html
```

**What Jinja2 does:**

Template input:
```html
<h1>Proposal for {{ company_name }}</h1>
<p>Dear {{ lead_name }},</p>
<p>We can save you {{ savings_formatted }} annually.</p>
```

After rendering with `{"company_name": "Acme Corp", "lead_name": "John", "savings_formatted": "$150,000"}`:
```html
<h1>Proposal for Acme Corp</h1>
<p>Dear John,</p>
<p>We can save you $150,000 annually.</p>
```

**Fallback behavior:**

If template fetching fails, the component generates a basic HTML document:
```python
def _generate_fallback_html(self, context):
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Proposal for {context['company_name']}</title></head>
    <body>
        <h1>Cloud Optimization Proposal</h1>
        <p>Prepared for: {context['lead_name']}</p>
        <p>Projected Savings: {context['savings_formatted']}</p>
        <div>{context['ai_executive_summary']}</div>
    </body>
    </html>
    """
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `template_source` | HandleInput (Data) | Yes | URL/path from Template Selector |
| `company_name` | HandleInput | No | Company name for `{{ company_name }}` |
| `lead_name` | HandleInput | No | Lead name for `{{ lead_name }}` |
| `role` | HandleInput | No | Role for `{{ role }}` |
| `industry` | HandleInput | No | Industry for `{{ industry }}` |
| `ai_executive_summary` | HandleInput | No | Summary for `{{ ai_executive_summary }}` |
| `calculated_savings` | HandleInput (Data) | No | Savings data from Savings Calculator |
| `annual_cloud_spend` | HandleInput | No | Spend for `{{ annual_spend_formatted }}` |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `html` | Data | `{"html": "<html>...</html>", "render_time_ms": 45, "fallback_used": false}` |

---

### WeasyPrint PDF Generator

**Location:** `components/cloudgeometry/weasyprint_pdf.py`

#### What It Does

Converts HTML to a PDF file.

#### How It Works (Implementation Details)

**This uses the WeasyPrint library** - a Python library that renders HTML/CSS to PDF. WeasyPrint is NOT a headless browser; it's a purpose-built HTML-to-PDF converter that supports a subset of CSS.

**The conversion process:**
```python
def generate_pdf(self):
    from weasyprint import HTML, CSS

    # 1. Get HTML content
    html_content = self._extract_value(self.html_content)

    # 2. Create page CSS for size and margins
    page_css = CSS(string=f"""
        @page {{
            size: {self.page_size};
            margin: {self.margin};
        }}
    """)

    # 3. Convert HTML to PDF bytes
    html_doc = HTML(string=html_content)
    pdf_bytes = html_doc.write_pdf(stylesheets=[page_css])

    # 4. Encode as base64 for transmission
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    return {
        "pdf_base64": pdf_base64,
        "pdf_bytes": pdf_bytes,
        "size_kb": len(pdf_bytes) / 1024,
        "filename": self.filename or "document.pdf"
    }
```

**System dependencies required:**

WeasyPrint requires native libraries (NOT pure Python):
- **Cairo** - 2D graphics library
- **Pango** - Text rendering
- **GDK-PixBuf** - Image handling

```bash
# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu/Debian
apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0

# Then install Python package
pip install weasyprint
```

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `html_content` | HandleInput | Yes | - | HTML string to convert |
| `filename` | HandleInput | No | "document.pdf" | Output filename |
| `page_size` | DropdownInput | No | "letter" | letter, A4, or legal |
| `margin` | StrInput | No | "0.75in" | CSS margin value |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `pdf` | Data | `{"pdf_base64": "JVBERi0x...", "pdf_bytes": <bytes>, "size_kb": 125.4, "filename": "proposal.pdf"}` |

---

### Contact Info Extractor

**Location:** `components/cloudgeometry/contact_info_extractor.py`

#### What It Does

Parses natural language text to extract a contact name, ID, or topic.

#### How It Works (Implementation Details)

**This uses regular expressions (regex)** - no AI, no NLP library, just pattern matching.

**The parsing logic:**
```python
import re

def parse_contact_info(self):
    text = self.text_input  # e.g., "Ken about AI Transformation"

    result = {
        "contact_id": None,
        "contact_name": None,
        "topic": None
    }

    # Pattern 1: Look for numeric ID (5+ digits)
    id_match = re.search(r'\b(\d{5,})\b', text)
    if id_match:
        result["contact_id"] = id_match.group(1)

    # Pattern 2: Look for name before keywords
    # Matches: "Ken about", "John Smith regarding", "Jane for"
    name_match = re.search(
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:about|regarding|for|on)\b',
        text
    )
    if name_match:
        result["contact_name"] = name_match.group(1)

    # Pattern 3: Look for topic after keywords
    # Matches: "about AI Transformation", "regarding cloud costs"
    topic_match = re.search(
        r'(?:about|regarding|for|on)\s+(.+)$',
        text,
        re.IGNORECASE
    )
    if topic_match:
        result["topic"] = topic_match.group(1).strip()

    return result
```

**Examples:**

| Input | contact_name | contact_id | topic |
|-------|--------------|------------|-------|
| "Ken about AI Transformation" | "Ken" | None | "AI Transformation" |
| "contact 12345678 regarding cloud" | None | "12345678" | "cloud" |
| "John Smith for DevOps" | "John Smith" | None | "DevOps" |
| "random text here" | None | None | None |

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `text_input` | MessageTextInput | Yes | Natural language text to parse |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `parsed_data` | Data | `{"contact_name": "Ken", "contact_id": null, "topic": "AI Transformation"}` |

#### Limitations

1. **Case sensitive for names** - Names must start with capital letter
2. **Limited keywords** - Only recognizes "about", "regarding", "for", "on"
3. **No fuzzy matching** - Won't correct typos
4. **English only** - Keywords are English

---

## HubSpot Integration Components

These components make HTTP API calls to HubSpot's REST API.

### HubSpot Contact Search

**Location:** `components/hubspot/hubspot_contact_search.py`

#### What It Does

Searches HubSpot for contacts by name or email.

#### How It Works (Implementation Details)

**This makes an HTTP POST request to HubSpot's Search API.**

**The API call:**
```python
async def search_contacts(self):
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"

    headers = {
        "Authorization": f"Bearer {self.hubspot_api_key}",
        "Content-Type": "application/json"
    }

    # Build search filter
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "firstname",
                "operator": "CONTAINS_TOKEN",
                "value": self.search_query
            }]
        }],
        "properties": ["firstname", "lastname", "email", "phone", "jobtitle"],
        "limit": self.limit
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
```

**What HubSpot returns:**
```json
{
  "total": 3,
  "results": [
    {
      "id": "12345",
      "properties": {
        "firstname": "Ken",
        "lastname": "Smith",
        "email": "ken@example.com"
      }
    },
    ...
  ]
}
```

**Selection logic:**

The component picks the "best" match from results:
```python
def _select_best_match(self, contacts, search_query):
    # Exact match on firstname gets priority
    for contact in contacts:
        if contact["properties"]["firstname"].lower() == search_query.lower():
            return contact["id"]

    # Otherwise return first result
    return contacts[0]["id"] if contacts else None
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | HubSpot private app API key |
| `parsed_data` | DataInput | No | From Contact Info Extractor |
| `search_query` | StrInput | No | Direct search string |
| `limit` | IntInput | No (default 10) | Max results |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `search_results` | Data | `{"contacts": [...], "total_count": 3, "selected_contact_id": "12345"}` |

---

### HubSpot Contact Fetcher

**Location:** `components/hubspot/hubspot_contact_fetcher.py`

#### What It Does

Retrieves a single contact's full details from HubSpot by ID.

#### How It Works (Implementation Details)

**This makes an HTTP GET request to HubSpot's Contacts API.**

**The API call:**
```python
async def fetch_contact(self):
    contact_id = self._extract_value(self.contact_id)

    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"

    params = {
        "properties": self.properties,  # e.g., "firstname,lastname,email,jobtitle"
        "associations": "companies" if self.include_company_association else ""
    }

    headers = {"Authorization": f"Bearer {self.hubspot_api_key}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
```

**What HubSpot returns:**
```json
{
  "id": "12345",
  "properties": {
    "firstname": "Ken",
    "lastname": "Smith",
    "email": "ken@example.com",
    "jobtitle": "CTO",
    "company": "Acme Corp"
  },
  "associations": {
    "companies": {
      "results": [{"id": "67890"}]
    }
  }
}
```

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | API key |
| `contact_id` | HandleInput | Yes | - | HubSpot contact ID |
| `properties` | StrInput | No | common fields | Comma-separated property names |
| `include_company_association` | BoolInput | No | True | Also fetch company IDs |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `contact` | Data | Full contact record with `associated_company_ids` list |

---

### HubSpot Contact Updater

**Location:** `components/hubspot/hubspot_contact_updater.py`

#### What It Does

Updates properties on an existing HubSpot contact.

#### How It Works (Implementation Details)

**This makes an HTTP PATCH request to HubSpot's Contacts API.**

**The API call:**
```python
async def update_contact(self):
    contact_id = self._extract_value(self.contact_id)
    properties = json.loads(self._extract_value(self.properties_json))

    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"

    headers = {
        "Authorization": f"Bearer {self.hubspot_api_key}",
        "Content-Type": "application/json"
    }

    payload = {"properties": properties}

    async with httpx.AsyncClient() as client:
        response = await client.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | API key |
| `contact_id` | HandleInput | Yes | Contact to update |
| `properties_json` | HandleInput | Yes | JSON string: `{"field": "value"}` |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | `{"success": true, "contact_id": "12345", "updated_properties": {...}}` |

---

### HubSpot Company Fetcher

**Location:** `components/hubspot/hubspot_company_fetcher.py`

#### What It Does

Retrieves company information and calculates derived analytics fields.

#### How It Works (Implementation Details)

**This makes an HTTP GET to HubSpot, then calculates additional fields.**

**The API call (same pattern as contact fetcher):**
```python
url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
```

**Derived field calculations:**
```python
def _calculate_derived_fields(self, company):
    employees = company.get("numberofemployees", 0)

    # Company size category
    if employees <= 50:
        company_size = "Small"
    elif employees <= 200:
        company_size = "Medium"
    elif employees <= 1000:
        company_size = "Large"
    else:
        company_size = "Enterprise"

    # Estimated cloud spend: $2,000 per employee, max $10M
    estimated_spend = min(employees * 2000, 10_000_000)

    return {
        "company_size": company_size,
        "estimated_cloud_spend": estimated_spend,
        "estimated_cloud_spend_formatted": f"${estimated_spend:,.0f}"
    }
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | API key |
| `company_id` | HandleInput | Yes | HubSpot company ID |
| `properties` | StrInput | No | Properties to fetch |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `company` | Data | Company data + `company_size`, `estimated_cloud_spend` |

---

### HubSpot File Uploader

**Location:** `components/hubspot/hubspot_file_uploader.py`

#### What It Does

Uploads a file (typically PDF) to HubSpot's Files API.

#### How It Works (Implementation Details)

**This makes a multipart form upload to HubSpot's Files API.**

**The API call:**
```python
async def upload_file(self):
    url = "https://api.hubapi.com/files/v3/files"

    # Decode base64 PDF content
    pdf_bytes = base64.b64decode(self.pdf_base64)

    # Create multipart form data
    files = {
        "file": (self.filename, pdf_bytes, "application/pdf")
    }

    data = {
        "folderPath": self.folder_path,
        "options": json.dumps({
            "access": self.access_level  # PUBLIC_INDEXABLE, etc.
        })
    }

    headers = {"Authorization": f"Bearer {self.hubspot_api_key}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()
```

**What HubSpot returns:**
```json
{
  "id": "file-id-123",
  "url": "https://app.hubspot.com/file-preview/123/file/456",
  "name": "proposal.pdf",
  "size": 125400
}
```

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | API key |
| `pdf_base64` | HandleInput | Yes | - | Base64-encoded file |
| `filename` | HandleInput | Yes | - | Filename with extension |
| `folder_path` | StrInput | No | "/" | HubSpot folder path |
| `access_level` | DropdownInput | No | "PUBLIC_INDEXABLE" | Visibility |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | `{"success": true, "file_url": "https://...", "file_id": "..."}` |

---

### HubSpot Note Creator

**Location:** `components/hubspot/hubspot_note_creator.py`

#### What It Does

Creates a note on a HubSpot contact's timeline.

#### How It Works (Implementation Details)

**This makes two API calls:**
1. Create the note (engagement)
2. Associate it with the contact

**The API calls:**
```python
async def create_note(self):
    # 1. Create the note
    note_url = "https://api.hubapi.com/crm/v3/objects/notes"

    note_payload = {
        "properties": {
            "hs_note_body": self.email_body,
            "hs_timestamp": int(time.time() * 1000)
        }
    }

    response = await client.post(note_url, headers=headers, json=note_payload)
    note_id = response.json()["id"]

    # 2. Associate with contact
    assoc_url = f"https://api.hubapi.com/crm/v3/objects/notes/{note_id}/associations/contacts/{self.contact_id}/note_to_contact"

    await client.put(assoc_url, headers=headers)
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | API key |
| `contact_id` | HandleInput | Yes | Contact to attach note to |
| `subject_line` | HandleInput | No | Note title |
| `email_body` | HandleInput | Yes | Note content (HTML supported) |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | `{"success": true, "engagement_id": "...", "hubspot_url": "..."}` |

---

## Zoho Recruit Integration Components

### Zoho Recruit Auth

**Location:** `components/zoho/zoho_recruit_auth.py`

#### What It Does

Handles OAuth 2.0 authentication for all Zoho Recruit API calls.

#### How It Works (Implementation Details)

**Zoho uses OAuth 2.0 with refresh tokens.** Access tokens expire after 1 hour, so this component manages token refresh automatically.

**Token refresh flow:**
```python
async def _refresh_access_token(self):
    # Zoho token endpoint varies by region
    urls = self.REGION_URLS[self.region]
    token_url = f"{urls['accounts']}/oauth/v2/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
            }
        )
        data = response.json()

    self._access_token = data["access_token"]
    # Tokens expire in 3600 seconds, refresh 5 min early
    self._token_expiry = time.time() + 3600 - 300
```

**Token caching logic:**
```python
async def get_access_token(self):
    # Return cached token if still valid
    if self._access_token and time.time() < self._token_expiry:
        return self._access_token

    # Otherwise refresh
    return await self._refresh_access_token()
```

**Region URLs:**

Zoho has separate data centers:
```python
REGION_URLS = {
    "US": {"api": "https://recruit.zoho.com/recruit/v2",
           "accounts": "https://accounts.zoho.com"},
    "EU": {"api": "https://recruit.zoho.eu/recruit/v2",
           "accounts": "https://accounts.zoho.eu"},
    # ... IN, AU, CN, JP
}
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | SecretStrInput | Yes | From Zoho API Console |
| `client_secret` | SecretStrInput | Yes | From Zoho API Console |
| `refresh_token` | SecretStrInput | Yes | Long-lived token from Self-Client grant |
| `region` | DropdownInput | No (default US) | Data center region |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `auth_config` | Data | `{"access_token": "...", "api_base_url": "...", "_auth_component": self}` |

**Important:** The output includes `_auth_component: self` which allows downstream components to call `get_access_token()` for automatic token refresh.

---

### Zoho Recruit Candidates

**Location:** `components/zoho/zoho_recruit_candidate.py`

#### What It Does

CRUD operations for candidate records in Zoho Recruit.

#### How It Works (Implementation Details)

**This makes HTTP calls to Zoho's REST API based on the selected operation.**

**Operation examples:**
```python
# LIST - GET /Candidates
async def _list_candidates(self, auth_config):
    url = f"{auth_config['api_base_url']}/Candidates"
    response = await client.get(url, headers=headers, params={"page": 1, "per_page": 200})
    return response.json()["data"]

# GET - GET /Candidates/{id}
async def _get_candidate(self, auth_config):
    url = f"{auth_config['api_base_url']}/Candidates/{self.candidate_id}"
    response = await client.get(url, headers=headers)
    return response.json()["data"][0]

# SEARCH - GET /Candidates/search?criteria=...
async def _search_candidates(self, auth_config):
    url = f"{auth_config['api_base_url']}/Candidates/search"
    params = {"criteria": "(Email:equals:john@example.com)"}
    response = await client.get(url, headers=headers, params=params)
    return response.json()["data"]

# UPDATE - PUT /Candidates/{id}
async def _update_candidate(self, auth_config):
    url = f"{auth_config['api_base_url']}/Candidates/{self.candidate_id}"
    payload = {"data": [self.update_data]}
    response = await client.put(url, headers=headers, json=payload)
    return response.json()
```

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `auth` | HandleInput (Data) | Yes | From ZohoRecruitAuth |
| `operation` | DropdownInput | No | list, get, search, update, get_by_job |
| `candidate_id` | StrInput | For get/update | Candidate record ID |
| `search_criteria` | StrInput | For search | Zoho search syntax |
| `update_data` | DictInput | For update | Fields to update |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Operation result |
| `candidates` | List[Data] | List of candidate records |

---

### Zoho Recruit Job Openings

**Location:** `components/zoho/zoho_recruit_job_opening.py`

#### What It Does

Retrieves job opening records and extracts job descriptions/requirements.

#### How It Works (Implementation Details)

**Same pattern as Candidates - HTTP GET to Zoho API.**

**The `get_requirements` operation parses job fields:**
```python
async def _get_requirements(self, auth_config):
    # First fetch the job opening
    job = await self._get_job_opening(auth_config)

    # Extract and structure requirements
    return {
        "job_title": job.get("Posting_Title", ""),
        "description": job.get("Job_Description", ""),
        "required_skills": job.get("Required_Skills", ""),
        "experience": job.get("Experience", ""),
        "industry": job.get("Industry", ""),
        "salary": job.get("Salary", ""),
        "location": job.get("City", ""),
        # ... more fields
    }
```

---

### Zoho Recruit Attachments

**Location:** `components/zoho/zoho_recruit_attachment.py`

#### What It Does

Handles file attachments (CVs/resumes) on candidate records.

#### How It Works (Implementation Details)

**For download:**
```python
async def _download_attachment(self, auth_config):
    url = f"{base_url}/Candidates/{self.record_id}/Attachments/{self.attachment_id}"
    response = await client.get(url, headers=headers)

    # Return as base64
    return {
        "content_base64": base64.b64encode(response.content).decode(),
        "filename": response.headers.get("Content-Disposition", "").split("filename=")[1]
    }
```

**For PDF text extraction (uses pypdf library):**
```python
async def _get_resume_text(self, auth_config):
    # Download the attachment
    download = await self._download_attachment(auth_config)
    pdf_bytes = base64.b64decode(download["content_base64"])

    # Extract text using pypdf
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))

    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text())

    return {"text": "\n".join(text_parts)}
```

---

### Zoho Recruit Notes

**Location:** `components/zoho/zoho_recruit_notes.py`

#### What It Does

Creates and manages notes on candidate records.

#### How It Works (Implementation Details)

**Adding a note:**
```python
async def _add_note(self, auth_config):
    url = f"{base_url}/Candidates/{self.record_id}/Notes"

    payload = {
        "data": [{
            "Note_Title": self.note_title,
            "Note_Content": self.note_content,
            "Parent_Id": self.record_id,
            "se_module": "Candidates"
        }]
    }

    response = await client.post(url, headers=headers, json=payload)
    return response.json()
```

---

## Flow Patterns

### Content Generation Pipeline

```
[Webhook] → [Contact Info Extractor] → [HubSpot Contact Search]
                                              │
                                              ▼
                                    [HubSpot Contact Fetcher]
                                              │
                    ┌─────────────────────────┴────────────────────────┐
                    ▼                                                  ▼
          [HubSpot Company Fetcher]                          [Pain Point Mapper]
                    │                                                  │
                    ▼                                                  │
          [Savings Calculator]                                         │
                    │                                                  │
                    └──────────────────┬───────────────────────────────┘
                                       ▼
                            [Template Selector]
                                       │
                                       ▼
                            [Jinja2 Renderer]
                                       │
                                       ▼
                         [WeasyPrint PDF Generator]
                                       │
                                       ▼
                         [HubSpot File Uploader]
                                       │
                                       ▼
                         [HubSpot Note Creator]
```

---

## Security Notes

- All API keys use `SecretStrInput` - values are masked in UI and encrypted at rest
- No credentials are hardcoded in any component
- Zoho tokens auto-refresh without exposing credentials

---

*Documentation generated for CloudGeometry LangBuilder Custom Components*
