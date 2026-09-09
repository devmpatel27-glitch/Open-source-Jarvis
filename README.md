# Open Source Jarvis 🎙️

A voice-first AI assistant that listens, reasons, and talks back — running entirely
on local, self-hosted infrastructure (no cloud API required).


## What it does
- Push-to-talk voice input (hold Alt to speak, release to send)
- Local speech-to-text via Whisper.cpp
- LLM reasoning/orchestration via Open Code
- Local text-to-speech via Kokoro
- A browser-based visualizer that reflects assistant state in real time, synced
  through a file-based signal bus
- Memory: persistent long-term memory backed by an Obsidian vault (see docs/OBSIDIAN-INTEGRATION.md)

Open Source Jarvis is an AI assistant ecosystem built around a real-time voice-first runtime, a live visualizer, and a modular agent system. In the current setup, it runs with Open Code as the reasoning engine and (optionally) an attached Obsidian vault to provide memory for multi-turn context and retrieval-augmented behavior.

## Core subsystems

- `voice-line/` — Push-to-talk voice assistant named Doom. Handles STT, brain orchestration, TTS, and signal coordination.
- `visualizer/` — Fullscreen browser scene that visualizes assistant state through a Doctor Doom-inspired metallic mask.
- `agency_agents/` — Agent markdown library and task domain structure.
- `docs/` — Unified documentation, setup, troubleshooting, and architecture notes (see docs/OBSIDIAN-INTEGRATION.md for memory integration).
- `.github/workflows/` — CI scaffolding for future validation.

## Current stack

- STT: Whisper.cpp using the CUDA build and `ggml-small.en.bin`
- Brain: Open Code CLI with `opencode/deepseek-v4-flash-free`
- Memory: Obsidian vault (local filesystem) used as a persistent memory store when enabled
- TTS: Kokoro FastAPI at `:8880` with voice `bm_daniel`
- Input: Hold `Alt` to speak; release to send
- IPC: File-based signal bus shared between voice and visual systems

## Working patterns and lessons learned

- Prefer real runtime verification over synthetic success checks.
- Use epoch-based time comparisons rather than browser-relative clocks.
- Validate stale state behavior and restart processes after important edits.
- Test visual behavior programmatically with deterministic render hooks.
- Keep token use efficient when running local reasoning under tight constraints.

## Repository structure

```text
open-source-jarvis/
├── .github/workflows/
├── agency_agents/
├── docs/
├── voice-line/
├── visualizer/
├── .gitignore
├── LICENSE
├── README.md
└── ...
```

## Quick start

1. Review the documentation in `docs/` (start with docs/QUICK-START.md and docs/OBSIDIAN-INTEGRATION.md if you plan to enable memory).
2. Set up the environment in `voice-line/`.
3. Use the startup commands in the voice-line guide.
4. Launch the visualizer and validate the signal bus state transitions.
5. Reuse the operational patterns in `docs/SKILLS-AND-KNOWLEDGE.md` when debugging or extending the system.

## Memory (Obsidian) — short notes

If you've connected Open Code to an Obsidian vault to give the assistant long-term memory, the repository documents a recommended integration pattern in docs/OBSIDIAN-INTEGRATION.md. That document includes:

- An architecture overview showing how the voice-line, Open Code brain, and a memory adapter interact with an Obsidian vault.
- Recommended vault structure and note metadata for reliable retrieval.
- A safe, local-only sync and embedding workflow (what to index, what to keep private).
- Example environment variables and quick verification steps.

If you'd like, I can add a runnable example adapter (e.g., `voice-line/memory_adapter.py`) that demonstrates simple read/write and retrieval calls against your Obsidian vault.

## Documentation index

- [docs/INDEX.md](docs/INDEX.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/QUICK-START.md](docs/QUICK-START.md)
- [docs/REPLICATION-GUIDE.md](docs/REPLICATION-GUIDE.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [docs/SKILLS-AND-KNOWLEDGE.md](docs/SKILLS-AND-KNOWLEDGE.md)
- [docs/OBSIDIAN-INTEGRATION.md](docs/OBSIDIAN-INTEGRATION.md)

## License

This project is licensed under the MIT License.
