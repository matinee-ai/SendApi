# Testing Guide for SendApi

This document provides comprehensive information about testing the SendApi application, including unit tests, integration tests, and how to run them.

## Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py
├── test_models.py              # Unit tests for data models
├── test_request_runner.py      # Unit tests for request execution
├── test_batch_request_runner.py # Unit tests for batch execution
├── test_postman_importer.py    # Unit tests for import functionality
├── test_ui_components.py       # Unit tests for UI components
└── test_integration.py         # Integration tests
```

## Test Categories

### 1. Unit Tests

Unit tests focus on testing individual components in isolation:

- **Models** (`test_models.py`): Tests for `Request`, `Collection`, `Environment`, and `Response` classes
- **Request Runner** (`test_request_runner.py`): Tests for HTTP request execution and test script evaluation
- **Batch Request Runner** (`test_batch_request_runner.py`): Tests for batch request execution
- **Postman Importer** (`test_postman_importer.py`): Tests for collection and environment import functionality
- **UI Components** (`test_ui_components.py`): Tests for individual UI components

### 2. Integration Tests

Integration tests (`test_integration.py`) test how components work together:

- Complete request execution flow
- Batch execution with multiple requests
- Import/export functionality
- UI interactions and signal connections
- Error handling scenarios

## Running Tests

### Prerequisites

Install testing dependencies:

```bash
pip install -r requirements.txt
```

### Using the Test Runner

The project includes a custom test runner (`run_tests.py`) that provides convenient options:

```bash
# Run all tests (unit + integration)
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run a specific test file
python run_tests.py --test test_models
```

### Using pytest

You can also use pytest directly for more advanced testing features:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests matching a pattern
pytest -k "test_request"

# Run tests with markers
pytest -m "unit"
pytest -m "integration"
```

### Using unittest

For basic test execution:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_models

