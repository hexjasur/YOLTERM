"""Overall branded YOLTERM window layout."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFrame, QLabel, QMainWindow, QSizeGrip, QVBoxLayout, QWidget

from .. import __version__
from ..terminal.widget import TerminalWidget
from .logo import NeonLogo
from .theme import WINDOW_STYLE
from .title_bar import TitleBar


class MainWindow(QMainWindow):
    """Custom-framed YOLTERM window containing the terminal interface."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YOLTERM")
        self.setMinimumSize(760, 520)
        self.resize(1120, 760)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shell = QFrame(self)
        shell.setObjectName("windowShell")
        outer = QVBoxLayout(shell)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)
        outer.addWidget(TitleBar(self))

        content = QWidget(shell)
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(22, 14, 22, 18)
        content_layout.setSpacing(4)
        status = QLabel(f"──── v{__version__} ─────────────── BUILDING A SMOOTHER JOURNEY ────")
        status.setObjectName("statusLabel")
        content_layout.addWidget(status)
        self._logo = NeonLogo(content)
        content_layout.addWidget(self._logo)
        self._welcome = QLabel(
            "Welcome to YOLTERM!\nType 'help' to get started.\nYour journey. Your terminal.\nReady."
        )
        self._welcome.setObjectName("welcomeLabel")
        content_layout.addWidget(self._welcome)
        self._terminal = TerminalWidget(content)
        self._terminal.command_started.connect(self._hide_welcome)
        content_layout.addWidget(self._terminal, 1)
        outer.addWidget(content, 1)

        self._grip = QSizeGrip(shell)
        self._grip.setFixedSize(16, 16)
        self._grip.setStyleSheet("QSizeGrip { background: transparent; }")
        self.setCentralWidget(shell)
        self.setStyleSheet(WINDOW_STYLE)

    @property
    def terminal(self) -> TerminalWidget:
        """Return the embedded terminal widget for lifecycle management."""
        return self._terminal

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        self._grip.move(self.centralWidget().width() - 18, self.centralWidget().height() - 18)

    def _hide_welcome(self) -> None:
        self._welcome.hide()
        self._logo.setMinimumHeight(92)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._terminal.close_session()
        event.accept()
