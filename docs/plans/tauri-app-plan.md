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

## Storage
- Use a local JSON file stored in the app data directory (Tauri path APIs).
- Simple load/save with atomic writes.
- Avoid database dependencies (no SQLite/MySQL).

### File Format (Proposed)
- One file per dataset to avoid collisions and simplify backup/export.
- Filename derived from dataset hash: `annotations_<datasetHash>.json`

Example:
```json
{
  "schemaVersion": 1,
  "datasetHash": "sha256:...",
  "updatedAt": "2026-01-28T12:34:56Z",
  "annotations": {
    "R-001": {
      "recordId": "R-001",
      "status": "submitted",
      "updatedAt": "2026-01-28T12:10:00Z",
      "data": {
        "overall_rank": 4,
        "is_spam": false
      }
    }
  }
}
```

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
- Large datasets may need incremental writes or sharding to avoid memory pressure.
- File storage concurrency for multiple windows.
- The generator must ensure stable record IDs for durable annotations.

## Milestones
1) Scaffold Tauri app and wire distDir to generated UI.
2) Implement local JSON storage via Tauri FS.
3) Packaging + release workflow.
