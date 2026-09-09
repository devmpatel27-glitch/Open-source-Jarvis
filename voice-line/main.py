"""Core orchestration logic for the voice-line assistant."""

from __future__ import annotations

from memory_adapter import MemoryAdapter, build_augmented_prompt


_memory_adapter: MemoryAdapter | None = None


def get_memory_adapter() -> MemoryAdapter:
    """Create and load the memory adapter once for the process."""
    global _memory_adapter
    if _memory_adapter is None:
        _memory_adapter = MemoryAdapter()
        _memory_adapter.load_index()
    return _memory_adapter


def build_prompt(system_instructions: str, conversation_history: str, user_input: str) -> str:
    """Build the Open Code prompt with up to three relevant memories."""
    return build_augmented_prompt(system_instructions, conversation_history, user_input, get_memory_adapter(), k=3)


def main() -> None:
    """Launch the assistant runtime."""
    print("Voice-line assistant starting...")
    print("Memory-aware Open Code prompt orchestration is ready.")


if __name__ == "__main__":
    main()
