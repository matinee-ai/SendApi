"""
Unit tests for the request_runner module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from src.request_runner import RequestRunner
from src.models import Request, Environment
import requests


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
        self.environment.set_variable("API_URL", "https://httpbin.org")
        self.environment.set_variable("API_KEY", "test-key-123")
    
    def test_request_runner_creation(self):
        """Test RequestRunner object creation."""
        runner = RequestRunner(self.request, self.environment)
        self.assertEqual(runner.request_data, self.request)
        self.assertEqual(runner.environment, self.environment)
        self.assertIsNone(runner.response_data)
        self.assertIsNone(runner.test_results)
    
    def test_substitute_variables(self):
        """Test variable substitution in text."""
        request_text = "{{API_URL}}/get"
        headers_dict = {"Authorization": "Bearer {{API_KEY}}"}
        
        runner = RequestRunner(self.request, self.environment)
        
        substituted_url = runner.replace_environment_variables(request_text)
        substituted_headers = runner.replace_environment_variables_in_dict(headers_dict)
        
        self.assertEqual(substituted_url, "https://httpbin.org/get")
        self.assertEqual(substituted_headers["Authorization"], "Bearer test-key-123")
    
    def test_substitute_variables_no_environment(self):
        """Test variable substitution without environment."""
        request_text = "{{API_URL}}/get"
        
        runner = RequestRunner(self.request, None)
        substituted_url = runner.replace_environment_variables(request_text)
        
        # Variables should remain unchanged when no environment is provided
        self.assertEqual(substituted_url, "{{API_URL}}/get")
    
    @patch('src.request_runner.requests.request')
    def test_execute_request_success(self, mock_request):
        """Test successful request execution through run method."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json", "Server": "nginx"}
        mock_response.text = '{"message": "success"}'
        mock_response.elapsed.total_seconds.return_value = 0.15
        mock_response.content = b'{"message": "success"}' # Mock content for size
        mock_response.url = "https://httpbin.org/get"
        mock_request.return_value = mock_response
        
        request_data_for_run = self.request.to_dict()
        runner = RequestRunner(request_data_for_run, self.environment)
        runner.run()
        
        response_data = runner.get_response()
        
        self.assertEqual(response_data["status_code"], 200)
        self.assertEqual(response_data["headers"]["Content-Type"], "application/json")
        self.assertEqual(response_data["body"], '{"message": "success"}')
        # Response time is calculated by actual time.time(), not mocked
        self.assertGreater(response_data["response_time"], 0)
        
        # Verify request was called with correct parameters
        mock_request.assert_called_once_with(
            method="GET",
            url="https://httpbin.org/get",
            headers={'User-Agent': 'SendApi/1.0'}, # Ensure headers are correctly passed
            params={'param1': 'value1'}, # Ensure params are correctly passed
            timeout=30
        )
    
    @patch('src.request_runner.requests.request')
    def test_execute_request_error(self, mock_request):
        """Test request execution with error through run method."""
        # Mock request exception
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
    
        request_data_for_run = self.request.to_dict()
        runner = RequestRunner(request_data_for_run, self.environment)
        runner.run()
    
        response_data = runner.get_response()
    
        self.assertEqual(response_data["status_code"], 0)
        self.assertIn("error", response_data)
        self.assertIn("Connection error", response_data["error"])
    
    def test_run_tests_no_tests(self):
        """Test running tests when no tests are provided."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0,
            "url": "", "method": ""
        }
    
        request_with_no_tests = self.request.to_dict()
        request_with_no_tests["tests"] = ""
        runner = RequestRunner(request_with_no_tests, self.environment)
        test_results = runner.run_tests(response_data)
    
        self.assertTrue(test_results["passed"])
        self.assertEqual(test_results["summary"], "No tests to run")
        self.assertEqual(test_results["results"], ["No tests provided"])
    
    def test_run_tests_basic_tests(self):
        """Test running basic tests."""
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0,
            "url": "", "method": ""
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
    
        request_with_tests = self.request.to_dict()
        request_with_tests["tests"] = tests_script
        runner = RequestRunner(request_with_tests, self.environment)
        test_results = runner.run_tests(response_data)
    
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
            "response_time": 1500.0,
            "url": "", "method": ""
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
    
        request_with_failing_tests = self.request.to_dict()
        request_with_failing_tests["tests"] = tests_script
        runner = RequestRunner(request_with_failing_tests, self.environment)
        test_results = runner.run_tests(response_data)
    
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
            "response_time": 1500.0,
            "url": "", "method": ""
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
    
        request_with_mixed_tests = self.request.to_dict()
        request_with_mixed_tests["tests"] = tests_script
        runner = RequestRunner(request_with_mixed_tests, self.environment)
        test_results = runner.run_tests(response_data)
    
        self.assertFalse(test_results["passed"])
        self.assertEqual(test_results["passed_count"], 2)
        self.assertEqual(test_results["total_count"], 3)
        self.assertIn("2/3 tests passed", test_results["summary"])
    
    def test_run_complete_flow(self):
        """Test complete request execution flow."""
        request_data_for_run = self.request.to_dict()
        request_data_for_run["tests"] = """
            pm.test("Status code is 200", function () { pm.response.to.have.status(200); });
            """
        runner = RequestRunner(request_data_for_run, self.environment)
        runner.run()
        
        # Verify response data and test results were stored
        self.assertIsNotNone(runner.get_response())
        self.assertEqual(runner.get_response()["status_code"], 200)
        self.assertIsNotNone(runner.get_test_results())
        self.assertTrue(runner.get_test_results()["passed"])
        self.assertEqual(runner.get_test_results()["passed_count"], 1)

if __name__ == "__main__":
    unittest.main() 