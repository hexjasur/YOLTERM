"""Native filesystem commands used by YOLTERM."""

from __future__ import annotations

from pathlib import Path


class FileSystemCommands:
    """Execute filesystem commands against an explicit YOLTERM directory."""

    def __init__(self, current_directory: Path | None = None) -> None:
        self.current_directory = (current_directory or Path.cwd()).expanduser().resolve()

    def pwd(self, arguments: list[str]) -> str:
        if arguments:
            return "Usage: pwd\n"
        return f"{self.current_directory}\n"

    def cd(self, arguments: list[str]) -> str:
        if len(arguments) > 1:
            return "Usage: cd [directory]\n"
        target = Path.home().resolve() if not arguments else self._resolve(arguments[0])
        if not target.is_dir():
            requested = arguments[0] if arguments else str(target)
            return f"Directory not found: {requested}\n"
        self.current_directory = target
        return ""

    def ls(self, arguments: list[str]) -> str:
        if len(arguments) > 1:
            return "Usage: ls [directory]\n"
        target = self.current_directory if not arguments else self._resolve(arguments[0])
        if not target.is_dir():
            requested = arguments[0] if arguments else str(target)
            return f"Directory not found: {requested}\n"
        try:
            entries = sorted(
                target.iterdir(),
                key=lambda entry: (not entry.is_dir(), entry.name.casefold()),
            )
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
        target = self.current_directory if not arguments else self._resolve(arguments[0])
        if not target.is_dir():
            requested = arguments[0] if arguments else str(target)
            return f"Directory not found: {requested}\n"
        lines = [target.name or str(target)]
        self._append_tree(target, lines, "", depth=0)
        return "\n".join(lines) + "\n"

    @staticmethod
    def _format_entry(entry: Path) -> str:
        return f"{'📁' if entry.is_dir() else '📄'} {entry.name}"

    def _append_tree(self, directory: Path, lines: list[str], prefix: str, depth: int) -> None:
        if depth >= 8:
            lines.append(f"{prefix}└── … (maximum depth reached)")
            return
        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda entry: (not entry.is_dir(), entry.name.casefold()),
            )
        except OSError:
            return
        for index, entry in enumerate(entries):
            branch = "└── " if index == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{branch}{self._format_entry(entry)}")
            if entry.is_dir() and not entry.is_symlink():
                child_prefix = prefix + ("    " if index == len(entries) - 1 else "│   ")
                self._append_tree(entry, lines, child_prefix, depth + 1)

    def _resolve(self, argument: str) -> Path:
        path = Path(argument).expanduser()
        if not path.is_absolute():
            path = self.current_directory / path
        return path.resolve()
