# Replication Guide

This guide explains how to recreate the Open Source Jarvis setup described in this repository and in the working runtime notes for the voice assistant and visualizer projects.

## 1. Goal

The system is designed to work as a local AI assistant stack with:

- push-to-talk voice input
- speech-to-text using Whisper.cpp
- reasoning using Open Code CLI
- text-to-speech using Kokoro FastAPI
- a browser-based visualizer that reflects live assistant state
- a shared file-based signal bus between subsystems

The goal is to reproduce the same architecture in a way that is understandable, testable, and easy to maintain.

## 2. Recommended environment

Use a Windows 11 machine for the most faithful reproduction.

### Required software

- Git
- Python 3.11 or 3.12
- Chrome or Edge browser
- Open Code CLI version 1.18.16
- Whisper.cpp with a CUDA build
- Kokoro FastAPI
- Optional: uv for Python environment management

### Recommended folders

- project root: `C:\Users\devpa\OneDrive\Documents\Default Project`
- home: `C:\Users\devpa\`
- Obsidian vaults: `C:\Users\devpa\Brain\` and `C:\Users\devpa\SecondBrain\`

## 3. Repository layout

Use this repository structure as the base:

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

This repo acts as the master memory and documentation layer for the runtime ecosystem.

## 4. Clone and set up the repo

```powershell
git clone https://github.com/devmpatel27-glitch/Open-source-Jarvis.git
cd open-source-jarvis
```

Create the local Python environment for the voice subsystem:

```powershell
cd voice-line
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the project uses the package metadata instead of a requirements file:

```powershell
pip install -e .
```

## 5. Install Open Code CLI

Install the Open Code CLI and verify that it is on your PATH:

```powershell
opencode --version
```

Expected behavior: the CLI should print the installed version. The working configuration used in this project uses:

- `opencode/deepseek-v4-flash-free`

Configure your preferred model in the relevant runtime configuration file or environment variables if your project uses them.

## 6. Install Whisper.cpp

Whisper.cpp is the speech-to-text layer used by the voice assistant.

### Minimum requirements

- A local Whisper.cpp build
- A model file similar to `ggml-small.en.bin`
- CUDA support if using GPU acceleration

### Typical flow

1. Clone or download Whisper.cpp.
2. Build the CUDA-enabled binary.
3. Download the encoder model.
4. Ensure your local startup script launches Whisper on a stable port.

Example flow:

```powershell
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release
```

Then start the server or runtime with the model file loaded.

## 7. Set up Kokoro FastAPI

Kokoro provides the text-to-speech layer. In the working runtime, it listens at port `8880` and uses the voice `bm_daniel`.

### Typical setup

1. Install Kokoro and its Python dependencies.
2. Start the FastAPI service.
3. Verify HTTP health checks respond successfully.
4. Use the voice model `bm_daniel` or the closest equivalent available in your build.

Example health check:

```powershell
Invoke-WebRequest http://localhost:8880/health
```

## 8. Set up the voice-line runtime

The voice-line subsystem is the orchestration layer. It should coordinate:

- hotkey input (`Alt` hold-to-talk)
- STT capture
- brain interaction through Open Code
- TTS playback
- shared state bus updates

### Key files in the voice-line runtime

- `main.py` — turn loop and orchestration
- `ptt.py` — push-to-talk logic using `GetAsyncKeyState`
- `brain.py` — Open Code integration and active message tracking
- `ears.py` — Whisper STT client
- `mouth.py` — Kokoro TTS and sentence chunking logic
- `signals.py` — file bus state tracking
- `vlog.py` — logging

### Important implementation choice

The project learned that `pynput` low-level hooks can silently fail in some Windows environments. The working approach is to poll physical key state using `GetAsyncKeyState` in a short loop instead.

## 9. File-based state bus pattern

The visualizer and voice-line communicate through files instead of a direct in-process broker.

### Shared file bus

- `.voice_state` — state values like `idle`, `listening`, `thinking`, `speaking`, `alert`
- `.voice_waveform` — JSON waveform payload with a timestamp and samples
- `.voice_alert` — marker indicating when the alert state is active

### Correct stale-state rule

Use epoch timestamps for staleness checks. Do not compare against `performance.now()` because it is page-relative, not wall-clock time.

Use this logic:

```python
Date.now() / 1000 - bus_ts > 3
```

This marks old data as stale instead of continuing to show a live state.

## 10. Launch the visualizer

The visualizer is a local fullscreen browser scene rendered with canvas 2D and vanilla JavaScript.

### Typical launch flow

- serve the UI over a local Python HTTP server
- open it in Chrome in kiosk mode
- use the state bus to drive animation and appearance

### Common ports

- live server: `8777`
- mock server: `8778`

### Useful verification hooks

- `?shot=idle&t=2000` for deterministic freeze render
- `?mockstate=speaking` for local simulation without touching the live state bus
- `--mock` flag for a scripted loop on the mock port

## 11. End-to-end verification

Once the services are running, check the whole stack in order:

1. Confirm Whisper is responsive.
2. Confirm Kokoro is reachable.
3. Confirm Open Code CLI is healthy and selected model is available.
4. Hold Alt and speak.
5. Verify the STT pipeline transcribes correctly.
6. Confirm the brain returns a valid response.
7. Confirm the TTS layer emits spoken output.
8. Confirm the visualizer reflects the correct state changes.

### State transitions to verify

- idle
- listening
- thinking
- speaking
- alert

## 12. Common pitfalls

### Hook-based input failure

Do not depend on low-level keyboard hooks in a constrained Windows environment unless you have validated them. Use polling with `GetAsyncKeyState` instead.

### Wrong timestamp source

Always use epoch time or `Date.now()` for freshness checks.

### Stale process confusion

After editing shared timing, signal, or audio logic, restart the process to avoid stale instance issues.

### Mock success vs. real runtime verification

A synthetic pass is not enough. Validate the actual voice path end-to-end.

### Long PowerShell runs

Avoid long single-command sleeps and long-running PowerShell tasks with strict timeouts. Split commands into smaller steps where necessary.

## 13. Optional verification automation

For visual confidence, use headless browser capture and PIL-based pixel analysis.

### Example screenshot flow

```powershell
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
& $chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1280,720 --screenshot="out.png" --virtual-time-budget=500 "http://localhost:8778/?shot=state&t=2000"
```

Then inspect the image for brightness, contrast, and color distribution using Python PIL.

## 14. Recommended replication checklist

- install Python and Git
- clone this repo
- set up the voice-line venv
- install Open Code CLI
- set up Whisper.cpp and model file
- start the Kokoro TTS server
- launch the voice assistant pipeline
- launch the visualizer
- verify state transitions and audio flow end-to-end
- check stale-state logic and timestamp correctness
- document any environment-specific local differences in the project memory

## 15. Best practices

- Keep a single source of truth for project memory in this repository.
- Treat shared timing logic as correctness-critical.
- Verify with real runtime behavior, not assumptions.
- Prefer small, testable subsystems over monolithic setup scripts.
- Preserve the file-bus architecture for stable communication between the voice and visual layers.

## 16. Final note

The real power of this project is not just the AI model itself, but the way the full system is assembled: voice input, state bus, reasoning engine, speech output, and live visual feedback working together. The most important part of replication is not copying code blindly; it is reproducing the verification discipline and runtime behavior that made the system reliable.
