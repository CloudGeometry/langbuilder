# Week 1 Learning Guide

Your first week with LangBuilder - a structured path from setup to first contribution.

## Overview

| Day | Focus Area | Goal |
|-----|------------|------|
| Day 1 | Environment Setup | Application running locally |
| Day 2 | Architecture Overview | Understand project structure |
| Day 3 | Backend Deep Dive | Navigate API and services |
| Day 4 | Frontend Deep Dive | Understand React components |
| Day 5 | First Contribution | Make a small change |

---

## Day 1: Environment Setup

**Goal**: Get the application running and create your first flow.

### Morning

1. Complete the [Day 1 Setup Guide](./day-1-setup.md)
2. Verify backend and frontend are running
3. Access the application at http://localhost:5175

### Afternoon

1. Create a user account
2. Create your first flow:
   - Add a Text Input node
   - Add an OpenAI node (if you have an API key)
   - Connect them together
   - Run the flow
3. Explore the UI:
   - Browse available components
   - Try different node types
   - Understand the flow canvas

### End of Day Checklist

- [ ] Development environment is working
- [ ] Created first flow
- [ ] Understand basic UI navigation

---

## Day 2: Architecture Overview

**Goal**: Understand how the project is structured and how components interact.

### Morning: Project Structure

Study the repository layout:

```
langbuilder/                          # Repository root
├── langbuilder/                      # Main package
│   ├── src/
│   │   ├── backend/
│   │   │   ├── base/                 # Core library (langbuilder-base)
│   │   │   │   └── langbuilder/
│   │   │   │       ├── api/          # FastAPI routes
│   │   │   │       ├── components/   # AI components (455+)
│   │   │   │       ├── graph/        # Execution engine
│   │   │   │       ├── services/     # Business logic
│   │   │   │       └── custom/       # Custom component support
│   │   │   └── tests/                # Backend tests
│   │   └── frontend/
│   │       └── src/
│   │           ├── stores/           # Zustand state
│   │           ├── pages/            # Page components
│   │           ├── CustomNodes/      # Flow canvas nodes
│   │           └── components/       # UI components
│   ├── pyproject.toml                # Package dependencies
│   └── Makefile                      # Development commands
├── openwebui/                        # ActionBridge integration
└── pyproject.toml                    # Workspace root
```

### Afternoon: Core Concepts

Read and understand these files:

1. **Codebase Primer**: `E:/Work/CloudGeometry/langbuilder/.cg-aix-sdlc/ai-context/codebase-primer.md`
2. **Architecture Patterns**: `E:/Work/CloudGeometry/langbuilder/.cg-aix-sdlc/docs/architecture/patterns-and-principles.md`

### Key Files to Explore

| File | Purpose |
|------|---------|
| `langbuilder/src/backend/base/langbuilder/api/router.py` | API route definitions |
| `langbuilder/src/backend/base/langbuilder/components/__init__.py` | Component registry |
| `langbuilder/src/frontend/src/App.tsx` | Frontend entry point |
| `langbuilder/src/frontend/src/stores/flowStore.ts` | Flow state management |

### End of Day Checklist

- [ ] Understand monorepo structure
- [ ] Know where to find API routes
- [ ] Know where to find components
- [ ] Reviewed architecture documentation

---

## Day 3: Backend Deep Dive

**Goal**: Understand the FastAPI backend, API structure, and service layer.

### Morning: API Layer

#### Explore API Routes

```bash
# Navigate to API directory
cd langbuilder/src/backend/base/langbuilder/api/
```

Key API modules:

| Path | Purpose |
|------|---------|
| `v1/flows.py` | Flow CRUD operations |
| `v1/build.py` | Flow execution/build |
| `v1/run.py` | API endpoint execution |
| `v1/chat.py` | Chat interface API |
| `v1/mcp.py` | MCP protocol support |

#### Try the API

```bash
# List all API endpoints
curl http://localhost:8002/docs

# Or access Swagger UI at:
# http://localhost:8002/docs
```

### Afternoon: Services and Database

#### Database Models

Explore: `langbuilder/src/backend/base/langbuilder/services/database/models/`

Key models:
- `User` - User accounts
- `Flow` - Workflow definitions
- `Folder` - Flow organization
- `ApiKey` - API authentication
- `MessageTable` - Chat messages

#### Service Layer

Explore: `langbuilder/src/backend/base/langbuilder/services/`

Understand the service pattern:
```python
# Service pattern example
class FlowService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_flow(self, flow_id: UUID, user_id: UUID) -> Flow:
        # Database operations
        pass
```

### Hands-On Exercise

1. Find the endpoint that creates a new flow
2. Trace the code path from API route to database
3. Identify the Pydantic schemas used for request/response

