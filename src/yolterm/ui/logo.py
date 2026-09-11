"""Animated neon ASCII YOLTERM logo."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import BLUE, CYAN, PINK, PURPLE, monospace_font


class NeonLogo(QWidget):
    """Render a stable-position ASCII logo with a lightweight flowing gradient."""

    _LINES = (
        "Y   Y  OOO  L      TTTTT  EEEEE  RRR   M   M",
        " Y Y  O   O L        T    E      R  R  MM MM",
        "  Y   O   O L        T    EEEE   RRR   M M M",
        "  Y   O   O L        T    E      R R   M   M",
        "  Y    OOO  LLLLL    T    EEEEE  R  R  M   M",
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._phase = 0.0
        self.setMinimumHeight(96)
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
        size = max(9, min(17, self.width() // 62))
        font = monospace_font(size, bold=True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        logo_width = metrics.horizontalAdvance(self._LINES[0])
        x = max(8, (self.width() - logo_width) // 2)
        line_height = metrics.height()
        y = max(metrics.ascent(), (self.height() - line_height * len(self._LINES)) // 2 + metrics.ascent())

        gradient = QLinearGradient(-self.width() * self._phase, 0, self.width() * (1.0 - self._phase), 0)
        gradient.setColorAt(0.0, QColor(CYAN))
        gradient.setColorAt(0.25, QColor(BLUE))
        gradient.setColorAt(0.55, QColor(PURPLE))
        gradient.setColorAt(0.8, QColor(PINK))
        gradient.setColorAt(1.0, QColor(CYAN))
        painter.setPen(QPen(gradient, 1))
        for index, line in enumerate(self._LINES):
            painter.drawText(x, y + index * line_height, line)
        painter.end()
