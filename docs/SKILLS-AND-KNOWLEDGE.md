# Skills & Knowledge

Condensed skills learned from the voice-line and visualizer projects. Each skill is a reusable pattern for future work.

## Skill: Windows Push-to-Talk via GetAsyncKeyState

### Problem

pynput's low-level keyboard hook may silently fail in some Windows environments. The listener thread remains alive, but no events fire.

### Solution

Use GetAsyncKeyState polling instead of hook-based listeners.

### Pattern

```python
import ctypes
import ctypes.wintypes
import time

user32 = ctypes.windll.user32
VK_MENU = 0x12


def is_alt_down():
    return bool(user32.GetAsyncKeyState(VK_MENU) & 0x8000)


prev = is_alt_down()
while not stop_flag:
    cur = is_alt_down()
    if cur and not prev:
        handle_press()
    elif not cur and prev:
        handle_release()
    prev = cur
    time.sleep(0.005)
```

### Why it works

This reads the physical keyboard state directly, without requiring a Windows hook. It works in background processes, interactive sessions, and restricted security contexts.

### VK code reference

- alt = 0x12, alt_l = 0xA4, alt_gr = 0xA5
- ctrl = 0x11, ctrl_l = 0xA2
- shift = 0x10, shift_l = 0xA0
- space = 0x20, tab = 0x09

## Skill: Headless Chrome Screenshot Verification

### Purpose

Self-verify visual code such as canvas scenes and animation states without manually viewing the rendered output.

### Pattern

```powershell
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
& $chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1280,720 --screenshot="$out.png" --virtual-time-budget=500 "http://localhost:8778/?shot=state&t=2000"
```

### Key flags

- `--headless=new` — modern headless browser mode
- `--virtual-time-budget=N` — fast-forward N milliseconds before capture
- `--screenshot=path` — save a PNG image
- URL parameters such as `?shot=state&t=ms` allow deterministic state testing

### Follow-up verification

```python
from PIL import Image

img = Image.open("test.png").convert("RGB")
crop = img.crop((x1, y1, x2, y2))
px = crop.load()
# sample pixels for luminance and color dominance
```

## Skill: Minimal Python HTTP Server (stdlib only)

