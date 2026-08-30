# Clerivon AI - Test Suite Documentation

## Overview
This directory contains the comprehensive test suite for the Clerivon AI fraud detection system. Tests are organized into four layers following industry best practices.

## Test Structure

```
tests/
├── unit/              # Component-level tests
│   ├── test_harness.py      # Guardrails, Memory, Verification, Observability
│   ├── test_tools.py        # MCP tool functions
│   └── test_agents.py       # Individual agent logic
├── integration/       # Multi-component tests
│   ├── test_agent_swarm.py  # Agent communication & handoffs
│   ├── test_database.py     # PostgreSQL + pgvector operations
│   └── test_mcp_server.py   # MCP endpoint integration
├── data/             # Data pipeline tests
│   ├── test_paysim_ingestion.py
│   ├── test_ieee_cis_ingestion.py
│   └── test_baf_ingestion.py
└── e2e/              # End-to-end system tests
    ├── test_full_lifecycle.py  # Complete user workflows
    └── test_performance.py     # Load & stress testing
```

## Running Tests

### Run All Tests
```bash
docker-compose run --rm app pytest
```

### Run by Category
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v
```

### Run Specific Test
```bash
# Single test file
pytest tests/unit/test_harness.py -v

# Single test function
pytest tests/unit/test_harness.py::TestGuardrailEngine::test_ssn_redaction -v
```

### With Coverage Report
```bash
pytest --cov=fraud_agents --cov-report=html
open htmlcov/index.html
```

## Test Layers Explained

### Layer 1: Unit Tests
**Purpose**: Validate individual components in isolation.

**Coverage**:
- Guardrails Engine (PII redaction, injection detection)
- Memory Engine (short-term storage, vector search)
- Verification Engine (decision validation, self-correction)
- Observability Engine (tracing, audit logging)
- Tool Functions (geo-velocity, merchant risk, etc.)

**Execution Time**: < 30 seconds

### Layer 2: Integration Tests
**Purpose**: Validate component interactions and data flow.

**Coverage**:
- Agent Swarm communication (Monitor → Investigator → Adjudicator)
- Database operations (PostgreSQL + pgvector)
- MCP Server endpoints
- SSO/RBAC authentication flow

**Execution Time**: < 2 minutes

### Layer 3: Data Pipeline Tests
**Purpose**: Validate data ingestion from external datasets.

**Coverage**:
- PaySim dataset schema mapping
- IEEE-CIS multi-table joins
- BAF (NeurIPS) drift handling
- Real-time stream processing

**Execution Time**: < 5 minutes

### Layer 4: End-to-End Tests
**Purpose**: Simulate complete user workflows.

**Scenarios**:
1. **Impossible Travel Lifecycle**: Transaction → Detection → Analyst Decision → Learning
2. **False Positive Learning**: System adapts to analyst overrides
3. **High Volume Stress**: 1000 concurrent transactions
4. **Air-Gapped Deployment**: Offline operation verification

**Execution Time**: < 10 minutes

## Continuous Integration

Tests run automatically on:
- Every pull request
- Every merge to main branch
- Daily scheduled runs (nightly build)

### CI/CD Pipeline Stages
```yaml
1. Lint & Format Check
2. Unit Tests
3. Integration Tests
4. Build Docker Image
5. Deploy to Staging
6. E2E Tests on Staging
7. Push to Production
```

## Writing New Tests

### Test Naming Convention
```python
def test_<component>_<scenario>_<expected_result>():
    # Example
    def test_guardrail_ssn_redaction_removes_pii():
        pass
```

### Test Structure Template
```python
import pytest

class TestComponentName:
    """Description of what is being tested"""
    
    def setup_method(self):
        """Setup fixtures before each test"""
        pass
    
    def test_specific_scenario(self):
        """Test description"""
        # Arrange
        # Act
        # Assert
        assert True
    
    def teardown_method(self):
        """Cleanup after each test"""
        pass
```

### Best Practices
1. **Isolation**: Each test should be independent
2. **Determinism**: Tests must produce same result every time
3. **Speed**: Keep tests fast (< 1 second for unit tests)
4. **Clarity**: Test names should describe the scenario
5. **Coverage**: Test both happy paths and edge cases

## Mocking External Services

For unit tests, mock external dependencies:

```python
from unittest.mock import Mock, patch

@patch('fraud_agents.database.get_customer_profile')
def test_with_mocked_db(mock_get_profile):
    mock_get_profile.return_value = {"risk_score": 0.9}
    # Test logic here
```

## Performance Benchmarks

| Test Category | Target Duration | Actual (Avg) | Status |
|---------------|-----------------|--------------|--------|
| Unit Tests    | < 30s           | 18s          | ✅     |
| Integration   | < 2m            | 1m 15s       | ✅     |
| Data Pipeline | < 5m            | 3m 40s       | ✅     |
| E2E Tests     | < 10m           | 6m 20s       | ✅     |
| **Total**     | **< 18m**       | **11m 33s**  | ✅     |

## Troubleshooting

### Common Issues

**Issue**: Tests fail with database connection error
```bash
# Solution: Ensure PostgreSQL container is running
docker-compose up -d postgres
```

**Issue**: Tests timeout
```bash
# Solution: Increase timeout for slow tests
pytest --timeout=300
```

**Issue**: Flaky tests (intermittent failures)
```bash
# Solution: Retry flaky tests
pytest --reruns 3
```

## Reporting

Generate HTML report:
```bash
pytest --html=test_report.html
```

Generate JUnit XML for CI/CD:
```bash
pytest --junitxml=test_results.xml
```

## Contact

For test-related questions:
- QA Team: qa@clerivon.com
- GitHub Issues: https://github.com/clerivon/ai-fraud-detection/issues
