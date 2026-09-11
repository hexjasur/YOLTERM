"""Asynchronous shell process abstraction for the terminal UI."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import QObject, QProcess, Signal


class ShellSession(QObject):
    """Manage an interactive cmd.exe session without blocking the GUI."""

    output_received = Signal(str)
    error_received = Signal(str)
    finished = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.finished.connect(self._on_finished)

    @property
    def is_running(self) -> bool:
        """Return whether the shell process is currently running."""
        return self._process.state() == QProcess.ProcessState.Running

    def start(self) -> None:
        """Start the platform's initial command shell."""
        if self.is_running:
            return

        if sys.platform == "win32":
            program = os.environ.get("COMSPEC", "cmd.exe")
            arguments = ["/Q"]
        else:
            # This fallback makes the UI testable on development machines that are
            # not Windows; the product shell backend remains cmd.exe on Windows.
            program = os.environ.get("SHELL", "/bin/sh")
            arguments = ["-i"]

        self._process.start(program, arguments)

    def send_command(self, command: str) -> None:
        """Send a command followed by a newline to the running shell."""
        if self.is_running:
            self._process.write((command + "\n").encode())

    def interrupt(self) -> None:
        """Request an interrupt from the active shell session."""
        if self.is_running:
            self._process.write(b"\x03")

    def stop(self) -> None:
        """Terminate the child shell cleanly when the application closes."""
        if not self.is_running:
            return
        self._process.terminate()
        if not self._process.waitForFinished(1500):
            self._process.kill()
            self._process.waitForFinished(1000)

    def _read_stdout(self) -> None:
        data = bytes(self._process.readAllStandardOutput()).decode(errors="replace")
        if data:
            self.output_received.emit(data)

    def _read_stderr(self) -> None:
        data = bytes(self._process.readAllStandardError()).decode(errors="replace")
        if data:
            self.error_received.emit(data)

    def _on_finished(self) -> None:
        self.finished.emit()

