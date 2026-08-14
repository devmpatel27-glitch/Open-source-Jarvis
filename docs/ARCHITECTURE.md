# Open Source Jarvis Architecture

## Overview

Open Source Jarvis is structured as a modular assistant ecosystem composed of a voice subsystem, a visualizer, and a shared agent domain layer. The project is designed to preserve a single source of truth for project memory, runtime health, and operational lessons.

## Voice line runtime

### Components

- STT: Whisper.cpp
- Brain: Open Code CLI using `opencode/deepseek-v4-flash-free`
- TTS: Kokoro FastAPI on port `8880`
- Input: push-to-talk via `Alt` key polling
- Bus: file-based state and signal sharing

### Operational notes

- `Doom` is the runtime identity for the voice assistant.
- The assistant responds with spoken output after the user releases the push-to-talk trigger.
- Real runtime verification is required to confirm STT, brain, and TTS integration is working end-to-end.

## Visualizer runtime

### Components

- Browser-based fullscreen scene
- Canvas 2D rendering with vanilla JavaScript
- Python stdlib server bridge for state reading
- States: idle, listening, thinking, speaking, alert

### Performance and behavior

- A single eased energy model drives multiple visual outputs.
- Adaptive frame targeting keeps the system responsive under different constraints.
- State transitions are captured through a file bus and rendered programmatically.

## Shared engineering principles

### Timestamp correctness

Use epoch-based comparisons such as `Date.now() / 1000` instead of page-relative timing sources when validating stale state across subsystems.

### State freshness

Stale state files should be treated as invalid and reset explicitly to avoid ghost outputs or incorrect UI states.

### Verification discipline

- Validate actual runtime behavior with fresh tests.
- Use headless browser checks for visuals.
- Test stale-state and restart edge cases.
- Keep a written source of truth for system memory.

## Agent system

The `agency_agents/` directory is the structured agent knowledge base. These files capture operational domains, execution workers, tasks, and specialized agent definitions that support the broader Jarvis ecosystem.

## Documentation approach

This repository should remain the canonical landing point for:

- setup guidance
- runtime behavior notes
- failure cases and fixes
- architectural understanding
- known working patterns and lessons learned
