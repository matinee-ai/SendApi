"""
Main Window for the API Testing Application
"""

import json
import os

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .batch_request_runner import BatchRequestRunner
from .models import Collection, Environment, Request
from .request_panel import RequestPanel
from .request_runner import RequestRunner
from .response_panel import ResponsePanel
from .sidebar import Sidebar


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.collections = []
        self.environments = []
        self.current_environment = None
        self.current_request = None

        self.init_ui()
        self.setup_menus()
        self.load_data()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SendApi - API Testing Tool")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)

        # Create header toolbar
        self.create_header_toolbar(main_layout)

        # Create content layout
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        content_layout.addWidget(splitter)

        # Create sidebar with collections
        self.sidebar = Sidebar(self)

        # Create environment panel
        self.environment_panel = self.create_environment_panel()

        # Create left panel with sidebar and environment
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(self.sidebar)
        left_layout.addWidget(self.environment_panel)

        splitter.addWidget(left_panel)

        # Create main content area with tabs
        self.content_tab_widget = QTabWidget()

        # Create request/response tab
        request_response_widget = QWidget()
        request_response_layout = QVBoxLayout(request_response_widget)

        # Create request and response panels
        self.request_panel = RequestPanel(self)
        self.response_panel = ResponsePanel(self)

        # Create splitter for request and response panels
        request_response_splitter = QSplitter(Qt.Orientation.Vertical)
        request_response_splitter.addWidget(self.request_panel)
        request_response_splitter.addWidget(self.response_panel)

        # Set splitter proportions (request panel takes more space)
        request_response_splitter.setSizes([600, 400])

        request_response_layout.addWidget(request_response_splitter)

        # Create batch testing tab
        self.batch_testing_widget = self.create_batch_testing_widget()

        # Add tabs
        self.content_tab_widget.addTab(request_response_widget, "Request/Response")
        self.content_tab_widget.addTab(self.batch_testing_widget, "Batch Testing")

        splitter.addWidget(self.content_tab_widget)

        # Set splitter proportions
        splitter.setSizes([300, 1100])

        # Connect signals
        self.sidebar.request_selected.connect(self.on_request_selected)
        self.request_panel.send_request.connect(self.on_send_request)
        self.environment_panel.environment_changed.connect(self.on_environment_changed)

        # Add console output for debugging
        print("API Tester application initialized successfully!")
        print("Main window created with sidebar and panels")

    def create_header_toolbar(self, parent_layout):
        """Create the header toolbar with main action buttons."""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # Style the toolbar
        toolbar_widget.setStyleSheet(
            """
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """
        )

        # Import button
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.import_file)
        import_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #117a8b;
            }
        """
        )
        toolbar_layout.addWidget(import_btn)

        # Save Request as cURL button
        save_curl_btn = QPushButton("Save as cURL")
        save_curl_btn.clicked.connect(self.save_request_as_curl)
        save_curl_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """
        )
        toolbar_layout.addWidget(save_curl_btn)

        # Save Response button
        save_response_btn = QPushButton("Save Response")
        save_response_btn.clicked.connect(self.save_response)
        save_response_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8690b;
            }
        """
        )
        toolbar_layout.addWidget(save_response_btn)

        # Add stretch to push buttons to the left
        toolbar_layout.addStretch()

        parent_layout.addWidget(toolbar_widget)

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About SendApi",
            "SendApi v1.0\n\n"
            "A desktop application for testing APIs.\n"
            "Supports collections, environments, and request/response management.",
        )

    def load_data(self):
        """Load saved collections and environments."""
        # Load collections
        if os.path.exists("collections.json"):
            try:
                with open("collections.json", "r") as f:
                    collections_data = json.load(f)
                    for coll_data in collections_data:
                        collection = Collection.from_dict(coll_data)
                        self.collections.append(collection)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load collections: {e}")

        # Load environments
        if os.path.exists("environments.json"):
            try:
                with open("environments.json", "r") as f:
                    envs_data = json.load(f)
                    for env_data in envs_data:
                        environment = Environment.from_dict(env_data)
                        self.environments.append(environment)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load environments: {e}")

        # Update sidebar and environment panel
        self.sidebar.update_collections(self.collections)
        self.environment_panel.update_environments(self.environments)

    def save_data(self):
        """Save collections and environments to files."""
        # Save collections
        collections_data = [coll.to_dict() for coll in self.collections]
        with open("collections.json", "w") as f:
            json.dump(collections_data, f, indent=2)

        # Save environments
        envs_data = [env.to_dict() for env in self.environments]
        with open("environments.json", "w") as f:
            json.dump(envs_data, f, indent=2)

    def new_collection(self):
        """Create a new collection."""
        name, ok = QInputDialog.getText(self, "New Collection", "Collection name:")
        if ok and name:
            collection = Collection(name)
            self.collections.append(collection)
            self.sidebar.update_collections(self.collections)
            self.save_data()

    def new_environment(self):
        """Create a new environment."""
        name, ok = QInputDialog.getText(self, "New Environment", "Environment name:")
        if ok and name:
            environment = Environment(name)
            self.environments.append(environment)
            self.environment_panel.update_environments(self.environments)
            self.save_data()

    def import_file(self):
        """Import collections and environments from file (unified import)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Collection/Environment", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                from .postman_importer import PostmanImporter

                imported_collections, imported_environments = (
                    PostmanImporter.import_file(file_path)
                )

                # Add all imported collections
                for collection in imported_collections:
                    self.collections.append(collection)

                # Add all imported environments
                for environment in imported_environments:
                    self.environments.append(environment)

                # Update UI
                self.sidebar.update_collections(self.collections)
                self.environment_panel.update_environments(self.environments)
                self.save_data()

                # Show success message
                success_messages = []
                if imported_collections:
                    if len(imported_collections) == 1:
                        success_messages.append(
                            f"Collection '{imported_collections[0].name}'"
                        )
                    else:
                        success_messages.append(
                            f"{len(imported_collections)} collections"
                        )

                if imported_environments:
                    if len(imported_environments) == 1:
                        success_messages.append(
                            f"Environment '{imported_environments[0].name}'"
                        )
                    else:
                        success_messages.append(
                            f"{len(imported_environments)} environments"
                        )

                if success_messages:
                    message = f"Imported: {', '.join(success_messages)}"
                    QMessageBox.information(self, "Success", message)
                else:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "No collections or environments found in the file.",
                    )

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import file: {e}")

    def import_collection(self):
        """Import collections and environments from file."""
        self.import_file()

    def import_environment(self):
        """Import environment from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Environment", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                from .postman_importer import PostmanImporter

                imported_environments = PostmanImporter.import_environment(file_path)

                # Add all imported environments
                for environment in imported_environments:
                    self.environments.append(environment)

                # Update UI
                self.environment_panel.update_environments(self.environments)
                self.save_data()

                # Show success message
                if len(imported_environments) == 1:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Environment '{imported_environments[0].name}' imported successfully!",
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"{len(imported_environments)} environments imported successfully!",
                    )

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import environment: {e}")

    def save_request_as_curl(self):
        """Save the current request as a cURL command."""
        current_request = self.request_panel.get_current_request()
        if not current_request:
            QMessageBox.warning(self, "Warning", "No request selected.")
            return

        try:
            # Generate cURL command
            curl_command = self._generate_curl_command(current_request)

            # Ask user for file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save cURL Command",
                f"{current_request.name}.sh",
                "Shell Scripts (*.sh);;Text Files (*.txt);;All Files (*)",
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(curl_command)
                QMessageBox.information(
                    self, "Success", f"cURL command saved to {file_path}"
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save cURL command: {e}")

    def save_response(self):
        """Save the current response to a file."""
        if not hasattr(self, "last_response") or not self.last_response:
            QMessageBox.warning(self, "Warning", "No response to save.")
            return

        try:
            # Get response body from dictionary
            response_body = self.last_response.get("body", "")

            if not response_body:
                QMessageBox.warning(self, "Warning", "No response body to save.")
                return

            # Ask user for file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Response",
                "response.txt",
                "Text Files (*.txt);;JSON Files (*.json);;All Files (*)",
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response_body)
                QMessageBox.information(
                    self, "Success", f"Response saved to {file_path}"
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save response: {e}")

    def _generate_curl_command(self, request):
        """Generate a cURL command from a request."""
        curl_parts = ["curl"]

        # Add method
        if request.method.upper() != "GET":
            curl_parts.append(f"-X {request.method.upper()}")

        # Add headers
        for key, value in request.headers.items():
            curl_parts.append(f'-H "{key}: {value}"')

        # Add query parameters
        if request.params:
            param_str = "&".join([f"{k}={v}" for k, v in request.params.items()])
            if "?" in request.url:
                url = f"{request.url}&{param_str}"
            else:
                url = f"{request.url}?{param_str}"
        else:
            url = request.url

        # Add body
        if request.body and request.body_type != "none":
            if request.body_type == "raw":
                curl_parts.append(f"--data-raw '{request.body}'")
            elif request.body_type == "x-www-form-urlencoded":
                curl_parts.append(f'--data-raw "{request.body}"')
            elif request.body_type == "form-data":
                # Handle form data
                try:
                    import json

                    form_data = json.loads(request.body)
                    for key, value in form_data.items():
                        curl_parts.append(f'-F "{key}={value}"')
                except:
                    curl_parts.append(f'--data-raw "{request.body}"')

        # Add URL
        curl_parts.append(f'"{url}"')

        generated_curl = " ".join(curl_parts)
        print(f"DEBUG: Generated cURL command: {generated_curl}")  # Debug print
        return generated_curl

    def export_collection(self):
        """Export a collection to file."""
        if not self.collections:
            QMessageBox.information(self, "Info", "No collections to export.")
            return

        # TODO: Add collection selection dialog
        collection = self.collections[0]  # For now, export first collection

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Collection", f"{collection.name}.json", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(collection.to_dict(), f, indent=2)
                QMessageBox.information(
                    self, "Success", "Collection exported successfully!"
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export collection: {e}")

    def manage_environments(self):
        """Open environment management dialog."""
        # TODO: Implement environment management dialog
        QMessageBox.information(self, "Info", "Environment management coming soon!")

    def on_request_selected(self, request):
        """Handle request selection from sidebar."""
        self.current_request = request
        self.request_panel.load_request(request)

    def on_send_request(self, request_data):
        """Handle send request from request panel."""
        print(
            f"Sending request: {request_data.get('method', 'GET')} {request_data.get('url', 'No URL')}"
        )

        # Get current environment from environment panel
        current_environment = self.environment_panel.get_current_environment()

        # Create request runner
        self.request_runner = RequestRunner(request_data, current_environment)
        self.request_runner.response_received.connect(
            self.response_panel.display_response
        )
        self.request_runner.response_received.connect(self.on_response_received)
        self.request_runner.error_occurred.connect(self.on_request_error)
        self.request_runner.start()

        print("Request runner started...")

    def on_environment_changed(self, environment):
        """Handle environment selection change."""
        print(f"Environment changed to: {environment.name if environment else 'None'}")
        self.current_environment = environment

    def on_environment_updated(self, environment):
        """Handle environment updates (rename/delete)."""
        if environment is None:
            # Environment was deleted
            self.current_environment = None
        else:
            # Environment was renamed or modified
            self.current_environment = environment

        # Save data to persist changes
        self.save_data()

    def on_response_received(self, response):
        """Handle response received from request runner."""
        self.last_response = response
        print(f"Response received and stored: {response.get('status_code', 'Unknown')}")

    def on_request_error(self, error_message):
        """Handle request errors."""
        print(f"Request error: {error_message}")
        QMessageBox.warning(self, "Request Error", error_message)

    def run_all_requests(self, requests):
        """Run all requests in a collection."""
        if not requests:
            print("No requests to run")
            return

        print(f"MainWindow: Starting batch run of {len(requests)} requests...")

        # Store requests for batch testing
        self.current_batch_requests = requests

        # Switch to batch testing tab
        self.content_tab_widget.setCurrentIndex(1)  # Switch to batch testing tab

        # Prepare the batch testing interface
        self.prepare_batch_testing(requests)

        # Get current environment
        current_environment = self.environment_panel.get_current_environment()
        print(
            f"MainWindow: Using environment: {current_environment.name if current_environment else 'None'}"
        )

        # Create a runner for all requests
        self.batch_runner = BatchRequestRunner(requests, current_environment, self)
        self.batch_runner.request_completed.connect(self.on_batch_request_completed)
        self.batch_runner.all_completed.connect(self.on_batch_all_completed)
        self.batch_runner.start()

        print(f"MainWindow: Batch runner started")

    def prepare_batch_testing(self, requests):
        """Prepare the batch testing interface."""
        # Clear previous results
        self.results_table.setRowCount(0)

        # Add requests to table
        for i, request in enumerate(requests):
            self.results_table.insertRow(i)
            self.results_table.setItem(i, 0, QTableWidgetItem(request.name))
            self.results_table.setItem(i, 1, QTableWidgetItem("Pending"))
            self.results_table.setItem(i, 2, QTableWidgetItem(""))

        # Update progress
        self.progress_label.setText(f"Ready to run {len(requests)} requests")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(requests))
        self.progress_bar.setValue(0)

        # Disable start button
        self.start_batch_btn.setEnabled(False)

    def start_batch_test(self):
        """Start batch testing manually."""
        if not self.current_batch_requests:
            QMessageBox.information(
                self,
                "Info",
                "No requests selected for batch testing. Please run 'Run All Requests' from a collection first.",
            )
            return

        self.run_all_requests(self.current_batch_requests)

    def clear_batch_results(self):
        """Clear batch testing results."""
        self.results_table.setRowCount(0)
        self.progress_label.setText("Ready to run batch tests")
        self.progress_bar.setVisible(False)
        self.summary_label.setText("No tests run yet")
        # Don't clear current_batch_requests - keep them for re-running
        self.start_batch_btn.setEnabled(True)

    def on_batch_request_completed(self, request, response, test_results):
        """Handle completion of a single request in batch."""
        print(
            f"MainWindow: Batch request completed: {request.name} - Status: {response.get('status_code', 'Unknown')}"
        )

        # Find the request in the results table
        for row in range(self.results_table.rowCount()):
            if self.results_table.item(row, 0).text() == request.name:
                # Update status and test results combined
                status = response.get("status_code", 0)
                if isinstance(status, str):
                    try:
                        status = int(status)
                    except ValueError:
                        status = 0

                # Create combined status and test results text
                status_text = f"Status: {status}"
                if isinstance(test_results, dict):
                    test_summary = test_results.get("summary", "No tests")
                    status_text += f" | {test_summary}"
                else:
                    status_text += f" | {str(test_results)}"

                status_item = QTableWidgetItem(status_text)

                # Set background color based on status and test results
                if 200 <= status < 300:
                    if isinstance(test_results, dict) and test_results.get(
                        "passed", False
                    ):
                        status_item.setBackground(QColor(144, 238, 144))  # Light green
                    else:
                        status_item.setBackground(QColor(255, 255, 224))  # Light yellow
                elif 400 <= status < 500:
                    status_item.setBackground(QColor(255, 182, 193))  # Light red
                elif 500 <= status < 600:
                    status_item.setBackground(QColor(255, 160, 122))  # Light orange
                else:
                    status_item.setBackground(QColor(255, 255, 224))  # Light yellow

                self.results_table.setItem(row, 1, status_item)

                # Update response time
                response_time = response.get("response_time", 0)
                self.results_table.setItem(
                    row, 2, QTableWidgetItem(f"{response_time:.2f} ms")
                )
                break

        # Update progress
        current_progress = self.progress_bar.value() + 1
        self.progress_bar.setValue(current_progress)
        self.progress_label.setText(
            f"Completed {current_progress}/{self.progress_bar.maximum()} requests"
        )

        # Update the response panel with the latest response
        self.response_panel.display_response(response)
        self.response_panel.update_test_results(test_results)

    def on_batch_all_completed(self, results):
        """Handle completion of all requests in batch."""
        print(f"MainWindow: Batch run completed. {len(results)} requests processed.")

        # Update progress
        self.progress_label.setText(
            f"Batch testing completed! {len(results)} requests processed."
        )
        self.progress_bar.setValue(self.progress_bar.maximum())

        # Calculate summary
        passed = sum(1 for result in results if result.get("tests_passed", False))
        failed = len(results) - passed

        # Update summary label
        summary_text = f"✓ Completed: {len(results)} requests | ✓ Passed: {passed} | ✗ Failed: {failed}"
        self.summary_label.setText(summary_text)

        # Re-enable start button
        self.start_batch_btn.setEnabled(True)

        # Show completion message
        QMessageBox.information(
            self,
            "Batch Run Complete",
            f"Batch testing completed!\n\n"
            f"Total requests: {len(results)}\n"
            f"Passed: {passed}\n"
            f"Failed: {failed}",
        )

    def create_environment_panel(self):
        """Create the environment management panel."""
        from .environment_panel import EnvironmentPanel

        return EnvironmentPanel(self)

    def create_batch_testing_widget(self):
        """Create the batch testing widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header_label = QLabel("Batch Testing")
        header_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #2c3e50; padding: 10px; background-color: #ecf0f1; border-radius: 5px;"
        )
        layout.addWidget(header_label)

        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_label = QLabel("Ready to run batch tests")
        self.progress_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_group)

        # Results section
        results_group = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_group)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(
            ["Request", "Status & Tests", "Response Time"]
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.results_table.setMaximumHeight(300)
        results_layout.addWidget(self.results_table)

        # Summary
        self.summary_label = QLabel("No tests run yet")
        self.summary_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; color: #2c3e50; padding: 5px;"
        )
        results_layout.addWidget(self.summary_label)

        layout.addWidget(results_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_batch_btn = QPushButton("Start Batch Test")
        self.start_batch_btn.clicked.connect(self.start_batch_test)
        self.start_batch_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        button_layout.addWidget(self.start_batch_btn)

        self.clear_results_btn = QPushButton("Clear Results")
        self.clear_results_btn.clicked.connect(self.clear_batch_results)
        self.clear_results_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        button_layout.addWidget(self.clear_results_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Store current batch requests
        self.current_batch_requests = []

        return widget

    def closeEvent(self, event):
        """Handle application close event."""
        self.save_data()
        event.accept()
