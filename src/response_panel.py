"""
Response Panel for the API Testing Application
"""

import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .models import Response


class ResponsePanel(QWidget):
    """Panel for displaying HTTP responses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_response = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Add response section label
        response_label = QLabel("Response")
        response_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px; background-color: #ecf0f1; border-radius: 3px;"
        )
        layout.addWidget(response_label)

        # Response status and info
        self.create_status_section(layout)

        # Response content tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setMaximumHeight(300)  # Limit height to make it more compact
        layout.addWidget(self.tab_widget)

        # Body tab
        self.body_tab = self.create_body_tab()
        self.tab_widget.addTab(self.body_tab, "Body")

        # Headers tab
        self.headers_tab = self.create_headers_tab()
        self.tab_widget.addTab(self.headers_tab, "Headers")

        # Cookies tab
        self.cookies_tab = self.create_cookies_tab()
        self.tab_widget.addTab(self.cookies_tab, "Cookies")

        # Test Results tab
        self.tests_tab = self.create_tests_tab()
        self.tab_widget.addTab(self.tests_tab, "Test Results")

    def create_status_section(self, layout):
        """Create the status information section."""
        status_group = QGroupBox("Response Status")
        status_group.setMaximumHeight(120)  # Make status section more compact
        status_layout = QFormLayout(status_group)

        # Status code
        self.status_code_label = QLabel("")
        self.status_code_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addRow("Status:", self.status_code_label)

        # Response time
        self.response_time_label = QLabel("")
        status_layout.addRow("Time:", self.response_time_label)

        # Size
        self.size_label = QLabel("")
        status_layout.addRow("Size:", self.size_label)

        # URL
        self.url_label = QLabel("")
        self.url_label.setWordWrap(True)
        status_layout.addRow("URL:", self.url_label)

        layout.addWidget(status_group)

    def create_body_tab(self):
        """Create the response body tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Body type selector
        body_type_layout = QHBoxLayout()
        body_type_layout.addWidget(QLabel("Body type:"))

        self.body_type_label = QLabel("")
        body_type_layout.addWidget(self.body_type_label)
        body_type_layout.addStretch()

        layout.addLayout(body_type_layout)

        # Body content
        self.body_edit = QTextEdit()
        self.body_edit.setReadOnly(True)
        self.body_edit.setMaximumHeight(200)  # Limit height to make it more compact
        layout.addWidget(self.body_edit)

        return widget

    def create_headers_tab(self):
        """Create the response headers tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Headers table
        self.headers_table = QTableWidget()
        self.headers_table.setColumnCount(2)
        self.headers_table.setHorizontalHeaderLabels(["Header", "Value"])
        self.headers_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.headers_table.setMaximumHeight(150)  # Limit height to make it more compact
        layout.addWidget(self.headers_table)

        return widget

    def create_cookies_tab(self):
        """Create the cookies tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Cookies table
        self.cookies_table = QTableWidget()
        self.cookies_table.setColumnCount(4)
        self.cookies_table.setHorizontalHeaderLabels(
            ["Name", "Value", "Domain", "Path"]
        )
        self.cookies_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.cookies_table.setMaximumHeight(100)  # Limit height to make it more compact
        layout.addWidget(self.cookies_table)

        return widget

    def create_tests_tab(self):
        """Create the test results tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Test results
        self.tests_edit = QTextEdit()
        self.tests_edit.setReadOnly(True)
        self.tests_edit.setMaximumHeight(100)  # Limit height to make it more compact
        layout.addWidget(self.tests_edit)

        return widget

    def display_response(self, response_data):
        """Display a response in the panel."""
        print(
            f"ResponsePanel: Received response with status {response_data.get('status_code', 'Unknown')}"
        )
        self.current_response = response_data

        # Update status information
        status_code = response_data.get("status_code", 0)
        print(f"ResponsePanel: Updating status code to {status_code}")
        self.status_code_label.setText(f"{status_code}")

        # Set status code color
        if 200 <= status_code < 300:
            self.status_code_label.setStyleSheet(
                "color: green; font-weight: bold; font-size: 14px;"
            )
        elif 300 <= status_code < 400:
            self.status_code_label.setStyleSheet(
                "color: orange; font-weight: bold; font-size: 14px;"
            )
        elif 400 <= status_code < 500:
            self.status_code_label.setStyleSheet(
                "color: red; font-weight: bold; font-size: 14px;"
            )
        elif 500 <= status_code < 600:
            self.status_code_label.setStyleSheet(
                "color: darkred; font-weight: bold; font-size: 14px;"
            )
        else:
            self.status_code_label.setStyleSheet(
                "color: gray; font-weight: bold; font-size: 14px;"
            )

        # Update other status info
        response_time = response_data.get("response_time", 0.0)
        self.response_time_label.setText(f"{response_time:.2f} ms")

        size = response_data.get("size", 0)
        self.size_label.setText(self.format_size(size))

        url = response_data.get("url", "")
        self.url_label.setText(url)

        # Update body
        body = response_data.get("body", "")
        print(f"ResponsePanel: Updating response body (length: {len(body)})")
        self.body_edit.setPlainText(body)

        # Try to format JSON
        try:
            if body.strip():
                parsed_json = json.loads(body)
                formatted_json = json.dumps(parsed_json, indent=2)
                self.body_edit.setPlainText(formatted_json)
                self.body_type_label.setText("JSON")
        except (json.JSONDecodeError, ValueError):
            # Check if it's HTML
            if body.strip().startswith("<") and body.strip().endswith(">"):
                self.body_type_label.setText("HTML")
            else:
                self.body_type_label.setText("Text")

        # Update headers
        headers = response_data.get("headers", {})
        print(f"ResponsePanel: Updating response headers (count: {len(headers)})")
        self.headers_table.setRowCount(len(headers))

        for i, (key, value) in enumerate(headers.items()):
            self.headers_table.setItem(i, 0, QTableWidgetItem(key))
            self.headers_table.setItem(i, 1, QTableWidgetItem(value))

        # Update cookies (placeholder for now)
        self.cookies_table.setRowCount(0)

        # Update test results
        test_results = response_data.get("test_results", "No tests executed")
        print(f"ResponsePanel: Updating test results: {test_results}")
        self.update_test_results(test_results)

    def format_size(self, size_bytes):
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def clear_response(self):
        """Clear the response display."""
        print("ResponsePanel: Clearing response display")
        self.status_code_label.setText("")
        self.response_time_label.setText("")
        self.size_label.setText("")
        self.url_label.setText("")
        self.body_edit.clear()
        self.headers_table.setRowCount(0)
        self.cookies_table.setRowCount(0)
        self.tests_edit.clear()
        self.body_type_label.setText("")

    def display_error(self, error_message):
        """Display an error message."""
        print(f"ResponsePanel: Displaying error: {error_message}")
        self.clear_response()
        self.status_code_label.setText("Error")
        self.status_code_label.setStyleSheet(
            "color: red; font-weight: bold; font-size: 14px;"
        )
        self.body_edit.setPlainText(f"Request failed: {error_message}")
        self.body_type_label.setText("Error")
        print(f"ResponsePanel: Error displayed in body: {error_message}")

    def update_test_results(self, test_results):
        """Update test results with visual feedback."""
        if isinstance(test_results, dict):
            # New format with detailed results
            passed = test_results.get("passed", True)
            results = test_results.get("results", [])
            summary = test_results.get("summary", "")

            # Set background color based on test results
            if passed:
                self.tests_edit.setStyleSheet(
                    """
                    QTextEdit {
                        background-color: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 5px;
                    }
                """
                )
            else:
                self.tests_edit.setStyleSheet(
                    """
                    QTextEdit {
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        color: #721c24;
                        padding: 5px;
                    }
                """
                )

            # Display results
            content = f"Test Results: {summary}\n\n"
            for result in results:
                content += f"{result}\n"

            self.tests_edit.setPlainText(content)
        else:
            # Old format (string)
            self.tests_edit.setStyleSheet("")
            self.tests_edit.setPlainText(str(test_results))
