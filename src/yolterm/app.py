"""Application startup for YOLTERM."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def create_application() -> QApplication:
    """Create the Qt application instance."""
    application = QApplication.instance() or QApplication(sys.argv)
    application.setStyle("Fusion")
    return application


def run() -> int:
    """Start the application and return its exit status."""
    application = create_application()
    window = MainWindow()
    window.show()
    return application.exec()
