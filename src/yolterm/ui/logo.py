"""Animated neon FIGlet YOLTERM logo."""

from __future__ import annotations

import pyfiglet
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import BLUE, CYAN, PINK, PURPLE, monospace_font


FIGLET_FONT = "doom"


def generate_logo_text(text: str = "YOLTERM", font: str = FIGLET_FONT) -> str:
    """Generate the logo text dynamically with a bundled FIGlet font."""
    return pyfiglet.figlet_format(text, font=font).rstrip("\n")


class NeonLogo(QWidget):
    """Render generated FIGlet text with a flowing gradient and subtle glow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._phase = 0.0
        self._logo_text = generate_logo_text()
        self.setMinimumHeight(112)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(50)

    @property
    def logo_text(self) -> str:
        """Return the generated FIGlet source text used by the painter."""
        return self._logo_text

    def _advance(self) -> None:
        self._phase = (self._phase + 0.012) % 1.0
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        lines = self._logo_text.splitlines()
        available_width = max(1, self.width() - 24)
        base_size = max(7, min(17, available_width // max(20, max(map(len, lines), default=1))))
        font = monospace_font(base_size, bold=True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        line_height = metrics.height()
        text_width = max((metrics.horizontalAdvance(line) for line in lines), default=0)
        x = max(12, (self.width() - text_width) // 2)
        y = max(metrics.ascent(), (self.height() - line_height * len(lines)) // 2 + metrics.ascent())

        gradient = QLinearGradient(-self.width() * self._phase, 0, self.width() * (1.0 - self._phase), 0)
        gradient.setColorAt(0.0, QColor(CYAN))
        gradient.setColorAt(0.25, QColor(BLUE))
        gradient.setColorAt(0.55, QColor(PURPLE))
        gradient.setColorAt(0.8, QColor(PINK))
        gradient.setColorAt(1.0, QColor(CYAN))

        # Draw a low-alpha offset halo first, then the crisp generated logo.
        glow_pen = QPen(gradient, 3)
        glow_color = QColor(CYAN)
        glow_color.setAlpha(45)
        glow_pen.setColor(glow_color)
        painter.setPen(glow_pen)
        for index, line in enumerate(lines):
            baseline = y + index * line_height
            painter.drawText(x - 1, baseline, line)
            painter.drawText(x + 1, baseline, line)

        painter.setPen(QPen(gradient, 1))
        for index, line in enumerate(lines):
            painter.drawText(x, y + index * line_height, line)
        painter.end()
