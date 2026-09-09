# Project Memory Runbook

This is the operational history for the working Open Source Jarvis voice and visualizer systems.

## Voice-line

- Identity: Doom
- Input: hold `Alt` to speak, release to send
- STT: Whisper.cpp on port `2022`, CUDA build, `ggml-small.en.bin`
- Brain: Open Code CLI `1.18.16` with `opencode/deepseek-v4-flash-free`
- TTS: Kokoro FastAPI on port `8880`, voice `bm_daniel`
- IPC: file-based signal bus in the voice-line directory

### Key fixes

- Replaced a silently failing `pynput` hook with `GetAsyncKeyState` polling at a 5ms interval.
- Corrected stale timestamp comparisons to use epoch time (`Date.now() / 1000`) rather than `performance.now() / 1000`.
- Scoped Open Code message IDs to the active turn to prevent cross-turn leakage.
- Marked the runtime idle in a `finally` path after warmup and failures.
- Changed the default model from the unavailable Claude configuration to `opencode/deepseek-v4-flash-free`.

### Startup commands

```bat
start servers\start-whisper.bat
start servers\start-kokoro.bat
run-voice-line.bat
```

## Visualizer

- Fullscreen browser canvas scene with a Doctor Doom-inspired metallic mask.
- States: `idle`, `listening`, `thinking`, `speaking`, and `alert`.
- Live port: `8777`; mock port: `8778`.
- Python standard-library server bridge reads the shared bus.
- `F` toggles telemetry; `G` cycles efficiency, balanced, and performance tiers.

### Verification hooks

- `?shot=idle&t=2000` freezes a deterministic state for screenshots.
- `?mockstate=speaking` simulates a state without writing the live bus.
- `--mock` runs a scripted state loop on port `8778`.
- Use headless Chrome and PIL pixel analysis for repeatable visual checks.

## Shared lessons

- Verify hook-based input in the target environment before relying on it.
- Never compare timestamps from different clocks.
- Treat stale state files as idle rather than trusting old waveforms.
- Restart processes after edits so stale instances cannot hide behavior changes.
- Test real end-to-end audio and visual flows, not only synthetic helpers.

## Memory integration

Obsidian notes are indexed locally through [OBSIDIAN-INTEGRATION.md](OBSIDIAN-INTEGRATION.md). The adapter preserves title, relative path, frontmatter, and a bounded snippet so retrieved context remains auditable before it reaches Open Code.
