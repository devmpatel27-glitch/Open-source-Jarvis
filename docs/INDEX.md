# Open Source Jarvis Documentation Index

## Overview

This documentation hub centralizes the real runtime knowledge for the Open Source Jarvis ecosystem, including the working voice assistant, the visualizer, shared verification practices, and the agent architecture.

## Primary references

- [QUICK-START.md](QUICK-START.md) — one-page setup guide for the current local runtime
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — common issue handling and debugging flow
- [ARCHITECTURE.md](ARCHITECTURE.md) — end-to-end system design and runtime notes
- [SKILLS-AND-KNOWLEDGE.md](SKILLS-AND-KNOWLEDGE.md) — reusable patterns and lessons learned
- [index.md](index.md) — master index for agent domains and system connections

## System domains

- `voice-line/` — real-time voice assistant subsystem (`Doom`), STT + brain + TTS stack
- `visualizer/` — browser-based stream visualizer with state-driven mask behavior
- `agency_agents/` — the prepared multi-domain agent markdown collection
- `docs/` — project memory and operational guidance

## Shared operational principles

- Verify against real runtime behavior, not synthetic assumptions.
- Treat timestamps and stale-state handling as correctness-critical issues.
- Validate audio and visual flows as integrated end-to-end systems.
- Keep a single source of truth for what works, what failed, and what remains under development.

## Recommended workflow

1. Start with the quick start guide.
2. Review the architecture notes for subsystem relationships.
3. Validate the voice-line stack before changing runtime behavior.
4. Confirm visualizer state transitions when editing the UI state bus.
5. Revisit troubleshooting for stale-instance or integration issues.
