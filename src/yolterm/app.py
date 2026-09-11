"""Application startup and branded synthwave window for YOLTERM."""

from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QColor, QCloseEvent, QFont, QLinearGradient, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizeGrip,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .terminal.widget import TerminalWidget


class NeonLogo(QWidget):
    """Static-position ASCII logo with a lightweight animated gradient."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._phase = 0.0
        self._logo = "Y   Y  OOO  L      TTTTT  EEEEE  RRR   M   M\n Y Y  O   O L        T    E      R  R  MM MM\n  Y   O   O L        T    EEEE   RRR   M M M\n  Y   O   O L        T    E      R R   M   M\n  Y    OOO  LLLLL    T    EEEEE  R  R  M   M"
        self.setMinimumHeight(118)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(50)

    def _advance(self) -> None:
        self._phase = (self._phase + 0.012) % 1.0
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont("Consolas", 17, QFont.Weight.Bold)
        painter.setFont(font)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        colors = [QColor("#4df6ff"), QColor("#368dff"), QColor("#9d5cff"), QColor("#ff4fc4"), QColor("#4df6ff")]
        for index, color in enumerate(colors):
            gradient.setColorAt((index / 4.0 + self._phase) % 1.0, color)
        pen = QPen(gradient, 1)
        painter.setPen(pen)
        metrics = painter.fontMetrics()
        x = max(12, (self.width() - metrics.horizontalAdvance("Y   Y  OOO  L      TTTTT  EEEEE  RRR   M   M")) // 2)
        y = (self.height() - metrics.height() * 5) // 2 + metrics.ascent()
        for index, line in enumerate(self._logo.splitlines()):
            painter.drawText(x, y + index * metrics.height(), line)
        painter.end()


class TitleBar(QFrame):
    """Custom draggable title bar with synthwave window controls."""

    def __init__(self, window: QMainWindow) -> None:
        super().__init__(window)
        self._window = window
        self._drag_offset = QPoint()
        self.setFixedHeight(42)
        self.setObjectName("titleBar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(0)
        brand = QLabel("YOLTERM  //  NEON TERMINAL", self)
        brand.setObjectName("brandLabel")
        brand.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        layout.addWidget(brand, alignment=Qt.AlignmentFlag.AlignVCenter)
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        for text, slot, name in (("−", window.showMinimized, "minimizeButton"), ("□", self._toggle_maximize, "maximizeButton"), ("×", window.close, "closeButton")):
            button = QPushButton(text, self)
            button.setObjectName(name)
            button.setFixedSize(34, 28)
            button.clicked.connect(slot)
            controls.addWidget(button)
        # Put controls on the right using a separate child widget.
        controls_widget = QWidget(self)
        controls_widget.setLayout(controls)
        controls_widget.move(self.width() - 110, 7)
        controls_widget.resize(106, 28)
        self._controls_widget = controls_widget

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        self._controls_widget.move(self.width() - 110, 7)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and not self._window.isMaximized():
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def _toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()


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
        self._title_bar = TitleBar(self)
        outer.addWidget(self._title_bar)

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
        self._welcome = QLabel("Welcome to YOLTERM!\nType 'help' to get started.\nYour journey. Your terminal.\nReady.")
        self._welcome.setObjectName("welcomeLabel")
        content_layout.addWidget(self._welcome)
        self._terminal = TerminalWidget(content)
        self._terminal.command_started.connect(self._hide_welcome)
        content_layout.addWidget(self._terminal, 1)
        outer.addWidget(content, 1)

        grip = QSizeGrip(shell)
        grip.setFixedSize(16, 16)
        grip.setStyleSheet("QSizeGrip { background: transparent; }")
        grip.move(self.width() - 18, self.height() - 18)
        self._grip = grip
        self.setCentralWidget(shell)
        self.setStyleSheet(
            "QMainWindow { background: transparent; } #windowShell { background: #080817; "
            "border: 1px solid #6f47bd; border-radius: 10px; } #titleBar { background: #10102a; "
            "border-bottom: 1px solid #2c82c9; border-top-left-radius: 9px; border-top-right-radius: 9px; } "
            "#brandLabel { color: #55e6ff; letter-spacing: 1px; } #contentArea { background: #080817; } "
            "#statusLabel { color: #786fbe; font: 9pt Consolas; padding: 2px 4px; } "
            "#welcomeLabel { color: #ba9dff; font: 10pt Consolas; line-height: 1.4; padding: 2px 4px 8px; } "
            "QPushButton { color: #bcaeff; background: transparent; border: none; font: 13pt Consolas; } "
            "QPushButton:hover { color: #55e6ff; background: #24204b; border-radius: 4px; } "
            "#closeButton:hover { color: #ff65bb; background: #4b183d; }"
        )

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        self._grip.move(self.centralWidget().width() - 18, self.centralWidget().height() - 18)

    def _hide_welcome(self) -> None:
        self._welcome.hide()
        self._logo.setMinimumHeight(92)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._terminal.close_session()
        event.accept()


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