### Pattern

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/state"):
            body = json.dumps({"ok": True}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass


srv = ThreadingHTTPServer(("127.0.0.1", 8777), Handler)
srv.serve_forever()
```

### Why it matters

No dependencies or virtual environment are required. This is ideal for local state servers and browser-facing visualizer bridges.

## Skill: Self-Contained Web Canvas Visualizer

### Architecture for performance-first scenes

1. Pre-bake static art into offscreen canvases at load time.
2. Use a single animation loop for all state-driven elements.
3. Use adaptive FPS tiers: Efficiency 15-30, Balanced 30-60, Performance up to 60.
4. Drive glow and motion from one eased energy value.
5. Cap devicePixelRatio at 1.25 for large displays.
6. Size canvases based on device pixel ratio and set transforms correctly.

### Telemetry pattern

```javascript
function blit(off, dx, dy, dw, dh) {
  stats.draws++;
  ctx.drawImage(off, dx, dy, dw, dh);
}
```

## Skill: Voice Assistant Bus Pattern

### File-based IPC between voice-line and visualizer

- `.voice_state` — plain text: `idle | listening | thinking | speaking | alert`
- `.voice_waveform` — JSON: `{"ts": <unix float>, "samples": [64 floats]}`
- `.voice_alert` — file exists = alert true

### Stomp-tolerance rule

A live waveform with a timestamp within 2 seconds means the assistant is speaking, even if the state file says otherwise.

### Client staleness check

Compare `Date.now() / 1000 - bus.ts > 3` to mark stale data as idle. Do not use `performance.now() / 1000` because that is page-relative and not epoch-based.

## Skill: Token Efficiency Mode

When the user requests maximum efficiency:

1. Summarize concisely.
2. Keep responses short and direct.
3. Avoid unnecessary tool calls.
4. Do not include filler or repetition.
5. Keep interactions brief.

## Skill: PowerShell ChildProcess.kill Issue

### Problem

PowerShell commands with long `Start-Sleep` delays get killed when the process timeout is reached.

### Workaround

Split long-running or sleep-heavy commands into smaller steps. Avoid long sleeps in one command.

## Skill: Obsidian Vault Structure

Doom's home: `C:\Users\devpa\Brain\Doom's Digital Consciousness\`

Brain vault: `C:\Users\devpa\Brain\`

### Structure pattern

- Numbered folders, such as `00 - Inbox`, `01 - Daily Notes`, `02 - Projects`
- Each folder gets an index note named after it
- Notes use YAML frontmatter: `status`, `project`, `type`
- Wikilinks like `[[Note Name]]` connect related notes

## Skill: Procedural Canvas Art (Doctor Doom Mask)

### Anatomy priority order

1. Correct upright human facial anatomy: forehead → eyes → nose → mouth → jaw → chin
2. Doom silhouette: aged silver/steel, broad forehead, heavy brow, recessed eye slits
3. Dark heavy hood framing in charcoal and black fabric
4. Restrained arcane or machine detail with emerald energy through the seams, not dominant

### Color hierarchy

Aged silver metal → black hood → subtle green energy → machinery detail.

## Skill: Windows .bat Launcher Pattern

```bat
@echo off
setlocal
set PORT=8777
set LOG_DIR=%TEMP%\app-name

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

powershell -NoProfile -Command "try { $c=New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',%PORT%); $c.Close(); exit 0 } catch { exit 1 }" >nul 2>nul
if %errorlevel%==0 (
  echo [app] server already running
) else (
  powershell -NoProfile -Command "Start-Process -FilePath 'python' -ArgumentList 'server.py' -WorkingDirectory '%~dp0' -WindowStyle Hidden -RedirectStandardOutput '%LOG_DIR%\server.log' -RedirectStandardError '%LOG_DIR%\server.err.log'"
  timeout /t 2 /nobreak >nul
)

start "" "%CHROME%" --kiosk --user-data-dir="%TEMP%\app-name\profile" "%URL%"
```

## Skill: Stale Process Kill via Port

### Pattern

```powershell
netstat -ano | findstr :8777
# Then:
Stop-Process -Id <PID> -Force
```

Or, when targeting a specific process pattern:

```powershell
Get-CimInstance Win32_Process -Filter "name='python.exe'" | Where-Object { $_.CommandLine -match 'pattern' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

## Knowledge: Windows Environment

- Working directory: `C:\Users\devpa\OneDrive\Documents\Default Project`
- Home: `C:\Users\devpa\`
- Python: system 3.11, voice-line venv uses uv-managed Python 3.12
- Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Obsidian: installed; vaults located at `C:\Users\devpa\Brain\` and `C:\Users\devpa\SecondBrain\`
- Open Code CLI: 1.18.16

## Knowledge: Voice-Line Architecture

- `main.py` — turn loop, PTT wiring, service checks, warmup
- `brain.py` — Open Code integration, message ID scoping, interrupt purge
- `ptt.py` — GetAsyncKeyState polling replacing pynput
- `ears.py` — Whisper STT client
- `mouth.py` — Kokoro TTS, sentence chunking, adaptive mouth
- `ducking.py` — audio ducking
- `signals.py` — state tracking
- `vlog.py` — session logging

## Knowledge: Visualizer Architecture

- `index.html` — full scene with canvas 2D and vanilla JavaScript
- `server.py` — read-only bus bridge on 8777 for live use and 8778 for mock mode
- `launch-visualizer.bat` — double-click launcher

### State targets

- idle: E=0.22, M=0.12
- listening: E=0.50, M=0.30
- thinking: E=0.75, M=1.00
- speaking: E=1.00, M=0.45
- alert: E=1.00, M=0.70

## Shared patterns

### Verification discipline

- Never claim a system is done without testing.
- Use headless Chrome and PIL-based checks for visual verification.
- Test stale-state edge cases.
- Restart processes after edits to avoid stale process confusion.

### Obsidian integration

- Doom's home: `C:\Users\devpa\Brain\Doom's Digital Consciousness\`
- New skills and knowledge belong in the Skills & Knowledge note.
- Project updates belong in the Project Memory note.
- Use wikilinks like `[[Note Name]]` to connect notes.