### End of Day Checklist

- [ ] Explored API routes
- [ ] Understand service layer pattern
- [ ] Know database model locations
- [ ] Can trace a request through the backend

---

## Day 4: Frontend Deep Dive

**Goal**: Understand the React frontend, state management, and flow editor.

### Morning: Frontend Architecture

#### Key Technologies

| Library | Purpose | Version |
|---------|---------|---------|
| React | UI framework | 18.3.x |
| TypeScript | Type safety | 5.4.x |
| Zustand | State management | 4.5.x |
| @xyflow/react | Flow canvas | 12.3.x |
| TailwindCSS | Styling | 3.4.x |
| Radix UI | Component primitives | Various |

#### State Management

Explore Zustand stores in `langbuilder/src/frontend/src/stores/`:

| Store | Purpose |
|-------|---------|
| `flowStore.ts` | Flow nodes and edges |
| `flowsManagerStore.ts` | Flow list management |
| `authStore.ts` | Authentication state |
| `alertStore.ts` | Notifications |

### Afternoon: Flow Editor

#### Understanding the Canvas

Explore `langbuilder/src/frontend/src/CustomNodes/`:

```typescript
// Node structure pattern
interface NodeData {
  id: string;
  type: string;
  data: {
    // Component-specific data
  };
  position: { x: number; y: number };
}
```

#### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| FlowCanvas | `pages/FlowPage/` | Main flow editor |
| GenericNode | `CustomNodes/GenericNode/` | Node rendering |
| Sidebar | `components/Sidebar/` | Component browser |

### Hands-On Exercise

1. Find where nodes are rendered
2. Trace how a node selection updates state
3. Identify how component data flows to the node

### End of Day Checklist

- [ ] Understand Zustand store pattern
- [ ] Explored flow canvas components
- [ ] Know how state flows in the frontend
- [ ] Can trace a user interaction

---

## Day 5: First Contribution

**Goal**: Make a small, meaningful contribution to the codebase.

### Morning: Development Workflow

#### Running Tests

```bash
# From langbuilder/ directory

# Run unit tests
make unit_tests

# Run specific test file
uv run pytest src/backend/tests/unit/test_specific.py -v

# Run frontend tests
cd src/frontend
npm test
```

#### Code Quality

```bash
# Format Python code
make format_backend

# Format frontend code
cd src/frontend
npm run format

# Run linting
make lint
```

### Afternoon: First Contribution Ideas

Choose one of these beginner-friendly tasks:

#### Option 1: Add a Code Comment

1. Find a function that lacks documentation
2. Add a clear docstring explaining its purpose
3. Commit your change

#### Option 2: Fix a Minor Issue

1. Look for issues labeled `good-first-issue` on GitHub
2. Pick one and work on it
3. Submit a PR

#### Option 3: Improve a Component

1. Find a simple component in `components/`
2. Add input validation or improve error messages
3. Add a test for your change

### Contribution Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ...

# Run tests
make unit_tests

# Format code
make format

# Commit with descriptive message
git add .
git commit -m "feat: Add description of your change"

# Push and create PR
git push origin feature/your-feature-name
```

### End of Day Checklist

- [ ] Ran tests successfully
- [ ] Made a small code change
- [ ] Formatted code correctly
- [ ] Created a commit with good message

---

## Week 1 Summary

By the end of Week 1, you should be able to:

1. **Run the development environment** confidently
2. **Navigate the codebase** and find relevant files
3. **Understand the architecture** - how frontend and backend interact
4. **Trace code paths** from UI action to database
5. **Make small changes** and run tests

## Resources for Week 1

### Documentation

- [Local Development Guide](./local-development.md)
- [Debugging Guide](./debugging-guide.md)

### Key Files Quick Reference

| Purpose | Path |
|---------|------|
| Backend entry | `langbuilder/langbuilder_launcher.py` |
| API routes | `langbuilder/src/backend/base/langbuilder/api/` |
| Components | `langbuilder/src/backend/base/langbuilder/components/` |
| Frontend entry | `langbuilder/src/frontend/src/App.tsx` |
| State stores | `langbuilder/src/frontend/src/stores/` |
| Tests | `langbuilder/src/backend/tests/` |

### Useful Commands

| Command | Purpose |
|---------|---------|
| `make backend` | Start backend server |
| `npm start` | Start frontend dev server |
| `make unit_tests` | Run backend tests |
| `make format` | Format all code |
| `make lint` | Run linting |

## Next Steps

Continue to [30-Day Roadmap](./30-day-roadmap.md) for deeper learning.

---

*Generated by CloudGeometry AIx SDLC - Onboarding Documentation*
