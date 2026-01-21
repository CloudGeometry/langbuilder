# LangBuilder Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the LangBuilder project, covering testing philosophy, principles, and implementation guidelines.

## Testing Philosophy

### Core Principles

1. **Test Pyramid Approach**: Focus on a broad base of fast unit tests, fewer integration tests, and minimal E2E tests
2. **Shift-Left Testing**: Catch issues early in the development cycle through automated testing
3. **Continuous Testing**: Tests run automatically on every code change via CI/CD
4. **Test Independence**: Each test should be isolated and not depend on other tests
5. **Deterministic Tests**: Tests should produce consistent results across runs

### Test Hierarchy

```
                    /\
                   /  \
                  / E2E \           <- Playwright Tests (150+ specs)
                 /--------\
                /          \
               / Integration \      <- pytest integration (36+ files)
              /----------------\
             /                  \
            /    Unit Tests      \  <- pytest + Jest (253+ files)
           /----------------------\
```

## Test Categories

### 1. Unit Tests

**Purpose**: Test individual functions, methods, and classes in isolation

**Characteristics**:
- Fast execution (< 100ms per test)
- No external dependencies (mocked)
- High code coverage target (> 80%)

**Backend (Python)**:
- Framework: pytest
- Location: `src/backend/tests/unit/`
- Command: `make unit_tests`

**Frontend (TypeScript)**:
- Framework: Jest + Testing Library
- Location: `src/frontend/src/**/__tests__/`
- Command: `npm test`

### 2. Integration Tests

**Purpose**: Test component interactions and system boundaries

**Characteristics**:
- Tests actual service integration
- May require external resources (databases, APIs)
- Moderate execution time

**Backend**:
- Location: `src/backend/tests/integration/`
- Command: `make integration_tests`

**Frontend**:
- Location: `src/frontend/tests/core/integrations/`
- Framework: Playwright

### 3. End-to-End (E2E) Tests

**Purpose**: Test complete user workflows through the UI

**Characteristics**:
- Simulates real user behavior
- Tests full stack integration
- Longer execution time
- Browser-based testing

**Framework**: Playwright
**Location**: `src/frontend/tests/`

### 4. Performance Tests

**Purpose**: Validate system performance and scalability

**Types**:
- Server initialization tests
- Load testing (Locust)
- Benchmark tests

**Location**: `src/backend/tests/performance/` and `src/backend/tests/locust/`

## Coverage Goals

### Backend Coverage Targets

| Category | Target | Current |
|----------|--------|---------|
| Overall | > 70% | TBD |
| Core Logic | > 85% | TBD |
| API Endpoints | > 80% | TBD |
| Components | > 75% | TBD |

### Frontend Coverage Targets

| Category | Target | Current |
|----------|--------|---------|
| Overall | > 60% | TBD |
| Components | > 70% | TBD |
| Utilities | > 80% | TBD |
| Stores | > 75% | TBD |

### Coverage Exclusions

Files excluded from coverage metrics:
- Test files themselves
- Alembic migrations (`*/alembic/*`)
- `__init__.py` files
- Type stubs (`.d.ts`)
- Test setup files

## Quality Gates

### Pre-Commit

1. Ruff linting and formatting (Python)
2. Biome check (TypeScript/JavaScript)
3. Starter project template validation

### CI Requirements

1. All unit tests pass
2. All integration tests pass (excluding API key tests)
3. Linting passes (Ruff, Biome)
4. Type checking passes (MyPy)
5. Coverage thresholds met

### Release Requirements

1. All CI requirements met
2. E2E tests pass
3. Performance regression tests pass
4. Template tests validate
5. Cross-platform tests (Python 3.10-3.13)

## Test Execution Strategy

### Local Development

```bash
# Quick feedback loop
make unit_tests async=true lf=true  # Run failed tests first

# Full local validation
make tests
```

### CI Pipeline

1. **Path Filtering**: Only run relevant tests based on changed files
2. **Parallel Execution**: Tests split across multiple shards
3. **Retry Logic**: Flaky tests retried up to 3 times
4. **Caching**: Dependency caching for faster builds

### Test Prioritization

| Priority | Test Type | When to Run |
|----------|-----------|-------------|
| P0 | Unit Tests | Every commit |
| P1 | Integration Tests | PR creation |
| P2 | E2E Tests (core) | PR with `lgtm` label |
| P3 | Full E2E Suite | Release candidates |
| P4 | Performance Tests | Scheduled/Release |

## Test Data Management

### Principles

1. **Isolation**: Each test creates and cleans up its own data
2. **Determinism**: Use fixed seeds for random data generation
3. **Minimal Data**: Create only necessary test data
4. **Factory Pattern**: Use factories for complex object creation

### Strategies

- **Fixtures**: pytest fixtures for reusable test setup
- **Factories**: Faker for generating test data
- **Mocking**: External services mocked using `pytest-mock`, `respx`
- **In-Memory DB**: SQLite with StaticPool for test isolation

## Async Testing Strategy

LangBuilder heavily uses async operations. Testing strategy:

1. **pytest-asyncio**: Automatic async test detection (`asyncio_mode = "auto"`)
2. **Function-scoped loops**: Each test gets fresh event loop
3. **Async fixtures**: Support for async setup/teardown
4. **httpx AsyncClient**: Async API testing

## Flaky Test Management

### Detection

- Use `pytest-flakefinder` to identify flaky tests
- Track test duration variations with `.test_durations`

### Mitigation

- Use `pytest-rerunfailures` for automatic retries
- Implement proper async cleanup
- Add explicit waits instead of sleep
- Use `blockbuster` for detecting blocking calls

## Cross-Platform Testing

### Python Versions

Tests run against:
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

### Operating Systems

- Linux (primary CI)
- Windows (cross-platform workflow)
- macOS (cross-platform workflow)

## Continuous Improvement

### Metrics to Track

1. Test execution time trends
2. Flaky test rate
3. Coverage trends
4. Test failure patterns

### Review Process

1. Monthly test health review
2. Quarterly coverage analysis
3. Performance baseline updates

---
*Last Updated: Auto-generated by CG AIx SDLC*
