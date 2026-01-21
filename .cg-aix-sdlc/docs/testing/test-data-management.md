# Test Data Management

## Overview

This document describes the strategies and patterns for managing test data in the LangBuilder project, including fixtures, factories, mocking, and database setup.

## Test Data Strategy

### Principles

1. **Isolation**: Each test creates its own data and cleans up after
2. **Determinism**: Tests produce consistent results
3. **Minimal Data**: Create only what's needed for the test
4. **Real-ish Data**: Use realistic data that represents production scenarios

## Backend Fixtures

### Database Session Fixtures

#### Synchronous Session (SQLite in-memory)

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

#### Async Session (aiosqlite)

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

### User Fixtures

#### Active User

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
        stmt = select(User).where(User.username == user.username)
        if existing := (await session.exec(stmt)).first():
            user = existing
        else:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        yield UserRead.model_validate(user, from_attributes=True)
    # Cleanup logic...
```

#### Superuser

```python
@pytest.fixture
async def active_super_user(client):
    # Similar to active_user but with is_superuser=True
    pass
```

#### Authenticated Headers

```python
@pytest.fixture
async def logged_in_headers(client, active_user):
    login_data = {"username": active_user.username, "password": "testpassword"}
    response = await client.post("api/v1/login", data=login_data)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
```

### Flow Fixtures

#### Basic Flow

```python
@pytest.fixture
async def flow(client, json_flow, active_user):
    loaded_json = json.loads(json_flow)
    flow_data = FlowCreate(
        name="test_flow",
        data=loaded_json.get("data"),
        user_id=active_user.id
    )
    flow = Flow.model_validate(flow_data)
    async with session_getter(get_db_service()) as session:
        session.add(flow)
        await session.commit()
        await session.refresh(flow)
        yield flow
        await session.delete(flow)
        await session.commit()
```

#### Flow from JSON Files

```python
@pytest.fixture
def json_flow():
    return pytest.BASIC_EXAMPLE_PATH.read_text(encoding="utf-8")

@pytest.fixture
def json_flow_with_prompt_and_history():
    return pytest.BASIC_CHAT_WITH_PROMPT_AND_HISTORY.read_text(encoding="utf-8")
```

### API Key Fixture

```python
@pytest.fixture
async def created_api_key(active_user):
    hashed = get_password_hash("random_key")
    api_key = ApiKey(
        name="test_api_key",
        user_id=active_user.id,
        api_key="random_key",
        hashed_api_key=hashed,
    )
    db_manager = get_db_service()
    async with session_getter(db_manager) as session:
        session.add(api_key)
        await session.commit()
        await session.refresh(api_key)
        yield api_key
        await session.delete(api_key)
        await session.commit()
```

## Test Data Files

### JSON Flow Examples

Located in `src/backend/tests/data/`:

| File | Purpose |
|------|---------|
| `basic_example.json` | Simple flow structure |
| `complex_example.json` | Complex multi-node flow |
| `Openapi.json` | OpenAPI-based flow |
| `grouped_chat.json` | Grouped chat flow |
| `ChatInputTest.json` | Chat input testing |
| `Vector_store.json` | Vector store testing |
| `MemoryChatbotNoLLM.json` | Memory without LLM |
| `LoopTest.json` | Loop flow testing |
| `WebhookTest.json` | Webhook endpoint testing |

### Loading Test Data

```python
def pytest_configure(config):
    data_path = Path(__file__).parent.absolute() / "data"

    pytest.BASIC_EXAMPLE_PATH = data_path / "basic_example.json"
    pytest.COMPLEX_EXAMPLE_PATH = data_path / "complex_example.json"
    # ... more paths

    # Validate paths exist
    for path in [pytest.BASIC_EXAMPLE_PATH, pytest.COMPLEX_EXAMPLE_PATH]:
        assert path.exists()
```

## Mocking Strategies

### External Service Mocking

#### Using respx for HTTP

```python
import respx
from httpx import Response

@respx.mock
async def test_external_api():
    respx.get("https://api.openai.com/v1/models").mock(
        return_value=Response(200, json={"data": []})
    )
    # Test code that calls OpenAI
```

#### Using pytest-mock

```python
def test_with_mock(mocker):
    mock_llm = mocker.patch('langbuilder.services.llm_service')
    mock_llm.generate.return_value = "mocked response"

    result = function_under_test()
    assert result == "mocked response"
