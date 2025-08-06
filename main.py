#!/usr/bin/env python3
"""
API Testing Desktop Application
A SendApi application for testing APIs with collections, environments, and scripts.
"""

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow


def main():
    """Main application entry point."""
    print("Starting API Tester application...")
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("API Tester")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("API Tester")

    # Set application style
    app.setStyle("Fusion")

    # Create and show the main window
    print("Creating main window...")
    window = MainWindow()
    window.show()
    print("Main window displayed successfully!")

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
