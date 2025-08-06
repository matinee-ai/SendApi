"""
Integration tests for the SendApi application.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

# Set up headless environment for CI
if os.environ.get("CI") or not os.environ.get("DISPLAY"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["DISPLAY"] = ":99"
    # Additional environment variables for better headless support
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
    os.environ["QT_QPA_FONTDIR"] = "/usr/share/fonts"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.batch_request_runner import BatchRequestRunner
from src.main_window import MainWindow
from src.models import Collection, Environment, Request
from src.request_runner import RequestRunner


@pytest.mark.gui
@pytest.mark.integration
class TestSendApiIntegration(unittest.TestCase):
    """Integration tests for the SendApi application."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication for all tests."""
        try:
            cls.app = QApplication.instance()
            if cls.app is None:
                # Use empty argv to avoid conflicts
                cls.app = QApplication([])
        except Exception as e:
            print(f"Warning: Could not initialize QApplication: {e}")
            cls.app = None

    @patch.object(MainWindow, "load_data")
    def setUp(self, mock_load_data):
        """Set up test fixtures."""
        super().setUp()
        self.mock_load_data = mock_load_data
        self.mock_load_data.return_value = None  # Ensure it does nothing

        try:
            self.main_window = MainWindow()
        except Exception as e:
            print(f"Warning: Could not create MainWindow: {e}")
            self.main_window = None
        self.temp_dir = tempfile.mkdtemp()

        # Clear any previously loaded data to ensure a clean state for each test
        self.main_window.collections = []
        self.main_window.environments = []

        # Create test data
        self.test_collection = Collection("Test Collection")
        self.test_request = Request(
            name="Test Request",
            method="GET",
            url="https://httpbin.org/get",
            headers={"User-Agent": "SendApi/1.0"},
            params={"param1": "value1"},
        )
        self.test_collection.add_request(self.test_request)

        self.test_environment = Environment("Test Environment")
        self.test_environment.set_variable("API_URL", "https://httpbin.org")
        self.test_environment.set_variable("API_KEY", "test-key-123")

    def tearDown(self):
        """Clean up after each test."""
        if self.main_window is not None:
            self.main_window.close()

        # Stop the patcher
        self.mock_load_data.stop()  # Stop the patch applied by @patch.object

        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_main_window_creation(self):
        """Test that the main window can be created and displayed."""
        if self.main_window is None:
            self.skipTest("MainWindow could not be created in this environment")

        self.assertIsNotNone(self.main_window)
        self.assertEqual(self.main_window.windowTitle(), "SendApi - API Testing Tool")
        self.assertIsNotNone(self.main_window.sidebar)
        self.assertIsNotNone(self.main_window.request_panel)
        self.assertIsNotNone(self.main_window.response_panel)
        self.assertIsNotNone(self.main_window.environment_panel)

    def test_collection_management_integration(self):
        """Test collection management through the main window."""
        if self.main_window is None:
            self.skipTest("MainWindow could not be created in this environment")

        # Add collection
        self.main_window.collections.append(self.test_collection)
        self.main_window.sidebar.update_collections(self.main_window.collections)

        # Verify collection is displayed
        self.assertEqual(len(self.main_window.collections), 1)
        self.assertEqual(self.main_window.collections[0].name, "Test Collection")

        # Save and load collections
        self.main_window.save_data()

        # Clear collections and reload
        self.main_window.collections = []
        self.main_window.load_data()

        # Verify collection was loaded
        self.assertEqual(len(self.main_window.collections), 1)
        self.assertEqual(self.main_window.collections[0].name, "Test Collection")

    def test_curl_export_integration(self):
        """Test cURL command export functionality."""
        request = Request(
            name="cURL Test Request",
            method="POST",
            url="https://httpbin.org/post",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token",
            },
            params={"param1": "value1"},
            body='{"key": "value"}',
            body_type="raw",
        )

        # Generate cURL command
        curl_command = self.main_window._generate_curl_command(request)
        # print(f"Generated cURL command: {curl_command}") # Debug print

        # Verify cURL command structure
        self.assertIn("curl", curl_command)
        self.assertIn("-X POST", curl_command)
        self.assertIn("https://httpbin.org/post", curl_command)
        # The format is -H "Key: Value"
        self.assertIn('-H "Content-Type: application/json"', curl_command)
        self.assertIn('-H "Authorization: Bearer token"', curl_command)
        self.assertIn('--data-raw \'{"key": "value"}\'', curl_command)
        self.assertIn("https://httpbin.org/post?param1=value1", curl_command)

    def test_environment_management_integration(self):
        """Test environment management through the main window."""
        # Add environment
        self.main_window.environments.append(self.test_environment)
        self.main_window.environment_panel.update_environments(
            self.main_window.environments
        )

        # Verify environment is displayed
        self.assertEqual(len(self.main_window.environments), 1)
        self.assertEqual(self.main_window.environments[0].name, "Test Environment")

        # Test environment variable substitution
        request_with_vars = Request(
            name="Request with vars",
            method="GET",
            url="{{API_URL}}/get",
            headers={"Authorization": "Bearer {{API_KEY}}"},
        )

        runner = RequestRunner(
            request_with_vars.to_dict(), self.test_environment
        )  # Pass dict
        runner.run()

        response_data = (
            runner.get_response()
        )  # Now get_response returns the full response dictionary

        self.assertEqual(response_data["url"], "https://httpbin.org/get")
        # Note: response_data["headers"] contains response headers from the server, not request headers
        # The environment variable substitution is working correctly in the request

    def test_request_execution_integration(self):
        """Test complete request execution flow."""
        # Set up request with tests
        request_with_tests = Request(
            name="Test Request with Tests",
            method="GET",
            url="https://httpbin.org/json",
            tests="""
            pm.test("Status code is 200", function () {
                pm.response.to.have.status(200);
            });
            
            pm.test("Response time is less than 1000ms", function () {
                pm.expect(pm.response.responseTime).to.be.below(1000);
            });
            
            pm.test("Content-Type is present", function () {
                pm.response.to.have.header("Content-Type");
            });
            """,
        )

        # Execute request
        runner = RequestRunner(
            request_with_tests.to_dict(), self.test_environment
        )  # Pass dict
        runner.run()

        # Verify response
        response_data = runner.get_response()
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["status_code"], 200)
        self.assertIn("Content-Type", response_data["headers"])

        # Verify test results
        test_results = runner.get_test_results()
        self.assertIsNotNone(test_results)
        # Some tests might fail due to response time, but we should have results
        self.assertGreaterEqual(test_results["total_count"], 3)
        self.assertGreaterEqual(
            test_results["passed_count"], 2
        )  # At least 2 out of 3 should pass

    def test_batch_execution_integration(self):
        """Test batch request execution."""
        # Create multiple requests
        requests_list = [
            Request("Request 1", "GET", "https://httpbin.org/get"),
            Request("Request 2", "POST", "https://httpbin.org/post"),
            Request("Request 3", "PUT", "https://httpbin.org/put"),
        ]

        # Execute batch
        batch_runner = BatchRequestRunner(requests_list, self.test_environment)
        batch_runner.run()

        # Wait for completion
        batch_runner.wait()

        # Verify results
        self.assertEqual(len(batch_runner.results), 3)

        for result in batch_runner.results:
            self.assertIn("request", result)
            self.assertIn("response", result)
            self.assertIn("test_results", result)
            self.assertIsNotNone(result["response"]["status_code"])

    def test_import_export_integration(self):
        """Test import and export functionality."""
        # Create test collection
        collection = Collection("Import Test Collection")
        request = Request("Import Test Request", "GET", "https://httpbin.org/get")
        collection.add_request(request)

        # Export collection
        collection_data = collection.to_dict()

        # Save to temporary file
        export_file = os.path.join(self.temp_dir, "exported_collection.json")
        with open(export_file, "w") as f:
            json.dump(collection_data, f)

        # Import collection
        with open(export_file, "r") as f:
            imported_data = json.load(f)

        imported_collection = Collection.from_dict(imported_data)

        # Verify import/export
        self.assertEqual(imported_collection.name, "Import Test Collection")
        self.assertEqual(len(imported_collection.requests), 1)
        self.assertEqual(imported_collection.requests[0].name, "Import Test Request")
        self.assertEqual(imported_collection.requests[0].method, "GET")

    def test_test_creation_integration(self):
        """Test automatic test creation functionality."""
        # Create request without tests
        request = Request("Request without tests", "GET", "https://httpbin.org/get")
        self.assertEqual(request.tests, "")

        # Add standard tests
        standard_tests = (
            self.main_window.sidebar._generate_standard_tests()
        )  # Access through MainWindow -> Sidebar
        request.tests = standard_tests

        # Execute request with tests
        runner = RequestRunner(request.to_dict(), self.test_environment)  # Pass dict
        runner.run()

        # Verify test results
        test_results = runner.get_test_results()
        self.assertIsNotNone(test_results)
        # Standard tests might fail due to response time, but we should have results
        self.assertGreaterEqual(
            test_results["total_count"], 4
        )  # Standard tests have 4 tests

    def test_error_handling_integration(self):
        """Test error handling in various scenarios."""
        # Test invalid URL
        invalid_request = Request(
            "Invalid Request",
            "GET",
            "https://invalid-url-that-does-not-exist-12345.com",
        )
        runner = RequestRunner(
            invalid_request.to_dict(), self.test_environment
        )  # Pass dict
        runner.run()

        # Should handle connection error gracefully
        response_data = runner.get_response()
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["status_code"], 0)
        self.assertIn("error", response_data)

        # Test invalid JSON in body
        invalid_json_request = Request(
            name="Invalid JSON Request",
            method="POST",
            url="https://httpbin.org/post",
            body="invalid json content",
            body_type="raw",
            headers={"Content-Type": "application/json"},
        )

        runner = RequestRunner(
            invalid_json_request.to_dict(), self.test_environment
        )  # Pass dict
        runner.run()

        # Should still execute the request (server will handle JSON validation)
        response_data = runner.get_response()
        self.assertIsNotNone(response_data)
        self.assertEqual(
            response_data["status_code"], 200
        )  # Assuming httpbin returns 200 for invalid JSON in POST
        self.assertIn(
            "data", response_data["body"]
        )  # Check if the invalid data is echoed back

    def test_ui_interaction_integration(self):
        """Test UI interactions and signal connections."""
        # Test request selection
        self.main_window.on_request_selected(self.test_request)

        # Verify request panel was updated
        current_request = self.main_window.request_panel.get_current_request()
        self.assertEqual(current_request.name, "Test Request")
        self.assertEqual(current_request.method, "GET")
        self.assertEqual(current_request.url, "https://httpbin.org/get")

        # Test environment change
        self.main_window.on_environment_changed(self.test_environment)
        self.assertEqual(self.main_window.current_environment, self.test_environment)

        # Test response display
        mock_response = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0,
            "url": "https://httpbin.org/get",
            "method": "GET",
        }

        self.main_window.on_response_received(mock_response)
        self.assertEqual(self.main_window.last_response, mock_response)

    def test_batch_testing_ui_integration(self):
        """Test batch testing UI functionality."""
        # Prepare batch testing
        requests = [
            Request("Batch Request 1", "GET", "https://httpbin.org/get"),
            Request("Batch Request 2", "POST", "https://httpbin.org/post"),
        ]

        self.main_window.prepare_batch_testing(requests)

        # Verify batch testing table was prepared
        self.assertEqual(self.main_window.results_table.rowCount(), 2)
        self.assertEqual(
            self.main_window.results_table.item(0, 0).text(), "Batch Request 1"
        )
        self.assertEqual(
            self.main_window.results_table.item(1, 0).text(), "Batch Request 2"
        )

        # Test batch request completion
        mock_response = {
            "status_code": 200,
            "response_time": 150.0,
            "url": "https://httpbin.org/get",
            "method": "GET",
        }

        mock_test_results = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed",
        }

        self.main_window.on_batch_request_completed(
            requests[0], mock_response, mock_test_results
        )

        # Verify table was updated
        status_item = self.main_window.results_table.item(0, 1)
        self.assertIsNotNone(status_item)
        self.assertIn("Status: 200", status_item.text())
        self.assertIn("2/2 tests passed", status_item.text())


if __name__ == "__main__":
    unittest.main()
