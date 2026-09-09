# Open Source Jarvis

Open Source Jarvis is an AI assistant ecosystem built around a real-time voice-first runtime, a live visualizer, and a modular agent system. In the current setup, it runs with Open Code as the reasoning layer, Whisper for speech-to-text, Kokoro for text-to-speech, and a browser-based visual mask that reflects the assistant state in real time.

## Core subsystems

- `voice-line/` — Push-to-talk voice assistant named Doom. Handles STT, brain orchestration, TTS, and signal coordination.
- `visualizer/` — Fullscreen browser scene that visualizes assistant state through a Doctor Doom-inspired metallic mask.
- `agency_agents/` — Agent markdown library and task domain structure.
- `docs/` — Unified documentation, setup, troubleshooting, and architecture notes.
- `tests/` — Deterministic memory adapter fixtures and CI-safe tests.
- `.github/workflows/` — CI scaffolding for future validation.

## Current stack

- STT: Whisper.cpp using the CUDA build and `ggml-small.en.bin`
- Brain: Open Code CLI with `opencode/deepseek-v4-flash-free`
- TTS: Kokoro FastAPI at `:8880` with voice `bm_daniel`
- Input: Hold `Alt` to speak; release to send
- IPC: File-based signal bus shared between voice and visual systems

## Obsidian memory

The optional memory layer indexes a local Obsidian vault and injects the top
three relevant notes into Open Code prompts with title, path, date, and a
bounded snippet for auditability. The adapter has a standard-library dummy
backend for CI and smoke tests, with optional Sentence Transformers and FAISS
dependencies for local semantic search.

Hardware note: a GPU is recommended for Whisper and larger local models; CPU-only Whisper and the dummy embedding backend provide a slower but reproducible fallback.

- [Obsidian integration guide](docs/OBSIDIAN-INTEGRATION.md)
- [Architecture diagram](docs/architecture-ai-jarvis.svg)
- [Project memory runbook](docs/PROJECT-MEMORY.md)

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
├── tests/
├── voice-line/
├── visualizer/
├── .gitignore
├── LICENSE
├── README.md
└── ...
```

## Quick start

1. Review the documentation in `docs/`.
2. Set up the environment in `voice-line/`.
3. Use the startup commands in the voice-line guide.
4. Launch the visualizer and validate the signal bus state transitions.
5. Reuse the operational patterns in `docs/SKILLS-AND-KNOWLEDGE.md` when debugging or extending the system.

## Documentation index

- [docs/INDEX.md](docs/INDEX.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/QUICK-START.md](docs/QUICK-START.md)
- [docs/REPLICATION-GUIDE.md](docs/REPLICATION-GUIDE.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [docs/SKILLS-AND-KNOWLEDGE.md](docs/SKILLS-AND-KNOWLEDGE.md)
- [docs/OBSIDIAN-INTEGRATION.md](docs/OBSIDIAN-INTEGRATION.md)
- [docs/PROJECT-MEMORY.md](docs/PROJECT-MEMORY.md)

## License

This project is licensed under the MIT License.