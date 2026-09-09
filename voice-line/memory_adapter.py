"""Obsidian Markdown to a small, portable vector index.

The adapter intentionally depends only on the Python standard library. A real
embedding provider can implement ``Embedder`` and be passed to ``build_index``.
This makes local Windows use simple and keeps CI deterministic.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence


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
    def build(cls, vault: Path, embedder: Embedder) -> "MemoryIndex":
        vault = vault.expanduser().resolve()
        if not vault.is_dir():
            raise FileNotFoundError(f"Obsidian vault does not exist: {vault}")
        entries = []
        for path in sorted(vault.rglob("*.md")):
            if any(part.startswith(".") for part in path.relative_to(vault).parts):
                continue
            note = parse_markdown(path, vault)
            entries.append(IndexedNote(note=note, vector=list(embedder.embed(f"{note.title}\n{note.content}"))))
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


def build_index(vault_path: str | Path, index_path: str | Path, embedder: Embedder) -> MemoryIndex:
    """Build and persist an index from an Obsidian vault."""
    index = MemoryIndex.build(Path(vault_path), embedder)
    index.save(Path(index_path))
    return index
