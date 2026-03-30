.PHONY: test test-unit test-integration test-e2e test-coverage clean

# Run all tests
test:
	python -m pytest tests/ -v

# Run only unit tests (fast)
test-unit:
	python -m pytest tests/test_*.py -v -m unit

# Run only integration tests
test-integration:
	python -m pytest tests/integration/ -v -m integration

# Run end-to-end tests
test-e2e:
	python -m pytest tests/integration/test_end_to_end.py -v -m e2e

# Run with coverage (if pytest-cov is installed)
test-coverage:
	python -m pytest tests/ --cov=src --cov=algomath --cov-report=html --cov-report=term 2>/dev/null || python -m pytest tests/ -v

# Clean test artifacts
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Run tests with verbose output
test-verbose:
	python -m pytest tests/ -vv --tb=long

# Quick smoke test (fast unit tests only)
smoke:
	python -m pytest tests/test_context.py tests/test_persistence.py -v -x
