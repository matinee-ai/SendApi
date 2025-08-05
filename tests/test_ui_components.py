"""
Unit tests for UI components.
"""

import unittest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.request_panel import RequestPanel
from src.response_panel import ResponsePanel
from src.sidebar import Sidebar
from src.environment_panel import EnvironmentPanel
from src.models import Request, Collection, Environment


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
        self.environment.add_variable("API_URL", "https://httpbin.org")
    
    def test_request_panel_creation(self):
        """Test RequestPanel creation and basic functionality."""
        panel = RequestPanel(None)
        
        # Test basic UI elements exist
        self.assertIsNotNone(panel.method_combo)
        self.assertIsNotNone(panel.url_edit)
        self.assertIsNotNone(panel.send_button)
        
        # Test default values
        self.assertEqual(panel.method_combo.currentText(), "GET")
        self.assertEqual(panel.url_edit.text(), "")
    
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
        self.assertIsNotNone(panel.status_label)
        self.assertIsNotNone(panel.response_text)
        self.assertIsNotNone(panel.headers_text)
        self.assertIsNotNone(panel.test_results_text)
    
    def test_response_panel_display_response(self):
        """Test displaying a response in the panel."""
        panel = ResponsePanel(None)
        
        response_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"message": "success"}',
            "response_time": 150.0
        }
        
        test_results = {
            "passed": True,
            "passed_count": 2,
            "total_count": 2,
            "summary": "2/2 tests passed",
            "results": ["Test 1 passed", "Test 2 passed"]
        }
        
        panel.display_response(response_data, test_results)
        
        # Verify status is displayed
        self.assertIn("200", panel.status_label.text())
        self.assertIn("150.0", panel.status_label.text())
        
        # Verify response body is displayed
        self.assertIn('{"message": "success"}', panel.response_text.toPlainText())
        
        # Verify headers are displayed
        self.assertIn("Content-Type", panel.headers_text.toPlainText())
    
    def test_sidebar_creation(self):
        """Test Sidebar creation."""
        sidebar = Sidebar(None)
        
        # Test basic UI elements exist
        self.assertIsNotNone(sidebar.tree_widget)
    
    def test_sidebar_update_collections(self):
        """Test updating collections in sidebar."""
        sidebar = Sidebar(None)
        collections = [self.collection]
        
        sidebar.update_collections(collections)
        
        # Verify collection is displayed
        root_item = sidebar.tree_widget.topLevelItem(0)
        self.assertIsNotNone(root_item)
        self.assertEqual(root_item.text(0), "Test Collection")
        
        # Verify request is displayed under collection
        request_item = root_item.child(0)
        self.assertIsNotNone(request_item)
        self.assertEqual(request_item.text(0), "Test Request")
    
    def test_sidebar_context_menu(self):
        """Test sidebar context menu functionality."""
        sidebar = Sidebar(None)
        collections = [self.collection]
        sidebar.update_collections(collections)
        
        # Get the collection item
        collection_item = sidebar.tree_widget.topLevelItem(0)
        
        # Test context menu for collection
        with patch('src.sidebar.QMenu') as mock_menu:
            sidebar.show_context_menu(collection_item, MagicMock())
            mock_menu.assert_called()
    
    def test_environment_panel_creation(self):
        """Test EnvironmentPanel creation."""
        panel = EnvironmentPanel()
        
        # Test basic UI elements exist
        self.assertIsNotNone(panel.environment_combo)
        self.assertIsNotNone(panel.variables_table)
    
    def test_environment_panel_update_environments(self):
        """Test updating environments in panel."""
        panel = EnvironmentPanel()
        environments = [self.environment]
        
        panel.update_environments(environments)
        
        # Verify environment is in combo box
        self.assertEqual(panel.environment_combo.count(), 1)
        self.assertEqual(panel.environment_combo.itemText(0), "Test Environment")
    
    def test_environment_panel_variable_management(self):
        """Test environment variable management."""
        panel = EnvironmentPanel()
        environments = [self.environment]
        panel.update_environments(environments)
        
        # Select the environment
        panel.environment_combo.setCurrentIndex(0)
        
        # Verify variables are displayed
        self.assertEqual(panel.variables_table.rowCount(), 1)
        self.assertEqual(panel.variables_table.item(0, 0).text(), "API_URL")
        self.assertEqual(panel.variables_table.item(0, 1).text(), "https://httpbin.org")
    
    def test_request_panel_headers_management(self):
        """Test headers management in request panel."""
        panel = RequestPanel(None)
        
        # Add a header
        panel.add_header("Content-Type", "application/json")
        
        # Verify header was added
        headers = panel.get_headers()
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
    
    def test_request_panel_params_management(self):
        """Test parameters management in request panel."""
        panel = RequestPanel(None)
        
        # Add a parameter
        panel.add_param("param1", "value1")
        
        # Verify parameter was added
        params = panel.get_params()
        self.assertIn("param1", params)
        self.assertEqual(params["param1"], "value1")
    
    def test_request_panel_body_management(self):
        """Test body management in request panel."""
        panel = RequestPanel(None)
        
        # Set body content
        panel.set_body('{"key": "value"}', "raw")
        
        # Verify body was set
        body_data = panel.get_body()
        self.assertEqual(body_data["content"], '{"key": "value"}')
        self.assertEqual(body_data["type"], "raw")
    
    def test_response_panel_test_results_display(self):
        """Test test results display in response panel."""
        panel = ResponsePanel(None)
        
        test_results = {
            "passed": True,
            "passed_count": 3,
            "total_count": 4,
            "summary": "3/4 tests passed",
            "results": [
                "✓ Status code is 200 passed",
                "✓ Response time is less than 1000ms passed",
                "✓ Content-Type is present passed",
                "✗ Status code name has string OK failed (got 404)"
            ]
        }
        
        panel.update_test_results(test_results)
        
        # Verify test results are displayed
        test_text = panel.test_results_text.toPlainText()
        self.assertIn("3/4 tests passed", test_text)
        self.assertIn("✓ Status code is 200 passed", test_text)
        self.assertIn("✗ Status code name has string OK failed", test_text)
    
    def test_sidebar_request_selection(self):
        """Test request selection in sidebar."""
        sidebar = Sidebar(None)
        collections = [self.collection]
        sidebar.update_collections(collections)
        
        # Get the request item
        collection_item = sidebar.tree_widget.topLevelItem(0)
        request_item = collection_item.child(0)
        
        # Simulate request selection
        with patch.object(sidebar, 'request_selected') as mock_signal:
            sidebar.tree_widget.setCurrentItem(request_item)
            sidebar.on_item_clicked(request_item, 0)
            
            # Verify signal was emitted
            mock_signal.emit.assert_called_once()
    
    def test_environment_panel_variable_editing(self):
        """Test environment variable editing."""
        panel = EnvironmentPanel()
        environments = [self.environment]
        panel.update_environments(environments)
        panel.environment_combo.setCurrentIndex(0)
        
        # Edit a variable
        panel.variables_table.item(0, 1).setText("https://new-api.example.com")
        
        # Verify variable was updated
        current_env = panel.get_current_environment()
        self.assertEqual(current_env.variables["API_URL"], "https://new-api.example.com")
    
    def test_request_panel_validation(self):
        """Test request validation in request panel."""
        panel = RequestPanel(None)
        
        # Test empty URL validation
        panel.url_edit.setText("")
        is_valid = panel.validate_request()
        self.assertFalse(is_valid)
        
        # Test valid URL
        panel.url_edit.setText("https://httpbin.org/get")
        is_valid = panel.validate_request()
        self.assertTrue(is_valid)
        
        # Test invalid URL
        panel.url_edit.setText("invalid-url")
        is_valid = panel.validate_request()
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main() 