"""Terminal display and input widget."""

from __future__ import annotations

import os
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeyEvent, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

from .session import ShellSession


class TerminalWidget(QPlainTextEdit):
    """A deliberately small terminal-like text editor backed by a shell session."""

    _ANSI_ESCAPE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def __init__(self, parent: QPlainTextEdit | None = None) -> None:
        super().__init__(parent)
        self._session = ShellSession(self)
        self._history: list[str] = []
        self._history_index = 0
        self._prompt_start = 0
        self._prompt = self._default_prompt()

        self.setUndoRedoEnabled(False)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(QFont("Consolas", 11))
        self.setStyleSheet(
            "QPlainTextEdit { background-color: #080808; color: #f2f2f2; "
            "selection-background-color: #3d5a80; border: none; padding: 12px; }"
        )
        self.setCursorWidth(8)
        self._session.output_received.connect(self._append_output)
        self._session.error_received.connect(self._append_output)
        self._session.finished.connect(self._on_session_finished)
        self._session.start()
        self._append_prompt()

    def close_session(self) -> None:
        """Stop the child shell process."""
        self._session.stop()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle editing only within the current command input area."""
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._execute_current_input()
            return
        if key == Qt.Key.Key_L and modifiers & Qt.KeyboardModifier.ControlModifier:
            self.clear()
            self._append_prompt()
            return
        if key == Qt.Key.Key_C and modifiers & Qt.KeyboardModifier.ControlModifier:
            if not self.textCursor().hasSelection():
                self._session.interrupt()
                self._append_output("^C\n")
            else:
                self.copy()
            return
        if key == Qt.Key.Key_Up:
            self._history_move(-1)
            return
        if key == Qt.Key.Key_Down:
            self._history_move(1)
            return

        self._keep_cursor_in_input()
        if key == Qt.Key.Key_Backspace and self.textCursor().position() <= self._prompt_start:
            return
        if key == Qt.Key.Key_Left and self.textCursor().position() <= self._prompt_start:
            return
        if key == Qt.Key.Key_Home:
            self._move_cursor(self._prompt_start)
            return
        if key == Qt.Key.Key_End:
            self._move_cursor(len(self.toPlainText()))
            return
        super().keyPressEvent(event)
        self._keep_cursor_in_input()

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self._keep_cursor_in_input()

    def _execute_current_input(self) -> None:
        command = self.toPlainText()[self._prompt_start :].replace("\n", "").strip()
        self._move_cursor(len(self.toPlainText()))
        self.insertPlainText("\n")
        if command:
            self._history.append(command)
            self._history_index = len(self._history)
            self._session.send_command(command)
        else:
            self._append_prompt()

    def _append_output(self, text: str) -> None:
        cleaned = self._ANSI_ESCAPE.sub("", text).replace("\r", "")
        if not cleaned:
            return
        self._move_cursor(len(self.toPlainText()))
        self.insertPlainText(cleaned)
        self.ensureCursorVisible()
        if self._looks_like_prompt(cleaned):
            self._prompt_start = len(self.toPlainText())

    def _append_prompt(self) -> None:
        self._move_cursor(len(self.toPlainText()))
        if self.toPlainText() and not self.toPlainText().endswith("\n"):
            self.insertPlainText("\n")
        self.insertPlainText(self._prompt)
        self._prompt_start = len(self.toPlainText())
        self.ensureCursorVisible()

    def _history_move(self, direction: int) -> None:
        if not self._history:
            return
        self._history_index = max(0, min(len(self._history), self._history_index + direction))
        value = self._history[self._history_index] if self._history_index < len(self._history) else ""
        self._replace_input(value)

    def _replace_input(self, value: str) -> None:
        cursor = self.textCursor()
        cursor.setPosition(self._prompt_start)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(value)
        self.setTextCursor(cursor)

    def _move_cursor(self, position: int) -> None:
        cursor = self.textCursor()
        cursor.setPosition(position)
        self.setTextCursor(cursor)

    def _keep_cursor_in_input(self) -> None:
        if self.textCursor().position() < self._prompt_start:
            self._move_cursor(self._prompt_start)

    def _looks_like_prompt(self, text: str) -> bool:
        return text.endswith("> ") or text.endswith("$ ") or text.endswith("# ")

    def _on_session_finished(self) -> None:
        if self.toPlainText() and not self.toPlainText().endswith("\n"):
            self.insertPlainText("\n")
        self._append_output("Shell session ended.\n")

    @staticmethod
    def _default_prompt() -> str:
        return f"{os.getcwd()}> " if os.name == "nt" else f"{os.getcwd()} $ "
