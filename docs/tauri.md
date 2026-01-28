# Tauri Desktop App (Local)

## Prereqs
- Rust + Cargo
- Tauri CLI: `cargo install tauri-cli` (or use `cargo tauri` if already available)

## Quick Start (using gallery example)
```bash
mkdir -p ui
cp -R docs/gallery/dismech/* ui/
cargo tauri dev
```

## Using your own dataset
Generate a static browser into `ui/`, then run Tauri:
```bash
uv run linkml-browser deploy path/to/data.json ui/
cargo tauri dev
```

## Notes
- The Tauri app loads files from `ui/` (configured in `src-tauri/tauri.conf.json`).
- `ui/` is treated as build output and is ignored by git.
