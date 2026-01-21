# Test Coverage Analysis

## Overview

This document analyzes the test coverage configuration, current status, and recommendations for improving coverage in the LangBuilder project.

## Coverage Configuration

### Backend Coverage (pytest-cov)

**Configuration in `pyproject.toml`:**

```toml
[tool.coverage.run]
command_line = """
    -m pytest --ignore=tests/integration
    --cov --cov-report=term --cov-report=html
    --instafail -ra -n auto -m "not api_key_required"
"""
source = ["src/backend/base/langbuilder/"]
omit = ["*/alembic/*", "tests/*", "*/__init__.py"]

[tool.coverage.report]
sort = "Stmts"
skip_empty = true
show_missing = false
ignore_errors = true

[tool.coverage.html]
directory = "coverage"
```

### Frontend Coverage (Jest)

**Configuration in `jest.config.js`:**

```javascript
collectCoverageFrom: [
  "src/**/*.{ts,tsx}",
  "!src/**/*.{test,spec}.{ts,tsx}",
  "!src/**/tests/**",
  "!src/**/__tests__/**",
  "!src/setupTests.ts",
  "!src/vite-env.d.ts",
  "!src/**/*.d.ts",
],
coverageDirectory: "coverage",
coverageReporters: ["text", "lcov", "html", "json-summary"],
coveragePathIgnorePatterns: ["/node_modules/", "/tests/"],
```

## Coverage Exclusions

### Backend Exclusions

| Pattern | Reason |
|---------|--------|
| `*/alembic/*` | Database migrations are tested via integration |
| `tests/*` | Test code itself |
| `*/__init__.py` | Package initialization files |
| Bundled components | Generated/vendor code |
| Legacy files | Deprecated code paths |

### Frontend Exclusions

| Pattern | Reason |
|---------|--------|
| `*.{test,spec}.{ts,tsx}` | Test files |
| `**/tests/**` | Test directories |
| `**/__tests__/**` | Jest test directories |
| `setupTests.ts` | Test configuration |
| `vite-env.d.ts` | Type definitions |
| `*.d.ts` | Declaration files |

## Dynamic Coverage Configuration

The project uses dynamic coverage configuration via `scripts/generate_coverage_config.py` to:

1. Exclude bundled components from coverage
2. Exclude legacy files
3. Generate `.coveragerc` at build time

## Coverage Reporting

### CI Integration

Coverage is reported to Codecov in CI:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v5
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage.xml
    flags: backend
    name: backend-coverage-group-${{ matrix.group }}
```

### Report Types

| Type | Format | Location |
|------|--------|----------|
| Terminal | Text summary | stdout |
| HTML | Interactive | `coverage/` or `htmlcov/` |
| XML | Machine-readable | `coverage.xml` |
| LCOV | Standard format | `coverage/lcov.info` |
| JSON Summary | Metrics | `coverage/coverage-summary.json` |

## Coverage Analysis by Module

### High-Priority Coverage Areas

| Module | Importance | Notes |
|--------|------------|-------|
| `langbuilder/graph/` | Critical | Core flow execution |
| `langbuilder/api/` | High | REST API endpoints |
| `langbuilder/services/` | High | Business logic |
| `langbuilder/components/` | Medium | Component implementations |

### Coverage Gaps

Based on the test inventory, potential gaps include:

1. **Authentication flows**: Limited integration coverage
2. **Error handling paths**: Exception scenarios
3. **Edge cases**: Boundary conditions
4. **Async cleanup**: Resource management
5. **Webhook handling**: External integrations

## Coverage Improvement Recommendations

### Short-term (1-2 sprints)

1. **Add missing API tests**
   - Endpoint error responses
   - Authentication edge cases
   - Pagination scenarios

2. **Improve component coverage**
   - Add tests for new Amazon components (Aurora MySQL)
   - Test SQL executor edge cases

3. **Error path testing**
   - Invalid input handling
   - Network failure scenarios
   - Timeout handling

### Medium-term (1-2 quarters)

1. **Integration test expansion**
   - End-to-end flow tests
   - Multi-component interactions
   - Database migration tests

2. **Performance coverage**
   - Add more benchmark tests
   - Memory leak detection
   - Concurrency testing

### Long-term

1. **Mutation testing**
   - Implement mutation testing to validate test effectiveness

2. **Property-based testing**
   - Use Hypothesis for generative testing

3. **Contract testing**
   - API contract validation

## Running Coverage Reports

### Backend

```bash
# Run with coverage
make unit_tests args="--cov --cov-report=html"

# View HTML report
open coverage/index.html

# Get terminal summary
uv run pytest --cov --cov-report=term-missing
```

### Frontend

```bash
cd src/frontend

# Run with coverage
npm test -- --coverage

# View report
open coverage/lcov-report/index.html
```

## Coverage Thresholds

### Recommended Thresholds

| Metric | Minimum | Target |
|--------|---------|--------|
| Line Coverage | 60% | 80% |
| Branch Coverage | 50% | 70% |
| Function Coverage | 70% | 85% |

### Enforcement

Currently, coverage thresholds are not enforced in CI. Recommended approach:

```yaml
# Add to CI workflow
- name: Check coverage thresholds
  run: |
    coverage report --fail-under=60
```

## Tracking Coverage Over Time

### Metrics to Monitor

1. **Overall coverage trend**: Weekly snapshots
2. **Coverage per PR**: Delta reporting
3. **Module-level coverage**: Critical path focus
4. **Test-to-code ratio**: Balance indicator

### Tools

- **Codecov**: PR coverage diffs
- **Coverage badges**: README visibility
- **Trend charts**: Historical analysis

---
*Generated by CG AIx SDLC - Testing Documentation*
