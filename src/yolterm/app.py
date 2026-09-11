"""Application startup and main window implementation for YOLTERM."""

from __future__ import annotations

import sys

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from .terminal.widget import TerminalWidget


class MainWindow(QMainWindow):
    """Main YOLTERM window containing the terminal interface."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YOLTERM")
        self.resize(1100, 700)
        self._terminal = TerminalWidget(self)
        self.setCentralWidget(self._terminal)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Stop the child shell before the window closes."""
        self._terminal.close_session()
        event.accept()


def create_application() -> QApplication:
    """Create the Qt application instance."""
    return QApplication.instance() or QApplication(sys.argv)


def run() -> int:
    """Start the application and return its exit status."""
    application = create_application()
    window = MainWindow()
    window.show()
    return application.exec()
