# YOLTERM

YOLTERM is a modern developer terminal for Windows, planned to combine terminal functionality, filesystem navigation, custom commands, Git/npm tooling, drag-and-drop folder navigation, and a custom user interface.

## Current status

This repository contains the initial Python desktop application foundation only. It currently opens a minimal PySide6 window titled **YOLTERM**. Terminal functionality and other product features have not been implemented yet.

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

## Development

The application source is under `src/yolterm`, and tests are under `tests`. The project intentionally has no third-party dependencies beyond PySide6 at this stage.
