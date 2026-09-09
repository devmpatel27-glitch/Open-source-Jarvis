# Obsidian Integration

Open Source Jarvis can use an Obsidian vault as a local memory source. The V1 adapter reads Markdown notes, extracts simple YAML frontmatter, embeds each note through a caller-provided embedder, and persists a portable JSON vector index.

## How it works

1. Select a vault directory, such as `C:\Users\devpa\Brain\Doom's Digital Consciousness`.
2. Recursively read `.md` files.
3. Skip hidden directories such as `.obsidian`.
4. Parse simple frontmatter fields such as `title`, `tags`, `created`, `source`, and `visibility`.
5. Embed title plus note body.
6. Persist vectors and metadata to a JSON index.
7. Search the index with the same embedding model.

The implementation is in [voice-line/memory_adapter.py](../voice-line/memory_adapter.py).

## Dependency options

The adapter itself uses only the Python standard library. This is intentional: Windows users can test the integration without downloading a model, and CI can run without GPU, audio, or network access.

For production embeddings, install the optional memory dependencies:

```powershell
cd voice-line
pip install -e ".[memory]"
```

The optional group contains:

- `sentence-transformers` for local semantic embeddings
- `faiss-cpu` for a scalable nearest-neighbor index
- `python-frontmatter` for richer YAML frontmatter parsing

The current JSON index is the V1 reference implementation. A FAISS-backed implementation can preserve the same `Embedder` and search boundary later.

## Recommended vault layout

Keep the vault outside this repository and organize notes by domain:

```text
Doom's Digital Consciousness/
├── 00 - Inbox/
├── 01 - Daily Notes/
├── 02 - Projects/
│   └── Open Source Jarvis.md
├── Skills & Knowledge/
└── Project Memory/
```

Use frontmatter that makes retrieval and auditing predictable:

```yaml
---
title: Open Source Jarvis
tags: [project:jarvis, domain:voice]
created: 2026-09-09
source: voice-line
visibility: public
---
```

Set `visibility: private` for sensitive notes. V1 excludes those notes from the index.

## Example usage

```python
from pathlib import Path

from memory_adapter import build_index


class MyEmbedder:
    def embed(self, text: str) -> list[float]:
        # Replace with SentenceTransformer.encode(...).tolist() in production.
        return [float(len(text))]


build_index(
    Path(r"C:\Users\devpa\Brain\Doom's Digital Consciousness"),
    Path(".jarvis/memory-index.json"),
    MyEmbedder(),
)
```

Do not commit the generated index or the vault itself. Vault content can be private and the index may contain recoverable text metadata.

## CLI usage

The adapter supports Windows-friendly environment variables and direct commands:

```powershell
$env:OB_VAULT_PATH = "C:\Users\devpa\Brain\Doom's Digital Consciousness"
$env:MEMORY_INDEX_PATH = ".jarvis\memory-index.json"
$env:MEMORY_METADATA_PATH = ".jarvis\memory-metadata.json"
$env:MEMORY_CHUNK_SIZE = "600"
$env:EMBEDDING_BACKEND = "dummy"
python voice-line\memory_adapter.py --build
python voice-line\memory_adapter.py --query "what did I say about project A?"
```

For a real local embedding model:

```powershell
pip install -e ".\voice-line[memory]"
$env:EMBEDDING_BACKEND = "sentence-transformers"
python voice-line\memory_adapter.py --build
```

The index format is JSON in V1. It is intentionally portable; future FAISS integration can store a binary vector index beside the same metadata manifest. `MEMORY_METADATA_PATH` optionally writes a metadata-only JSON manifest for inspection and auditing.

## Re-indexing policy

Rebuild the index when notes change. `MEMORY_CHUNK_SIZE` controls the maximum retrieved snippet size and defaults to 600 characters. For a larger vault, add file hashes and modification times so unchanged notes can be reused instead of re-embedded. V1 deliberately keeps the format small and explicit before adding incremental indexing.

## Runtime prompt integration

Before sending a user turn to Open Code, the orchestration layer loads the index once, retrieves the top three hits, and injects a bounded block:

```python
adapter.load_index()
hits = adapter.search(user_input, k=3)
memory_block = format_memory_block(hits)
prompt = f"{system_prompt}\n\n{memory_block}\n\n{history}\n\nUser: {user_input}"
```

Each hit includes title, relative path, optional `created` date, and a short snippet. The visualizer continues to consume the same file-based IPC state and does not need to know about embeddings.

## Hardware constraints

- A CUDA-capable GPU is recommended for Whisper.cpp and larger local models.
- CPU-only Whisper and smaller models work with lower throughput.
- The dummy embedder requires no model download and is the CI default.
- Sentence Transformers can run on CPU, but first startup downloads a model and uses more memory.
- FAISS is optional; the V1 JSON cosine index is suitable for small vaults.

## Safety and privacy

- Keep the vault outside the repository.
- Keep generated indexes in a local ignored directory.
- Never commit API keys or private notes.
- Prefer local embedding models when the vault contains sensitive content.
- Consider filesystem or volume encryption for the vault and index.
- Treat retrieved notes as untrusted context and apply normal prompt-injection defenses before passing them to Open Code.

## Tests

The tests use a deterministic dummy embedder and the fixture vault in `tests/fixture_vault/`:

```powershell
python -m pytest -q
```

This verifies frontmatter parsing, hidden-directory exclusion, cosine search, and persistence without requiring optional dependencies.
