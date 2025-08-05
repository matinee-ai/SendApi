"""
Unit tests for the request_runner module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from src.request_runner import RequestRunner
from src.models import Request, Environment


class TestRequestRunner(unittest.TestCase):
    """Test cases for the RequestRunner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.request = Request(
            name="Test Request",
            method="GET",
            url="https://httpbin.org/get",
            headers={"User-Agent": "SendApi/1.0"},
            params={"param1": "value1"}
        )
        self.environment = Environment("Test Environment")
        self.environment.add_variable("API_URL", "https://httpbin.org")
        self.environment.add_variable("API_KEY", "test-key-123")
    
    def test_request_runner_creation(self):
        """Test RequestRunner object creation."""
        runner = RequestRunner(self.request, self.environment)
        self.assertEqual(runner.request, self.request)
        self.assertEqual(runner.environment, self.environment)
        self.assertIsNone(runner.response_data)
        self.assertIsNone(runner.test_results)
    
    def test_substitute_variables(self):
        """Test variable substitution in request data."""
        request = Request(
            name="Test Request",
            method="GET",
            url="{{API_URL}}/get",
            headers={"Authorization": "Bearer {{API_KEY}}"},
            params={"param1": "value1"}
        )
        
        runner = RequestRunner(request, self.environment)
        substituted_data = runner._substitute_variables({
            "url": "{{API_URL}}/get",
            "headers": {"Authorization": "Bearer {{API_KEY}}"},
            "params": {"param1": "value1"}
        })
        
        self.assertEqual(substituted_data["url"], "https://httpbin.org/get")
        self.assertEqual(substituted_data["headers"]["Authorization"], "Bearer test-key-123")
        self.assertEqual(substituted_data["params"]["param1"], "value1")
    
    def test_substitute_variables_no_environment(self):
        """Test variable substitution without environment."""
        request = Request(
            name="Test Request",
            method="GET",
            url="{{API_URL}}/get"
        )
        
        runner = RequestRunner(request, None)
        substituted_data = runner._substitute_variables({
            "url": "{{API_URL}}/get"
        })
        
        # Variables should remain unchanged when no environment is provided
        self.assertEqual(substituted_data["url"], "{{API_URL}}/get")
    
    def test_prepare_request_data(self):
        """Test request data preparation."""
        runner = RequestRunner(self.request, self.environment)
        request_data = runner._prepare_request_data()
        
        self.assertEqual(request_data["method"], "GET")
        self.assertEqual(request_data["url"], "https://httpbin.org/get")
        self.assertEqual(request_data["headers"]["User-Agent"], "SendApi/1.0")
        self.assertEqual(request_data["params"]["param1"], "value1")
    
    def test_prepare_request_data_with_body(self):
        """Test request data preparation with body."""
        request = Request(
            name="Test Request",
            method="POST",
            url="https://httpbin.org/post",
            body='{"key": "value"}',
            body_type="raw",
            headers={"Content-Type": "application/json"}
        )
        
        runner = RequestRunner(request, self.environment)
        request_data = runner._prepare_request_data()
        
        self.assertEqual(request_data["method"], "POST")
        self.assertEqual(request_data["url"], "https://httpbin.org/post")
        self.assertEqual(request_data["body"], '{"key": "value"}')
        self.assertEqual(request_data["headers"]["Content-Type"], "application/json")
    
    def test_prepare_request_data_form_data(self):
        """Test request data preparation with form data."""
        request = Request(
            name="Test Request",
            method="POST",
            url="https://httpbin.org/post",
            body="key1=value1&key2=value2",
            body_type="x-www-form-urlencoded"
        )
        
        runner = RequestRunner(request, self.environment)
        request_data = runner._prepare_request_data()
        
        self.assertEqual(request_data["method"], "POST")
        self.assertEqual(request_data["data"], {"key1": "value1", "key2": "value2"})
    
    @patch('src.request_runner.requests.request')
    def test_execute_request_success(self, mock_request):
        """Test successful request execution."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json", "Server": "nginx"}
        mock_response.text = '{"message": "success"}'
        mock_response.elapsed.total_seconds.return_value = 0.15
        mock_request.return_value = mock_response
        
        runner = RequestRunner(self.request, self.environment)
        response_data = runner._execute_request({
            "method": "GET",
            "url": "https://httpbin.org/get",
            "headers": {"User-Agent": "SendApi/1.0"},
            "params": {"param1": "value1"}
        })
        
        self.assertEqual(response_data["status_code"], 200)
        self.assertEqual(response_data["headers"]["Content-Type"], "application/json")
        self.assertEqual(response_data["body"], '{"message": "success"}')
        self.assertEqual(response_data["response_time"], 150.0)
        
        # Verify request was called with correct parameters
        mock_request.assert_called_once_with(
            "GET",
            "https://httpbin.org/get",
            headers={"User-Agent": "SendApi/1.0"},
            params={"param1": "value1"},
            timeout=30
        )
    
    @patch('src.request_runner.requests.request')
    def test_execute_request_error(self, mock_request):
        """Test request execution with error."""
        # Mock request exception
        mock_request.side_effect = Exception("Connection error")
        
        runner = RequestRunner(self.request, self.environment)
        response_data = runner._execute_request({
            "method": "GET",
            "url": "https://httpbin.org/get"
        })
        
        self.assertEqual(response_data["status_code"], 0)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Connection error")
    
    def test_run_tests_no_tests(self):
        """Test running tests when no tests are provided."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        
        runner = RequestRunner(self.request, self.environment)
        test_results = runner._run_tests(response_data, "")
        
        self.assertFalse(test_results["passed"])
        self.assertEqual(test_results["summary"], "No tests to run")
        self.assertEqual(test_results["results"], ["No tests provided"])
    
    def test_run_tests_basic_tests(self):
        """Test running basic tests."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        
        tests_script = '''
        pm.test("Status code is 200", function () {
            pm.response.to.have.status(200);
        });
        
        pm.test("Response time is less than 1000ms", function () {
            pm.expect(pm.response.responseTime).to.be.below(1000);
        });
        
        pm.test("Content-Type is present", function () {
            pm.response.to.have.header("Content-Type");
        });
        '''
        
        runner = RequestRunner(self.request, self.environment)
        test_results = runner._run_tests(response_data, tests_script)
        
        self.assertTrue(test_results["passed"])
        self.assertEqual(test_results["passed_count"], 3)
        self.assertEqual(test_results["total_count"], 3)
        self.assertIn("3/3 tests passed", test_results["summary"])
    
    def test_run_tests_failing_tests(self):
        """Test running tests that fail."""
        response_data = {
            "status_code": 404,
            "headers": {"Server": "nginx"},
            "body": "Not Found",
            "response_time": 1500.0
        }
        
        tests_script = '''
        pm.test("Status code is 200", function () {
            pm.response.to.have.status(200);
        });
        
        pm.test("Response time is less than 1000ms", function () {
            pm.expect(pm.response.responseTime).to.be.below(1000);
        });
        
        pm.test("Content-Type is present", function () {
            pm.response.to.have.header("Content-Type");
        });
        '''
        
        runner = RequestRunner(self.request, self.environment)
        test_results = runner._run_tests(response_data, tests_script)
        
        self.assertFalse(test_results["passed"])
        self.assertEqual(test_results["passed_count"], 0)
        self.assertEqual(test_results["total_count"], 3)
        self.assertIn("0/3 tests passed", test_results["summary"])
    
    def test_run_tests_mixed_results(self):
        """Test running tests with mixed pass/fail results."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 1500.0
        }
        
        tests_script = '''
        pm.test("Status code is 200", function () {
            pm.response.to.have.status(200);
        });
        
        pm.test("Response time is less than 1000ms", function () {
            pm.expect(pm.response.responseTime).to.be.below(1000);
        });
        
        pm.test("Content-Type is present", function () {
            pm.response.to.have.header("Content-Type");
        });
        '''
        
        runner = RequestRunner(self.request, self.environment)
        test_results = runner._run_tests(response_data, tests_script)
        
        self.assertFalse(test_results["passed"])
        self.assertEqual(test_results["passed_count"], 2)
        self.assertEqual(test_results["total_count"], 3)
        self.assertIn("2/3 tests passed", test_results["summary"])
    
    @patch('src.request_runner.RequestRunner._prepare_request_data')
    @patch('src.request_runner.RequestRunner._execute_request')
    @patch('src.request_runner.RequestRunner._run_tests')
    def test_run_complete_flow(self, mock_run_tests, mock_execute_request, mock_prepare_data):
        """Test complete request execution flow."""
        # Mock return values
        mock_prepare_data.return_value = {
            "method": "GET",
            "url": "https://httpbin.org/get"
        }
        
        mock_execute_request.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        
        mock_run_tests.return_value = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed",
            "results": ["Test 1 passed", "Test 2 passed"]
        }
        
        runner = RequestRunner(self.request, self.environment)
        runner.run()
        
        # Verify all methods were called
        mock_prepare_data.assert_called_once()
        mock_execute_request.assert_called_once()
        mock_run_tests.assert_called_once()
        
        # Verify response data and test results were stored
        self.assertEqual(runner.response_data["status_code"], 200)
        self.assertEqual(runner.test_results["passed"], True)
        self.assertEqual(runner.test_results["passed_count"], 2)


if __name__ == "__main__":
    unittest.main() 