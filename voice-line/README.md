# Voice Line

Real-time voice assistant subsystem for Open Source Jarvis.

## Purpose

This project handles voice capture, wake-word or push-to-talk input, command routing, and AI orchestration.

## Typical structure

- `main.py` — orchestration entry point
- `ptt.py` — push-to-talk input logic
- `memory_adapter.py` — Obsidian Markdown index and retrieval adapter
- `pyproject.toml` — project configuration and dependencies

## Getting started

```bash
cd voice-line
python -m venv .venv
source .venv/bin/activate
pip install -e .
python main.py
```

## How to enable memory

Memory is opt-in. Set the vault and index paths, choose an embedding backend,
then build the local index before starting the assistant:

```powershell
$env:OB_VAULT_PATH = "C:\Users\devpa\Brain\Doom's Digital Consciousness"
$env:MEMORY_INDEX_PATH = ".jarvis\memory-index.json"
$env:EMBEDDING_BACKEND = "dummy"
python memory_adapter.py --build
python memory_adapter.py --query "what did I say about project A?"
```

Use `dummy` for tests and smoke checks. For local semantic embeddings:

```powershell
pip install -e ".[memory]"
$env:EMBEDDING_BACKEND = "sentence-transformers"
python memory_adapter.py --build
```

The orchestration path calls `MemoryAdapter.load_index()` once, retrieves the
top three hits for each user request, and injects a provenance-rich
`[RELEVANT MEMORY]` block before conversation history is sent to Open Code.
Only public notes (`visibility: public`) are indexed; private and sensitive notes are excluded. `MEMORY_CHUNK_SIZE` controls note chunks and `MEMORY_MAX_CHARS` caps the prompt memory block.
