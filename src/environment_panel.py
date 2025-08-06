"""
Environment Panel for the API Testing Application
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGroupBox, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .models import Environment


class EnvironmentPanel(QWidget):
    """Panel for managing environment variables."""
    
    environment_changed = Signal(Environment)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.environments = []
        self.current_environment = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Environment section label
        env_label = QLabel("Environment")
        env_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        layout.addWidget(env_label)
        
        # Environment selector
        env_group = QGroupBox("Active Environment")
        env_group.setMaximumHeight(80)
        env_layout = QVBoxLayout(env_group)
        
        self.env_combo = QComboBox()
        self.env_combo.currentTextChanged.connect(self.on_environment_changed)
        env_layout.addWidget(self.env_combo)
        
        layout.addWidget(env_group)
        
        # Variables section
        vars_group = QGroupBox("Variables")
        vars_layout = QVBoxLayout(vars_group)
        
        # Variables table
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(2)
        self.variables_table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.variables_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.variables_table.setMaximumHeight(200)
        self.variables_table.itemChanged.connect(self.on_variable_changed)
        vars_layout.addWidget(self.variables_table)
        
        # Variable buttons
        var_button_layout = QHBoxLayout()
        
        self.add_var_btn = QPushButton("Add")
        self.add_var_btn.clicked.connect(self.add_variable)
        var_button_layout.addWidget(self.add_var_btn)
        
        self.remove_var_btn = QPushButton("Remove")
        self.remove_var_btn.clicked.connect(self.remove_variable)
        var_button_layout.addWidget(self.remove_var_btn)
        
        vars_layout.addLayout(var_button_layout)
        layout.addWidget(vars_group)
        
        # Add some spacing at the bottom
        layout.addStretch()
        
    def update_environments(self, environments):
        """Update the environments list."""
        self.environments = environments
        self.env_combo.clear()
        self.env_combo.addItem("No Environment")
        
        for environment in environments:
            self.env_combo.addItem(environment.name, environment)
    
    def on_environment_changed(self, environment_name):
        """Handle environment selection change."""
        if environment_name == "No Environment":
            self.update_variables_table({})
            self.current_environment = None
            return
        
        for environment in self.environments:
            if environment.name == environment_name:
                self.update_variables_table(environment.variables)
                self.current_environment = environment
                self.environment_changed.emit(environment)
                break
    
    def update_variables_table(self, variables):
        """Update the variables table."""
        self.variables_table.setRowCount(len(variables))
        
        for i, (key, value) in enumerate(variables.items()):
            key_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(value)
            
            self.variables_table.setItem(i, 0, key_item)
            self.variables_table.setItem(i, 1, value_item)
    
    def add_variable(self):
        """Add a new environment variable."""
        current_env = self.env_combo.currentData()
        if not current_env:
            QMessageBox.information(self, "Info", "Please select an environment first.")
            return
        
        key, ok = QInputDialog.getText(self, "Add Variable", "Variable name:")
        if ok and key:
            value, ok = QInputDialog.getText(self, "Add Variable", "Variable value:")
            if ok:
                current_env.set_variable(key, value)
                self.update_variables_table(current_env.variables)
                self.environment_changed.emit(current_env)
    
    def remove_variable(self):
        """Remove a variable from the current environment."""
        current_env = self.env_combo.currentData()
        if not current_env:
            return
        
        current_row = self.variables_table.currentRow()
        if current_row >= 0:
            key_item = self.variables_table.item(current_row, 0)
            if key_item:
                key = key_item.text()
                current_env.remove_variable(key)
                self.update_variables_table(current_env.variables)
                self.environment_changed.emit(current_env)
    
    def get_current_environment(self):
        """Get the currently selected environment."""
        return self.current_environment
    
    def on_variable_changed(self, item):
        """Handle variable table item changes."""
        if not self.current_environment:
            return
        
        row = item.row()
        key_item = self.variables_table.item(row, 0)
        value_item = self.variables_table.item(row, 1)
        
        if key_item and value_item:
            key = key_item.text().strip()
            value = value_item.text().strip()
            
            if key:  # Only update if key is not empty
                self.current_environment.set_variable(key, value)
                self.environment_changed.emit(self.current_environment)
    
    def rename_environment(self):
        """Rename the current environment."""
        current_env = self.env_combo.currentData()
        if not current_env:
            QMessageBox.information(self, "Info", "Please select an environment first.")
            return
        
        new_name, ok = QInputDialog.getText(self, "Rename Environment", "New name:", text=current_env.name)
        if ok and new_name:
            current_env.name = new_name
            # Update the combo box
            current_index = self.env_combo.currentIndex()
            self.env_combo.setItemText(current_index, new_name)
            self.environment_changed.emit(current_env)
    
    def delete_environment(self):
        """Delete the current environment."""
        current_env = self.env_combo.currentData()
        if not current_env:
            QMessageBox.information(self, "Info", "Please select an environment first.")
            return
        
        reply = QMessageBox.question(
            self, "Delete Environment", 
            f"Are you sure you want to delete '{current_env.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from environments list
            if hasattr(self, 'environments') and current_env in self.environments:
                self.environments.remove(current_env)
            
            # Update the combo box
            current_index = self.env_combo.currentIndex()
            self.env_combo.removeItem(current_index)
            
            # Select first environment if available
            if self.env_combo.count() > 1:
                self.env_combo.setCurrentIndex(1)
            else:
                self.env_combo.setCurrentIndex(0)
            
            self.environment_changed.emit(None) 