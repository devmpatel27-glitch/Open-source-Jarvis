# Open Source Jarvis

Open Source Jarvis is a modular AI assistant ecosystem designed to combine voice interaction, streaming visualization, autonomous agent orchestration, and a shared documentation hub. The repository is organized into independent subsystems that can evolve together while remaining easy to navigate and extend.

## Repository overview

- `voice-line/` — Real-time voice assistant subsystem with orchestration logic and automation hooks.
- `visualizer/` — Live stream visualization and monitoring interfaces.
- `agency_agents/` — Agent knowledge base with organized markdown modules and specialist definitions.
- `docs/` — Centralized documentation for onboarding, troubleshooting, and architecture references.
- `.github/workflows/` — CI and automation scaffolding for future code validation.

## Included capabilities

- Voice-first interaction and command handling
- Agent-driven workflow support
- Shared memory and documentation patterns
- Visual monitoring and real-time feedback loops
- Modular architecture for local experimentation and future cloud deployment

## Quick start

1. Read the documentation in `docs/`.
2. Set up the Python environment in `voice-line/`.
3. Review the agent files in `agency_agents/`.
4. Extend the functionality in the corresponding subsystem folders.

## Project structure

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

## License

This project is licensed under the MIT License.
