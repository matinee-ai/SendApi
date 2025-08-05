"""
Request Panel for the API Testing Application
"""

import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QLabel, QGroupBox, QCheckBox,
    QSplitter, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor

from .models import Request


class RequestPanel(QWidget):
    """Panel for configuring and sending HTTP requests."""
    
    send_request = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_request = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Add request section label
        request_label = QLabel("Request")
        request_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        layout.addWidget(request_label)
        
        # Request URL and method
        url_layout = QHBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        url_layout.addWidget(self.method_combo)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter request URL")
        url_layout.addWidget(self.url_edit)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_request_clicked)
        url_layout.addWidget(self.send_btn)
        
        layout.addLayout(url_layout)
        
        # Request configuration tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Headers tab
        self.headers_tab = self.create_headers_tab()
        self.tab_widget.addTab(self.headers_tab, "Headers")
        
        # Params tab
        self.params_tab = self.create_params_tab()
        self.tab_widget.addTab(self.params_tab, "Params")
        
        # Body tab
        self.body_tab = self.create_body_tab()
        self.tab_widget.addTab(self.body_tab, "Body")
        
        # Pre-request Script tab
        self.script_tab = self.create_script_tab()
        self.tab_widget.addTab(self.script_tab, "Pre-request Script")
        
        # Tests tab
        self.tests_tab = self.create_tests_tab()
        self.tab_widget.addTab(self.tests_tab, "Tests")
        
    def create_headers_tab(self):
        """Create the headers configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Headers table
        self.headers_table = QTableWidget()
        self.headers_table.setColumnCount(2)
        self.headers_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.headers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.headers_table)
        
        # Headers buttons
        button_layout = QHBoxLayout()
        
        self.add_header_btn = QPushButton("Add Header")
        self.add_header_btn.clicked.connect(self.add_header)
        button_layout.addWidget(self.add_header_btn)
        
        self.remove_header_btn = QPushButton("Remove Header")
        self.remove_header_btn.clicked.connect(self.remove_header)
        button_layout.addWidget(self.remove_header_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_params_tab(self):
        """Create the parameters configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Params table
        self.params_table = QTableWidget()
        self.params_table.setColumnCount(3)
        self.params_table.setHorizontalHeaderLabels(["Key", "Value", "Description"])
        self.params_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.params_table)
        
        # Params buttons
        button_layout = QHBoxLayout()
        
        self.add_param_btn = QPushButton("Add Param")
        self.add_param_btn.clicked.connect(self.add_param)
        button_layout.addWidget(self.add_param_btn)
        
        self.remove_param_btn = QPushButton("Remove Param")
        self.remove_param_btn.clicked.connect(self.remove_param)
        button_layout.addWidget(self.remove_param_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_body_tab(self):
        """Create the body configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Body type selector
        body_type_layout = QHBoxLayout()
        body_type_layout.addWidget(QLabel("Body type:"))
        
        self.body_type_combo = QComboBox()
        self.body_type_combo.addItems(["none", "form-data", "x-www-form-urlencoded", "raw"])
        self.body_type_combo.currentTextChanged.connect(self.on_body_type_changed)
        body_type_layout.addWidget(self.body_type_combo)
        
        body_type_layout.addStretch()
        layout.addLayout(body_type_layout)
        
        # Body content
        self.body_stack = QTabWidget()
        layout.addWidget(self.body_stack)
        
        # Form data tab
        self.form_data_tab = self.create_form_data_tab()
        self.body_stack.addTab(self.form_data_tab, "Form Data")
        
        # Raw tab
        self.raw_tab = self.create_raw_tab()
        self.body_stack.addTab(self.raw_tab, "Raw")
        
        return widget
    
    def create_form_data_tab(self):
        """Create the form data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Form data table
        self.form_data_table = QTableWidget()
        self.form_data_table.setColumnCount(3)
        self.form_data_table.setHorizontalHeaderLabels(["Key", "Value", "Type"])
        self.form_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.form_data_table)
        
        # Form data buttons
        button_layout = QHBoxLayout()
        
        self.add_form_data_btn = QPushButton("Add Field")
        self.add_form_data_btn.clicked.connect(self.add_form_data)
        button_layout.addWidget(self.add_form_data_btn)
        
        self.remove_form_data_btn = QPushButton("Remove Field")
        self.remove_form_data_btn.clicked.connect(self.remove_form_data)
        button_layout.addWidget(self.remove_form_data_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_raw_tab(self):
        """Create the raw body tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Raw body editor
        self.raw_body_edit = QTextEdit()
        self.raw_body_edit.setPlaceholderText("Enter raw body content")
        layout.addWidget(self.raw_body_edit)
        
        return widget
    
    def create_script_tab(self):
        """Create the pre-request script tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Script editor
        self.script_edit = QTextEdit()
        self.script_edit.setPlaceholderText("Enter pre-request script (JavaScript)")
        layout.addWidget(self.script_edit)
        
        return widget
    
    def create_tests_tab(self):
        """Create the tests tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tests editor
        self.tests_edit = QTextEdit()
        self.tests_edit.setPlaceholderText("Enter test scripts (JavaScript)")
        layout.addWidget(self.tests_edit)
        
        return widget
    
    def on_body_type_changed(self, body_type):
        """Handle body type change."""
        if body_type == "none":
            self.body_stack.setCurrentIndex(0)
        elif body_type in ["form-data", "x-www-form-urlencoded"]:
            self.body_stack.setCurrentIndex(0)
        elif body_type == "raw":
            self.body_stack.setCurrentIndex(1)
    
    def add_header(self):
        """Add a new header."""
        key, ok = QInputDialog.getText(self, "Add Header", "Header name:")
        if ok and key:
            value, ok = QInputDialog.getText(self, "Add Header", "Header value:")
            if ok:
                row = self.headers_table.rowCount()
                self.headers_table.insertRow(row)
                self.headers_table.setItem(row, 0, QTableWidgetItem(key))
                self.headers_table.setItem(row, 1, QTableWidgetItem(value))
    
    def remove_header(self):
        """Remove the selected header."""
        current_row = self.headers_table.currentRow()
        if current_row >= 0:
            self.headers_table.removeRow(current_row)
    
    def add_param(self):
        """Add a new parameter."""
        key, ok = QInputDialog.getText(self, "Add Parameter", "Parameter name:")
        if ok and key:
            value, ok = QInputDialog.getText(self, "Add Parameter", "Parameter value:")
            if ok:
                row = self.params_table.rowCount()
                self.params_table.insertRow(row)
                self.params_table.setItem(row, 0, QTableWidgetItem(key))
                self.params_table.setItem(row, 1, QTableWidgetItem(value))
                self.params_table.setItem(row, 2, QTableWidgetItem(""))
    
    def remove_param(self):
        """Remove the selected parameter."""
        current_row = self.params_table.currentRow()
        if current_row >= 0:
            self.params_table.removeRow(current_row)
    
    def add_form_data(self):
        """Add a new form data field."""
        key, ok = QInputDialog.getText(self, "Add Field", "Field name:")
        if ok and key:
            value, ok = QInputDialog.getText(self, "Add Field", "Field value:")
            if ok:
                row = self.form_data_table.rowCount()
                self.form_data_table.insertRow(row)
                self.form_data_table.setItem(row, 0, QTableWidgetItem(key))
                self.form_data_table.setItem(row, 1, QTableWidgetItem(value))
                
                type_combo = QComboBox()
                type_combo.addItems(["Text", "File"])
                self.form_data_table.setCellWidget(row, 2, type_combo)
    
    def remove_form_data(self):
        """Remove the selected form data field."""
        current_row = self.form_data_table.currentRow()
        if current_row >= 0:
            self.form_data_table.removeRow(current_row)
    
    def load_request(self, request):
        """Load a request into the panel."""
        print(f"RequestPanel: Loading request: {request.name}")
        self.current_request = request
        
        # Load basic request data
        self.method_combo.setCurrentText(request.method)
        self.url_edit.setText(request.url)
        
        # Load headers
        self.headers_table.setRowCount(0)
        for key, value in request.headers.items():
            row = self.headers_table.rowCount()
            self.headers_table.insertRow(row)
            self.headers_table.setItem(row, 0, QTableWidgetItem(key))
            self.headers_table.setItem(row, 1, QTableWidgetItem(value))
        
        # Load parameters
        self.params_table.setRowCount(0)
        for key, value in request.params.items():
            row = self.params_table.rowCount()
            self.params_table.insertRow(row)
            self.params_table.setItem(row, 0, QTableWidgetItem(key))
            self.params_table.setItem(row, 1, QTableWidgetItem(value))
            self.params_table.setItem(row, 2, QTableWidgetItem(""))
        
        # Load body
        self.body_type_combo.setCurrentText(request.body_type)
        self.raw_body_edit.setPlainText(request.body)
        
        # Load scripts
        self.script_edit.setPlainText(request.pre_request_script)
        self.tests_edit.setPlainText(request.tests)
    
    def save_request(self):
        """Save the current request data."""
        if not self.current_request:
            return
        
        # Save basic request data
        self.current_request.method = self.method_combo.currentText()
        self.current_request.url = self.url_edit.text()
        
        # Save headers
        headers = {}
        for row in range(self.headers_table.rowCount()):
            key_item = self.headers_table.item(row, 0)
            value_item = self.headers_table.item(row, 1)
            if key_item and value_item:
                headers[key_item.text()] = value_item.text()
        self.current_request.headers = headers
        
        # Save parameters
        params = {}
        for row in range(self.params_table.rowCount()):
            key_item = self.params_table.item(row, 0)
            value_item = self.params_table.item(row, 1)
            if key_item and value_item:
                params[key_item.text()] = value_item.text()
        self.current_request.params = params
        
        # Save body
        self.current_request.body_type = self.body_type_combo.currentText()
        self.current_request.body = self.raw_body_edit.toPlainText()
        
        # Save scripts
        self.current_request.pre_request_script = self.script_edit.toPlainText()
        self.current_request.tests = self.tests_edit.toPlainText()
    
    def send_request_clicked(self):
        """Handle send request button click."""
        print(f"RequestPanel: Send button clicked!")
        # Save current request
        self.save_request()
        
        # Prepare request data
        request_data = {
            "method": self.method_combo.currentText(),
            "url": self.url_edit.text(),
            "headers": {},
            "params": {},
            "body": "",
            "body_type": self.body_type_combo.currentText(),
            "pre_request_script": self.script_edit.toPlainText(),
            "tests": self.tests_edit.toPlainText()
        }
        
        # Get headers
        for row in range(self.headers_table.rowCount()):
            key_item = self.headers_table.item(row, 0)
            value_item = self.headers_table.item(row, 1)
            if key_item and value_item:
                request_data["headers"][key_item.text()] = value_item.text()
        
        # Get parameters
        for row in range(self.params_table.rowCount()):
            key_item = self.params_table.item(row, 0)
            value_item = self.params_table.item(row, 1)
            if key_item and value_item:
                request_data["params"][key_item.text()] = value_item.text()
        
        # Get body
        if self.body_type_combo.currentText() == "raw":
            request_data["body"] = self.raw_body_edit.toPlainText()
        elif self.body_type_combo.currentText() in ["form-data", "x-www-form-urlencoded"]:
            # Convert form data to appropriate format
            form_data = {}
            for row in range(self.form_data_table.rowCount()):
                key_item = self.form_data_table.item(row, 0)
                value_item = self.form_data_table.item(row, 1)
                if key_item and value_item:
                    form_data[key_item.text()] = value_item.text()
            
            if self.body_type_combo.currentText() == "x-www-form-urlencoded":
                import urllib.parse
                request_data["body"] = urllib.parse.urlencode(form_data)
            else:
                request_data["body"] = json.dumps(form_data)
        
        # Emit signal
        print(f"RequestPanel: Emitting request data: {request_data.get('method')} {request_data.get('url')}")
        self.send_request.emit(request_data)
    
    def get_current_request(self):
        """Get the current request object."""
        if not self.current_request:
            return None
        
        # Update current request with current UI data
        self.current_request.method = self.method_combo.currentText()
        self.current_request.url = self.url_edit.text()
        
        # Update headers
        headers = {}
        for row in range(self.headers_table.rowCount()):
            key_item = self.headers_table.item(row, 0)
            value_item = self.headers_table.item(row, 1)
            if key_item and value_item and key_item.text().strip():
                headers[key_item.text().strip()] = value_item.text().strip()
        self.current_request.headers = headers
        
        # Update params
        params = {}
        for row in range(self.params_table.rowCount()):
            key_item = self.params_table.item(row, 0)
            value_item = self.params_table.item(row, 1)
            if key_item and value_item and key_item.text().strip():
                params[key_item.text().strip()] = value_item.text().strip()
        self.current_request.params = params
        
        # Update body
        self.current_request.body = self.raw_body_edit.toPlainText()
        self.current_request.body_type = self.body_type_combo.currentText().lower().replace(' ', '-')
        
        # Update scripts
        self.current_request.pre_request_script = self.script_edit.toPlainText()
        self.current_request.tests = self.tests_edit.toPlainText()
        
        return self.current_request 