# LangBuilder Custom Components Documentation

This document provides comprehensive documentation for all custom components developed by CloudGeometry for LangBuilder. These components integrate with HubSpot CRM, Zoho Recruit ATS, and provide specialized business logic for content generation workflows.

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
   - [Content Generation Pipeline](#content-generation-pipeline)
   - [CRM Integration Pipeline](#crm-integration-pipeline)
   - [Recruitment Automation Pipeline](#recruitment-automation-pipeline)

---

## CloudGeometry Components

These components implement specialized business logic for CloudGeometry's content generation and lead engagement workflows.

### Pain Point Mapper

**Component Name:** `PainPointMapper`
**Display Name:** Pain Point Mapper
**Location:** `components/cloudgeometry/pain_point_mapper.py`

#### Purpose

Maps a combination of role, industry, and service type to a relevant business pain point. Contains 150+ pre-defined mappings across 6 cloud services, 5 roles, and 5 industries to generate contextually relevant messaging for leads.

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | HandleInput (Message, Data) | Yes | The lead's job role (e.g., "CTO", "VP of Engineering") |
| `industry` | HandleInput (Message, Data) | Yes | The lead's industry (e.g., "Financial Services", "Healthcare") |
| `service_type` | HandleInput (Message, Data) | Yes | The cloud service being offered |

**Supported Service Types:**
- AI Transformation
- Cloud Cost Optimization
- DevOps Automation
- Data Analytics
- Security & Compliance
- Cloud Migration

**Supported Roles:**
- CTO / VP of Engineering
- CFO / Finance Director
- CEO / Business Owner
- IT Director / Manager
- Operations Director

**Supported Industries:**
- Financial Services
- Healthcare
- Retail / E-commerce
- Manufacturing
- Technology / SaaS

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `pain_point` | Data | Contains: `pain_point` (string), `role`, `industry`, `service_type`, `is_default` (bool) |

#### What Can Connect To It

- **Text Outputs**: Any component outputting Message or Data containing role/industry/service text
- **LLM Outputs**: AI-extracted role/industry information
- **Form Inputs**: Webhook data with lead information
- **HubSpot Components**: Contact or company data with role/industry fields

#### What It Connects To

- **Prompt Templates**: Feed pain points into AI prompts for personalized content
- **Jinja2 Renderer**: Use pain points in document templates
- **LLM Components**: Provide context for AI content generation

#### Example Usage

```
[HubSpot Contact Fetcher] → role → [Pain Point Mapper]
[HubSpot Company Fetcher] → industry → [Pain Point Mapper]
[User Input] → service_type → [Pain Point Mapper]
                                      ↓
                              pain_point output
                                      ↓
                            [Prompt Template / LLM]
```

---

### Savings Calculator

**Component Name:** `SavingsCalculator`
**Display Name:** Cloud Savings Calculator
**Location:** `components/cloudgeometry/savings_calculator.py`

#### Purpose

Calculates projected cloud cost savings based on annual cloud spend and a configurable savings rate. Produces formatted currency values suitable for documents and presentations.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `annual_cloud_spend` | HandleInput (Message, Data) | Yes | - | Annual cloud spend amount (extracts numeric value) |
| `savings_rate` | FloatInput | No | 0.30 (30%) | Projected savings percentage |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `savings` | Data | Contains: `calculated_savings` (float), `savings_amount` (float), `annual_spend` (float), `savings_rate` (float), `savings_formatted` (string, e.g., "$150,000"), `spend_formatted` (string) |

#### What Can Connect To It

- **HubSpot Company Fetcher**: Company's estimated cloud spend
- **Form Data**: User-provided spend information
- **Data Extractors**: Numeric values from any source

#### What It Connects To

- **Jinja2 Renderer**: Inject formatted savings into documents
- **Prompt Templates**: Use savings figures in AI content
- **PDF Generator**: Include in generated reports

#### Calculation Logic

```
savings_amount = annual_cloud_spend × savings_rate
```

The component automatically:
- Parses numeric values from strings (handles "$500,000" → 500000)
- Formats output with currency symbols and thousands separators
- Preserves both raw numbers and formatted strings

---

### Template Selector

**Component Name:** `TemplateSelector`
**Display Name:** Template Selector
**Location:** `components/cloudgeometry/template_selector.py`

#### Purpose

Selects the appropriate HTML template URL or file path based on the service type. Supports 6 service-specific templates and allows configuration of template source location.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `service_type` | HandleInput (Message, Data) | Yes | - | Service type to select template for |
| `base_url` | StrInput | No | GitHub raw URL | Base URL or path for templates |
| `source_type` | DropdownInput | No | "url" | Either "url" or "file" |

**Template Mapping:**
| Service Type | Template File |
|--------------|---------------|
| AI Transformation | `ai_transformation_template.html` |
| Cloud Cost Optimization | `cost_optimization_template.html` |
| DevOps Automation | `devops_template.html` |
| Data Analytics | `data_analytics_template.html` |
| Security & Compliance | `security_template.html` |
| Cloud Migration | `cloud_migration_template.html` |
| (default) | `generic_template.html` |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `template_source` | Data | Contains: `template_url` or `template_path`, `service_type`, `template_name`, `source_type` |

#### What Can Connect To It

- **User Input**: Service type selection
- **CRM Data**: Service of interest from lead record
- **Workflow Logic**: Dynamically determined service type

#### What It Connects To

- **Jinja2 Renderer**: Provides the template URL/path to render

---

### Jinja2 Renderer

**Component Name:** `Jinja2TemplateRenderer`
**Display Name:** Jinja2 Template Renderer
**Location:** `components/cloudgeometry/jinja2_renderer.py`

#### Purpose

Renders Jinja2 HTML templates with dynamic context variables. Fetches templates from URLs or local files and produces final HTML ready for PDF conversion. Includes a built-in fallback template if the primary template fails to load.

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `template_source` | HandleInput (Data) | Yes | Template URL/path from Template Selector |
| `company_name` | HandleInput (Message, Data) | No | Company name for personalization |
| `lead_name` | HandleInput (Message, Data) | No | Lead's name |
| `role` | HandleInput (Message, Data) | No | Lead's job role |
| `industry` | HandleInput (Message, Data) | No | Lead's industry |
| `ai_executive_summary` | HandleInput (Message, Data) | No | AI-generated executive summary text |
| `calculated_savings` | HandleInput (Data) | No | Savings data from Savings Calculator |
| `annual_cloud_spend` | HandleInput (Message, Data) | No | Annual spend for display |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `html` | Data | Contains: `html` (rendered HTML string), `render_time_ms`, `template_source`, `fallback_used` (bool) |

#### Template Variables Available

The following Jinja2 variables are available in templates:

```jinja2
{{ company_name }}
{{ lead_name }}
{{ role }}
{{ industry }}
{{ ai_executive_summary }}
{{ savings_formatted }}      # e.g., "$150,000"
{{ savings_amount }}         # e.g., 150000.0
{{ annual_spend_formatted }} # e.g., "$500,000"
{{ annual_spend }}           # e.g., 500000.0
{{ render_date }}            # Current date formatted
```

#### What Can Connect To It

- **Template Selector**: Provides template source
- **Pain Point Mapper**: Role, industry data
- **Savings Calculator**: Financial projections
- **HubSpot Components**: Contact/company data
- **LLM Components**: AI-generated content (executive summary)

#### What It Connects To

- **WeasyPrint PDF Generator**: HTML → PDF conversion
- **Direct Output**: HTML for email or web display

#### Fallback Behavior

If template loading fails (network error, file not found), the component automatically generates a professional fallback HTML document containing all provided data, ensuring the workflow never fails completely.

---

### WeasyPrint PDF Generator

**Component Name:** `WeasyPrintPDF`
**Display Name:** WeasyPrint PDF Generator
**Location:** `components/cloudgeometry/weasyprint_pdf.py`

#### Purpose

Converts HTML content to PDF documents using the WeasyPrint library. Supports configurable page sizes and margins, and outputs base64-encoded PDF data suitable for file uploads or direct downloads.

#### System Requirements

Requires system-level dependencies:
- Cairo graphics library
- Pango text rendering
- GDK-PixBuf for images

Install on macOS: `brew install cairo pango gdk-pixbuf libffi`
Install on Ubuntu: `apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0`

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `html_content` | HandleInput (Message, Data) | Yes | - | HTML string to convert |
| `filename` | HandleInput (Message, Data) | No | "document.pdf" | Output filename |
| `page_size` | DropdownInput | No | "letter" | Page size: letter, A4, legal |
| `margin` | StrInput | No | "0.75in" | Page margins (CSS format) |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `pdf` | Data | Contains: `pdf_base64` (string), `pdf_bytes` (bytes), `filename`, `size_kb`, `page_size`, `generation_time_ms` |

#### What Can Connect To It

- **Jinja2 Renderer**: Rendered HTML content
- **Any HTML Source**: Raw HTML strings

#### What It Connects To

- **HubSpot File Uploader**: Upload PDF to CRM
- **Email Components**: Attach PDF to emails
- **Storage Components**: Save to cloud storage
- **Zoho Recruit Attachments**: Attach to candidate records

#### Page Size Reference

| Size | Dimensions |
|------|------------|
| letter | 8.5" × 11" |
| A4 | 210mm × 297mm |
| legal | 8.5" × 14" |

---

### Contact Info Extractor

**Component Name:** `ContactInfoExtractor`
**Display Name:** Contact Info Extractor
**Location:** `components/cloudgeometry/contact_info_extractor.py`

#### Purpose

Parses natural language input to extract contact identification and topic information. Useful for processing conversational queries like "Ken about AI Transformation" or "contact 12345 regarding cloud costs".

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `text_input` | MessageTextInput | Yes | Natural language text to parse |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `parsed_data` | Data | Contains: `contact_id` (if numeric ID found), `contact_name` (if name found), `topic` (extracted topic) |

#### Parsing Logic

The component uses regex patterns to identify:
1. **Numeric IDs**: Extracts sequences of 5+ digits as contact IDs
2. **Names**: Extracts capitalized words before keywords like "about", "regarding", "for"
3. **Topics**: Extracts text after "about", "regarding", "for", "on"

#### What Can Connect To It

- **Chat Input**: User messages in conversational interfaces
- **Webhook Data**: Incoming request text
- **Form Submissions**: Free-text fields

#### What It Connects To

- **HubSpot Contact Search**: Use extracted name to find contact
- **HubSpot Contact Fetcher**: Use extracted ID to fetch contact
- **Workflow Logic**: Route based on extracted topic

---

## HubSpot Integration Components

These components provide full integration with HubSpot CRM for contact management, company data, file storage, and engagement tracking.

### HubSpot Contact Search

**Component Name:** `HubSpotContactSearch`
**Display Name:** HubSpot Contact Search
**Location:** `components/hubspot/hubspot_contact_search.py`

#### Purpose

Searches HubSpot contacts by name or email, returning matching contacts with pagination support. Automatically selects the most relevant match when multiple results are found.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | HubSpot private app API key |
| `parsed_data` | DataInput | No | - | Parsed data from Contact Info Extractor |
| `search_query` | StrInput | No | - | Direct search query (name or email) |
| `limit` | IntInput | No | 10 | Maximum results to return |

**Note:** Either `parsed_data` or `search_query` must be provided.

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `search_results` | Data | Contains: `contacts` (list), `total_count`, `selected_contact_id` (best match), `search_query` |

#### What Can Connect To It

- **Contact Info Extractor**: Parsed contact name/ID
- **User Input**: Manual search query
- **Webhook Data**: Search parameters from external systems

#### What It Connects To

- **HubSpot Contact Fetcher**: Use `selected_contact_id` to get full details
- **Conditional Logic**: Branch based on result count

---

### HubSpot Contact Fetcher

**Component Name:** `HubSpotContactFetcher`
**Display Name:** HubSpot Contact Fetcher
**Location:** `components/hubspot/hubspot_contact_fetcher.py`

#### Purpose

Retrieves detailed contact information from HubSpot by contact ID. Supports fetching custom properties and associated company relationships.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | HubSpot private app API key |
| `contact_id` | HandleInput (Message, Data) | Yes | - | HubSpot contact ID |
| `properties` | StrInput | No | (common fields) | Comma-separated property names |
| `include_company_association` | BoolInput | No | True | Fetch associated company IDs |

**Default Properties:**
`firstname, lastname, email, phone, jobtitle, company, lifecyclestage, hs_lead_status`

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `contact` | Data | Full contact record with all requested properties and `associated_company_ids` list |

#### What Can Connect To It

- **HubSpot Contact Search**: Selected contact ID from search
- **Webhook Data**: Contact ID from HubSpot workflows
- **Contact Info Extractor**: Extracted numeric contact ID

#### What It Connects To

- **Pain Point Mapper**: Provide role for pain point lookup
- **Jinja2 Renderer**: Provide contact details for document
- **HubSpot Company Fetcher**: Use associated company ID
- **HubSpot Contact Updater**: Update the fetched contact
- **Any component needing contact data**

---

### HubSpot Contact Updater

**Component Name:** `HubSpotContactUpdater`
**Display Name:** HubSpot Contact Updater
**Location:** `components/hubspot/hubspot_contact_updater.py`

#### Purpose

Updates contact properties in HubSpot. Can update any standard or custom contact property.

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | HubSpot private app API key |
| `contact_id` | HandleInput (Message, Data) | Yes | Contact ID to update |
| `properties_json` | HandleInput (Message, Data) | Yes | JSON string of properties to update |

**Properties JSON Example:**
```json
{
  "lifecyclestage": "opportunity",
  "hs_lead_status": "QUALIFIED",
  "custom_field": "value"
}
```

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Contains: `success` (bool), `contact_id`, `updated_properties`, `hubspot_url` |

#### What Can Connect To It

- **HubSpot Contact Fetcher**: Contact ID to update
- **Workflow Logic**: Computed property values
- **LLM Output**: AI-determined field values

#### What It Connects To

- **Flow End**: Terminal action
- **Notification Components**: Confirm update
- **Logging**: Audit trail

---

### HubSpot Company Fetcher

**Component Name:** `HubSpotCompanyFetcher`
**Display Name:** HubSpot Company Fetcher
**Location:** `components/hubspot/hubspot_company_fetcher.py`

#### Purpose

Retrieves company information from HubSpot and derives useful analytics fields like company size category and estimated cloud spend based on employee count.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | HubSpot private app API key |
| `company_id` | HandleInput (Message, Data) | Yes | - | HubSpot company ID |
| `properties` | StrInput | No | (common fields) | Comma-separated property names |

**Default Properties:**
`name, domain, industry, numberofemployees, annualrevenue, city, state, country`

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `company` | Data | Company data plus derived fields: `company_size` (enum), `estimated_cloud_spend` (calculated) |

#### Derived Fields

**Company Size Categories:**
| Employees | Category |
|-----------|----------|
| 1-50 | Small |
| 51-200 | Medium |
| 201-1000 | Large |
| 1001+ | Enterprise |

**Estimated Cloud Spend Formula:**
```
spend = number_of_employees × $2,000/year (capped at $10M)
```

#### What Can Connect To It

- **HubSpot Contact Fetcher**: Associated company ID
- **Webhook Data**: Company ID from HubSpot
- **Direct Input**: Known company ID

#### What It Connects To

- **Pain Point Mapper**: Industry for pain point lookup
- **Savings Calculator**: Estimated cloud spend
- **Jinja2 Renderer**: Company details for document
- **Template Selector**: Industry-based template selection

---

### HubSpot File Uploader

**Component Name:** `HubSpotFileUploader`
**Display Name:** HubSpot File Uploader
**Location:** `components/hubspot/hubspot_file_uploader.py`

#### Purpose

Uploads files (typically PDFs) to HubSpot's Files API. Returns a shareable URL that can be used in emails, notes, or stored on contact records.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | HubSpot private app API key |
| `pdf_base64` | HandleInput (Message, Data) | Yes | - | Base64-encoded file content |
| `filename` | HandleInput (Message, Data) | Yes | - | Filename with extension |
| `folder_path` | StrInput | No | "/" | HubSpot folder path |
| `access_level` | DropdownInput | No | "PUBLIC_INDEXABLE" | File visibility |

**Access Level Options:**
- `PUBLIC_INDEXABLE` - Publicly accessible, indexed by search engines
- `PUBLIC_NOT_INDEXABLE` - Publicly accessible, not indexed
- `PRIVATE` - Requires authentication

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Contains: `success`, `file_url` (shareable link), `file_id`, `filename`, `size_bytes` |

#### What Can Connect To It

- **WeasyPrint PDF Generator**: PDF base64 and filename
- **Any File Generator**: Base64-encoded file content

#### What It Connects To

- **HubSpot Contact Updater**: Store file URL on contact
- **HubSpot Note Creator**: Reference file URL in note
- **Email Components**: Include download link

---

### HubSpot Note Creator

**Component Name:** `HubSpotNoteCreator`
**Display Name:** HubSpot Note Creator
**Location:** `components/hubspot/hubspot_note_creator.py`

#### Purpose

Creates engagement notes on HubSpot contact timelines. Useful for logging AI-generated content, workflow completions, or any activity that should appear in the contact's history.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hubspot_api_key` | SecretStrInput | Yes | - | HubSpot private app API key |
| `contact_id` | HandleInput (Message, Data) | Yes | - | Contact to attach note to |
| `subject_line` | HandleInput (Message, Data) | No | "AI Generated Note" | Note subject/title |
| `email_body` | HandleInput (Message, Data) | Yes | - | Note content (supports HTML) |
| `source_cited` | HandleInput (Message, Data) | No | - | Source reference for audit |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Contains: `success`, `engagement_id`, `hubspot_url` (direct link to note) |

#### What Can Connect To It

- **HubSpot Contact Fetcher**: Contact ID
- **LLM Components**: AI-generated note content
- **Jinja2 Renderer**: Formatted HTML content
- **Any Text Source**: Note body text

#### What It Connects To

- **Flow End**: Terminal action
- **Notification Components**: Confirm note creation
- **Logging**: Activity audit trail

---

## Zoho Recruit Integration Components

These components provide integration with Zoho Recruit ATS (Applicant Tracking System) for the AI Recruitment Command Center project.

### Zoho Recruit Auth

**Component Name:** `ZohoRecruitAuth`
**Display Name:** Recruit Auth (Zoho)
**Location:** `components/zoho/zoho_recruit_auth.py`

#### Purpose

Handles OAuth 2.0 authentication for Zoho Recruit API. Manages token refresh automatically and supports all Zoho data center regions. This component must be connected to all other Zoho Recruit components.

#### Setup Requirements

1. Create a Self-Client application in [Zoho API Console](https://api-console.zoho.com/)
2. Generate a refresh token with required scopes
3. Configure client ID, client secret, and refresh token in this component

**Required OAuth Scopes:**
- `ZohoRecruit.modules.ALL`
- `ZohoRecruit.modules.attachments.ALL`
- `ZohoRecruit.modules.notes.ALL`
- `ZohoRecruit.settings.ALL`

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | SecretStrInput | Yes | OAuth Client ID from Zoho API Console |
| `client_secret` | SecretStrInput | Yes | OAuth Client Secret |
| `refresh_token` | SecretStrInput | Yes | Long-lived refresh token |
| `region` | DropdownInput | No | Data center region: US, EU, IN, AU, CN, JP (default: US) |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `auth_config` | Data | Contains: `access_token`, `api_base_url`, `accounts_url`, `region`, `_auth_component` (for token refresh) |

#### Region URLs

| Region | API Base URL |
|--------|--------------|
| US | `https://recruit.zoho.com/recruit/v2` |
| EU | `https://recruit.zoho.eu/recruit/v2` |
| IN | `https://recruit.zoho.in/recruit/v2` |
| AU | `https://recruit.zoho.com.au/recruit/v2` |
| CN | `https://recruit.zoho.com.cn/recruit/v2` |
| JP | `https://recruit.zoho.jp/recruit/v2` |

#### Token Management

- Access tokens expire after 1 hour
- Component automatically refreshes tokens 5 minutes before expiry
- Refresh is transparent to downstream components

#### What It Connects To

All other Zoho Recruit components require this auth configuration:
- Zoho Recruit Candidates
- Zoho Recruit Job Openings
- Zoho Recruit Attachments
- Zoho Recruit Notes

---

### Zoho Recruit Candidates

**Component Name:** `ZohoRecruitCandidate`
**Display Name:** Recruit Candidates (Zoho)
**Location:** `components/zoho/zoho_recruit_candidate.py`

#### Purpose

Full CRUD operations for candidate records in Zoho Recruit. Supports listing, searching, retrieving, and updating candidate information.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `auth` | HandleInput (Data) | Yes | - | Auth config from ZohoRecruitAuth |
| `operation` | DropdownInput | No | "list" | Operation to perform |
| `candidate_id` | StrInput | Conditional | - | Required for "get" and "update" |
| `job_opening_id` | StrInput | Conditional | - | Required for "get_by_job" |
| `search_criteria` | StrInput | Conditional | - | Required for "search" |
| `update_data` | DictInput | Conditional | - | Required for "update" |
| `fields` | StrInput | No | "" | Comma-separated fields to return |
| `page` | IntInput | No | 1 | Page number for pagination |
| `per_page` | IntInput | No | 200 | Records per page (max 200) |

**Operations:**
| Operation | Description | Required Inputs |
|-----------|-------------|-----------------|
| `list` | List all candidates with pagination | - |
| `get` | Get single candidate by ID | `candidate_id` |
| `search` | Search by criteria | `search_criteria` |
| `update` | Update candidate fields | `candidate_id`, `update_data` |
| `get_by_job` | Get candidates for a job | `job_opening_id` |

**Search Criteria Format:**
```
(Email:equals:john@example.com)
(Last_Name:starts_with:Smi)
((City:equals:New York)and(Experience:greater_than:5))
```

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Operation result with candidate data |
| `candidates` | List[Data] | List of candidates for iteration |

#### What Can Connect To It

- **Zoho Recruit Auth**: Required auth configuration
- **Zoho Recruit Job Openings**: Job ID for filtering
- **Workflow Logic**: Search criteria, update data

#### What It Connects To

- **Zoho Recruit Attachments**: Candidate ID for attachments
- **Zoho Recruit Notes**: Candidate ID for notes
- **LLM Components**: Candidate data for analysis
- **Loop Components**: Iterate over candidates list

**Rate Limits:**
- list/get: 200 requests/minute
- search/update: 100 requests/minute

---

### Zoho Recruit Job Openings

**Component Name:** `ZohoRecruitJobOpening`
**Display Name:** Recruit Job Openings (Zoho)
**Location:** `components/zoho/zoho_recruit_job_opening.py`

#### Purpose

Access job opening records and extract job descriptions and requirements. Essential for matching candidates to positions and providing context for CV analysis.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `auth` | HandleInput (Data) | Yes | - | Auth config from ZohoRecruitAuth |
| `operation` | DropdownInput | No | "list" | Operation to perform |
| `job_opening_id` | StrInput | Conditional | - | Required for get operations |
| `fields` | StrInput | No | "" | Comma-separated fields to return |
| `page` | IntInput | No | 1 | Page number |
| `per_page` | IntInput | No | 200 | Records per page |

**Operations:**
| Operation | Description | Required Inputs |
|-----------|-------------|-----------------|
| `list` | List all job openings | - |
| `get` | Get single job opening | `job_opening_id` |
| `get_description` | Get job description text | `job_opening_id` |
| `get_requirements` | Extract all requirements | `job_opening_id` |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Operation result with job data |
| `job_openings` | List[Data] | List of jobs for iteration |
| `description_text` | str | Just the job description text |

#### Requirements Data Structure

The `get_requirements` operation returns:
```json
{
  "job_title": "Senior Developer",
  "description": "Full job description...",
  "required_skills": "Python, AWS, Docker",
  "experience": "5+ years",
  "industry": "Technology",
  "job_type": "Full-time",
  "salary": "$150,000",
  "location": "San Francisco",
  "state": "CA",
  "country": "USA",
  "department": "Engineering",
  "number_of_positions": 2,
  "date_opened": "2024-01-15",
  "target_date": "2024-03-01"
}
```

#### What Can Connect To It

- **Zoho Recruit Auth**: Required auth configuration

#### What It Connects To

- **Zoho Recruit Candidates**: Filter candidates by job
- **LLM Components**: Job requirements for CV matching
- **Prompt Templates**: Job details for analysis prompts

---

### Zoho Recruit Attachments

**Component Name:** `ZohoRecruitAttachment`
**Display Name:** Recruit Attachments (Zoho)
**Location:** `components/zoho/zoho_recruit_attachment.py`

#### Purpose

Handle file attachments on Zoho Recruit records, primarily CVs/resumes on candidate records. Supports listing, downloading, uploading, and extracting text from PDF resumes.

#### System Requirements

For PDF text extraction (`get_resume_text` operation):
- pypdf library: `pip install pypdf`

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `auth` | HandleInput (Data) | Yes | - | Auth config from ZohoRecruitAuth |
| `operation` | DropdownInput | No | "list" | Operation to perform |
| `record_id` | StrInput | Yes | - | Candidate ID (or other record) |
| `module` | DropdownInput | No | "Candidates" | Zoho module |
| `attachment_id` | StrInput | Conditional | - | Required for download/get_resume_text |
| `file` | FileInput | Conditional | - | Required for upload |
| `filename` | StrInput | No | - | Custom filename for upload |

**Operations:**
| Operation | Description | Required Inputs |
|-----------|-------------|-----------------|
| `list` | List all attachments | `record_id` |
| `download` | Download attachment | `record_id`, `attachment_id` |
| `upload` | Upload new attachment | `record_id`, `file` |
| `get_resume_text` | Extract PDF text | `record_id`, `attachment_id` |

**Supported Modules:**
- Candidates
- Job_Openings
- Contacts
- Clients

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Operation result |
| `attachments` | List[Data] | List of attachments with `is_resume` flag |
| `file_content` | str | Base64-encoded file content |
| `text_content` | str | Extracted text from PDF |

#### Resume Detection

The component automatically flags likely resumes based on:
- Filename contains: "resume", "cv", "curriculum", "vitae"
- File extension: .pdf, .doc, .docx

#### What Can Connect To It

- **Zoho Recruit Auth**: Required auth configuration
- **Zoho Recruit Candidates**: Candidate ID
- **File Components**: File content for upload

#### What It Connects To

- **LLM Components**: Resume text for AI analysis
- **Storage Components**: Downloaded file content
- **Text Processing**: Extracted resume text

**Rate Limits:**
- list/download: 200 requests/minute
- upload: 50 requests/minute

---

### Zoho Recruit Notes

**Component Name:** `ZohoRecruitNotes`
**Display Name:** Recruit Notes (Zoho)
**Location:** `components/zoho/zoho_recruit_notes.py`

#### Purpose

Manage notes on Zoho Recruit records. Used for storing interview feedback, recruiter observations, AI-generated summaries, and status updates on candidate timelines.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `auth` | HandleInput (Data) | Yes | - | Auth config from ZohoRecruitAuth |
| `operation` | DropdownInput | No | "get_notes" | Operation to perform |
| `record_id` | StrInput | Yes | - | Candidate ID (or other record) |
| `module` | DropdownInput | No | "Candidates" | Zoho module |
| `note_id` | StrInput | Conditional | - | Required for update/delete |
| `note_title` | StrInput | Conditional | - | Required for add_note |
| `note_content` | MultilineInput | Conditional | - | Required for add_note |

**Operations:**
| Operation | Description | Required Inputs |
|-----------|-------------|-----------------|
| `get_notes` | Get all notes for record | `record_id` |
| `add_note` | Add new note | `record_id`, `note_title`, `note_content` |
| `update_note` | Update existing note | `record_id`, `note_id` |
| `delete_note` | Delete a note | `record_id`, `note_id` |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `result` | Data | Operation result with note_id if created |
| `notes` | List[Data] | List of notes for iteration |

#### What Can Connect To It

- **Zoho Recruit Auth**: Required auth configuration
- **Zoho Recruit Candidates**: Candidate ID
- **LLM Components**: AI-generated note content
- **Workflow Logic**: Dynamic note title/content

#### What It Connects To

- **Flow End**: Terminal action
- **Notification Components**: Confirm note creation
- **Logging**: Activity audit

**Rate Limits:**
- get_notes: 200 requests/minute
- add/update/delete: 100 requests/minute

---

## Flow Patterns

### Content Generation Pipeline

A typical flow for generating personalized content documents:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CONTENT GENERATION PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Webhook/Trigger]                                                      │
│        │                                                                │
│        ▼                                                                │
│  [Contact Info Extractor] ──────────────────────────────┐               │
│        │                                                │               │
│        ▼                                                ▼               │
│  [HubSpot Contact Search] ◄────────────────── (search query)            │
│        │                                                                │
│        │ contact_id                                                     │
│        ▼                                                                │
│  [HubSpot Contact Fetcher] ────────► role ────► [Pain Point Mapper]     │
│        │                                              │                 │
│        │ company_id                                   │ pain_point      │
│        ▼                                              ▼                 │
│  [HubSpot Company Fetcher] ─► industry ──────► [Pain Point Mapper]      │
│        │                                              │                 │
│        │ estimated_cloud_spend                        │                 │
│        ▼                                              │                 │
│  [Savings Calculator] ───────────────────────────────┐│                 │
│        │                                             ││                 │
│        │ savings_formatted                           ││                 │
│        ▼                                             ▼▼                 │
│  [Template Selector] ──► template_url ──► [Jinja2 Renderer]             │
│                                                  │                      │
│        ┌──────────────────────────────◄──────────┘                      │
│        │ html                                                           │
│        ▼                                                                │
│  [WeasyPrint PDF Generator]                                             │
│        │                                                                │
│        │ pdf_base64                                                     │
│        ▼                                                                │
│  [HubSpot File Uploader] ────────► file_url ────► [HubSpot Note Creator]│
│                                                          │              │
│                                                          ▼              │
│                                                    [Flow Complete]      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### CRM Integration Pipeline

Pattern for fetching and updating CRM data:

```
[Trigger] → [Contact Search] → [Contact Fetcher] → [Process/LLM]
                                      │
                                      ▼
                              [Company Fetcher]
                                      │
                                      ▼
                              [Business Logic]
                                      │
                                      ▼
                              [Contact Updater]
                                      │
                                      ▼
                              [Note Creator]
```

### Recruitment Automation Pipeline

Pattern for AI-powered candidate analysis:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RECRUITMENT AUTOMATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Zoho Recruit Auth] ◄─── OAuth credentials (one-time setup)            │
│        │                                                                │
│        │ auth_config (shared to all Zoho components)                    │
│        │                                                                │
│        ├────────────────┬────────────────┬────────────────┐             │
│        ▼                ▼                ▼                ▼             │
│  [Job Openings]   [Candidates]    [Attachments]    [Notes]              │
│        │                │                │                              │
│        │ requirements   │ candidate_id   │ resume_text                  │
│        ▼                ▼                ▼                              │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │                    [LLM/AI Agent]                       │            │
│  │  - Match candidates to job requirements                 │            │
│  │  - Analyze CV/resume content                            │            │
│  │  - Generate screening questions                         │            │
│  │  - Score candidate fit                                  │            │
│  └─────────────────────────────────────────────────────────┘            │
│                          │                                              │
│                          │ analysis_result                              │
│                          ▼                                              │
│                    [Recruit Notes]                                      │
│                          │                                              │
│                          │ add_note (AI summary)                        │
│                          ▼                                              │
│                    [Candidates]                                         │
│                          │                                              │
│                          │ update (status, score)                       │
│                          ▼                                              │
│                    [Flow Complete]                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### API Key Management

All components use `SecretStrInput` for API keys and credentials, which:
- Masks values in the UI
- Encrypts at rest
- Never logs credential values

### Best Practices

1. **Use environment variables** for credentials in production
2. **Limit API key scopes** to minimum required permissions
3. **Monitor rate limits** - HubSpot and Zoho have per-minute limits
4. **Audit trail** - Use Note Creator components to log AI actions

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12 | Initial release with 17 components |

---

*Documentation generated for CloudGeometry LangBuilder Custom Components*
*Author: CloudGeometry Development Team*
