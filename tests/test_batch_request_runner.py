"""
Unit tests for the batch_request_runner module.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
from PySide6.QtCore import QThread
from src.batch_request_runner import BatchRequestRunner
from src.models import Request, Environment


class TestBatchRequestRunner(unittest.TestCase):
    """Test cases for the BatchRequestRunner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.requests = [
            Request("Request 1", "GET", "https://httpbin.org/get"),
            Request("Request 2", "POST", "https://httpbin.org/post"),
            Request("Request 3", "PUT", "https://httpbin.org/put")
        ]
        self.environment = Environment("Test Environment")
        self.environment.set_variable("API_URL", "https://httpbin.org")
    
    def _get_expected_request_data_dict(self, request_obj):
        """Helper to create the expected dictionary format passed to RequestRunner."""
        return {
            "method": request_obj.method,
            "url": request_obj.url,
            "headers": request_obj.headers,
            "params": request_obj.params,
            "body": request_obj.body,
            "body_type": request_obj.body_type,
            "pre_request_script": request_obj.pre_request_script,
            "tests": request_obj.tests
        }

    def test_batch_request_runner_creation(self):
        """Test BatchRequestRunner object creation."""
        runner = BatchRequestRunner(self.requests, self.environment)
        self.assertEqual(runner.requests, self.requests)
        self.assertEqual(runner.environment, self.environment)
        self.assertEqual(len(runner.results), 0)
        self.assertFalse(runner.isRunning()) # Corrected: use isRunning()
    
    def test_batch_request_runner_inheritance(self):
        """Test that BatchRequestRunner inherits from QThread."""
        runner = BatchRequestRunner(self.requests, self.environment)
        self.assertIsInstance(runner, QThread)
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_run_single_request_success(self, MockRequestRunner):
        """Test running a single request successfully (orchestrated via BatchRequestRunner.run())."""
        # Mock RequestRunner instance behavior
        mock_runner_instance = MockRequestRunner.return_value
        mock_runner_instance.get_response.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        mock_runner_instance.get_test_results.return_value = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed"
        }

        # Create BatchRequestRunner with a single request
        batch_runner = BatchRequestRunner([self.requests[0]], self.environment)
        batch_runner.run() # Execute the run method

        # Verify RequestRunner was called and its methods used
        expected_request_data = self._get_expected_request_data_dict(self.requests[0])
        MockRequestRunner.assert_called_once_with(expected_request_data, self.environment)
        mock_runner_instance.start.assert_called_once()
        mock_runner_instance.wait.assert_called_once()

        # Verify results stored in batch_runner
        self.assertEqual(len(batch_runner.results), 1)
        result = batch_runner.results[0]
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 200)
        self.assertEqual(result["test_results"]["passed"], True)

    @patch('src.batch_request_runner.RequestRunner')
    def test_run_single_request_error(self, MockRequestRunner):
        """Test running a single request with error (orchestrated via BatchRequestRunner.run())."""
        # Mock RequestRunner instance to raise an exception when start() is called
        mock_runner_instance = MockRequestRunner.return_value
        mock_runner_instance.start.side_effect = Exception("Connection error during request")

        # Create BatchRequestRunner with a single request
        batch_runner = BatchRequestRunner([self.requests[0]], self.environment)
        batch_runner.run() # Execute the run method

        # Verify RequestRunner was called and start was attempted
        expected_request_data = self._get_expected_request_data_dict(self.requests[0])
        MockRequestRunner.assert_called_once_with(expected_request_data, self.environment)
        mock_runner_instance.start.assert_called_once()
        # No wait() is called if start() immediately raises an exception

        # Verify error is captured in results
        self.assertEqual(len(batch_runner.results), 1)
        result = batch_runner.results[0]
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 0)
        self.assertIn("error", result["response"])
        self.assertIn("Connection error", result["response"]["error"])
        self.assertEqual(result["test_results"]["passed"], False)

    @patch('src.batch_request_runner.RequestRunner')
    def test_run_single_request_no_response(self, MockRequestRunner):
        """Test running a single request with no response (orchestrated via BatchRequestRunner.run())."""
        # Mock RequestRunner instance to return None for response and test results
        mock_runner_instance = MockRequestRunner.return_value
        mock_runner_instance.get_response.return_value = None
        mock_runner_instance.get_test_results.return_value = None

        # Create BatchRequestRunner with a single request
        batch_runner = BatchRequestRunner([self.requests[0]], self.environment)
        batch_runner.run() # Execute the run method

        # Verify RequestRunner was called and its methods used
        expected_request_data = self._get_expected_request_data_dict(self.requests[0])
        MockRequestRunner.assert_called_once_with(expected_request_data, self.environment)
        mock_runner_instance.start.assert_called_once()
        mock_runner_instance.wait.assert_called_once()

        # Verify results capture the no response scenario
        self.assertEqual(len(batch_runner.results), 1)
        result = batch_runner.results[0]
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 0)
        self.assertIn("error", result["response"])
        self.assertEqual(result["response"]["error"], "No response received")
        self.assertEqual(result["test_results"]["passed"], False)

    @patch('src.batch_request_runner.RequestRunner')
    def test_run_all_requests(self, MockRequestRunner):
        """Test running all requests in batch."""
        # Configure side_effect for RequestRunner to return different mock instances for each call
        mock_runner_1 = MagicMock()
        mock_runner_1.get_response.return_value = {"status_code": 200, "response_time": 150.0}
        mock_runner_1.get_test_results.return_value = {"passed": True, "passed_count": 2, "total_count": 2}

        mock_runner_2 = MagicMock()
        mock_runner_2.get_response.return_value = {"status_code": 201, "response_time": 200.0}
        mock_runner_2.get_test_results.return_value = {"passed": True, "passed_count": 1, "total_count": 1}

        mock_runner_3 = MagicMock()
        mock_runner_3.get_response.return_value = {"status_code": 404, "response_time": 100.0}
        mock_runner_3.get_test_results.return_value = {"passed": False, "passed_count": 0, "total_count": 2}

        MockRequestRunner.side_effect = [mock_runner_1, mock_runner_2, mock_runner_3]

        batch_runner = BatchRequestRunner(self.requests, self.environment)
        batch_runner.run()

        # Verify RequestRunner was called for each request with the dictionary representation of the request
        self.assertEqual(MockRequestRunner.call_count, 3)
        
        expected_call_1_data = self._get_expected_request_data_dict(self.requests[0])
        expected_call_2_data = self._get_expected_request_data_dict(self.requests[1])
        expected_call_3_data = self._get_expected_request_data_dict(self.requests[2])

        MockRequestRunner.assert_any_call(expected_call_1_data, self.environment)
        MockRequestRunner.assert_any_call(expected_call_2_data, self.environment)
        MockRequestRunner.assert_any_call(expected_call_3_data, self.environment)

        # Verify results
        self.assertEqual(len(batch_runner.results), 3)
        self.assertEqual(batch_runner.results[0]["response"]["status_code"], 200)
        self.assertEqual(batch_runner.results[1]["response"]["status_code"], 201)
        self.assertEqual(batch_runner.results[2]["response"]["status_code"], 404)

    @patch('src.batch_request_runner.RequestRunner')
    def test_run_method(self, MockRequestRunner):
        """Test the main run method orchestrates request execution."""
        mock_runner_instance = MockRequestRunner.return_value
        mock_runner_instance.get_response.return_value = {}
        mock_runner_instance.get_test_results.return_value = {}

        batch_runner = BatchRequestRunner(self.requests, self.environment)
        batch_runner.run()

        # Verify RequestRunner instances were created and run for each request
        self.assertEqual(MockRequestRunner.call_count, len(self.requests))
        for i, _call in enumerate(MockRequestRunner.call_args_list):
            expected_call_data = self._get_expected_request_data_dict(self.requests[i])
            # Ensure each call was with a request dict and environment
            self.assertEqual(_call.args[0], expected_call_data)
            self.assertEqual(_call.args[1], self.environment)
        mock_runner_instance.start.call_count = len(self.requests)
        mock_runner_instance.wait.call_count = len(self.requests)

    def test_batch_runner_with_empty_requests(self):
        """Test BatchRequestRunner with empty requests list."""
        batch_runner = BatchRequestRunner([], self.environment)
        self.assertEqual(len(batch_runner.requests), 0)
        self.assertEqual(len(batch_runner.results), 0)
    
    def test_batch_runner_with_no_environment(self):
        """Test BatchRequestRunner without environment."""
        # The BatchRequestRunner's __init__ expects 'requests' as a list of Request objects.
        # If the environment is None, it should still function.
        batch_runner = BatchRequestRunner(self.requests, None)
        self.assertIsNone(batch_runner.environment)

    @patch('src.batch_request_runner.RequestRunner')
    def test_batch_runner_signal_emission(self, MockRequestRunner):
        """Test that signals are emitted during batch execution."""
        # Mock RequestRunner
        mock_runner_instance = MockRequestRunner.return_value
        mock_runner_instance.get_response.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        mock_runner_instance.get_test_results.return_value = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed"
        }

        batch_runner = BatchRequestRunner([self.requests[0]], self.environment) # Use a single request for simpler signal testing
        
        # Connect mocks to signals to capture emissions
        mock_request_completed_slot = MagicMock()
        mock_all_completed_slot = MagicMock()

        batch_runner.request_completed.connect(mock_request_completed_slot)
        batch_runner.all_completed.connect(mock_all_completed_slot)

        batch_runner.run() # This will emit signals

        # Verify request_completed signal was emitted once for the single request
        mock_request_completed_slot.assert_called_once()
        # Check arguments: request object, response dict, test_results dict
        args, kwargs = mock_request_completed_slot.call_args
        self.assertEqual(args[0], self.requests[0])
        self.assertIn('status_code', args[1])
        self.assertIn('passed', args[2])

        # Verify all_completed signal was emitted once
        mock_all_completed_slot.assert_called_once()
        # Check arguments: list of results
        args, kwargs = mock_all_completed_slot.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(len(args[0]), 1) # One result for one request
    
    def test_batch_runner_results_structure(self):
        """Test the structure of batch results."""
        # We need to run the batch runner to populate results naturally, or mock RequestRunner behavior.
        # Let's use the mocking approach similar to test_run_all_requests for consistency and control.
        # This setup is largely similar to test_run_all_requests, but focuses on the structure of `results`.

        mock_runner_instance = MagicMock()
        mock_runner_instance.get_response.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        mock_runner_instance.get_test_results.return_value = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed",
            "results": ["Test 1 passed", "Test 2 passed"]
        }
        
        with patch('src.batch_request_runner.RequestRunner', return_value=mock_runner_instance) as MockRequestRunner:
            batch_runner = BatchRequestRunner([self.requests[0]], self.environment)
            batch_runner.run()

            self.assertEqual(len(batch_runner.results), 1)
            result = batch_runner.results[0]
            
            self.assertIn("request", result)
            self.assertIn("response", result)
            self.assertIn("test_results", result)
            
            self.assertEqual(result["request"], self.requests[0])
            self.assertEqual(result["response"]["status_code"], 200)
            self.assertEqual(result["test_results"]["passed"], True)
            self.assertEqual(result["test_results"]["passed_count"], 2)
            self.assertIn("Test 1 passed", result["test_results"]["results"][0])
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_batch_runner_timeout_handling(self, MockRequestRunner):
        """Test timeout handling in batch execution.
        Simulate timeout by having RequestRunner.wait() not set a response.
        """
        mock_runner_instance = MockRequestRunner.return_value
        # Simulate that wait finishes, but no response is set (e.g., due to internal timeout)
        mock_runner_instance.get_response.return_value = None
        mock_runner_instance.get_test_results.return_value = None

        batch_runner = BatchRequestRunner([self.requests[0]], self.environment)
        # Note: Actual timeout logic is within RequestRunner. We simulate RequestRunner's failure to produce
        # a response due to timeout from BatchRequestRunner's perspective.
        batch_runner.run() # This will call runner.start() and runner.wait()

        self.assertEqual(len(batch_runner.results), 1)
        result = batch_runner.results[0]

        # Should handle timeout gracefully by logging no response received
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 0)
        self.assertIn("error", result["response"])
        self.assertEqual(result["response"]["error"], "No response received")
        self.assertEqual(result["test_results"]["passed"], False)

if __name__ == "__main__":
    unittest.main() 