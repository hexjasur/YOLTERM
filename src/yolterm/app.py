"""Application startup and main window implementation for YOLTERM."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    """Main application window placeholder for the initial foundation."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YOLTERM")
        self.resize(1100, 700)


def create_application() -> QApplication:
    """Create the Qt application instance."""
    return QApplication.instance() or QApplication(sys.argv)


def run() -> int:
    """Start the application and return its exit status."""
    application = create_application()
    window = MainWindow()
    window.show()
    return application.exec()
