# Testing Patterns and Conventions

## Overview

This document describes the testing patterns, conventions, and best practices used in the LangBuilder project for both Python (backend) and TypeScript (frontend) codebases.

## Python Testing Patterns

### Async Testing Pattern

LangBuilder uses `pytest-asyncio` with automatic mode:

```python
# pyproject.toml
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

**Test Example:**

```python
# Async test function - automatically detected
async def test_create_flow(client, logged_in_headers):
    response = await client.post(
        "api/v1/flows/",
        json=flow_data,
        headers=logged_in_headers
    )
    assert response.status_code == 201
```

### Fixture Pattern

#### Session-Scoped Database Fixture

```python
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()
```

#### Async Session Fixture

```python
@pytest.fixture
async def async_session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

#### User Authentication Fixture

```python
@pytest.fixture
async def active_user(client):
    db_manager = get_db_service()
    async with db_manager.with_session() as session:
        user = User(
            username="activeuser",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        # ... setup logic
        yield user
    # Cleanup logic follows
```

### Client Fixture Pattern

```python
@pytest.fixture(name="client")
async def client_fixture(session, monkeypatch, request, load_flows_dir):
    if "noclient" in request.keywords:
        yield
    else:
        # Setup temp database
        db_dir = tempfile.mkdtemp()
        db_path = Path(db_dir) / "test.db"
        monkeypatch.setenv("LANGBUILDER_DATABASE_URL", f"sqlite:///{db_path}")

        app = create_app()
        async with (
            LifespanManager(app) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://testserver/"
            ) as client,
        ):
            yield client
```

### Marker Pattern

```python
# Mark tests requiring API keys
@pytest.mark.api_key_required
async def test_openai_integration():
    pass

# Mark slow tests
@pytest.mark.slow
def test_heavy_computation():
    pass

# Mark benchmark tests
@pytest.mark.benchmark
def test_performance():
    pass

# Exclude blockbuster checks
@pytest.mark.no_blockbuster
async def test_blocking_operation():
    pass
```

### Mocking Pattern

#### Using pytest-mock

```python
def test_with_mock(mocker):
    mock_service = mocker.patch('langbuilder.services.some_service')
    mock_service.return_value = expected_value

    result = function_under_test()

    mock_service.assert_called_once()
```

#### Using respx for HTTP Mocking

```python
@respx.mock
async def test_external_api():
    respx.get("https://api.example.com/data").mock(
        return_value=httpx.Response(200, json={"result": "ok"})
    )

    response = await external_api_call()
    assert response == {"result": "ok"}
```

### Parametrize Pattern

```python
@pytest.mark.parametrize("input_value,expected", [
    ("valid_input", True),
    ("", False),
    (None, False),
    ("special@chars", True),
])
def test_validation(input_value, expected):
    result = validate(input_value)
    assert result == expected
```

### Test Data Pattern

```python
# In conftest.py
def pytest_configure(config):
    data_path = Path(__file__).parent.absolute() / "data"
    pytest.BASIC_EXAMPLE_PATH = data_path / "basic_example.json"
    pytest.COMPLEX_EXAMPLE_PATH = data_path / "complex_example.json"
    # ... more paths

# Usage in tests
def test_with_example_data(basic_graph_data):
    # basic_graph_data fixture loads from pytest.BASIC_EXAMPLE_PATH
    assert "nodes" in basic_graph_data
```

## TypeScript Testing Patterns

### Jest Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = jest.fn();
    render(<MyComponent onClick={handleClick} />);

    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Playwright E2E Pattern

```typescript
import { test, expect, Page } from "@playwright/test";

test.describe("Feature Name", () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto("/");
    await page.waitForSelector('[data-testid="app-loaded"]');
  });

  test("should perform action @release @workspace", async () => {
    // Test tagged for release and workspace suites
    await page.click('[data-testid="action-button"]');
    await expect(page.locator('[data-testid="result"]')).toBeVisible();
  });
});
```

### Page Object Pattern

```typescript
// pages/FlowPage.ts
export class FlowPage {
  constructor(private page: Page) {}

  async createFlow(name: string) {
    await this.page.click('[data-testid="new-flow"]');
    await this.page.fill('[data-testid="flow-name"]', name);
    await this.page.click('[data-testid="save-flow"]');
  }

  async waitForFlowLoaded() {
    await this.page.waitForSelector('[data-testid="flow-canvas"]');
  }
}

// Usage in test
test("create flow", async ({ page }) => {
  const flowPage = new FlowPage(page);
  await flowPage.createFlow("My Flow");
  await flowPage.waitForFlowLoaded();
});
```

### Test Tags Pattern

```typescript
// Tag tests for selective execution
test("feature test @components", async () => {});
test("api test @api", async () => {});
test("database test @database", async () => {});
test("full test @release", async () => {});
```

## Common Testing Conventions

### Naming Conventions

**Python:**
- Test files: `test_<module_name>.py`
- Test functions: `test_<what_is_being_tested>`
- Test classes: `Test<ClassName>`

**TypeScript:**
- Test files: `<module_name>.spec.ts` or `<module_name>.test.ts`
- Test suites: `describe('<ComponentName>', () => {})`
- Test cases: `it('should <expected behavior>', () => {})`

### Assertion Patterns

**Python:**
```python
# Use native assertions
assert result == expected
assert "error" in response.text
assert response.status_code == 200

# With pytest helpers
from pytest import raises
with raises(ValueError):
    function_that_raises()
```

**TypeScript:**
```typescript
// Jest
expect(result).toBe(expected);
expect(result).toEqual(expected);
expect(result).toContain(item);
expect(fn).toThrow(Error);

// Playwright
await expect(locator).toBeVisible();
await expect(locator).toHaveText('expected');
await expect(page).toHaveURL(/expected/);
```

### Cleanup Pattern

**Python:**
```python
@pytest.fixture
async def resource():
    # Setup
    resource = await create_resource()
    yield resource
    # Teardown
    await cleanup_resource(resource)
```

**TypeScript:**
```typescript
test.afterEach(async ({ page }) => {
  // Cleanup after each test
  await page.evaluate(() => localStorage.clear());
});

test.afterAll(async () => {
  // Global cleanup
});
```

### Retry Pattern for Flaky Tests

**Python:**
```python
# Using pytest-rerunfailures
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_potentially_flaky():
    pass
```

**Playwright:**
```typescript
// In playwright.config.ts
retries: process.env.CI ? 2 : 3,

// Or per-test
test("flaky test", async ({ page }) => {
  test.info().annotations.push({ type: 'retries', description: '3' });
});
```

## Anti-Patterns to Avoid

### 1. Test Interdependence
```python
# BAD - tests depend on order
def test_create_user():
    global user_id
    user_id = create_user()

def test_delete_user():
    delete_user(user_id)  # Depends on previous test
```

### 2. Hardcoded Test Data
```python
# BAD
def test_user():
    user = create_user(email="john@example.com")  # Hardcoded

# GOOD
def test_user(faker):
    user = create_user(email=faker.email())  # Generated
```

### 3. Sleep-Based Waits
```typescript
// BAD
await page.click('#button');
await page.waitForTimeout(5000);  // Arbitrary wait

// GOOD
await page.click('#button');
await page.waitForSelector('#result');  // Explicit wait
```

### 4. Testing Implementation Details
```python
# BAD - testing private methods
def test_internal_method():
    assert obj._private_method() == expected

# GOOD - testing public interface
def test_public_behavior():
    assert obj.public_method() == expected
```

---
*Generated by CG AIx SDLC - Testing Documentation*
