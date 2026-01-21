# Quality Gates

## Overview

This document defines the quality criteria and thresholds that must be met before code can be merged or released in the LangBuilder project.

## Pre-Commit Hooks

### Configuration

**Location:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-case-conflict
      - id: end-of-file-fixer
        files: \.(py|js|ts)$
      - id: mixed-line-ending
        files: \.(py|js|ts)$
        args: [--fix=lf]
      - id: trailing-whitespace

  - repo: local
    hooks:
      - id: ruff
        name: ruff check
        entry: uv run ruff check
        language: system
        types_or: [python, pyi]
        args: [--fix]

      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types_or: [python, pyi]

      - id: local-biome-check
        name: biome check
        entry: bash -c 'cd src/frontend && npx @biomejs/biome check --write'
        files: "\\.(jsx?|tsx?|c(js|ts)|m(js|ts)|d\\.(ts|cts|mts)|jsonc?)$"

      - id: validate-starter-projects
        name: Validate Starter Project Templates
        entry: uv run python src/backend/tests/unit/template/test_starter_projects.py
        files: ^src/backend/base/langbuilder/initial_setup/starter_projects/.*\.json$
        args: [--security-check]
```

### Enforcement

Pre-commit hooks are installed via:
```bash
make init  # Runs: uvx pre-commit install
```

## Code Quality Tools

### Python - Ruff

**Configuration in `pyproject.toml`:**

```toml
[tool.ruff]
exclude = ["src/backend/base/langbuilder/alembic/*", "src/frontend/tests/assets/*"]
line-length = 120

[tool.ruff.lint]
pydocstyle.convention = "google"
select = ["ALL"]
ignore = [
    "C90",      # McCabe complexity
    "CPY",      # Missing copyright
    "COM812",   # Messes with formatter
    "ERA",      # Commented-out code
    "FIX002",   # Line contains TODO
    "ISC001",   # Messes with formatter
    "PERF203",  # Rarely useful
    "PLR09",    # Too many something
    "TD002",    # Missing author in TODO
    "TD003",    # Missing issue link in TODO
    "D10",      # Missing docstrings
    "ANN",      # Type annotations (TODO)
]

[tool.ruff.lint.per-file-ignores]
"src/backend/tests/*" = [
    "D1",       # Missing docstrings in tests
    "PLR2004",  # Magic values
    "S101",     # Use of assert
    "SLF001",   # Private member access
    "BLE001",   # Broad exception catching
]
```

### Python - MyPy

**Configuration in `pyproject.toml`:**

```toml
[tool.mypy]
plugins = ["pydantic.mypy"]
follow_imports = "skip"
disable_error_code = ["type-var"]
namespace_packages = true
mypy_path = "langbuilder"
ignore_missing_imports = true
```

### TypeScript/JavaScript - Biome

**Configuration in `src/frontend/biome.json`:**

```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2
  }
}
```

## CI Quality Requirements

### Pull Request Requirements

#### 1. Label Requirements

PRs must have the `lgtm` label and not be in draft state:
```yaml
should-run-ci: ${{ contains(labels, 'lgtm') && !draft }}
```

#### 2. Path-Based Testing

Tests run based on changed files:

| Path Change | Tests Run |
|-------------|-----------|
| Python files | Backend tests, linting |
| Frontend files | Frontend tests, Jest, Playwright |
| Docs files | Documentation build test |

#### 3. Test Requirements

All of the following must pass:
- [ ] Backend unit tests (all 5 shards)
- [ ] Backend integration tests (no API keys)
- [ ] Python linting (Ruff)
- [ ] Frontend Jest tests
- [ ] Frontend Playwright tests
- [ ] Template validation

### Merge Queue Requirements

```yaml
on:
  merge_group:
```

All CI checks must pass before merge.

### Fast-Track Option

For urgent changes, the `fast-track` label skips tests:
```yaml
should-run-tests: ${{ !contains(labels, 'fast-track') }}
```

**Warning:** Use sparingly and only for non-code changes.

## Coverage Thresholds

### Current Configuration

Coverage is reported but not enforced. Recommended thresholds:

| Metric | Backend | Frontend |
|--------|---------|----------|
| Line Coverage | 60% min | 50% min |
| Branch Coverage | 50% min | 40% min |
| Function Coverage | 70% min | 60% min |

### Future Enforcement

```yaml
# Add to CI workflow
- name: Check coverage
  run: |
    coverage report --fail-under=60
```

## Release Quality Gates

### Pre-Release Checklist

- [ ] All CI checks pass
- [ ] Cross-platform tests pass (Python 3.10-3.13)
- [ ] E2E tests pass on release branch
- [ ] Performance regression tests pass
- [ ] Security scan passes
- [ ] Documentation builds successfully

### Release Verification

The CI checks nightly build status:
```yaml
- name: Check PyPI package update
  # Verifies langbuilder-nightly was updated today
```

## Code Review Requirements

### Review Criteria

1. **Functionality**: Code does what it's supposed to do
2. **Tests**: Adequate test coverage for changes
3. **Style**: Follows project conventions
4. **Performance**: No obvious performance issues
5. **Security**: No security vulnerabilities introduced

### Approval Requirements

- At least 1 approval required
- CI must pass
- No unresolved review comments

## Quality Metrics Dashboard

### Key Metrics to Track

| Metric | Target | Monitoring |
|--------|--------|------------|
| CI Pass Rate | > 95% | GitHub Actions |
| Test Flakiness | < 5% | pytest-flakefinder |
| Coverage Trend | Increasing | Codecov |
| Build Time | < 15 min | GitHub Actions |
| Security Issues | 0 critical | CodeQL |

### Alerting

- CI failures notify PR author
- Security issues notify maintainers
- Coverage drops flagged in PR

## Workflow Commands

### Run All Quality Checks Locally

```bash
# Python
make format_backend  # Format code
make lint           # Run MyPy
uv run ruff check . # Lint check

# Frontend
cd src/frontend
npx @biomejs/biome check  # Lint check
npm test -- --coverage    # Tests with coverage

# All pre-commit hooks
uvx pre-commit run --all-files
```

### Fix Common Issues

```bash
# Auto-fix Python issues
uv run ruff check . --fix
uv run ruff format .

# Auto-fix Frontend issues
cd src/frontend
npx @biomejs/biome check --write

# Fix codespell
make fix_codespell
```

## Security Quality Gates

### CodeQL Analysis

Workflow: `.github/workflows/codeql.yml`

Scans for:
- Security vulnerabilities
- Code quality issues
- Bug patterns

### Dependency Scanning

- Dependabot alerts enabled
- Regular dependency updates
- Security advisory monitoring

---
*Generated by CG AIx SDLC - Testing Documentation*
