"""Custom title bar for the frameless YOLTERM window."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class TitleBar(QFrame):
    """Custom draggable title bar with synthwave window controls."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window
        self._drag_offset = QPoint()
        self.setFixedHeight(42)
        self.setObjectName("titleBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(0)
        brand = QLabel("YOLTERM  //  NEON TERMINAL", self)
        brand.setObjectName("brandLabel")
        brand.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        layout.addWidget(brand, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(2)
        for text, slot, name in (
            ("−", window.showMinimized, "minimizeButton"),
            ("□", self._toggle_maximize, "maximizeButton"),
            ("×", window.close, "closeButton"),
        ):
            button = QPushButton(text, self)
            button.setObjectName(name)
            button.setFixedSize(34, 28)
            button.clicked.connect(slot)
            controls.addWidget(button)
        controls_widget = QWidget(self)
        controls_widget.setLayout(controls)
        layout.addWidget(controls_widget, 0, alignment=Qt.AlignmentFlag.AlignVCenter)

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
