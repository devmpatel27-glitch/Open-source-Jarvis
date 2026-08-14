# Quick Start

## Current runtime summary

This repository is intended to track the real Open Code-based Open Source Jarvis runtime. The active voice assistant is a push-to-talk system named Doom, currently operating with:

- Whisper.cpp for STT
- Open Code CLI with `opencode/deepseek-v4-flash-free` for reasoning
- Kokoro FastAPI for TTS with voice `bm_daniel`
- A file-based signal bus shared across subsystems

## Requirements

- Python 3.10+
- A virtual environment
- Local access to the voice-line runtime dependencies
- The Whisper and Kokoro services running
- The Open Code CLI available on PATH

## Setup

```bash
cd voice-line
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If using the project metadata instead of requirements:

```bash
pip install -e .
```

## Startup commands

```bat
start servers\start-whisper.bat
start servers\start-kokoro.bat
run-voice-line.bat
```

## Visualizer launch

The visualizer runs as a fullscreen browser scene, typically on port `8777`, with a mock mode available at `8778` for scripted testing.

## Verification checklist

- Confirm Whisper responds successfully.
- Confirm Kokoro is responding on port `8880`.
- Confirm Open Code is healthy before use.
- Validate the signal bus and state transitions.
- Restart stale processes after editing any shared timing or state logic.

## Notes

- Use real runtime checks instead of synthetic success assumptions.
- Keep the repo documentation as the canonical source of current project memory.
- Prefer true end-to-end validation whenever changing voice or visual behavior.
