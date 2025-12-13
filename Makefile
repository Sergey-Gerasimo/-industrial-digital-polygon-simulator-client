# Makefile for simulation client

.PHONY: install install-dev test test-integration test-smoke clean

# Install dependencies
install:
	poetry install

# Install with dev dependencies
install-dev:
	poetry install --with dev

# Run smoke tests (quick service availability check)
test-smoke:
	python scripts/smoke_test.py

# Run all integration tests
test-integration:
	python scripts/run_integration_tests.py

# Run all tests
test: test-smoke test-integration

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Generate proto files
proto:
	poetry run python scripts/generate_code.py

# Format code
format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

# Lint code
lint:
	poetry run flake8 src/ tests/
	poetry run mypy src/simulation_client/

# Build documentation
docs:
	poetry run sphinx-build docs docs/_build/html

# Run example
example:
	poetry run python examples/unified_client.py
