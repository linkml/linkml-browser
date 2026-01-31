# MANTRA - Tauri Desktop App

**MANTRA**: Manual ANnotation Tool for Reviewing Agents

This document is for:
- **Core contributors** working on the LinkML Browser + Tauri wrapper.
- **KB admins / curators-in-charge** who want to package and administer evaluation projects.

It is **not** end-user help for evaluators (those live in each project’s `help.html`).

## Overview
MANTRA is a Tauri desktop wrapper around the same static HTML/JS that powers LinkML Browser.
You can run the exact same project folder in a browser or in the desktop app. The desktop app adds:
- Native menus, file dialogs, and keyboard shortcuts.
- Persistent “Open Recent” lists.
- Autosave to a chosen evaluations JSON file.
- GitHub-based project download into an app data directory.

## What is a “Project”?
A project is a folder containing:
- `index.html` (the browser UI)
- `data.js` (dataset)
- `schema.js` (configuration)
- `help.html` (project-specific help, optional but recommended)

The project folder can be:
- A generated static build (`linkml-browser deploy ...`)
- A gallery entry under `docs/gallery/...`
- A folder downloaded from GitHub via the desktop app

## Dev Quick Start
```bash
# Use a gallery example in ui/
just tauri-demo dismech
cargo tauri dev
```

## Test with Your Own Project
```bash
uv run linkml-browser deploy path/to/data.json ui/
cargo tauri dev
```

Notes:
- `ui/` is the Tauri frontend bundle (configured in `src-tauri/tauri.conf.json` via `build.frontendDist`).
- The static browser does **not** depend on `ui/`; only the Tauri wrapper does.

## Native Menu + Shortcuts
The desktop app exposes a native menu (File / Edit / Help). Key actions:
- **Open Project…**: choose a folder with `index.html`, `data.js`, `schema.js`.
- **Open Project from GitHub…**: downloads a project into app data (`datasets/`).
- **Open Evaluations…**: open an existing evaluations JSON.
- **Save Evaluations As…**: choose a file that becomes the autosave target.
- **Open Recent**: inline submenus for recent projects/evaluations.

Shortcuts:
- **Cmd/Ctrl+O**: Open Evaluations

## GitHub Projects (Admin Use)
“Open Project from GitHub” expects a repo (owner/repo or URL), a branch/tag, and a subdirectory.
- Default subdir: `app`
- Required files in that subdir: `index.html`, `data.js`, `schema.js` (and optionally `help.html`)

The app downloads into the **app data directory** under:
```
{appDataDir}/datasets/{owner}-{repo}-{ref}-{subdir}/
```
The prompt displays the base directory so admins know where files are stored.

Troubleshooting:
- You’ll see explicit HTTP errors for missing files (e.g. 404 on `data.js`).
- Verify the raw URL is reachable in a browser.

## Evaluations: Storage & Format
The app keeps evaluations in two places:
1) **localStorage** (always, per project)
2) **Autosave file** (if you use “Save Evaluations As…” or open an evaluations JSON)

The evaluations JSON uses this shape:
```json
{
  "schemaVersion": 1,
  "datasetHash": "fnv1a:...",
  "updatedAt": "2026-01-29T12:00:00Z",
  "annotations": [
    {
      "recordId": "example-id",
      "curatorId": "local",
      "updatedAt": "2026-01-29T12:00:00Z",
      "status": "draft",
      "data": { "field": "value" },
      "record": { "...": "original item" }
    }
  ]
}
```

Notes:
- `recordId` must be stable (configured via `recordIdField` in `schema.js`).
- The exported JSON includes `record` for durability (keeps a snapshot of the evaluated item).
- The status facet is auto‑injected unless disabled in schema.

## Project Configuration Notes (Admins)
Required schema fields:
- `recordIdField` (must be stable and unique)
- `displayFields` and `facets`

Evaluation configuration:
- `curationFields` defines editable fields.
- `curation.sections` groups fields in the UI.
- Decorators (e.g. `thumbs`) can be added to display fields for quick decisions.

Optional:
- `customCss` for project-specific layout tweaks.
- `help.html` for evaluator guidance (opened via Help → Documentation).

## Help Pages
Help → Documentation opens `help.html` from the project directory.
If it’s missing, the app falls back to opening `help.html` relative to the UI bundle.

## Permissions (Desktop App)
Tauri permissions live in:
- `src-tauri/capabilities/default.json`

Current permissions include:
- `fs:allow-read-text-file`
- `fs:allow-write-text-file`
- `fs:allow-mkdir`
- `shell:default` (open URLs in the system browser)
- `dialog:default`

If you expand functionality (e.g., export to other locations), update permissions accordingly.

## Build Binaries (Local)
```bash
just tauri-build
```

## Distribution Guidance
MANTRA is a **desktop GUI app**, so **crates.io is not the right distribution channel** for end users.
Crates are for Rust libraries and CLIs; MANTRA should ship as platform installers:

- **GitHub Releases** (DMG/MSI/AppImage) — primary distribution
- Optional: Homebrew (macOS), winget (Windows), or Linux package repos

If you later add a Rust CLI for admins (e.g., validation or batch export), that CLI could be
published on crates.io, but the desktop app should remain in GitHub Releases.

## GitHub Actions (Tagged Releases)
We publish platform-specific binaries on **tagged releases** (e.g., `v0.2.0`). The workflow:

1. Generates a **placeholder UI** (no bundled example data) using `scripts/prepare_tauri_ui.sh`.
2. Builds installers for macOS, Windows, and Linux.
3. Attaches artifacts to the GitHub Release.

Workflow file:
```
.github/workflows/tauri-release.yml
```

Key steps in CI:
- Generate a placeholder UI (`scripts/prepare_tauri_ui.sh`).
- Install Linux build deps (webkit2gtk, appindicator, librsvg, patchelf).
- Build with `tauri-apps/tauri-action` on macOS (x86_64 + arm64), Windows, and Linux.

### Signing (Recommended)
The workflow supports signing if you add the appropriate GitHub Secrets:

**macOS**
- `APPLE_CERTIFICATE`
- `APPLE_CERTIFICATE_PASSWORD`
- `APPLE_SIGNING_IDENTITY`
- `APPLE_ID`
- `APPLE_PASSWORD`
- `APPLE_TEAM_ID`

**Windows**
- `WINDOWS_CERTIFICATE`
- `WINDOWS_CERTIFICATE_PASSWORD`

If you omit these, builds will still succeed but installers will be unsigned.

If you hit a bundle identifier error, update:
- `src-tauri/tauri.conf.json` → `identifier`

## Troubleshooting
- **GitHub import fails**: check the error message for the failing URL + status.
- **Help menu does nothing**: ensure `help.html` exists in the project folder.
- **Links don’t open**: ensure `shell:default` permission is set and the shell plugin is enabled.
- **Evaluations not saving**: verify autosave path is set and writable.

## Admin Workflow (Suggested)
1. Generate a project folder (`linkml-browser deploy ...`).
2. Add `help.html` for evaluator instructions.
3. Distribute the folder or host it in GitHub under `app/`.
4. Evaluators open the project in the desktop app.
5. Collect evaluation JSONs (autosave files) for downstream analysis.
