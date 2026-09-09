# Contributing

## Before opening a pull request

Run the same lightweight checks used by CI:

```bash
python -m pip install -r voice-line/requirements-ci.txt
EMBEDDING_BACKEND=dummy python -m pytest -q
python -m compileall voice-line tests
```

On PowerShell:

```powershell
$env:EMBEDDING_BACKEND = "dummy"
python -m pytest -q
python -m compileall voice-line tests
```

Do not add vault content, generated indexes, API keys, or local voice-bus
files. Use `tests/fixture_vault/` for small, synthetic memory fixtures.

## Memory changes

- Keep the dummy backend deterministic and dependency-light.
- Preserve title, relative path, frontmatter, chunk index, and wikilinks in
  retrieved metadata.
- Keep private and sensitive notes out of the index.
- Add or update tests for changes to parsing, chunking, ranking, persistence,
  or prompt formatting.

## Visualizer changes

Use deterministic screenshot hooks and test stale-state behavior. Do not make
the visualizer depend on the memory adapter; both systems communicate through
the existing state bus.