```

### Database Mocking

#### NoOp Session

```python
@pytest.fixture
def use_noop_session(monkeypatch):
    monkeypatch.setenv("LANGBUILDER_USE_NOOP_DATABASE", "1")
    yield
    monkeypatch.undo()
```

### Environment Variable Mocking

```python
@pytest.fixture(autouse=True)
def deactivate_tracing(monkeypatch):
    monkeypatch.setenv("LANGBUILDER_DEACTIVATE_TRACING", "true")
    yield
    monkeypatch.undo()

@pytest.fixture(name="distributed_env")
def _setup_env(monkeypatch):
    monkeypatch.setenv("LANGBUILDER_CACHE_TYPE", "redis")
    monkeypatch.setenv("LANGBUILDER_REDIS_HOST", "result_backend")
    monkeypatch.setenv("LANGBUILDER_REDIS_PORT", "6379")
```

## Factory Pattern

### Using Faker

```python
from faker import Faker

fake = Faker()

def create_test_user(**kwargs):
    return User(
        username=kwargs.get('username', fake.user_name()),
        email=kwargs.get('email', fake.email()),
        password=kwargs.get('password', fake.password()),
        is_active=kwargs.get('is_active', True),
    )

def create_test_flow(**kwargs):
    return Flow(
        name=kwargs.get('name', fake.sentence(nb_words=3)),
        description=kwargs.get('description', fake.text()),
        data=kwargs.get('data', {}),
    )
```

## Database Setup/Teardown

### Transaction Cleanup

```python
async def delete_transactions_by_flow_id(db: AsyncSession, flow_id: UUID):
    if not flow_id:
        return
    stmt = select(TransactionTable).where(TransactionTable.flow_id == flow_id)
    transactions = await db.exec(stmt)
    for transaction in transactions:
        await db.delete(transaction)

async def _delete_transactions_and_vertex_builds(session, flows: list[Flow]):
    flow_ids = [flow.id for flow in flows]
    for flow_id in flow_ids:
        await delete_vertex_builds_by_flow_id(session, flow_id)
        await delete_transactions_by_flow_id(session, flow_id)
```

### Temporary Database

```python
@pytest.fixture
async def client_fixture(session, monkeypatch, request, load_flows_dir):
    db_dir = tempfile.mkdtemp()
    db_path = Path(db_dir) / "test.db"
    monkeypatch.setenv("LANGBUILDER_DATABASE_URL", f"sqlite:///{db_path}")

    # ... test execution ...

    # Cleanup
    with suppress(FileNotFoundError):
        await anyio.Path(db_path).unlink()
```

## Frontend Test Data

### Test Fixtures for Playwright

```typescript
// Test data constants
const TEST_FLOW = {
  name: "Test Flow",
  description: "A test flow for E2E testing",
};

const TEST_USER = {
  username: "testuser",
  password: "testpassword",
};
```

### Mock Data for Jest

```typescript
// __mocks__/api.ts
export const mockFlows = [
  { id: "1", name: "Flow 1", nodes: [] },
  { id: "2", name: "Flow 2", nodes: [] },
];

export const mockUser = {
  id: "user-1",
  username: "testuser",
  email: "test@example.com",
};
```

## Best Practices

### Do's

1. **Use fixtures for setup/teardown** - Ensures cleanup
2. **Isolate test databases** - Each test gets fresh state
3. **Mock external services** - Avoid network calls
4. **Use factories for complex objects** - Reduces boilerplate
5. **Version control test data files** - Track changes

### Don'ts

1. **Don't share state between tests** - Causes flakiness
2. **Don't use production data** - Security and privacy
3. **Don't hardcode credentials** - Use environment variables
4. **Don't create excessive data** - Slows tests
5. **Don't rely on test order** - Tests should be independent

## Data Cleanup Strategies

### Fixture-Based Cleanup

```python
@pytest.fixture
async def resource():
    resource = await create_resource()
    yield resource
    await delete_resource(resource)
```

### Transaction Rollback

```python
@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.begin_nested()  # Savepoint
        yield conn
        await conn.rollback()  # Rollback to savepoint
```

### Manual Cleanup in Tests

```python
async def test_something(client):
    resource = await create_resource()
    try:
        # Test logic
        pass
    finally:
        await delete_resource(resource)
```

---
*Generated by CG AIx SDLC - Testing Documentation*
