"""Asynchronous shell process abstraction for the terminal UI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal


class ShellSession(QObject):
    """Manage an interactive shell while keeping its prompt invisible to YOLTERM."""

    output_received = Signal(str)
    error_received = Signal(str)
    prompt_received = Signal()
    finished = Signal()

    _PROMPT_MARKER = "__YOLTERM_PROMPT_7F3A__"

    def __init__(self, working_directory: Path | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.working_directory = (working_directory or Path.cwd()).resolve()
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.started.connect(self._configure_prompt)
        self._process.finished.connect(self._on_finished)
        self._output_buffer = ""
        self._shell_ready = False
        self._user_command_started = False
        self._pending_echo = ""
        self._awaiting_prompt = False

    @property
    def is_running(self) -> bool:
        return self._process.state() == QProcess.ProcessState.Running

    def start(self) -> None:
        if self.is_running:
            return
        self._output_buffer = ""
        self._shell_ready = False
        self._user_command_started = False
        self._pending_echo = ""
        self._awaiting_prompt = False
        if sys.platform == "win32":
            program = os.environ.get("COMSPEC", "cmd.exe")
            arguments = ["/Q", "/D"]
        else:
            program = os.environ.get("SHELL", "/bin/sh")
            arguments = ["-i"]
        self._process.setWorkingDirectory(str(self.working_directory))
        self._process.start(program, arguments)

    def send_command(self, command: str) -> None:
        """Send a user command to the shell without blocking the GUI."""
        if self.is_running:
            self._user_command_started = True
            self._pending_echo = command
            self._awaiting_prompt = True
            self._write(command)

    def sync_working_directory(self, working_directory: Path) -> None:
        self.working_directory = working_directory.resolve()
        if not self.is_running:
            return
        command = (
            f'cd /d "{self.working_directory}"'
            if sys.platform == "win32"
            else f'cd -- "{self.working_directory}"'
        )
        self._write(command)

    def interrupt(self) -> None:
        if self.is_running:
            self._process.write(b"\x03")

    def stop(self) -> None:
        if self._process.state() == QProcess.ProcessState.NotRunning:
            return
        self._process.terminate()
        if not self._process.waitForFinished(1500):
            self._process.kill()
            self._process.waitForFinished(1000)

    def _configure_prompt(self) -> None:
        command = (
            f"prompt {self._PROMPT_MARKER}"
            if sys.platform == "win32"
            else f"PS1='{self._PROMPT_MARKER}'"
        )
        self._write(command)

    def _write(self, command: str) -> None:
        self._process.write((command + "\n").encode())

    def _read_stdout(self) -> None:
        data = bytes(self._process.readAllStandardOutput()).decode(errors="replace")
        if data:
            self._consume_shell_data(data)

    def _read_stderr(self) -> None:
        data = bytes(self._process.readAllStandardError()).decode(errors="replace")
        if data:
            self._consume_shell_data(data)

    def _consume_shell_data(self, data: str) -> None:
        self._output_buffer += data
        marker = self._PROMPT_MARKER
        while marker in self._output_buffer:
            before, self._output_buffer = self._output_buffer.split(marker, 1)
            if self._shell_ready and before:
                self._emit_clean_output(before)
            if self._shell_ready and self._awaiting_prompt:
                self._awaiting_prompt = False
                self.prompt_received.emit()
            else:
                self._shell_ready = True
        if self._shell_ready and self._output_buffer:
            possible_prefix = 0
            for size in range(1, min(len(self._output_buffer), len(marker)) + 1):
                if marker.startswith(self._output_buffer[-size:]):
                    possible_prefix = size
            safe_length = len(self._output_buffer) - possible_prefix
            if safe_length:
                self._emit_clean_output(self._output_buffer[:safe_length])
                self._output_buffer = self._output_buffer[safe_length:]

    def _emit_clean_output(self, text: str) -> None:
        if not self._user_command_started:
            return
        if self._pending_echo:
            for prefix in (self._pending_echo + "\r\n", self._pending_echo + "\n"):
                if text.startswith(prefix):
                    text = text[len(prefix) :]
                    self._pending_echo = ""
                    break
        if text:
            self.output_received.emit(text)

    def _on_finished(self) -> None:
        if self._shell_ready and self._output_buffer:
            self._emit_clean_output(self._output_buffer)
        self.finished.emit()
