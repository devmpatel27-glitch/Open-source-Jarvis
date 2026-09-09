"""Obsidian Markdown to a small, portable vector index.

The adapter intentionally depends only on the Python standard library. A real
embedding provider can implement ``Embedder`` and be passed to ``build_index``.
This makes local Windows use simple and keeps CI deterministic.
"""

from __future__ import annotations

import json
import argparse
import hashlib
import logging
import math
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence


logger = logging.getLogger(__name__)


class Embedder(Protocol):
    """Minimal embedding interface used by the index."""

    def embed(self, text: str) -> Sequence[float]:
        """Return a stable numeric vector for ``text``."""


@dataclass(frozen=True)
class Note:
    """A Markdown note and its searchable metadata."""

    path: str
    title: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class IndexedNote:
    """A note plus its persisted embedding."""

    note: Note
    vector: list[float]


_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
    return value.strip("'\"")


def _parse_wikilinks(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", text)


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    """Split notes at paragraph boundaries while respecting a character cap."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > chunk_size:
            chunks.append(current)
            current = ""
        while len(paragraph) > chunk_size:
            chunks.append(paragraph[:chunk_size].strip())
            paragraph = paragraph[chunk_size:]
        current = f"{current}\n\n{paragraph}".strip() if current else paragraph
    if current:
        chunks.append(current)
    return chunks or [""]


def parse_markdown(path: Path, root: Path) -> Note:
    """Read one Obsidian note without requiring PyYAML or frontmatter."""
    raw = path.read_text(encoding="utf-8")
    metadata: dict[str, Any] = {}
    match = _FRONTMATTER.match(raw)
    content = raw
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = _parse_scalar(value)
        content = raw[match.end():]

    title = str(metadata.get("title") or path.stem)
    relative_path = path.relative_to(root).as_posix()
    return Note(path=relative_path, title=title, content=content.strip(), metadata=metadata)


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions must match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


class MemoryIndex:
    """Portable vector index with cosine search and JSON persistence."""

    def __init__(self, entries: Sequence[IndexedNote] = ()) -> None:
        self.entries = list(entries)

    @classmethod
    def build(cls, vault: Path, embedder: Embedder, chunk_size: int = 600) -> "MemoryIndex":
        vault = vault.expanduser().resolve()
        if not vault.is_dir():
            raise FileNotFoundError(f"Obsidian vault does not exist: {vault}")
        entries = []
        for path in sorted(vault.rglob("*.md")):
            if any(part.startswith(".") for part in path.relative_to(vault).parts):
                continue
            note = parse_markdown(path, vault)
            if str(note.metadata.get("visibility", "public")).lower() != "public":
                logger.info("Skipping non-public note: %s", note.path)
                continue
            wikilinks = _parse_wikilinks(note.content)[:10]
            chunks = _chunk_text(note.content, chunk_size)
            for chunk_index, chunk in enumerate(chunks):
                chunk_metadata = {**note.metadata, "chunk_index": chunk_index, "wikilinks": wikilinks}
                chunk_note = Note(note.path, note.title, chunk, chunk_metadata)
                entries.append(
                    IndexedNote(note=chunk_note, vector=list(embedder.embed(f"{note.title}\n{chunk}")))
                )
        return cls(entries)

    def search(self, query: str, embedder: Embedder, top_k: int = 5) -> list[tuple[float, Note]]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        query_vector = embedder.embed(query)
        ranked = sorted(
            ((_cosine_similarity(query_vector, entry.vector), entry.note) for entry in self.entries),
            key=lambda item: item[0],
            reverse=True,
        )
        return ranked[:top_k]

    def save(self, destination: Path) -> None:
        destination = destination.expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "entries": [asdict(entry) for entry in self.entries]}
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, source: Path) -> "MemoryIndex":
        payload = json.loads(source.expanduser().read_text(encoding="utf-8"))
        if payload.get("version") != 1:
            raise ValueError("Unsupported memory index version")
        entries = []
        for item in payload["entries"]:
            entries.append(
                IndexedNote(
                    note=Note(**item["note"]),
                    vector=[float(value) for value in item["vector"]],
                )
            )
        return cls(entries)


def build_index(
    vault_path: str | Path,
    index_path: str | Path,
    embedder: Embedder,
    chunk_size: int = 600,
) -> MemoryIndex:
    """Build and persist an index from an Obsidian vault."""
    index = MemoryIndex.build(Path(vault_path), embedder, chunk_size=chunk_size)
    index.save(Path(index_path))
    return index


class DummyEmbedder:
    """Deterministic local embedder for tests and smoke checks."""

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            vector[int.from_bytes(digest[:4], "big") % self.dimensions] += 1.0
        return vector


class SentenceTransformerEmbedder:
    """Optional production embedder backed by sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError('Install the optional memory dependencies with: pip install -e ".[memory]"') from exc
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        return [float(value) for value in self.model.encode(text, normalize_embeddings=True).tolist()]


class MemoryAdapter:
    """Runtime facade used by voice-line orchestration."""

    def __init__(self, index_path: str | Path | None = None, embedder: Embedder | None = None) -> None:
        self.index_path = Path(index_path or os.getenv("MEMORY_INDEX_PATH", ".jarvis/memory-index.json")).expanduser()
        metadata_path = os.getenv("MEMORY_METADATA_PATH", ".jarvis/memory-metadata.json")
        self.metadata_path = Path(metadata_path).expanduser()
        self.embedder = embedder or create_embedder()
        self.index: MemoryIndex | None = None
        self.chunk_size = int(os.getenv("MEMORY_CHUNK_SIZE", "600"))
        self.max_memory_chars = int(os.getenv("MEMORY_MAX_CHARS", "4000"))

    def load_index(self) -> MemoryIndex:
        """Load the index once at runtime; an absent index means no memories."""
        if self.index is None:
            self.index = MemoryIndex.load(self.index_path) if self.index_path.exists() else MemoryIndex()
        return self.index

    def search(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        """Return auditable memory hits with title, path, metadata, and snippet."""
        hits = self.load_index().search(query, self.embedder, top_k=k)
        return [
            {
                "score": score,
                "meta": {"title": note.title, "path": note.path, **note.metadata},
                "snippet": note.content[: self.chunk_size].strip(),
            }
            for score, note in hits
        ]

    def build(self, vault_path: str | Path) -> MemoryIndex:
        self.index = build_index(vault_path, self.index_path, self.embedder, chunk_size=self.chunk_size)
        if self.metadata_path:
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata = [
                {"title": entry.note.title, "path": entry.note.path, **entry.note.metadata}
                for entry in self.index.entries
            ]
            self.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return self.index


def create_embedder() -> Embedder:
    backend = os.getenv("EMBEDDING_BACKEND", "dummy").lower()
    if backend == "dummy":
        return DummyEmbedder()
    if backend == "sentence-transformers":
        return SentenceTransformerEmbedder(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    raise ValueError(f"Unsupported EMBEDDING_BACKEND: {backend}")


def format_memory_block(hits: Sequence[dict[str, Any]], max_chars: int = 4000) -> str:
    """Format retrieved notes as a bounded, provenance-rich prompt section."""
    suffix = "\n[END MEMORY]"
    if max_chars < len(suffix):
        raise ValueError(f"max_chars must be at least {len(suffix)}")
    if not hits:
        return "[RELEVANT MEMORY]\nNo relevant memory was retrieved.\n[END MEMORY]"
    sections = []
    for hit in hits:
        meta = hit["meta"]
        date = meta.get("created", "")
        sections.append(
            f"=== RELEVANT MEMORY ({meta.get('title', 'Untitled')}, {date}) ===\n"
            f"Source: {meta.get('path', '')}\n{hit['snippet']}\n=== END MEMORY ==="
        )
    block = "[RELEVANT MEMORY]\n" + "\n\n".join(sections) + "\n[END MEMORY]"
    if len(block) <= max_chars:
        return block
    return block[: max_chars - len(suffix)].rstrip() + suffix


def build_augmented_prompt(
    system_instructions: str,
    conversation_history: str,
    user_input: str,
    adapter: MemoryAdapter,
    k: int = 3,
) -> str:
    """Retrieve memory and inject it between system instructions and history."""
    adapter.load_index()
    memory_block = format_memory_block(adapter.search(user_input, k=k), adapter.max_memory_chars)
    return f"{system_instructions}\n\n{memory_block}\n\n{conversation_history}\n\nUser: {user_input}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or query an Obsidian memory index.")
    parser.add_argument("--build", action="store_true", help="Build an index from an Obsidian vault")
    parser.add_argument("--vault", default=os.getenv("OB_VAULT_PATH"), help="Path to the Obsidian vault")
    parser.add_argument("--query", help="Search the persisted index")
    parser.add_argument("--index", help="Override MEMORY_INDEX_PATH")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    adapter = MemoryAdapter(index_path=args.index)
    if args.build:
        if not args.vault:
            parser.error("--build requires --vault or OB_VAULT_PATH")
        index = adapter.build(args.vault)
        print(f"Indexed {len(index.entries)} notes at {adapter.index_path}")
    if args.query:
        for hit in adapter.search(args.query, k=args.top_k):
            print(f"{hit['score']:.4f} {hit['meta']['title']} [{hit['meta']['path']}]")
            print(hit["snippet"])
            print()


if __name__ == "__main__":
    main()
