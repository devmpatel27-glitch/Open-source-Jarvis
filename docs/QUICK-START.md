# Quick Start

## Requirements

- Python 3.10+
- A virtual environment
- Required runtime packages from the `voice-line` project

## Setup

```bash
cd voice-line
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If your project uses `pyproject.toml`, install with:

```bash
pip install -e .
```

## Run the project

```bash
python main.py
```

## Notes

- Keep project-specific files inside their own subfolders.
- Add logs, env files, and local-generated artifacts to `.gitignore`.
- Use the docs index for additional setup guidance.
