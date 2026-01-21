# Master Test Plan

## Overview

This document provides a comprehensive test plan template for LangBuilder releases, including regression testing, smoke tests, and release verification procedures.

## Release Testing Phases

### Phase 1: Pre-Release Verification

| Step | Description | Command | Owner |
|------|-------------|---------|-------|
| 1.1 | Run all unit tests | `make unit_tests` | Dev |
| 1.2 | Run integration tests | `make integration_tests` | Dev |
| 1.3 | Verify code formatting | `make format_backend` | Dev |
| 1.4 | Run linting | `make lint` | Dev |
| 1.5 | Check starter templates | `make template_tests` | Dev |

### Phase 2: CI Pipeline Validation

| Step | Description | Verification | Status |
|------|-------------|--------------|--------|
| 2.1 | Backend tests (all shards) | GitHub Actions | [ ] |
| 2.2 | Frontend Jest tests | GitHub Actions | [ ] |
| 2.3 | Playwright E2E tests | GitHub Actions | [ ] |
| 2.4 | Cross-platform tests | GitHub Actions | [ ] |
| 2.5 | Documentation build | GitHub Actions | [ ] |

### Phase 3: Release Candidate Testing

| Step | Description | Duration | Status |
|------|-------------|----------|--------|
| 3.1 | Full E2E test suite | 30-60 min | [ ] |
| 3.2 | Performance regression | 15-30 min | [ ] |
| 3.3 | Load testing | 30-60 min | [ ] |
| 3.4 | Manual smoke tests | 30 min | [ ] |

## Smoke Test Suite

### Backend Smoke Tests

```bash
# 1. Server startup
uv run langbuilder run --backend-only &
sleep 10
curl -f http://localhost:7860/api/v1/auto_login

# 2. Health check
curl -f http://localhost:7860/health

# 3. API authentication
curl -X POST http://localhost:7860/api/v1/login \
  -d "username=test&password=test"

# 4. Flow operations
curl -f http://localhost:7860/api/v1/flows/
```

### Frontend Smoke Tests

| Test | Description | Expected Result |
|------|-------------|-----------------|
| Homepage loads | Navigate to `/` | Application renders |
| Login works | Enter credentials | User authenticated |
| Flow canvas | Create new flow | Canvas displayed |
| Component drag | Drag component to canvas | Component added |
| Save flow | Click save | Flow persisted |
| Run flow | Execute basic flow | Output generated |

### Starter Project Smoke Tests

| Project | Test | Expected |
|---------|------|----------|
| Basic Prompting | Run with test input | Valid output |
| Memory Chatbot | Multi-turn conversation | Context preserved |
| Document QA | Upload and query | Relevant answer |
| Blog Writer | Generate content | Formatted output |

## Regression Test Suite

### Critical Path Tests

| ID | Feature | Test Case | Priority |
|----|---------|-----------|----------|
| REG-001 | Authentication | User login/logout | P0 |
| REG-002 | Flow Creation | Create new flow | P0 |
| REG-003 | Flow Execution | Run basic flow | P0 |
| REG-004 | Component Loading | All components load | P0 |
| REG-005 | API Endpoints | CRUD operations | P0 |

### Feature-Specific Regression

| ID | Feature | Test Cases | Status |
|----|---------|------------|--------|
| REG-010 | Folders | Create, rename, delete | [ ] |
| REG-011 | Variables | Global variable CRUD | [ ] |
| REG-012 | Groups | Node grouping | [ ] |
| REG-013 | Freeze | Freeze/unfreeze nodes | [ ] |
| REG-014 | Publish | Flow publishing | [ ] |
| REG-015 | MCP | MCP server integration | [ ] |

### API Regression Tests

```bash
# Run API-specific tests
pytest src/backend/tests/unit/api/ -v

# Run with specific markers
pytest -m "api" -v
```

### UI Regression Tests

```bash
# Run core feature tests
cd src/frontend
npx playwright test tests/core/features/ --grep "@release"

# Run integration tests
npx playwright test tests/core/integrations/
```

## Performance Test Plan

### Baseline Metrics

| Metric | Baseline | Threshold |
|--------|----------|-----------|
| Server startup | < 10s | < 15s |
| Flow save | < 2s | < 5s |
| Flow execution (simple) | < 5s | < 10s |
| API response (list) | < 500ms | < 1s |
| API response (create) | < 1s | < 2s |

### Load Testing

```bash
# Run Locust load tests
make locust \
  locust_users=50 \
  locust_spawn_rate=5 \
  locust_time=300s \
  locust_host=http://localhost:7860
```

#### Load Test Scenarios

| Scenario | Users | Duration | Success Criteria |
|----------|-------|----------|------------------|
| Baseline | 10 | 5 min | 0% errors |
| Normal Load | 50 | 10 min | < 1% errors |
| Peak Load | 100 | 5 min | < 5% errors |
| Stress Test | 200 | 5 min | Graceful degradation |

### Performance Regression Detection

```bash
# Run benchmark tests
pytest src/backend/tests/performance/ -v --benchmark-only

# Compare with baseline
pytest --benchmark-compare=baseline.json
```

## Cross-Platform Testing

### Python Version Matrix

| Version | Ubuntu | Windows | macOS |
|---------|--------|---------|-------|
| 3.10 | [ ] | [ ] | [ ] |
| 3.11 | [ ] | [ ] | [ ] |
| 3.12 | [ ] | [ ] | [ ] |
| 3.13 | [ ] | [ ] | [ ] |

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | Latest | [ ] |
| Firefox | Latest | [ ] |
| Safari | Latest | [ ] |
| Edge | Latest | [ ] |

## Release Checklist

### Pre-Release

- [ ] All CI checks pass on release branch
- [ ] Version numbers updated (`make patch v=X.Y.Z`)
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Security scan clean

### Release Testing

- [ ] Smoke tests pass
- [ ] Regression tests pass
- [ ] Performance within thresholds
- [ ] Cross-platform verification
- [ ] Starter projects functional

### Post-Release Verification

- [ ] PyPI package installable
- [ ] Docker image builds
- [ ] Documentation site updated
- [ ] Release notes published

## Test Execution Commands

### Full Regression Suite

```bash
# Backend
make tests

# Frontend
cd src/frontend
npm test
npx playwright test
```

### Quick Validation

```bash
# Backend unit tests only
make unit_tests async=true

# Frontend smoke tests
cd src/frontend
npx playwright test tests/core/features/ --grep "@smoke"
```

### Release Build Verification

```bash
# Build and test package
make build main=true
pip install dist/*.whl

# Verify installation
python -c "import langbuilder; print(langbuilder.__version__)"
langbuilder run --help
```

## Test Results Template

### Summary

| Category | Pass | Fail | Skip | Total |
|----------|------|------|------|-------|
| Unit Tests | | | | |
| Integration | | | | |
| E2E Tests | | | | |
| Performance | | | | |
| **Total** | | | | |

### Failures

| Test | Category | Failure Reason | Severity |
|------|----------|----------------|----------|
| | | | |

### Issues Found

| ID | Description | Severity | Status |
|----|-------------|----------|--------|
| | | | |

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | | | |
| Dev Lead | | | |
| Product Owner | | | |

---
*Generated by CG AIx SDLC - Testing Documentation*
