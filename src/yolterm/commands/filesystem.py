"""Native filesystem commands used by YOLTERM."""

from __future__ import annotations

import os
from pathlib import Path


class FileSystemCommands:
    """Execute filesystem commands against YOLTERM's current directory."""

    def pwd(self, arguments: list[str]) -> str:
        if arguments:
            return "Usage: pwd\n"
        return f"{Path.cwd()}\n"

    def cd(self, arguments: list[str]) -> str:
        if len(arguments) > 1:
            return "Usage: cd [directory]\n"
        target = Path.home() if not arguments else self._resolve(arguments[0])
        if not target.is_dir():
            requested = arguments[0] if arguments else str(target)
            return f"Directory not found: {requested}\n"
        try:
            os.chdir(target)
        except OSError as error:
            return f"Unable to change directory: {error}\n"
        return ""

    def ls(self, arguments: list[str]) -> str:
        if len(arguments) > 1:
            return "Usage: ls [directory]\n"
        target = Path.cwd() if not arguments else self._resolve(arguments[0])
        if not target.is_dir():
            requested = arguments[0] if arguments else str(target)
            return f"Directory not found: {requested}\n"
        try:
            entries = sorted(target.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.casefold()))
        except OSError as error:
            return f"Unable to list directory: {error}\n"
        if not entries:
            return "(empty)\n"
        return "\n".join(self._format_entry(entry) for entry in entries) + "\n"

    def mkdir(self, arguments: list[str]) -> str:
        if not arguments:
            return "Usage: mkdir <directory> [directory ...]\n"
        messages: list[str] = []
        for argument in arguments:
            target = self._resolve(argument)
            try:
                target.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                messages.append(f"Directory already exists: {argument}")
            except OSError as error:
                messages.append(f"Unable to create directory {argument}: {error}")
        return "\n".join(messages) + ("\n" if messages else "")

    def tree(self, arguments: list[str]) -> str:
        if len(arguments) > 1:
            return "Usage: tree [directory]\n"
        target = Path.cwd() if not arguments else self._resolve(arguments[0])
        if not target.is_dir():
            requested = arguments[0] if arguments else str(target)
            return f"Directory not found: {requested}\n"
        lines = [f"📁 {target.name or target}"]
        self._append_tree(target, lines, "")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _format_entry(entry: Path) -> str:
        return f"{'📁' if entry.is_dir() else '📄'} {entry.name}"

    def _append_tree(self, directory: Path, lines: list[str], prefix: str) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.casefold()))
        except OSError:
            return
        for index, entry in enumerate(entries):
            branch = "└── " if index == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{branch}{self._format_entry(entry)}")
            if entry.is_dir():
                child_prefix = prefix + ("    " if index == len(entries) - 1 else "│   ")
                self._append_tree(entry, lines, child_prefix)

    @staticmethod
    def _resolve(argument: str) -> Path:
        return Path(argument).expanduser().resolve()
