from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "voice-line"))

from memory_adapter import MemoryIndex, build_index  # noqa: E402


class DummyEmbedder:
    """Deterministic CI-safe embedder with no model downloads."""

    def embed(self, text: str) -> list[float]:
        words = set(text.lower().split())
        return [
            float("voice" in words or "audio" in words),
            float("open" in words or "code" in words),
            float("whisper" in words or "speech" in words),
        ]


def test_build_search_and_persist_index(tmp_path: Path) -> None:
    vault = Path(__file__).parent / "fixture_vault"
    destination = tmp_path / "memory-index.json"
    embedder = DummyEmbedder()

    index = build_index(vault, destination, embedder)

    assert destination.exists()
    assert len(index.entries) == 2
    results = index.search("voice Open Code", embedder, top_k=1)
    assert results[0][1].title == "Jarvis Project"
    assert results[0][1].metadata["project"] == "jarvis"

    loaded = MemoryIndex.load(destination)
    assert loaded.search("Whisper speech", embedder, top_k=1)[0][1].title == "Audio Notes"


def test_hidden_markdown_is_excluded(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / ".obsidian" / "internal.md").write_text("hidden", encoding="utf-8")
    (vault / "visible.md").write_text("visible", encoding="utf-8")

    index = MemoryIndex.build(vault, DummyEmbedder())

    assert [entry.note.path for entry in index.entries] == ["visible.md"]


def test_private_notes_are_excluded(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "private.md").write_text(
        "---\nvisibility: private\n---\nsecret note",
        encoding="utf-8",
    )
    (vault / "public.md").write_text("public note", encoding="utf-8")

    index = MemoryIndex.build(vault, DummyEmbedder())

    assert [entry.note.path for entry in index.entries] == ["public.md"]
