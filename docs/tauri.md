# Tauri Desktop App (Local)

## Prereqs
- Rust + Cargo
- Tauri CLI: `cargo install tauri-cli` (or use `cargo tauri` if already available)

## Testing Workflow (using gallery example)
```bash
mkdir -p ui
cp -R docs/gallery/dismech/* ui/
cargo tauri dev
```

## Testing Workflow (your own dataset)
Generate a static browser into `ui/`, then run Tauri:
```bash
uv run linkml-browser deploy path/to/data.json ui/
cargo tauri dev
```

## Notes
- The Tauri app loads files from `ui/` (configured in `src-tauri/tauri.conf.json` via `build.frontendDist`).
- The static browser itself is not hardwired to `ui/`; only the Tauri wrapper uses that path.
- You can change the path by updating `src-tauri/tauri.conf.json`.
- `ui/` is treated as build output and is ignored by git.
- In the desktop app, use the “Open Dataset” button to select another generated browser folder.
