# Test Infrastructure

## Overview

This document describes the test tooling, configuration, and CI/CD integration for the LangBuilder project.

## Backend Test Infrastructure

### pytest Configuration

**Location:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
timeout = 150
timeout_method = "signal"
minversion = "6.0"
testpaths = ["src/backend/tests"]
console_output_style = "progress"
filterwarnings = ["ignore::DeprecationWarning", "ignore::ResourceWarning"]
log_cli = true
log_cli_format = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
markers = [
    "async_test",
    "api_key_required",
    "no_blockbuster",
    "benchmark",
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow-running tests"
]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
addopts = "-p no:benchmark"
```

### pytest Plugins

| Plugin | Version | Purpose |
|--------|---------|---------|
| pytest-asyncio | >=0.23.0 | Async test support |
| pytest-cov | >=5.0.0 | Coverage reporting |
| pytest-mock | >=3.14.0 | Mocking utilities |
| pytest-xdist | >=3.6.0 | Parallel execution |
| pytest-sugar | >=1.0.0 | Better test output |
| pytest-instafail | >=0.5.0 | Immediate failure reporting |
| pytest-split | >=0.9.0 | Test splitting for CI |
| pytest-flakefinder | >=1.1.0 | Flaky test detection |
| pytest-rerunfailures | >=15.0 | Automatic retries |
| pytest-timeout | >=2.3.1 | Test timeout enforcement |
| pytest-profiling | >=1.7.0 | Performance profiling |
| respx | >=0.21.1 | HTTP mocking |
| blockbuster | >=1.5.20 | Blocking call detection |
| hypothesis | >=6.123.17 | Property-based testing |

### Test Parallelization

Tests are split across 5 shards in CI:

```yaml
strategy:
  matrix:
    splitCount: [5]
    group: [1, 2, 3, 4, 5]
```

Using `pytest-split` with timing data:
```bash
pytest --splits 5 --group 1 \
    --durations-path src/backend/tests/.test_durations \
    --splitting-algorithm least_duration
```

## Frontend Test Infrastructure

### Jest Configuration

**Location:** `src/frontend/jest.config.js`

```javascript
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  injectGlobals: true,
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
  },
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.ts"],
  setupFiles: ["<rootDir>/jest.setup.js"],
  testMatch: [
    "<rootDir>/src/**/__tests__/**/*.{test,spec}.{ts,tsx}",
    "<rootDir>/src/**/*.{test,spec}.{ts,tsx}",
  ],
  transform: {
    "^.+\\.(ts|tsx)$": "ts-jest",
  },
};
```

### Playwright Configuration

**Location:** `src/frontend/playwright.config.ts`

```typescript
export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 3,
  workers: 2,
  timeout: 5 * 60 * 1000, // 5 minutes
  reporter: process.env.CI ? "blob" : "html",

  use: {
    baseURL: `http://localhost:${PORT || 3000}/`,
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        contextOptions: {
          permissions: ["clipboard-read", "clipboard-write"],
        },
      },
    },
  ],

  webServer: [
    {
      command: "uv run uvicorn --factory langbuilder.main:create_app --host localhost --port 7860",
      port: 7860,
      env: {
        LANGBUILDER_DATABASE_URL: "sqlite:///./temp",
        LANGBUILDER_AUTO_LOGIN: "true",
      },
      reuseExistingServer: true,
      timeout: 120 * 750,
    },
    {
      command: "npm start",
      port: PORT || 3000,
      reuseExistingServer: true,
    },
  ],
});
```

## CI/CD Pipeline

### GitHub Actions Workflows

#### Main CI Workflow (`ci.yml`)

```yaml
name: CI

on:
  workflow_call:
  workflow_dispatch:
  pull_request:
    types: [synchronize, labeled]
  merge_group:

jobs:
  set-ci-condition:
    # Determines if CI should run based on labels
    outputs:
      should-run-ci: ${{ contains(labels, 'lgtm') && !draft }}

  path-filter:
    # Filters paths to determine which tests to run
    outputs:
      python: ${{ steps.filter.outputs.python }}
      frontend: ${{ steps.filter.outputs.frontend }}

  test-backend:
    needs: [path-filter, set-ci-condition]
    if: ${{ needs.path-filter.outputs.python == 'true' }}
    uses: ./.github/workflows/python_test.yml

  test-frontend:
    needs: [path-filter, set-ci-condition]
    if: ${{ needs.path-filter.outputs.frontend == 'true' }}
    uses: ./.github/workflows/typescript_test.yml
