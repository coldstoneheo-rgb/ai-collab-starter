# Tests

This directory contains tests for AI-Collab-Starter.

## Structure

```
tests/
├── test_pr_collector.py    # PR Collector unit tests
└── README.md                # This file
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# From repository root
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=ai --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_pr_collector.py -v
```

### Run Specific Test

```bash
pytest tests/test_pr_collector.py::TestPRCollector::test_get_pr_info -v
```

## Integration Testing

### Test PR Collector with Real GitHub API

**⚠️ Requires GITHUB_TOKEN environment variable**

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Test with PR #6
python -m ai.utils.pr_collector 6
```

Expected output:
```
🔍 Fetching PR #6...

✅ PR #6: Phase 1 Infrastructure Setup and Workflow Fix
   Author: coldstoneheo-rgb
   State: closed
   Branch: claude/update-ai-collab-docs-Zf1Dg → main
   Changes: +4267 -44
   Files: 30
   Commits: 7
   Labels: None
   URL: https://github.com/coldstoneheo-rgb/ai-collab-starter/pull/6

📁 Changed Files (30):
   ✨ .ai/budget.json (+13 -0)
   ✨ .ai/config.yml (+57 -0)
   ... (showing first 10)

💬 Comments (0):
   (none)

🔒 Sensitive Changes: Yes ⚠️
```

## Writing New Tests

### Unit Tests

Use mocking to avoid actual API calls:

```python
from unittest.mock import Mock, patch

@patch('ai.utils.pr_collector.Github')
def test_something(self, mock_github):
    # Set up mocks
    mock_repo = MagicMock()
    mock_github.return_value.get_repo.return_value = mock_repo

    # Test your code
    collector = PRCollector(token='test', repo_name='owner/repo')
    # ... assertions
```

### Integration Tests

Mark integration tests with pytest marker:

```python
@pytest.mark.integration
def test_real_github_api():
    # This test requires GITHUB_TOKEN
    collector = PRCollector()
    pr_info = collector.get_pr_info(6)
    assert pr_info.number == 6
```

Run only integration tests:
```bash
pytest -v -m integration
```

Skip integration tests:
```bash
pytest -v -m "not integration"
```

## Test Coverage Goals

- Phase 1: 50%+ coverage (infrastructure only)
- Phase 2: 70%+ coverage (with real API clients)
- Phase 3: 85%+ coverage (production ready)

## Continuous Integration

Tests are automatically run on:
- Every PR (via GitHub Actions)
- Push to main branch
- Before release tags

See `.github/workflows/test.yml` for CI configuration.