# Run specific test class
python -m unittest tests.test_models.TestRequest
```

## Test Coverage

The test suite aims to achieve high coverage across all components:

- **Models**: 100% coverage for data structures
- **Request Runner**: 95%+ coverage for HTTP execution
- **Batch Runner**: 90%+ coverage for batch operations
- **UI Components**: 85%+ coverage for user interface
- **Integration**: End-to-end workflow testing

## Test Data

### Sample Collections

Tests use sample collections with various request types:

```python
sample_collection = {
    "info": {
        "name": "Test Collection",
        "description": "A test collection"
    },
    "item": [
        {
            "name": "Test Request",
            "request": {
                "method": "GET",
                "url": {"raw": "https://httpbin.org/get"}
            }
        }
    ]
}
```

### Sample Environments

Test environments include variables for testing substitution:

```python
sample_environment = {
    "name": "Test Environment",
    "variables": {
        "API_URL": "https://httpbin.org",
        "API_KEY": "test-key-123"
    }
}
```

### Test Requests

Various request types are tested:

- GET requests with parameters
- POST requests with JSON bodies
- PUT/PATCH requests
- Requests with custom headers
- Requests with authentication

## Mocking Strategy

### HTTP Requests

HTTP requests are mocked to avoid external dependencies:

```python
@patch('src.request_runner.requests.request')
def test_execute_request_success(self, mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.text = '{"message": "success"}'
    mock_request.return_value = mock_response
```

### Qt Components

Qt components are mocked for unit testing:

```python
@patch('src.sidebar.QMenu')
def test_context_menu(self, mock_menu):
    # Test context menu functionality
    pass
```

## Test Scenarios

### 1. Request Execution

Tests cover various request execution scenarios:

- **Successful requests**: 200 responses with valid data
- **Error responses**: 4xx and 5xx status codes
- **Network errors**: Connection timeouts and failures
- **Invalid URLs**: Malformed URLs and DNS failures
- **Authentication**: Requests with various auth methods

### 2. Test Script Evaluation

Tests verify test script execution:

- **Status code tests**: `pm.response.to.have.status(200)`
- **Response time tests**: `pm.expect(pm.response.responseTime).to.be.below(1000)`
- **Header tests**: `pm.response.to.have.header("Content-Type")`
- **JSON parsing tests**: Response body validation
- **Custom tests**: User-defined test scripts

### 3. Environment Variable Substitution

Tests ensure proper variable substitution:

- **URL substitution**: `{{API_URL}}/endpoint`
- **Header substitution**: `Bearer {{API_KEY}}`
- **Body substitution**: JSON with variables
- **Parameter substitution**: Query parameters with variables

### 4. Import/Export Functionality

Tests verify data persistence:

- **Collection export**: Save collections to JSON
- **Collection import**: Load collections from JSON
- **Environment export**: Save environments to JSON
- **Environment import**: Load environments from JSON
- **Postman compatibility**: Import Postman collections

### 5. UI Interactions

Tests cover user interface functionality:

- **Request selection**: Clicking on requests in sidebar
- **Environment switching**: Changing active environment
- **Response display**: Showing response data and test results
- **Context menus**: Right-click actions on collections/requests
- **Form validation**: Input validation and error messages

## Continuous Integration

### GitHub Actions

The project includes GitHub Actions workflow for automated testing:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
```

### Pre-commit Hooks

Consider adding pre-commit hooks for code quality:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## Performance Testing

### Request Performance

Tests measure request execution performance:

```python
def test_request_performance(self):
    start_time = time.time()
    runner = RequestRunner(request, environment)
    runner.run()
    execution_time = time.time() - start_time
    
    self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
```

### Batch Performance

Tests verify batch execution efficiency:

```python
def test_batch_performance(self):
    requests = [create_test_request() for _ in range(10)]
    batch_runner = BatchRequestRunner(requests, environment)
    
    start_time = time.time()
    batch_runner.run()
    batch_runner.wait()
    execution_time = time.time() - start_time
    
    self.assertLess(execution_time, 30.0)  # Should complete within 30 seconds
```

## Debugging Tests

### Verbose Output

Enable verbose test output for debugging:

```bash
python run_tests.py -v
pytest -v
```

### Test Isolation

Run individual tests for debugging:

```bash
python -m unittest tests.test_models.TestRequest.test_request_creation
pytest tests/test_models.py::TestRequest::test_request_creation
```

### Coverage Analysis

Generate detailed coverage reports:

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` to view coverage report.

## Best Practices

### 1. Test Organization

- Group related tests in test classes
- Use descriptive test method names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Data

- Use realistic test data
- Create reusable test fixtures
- Clean up test data after tests

### 3. Mocking

- Mock external dependencies
- Use appropriate mock levels
- Verify mock interactions

### 4. Assertions

- Use specific assertions
- Test both positive and negative cases
- Verify error conditions

### 5. Performance

- Keep tests fast
- Use appropriate timeouts
- Test performance-critical paths

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` is in Python path
2. **Qt Issues**: QApplication must be created for UI tests
3. **Network Timeouts**: Increase timeout values for slow connections
4. **Mock Issues**: Verify mock setup and teardown

### Debug Commands

```bash
# Run with debug output
python run_tests.py --debug

# Run specific failing test
python -m unittest tests.test_models.TestRequest.test_failing_method

# Check test discovery
python -m unittest discover tests -v
```

## Contributing

When adding new features, ensure:

1. **Unit tests** cover the new functionality
2. **Integration tests** verify component interactions
3. **Test coverage** remains high
4. **Documentation** is updated

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Inherit from `unittest.TestCase`
4. Add appropriate docstrings
5. Update this documentation if needed

### Test Review Checklist

- [ ] Tests cover all code paths
- [ ] Edge cases are tested
- [ ] Error conditions are handled
- [ ] Tests are fast and reliable
- [ ] Mocking is appropriate
- [ ] Documentation is clear 