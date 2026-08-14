# Voice Line

Real-time voice assistant subsystem for Open Source Jarvis.

## Purpose

This project handles voice capture, wake-word or push-to-talk input, command routing, and AI orchestration.

## Typical structure

- `main.py` — orchestration entry point
- `ptt.py` — push-to-talk input logic
- `pyproject.toml` — project configuration and dependencies

## Getting started

```bash
cd voice-line
python -m venv .venv
source .venv/bin/activate
pip install -e .
python main.py
```