```

#### Backend Tests Workflow (`python_test.yml`)

```yaml
jobs:
  build:
    name: Unit Tests - Python ${{ matrix.python-version }} - Group ${{ matrix.group }}
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
        splitCount: [5]
        group: [1, 2, 3, 4, 5]
    steps:
      - uses: astral-sh/setup-uv@v6
      - name: Run unit tests
        uses: nick-fields/retry@v3
        with:
          timeout_minutes: 12
          max_attempts: 2
          command: make unit_tests args="--splits 5 --group ${{ matrix.group }}"

  integration-tests:
    name: Integration Tests
    steps:
      - name: Run integration tests
        run: make integration_tests_no_api_keys
```

#### Frontend Tests Workflow (`typescript_test.yml`)

```yaml
jobs:
  determine-test-suite:
    # Calculates optimal shard count based on test count
    outputs:
      matrix: ${{ steps.setup-matrix.outputs.matrix }}

  setup-and-test:
    name: Playwright Tests - Shard ${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
    strategy:
      matrix: ${{ fromJson(needs.determine-test-suite.outputs.matrix) }}
    steps:
      - name: Execute Playwright Tests
        uses: nick-fields/retry@v3
        with:
          command: npx playwright test --shard ${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
```

### Test Sharding Strategy

**Backend:**
- Fixed 5 shards using `pytest-split`
- Timing-based distribution from `.test_durations`

**Frontend:**
- Dynamic shard calculation: 1 shard per 5 tests
- Maximum 40 shards
- Based on Playwright test count

### Caching Strategy

**Python Dependencies:**
```yaml
uses: astral-sh/setup-uv@v6
with:
  enable-cache: true
  cache-dependency-glob: "uv.lock"
```

**Node Dependencies:**
```yaml
uses: actions/setup-node@v4
with:
  cache: "npm"
  cache-dependency-path: ./src/frontend/package-lock.json
```

**Playwright Browsers:**
```yaml
uses: actions/cache@v4
with:
  path: ${{ env.PLAYWRIGHT_BROWSERS_PATH }}
  key: playwright-${{ env.PLAYWRIGHT_VERSION }}-chromium-${{ runner.os }}
```

## Load Testing (Locust)

### Configuration

```bash
make locust \
  locust_users=10 \
  locust_spawn_rate=1 \
  locust_host=http://localhost:7860 \
  locust_time=300s \
  locust_file=src/backend/tests/locust/locustfile.py
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API authentication | - |
| `FLOW_ID` | Target flow ID | - |
| `LANGBUILDER_HOST` | Target host | localhost:7860 |
| `MIN_WAIT` | Minimum wait time | 2000ms |
| `MAX_WAIT` | Maximum wait time | 5000ms |
| `REQUEST_TIMEOUT` | Request timeout | 30.0s |

## Local Test Execution

### Makefile Targets

```makefile
# Unit tests
make unit_tests                    # Run all unit tests
make unit_tests async=true         # Parallel execution
make unit_tests lf=true            # Re-run last failed
make unit_tests ff=true            # Failed first
make unit_tests args="--cov"       # With coverage

# Integration tests
make integration_tests             # All integration tests
make integration_tests_no_api_keys # Without API keys
make integration_tests_api_keys    # Only API key tests

# All tests
make tests                         # Unit + integration + coverage

# Template tests
make template_tests               # Starter project validation
```

### Frontend Commands

```bash
cd src/frontend

# Jest unit tests
npm test                          # Run all Jest tests
npm test -- --coverage            # With coverage
npm test -- --watch               # Watch mode

# Playwright E2E tests
npx playwright test               # Run all E2E tests
npx playwright test --ui          # Interactive mode
npx playwright test --debug       # Debug mode
npx playwright show-report        # View HTML report
```

## Artifact Management

### CI Artifacts

| Artifact | Retention | Purpose |
|----------|-----------|---------|
| Coverage XML | 30 days | Codecov upload |
| HTML Coverage | 30 days | Manual review |
| Playwright Reports | 1 day (blob), 14 days (HTML) | Test debugging |

### Report Merging

Playwright reports are merged after all shards complete:
```yaml
- name: Merge into HTML Report
  run: npx playwright merge-reports --reporter html ./all-blob-reports
```

## Monitoring and Debugging

### Test Duration Tracking

The `.test_durations` file tracks test execution times for optimal splitting:
```
# File: src/backend/tests/.test_durations
# Format: JSON mapping test paths to duration in seconds
```

### Blockbuster Integration

Detects blocking I/O calls in async code:
```python
@pytest.fixture(autouse=False)
def blockbuster(request):
    with blockbuster_ctx() as bb:
        # Configure allowed blocking calls
        bb.functions["os.stat"].can_block_in("specific/path.py", "function")
        yield bb
```

---
*Generated by CG AIx SDLC - Testing Documentation*
