"""
Unit tests for UI components.
"""

import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTableWidgetItem

from src.environment_panel import EnvironmentPanel
from src.models import Collection, Environment, Request
from src.request_panel import RequestPanel
from src.response_panel import ResponsePanel
from src.sidebar import Sidebar


class TestUIComponents(unittest.TestCase):
    """Test cases for UI components."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication for all tests."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures."""
        self.request = Request("Test Request", "GET", "https://httpbin.org/get")
        self.collection = Collection("Test Collection")
        self.collection.add_request(self.request)
        self.environment = Environment("Test Environment")
        self.environment.set_variable("API_URL", "https://httpbin.org")

    def test_request_panel_creation(self):
        """Test RequestPanel creation and basic functionality."""
        panel = RequestPanel(None)

        # Test basic UI elements exist
        self.assertIsNotNone(panel.method_combo)
        self.assertIsNotNone(panel.url_edit)
        self.assertIsNotNone(panel.send_btn)

    def test_request_panel_load_request(self):
        """Test loading a request into the panel."""
        panel = RequestPanel(None)
        panel.load_request(self.request)

        self.assertEqual(panel.method_combo.currentText(), "GET")
        self.assertEqual(panel.url_edit.text(), "https://httpbin.org/get")

    def test_request_panel_get_current_request(self):
        """Test getting current request from panel."""
        panel = RequestPanel(None)
        panel.load_request(self.request)

        current_request = panel.get_current_request()
        self.assertEqual(current_request.name, "Test Request")
        self.assertEqual(current_request.method, "GET")
        self.assertEqual(current_request.url, "https://httpbin.org/get")

    def test_response_panel_creation(self):
        """Test ResponsePanel creation."""
        panel = ResponsePanel(None)

        # Test basic UI elements exist
        self.assertIsNotNone(panel.status_code_label)
        self.assertIsNotNone(panel.body_edit)  # Changed from response_text
        self.assertIsNotNone(
            panel.headers_table
        )  # Changed from headers_text (now a table)
        self.assertIsNotNone(panel.tests_edit)  # Changed from test_results_text

    def test_response_panel_display_response(self):
        """Test displaying a response in the panel."""
        panel = ResponsePanel(None)

        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0,
            "url": "https://httpbin.org/get",
            "method": "GET",
            "test_results": {
                "passed": True,
                "passed_count": 2,
                "total_count": 2,
                "summary": "2/2 tests passed",
                "results": ["Test 1 passed", "Test 2 passed"],
            },
        }

        panel.display_response(response_data)  # Only pass response_data

        # Verify status is displayed
        self.assertIn("200", panel.status_code_label.text())
        self.assertIn(
            "150.0", panel.response_time_label.text()
        )  # Use response_time_label

        # Verify response body is displayed (formatted JSON)
        self.assertIn(
            '"message": "success"', panel.body_edit.toPlainText()
        )  # Changed from response_text

        # Verify headers are displayed (now in a table)
        self.assertEqual(panel.headers_table.rowCount(), 1)
        self.assertEqual(panel.headers_table.item(0, 0).text(), "Content-Type")
        self.assertEqual(panel.headers_table.item(0, 1).text(), "application/json")

    def test_sidebar_creation(self):
        """Test Sidebar creation."""
        sidebar = Sidebar(None)

        # Test basic UI elements exist
        self.assertIsNotNone(sidebar.collections_tree)

    def test_sidebar_update_collections(self):
        """Test updating collections in sidebar."""
        sidebar = Sidebar(None)
        collections = [self.collection]

        sidebar.update_collections(collections)

        # Verify collection is displayed
        root_item = sidebar.collections_tree.topLevelItem(0)
        self.assertIsNotNone(root_item)
        self.assertEqual(root_item.text(0), "Test Collection")

        # Verify request is displayed under collection
        request_item = root_item.child(0)
        self.assertIsNotNone(request_item)
        self.assertEqual(
            request_item.text(0), "GET Test Request"
        )  # Expects method prefix

    def test_sidebar_context_menu(self):
        """Test sidebar context menu functionality."""
        sidebar = Sidebar(None)
        collections = [self.collection]
        sidebar.update_collections(collections)

        # Get the collection item
        collection_item = sidebar.collections_tree.topLevelItem(0)

        # Test context menu for collection
        with patch("src.sidebar.QMenu") as mock_menu:
            from PySide6.QtCore import QPoint

            sidebar.show_collection_context_menu(QPoint(0, 0))  # Pass a proper QPoint
            mock_menu.assert_called()

    def test_environment_panel_creation(self):
        """Test EnvironmentPanel creation."""
        panel = EnvironmentPanel()

        # Test basic UI elements exist
        self.assertIsNotNone(panel.env_combo)
        self.assertIsNotNone(panel.variables_table)

    def test_environment_panel_update_environments(self):
        """Test updating environments in panel."""
        panel = EnvironmentPanel()
        environments = [self.environment]

        panel.update_environments(environments)

        # Verify environment is in combo box
        self.assertEqual(panel.env_combo.count(), 2)  # Includes "No Environment"
        self.assertEqual(
            panel.env_combo.itemText(1), "Test Environment"
        )  # "Test Environment" is at index 1

    def test_environment_panel_variable_management(self):
        """Test environment variable management."""
        panel = EnvironmentPanel()
        environments = [self.environment]
        panel.update_environments(environments)

        # Select the environment
        panel.env_combo.setCurrentIndex(1)  # Select "Test Environment"

        # Verify variables are displayed
        self.assertEqual(panel.variables_table.rowCount(), 1)
        self.assertEqual(panel.variables_table.item(0, 0).text(), "API_URL")
        self.assertEqual(panel.variables_table.item(0, 1).text(), "https://httpbin.org")

    def test_request_panel_headers_management(self):
        """Test headers management in request panel."""
        panel = RequestPanel(None)

        # Simulate adding a header directly to the table
        row_count = panel.headers_table.rowCount()
        panel.headers_table.insertRow(row_count)
        panel.headers_table.setItem(row_count, 0, QTableWidgetItem("X-Custom-Header"))
        panel.headers_table.setItem(row_count, 1, QTableWidgetItem("CustomValue"))

        # Verify header was added by inspecting the table
        headers = {}
        for row in range(panel.headers_table.rowCount()):
            key_item = panel.headers_table.item(row, 0)
            value_item = panel.headers_table.item(row, 1)
            if key_item and value_item:
                headers[key_item.text()] = value_item.text()

        self.assertIn("X-Custom-Header", headers)
        self.assertEqual(headers["X-Custom-Header"], "CustomValue")

    def test_request_panel_params_management(self):
        """Test parameters management in request panel."""
        panel = RequestPanel(None)

        # Simulate adding a parameter directly to the table
        row_count = panel.params_table.rowCount()
        panel.params_table.insertRow(row_count)
        panel.params_table.setItem(row_count, 0, QTableWidgetItem("newParam"))
        panel.params_table.setItem(row_count, 1, QTableWidgetItem("paramValue"))
        panel.params_table.setItem(row_count, 2, QTableWidgetItem(""))

        # Verify parameter was added by inspecting the table
        params = {}
        for row in range(panel.params_table.rowCount()):
            key_item = panel.params_table.item(row, 0)
            value_item = panel.params_table.item(row, 1)
            if key_item and value_item:
                params[key_item.text()] = value_item.text()

        self.assertIn("newParam", params)
        self.assertEqual(params["newParam"], "paramValue")

    def test_request_panel_body_management(self):
        """Test body management in request panel."""
        panel = RequestPanel(None)

        # Create a test request and load it
        test_request = Request(
            name="Test Request",
            method="POST",
            url="https://httpbin.org/post",
            body="",
            body_type="raw",
        )
        panel.load_request(test_request)

        # Simulate setting raw body content
        panel.raw_body_edit.setPlainText('{"key": "value"}')
        panel.body_type_combo.setCurrentText("raw")

        # Verify body was set via get_current_request
        current_request = panel.get_current_request()
        self.assertEqual(current_request.body, '{"key": "value"}')
        self.assertEqual(current_request.body_type, "raw")

    def test_response_panel_test_results_display(self):
        """Test test results display in response panel."""
        panel = ResponsePanel(None)

        test_results_data = {
            "passed": True,
            "passed_count": 3,
            "total_count": 4,
            "summary": "3/4 tests passed",
            "results": [
                "✓ Status code is 200 passed",
                "✓ Response time is less than 1000ms passed",
                "✓ Content-Type is present passed",
                "✗ Status code name has string OK failed (got 404)",
            ],
        }

        panel.update_test_results(test_results_data)

        # Verify test results are displayed
        test_text = panel.tests_edit.toPlainText()  # Changed from test_results_output
        self.assertIn("3/4 tests passed", test_text)
        self.assertIn("✓ Status code is 200 passed", test_text)
        self.assertIn("✗ Status code name has string OK failed", test_text)

    def test_sidebar_request_selection(self):
        """Test request selection in sidebar."""
        sidebar = Sidebar(None)
        collections = [self.collection]
        sidebar.update_collections(collections)

        # Get the request item
        collection_item = sidebar.collections_tree.topLevelItem(0)
        request_item = collection_item.child(0)

        # Simulate request selection
        with patch.object(sidebar, "request_selected") as mock_signal:
            sidebar.collections_tree.setCurrentItem(request_item)
            sidebar.on_collection_item_clicked(request_item, 0)

            # Verify signal was emitted
            mock_signal.emit.assert_called_once()

    def test_environment_panel_variable_editing(self):
        """Test environment variable editing."""
        panel = EnvironmentPanel()
        environments = [self.environment]
        panel.update_environments(environments)
        panel.env_combo.setCurrentIndex(1)  # Select "Test Environment"

        # Edit a variable by setting text in the table item directly
        panel.variables_table.item(0, 1).setText("https://new-api.example.com")

        # Verify variable was updated via the panel's internal get_current_environment
        current_env = panel.get_current_environment()
        self.assertEqual(
            current_env.variables["API_URL"], "https://new-api.example.com"
        )

    def test_request_panel_validation(self):
        """Test request validation in request panel."""
        panel = RequestPanel(None)

        # Test empty URL validation - this logic is now likely within send_request_clicked
        # We will test the observable outcome if validation is triggered.
        panel.url_edit.setText("")

        # Simulate send button click to trigger internal validation
        with patch.object(panel, "send_request") as mock_send_signal:
            panel.send_request_clicked()
            # Expect send_request signal NOT to be emitted if validation fails
            mock_send_signal.assert_not_called()

        # Test valid URL
        panel.url_edit.setText("https://httpbin.org/get")
        # Connect to the signal to verify it's emitted
        signal_emitted = False

        def on_signal_emitted(data):
            nonlocal signal_emitted
            signal_emitted = True

        panel.send_request.connect(on_signal_emitted)
        panel.send_request_clicked()
        # Expect send_request signal to be emitted if validation passes
        self.assertTrue(signal_emitted)


if __name__ == "__main__":
    unittest.main()
