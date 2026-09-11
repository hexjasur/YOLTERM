"""Visual constants and stylesheet fragments for the YOLTERM UI."""

from __future__ import annotations

from PySide6.QtGui import QFont

BACKGROUND = "#080817"
PANEL = "#10102a"
INPUT_BACKGROUND = "#111126"
TEXT = "#e8e6ff"
MUTED = "#786fbe"
CYAN = "#55e6ff"
BLUE = "#368dff"
PURPLE = "#9d5cff"
PINK = "#ff4fc4"

WINDOW_STYLE = f"""
QMainWindow {{ background: transparent; }}
#windowShell {{ background: {BACKGROUND}; border: 1px solid #6f47bd;
    border-radius: 10px; }}
#titleBar {{ background: {PANEL}; border-bottom: 1px solid #2c82c9;
    border-top-left-radius: 9px; border-top-right-radius: 9px; }}
#brandLabel {{ color: {CYAN}; letter-spacing: 1px; }}
#contentArea {{ background: {BACKGROUND}; }}
#statusLabel {{ color: {MUTED}; font: 9pt Consolas; padding: 2px 4px; }}
#welcomeLabel {{ color: #ba9dff; font: 10pt Consolas; padding: 2px 4px 8px; }}
QPushButton {{ color: #bcaeff; background: transparent; border: none;
    font: 13pt Consolas; }}
QPushButton:hover {{ color: {CYAN}; background: #24204b; border-radius: 4px; }}
#closeButton:hover {{ color: {PINK}; background: #4b183d; }}
"""

OUTPUT_STYLE = f"""
QPlainTextEdit {{ background-color: {BACKGROUND}; color: {TEXT};
    selection-background-color: #442b68; selection-color: #ffffff;
    border: 1px solid #5b2a86; border-radius: 6px; padding: 12px; }}
QScrollBar:vertical {{ background: #111126; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #7b3fb2; min-height: 28px; border-radius: 5px; }}
QScrollBar::handle:vertical:hover {{ background: #b44cff; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
"""

INPUT_STYLE = f"""
QLineEdit {{ background: {INPUT_BACKGROUND}; color: #ff8de1; border: 1px solid #7b3fb2;
    border-radius: 4px; padding: 6px 8px; selection-background-color: #5b2a86; }}
"""


def monospace_font(size: int = 11, bold: bool = False) -> QFont:
    """Return a safe monospace fallback stack for the current platform."""
    font = QFont()
    font.setFamilies(["JetBrains Mono", "Cascadia Code", "Cascadia Mono", "Consolas", "monospace"])
    font.setPointSize(size)
    font.setBold(bold)
    return font
