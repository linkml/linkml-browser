# Tauri Desktop App Plan

## Goals
- Package the existing generated static UI as a desktop app without changing the default static-site workflow.
- Provide durable local annotation storage (file or SQLite) and native file dialogs.
- Keep the same JS/HTML/CSS logic; add only small bridge code.
- Allow optional API sync later without making it required.

## Non-Goals (initial)
- Rewriting search/faceting in Rust.
- Multi-user collaboration or server-hosted datasets.
- Complex auth flows beyond optional API tokens.

## Repo Layout (Monorepo)
```
apps/
  tauri/
    src-tauri/
    ui/                 # generated output (same as static site output)
```

- Keep `src/linkml_browser/index.html` as the source of truth.
- The generator writes a complete static bundle into `apps/tauri/ui/`.
- Tauri points its `distDir` to `apps/tauri/ui/`.

## Build Flow

### Static (unchanged)
```
uv run linkml-browser deploy data.json out/
```

### Desktop
```
uv run linkml-browser deploy data.json apps/tauri/ui
cd apps/tauri
cargo tauri dev
```

## Configuration
- Tauri config uses `distDir: "../ui"` and `devPath` for local preview.
- Allowlist only the needed APIs:
  - file dialogs
  - filesystem (scoped to the app data directory)
  - optional SQLite plugin
- Disable remote navigation by default.

## Storage Options

### Option A: Local JSON file (MVP)
- Store annotations in an app data directory (Tauri path APIs).
- Simple load/save (atomic writes).
- Good for small/medium datasets.

### Option B: SQLite (Phase 2)
- Use Tauri SQL plugin for large datasets.
- Keyed by `recordId` with JSON blobs for `data` and `status`.

## UI Integration Strategy
- Add a small "store" abstraction in JS.
- At runtime detect `window.__TAURI__`:
  - If present, use Tauri store backend (file/SQLite).
  - Else, fall back to browser localStorage.
- Keep the rendering pipeline identical for static and desktop.

## Security / Permissions
- Use Tauri allowlist to restrict file system scope.
- Disallow opening external URLs unless explicitly enabled.
- Store API tokens in OS keychain (Phase 3).

## Distribution
- Provide packaged builds for macOS/Windows/Linux.
- Use GitHub Actions for release artifacts.

## Risks / Open Questions
- Large datasets may need SQLite to avoid memory pressure.
- File storage concurrency for multiple windows.
- The generator must ensure stable record IDs for durable annotations.

## Milestones
1) Scaffold Tauri app and wire distDir to generated UI.
2) Implement local JSON storage via Tauri FS.
3) Optional SQLite backend.
4) Packaging + release workflow.
