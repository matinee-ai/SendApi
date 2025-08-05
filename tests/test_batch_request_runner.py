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
        self.environment.add_variable("API_URL", "https://httpbin.org")
    
    def test_batch_request_runner_creation(self):
        """Test BatchRequestRunner object creation."""
        runner = BatchRequestRunner(self.requests, self.environment)
        self.assertEqual(runner.requests, self.requests)
        self.assertEqual(runner.environment, self.environment)
        self.assertEqual(len(runner.results), 0)
        self.assertFalse(runner.is_running)
    
    def test_batch_request_runner_inheritance(self):
        """Test that BatchRequestRunner inherits from QThread."""
        runner = BatchRequestRunner(self.requests, self.environment)
        self.assertIsInstance(runner, QThread)
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_run_single_request_success(self, mock_request_runner_class):
        """Test running a single request successfully."""
        # Mock RequestRunner
        mock_runner = MagicMock()
        mock_runner.get_response.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        mock_runner.get_test_results.return_value = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed"
        }
        mock_request_runner_class.return_value = mock_runner
        
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        result = batch_runner._run_single_request(self.requests[0])
        
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 200)
        self.assertEqual(result["test_results"]["passed"], True)
        self.assertEqual(result["test_results"]["passed_count"], 2)
        
        # Verify RequestRunner was called correctly
        mock_request_runner_class.assert_called_once_with(self.requests[0], self.environment)
        mock_runner.start.assert_called_once()
        mock_runner.wait.assert_called_once()
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_run_single_request_error(self, mock_request_runner_class):
        """Test running a single request with error."""
        # Mock RequestRunner to raise exception
        mock_request_runner_class.side_effect = Exception("Connection error")
        
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        result = batch_runner._run_single_request(self.requests[0])
        
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 0)
        self.assertIn("error", result["response"])
        self.assertEqual(result["response"]["error"], "Connection error")
        self.assertEqual(result["test_results"]["passed"], False)
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_run_single_request_no_response(self, mock_request_runner_class):
        """Test running a single request with no response."""
        # Mock RequestRunner returning None
        mock_runner = MagicMock()
        mock_runner.get_response.return_value = None
        mock_runner.get_test_results.return_value = None
        mock_request_runner_class.return_value = mock_runner
        
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        result = batch_runner._run_single_request(self.requests[0])
        
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 0)
        self.assertIn("error", result["response"])
        self.assertEqual(result["response"]["error"], "No response received")
        self.assertEqual(result["test_results"]["passed"], False)
    
    @patch.object(BatchRequestRunner, '_run_single_request')
    def test_run_all_requests(self, mock_run_single_request):
        """Test running all requests in batch."""
        # Mock single request results
        mock_run_single_request.side_effect = [
            {
                "request": self.requests[0],
                "response": {"status_code": 200, "response_time": 150.0},
                "test_results": {"passed": True, "passed_count": 2, "total_count": 2}
            },
            {
                "request": self.requests[1],
                "response": {"status_code": 201, "response_time": 200.0},
                "test_results": {"passed": True, "passed_count": 1, "total_count": 1}
            },
            {
                "request": self.requests[2],
                "response": {"status_code": 404, "response_time": 100.0},
                "test_results": {"passed": False, "passed_count": 0, "total_count": 2}
            }
        ]
        
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        batch_runner._run_all_requests()
        
        # Verify all requests were processed
        self.assertEqual(mock_run_single_request.call_count, 3)
        self.assertEqual(len(batch_runner.results), 3)
        
        # Verify results
        self.assertEqual(batch_runner.results[0]["response"]["status_code"], 200)
        self.assertEqual(batch_runner.results[1]["response"]["status_code"], 201)
        self.assertEqual(batch_runner.results[2]["response"]["status_code"], 404)
    
    @patch.object(BatchRequestRunner, '_run_all_requests')
    def test_run_method(self, mock_run_all_requests):
        """Test the main run method."""
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        batch_runner.run()
        
        # Verify run_all_requests was called
        mock_run_all_requests.assert_called_once()
        
        # Verify signals were emitted
        # Note: We can't easily test signal emission in unit tests without Qt event loop
    
    def test_batch_runner_with_empty_requests(self):
        """Test BatchRequestRunner with empty requests list."""
        batch_runner = BatchRequestRunner([], self.environment)
        self.assertEqual(len(batch_runner.requests), 0)
        self.assertEqual(len(batch_runner.results), 0)
    
    def test_batch_runner_with_no_environment(self):
        """Test BatchRequestRunner without environment."""
        batch_runner = BatchRequestRunner(self.requests, None)
        self.assertIsNone(batch_runner.environment)
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_batch_runner_signal_emission(self, mock_request_runner_class):
        """Test that signals are emitted during batch execution."""
        # Mock RequestRunner
        mock_runner = MagicMock()
        mock_runner.get_response.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        mock_runner.get_test_results.return_value = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed"
        }
        mock_request_runner_class.return_value = mock_runner
        
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        
        # Test that signals are connected (this is more of an integration test)
        # In a real scenario, you'd need to run this in a Qt event loop
        self.assertTrue(hasattr(batch_runner, 'request_completed'))
        self.assertTrue(hasattr(batch_runner, 'all_completed'))
    
    def test_batch_runner_results_structure(self):
        """Test the structure of batch results."""
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        
        # Add a mock result
        mock_result = {
            "request": self.requests[0],
            "response": {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "body": '{"message": "success"}',
                "response_time": 150.0
            },
            "test_results": {
                "passed": True,
                "passed_count": 2,
                "total_count": 2,
                "summary": "2/2 tests passed",
                "results": ["Test 1 passed", "Test 2 passed"]
            }
        }
        
        batch_runner.results.append(mock_result)
        
        # Verify result structure
        self.assertEqual(len(batch_runner.results), 1)
        result = batch_runner.results[0]
        
        self.assertIn("request", result)
        self.assertIn("response", result)
        self.assertIn("test_results", result)
        
        self.assertEqual(result["request"], self.requests[0])
        self.assertEqual(result["response"]["status_code"], 200)
        self.assertEqual(result["test_results"]["passed"], True)
    
    @patch('src.batch_request_runner.RequestRunner')
    def test_batch_runner_timeout_handling(self, mock_request_runner_class):
        """Test timeout handling in batch execution."""
        # Mock RequestRunner that takes too long
        mock_runner = MagicMock()
        mock_runner.start.side_effect = lambda: time.sleep(0.1)  # Simulate delay
        mock_runner.get_response.return_value = {
            "status_code": 200,
            "response_time": 150.0
        }
        mock_runner.get_test_results.return_value = {
            "passed": True,
            "passed_count": 1,
            "total_count": 1
        }
        mock_request_runner_class.return_value = mock_runner
        
        batch_runner = BatchRequestRunner(self.requests, self.environment)
        batch_runner.timeout = 0.05  # Set short timeout
        
        result = batch_runner._run_single_request(self.requests[0])
        
        # Should handle timeout gracefully
        self.assertIsNotNone(result)
        self.assertEqual(result["request"], self.requests[0])


if __name__ == "__main__":
    unittest.main() 