# YOLTERM

YOLTERM is a modern developer terminal for Windows, planned to combine terminal functionality, filesystem navigation, custom commands, Git/npm tooling, drag-and-drop folder navigation, and a custom user interface.

## Current status

The current foundation includes a stabilized command routing layer and native filesystem commands: `pwd`, `cd`, `ls`, `mkdir`, and `tree`. These commands use Python filesystem APIs and maintain YOLTERM's own explicit session directory, independent of the Python process working directory. Shell startup banners and prompts are hidden so YOLTERM controls the visible prompt. The terminal uses a minimal synthwave/neon color treatment while retaining the existing behavior. Other commands continue to run through the asynchronous shell session. On Windows the initial backend is `cmd.exe`; non-Windows development environments use an interactive system shell for testing. PowerShell integration, Git/npm tooling, and drag-and-drop are not implemented yet.

## Requirements

- Python 3.12 or newer
- Git

## Setup

Create a virtual environment from the project root:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project and its dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

## Run

With the virtual environment activated:

```bash
python -m yolterm
```

Type a shell command and press Enter. Native filesystem commands include `pwd`, `cd`, `ls`, `mkdir`, and `tree`; other commands are sent to the underlying shell. Basic history navigation, cursor editing, selection, copy/paste, Ctrl+C interruption, and Ctrl+L clearing are supported.

## Development

The application source is under `src/yolterm`, and tests are under `tests`. The project intentionally has no third-party dependencies beyond PySide6 at this stage.
