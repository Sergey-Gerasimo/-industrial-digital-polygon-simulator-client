# Integration Tests

This directory contains integration tests for the simulation client library.

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Poetry (for dependency management)

## Setup

1. Install test dependencies:
```bash
# Using Poetry (recommended)
poetry install --with dev

# Or using pip
pip install -r requirements-dev.txt
```

2. Make sure Docker daemon is running

## Running Tests

### All Integration Tests
```bash
python scripts/run_integration_tests.py
```

### Quick Smoke Tests
```bash
python scripts/smoke_test.py
```

### Specific Test Categories
```bash
# Service availability tests
pytest tests/integration/test_service_availability.py -v

# Simulation service tests
pytest tests/integration/test_simulation_service.py -v

# Database service tests
pytest tests/integration/test_database_service.py -v

# Complex scenarios
pytest tests/integration/test_simulation_scenarios.py -v
```

### With Coverage
```bash
pytest tests/integration/ --cov=simulation_client --cov-report=html
```

## Test Structure

### conftest.py
- Docker Compose service management
- Health checks for services
- Test fixtures (unified_client, etc.)

### test_service_availability.py
- Basic service connectivity tests
- Ping endpoint validation
- gRPC channel health checks

### test_simulation_service.py
- SimulationService API endpoint tests
- Data validation for simulation operations
- Reference data endpoint tests

### test_database_service.py
- SimulationDatabaseManager API endpoint tests
- CRUD operation validation
- Data consistency checks

### test_simulation_scenarios.py
- Complex multi-step simulation workflows
- Concurrent operation testing
- Error handling validation

## Docker Services

The tests automatically start and stop the following services using Docker Compose:

- **simulation_service**: gRPC service on port 50051
- **db**: PostgreSQL database on port 5432

## Test Data

Tests use the existing data in the database. No test data is created or modified during testing.

## Troubleshooting

### Services Don't Start
- Check Docker daemon is running
- Check ports 50051, 50052, 5432 are available
- Check Docker Compose logs: `docker-compose logs`

### Tests Fail with Connection Errors
- Wait for services to fully start (health checks may take time)
- Check service logs for errors
- Verify gRPC endpoints are responding

### Database Connection Issues
- Ensure PostgreSQL container is healthy
- Check database credentials in docker-compose.yaml

## CI/CD Integration

For CI/CD pipelines, use:
```bash
# Quick smoke tests
pytest tests/integration/test_service_availability.py::TestServiceAvailability::test_both_services_ping

# Full integration suite
pytest tests/integration/ --durations=10
```

## Performance Considerations

- Tests include automatic retries for flaky operations
- Docker health checks prevent premature test execution
- Concurrent testing capabilities for performance validation
