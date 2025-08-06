"""
Sidebar component for the API Testing Application
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .models import Collection, Environment, Request


class Sidebar(QWidget):
    """Sidebar widget containing collections and environments."""

    request_selected = Signal(Request)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.collections = []
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Collections section label
        collections_label = QLabel("Collections")
        collections_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px; background-color: #ecf0f1; border-radius: 3px;"
        )
        layout.addWidget(collections_label)

        # Collections widget
        self.collections_widget = self.create_collections_widget()
        layout.addWidget(self.collections_widget)

    def create_collections_widget(self):
        """Create the collections widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Collections tree
        self.collections_tree = QTreeWidget()
        self.collections_tree.setHeaderLabel("Collections")
        self.collections_tree.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.collections_tree.customContextMenuRequested.connect(
            self.show_collection_context_menu
        )
        self.collections_tree.itemClicked.connect(self.on_collection_item_clicked)
        layout.addWidget(self.collections_tree)

        # Buttons
        button_layout = QHBoxLayout()

        self.new_request_btn = QPushButton("New Request")
        self.new_request_btn.clicked.connect(self.new_request)
        button_layout.addWidget(self.new_request_btn)

        layout.addLayout(button_layout)

        return widget

    def update_collections(self, collections):
        """Update the collections tree."""
        self.collections = collections
        self.collections_tree.clear()

        for collection in collections:
            collection_item = QTreeWidgetItem(self.collections_tree)
            collection_item.setText(0, collection.name)
            collection_item.setData(0, Qt.ItemDataRole.UserRole, collection)

            # Add requests
            for request in collection.requests:
                request_item = QTreeWidgetItem(collection_item)
                request_item.setText(0, f"{request.method} {request.name}")
                request_item.setData(0, Qt.ItemDataRole.UserRole, request)

            # Add folders
            for folder in collection.folders:
                folder_item = QTreeWidgetItem(collection_item)
                folder_item.setText(0, f"📁 {folder.name}")
                folder_item.setData(0, Qt.ItemDataRole.UserRole, folder)

                # Add requests in folders
                for request in folder.requests:
                    request_item = QTreeWidgetItem(folder_item)
                    request_item.setText(0, f"{request.method} {request.name}")
                    request_item.setData(0, Qt.ItemDataRole.UserRole, request)

                # Add sub-folders (recursive)
                self._add_folders_recursive(folder_item, folder.folders)

        self.collections_tree.expandAll()

    def _add_folders_recursive(self, parent_item, folders):
        """Recursively add folders to the tree."""
        for folder in folders:
            folder_item = QTreeWidgetItem(parent_item)
            folder_item.setText(0, f"📁 {folder.name}")
            folder_item.setData(0, Qt.ItemDataRole.UserRole, folder)

            # Add requests in folders
            for request in folder.requests:
                request_item = QTreeWidgetItem(folder_item)
                request_item.setText(0, f"{request.method} {request.name}")
                request_item.setData(0, Qt.ItemDataRole.UserRole, request)

            # Add sub-folders (recursive)
            self._add_folders_recursive(folder_item, folder.folders)

    def show_collection_context_menu(self, position):
        """Show context menu for collections."""
        item = self.collections_tree.itemAt(position)
        if not item:
            return

        context_menu = QMenu()

        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, Collection):
            # Collection context menu
            add_request_action = context_menu.addAction("Add Request")
            add_request_action.triggered.connect(
                lambda: self.add_request_to_collection(data)
            )

            add_folder_action = context_menu.addAction("Add Folder")
            add_folder_action.triggered.connect(
                lambda: self.add_folder_to_collection(data)
            )

            context_menu.addSeparator()

            run_all_action = context_menu.addAction("Run All Requests")
            run_all_action.triggered.connect(lambda: self.run_all_requests(data))

            create_tests_action = context_menu.addAction("Create Tests")
            create_tests_action.triggered.connect(
                lambda: self.create_tests_for_collection(data)
            )

            context_menu.addSeparator()

            export_action = context_menu.addAction("Export")
            export_action.triggered.connect(lambda: self.export_collection(data))

            duplicate_action = context_menu.addAction("Duplicate")
            duplicate_action.triggered.connect(lambda: self.duplicate_collection(data))

            context_menu.addSeparator()

            rename_action = context_menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self.rename_collection(data))

            delete_action = context_menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_collection(data))

        elif isinstance(data, Request):
            # Request context menu
            create_tests_action = context_menu.addAction("Create Tests")
            create_tests_action.triggered.connect(
                lambda: self.create_tests_for_request(data)
            )

            context_menu.addSeparator()

            export_action = context_menu.addAction("Export as cURL")
            export_action.triggered.connect(lambda: self.export_request_as_curl(data))

            context_menu.addSeparator()

            rename_action = context_menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self.rename_request(data))

            duplicate_action = context_menu.addAction("Duplicate")
            duplicate_action.triggered.connect(lambda: self.duplicate_request(data))

            context_menu.addSeparator()

            delete_action = context_menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_request(data))

        context_menu.exec(self.collections_tree.mapToGlobal(position))

    def on_collection_item_clicked(self, item, column):
        """Handle collection item click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, Request):
            print(f"Sidebar: Request selected: {data.name}")
            self.request_selected.emit(data)

    def new_request(self):
        """Create a new request."""
        if not self.collections:
            QMessageBox.information(self, "Info", "Please create a collection first.")
            return

        # For now, add to first collection
        collection = self.collections[0]
        self.add_request_to_collection(collection)

    def add_request_to_collection(self, collection):
        """Add a new request to a collection."""
        name, ok = QInputDialog.getText(self, "New Request", "Request name:")
        if ok and name:
            request = Request(name=name)
            collection.add_request(request)
            self.update_collections(self.collections)
            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

    def add_folder_to_collection(self, collection):
        """Add a new folder to a collection."""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            folder = Collection(name=name)
            collection.folders.append(folder)
            self.update_collections(self.collections)
            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

    def rename_collection(self, collection):
        """Rename a collection."""
        new_name, ok = QInputDialog.getText(
            self, "Rename Collection", "New name:", text=collection.name
        )
        if ok and new_name:
            collection.name = new_name
            self.update_collections(self.collections)
            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

    def delete_collection(self, collection):
        """Delete a collection."""
        reply = QMessageBox.question(
            self,
            "Delete Collection",
            f"Are you sure you want to delete '{collection.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.collections.remove(collection)
            self.update_collections(self.collections)
            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

    def rename_request(self, request):
        """Rename a request."""
        new_name, ok = QInputDialog.getText(
            self, "Rename Request", "New name:", text=request.name
        )
        if ok and new_name:
            request.name = new_name
            self.update_collections(self.collections)
            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

    def export_collection(self, collection):
        """Export a collection to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Collection", f"{collection.name}.json", "JSON Files (*.json)"
        )
        if file_path:
            try:
                import json

                with open(file_path, "w") as f:
                    json.dump(collection.to_dict(), f, indent=2)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Collection '{collection.name}' exported successfully!",
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export collection: {e}")

    def export_request_as_curl(self, request):
        """Export a request as cURL command."""
        try:
            # Find parent with _generate_curl_command method
            parent = self.parent()
            while parent and not hasattr(parent, "_generate_curl_command"):
                parent = parent.parent()

            if parent and hasattr(parent, "_generate_curl_command"):
                curl_command = parent._generate_curl_command(request)

                # Ask user for file path
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save cURL Command",
                    f"{request.name}.sh",
                    "Shell Scripts (*.sh);;Text Files (*.txt);;All Files (*)",
                )

                if file_path:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(curl_command)
                    QMessageBox.information(
                        self, "Success", f"cURL command saved to {file_path}"
                    )
            else:
                QMessageBox.warning(self, "Error", "Export functionality not available")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export cURL command: {e}")

    def duplicate_collection(self, collection):
        """Duplicate a collection."""
        try:
            # Create a deep copy of the collection
            from copy import deepcopy

            duplicated_collection = deepcopy(collection)
            duplicated_collection.name = f"{collection.name} (Copy)"
            duplicated_collection.id = (
                f"{collection.id}_copy" if collection.id else f"{collection.name}_copy"
            )

            # Add to collections list
            self.collections.append(duplicated_collection)

            # Update UI
            self.update_collections(self.collections)

            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

            QMessageBox.information(
                self,
                "Success",
                f"Collection '{collection.name}' duplicated successfully!",
            )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to duplicate collection: {e}")

    def run_all_requests(self, collection):
        """Run all requests in a collection or folder."""
        print(f"Sidebar: run_all_requests called for collection: {collection.name}")

        # Get all requests from the collection (including nested folders)
        all_requests = self._get_all_requests_from_collection(collection)
        print(f"Sidebar: Found {len(all_requests)} requests in collection")

        if not all_requests:
            QMessageBox.information(
                self, "Info", "No requests found in this collection."
            )
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Run All Requests",
            f"Run all {len(all_requests)} requests in '{collection.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            print(f"Sidebar: User confirmed running {len(all_requests)} requests")
            # Notify parent to run all requests
            parent = self.parent()
            while parent and not hasattr(parent, "run_all_requests"):
                parent = parent.parent()

            if parent and hasattr(parent, "run_all_requests"):
                print(f"Sidebar: Calling parent.run_all_requests")
                parent.run_all_requests(all_requests)
            else:
                print(
                    f"Sidebar: Could not find run_all_requests method in parent hierarchy"
                )
                QMessageBox.warning(
                    self, "Error", "Could not start batch testing. Please try again."
                )
        else:
            print(f"Sidebar: User cancelled batch run")

    def _get_all_requests_from_collection(self, collection):
        """Get all requests from a collection, including nested folders."""
        requests = []

        # Add direct requests
        print(
            f"Sidebar: Collection '{collection.name}' has {len(collection.requests)} direct requests"
        )
        requests.extend(collection.requests)

        # Add requests from nested folders
        print(
            f"Sidebar: Collection '{collection.name}' has {len(collection.folders)} folders"
        )
        for folder in collection.folders:
            folder_requests = self._get_all_requests_from_collection(folder)
            print(
                f"Sidebar: Folder '{folder.name}' has {len(folder_requests)} requests"
            )
            requests.extend(folder_requests)

        print(f"Sidebar: Total requests found: {len(requests)}")
        return requests

    def duplicate_request(self, request):
        """Duplicate a request."""
        new_request = Request(
            name=f"{request.name} (Copy)",
            method=request.method,
            url=request.url,
            headers=request.headers.copy(),
            params=request.params.copy(),
            body=request.body,
            body_type=request.body_type,
            pre_request_script=request.pre_request_script,
            tests=request.tests,
            description=request.description,
        )

        # Add to the same collection
        for collection in self.collections:
            for req in collection.requests:
                if req.id == request.id:
                    collection.add_request(new_request)
                    self.update_collections(self.collections)
                    return

    def delete_request(self, request):
        """Delete a request."""
        reply = QMessageBox.question(
            self,
            "Delete Request",
            f"Are you sure you want to delete '{request.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for collection in self.collections:
                collection.remove_request(request.id)
            self.update_collections(self.collections)
            # Notify parent to save data
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

    def create_tests_for_request(self, request):
        """Create standard tests for a single request."""
        if self._has_standard_tests(request.tests):
            QMessageBox.information(
                self, "Info", f"Standard tests already exist in '{request.name}'"
            )
            return

        standard_tests = self._generate_standard_tests()

        # Add tests to the request
        if request.tests:
            request.tests += "\n\n" + standard_tests
        else:
            request.tests = standard_tests

        # Update UI and save
        self.update_collections(self.collections)
        if hasattr(self.parent(), "save_data"):
            self.parent().save_data()

        QMessageBox.information(
            self, "Success", f"Standard tests added to '{request.name}'"
        )

    def create_tests_for_collection(self, collection):
        """Create standard tests for all requests in a collection or folder."""
        # Get all requests from the collection (including nested folders)
        all_requests = self._get_all_requests_from_collection(collection)

        if not all_requests:
            QMessageBox.information(
                self, "Info", "No requests found in this collection."
            )
            return

        # Check which requests need tests
        requests_needing_tests = [
            req for req in all_requests if not self._has_standard_tests(req.tests)
        ]

        if not requests_needing_tests:
            QMessageBox.information(
                self,
                "Info",
                f"All requests in '{collection.name}' already have standard tests.",
            )
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Create Tests",
            f"Add standard tests to {len(requests_needing_tests)} out of {len(all_requests)} requests in '{collection.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            standard_tests = self._generate_standard_tests()
            updated_count = 0

            for request in requests_needing_tests:
                # Add tests to the request
                if request.tests:
                    request.tests += "\n\n" + standard_tests
                else:
                    request.tests = standard_tests
                updated_count += 1

            # Update UI and save
            self.update_collections(self.collections)
            if hasattr(self.parent(), "save_data"):
                self.parent().save_data()

            QMessageBox.information(
                self,
                "Success",
                f"Standard tests added to {updated_count} requests in '{collection.name}'",
            )

    def _has_standard_tests(self, tests_script):
        """Check if standard tests already exist in the test script."""
        if not tests_script:
            return False

        # Check for the presence of all standard test patterns
        standard_patterns = [
            'pm.test("Status code is 200"',
            'pm.test("Response time is less than 1000ms"',
            'pm.test("Content-Type is present"',
            'pm.test("Status code name has string OK"',
        ]

        # All patterns must be present for it to be considered as having standard tests
        return all(pattern in tests_script for pattern in standard_patterns)

    def _generate_standard_tests(self):
        """Generate standard Postman tests."""
        return """pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is less than 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

pm.test("Content-Type is present", function () {
    pm.response.to.have.header("Content-Type");
});

pm.test("Status code name has string OK", function () {
    pm.response.to.have.status("OK");
});"""
