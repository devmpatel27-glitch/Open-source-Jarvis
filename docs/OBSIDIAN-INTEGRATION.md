# Obsidian Integration

Open Source Jarvis can use an Obsidian vault as a local memory source. The V1 adapter reads Markdown notes, extracts simple YAML frontmatter, embeds each note through a caller-provided embedder, and persists a portable JSON vector index.

## Important spelling note

The filename uses the standard **Obsidian** spelling. Keep that spelling consistent in prose and code identifiers.

## How it works

1. Select a vault directory, such as `C:\Users\devpa\Brain\Doom's Digital Consciousness`.
2. Recursively read `.md` files.
3. Skip hidden directories such as `.obsidian`.
4. Parse simple frontmatter fields such as `title`, `project`, `status`, and `tags`.
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

## Re-indexing policy

Rebuild the index when notes change. For a larger vault, add file hashes and modification times so unchanged notes can be reused instead of re-embedded. V1 deliberately keeps the format small and explicit before adding incremental indexing.

## Safety and privacy

- Keep the vault outside the repository.
- Keep generated indexes in a local ignored directory.
- Never commit API keys or private notes.
- Prefer local embedding models when the vault contains sensitive content.
- Treat retrieved notes as untrusted context and apply normal prompt-injection defenses before passing them to Open Code.

## Tests

The tests use a deterministic dummy embedder and the fixture vault in `tests/fixture_vault/`:

```powershell
python -m pytest -q
```

This verifies frontmatter parsing, hidden-directory exclusion, cosine search, and persistence without requiring optional dependencies.
