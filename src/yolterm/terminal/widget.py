"""Separated terminal output and command input widgets."""

from __future__ import annotations

import os
import re
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QFont, QKeyEvent, QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget

from ..commands import CommandKind, CommandRouter
from .session import ShellSession


class TerminalWidget(QWidget):
    """Terminal UI with immutable output and a dedicated editable input line."""

    command_started = Signal()
    _ANSI_ESCAPE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._router = CommandRouter()
        self._session = ShellSession(self._router.filesystem.current_directory, self)
        self._history: list[str] = []
        self._history_index = 0
        self._prompt = ""

        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output.setFont(self._terminal_font())
        self.output.setStyleSheet(
            "QPlainTextEdit { background-color: #080817; color: #e8e6ff; "
            "selection-background-color: #442b68; selection-color: #ffffff; "
            "border: 1px solid #5b2a86; border-radius: 6px; padding: 12px; "
            "} QScrollBar:vertical { background: #111126; width: 10px; margin: 2px; } "
            "QScrollBar::handle:vertical { background: #7b3fb2; min-height: 28px; "
            "border-radius: 5px; } QScrollBar::handle:vertical:hover { background: #b44cff; } "
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        self.output.setCursorWidth(0)

        self.prompt_label = QLabel(self)
        self.prompt_label.setFont(self.output.font())
        self.prompt_label.setStyleSheet("color: #55e6ff; padding: 0 4px 0 8px;")
        self.input_line = QLineEdit(self)
        self.input_line.setFont(self.output.font())
        self.input_line.setStyleSheet(
            "QLineEdit { background: #111126; color: #ff8de1; border: 1px solid #7b3fb2; "
            "border-radius: 4px; padding: 6px 8px; selection-background-color: #5b2a86; }"
        )
        self.input_line.installEventFilter(self)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 8, 0, 0)
        input_layout.setSpacing(4)
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.input_line, 1)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.output, 1)
        layout.addLayout(input_layout)

        self._session.output_received.connect(self._append_output)
        self._session.error_received.connect(self._append_output)
        self._session.prompt_received.connect(self._on_shell_prompt)
        self._session.finished.connect(self._on_session_finished)
        self._session.start()
        self._show_prompt()
        self.input_line.setFocus()

    def close_session(self) -> None:
        self._session.stop()

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if watched is self.input_line and event.type() == QEvent.Type.KeyPress:
            key_event = event  # type: ignore[assignment]
            if isinstance(key_event, QKeyEvent):
                if key_event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self._execute_current_input()
                    return True
                if key_event.key() == Qt.Key.Key_Up:
                    self._history_move(-1)
                    return True
                if key_event.key() == Qt.Key.Key_Down:
                    self._history_move(1)
                    return True
                if key_event.key() == Qt.Key.Key_L and key_event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.output.clear()
                    self._show_prompt()
                    return True
                if key_event.key() == Qt.Key.Key_C and key_event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    if self.input_line.hasSelectedText():
                        self.input_line.copy()
                    else:
                        self._session.interrupt()
                    return True
        return super().eventFilter(watched, event)

    def _execute_current_input(self) -> None:
        command = self.input_line.text().strip()
        if not command:
            self.input_line.clear()
            return
        if not self._history or self._history[-1] != command:
            self._history.append(command)
        self._history_index = len(self._history)
        self.command_started.emit()
        self._render_submitted_command(command)
        self.input_line.clear()
        routed = self._router.route(command)
        if routed.kind is CommandKind.NATIVE:
            output = self._router.execute_native(routed)
            if routed.name == "cd" and not output.startswith(("Usage:", "Directory not found:", "Unable")):
                self._session.sync_working_directory(self._router.filesystem.current_directory)
            self._append_output(output)
            self._show_prompt()
        else:
            self._session.send_command(command)
        self.input_line.setFocus()

    def _render_submitted_command(self, command: str) -> None:
        self._append_output(f"{self._prompt}{command}\n")

    def _append_output(self, text: str) -> None:
        cleaned = self._ANSI_ESCAPE.sub("", text).replace("\r", "")
        if not cleaned:
            return
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(cleaned)
        self._scroll_to_bottom()

    def _show_prompt(self) -> None:
        self._prompt = self._default_prompt()
        self.prompt_label.setText(self._prompt)

    def _on_shell_prompt(self) -> None:
        self._show_prompt()
        self.input_line.setFocus()

    def _history_move(self, direction: int) -> None:
        if not self._history:
            return
        self._history_index = max(0, min(len(self._history), self._history_index + direction))
        value = self._history[self._history_index] if self._history_index < len(self._history) else ""
        self.input_line.setText(value)
        self.input_line.setCursorPosition(len(value))

    def _scroll_to_bottom(self) -> None:
        self.output.ensureCursorVisible()
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_session_finished(self) -> None:
        self._append_output("\nShell session ended.\n")

    def _default_prompt(self) -> str:
        path = self._router.filesystem.current_directory
        display = str(path)
        if len(display) > 270:
            parts = list(path.parts)
            display = f"{path.anchor}…{Path(*parts[-2:])}"
        suffix = "> " if os.name == "nt" else " $ "
        return f"❯ {display}{suffix}"

    @staticmethod
    def _terminal_font() -> QFont:
        font = QFont()
        font.setFamilies(["JetBrains Mono", "Cascadia Code", "Cascadia Mono", "Consolas", "monospace"])
        font.setPointSize(11)
        return font
