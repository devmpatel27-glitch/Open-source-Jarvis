# Visualizer Integration Contract

The visualizer directory is reserved for the fullscreen canvas implementation
and its local state bridge. The current repository documents the integration
contract even when the visualizer runtime is maintained separately.

## State bus

The visualizer reads the same file-based bus written by `voice-line`:

- `.voice_state` — `idle`, `listening`, `thinking`, `speaking`, or `alert`
- `.voice_waveform` — JSON containing an epoch `ts` and waveform samples
- `.voice_alert` — presence means alert mode is active

Memory retrieval does not change this protocol. The visualizer should continue
to render assistant state independently of Open Code or the memory index.

## Expected runtime

- Live server: port `8777`
- Mock server: port `8778`
- Browser hooks: `?shot=state&t=2000`, `?mockstate=speaking`
- Verification: headless Chrome screenshots and PIL pixel analysis

When the visualizer implementation is added to this checkout, keep its state
reader read-only and treat bus data older than three seconds as stale.