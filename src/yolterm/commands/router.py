"""Route input between native YOLTERM commands and the shell."""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from enum import Enum

from .filesystem import FileSystemCommands


class CommandKind(Enum):
    NATIVE = "native"
    SHELL = "shell"
    EMPTY = "empty"


@dataclass(frozen=True)
class RoutedCommand:
    kind: CommandKind
    name: str = ""
    arguments: list[str] | None = None
    raw: str = ""


class CommandRouter:
    """Parse commands and execute only YOLTERM-owned filesystem commands."""

    NATIVE_COMMANDS = frozenset({"pwd", "cd", "ls", "mkdir", "tree"})

    def __init__(self, filesystem: FileSystemCommands | None = None) -> None:
        self.filesystem = filesystem or FileSystemCommands()

    def route(self, command: str) -> RoutedCommand:
        raw = command.strip()
        if not raw:
            return RoutedCommand(CommandKind.EMPTY, raw=raw)
        try:
            parts = shlex.split(raw, posix=False)
        except ValueError as error:
            return RoutedCommand(CommandKind.NATIVE, name="error", arguments=[str(error)], raw=raw)
        if not parts:
            return RoutedCommand(CommandKind.EMPTY, raw=raw)
        name = parts[0].lower()
        arguments = [self._strip_quotes(argument) for argument in parts[1:]]
        kind = CommandKind.NATIVE if name in self.NATIVE_COMMANDS else CommandKind.SHELL
        return RoutedCommand(kind, name=name, arguments=arguments, raw=raw)

    def execute_native(self, command: RoutedCommand) -> str:
        if command.kind is not CommandKind.NATIVE:
            return ""
        arguments = command.arguments or []
        if command.name == "error":
            return f"Invalid command syntax: {arguments[0]}\n"
        handler = getattr(self.filesystem, command.name)
        return handler(arguments)

    @staticmethod
    def _strip_quotes(argument: str) -> str:
        if len(argument) >= 2 and argument[0] == argument[-1] and argument[0] in {'"', "'"}:
            return argument[1:-1]
        return argument
